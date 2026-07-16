"""Trim filler tickets (from seed_more_months.py) for creators that ended up
over budget after merging duplicate rows — largest filler ticket first,
until each creator's remaining_budget is back to >= 0 (small positive buffer).

Only touches tickets whose notes exactly match one of the filler templates
below (formatted with a real brand name); hand-authored tickets from
seed_test_data.py or the live app are never touched.
"""

import os

from app.database import SessionLocal
from app.models import Creator, Brand, Ticket

FILLER_NOTE_TEMPLATES = [
    "Campana {brand} - post patrocinado",
    "Story destacada {brand} - 24h",
    "Reel promocional {brand}",
    "Unboxing {brand} - YouTube",
    "Review producto {brand} - TikTok",
    "Colaboracion {brand} - contenido pago",
    "Mencion en video {brand}",
    "Carrusel Instagram {brand}",
    "Live patrocinado {brand}",
    "Newsletter integracion {brand}",
    "Serie de stories {brand} - lanzamiento",
    "Video largo {brand} - integracion producto",
]

db = SessionLocal()

brand_names = [b.name for b in db.query(Brand).all()]
filler_notes = {t.format(brand=name) for t in FILLER_NOTE_TEMPLATES for name in brand_names}

overbudget_creators = db.query(Creator).filter(Creator.remaining_budget < 0).all()

if not overbudget_creators:
    print("Ningun creador esta sobregirado. Nada que hacer.")
    db.close()
    exit(0)

for creator in overbudget_creators:
    deficit = -creator.remaining_budget
    filler_tickets = sorted(
        (t for t in db.query(Ticket).filter(Ticket.creator_id == creator.id).all()
         if t.notes in filler_notes),
        key=lambda t: t.amount,
        reverse=True,
    )

    removed = []
    removed_total = 0.0
    for t in filler_tickets:
        if removed_total >= deficit:
            break
        removed.append(t)
        removed_total += t.amount

    if removed_total < deficit:
        print(f"  [WARN] {creator.name}: no hay suficientes tickets de relleno para cubrir "
              f"el deficit (${deficit:,.2f}); solo se pueden recuperar ${removed_total:,.2f}")

    for t in removed:
        if t.file_path and os.path.exists(t.file_path):
            os.remove(t.file_path)
        db.delete(t)
    db.flush()

    remaining_tickets = db.query(Ticket).filter(Ticket.creator_id == creator.id).all()
    total_spent = sum(t.amount for t in remaining_tickets)
    creator.spent_budget = total_spent
    creator.remaining_budget = creator.initial_budget - total_spent

    print(f"  [OK] {creator.name}: removidos {len(removed)} tickets (${removed_total:,.2f}), "
          f"nuevo remaining=${creator.remaining_budget:,.2f}")

db.commit()
db.close()
print("\n>>> Ajuste de sobregiro completado.")
