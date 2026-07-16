"""Login, cambio de contraseña, bloqueo por intentos fallidos, rate limiting,
rotación/reuso de refresh token y logout."""

from .conftest import (
    PASSWORD_CREADOR,
    PASSWORD_SUPERADMIN,
    login,
    make_user,
)


def test_login_success_returns_user_and_cookies(client, creador_user):
    resp = login(client, creador_user.username, PASSWORD_CREADOR)
    assert resp.status_code == 200
    body = resp.json()
    assert body["user"]["username"] == creador_user.username
    assert body["user"]["role"] == "creador"
    assert "access_token" in resp.cookies
    assert "refresh_token" in resp.cookies


def test_login_wrong_password_generic_message(client, creador_user):
    resp = login(client, creador_user.username, "clave-incorrecta-123")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Usuario o contraseña incorrectos."


def test_login_unknown_user_same_generic_message(client):
    resp = login(client, "no-existe", "cualquier-cosa-123")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Usuario o contraseña incorrectos."


def test_login_inactive_account_same_generic_message(client, db):
    make_user(db, username="inactivo", password="ClaveValida123!", role="creador", is_active=False)
    resp = login(client, "inactivo", "ClaveValida123!")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Usuario o contraseña incorrectos."


def test_login_by_email_also_works(client, creador_user):
    resp = login(client, creador_user.email, PASSWORD_CREADOR)
    assert resp.status_code == 200


def test_must_change_password_flag_present(client, db):
    make_user(db, username="nuevo", password="ClaveTemporal123!", role="creador", must_change_password=True)
    resp = login(client, "nuevo", "ClaveTemporal123!")
    assert resp.json()["user"]["must_change_password"] is True


def test_account_lockout_after_five_failed_attempts(client, creador_user):
    for _ in range(5):
        r = login(client, creador_user.username, "clave-mala")
        assert r.status_code == 401

    resp = login(client, creador_user.username, PASSWORD_CREADOR)
    assert resp.status_code == 401
    assert "bloqueada" in resp.json()["detail"].lower()


def test_ip_rate_limit_returns_429(client):
    for _ in range(30):
        client.post("/api/auth/login", json={"identificador": "x", "password": "y"})
    resp = client.post("/api/auth/login", json={"identificador": "x", "password": "y"})
    assert resp.status_code == 429


def test_change_password_requires_correct_current_password(logged_in_creador):
    resp = logged_in_creador.post(
        "/api/auth/change-password",
        json={"current_password": "clave-incorrecta", "new_password": "NuevaClaveValida123!"},
    )
    assert resp.status_code == 400


def test_change_password_rejects_weak_composition(logged_in_creador):
    resp = logged_in_creador.post(
        "/api/auth/change-password",
        json={"current_password": PASSWORD_CREADOR, "new_password": "sololetrassinnumero"},
    )
    assert resp.status_code == 400


def test_change_password_success_and_old_password_stops_working(client, creador_user):
    login(client, creador_user.username, PASSWORD_CREADOR)
    resp = client.post(
        "/api/auth/change-password",
        json={"current_password": PASSWORD_CREADOR, "new_password": "NuevaClaveValida123!"},
    )
    assert resp.status_code == 200

    # La sesion actual sigue viva (se reemitieron las cookies)
    assert client.get("/api/auth/me").status_code == 200

    # Login en un cliente nuevo: la clave vieja ya no sirve, la nueva si.
    from fastapi.testclient import TestClient
    from app.main import app

    other = TestClient(app)
    assert login(other, creador_user.username, PASSWORD_CREADOR).status_code == 401
    assert login(other, creador_user.username, "NuevaClaveValida123!").status_code == 200


def test_refresh_rotates_cookie(client, creador_user):
    login(client, creador_user.username, PASSWORD_CREADOR)
    old_refresh = client.cookies.get("refresh_token")

    resp = client.post("/api/auth/refresh")
    assert resp.status_code == 200
    new_refresh = client.cookies.get("refresh_token")
    assert new_refresh is not None
    assert new_refresh != old_refresh


def test_refresh_reuse_detected_revokes_chain(client, creador_user):
    login(client, creador_user.username, PASSWORD_CREADOR)
    old_refresh = client.cookies.get("refresh_token")

    assert client.post("/api/auth/refresh").status_code == 200
    new_refresh = client.cookies.get("refresh_token")

    # Reutilizar el token viejo (ya rotado) debe ser rechazado...
    client.cookies.set("refresh_token", old_refresh)
    assert client.post("/api/auth/refresh").status_code == 401

    # ...y debe haber revocado también el token nuevo (toda la cadena).
    client.cookies.set("refresh_token", new_refresh)
    assert client.post("/api/auth/refresh").status_code == 401


def test_refresh_without_cookie_is_401(client):
    assert client.post("/api/auth/refresh").status_code == 401


def test_logout_revokes_refresh_and_access(client, creador_user):
    login(client, creador_user.username, PASSWORD_CREADOR)
    assert client.get("/api/auth/me").status_code == 200

    logout_resp = client.post("/api/auth/logout")
    assert logout_resp.status_code == 200

    assert client.get("/api/auth/me").status_code == 401
    assert client.post("/api/auth/refresh").status_code == 401


def test_password_cannot_equal_username(client, db):
    # Username de 10+ caracteres para aislar la regla de igualdad de la de longitud mínima.
    long_username = "usuariolargo"
    make_user(db, username=long_username, password=PASSWORD_CREADOR, role="creador")
    login(client, long_username, PASSWORD_CREADOR)

    resp = client.post(
        "/api/auth/change-password",
        json={"current_password": PASSWORD_CREADOR, "new_password": long_username},
    )
    assert resp.status_code == 400
    assert "igual al nombre de usuario" in resp.json()["detail"]
