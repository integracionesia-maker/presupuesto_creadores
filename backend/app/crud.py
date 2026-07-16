"""CRUD helper functions used by API routers."""

from datetime import datetime, date, timedelta, timezone
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from . import models, schemas


# ── Creators ─────────────────────────────────────────────────────────────────

def get_creators(db: Session, active_only: bool = False) -> List[models.Creator]:
    q = db.query(models.Creator)
    if active_only:
        q = q.filter(models.Creator.is_active == True)
    return q.order_by(models.Creator.name).all()


def get_creator(db: Session, creator_id: int) -> Optional[models.Creator]:
    return db.query(models.Creator).filter(models.Creator.id == creator_id).first()


def create_creator(db: Session, data: schemas.CreatorCreate) -> models.Creator:
    creator = models.Creator(
        name=data.name,
        initial_budget=data.initial_budget,
        remaining_budget=data.initial_budget,
    )
    db.add(creator)
    db.commit()
    db.refresh(creator)
    return creator


def update_creator(
    db: Session, creator: models.Creator, data: schemas.CreatorUpdate
) -> models.Creator:
    update_data = data.model_dump(exclude_unset=True)
    if "initial_budget" in update_data:
        delta = update_data["initial_budget"] - creator.initial_budget
        creator.remaining_budget += delta
    for field, value in update_data.items():
        setattr(creator, field, value)
    db.commit()
    db.refresh(creator)
    return creator


def get_creators_kpi(db: Session) -> schemas.CreatorKpiResponse:
    active = (
        db.query(models.Creator)
        .filter(models.Creator.is_active == True)
        .all()
    )
    total_budget = sum(c.initial_budget for c in active)
    total_spent = sum(c.spent_budget for c in active)
    total_remaining = sum(c.remaining_budget for c in active)
    return schemas.CreatorKpiResponse(
        total_budget=total_budget,
        total_spent=total_spent,
        total_remaining=total_remaining,
        active_creators=len(active),
    )


# ── Brands ───────────────────────────────────────────────────────────────────

def get_brands(db: Session, active_only: bool = False) -> List[models.Brand]:
    q = db.query(models.Brand)
    if active_only:
        q = q.filter(models.Brand.is_active == True)
    return q.order_by(models.Brand.name).all()


def get_brand(db: Session, brand_id: int) -> Optional[models.Brand]:
    return db.query(models.Brand).filter(models.Brand.id == brand_id).first()


def create_brand(db: Session, data: schemas.BrandCreate) -> models.Brand:
    brand = models.Brand(name=data.name)
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand


def update_brand(
    db: Session, brand: models.Brand, data: schemas.BrandUpdate
) -> models.Brand:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(brand, field, value)
    db.commit()
    db.refresh(brand)
    return brand


# ── Tickets ──────────────────────────────────────────────────────────────────

def get_tickets(
    db: Session,
    creator_name: Optional[str] = None,
    brand_name: Optional[str] = None,
) -> List[models.Ticket]:
    q = db.query(models.Ticket)
    if creator_name:
        q = q.join(models.Creator).filter(models.Creator.name.ilike(f"%{creator_name}%"))
    if brand_name:
        q = q.join(models.Brand).filter(models.Brand.name.ilike(f"%{brand_name}%"))
    return q.order_by(models.Ticket.upload_date.desc()).all()


def get_ticket(db: Session, ticket_id: int) -> Optional[models.Ticket]:
    return db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()


def create_ticket_transactional(
    db: Session,
    creator: models.Creator,
    brand: models.Brand,
    amount: float,
    file_name: str,
    file_path: str,
    mime_type: str,
    notes: Optional[str],
) -> models.Ticket:
    if creator.remaining_budget < amount:
        raise ValueError(
            f"Fondos insuficientes. Presupuesto restante: ${creator.remaining_budget:,.2f}, "
            f"pero el ticket requiere: ${amount:,.2f}."
        )

    creator.spent_budget += amount
    creator.remaining_budget = creator.initial_budget - creator.spent_budget

    ticket = models.Ticket(
        creator_id=creator.id,
        brand_id=brand.id,
        amount=amount,
        file_name=file_name,
        file_path=file_path,
        mime_type=mime_type,
        notes=notes,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_brand_spend_breakdown(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[schemas.BrandSpendItem]:
    q = (
        db.query(
            models.Brand.name.label("brand_name"),
            func.coalesce(func.sum(models.Ticket.amount), 0.0).label("total_spent"),
        )
        .outerjoin(models.Ticket, models.Brand.id == models.Ticket.brand_id)
    )
    if start_date:
        q = q.filter(models.Ticket.upload_date >= start_date)
    if end_date:
        q = q.filter(models.Ticket.upload_date <= end_date)
    rows = (
        q.group_by(models.Brand.id, models.Brand.name)
        .order_by(func.sum(models.Ticket.amount).desc())
        .all()
    )
    return [
        schemas.BrandSpendItem(brand_name=r.brand_name, total_spent=float(r.total_spent))
        for r in rows
    ]


# ── Dashboard ──────────────────────────────────────────────────────────────────


def get_monthly_spend(
    db: Session, start_date: Optional[date] = None, end_date: Optional[date] = None
) -> List[schemas.MonthlySpendItem]:
    q = db.query(
        func.strftime("%Y-%m", models.Ticket.upload_date).label("month"),
        func.coalesce(func.sum(models.Ticket.amount), 0.0).label("total"),
        func.count(models.Ticket.id).label("count"),
    )
    if start_date:
        q = q.filter(models.Ticket.upload_date >= start_date)
    if end_date:
        q = q.filter(models.Ticket.upload_date <= end_date)
    rows = (
        q.group_by("month")
        .order_by("month")
        .all()
    )
    return [
        schemas.MonthlySpendItem(month=r.month, total=float(r.total), count=r.count)
        for r in rows
    ]


def get_creator_usage(
    db: Session, start_date: Optional[date] = None, end_date: Optional[date] = None
) -> List[schemas.CreatorUsageItem]:
    ticket_spent = (
        db.query(
            models.Ticket.creator_id,
            func.coalesce(func.sum(models.Ticket.amount), 0.0).label("spent"),
        )
    )
    if start_date:
        ticket_spent = ticket_spent.filter(models.Ticket.upload_date >= start_date)
    if end_date:
        ticket_spent = ticket_spent.filter(models.Ticket.upload_date <= end_date)
    ticket_spent = ticket_spent.group_by(models.Ticket.creator_id).subquery()

    rows = (
        db.query(
            models.Creator.id.label("creator_id"),
            models.Creator.name,
            models.Creator.initial_budget,
            func.coalesce(ticket_spent.c.spent, 0.0).label("spent"),
        )
        .outerjoin(ticket_spent, models.Creator.id == ticket_spent.c.creator_id)
        .filter(models.Creator.is_active == True)
        .order_by(func.coalesce(ticket_spent.c.spent, 0.0).desc())
        .all()
    )
    return [
        schemas.CreatorUsageItem(
            creator_id=r.creator_id,
            name=r.name,
            spent=float(r.spent),
            initial_budget=float(r.initial_budget),
            percentage=round((float(r.spent) / float(r.initial_budget)) * 100, 1) if r.initial_budget > 0 else 0.0,
        )
        for r in rows
    ]


def get_dashboard_summary(
    db: Session, start_date: Optional[date] = None, end_date: Optional[date] = None
) -> schemas.DashboardSummary:
    q = db.query(
        func.coalesce(func.sum(models.Ticket.amount), 0.0),
        func.count(models.Ticket.id),
    )
    if start_date:
        q = q.filter(models.Ticket.upload_date >= start_date)
    if end_date:
        q = q.filter(models.Ticket.upload_date <= end_date)
    total_spent, ticket_count = q.first()

    active_brands = (
        db.query(func.count(func.distinct(models.Brand.id)))
        .filter(models.Brand.is_active == True)
        .join(models.Ticket, models.Brand.id == models.Ticket.brand_id)
    )
    if start_date:
        active_brands = active_brands.filter(models.Ticket.upload_date >= start_date)
    if end_date:
        active_brands = active_brands.filter(models.Ticket.upload_date <= end_date)
    active_brands = active_brands.scalar() or 0

    avg_ticket = float(total_spent) / ticket_count if ticket_count > 0 else 0.0

    return schemas.DashboardSummary(
        total_spent=float(total_spent),
        ticket_count=ticket_count,
        avg_ticket=round(avg_ticket, 2),
        active_brands=active_brands,
    )


# ── Usuarios ─────────────────────────────────────────────────────────────────

MAX_FAILED_LOGIN_ATTEMPTS = 5
BASE_LOCK_MINUTES = 5
MAX_LOCK_MINUTES = 60


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_identifier(db: Session, identifier: str) -> Optional[models.User]:
    return get_user_by_username(db, identifier) or get_user_by_email(db, identifier)


def list_users(db: Session, role: Optional[str] = None) -> List[models.User]:
    q = db.query(models.User)
    if role:
        q = q.filter(models.User.role == role)
    return q.order_by(models.User.username).all()


def create_user(
    db: Session,
    *,
    username: str,
    email: str,
    password_hash: str,
    full_name: str,
    role: str,
    creator_id: Optional[int] = None,
    must_change_password: bool = True,
) -> models.User:
    user = models.User(
        username=username,
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        role=role,
        creator_id=creator_id,
        must_change_password=must_change_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_profile(
    db: Session, user: models.User, full_name: Optional[str], email: Optional[str]
) -> models.User:
    if full_name is not None:
        user.full_name = full_name
    if email is not None:
        user.email = email
    db.commit()
    db.refresh(user)
    return user


def update_user_admin(db: Session, user: models.User, update_data: dict) -> models.User:
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def set_user_password(
    db: Session, user: models.User, password_hash: str, must_change_password: bool
) -> models.User:
    user.password_hash = password_hash
    user.must_change_password = must_change_password
    user.token_version += 1
    db.commit()
    db.refresh(user)
    return user


def set_user_active(db: Session, user: models.User, is_active: bool) -> models.User:
    user.is_active = is_active
    if not is_active:
        user.token_version += 1
    db.commit()
    db.refresh(user)
    return user


def is_locked(user: models.User) -> bool:
    # Naive UTC: SQLite devuelve locked_until sin tzinfo; ambos lados deben coincidir.
    return user.locked_until is not None and user.locked_until > datetime.now(timezone.utc).replace(tzinfo=None)


def register_failed_login(db: Session, user: models.User) -> None:
    user.failed_login_attempts += 1
    if user.failed_login_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
        extra = user.failed_login_attempts - MAX_FAILED_LOGIN_ATTEMPTS
        lock_minutes = min(BASE_LOCK_MINUTES * (2 ** extra), MAX_LOCK_MINUTES)
        user.locked_until = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=lock_minutes)
    db.commit()


def register_successful_login(db: Session, user: models.User) -> None:
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.now(timezone.utc)
    db.commit()


# ── Refresh tokens ───────────────────────────────────────────────────────────

def create_refresh_token_record(
    db: Session, user_id: int, token_hash: str, expires_at: datetime
) -> models.RefreshToken:
    rt = models.RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt


def get_refresh_token_by_hash(db: Session, token_hash: str) -> Optional[models.RefreshToken]:
    return (
        db.query(models.RefreshToken)
        .filter(models.RefreshToken.token_hash == token_hash)
        .first()
    )


def rotate_refresh_token(
    db: Session, old_token: models.RefreshToken, new_token_hash: str, new_expires_at: datetime
) -> models.RefreshToken:
    new_rt = models.RefreshToken(
        user_id=old_token.user_id, token_hash=new_token_hash, expires_at=new_expires_at
    )
    db.add(new_rt)
    db.flush()
    old_token.revoked_at = datetime.now(timezone.utc)
    old_token.replaced_by_id = new_rt.id
    db.commit()
    db.refresh(new_rt)
    return new_rt


def revoke_refresh_token(db: Session, token: models.RefreshToken) -> None:
    token.revoked_at = datetime.now(timezone.utc)
    db.commit()


def revoke_all_refresh_tokens_for_user(db: Session, user_id: int) -> None:
    now = datetime.now(timezone.utc)
    (
        db.query(models.RefreshToken)
        .filter(
            models.RefreshToken.user_id == user_id,
            models.RefreshToken.revoked_at.is_(None),
        )
        .update({"revoked_at": now}, synchronize_session=False)
    )
    db.commit()


# ── Auditoría ────────────────────────────────────────────────────────────────

def log_audit(
    db: Session,
    *,
    action: str,
    actor_user_id: Optional[int] = None,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> None:
    entry = models.AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details,
        ip_address=ip_address,
    )
    db.add(entry)
    db.commit()
