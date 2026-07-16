"""REST endpoints for creators."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/creators", tags=["creators"])


@router.get("/", response_model=List[schemas.CreatorResponse])
def list_creators(active_only: bool = False, db: Session = Depends(get_db)):
    return crud.get_creators(db, active_only=active_only)


@router.get("/kpi", response_model=schemas.CreatorKpiResponse)
def get_kpi(db: Session = Depends(get_db)):
    return crud.get_creators_kpi(db)


@router.get("/{creator_id}", response_model=schemas.CreatorResponse)
def get_creator(creator_id: int, db: Session = Depends(get_db)):
    creator = crud.get_creator(db, creator_id)
    if not creator:
        raise HTTPException(status_code=404, detail="Creador no encontrado.")
    return creator


@router.post("/", response_model=schemas.CreatorResponse, status_code=201)
def create_creator(data: schemas.CreatorCreate, db: Session = Depends(get_db)):
    return crud.create_creator(db, data)


@router.put("/{creator_id}", response_model=schemas.CreatorResponse)
def update_creator(creator_id: int, data: schemas.CreatorUpdate, db: Session = Depends(get_db)):
    creator = crud.get_creator(db, creator_id)
    if not creator:
        raise HTTPException(status_code=404, detail="Creador no encontrado.")
    return crud.update_creator(db, creator, data)
