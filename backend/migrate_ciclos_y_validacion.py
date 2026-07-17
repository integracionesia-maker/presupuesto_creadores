"""Migración idempotente para R7 (ciclos de presupuesto), R9 (prioridad de marcas)
y R10 (estados de ticket) — ver doc/mejoras-diseno-fase1.md.

Ejecutar SIEMPRE desde backend/ (mismo requisito que seed.py / uvicorn):
    python migrate_ciclos_y_validacion.py

Seguro de correr más de una vez: cada ALTER TABLE se salta si la columna ya
existe; los UPDATE de backfill son idempotentes (solo tocan filas sin migrar).
"""

from app.database import Base, SessionLocal, engine
from app import models

# Nuevas tablas (budget_cycles) — aditivo, no toca las existentes.
Base.metadata.create_all(bind=engine)


def _existing_columns(conn, table: str) -> set:
    rows = conn.exec_driver_sql(f"PRAGMA table_info({table})").fetchall()
    return {row[1] for row in rows}


def _add_column_if_missing(conn, table: str, column: str, ddl: str) -> None:
    if column not in _existing_columns(conn, table):
        conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {ddl}")
        print(f"  + {table}.{column} agregada")
    else:
        print(f"  = {table}.{column} ya existía")


def migrate_schema() -> None:
    with engine.begin() as conn:
        print("Creators:")
        _add_column_if_missing(conn, "creators", "cycle_budget_amount", "cycle_budget_amount FLOAT")
        _add_column_if_missing(conn, "creators", "cycle_period", "cycle_period VARCHAR(20)")

        print("Brands:")
        _add_column_if_missing(
            conn, "brands", "priority", "priority VARCHAR(20) NOT NULL DEFAULT 'media'"
        )

        print("Tickets:")
        _add_column_if_missing(
            conn, "tickets", "status", "status VARCHAR(20) NOT NULL DEFAULT 'pendiente'"
        )
        _add_column_if_missing(conn, "tickets", "rejection_reason", "rejection_reason TEXT")
        _add_column_if_missing(
            conn, "tickets", "reviewed_by_user_id", "reviewed_by_user_id INTEGER"
        )
        _add_column_if_missing(conn, "tickets", "reviewed_at", "reviewed_at DATETIME")
        _add_column_if_missing(conn, "tickets", "budget_cycle_id", "budget_cycle_id INTEGER")


def backfill_data() -> None:
    db = SessionLocal()
    try:
        # Todo ticket que exista AL MOMENTO de esta migración es histórico pre-validación.
        updated_tickets = (
            db.query(models.Ticket)
            .filter(models.Ticket.status != models.TicketStatus.APROBADO.value)
            .update({"status": models.TicketStatus.APROBADO.value}, synchronize_session=False)
        )
        db.commit()
        print(f"Tickets marcados como 'aprobado' (histórico pre-validación): {updated_tickets}")

        creators = (
            db.query(models.Creator).filter(models.Creator.cycle_budget_amount.is_(None)).all()
        )
        for creator in creators:
            creator.cycle_period = models.CyclePeriod.MENSUAL.value
            creator.cycle_budget_amount = round((creator.initial_budget or 0.0) / 12, 2)
        db.commit()
        print(f"Creadores con ciclo configurado por primera vez: {len(creators)}")
        for creator in creators:
            print(f"  - {creator.name}: {creator.cycle_period}, monto ${creator.cycle_budget_amount:,.2f}")
    finally:
        db.close()


if __name__ == "__main__":
    print("=== Migrando esquema ===")
    migrate_schema()
    print("=== Backfill de datos ===")
    backfill_data()
    print("Migración completa.")
