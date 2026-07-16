"""CRUD helper functions used by API routers."""

from datetime import datetime, date
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
