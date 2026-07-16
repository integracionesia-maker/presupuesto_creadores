"""Seed idempotente de autenticación: crea la cuenta superadmin y, opcionalmente,
usuarios rol 'creador' vinculados a los Creator existentes que aún no tienen usuario.

Uso (ejecutar SIEMPRE desde backend/, igual que seed.py y uvicorn):
    python seed_auth.py
    python seed_auth.py --vincular-creadores
    python seed_auth.py --username admin --email admin@grupo-ortiz.com --password "Clave-Segura1"

Sin --password, se genera una contraseña temporal aleatoria (se imprime una sola vez).
"""

import argparse
import os
import unicodedata

from app.database import SessionLocal, engine, Base
from app import models, security

Base.metadata.create_all(bind=engine)


def _slugify(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    return normalized.lower().replace(" ", ".")


def _unique_username(db, base: str) -> str:
    username = base
    suffix = 1
    while db.query(models.User).filter(models.User.username == username).first():
        suffix += 1
        username = f"{base}{suffix}"
    return username


def seed_superadmin(db, username: str, email: str, password: str) -> models.User:
    existing = (
        db.query(models.User)
        .filter(models.User.role == models.UserRole.SUPERADMIN.value)
        .first()
    )
    if existing:
        print(f"Ya existe un superadmin ('{existing.username}'); no se crea uno nuevo.")
        return existing

    if password:
        error = security.validate_password_strength(password, username)
        if error:
            raise SystemExit(f"Contraseña inválida: {error}")
    else:
        password = security.generate_temp_password()
        print(f"Contraseña temporal generada para '{username}': {password}")

    user = models.User(
        username=username,
        email=email,
        password_hash=security.hash_password(password),
        full_name="Superadministrador",
        role=models.UserRole.SUPERADMIN.value,
        is_active=True,
        must_change_password=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Superadmin '{username}' creado. Deberá cambiar la contraseña en el primer login.")
    return user


def vincular_creadores(db) -> None:
    sin_usuario_ids = db.query(models.User.creator_id).filter(models.User.creator_id.isnot(None))
    creadores = db.query(models.Creator).filter(~models.Creator.id.in_(sin_usuario_ids)).all()

    if not creadores:
        print("Todos los creadores ya tienen un usuario vinculado.")
        return

    for creator in creadores:
        username = _unique_username(db, _slugify(creator.name))
        temp_password = security.generate_temp_password()
        user = models.User(
            username=username,
            email=f"{username}@creadores.grupo-ortiz.com",
            password_hash=security.hash_password(temp_password),
            full_name=creator.name,
            role=models.UserRole.CREADOR.value,
            creator_id=creator.id,
            is_active=True,
            must_change_password=True,
        )
        db.add(user)
        db.commit()
        print(f"  - {creator.name}: usuario '{username}', contraseña temporal '{temp_password}'")

    print(f"Usuarios 'creador' creados: {len(creadores)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed de autenticación (superadmin + opcional usuarios creador).")
    parser.add_argument("--username", default=os.getenv("SUPERADMIN_USERNAME", "superadmin"))
    parser.add_argument("--email", default=os.getenv("SUPERADMIN_EMAIL", "superadmin@grupo-ortiz.com"))
    parser.add_argument("--password", default=os.getenv("SUPERADMIN_PASSWORD", ""))
    parser.add_argument(
        "--vincular-creadores",
        action="store_true",
        help="Crea un usuario rol 'creador' para cada Creator existente sin usuario vinculado.",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        seed_superadmin(db, args.username, args.email, args.password)
        if args.vincular_creadores:
            vincular_creadores(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
