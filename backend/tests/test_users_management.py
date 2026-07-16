"""Reglas de gestión de usuarios: alcance de admin (solo rol creador + a sí mismo),
inmutabilidad del superadmin, y auto-desactivación con confirmación."""

from .conftest import make_user


def test_creador_forbidden_from_user_management(logged_in_creador):
    assert logged_in_creador.get("/api/users/").status_code == 403


def test_admin_sees_only_creador_users_and_self(logged_in_admin, admin_user, creador_user):
    resp = logged_in_admin.get("/api/users/")
    assert resp.status_code == 200
    by_username = {u["username"]: u["role"] for u in resp.json()}
    assert by_username[creador_user.username] == "creador"
    assert by_username[admin_user.username] == "admin"
    assert set(by_username.values()) <= {"creador", "admin"}


def test_superadmin_sees_all_roles(logged_in_superadmin, superadmin_user, admin_user, creador_user):
    resp = logged_in_superadmin.get("/api/users/")
    usernames = {u["username"] for u in resp.json()}
    assert {superadmin_user.username, admin_user.username, creador_user.username} <= usernames


def test_admin_cannot_create_admin(logged_in_admin):
    resp = logged_in_admin.post(
        "/api/users/",
        json={
            "username": "otro.admin",
            "email": "otro.admin@test.com",
            "full_name": "Otro Admin",
            "role": "admin",
            "password": "ClaveValida123!",
        },
    )
    assert resp.status_code == 403


def test_admin_can_create_creador_linked_to_a_creator(logged_in_admin, creator_b):
    resp = logged_in_admin.post(
        "/api/users/",
        json={
            "username": "nuevo.creador",
            "email": "nuevo.creador@test.com",
            "full_name": "Nuevo Creador",
            "role": "creador",
            "creator_id": creator_b.id,
            "password": "ClaveValida123!",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["must_change_password"] is True


def test_superadmin_cannot_create_superadmin(logged_in_superadmin):
    resp = logged_in_superadmin.post(
        "/api/users/",
        json={
            "username": "otro.sa",
            "email": "otro.sa@test.com",
            "full_name": "Otro SA",
            "role": "superadmin",
            "password": "ClaveValida123!",
        },
    )
    assert resp.status_code == 400


def test_admin_cannot_view_or_edit_other_admin(logged_in_admin, db):
    other_admin = make_user(db, username="admin2", password="Clave123456!", role="admin")
    assert logged_in_admin.get(f"/api/users/{other_admin.id}").status_code == 403
    assert logged_in_admin.put(f"/api/users/{other_admin.id}", json={"full_name": "Hackeado"}).status_code == 403


def test_admin_cannot_reset_password_of_other_admin(logged_in_admin, db):
    other_admin = make_user(db, username="admin3", password="Clave123456!", role="admin")
    assert logged_in_admin.post(f"/api/users/{other_admin.id}/reset-password").status_code == 403


def test_superadmin_role_immutable(logged_in_superadmin, superadmin_user):
    resp = logged_in_superadmin.put(f"/api/users/{superadmin_user.id}", json={"role": "admin"})
    assert resp.status_code == 403


def test_superadmin_status_immutable(logged_in_superadmin, superadmin_user):
    resp = logged_in_superadmin.patch(f"/api/users/{superadmin_user.id}/estado", json={"is_active": False})
    assert resp.status_code == 403


def test_admin_self_deactivate_requires_confirmation(logged_in_admin, admin_user):
    resp = logged_in_admin.patch(f"/api/users/{admin_user.id}/estado", json={"is_active": False})
    assert resp.status_code == 400

    resp2 = logged_in_admin.patch(
        f"/api/users/{admin_user.id}/estado",
        json={"is_active": False, "confirm_username": admin_user.username},
    )
    assert resp2.status_code == 200
    assert resp2.json()["is_active"] is False


def test_admin_self_deactivate_wrong_confirmation_rejected(logged_in_admin, admin_user):
    resp = logged_in_admin.patch(
        f"/api/users/{admin_user.id}/estado",
        json={"is_active": False, "confirm_username": "nombre-incorrecto"},
    )
    assert resp.status_code == 400


def test_deactivated_user_cannot_login(logged_in_superadmin, creador_user):
    from .conftest import PASSWORD_CREADOR, login
    from fastapi.testclient import TestClient
    from app.main import app

    resp = logged_in_superadmin.patch(f"/api/users/{creador_user.id}/estado", json={"is_active": True})
    assert resp.status_code == 200
    resp = logged_in_superadmin.patch(f"/api/users/{creador_user.id}/estado", json={"is_active": False})
    assert resp.status_code == 200

    other = TestClient(app)
    login_resp = login(other, creador_user.username, PASSWORD_CREADOR)
    assert login_resp.status_code == 401


def test_reset_password_returns_temporary_password_once(logged_in_superadmin, creador_user):
    resp = logged_in_superadmin.post(f"/api/users/{creador_user.id}/reset-password")
    assert resp.status_code == 200
    assert len(resp.json()["temporary_password"]) > 0


def test_weak_password_rejected_on_create(logged_in_superadmin):
    resp = logged_in_superadmin.post(
        "/api/users/",
        json={
            "username": "debil",
            "email": "debil@test.com",
            "full_name": "Debil",
            "role": "creador",
            "password": "short1",
        },
    )
    assert resp.status_code in (400, 422)


def test_creador_role_requires_creator_id(logged_in_superadmin):
    resp = logged_in_superadmin.post(
        "/api/users/",
        json={
            "username": "sin.creador",
            "email": "sin.creador@test.com",
            "full_name": "Sin Creador",
            "role": "creador",
            "password": "ClaveValida123!",
        },
    )
    assert resp.status_code == 400
