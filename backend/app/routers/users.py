"""Gestión de usuarios (sección Administración): crear, editar, resetear contraseña, activar/desactivar.

Reglas de alcance (ver doc/auth-diseno-fase1.md §2 y §0):
- superadmin: gestiona admins y creadores; nunca crea/edita otro superadmin (singleton, ver §0.2).
- admin: solo puede gestionar usuarios de rol 'creador'.
- El rol y el estado (is_active) del superadmin son inmutables por API.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import crud, models, schemas, security
from ..database import get_db
from ..dependencies import require_role

router = APIRouter(prefix="/api/users", tags=["users"])

VALID_ROLES = {r.value for r in models.UserRole}


def _ensure_assignable_role(role: str) -> None:
    if role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Rol inválido: '{role}'.")
    if role == models.UserRole.SUPERADMIN.value:
        raise HTTPException(
            status_code=400, detail="El rol 'superadmin' no se puede crear ni asignar por API."
        )


def _ensure_admin_scope(actor: models.User, role: str) -> None:
    if actor.role == models.UserRole.ADMIN.value and role != models.UserRole.CREADOR.value:
        raise HTTPException(
            status_code=403, detail="Un admin solo puede gestionar usuarios de rol 'creador'."
        )


def _ensure_can_manage_target(actor: models.User, target: models.User) -> None:
    if actor.role == models.UserRole.ADMIN.value and target.role != models.UserRole.CREADOR.value:
        raise HTTPException(status_code=403, detail="No tienes permiso para esta acción.")


def _get_target_or_404(db: Session, user_id: int) -> models.User:
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return user


@router.get("/", response_model=List[schemas.UserResponse])
def list_users(
    role: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin", "superadmin")),
):
    if current_user.role == models.UserRole.ADMIN.value:
        # Un admin ve los usuarios 'creador' que gestiona, más su propia fila
        # (para poder desactivar su propia cuenta; editarla se hace en /perfil).
        users = crud.list_users(db, role=models.UserRole.CREADOR.value)
        if not any(u.id == current_user.id for u in users):
            users = sorted(users + [current_user], key=lambda u: u.username)
        return users
    return crud.list_users(db, role=role)


@router.post("/", response_model=schemas.UserResponse, status_code=201)
def create_user(
    data: schemas.UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin", "superadmin")),
):
    _ensure_assignable_role(data.role)
    _ensure_admin_scope(current_user, data.role)

    if data.role == models.UserRole.CREADOR.value:
        if not data.creator_id:
            raise HTTPException(
                status_code=400,
                detail="Debes vincular un creador para un usuario de rol 'creador'.",
            )
        if not crud.get_creator(db, data.creator_id):
            raise HTTPException(status_code=404, detail="Creador no encontrado.")
    elif data.creator_id:
        raise HTTPException(
            status_code=400,
            detail="Solo los usuarios de rol 'creador' pueden vincularse a un creador.",
        )

    if data.password:
        error = security.validate_password_strength(data.password, data.username)
        if error:
            raise HTTPException(status_code=400, detail=error)
        password = data.password
    else:
        password = security.generate_temp_password()

    try:
        user = crud.create_user(
            db,
            username=data.username,
            email=data.email,
            password_hash=security.hash_password(password),
            full_name=data.full_name,
            role=data.role,
            creator_id=data.creator_id,
            must_change_password=True,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ya existe un usuario con ese nombre de usuario, correo, o el creador ya tiene un usuario vinculado.",
        )

    crud.log_audit(
        db,
        actor_user_id=current_user.id,
        action="user.create",
        target_type="user",
        target_id=user.id,
        details=f"role={user.role}",
    )
    return user


@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin", "superadmin")),
):
    target = _get_target_or_404(db, user_id)
    _ensure_can_manage_target(current_user, target)
    return target


@router.put("/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: int,
    data: schemas.UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin", "superadmin")),
):
    target = _get_target_or_404(db, user_id)
    _ensure_can_manage_target(current_user, target)

    if target.role == models.UserRole.SUPERADMIN.value:
        raise HTTPException(status_code=403, detail="La cuenta superadmin no se puede modificar por API.")

    update_data = data.model_dump(exclude_unset=True)

    if "role" in update_data and update_data["role"] is not None:
        _ensure_assignable_role(update_data["role"])
        _ensure_admin_scope(current_user, update_data["role"])

    if update_data.get("creator_id") is not None:
        if not crud.get_creator(db, update_data["creator_id"]):
            raise HTTPException(status_code=404, detail="Creador no encontrado.")

    if update_data.get("email"):
        existing = crud.get_user_by_email(db, update_data["email"])
        if existing and existing.id != target.id:
            raise HTTPException(status_code=409, detail="Ese correo ya está en uso.")

    try:
        updated = crud.update_user_admin(db, target, update_data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ese creador ya tiene un usuario vinculado.")

    crud.log_audit(
        db, actor_user_id=current_user.id, action="user.update", target_type="user", target_id=target.id,
    )
    return updated


@router.post("/{user_id}/reset-password", response_model=schemas.ResetPasswordResponse)
def reset_password(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin", "superadmin")),
):
    target = _get_target_or_404(db, user_id)
    _ensure_can_manage_target(current_user, target)
    if target.role == models.UserRole.SUPERADMIN.value:
        raise HTTPException(status_code=403, detail="La cuenta superadmin no se puede modificar por API.")

    temp_password = security.generate_temp_password()
    crud.set_user_password(db, target, security.hash_password(temp_password), must_change_password=True)
    crud.revoke_all_refresh_tokens_for_user(db, target.id)

    crud.log_audit(
        db,
        actor_user_id=current_user.id,
        action="password.reset_by_admin",
        target_type="user",
        target_id=target.id,
    )
    return schemas.ResetPasswordResponse(temporary_password=temp_password)


@router.patch("/{user_id}/estado", response_model=schemas.UserResponse)
def set_user_estado(
    user_id: int,
    data: schemas.SetUserActiveRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin", "superadmin")),
):
    target = _get_target_or_404(db, user_id)
    is_self = target.id == current_user.id

    # La restricción "un admin solo gestiona usuarios rol creador" aplica a terceros;
    # desactivarse a sí mismo es una excepción explícita (ver doc/auth-diseno-fase1.md §0.3).
    if not is_self:
        _ensure_can_manage_target(current_user, target)

    if target.role == models.UserRole.SUPERADMIN.value:
        raise HTTPException(status_code=403, detail="La cuenta superadmin no se puede desactivar.")

    if is_self and not data.is_active:
        if not data.confirm_username or data.confirm_username != current_user.username:
            raise HTTPException(
                status_code=400,
                detail="Para desactivar tu propia cuenta, confirma escribiendo tu nombre de usuario.",
            )

    updated = crud.set_user_active(db, target, data.is_active)
    if not data.is_active:
        crud.revoke_all_refresh_tokens_for_user(db, target.id)

    crud.log_audit(
        db,
        actor_user_id=current_user.id,
        action="user.activate" if data.is_active else "user.deactivate",
        target_type="user",
        target_id=target.id,
    )
    return updated
