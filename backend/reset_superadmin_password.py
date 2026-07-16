"""Recuperación de emergencia: resetea la contraseña del superadmin directamente
en la base de datos cuando se perdió el acceso y no se puede usar la API
(el rol/estado del superadmin es inmutable por API a propósito — ver
doc/auth-arquitectura.md §Decisiones).

Ejecutar desde backend/:
    python reset_superadmin_password.py --password "NuevaClaveSegura123!"
"""

import argparse

from app import models, security
from app.database import SessionLocal


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resetea la contraseña del superadmin (recuperación de emergencia)."
    )
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    db = SessionLocal()
    try:
        user = (
            db.query(models.User)
            .filter(models.User.role == models.UserRole.SUPERADMIN.value)
            .first()
        )
        if not user:
            raise SystemExit("No existe una cuenta superadmin. Usa seed_auth.py para crear una.")

        error = security.validate_password_strength(args.password, user.username)
        if error:
            raise SystemExit(f"Contraseña inválida: {error}")

        user.password_hash = security.hash_password(args.password)
        user.must_change_password = True
        user.is_active = True
        user.failed_login_attempts = 0
        user.locked_until = None
        user.token_version += 1  # invalida cualquier sesión/token previo
        db.commit()
        print(f"Contraseña de '{user.username}' actualizada. Deberá cambiarla de nuevo en el próximo login.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
