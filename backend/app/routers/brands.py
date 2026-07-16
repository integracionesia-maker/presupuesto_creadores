"""REST endpoints for brands."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/brands", tags=["brands"])


@router.get("/", response_model=List[schemas.BrandResponse])
def list_brands(active_only: bool = False, db: Session = Depends(get_db)):
    return crud.get_brands(db, active_only=active_only)


@router.get("/{brand_id}", response_model=schemas.BrandResponse)
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    brand = crud.get_brand(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Marca no encontrada.")
    return brand


@router.post("/", response_model=schemas.BrandResponse, status_code=201)
def create_brand(data: schemas.BrandCreate, db: Session = Depends(get_db)):
    return crud.create_brand(db, data)


@router.put("/{brand_id}", response_model=schemas.BrandResponse)
def update_brand(brand_id: int, data: schemas.BrandUpdate, db: Session = Depends(get_db)):
    brand = crud.get_brand(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Marca no encontrada.")
    return crud.update_brand(db, brand, data)
