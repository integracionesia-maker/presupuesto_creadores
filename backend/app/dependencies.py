"""FastAPI dependencies for authentication and role-based authorization."""

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from . import crud, models, security
from .database import get_db


def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.User:
    token = request.cookies.get(security.ACCESS_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado.")

    payload = security.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada.")

    user = crud.get_user(db, int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Sesión inválida.")

    if user.token_version != payload.get("tv"):
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada.")

    return user


def require_role(*roles: str):
    """Dependencia factory: 403 si el rol del usuario actual no está en `roles`."""

    def _dependency(current_user: models.User = Depends(get_current_user)) -> models.User:
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="No tienes permiso para esta acción.")
        return current_user

    return _dependency
