"""Password hashing, JWT access tokens, refresh-token helpers and login rate limiting."""

import hashlib
import os
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerifyMismatchError

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_COOKIE_PATH = "/api/auth"
IS_PRODUCTION = os.getenv("ENV", "development") == "production"


def _jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET_KEY", "")
    if not secret:
        raise RuntimeError(
            "JWT_SECRET_KEY no esta configurado. Defina esta variable de entorno "
            "(ver .env.example) antes de levantar el backend."
        )
    return secret


_hasher = PasswordHasher()


# ── Contraseñas ─────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, InvalidHash):
        return False


def needs_rehash(password_hash: str) -> bool:
    return _hasher.check_needs_rehash(password_hash)


def validate_password_strength(password: str, username: str) -> Optional[str]:
    """Devuelve un mensaje de error en español, o None si la contraseña es válida."""
    if len(password) < 10:
        return "La contraseña debe tener al menos 10 caracteres."
    if password.lower() == username.lower():
        return "La contraseña no puede ser igual al nombre de usuario."
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    if not (has_letter and has_digit):
        return "La contraseña debe combinar letras y números."
    return None


def generate_temp_password() -> str:
    return f"Temporal-{secrets.token_hex(4)}"


# ── Access token (JWT) ──────────────────────────────────────────────────────

def create_access_token(user_id: int, role: str, token_version: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "tv": token_version,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, _jwt_secret(), algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


# ── Refresh token (opaco, hasheado en DB) ───────────────────────────────────

def generate_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def refresh_token_expiry() -> datetime:
    # Naive UTC: SQLite devuelve datetimes sin tzinfo, y se compara contra este valor
    # (ver routers/auth.py:refresh) — debe quedar en el mismo formato para poder comparar.
    return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)


# ── Rate limiting en memoria por IP (defensa adicional al bloqueo por cuenta) ─
# Proceso único (uvicorn sin --workers) — el contador vive en memoria y se
# reinicia si el proceso se reinicia; no es distribuido. Ver doc/auth-diseno-fase1.md §0.6.

_LOGIN_WINDOW_SECONDS = 15 * 60
_MAX_ATTEMPTS_PER_IP = 30

_login_attempts_by_ip: dict[str, list[float]] = {}


def register_login_attempt(ip: str) -> None:
    now = time.monotonic()
    cutoff = now - _LOGIN_WINDOW_SECONDS
    attempts = [t for t in _login_attempts_by_ip.get(ip, []) if t >= cutoff]
    attempts.append(now)
    _login_attempts_by_ip[ip] = attempts


def is_ip_rate_limited(ip: str) -> bool:
    now = time.monotonic()
    cutoff = now - _LOGIN_WINDOW_SECONDS
    attempts = [t for t in _login_attempts_by_ip.get(ip, []) if t >= cutoff]
    return len(attempts) >= _MAX_ATTEMPTS_PER_IP
