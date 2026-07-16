"""One-off cleanup: merge duplicate creator/brand rows created by an earlier
unaccented reseed (e.g. "Mariana Lopez" vs "Mariana Lopez" with accents).

For each (keep_id, drop_id) pair:
  - reassigns every ticket from drop_id to keep_id
  - recomputes spent_budget/remaining_budget on the kept creator from its
    (now merged) ticket history
  - deletes the now-orphaned duplicate row
"""

from app.database import SessionLocal
from app.models import Creator, Brand, Ticket

db = SessionLocal()

# (keep_id, drop_id) -> keep the accented / original spelling
CREATOR_MERGES = [
    (1, 7),  # Mariana López <- Mariana Lopez
    (4, 8),  # Diego Fernández <- Diego Fernandez
    (5, 9),  # Sofía Herrera <- Sofia Herrera
]
BRAND_MERGES = [
    (8, 9),  # L'Oréal <- L'Oreal
]

for keep_id, drop_id in CREATOR_MERGES:
    keep = db.get(Creator, keep_id)
    drop = db.get(Creator, drop_id)
    if not keep or not drop:
        print(f"  [SKIP] creator {keep_id}/{drop_id}: no encontrado")
        continue
    keep_name, drop_name = keep.name, drop.name

    moved = db.query(Ticket).filter(Ticket.creator_id == drop_id).update(
        {"creator_id": keep_id}, synchronize_session=False
    )
    db.flush()
    db.expire(drop)  # drop the stale in-memory `tickets` collection before deleting

    total_spent = sum(
        t.amount for t in db.query(Ticket).filter(Ticket.creator_id == keep_id).all()
    )
    keep.spent_budget = total_spent
    keep.remaining_budget = keep.initial_budget - total_spent

    db.delete(drop)
    db.commit()
    print(f"  [OK] '{keep_name}' (id={keep_id}) <- '{drop_name}' (id={drop_id}): "
          f"{moved} tickets movidos, spent=${total_spent:,.2f}, remaining=${keep.remaining_budget:,.2f}")

for keep_id, drop_id in BRAND_MERGES:
    keep = db.get(Brand, keep_id)
    drop = db.get(Brand, drop_id)
    if not keep or not drop:
        print(f"  [SKIP] brand {keep_id}/{drop_id}: no encontrado")
        continue
    keep_name, drop_name = keep.name, drop.name

    moved = db.query(Ticket).filter(Ticket.brand_id == drop_id).update(
        {"brand_id": keep_id}, synchronize_session=False
    )
    db.flush()
    db.expire(drop)

    db.delete(drop)
    db.commit()
    print(f"  [OK] '{keep_name}' (id={keep_id}) <- '{drop_name}' (id={drop_id}): {moved} tickets movidos")

db.close()

print("\n>>> Fusion completada.")
