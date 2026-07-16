"""Seed the database with ~12 months of realistic ticket history.

Simula un año productivo: tickets mensuales por creador con estacionalidad,
afinidades creador-marca, notas ocasionales y comprobantes PNG en
uploads/tickets/. Actualiza spent_budget/remaining_budget de forma
consistente con la lógica de create_ticket_transactional.

Ejecutar desde backend/:  python seed_demo_year.py [--force]
(sin --force conserva los tickets existentes y agrega histórico alrededor;
--force borra todos los tickets y sus archivos, y reinicia presupuestos)
"""

import random
import struct
import sys
import uuid
import zlib
from datetime import datetime, timedelta
from pathlib import Path

from app.database import SessionLocal, engine, Base
from app import models

Base.metadata.create_all(bind=engine)

random.seed(20260716)  # reproducible

UPLOAD_DIR = Path("./uploads/tickets")
TODAY = datetime(2026, 7, 16, 12, 0, 0)
MONTHS_BACK = 12

# Peso relativo de gasto por mes (índice 0 = hace 11 meses, 11 = mes actual).
# Simula arranque suave, picos en Buen Fin/Navidad (nov-dic) y mayo.
SEASONALITY = [0.6, 0.7, 0.8, 1.0, 1.5, 1.6, 0.9, 0.7, 0.9, 1.3, 1.0, 0.5]

# Qué fracción de su presupuesto anual gasta cada creador.
SPEND_RATIO = {
    "Mariana López": 0.88,
    "Carlos Mendoza": 0.79,
    "Valentina Ruiz": 0.92,
    "Diego Fernández": 0.71,
    "Sofía Herrera": 0.84,
    "Alejandro Torres": 0.95,
}

# Afinidades creador → marcas (pesos para elegir la marca de cada ticket).
BRAND_AFFINITY = {
    "Mariana López": {"L'Oréal": 5, "Nike": 3, "Spotify": 2, "Coca-Cola": 1},
    "Carlos Mendoza": {"Samsung": 4, "Microsoft": 3, "Amazon": 2, "Adobe": 1},
    "Valentina Ruiz": {"Nike": 4, "Coca-Cola": 3, "Spotify": 3, "Amazon": 1},
    "Diego Fernández": {"Adobe": 4, "Microsoft": 3, "Samsung": 2},
    "Sofía Herrera": {"Coca-Cola": 4, "L'Oréal": 3, "Amazon": 2, "Nike": 1},
    "Alejandro Torres": {"Spotify": 4, "Amazon": 3, "Samsung": 2, "Adobe": 2},
}

NOTES_POOL = [
    "Campaña en Instagram Stories.",
    "Colaboración video unboxing.",
    "Post patrocinado + reel.",
    "Activación en evento presencial.",
    "Producción de contenido para TikTok.",
    "Sesión de fotos para catálogo.",
    "Renovación de licencias de software.",
    "Giveaway con la comunidad.",
    "Cobertura de lanzamiento de producto.",
    None, None, None, None,  # ~30% de tickets sin nota
]


def make_receipt_png(label: str) -> bytes:
    """PNG 1x1 válido (gris) — placeholder liviano de comprobante."""
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 0, 0, 0, 0)  # 1x1, grayscale
    idat = zlib.compress(b"\x00\xc8")
    text = chunk(b"tEXt", b"Comment\x00" + label.encode("latin-1", "replace"))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr) + text + chunk(b"IDAT", idat) + chunk(b"IEND", b"")
    )


def month_start(offset_back: int) -> datetime:
    """Primer día del mes `offset_back` meses antes del mes actual."""
    y, m = TODAY.year, TODAY.month
    m -= offset_back
    while m <= 0:
        m += 12
        y -= 1
    return datetime(y, m, 1)


def random_datetime_in_month(start: datetime) -> datetime:
    """Fecha hábil aleatoria dentro del mes (sin pasar de hoy)."""
    if start.month == 12:
        end = datetime(start.year + 1, 1, 1)
    else:
        end = datetime(start.year, start.month + 1, 1)
    end = min(end, TODAY)
    for _ in range(20):
        dt = start + timedelta(
            days=random.randrange(max((end - start).days, 1)),
            hours=random.randint(9, 19),
            minutes=random.randrange(60),
        )
        if dt.weekday() < 6 and dt <= TODAY:  # lun-sáb
            return dt
    return start + timedelta(days=1, hours=12)


def main() -> None:
    force = "--force" in sys.argv
    db = SessionLocal()

    existing = db.query(models.Ticket).count()
    if existing and force:
        for t in db.query(models.Ticket).all():
            Path(t.file_path).unlink(missing_ok=True)
        db.query(models.Ticket).delete()
        for c in db.query(models.Creator).all():
            c.spent_budget = 0.0
            c.remaining_budget = c.initial_budget
        db.commit()
        print(f"Eliminados {existing} tickets previos; presupuestos reiniciados.")
    elif existing:
        print(f"Conservando {existing} tickets existentes; se agrega histórico alrededor.")

    creators = db.query(models.Creator).filter(models.Creator.is_active == True).all()
    brands = {b.name: b for b in db.query(models.Brand).all()}
    if not creators or not brands:
        print("Faltan creadores o marcas — ejecuta primero seed.py.")
        db.close()
        return

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    season_total = sum(SEASONALITY)
    created = 0

    for creator in creators:
        ratio = SPEND_RATIO.get(creator.name, 0.8)
        annual_target = creator.initial_budget * ratio
        affinity = BRAND_AFFINITY.get(creator.name)
        pool = (
            [(brands[n], w) for n, w in affinity.items() if n in brands]
            if affinity
            else [(b, 1) for b in brands.values()]
        )
        names = [b for b, _ in pool]
        weights = [w for _, w in pool]

        for offset in range(MONTHS_BACK - 1, -1, -1):
            month_budget = annual_target * SEASONALITY[MONTHS_BACK - 1 - offset] / season_total
            spent_month = 0.0
            while spent_month < month_budget * 0.9:
                amount = round(random.uniform(0.05, 0.35) * month_budget, 2)
                amount = max(amount, 350.0)
                if spent_month + amount > month_budget * 1.05:
                    amount = round(month_budget - spent_month, 2)
                if amount < 350.0 or creator.remaining_budget < amount:
                    break

                when = random_datetime_in_month(month_start(offset))
                brand = random.choices(names, weights=weights)[0]
                label = f"{creator.name} - {brand.name} - {when:%Y-%m-%d}"
                unique_name = f"{uuid.uuid4().hex}.png"
                dest = UPLOAD_DIR / unique_name
                dest.write_bytes(make_receipt_png(label))

                creator.spent_budget += amount
                creator.remaining_budget = creator.initial_budget - creator.spent_budget
                db.add(
                    models.Ticket(
                        creator_id=creator.id,
                        brand_id=brand.id,
                        amount=amount,
                        file_name=unique_name,
                        file_path=str(dest.resolve()),
                        mime_type="image/png",
                        upload_date=when,
                        notes=random.choice(NOTES_POOL),
                    )
                )
                spent_month += amount
                created += 1

        db.commit()
        print(
            f"  {creator.name}: gastado ${creator.spent_budget:,.2f} "
            f"de ${creator.initial_budget:,.2f} "
            f"({creator.spent_budget / creator.initial_budget:.0%})"
        )

    total = db.query(models.Ticket).count()
    db.close()
    print(f"\nListo: {created} tickets creados ({total} en total).")


if __name__ == "__main__":
    main()
