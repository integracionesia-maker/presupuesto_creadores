"""Migración única: agrega la columna `brand_id` a `general_expenses` para
vincular cada gasto general a una marca (R12.1).

Ejecutar UNA sola vez, desde `backend/`:
    python migrate_add_brand_to_general_expenses.py

Es idempotente — si la columna ya existe, no hace nada.
"""

import sqlite3
from pathlib import Path

from app.database import DATABASE_URL

DB_PATH = DATABASE_URL.replace("sqlite:///", "")


def _existing_columns(cursor, table: str) -> set:
    cursor.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cursor.fetchall()}


def _brand_exists(cursor, brand_id: int) -> bool:
    cursor.execute("SELECT id FROM brands WHERE id = ?", (brand_id,))
    return cursor.fetchone() is not None


def migrate():
    if not Path(DB_PATH).exists():
        print(f"No existe {DB_PATH} — no hay nada que migrar.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Verificar si la columna ya existe
    columns = _existing_columns(cursor, "general_expenses")
    if "brand_id" in columns:
        print("'general_expenses' ya tiene brand_id — sin cambios.")
        conn.close()
        return

    # 2. Asegurar que haya al menos una marca para el valor por defecto
    cursor.execute("SELECT id FROM brands WHERE is_active = 1 ORDER BY id LIMIT 1")
    row = cursor.fetchone()
    if row:
        default_brand = row[0]
    else:
        # Crear una marca por defecto si no hay ninguna
        cursor.execute(
            "INSERT INTO brands (name, priority, is_active) VALUES (?, ?, ?)",
            ("Gastos Generales", "media", 1),
        )
        conn.commit()
        default_brand = cursor.lastrowid
        print(f"Marca 'Gastos Generales' creada (id={default_brand}).")

    # 3. Agregar la columna con un default (SQLite requiere DEFAULT para
    #    columnas nuevas en tablas con datos existentes)
    print(f"Agregando brand_id a 'general_expenses' (default={default_brand})...")
    cursor.execute(
        f"ALTER TABLE general_expenses ADD COLUMN brand_id INTEGER NOT NULL DEFAULT {default_brand} "
        "REFERENCES brands(id)"
    )
    conn.commit()
    print("Listo: 'general_expenses' actualizada.")

    conn.close()


if __name__ == "__main__":
    migrate()
