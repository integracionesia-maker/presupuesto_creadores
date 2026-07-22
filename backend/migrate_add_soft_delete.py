"""Migración única: agrega columnas de borrado lógico a `tickets` y crea la
tabla `general_expenses` si no existe.

Ejecutar UNA sola vez, desde `backend/`, antes de levantar el backend con
estos cambios: `python migrate_add_soft_delete.py`. Es idempotente — si se
corre dos veces, detecta las columnas/tabla ya existentes y no hace nada.
"""

import sqlite3
from pathlib import Path

from app.database import DATABASE_URL, Base, engine
from app import models  # noqa: F401 — registra GeneralExpense en Base.metadata

DB_PATH = DATABASE_URL.replace("sqlite:///", "")


def _existing_columns(cursor, table: str) -> set:
    cursor.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cursor.fetchall()}


def migrate():
    if not Path(DB_PATH).exists():
        print(f"No existe {DB_PATH} todavía — no hay nada que migrar (se creará vacía al arrancar el backend).")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    columns = _existing_columns(cursor, "tickets")
    if "is_deleted" not in columns:
        print("Agregando columnas de soft-delete a 'tickets'...")
        cursor.execute("ALTER TABLE tickets ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT 0")
        cursor.execute("ALTER TABLE tickets ADD COLUMN deleted_at DATETIME")
        cursor.execute("ALTER TABLE tickets ADD COLUMN deleted_by_user_id INTEGER REFERENCES users(id)")
        conn.commit()
        print("Listo: 'tickets' actualizada.")
    else:
        print("'tickets' ya tiene columnas de soft-delete — sin cambios.")

    conn.close()

    print("Creando tabla 'general_expenses' si no existe...")
    Base.metadata.create_all(bind=engine, tables=[models.GeneralExpense.__table__])
    print("Listo.")


if __name__ == "__main__":
    migrate()
