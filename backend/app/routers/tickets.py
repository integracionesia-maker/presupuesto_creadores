"""REST endpoints for tickets — includes transactional file-upload flow."""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db, SessionLocal
from ..dependencies import get_current_user, require_role
from ..upload_manager import save_upload, delete_upload

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.get("/", response_model=List[schemas.TicketResponse])
def list_tickets(
    creator_name: Optional[str] = None,
    brand_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role == "creador":
        # Se ignora cualquier filtro por nombre de creador: un creador solo ve lo suyo.
        tickets = crud.get_tickets(db, creator_name=None, brand_name=brand_name)
        tickets = [t for t in tickets if t.creator_id == current_user.creator_id]
    else:
        tickets = crud.get_tickets(db, creator_name=creator_name, brand_name=brand_name)
    result: List[schemas.TicketResponse] = []
    for t in tickets:
        result.append(
            schemas.TicketResponse(
                id=t.id,
                creator_id=t.creator_id,
                brand_id=t.brand_id,
                amount=t.amount,
                file_name=t.file_name,
                file_path=t.file_path,
                mime_type=t.mime_type,
                upload_date=t.upload_date,
                notes=t.notes,
                creator_name=t.creator.name if t.creator else None,
                brand_name=t.brand.name if t.brand else None,
            )
        )
    return result


@router.get("/brand-spend", response_model=List[schemas.BrandSpendItem])
def brand_spend_breakdown(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin", "superadmin")),
):
    return crud.get_brand_spend_breakdown(db, start_date=start_date, end_date=end_date)


@router.get("/file/{ticket_id}")
def download_file(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ticket = crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado.")
    if current_user.role == "creador" and ticket.creator_id != current_user.creator_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para esta acción.")
    return FileResponse(path=ticket.file_path, media_type=ticket.mime_type, filename=ticket.file_name)


@router.post("/", response_model=schemas.TicketResponse, status_code=201)
def create_ticket(
    creator_id: int = Form(...),
    brand_id: int = Form(...),
    amount: float = Form(..., gt=0),
    notes: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role == "creador" and creator_id != current_user.creator_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para esta acción.")

    db: Session = SessionLocal()
    file_path_on_disk: Optional[str] = None

    try:
        creator = crud.get_creator(db, creator_id)
        if not creator:
            raise HTTPException(status_code=404, detail="Creador no encontrado.")
        if not creator.is_active:
            raise HTTPException(status_code=400, detail="El creador esta inactivo.")

        brand = crud.get_brand(db, brand_id)
        if not brand:
            raise HTTPException(status_code=404, detail="Marca no encontrada.")
        if not brand.is_active:
            raise HTTPException(status_code=400, detail="La marca esta inactiva.")

        if creator.remaining_budget < amount:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Fondos insuficientes. El creador '{creator.name}' tiene "
                    f"${creator.remaining_budget:,.2f} restante, "
                    f"pero el ticket requiere ${amount:,.2f}."
                ),
            )

        file_name, file_path_on_disk, mime_type = save_upload(file)

        ticket = crud.create_ticket_transactional(
            db=db,
            creator=creator,
            brand=brand,
            amount=amount,
            file_name=file_name,
            file_path=file_path_on_disk,
            mime_type=mime_type,
            notes=notes,
        )

        return schemas.TicketResponse(
            id=ticket.id,
            creator_id=ticket.creator_id,
            brand_id=ticket.brand_id,
            amount=ticket.amount,
            file_name=ticket.file_name,
            file_path=ticket.file_path,
            mime_type=ticket.mime_type,
            upload_date=ticket.upload_date,
            notes=ticket.notes,
            creator_name=creator.name,
            brand_name=brand.name,
        )

    except HTTPException:
        db.rollback()
        if file_path_on_disk:
            delete_upload(file_path_on_disk)
        raise
    except Exception as exc:
        db.rollback()
        if file_path_on_disk:
            delete_upload(file_path_on_disk)
        raise HTTPException(status_code=500, detail=f"Error inesperado al crear el ticket: {exc}")
    finally:
        db.close()
