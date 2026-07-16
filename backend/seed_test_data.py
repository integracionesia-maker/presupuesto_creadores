"""Generate realistic test data: tickets with dummy files and updated budgets."""

import io
import os
import random
import struct
import uuid
import zlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.database import SessionLocal
from app.models import Creator, Brand, Ticket
from app.upload_manager import UPLOAD_DIR

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

db = SessionLocal()

creators = db.query(Creator).filter(Creator.is_active == True).all()
brands = db.query(Brand).filter(Brand.is_active == True).all()

if not creators or not brands:
    print("ERROR: Necesitas correr seed.py primero para poblar creadores y marcas.")
    db.close()
    exit(1)

# ── Helper: create a minimal valid PNG in memory ────────────────────────────
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

DUMMY_GENERATORS = {
    ".png": _make_dummy_png,
    ".jpg": _make_dummy_png,
    ".pdf": _make_dummy_pdf,
}

# ── Ticket scenarios ────────────────────────────────────────────────────────
ticket_scenarios = [
    (0, 0, 12_500.00, "Campana Instagram - 3 stories + 1 reel", ".png"),
    (0, 2, 8_200.00, "Post patrocinado Coca-Cola - feed", ".jpg"),
    (0, 4, 15_000.00, "Playlist curada Spotify - 4 semanas", ".pdf"),
    (1, 1, 5_750.00, "Unboxing Galaxy S25 - YouTube", ".png"),
    (1, 3, 22_300.00, "Review compras Amazon - TikTok + Instagram", ".pdf"),
    (2, 0, 45_000.00, "Campana completa Nike - 5 piezas", ".pdf"),
    (2, 5, 9_800.00, "Tutorial Photoshop - Reel", ".jpg"),
    (2, 6, 18_500.00, "Microsoft 365 - video productividad", ".png"),
    (3, 7, 3_200.00, "Skincare routine L'Oreal - stories", ".png"),
    (3, 2, 7_100.00, "Coca-Cola comida familiar - TikTok", ".jpg"),
    (4, 4, 11_300.00, "Podcast patrocinado Spotify - 2 episodios", ".pdf"),
    (4, 0, 28_000.00, "Nike Air Max - campana lanzamiento", ".png"),
    (5, 3, 6_400.00, "Haul Amazon - YouTube Shorts", ".jpg"),
    (5, 1, 13_600.00, "Samsung Galaxy Watch - review", ".pdf"),
    (5, 6, 4_900.00, "Windows 12 tip - reel rapido", ".png"),
    (1, 5, 19_200.00, "Adobe Creative Cloud - tutorial avanzado", ".pdf"),
    (2, 7, 7_800.00, "L'Oreal maquillaje - tutorial paso a paso", ".jpg"),
    (3, 0, 2_500.00, "Nike - mencion en video larga duracion", ".png"),
    (4, 2, 8_900.00, "Coca-Cola Zero - campana verano", ".pdf"),
    (0, 6, 33_000.00, "Microsoft Surface - review + unboxing", ".pdf"),
]

# ── Create tickets ──────────────────────────────────────────────────────────
created = 0
base_date = datetime.now(timezone.utc) - timedelta(days=60)

for i, (c_idx, b_idx, amount, notes, ext) in enumerate(ticket_scenarios):
    creator = creators[c_idx]
    brand = brands[b_idx]

    gen = DUMMY_GENERATORS.get(ext, _make_dummy_png)
    file_bytes = gen()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    dest = UPLOAD_DIR / unique_name
    dest.write_bytes(file_bytes)

    mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".pdf": "application/pdf"}

    if creator.remaining_budget < amount:
        print(f"  [SKIP] Ticket #{i+1}: {creator.name} sin presupuesto (${creator.remaining_budget:,.2f} < ${amount:,.2f})")
        dest.unlink()
        continue

    creator.spent_budget += amount
    creator.remaining_budget = creator.initial_budget - creator.spent_budget

    upload_date = base_date + timedelta(days=random.randint(0, 58), hours=random.randint(0, 23))

    ticket = Ticket(
        creator_id=creator.id,
        brand_id=brand.id,
        amount=amount,
        file_name=unique_name,
        file_path=str(dest.resolve()),
        mime_type=mime_map[ext],
        upload_date=upload_date,
        notes=notes,
    )
    db.add(ticket)
    created += 1
    print(f"  [OK] Ticket #{created}: {creator.name} -> {brand.name} | ${amount:,.2f} | {ext}")

db.commit()
db.close()

print(f"\n>>> {created} tickets creados exitosamente.")
print(f"Archivos dummy en: {UPLOAD_DIR.resolve()}")

# ── Summary ─────────────────────────────────────────────────────────────────
db2 = SessionLocal()
all_creators = db2.query(Creator).filter(Creator.is_active == True).all()
print("\nEstado de presupuestos despues de los tickets:")
for c in all_creators:
    pct = (c.spent_budget / c.initial_budget * 100) if c.initial_budget > 0 else 0
    bar = "#" * int(pct / 5) + "-" * (20 - int(pct / 5))
    print(f"  {c.name:<20s}  {bar}  ${c.remaining_budget:>10,.2f} / ${c.initial_budget:>10,.2f}  ({pct:.0f}%)")
db2.close()
