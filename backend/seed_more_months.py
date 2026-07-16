"""Extend test data across more months so dashboard charts have richer history.

Adds tickets spread over the last 12 months (instead of the ~2 months
seed_test_data.py covers), sized so each creator's remaining budget is
respected. Safe to run once on top of the existing seed_test_data.py data.
"""

import random
import struct
import uuid
import zlib
from calendar import monthrange
from datetime import datetime, timezone
from pathlib import Path

from app.database import SessionLocal
from app.models import Creator, Brand, Ticket
from app.upload_manager import UPLOAD_DIR

random.seed(7)

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

db = SessionLocal()

creators = db.query(Creator).filter(Creator.is_active == True).all()
brands = db.query(Brand).filter(Brand.is_active == True).all()

if not creators or not brands:
    print("ERROR: Necesitas correr seed.py primero para poblar creadores y marcas.")
    db.close()
    exit(1)


def _make_dummy_png():
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    idat = zlib.compress(b"\x00\x80\x80\x80")
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def _make_dummy_pdf():
    return (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
        b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n"
        b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"
    )


DUMMY_GENERATORS = {".png": _make_dummy_png, ".jpg": _make_dummy_png, ".pdf": _make_dummy_pdf}
MIME_MAP = {".png": "image/png", ".jpg": "image/jpeg", ".pdf": "application/pdf"}
EXTENSIONS = [".png", ".jpg", ".pdf"]

NOTE_TEMPLATES = [
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

# ── Build the last 12 (year, month) pairs ending at the current month ──────
today = datetime.now(timezone.utc)
MONTHS = []
y, m = today.year, today.month
for _ in range(12):
    MONTHS.append((y, m))
    m -= 1
    if m == 0:
        m = 12
        y -= 1
MONTHS.reverse()  # chronological order, oldest first

created = 0
skipped = 0

for creator in creators:
    running_remaining = creator.remaining_budget
    if running_remaining < 100:
        print(f"  [SKIP creator] {creator.name}: sin presupuesto restante (${running_remaining:,.2f})")
        continue

    num_tickets = random.randint(7, 11)
    chosen_months = sorted(random.sample(MONTHS, k=min(num_tickets, len(MONTHS))))
    # allow a couple of months to get a second ticket for busier history
    extra = random.sample(MONTHS, k=max(0, num_tickets - len(chosen_months)))
    all_months = sorted(chosen_months + extra)

    per_ticket_budget = running_remaining / (len(all_months) * 1.8)

    for (yy, mm) in all_months:
        if running_remaining < 100:
            break

        amount = per_ticket_budget * random.uniform(0.5, 1.5)
        amount = min(amount, running_remaining * 0.9)
        amount = round(amount / 50) * 50  # round to nearest $50
        if amount < 50:
            amount = min(50, running_remaining)

        brand = random.choice(brands)
        note = random.choice(NOTE_TEMPLATES).format(brand=brand.name)
        ext = random.choice(EXTENSIONS)

        gen = DUMMY_GENERATORS[ext]
        file_bytes = gen()
        unique_name = f"{uuid.uuid4().hex}{ext}"
        dest = UPLOAD_DIR / unique_name
        dest.write_bytes(file_bytes)

        last_day = monthrange(yy, mm)[1]
        day = random.randint(1, last_day)
        upload_date = datetime(
            yy, mm, day,
            hour=random.randint(8, 21), minute=random.randint(0, 59),
            tzinfo=timezone.utc,
        )
        if upload_date > today:
            upload_date = today

        creator.spent_budget += amount
        creator.remaining_budget = creator.initial_budget - creator.spent_budget
        running_remaining -= amount

        ticket = Ticket(
            creator_id=creator.id,
            brand_id=brand.id,
            amount=amount,
            file_name=unique_name,
            file_path=str(dest.resolve()),
            mime_type=MIME_MAP[ext],
            upload_date=upload_date,
            notes=note,
        )
        db.add(ticket)
        created += 1

    print(f"  [OK] {creator.name}: {len(all_months)} tickets nuevos, resta ${running_remaining:,.2f}")

db.commit()
db.close()

print(f"\n>>> {created} tickets nuevos creados (12 meses de historial), {skipped} omitidos.")

db2 = SessionLocal()
all_creators = db2.query(Creator).filter(Creator.is_active == True).all()
print("\nEstado de presupuestos:")
for c in all_creators:
    pct = (c.spent_budget / c.initial_budget * 100) if c.initial_budget > 0 else 0
    bar = "#" * int(pct / 5) + "-" * (20 - int(pct / 5))
    print(f"  {c.name:<20s}  {bar}  ${c.remaining_budget:>10,.2f} / ${c.initial_budget:>10,.2f}  ({pct:.0f}%)")
db2.close()
