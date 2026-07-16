"""Dashboard analytics endpoints with date-range filtering."""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=schemas.DashboardSummary)
def dashboard_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    return crud.get_dashboard_summary(db, start_date=start_date, end_date=end_date)


@router.get("/monthly-spend", response_model=List[schemas.MonthlySpendItem])
def monthly_spend(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    return crud.get_monthly_spend(db, start_date=start_date, end_date=end_date)


@router.get("/creator-usage", response_model=List[schemas.CreatorUsageItem])
def creator_usage(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    return crud.get_creator_usage(db, start_date=start_date, end_date=end_date)
