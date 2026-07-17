"""Matriz de permisos endpoint x rol: 401 sin token, 403 con rol incorrecto,
200/201 con el rol correcto. Incluye el filtrado por rol de creador (scoping)."""

import pytest

from .conftest import make_ticket

NO_TOKEN_ENDPOINTS = [
    ("get", "/api/creators/"),
    ("get", "/api/creators/kpi"),
    ("get", "/api/creators/1"),
    ("post", "/api/creators/"),
    ("put", "/api/creators/1"),
    ("get", "/api/brands/"),
    ("get", "/api/brands/1"),
    ("post", "/api/brands/"),
    ("put", "/api/brands/1"),
    ("get", "/api/tickets/"),
    ("get", "/api/tickets/brand-spend"),
    ("get", "/api/tickets/file/1"),
    ("post", "/api/tickets/"),
    ("get", "/api/dashboard/summary"),
    ("get", "/api/dashboard/monthly-spend"),
    ("get", "/api/dashboard/creator-usage"),
    ("get", "/api/users/"),
    ("post", "/api/users/"),
    ("get", "/api/users/1"),
    ("put", "/api/users/1"),
    ("post", "/api/users/1/reset-password"),
    ("patch", "/api/users/1/estado"),
    ("get", "/api/auth/me"),
    ("put", "/api/auth/me"),
    ("post", "/api/auth/change-password"),
    ("post", "/api/auth/logout"),
]


@pytest.mark.parametrize("method,path", NO_TOKEN_ENDPOINTS)
def test_rejects_without_token(client, method, path):
    resp = getattr(client, method)(path)
    assert resp.status_code == 401


def test_health_is_public(client):
    assert client.get("/api/health").status_code == 200


def test_uploads_static_mount_removed(client):
    assert client.get("/uploads/tickets/algo.png").status_code == 404


class TestCreatorsPermissions:
    def test_creador_sees_only_own_creator_in_list(self, logged_in_creador, creator_a, creator_b):
        resp = logged_in_creador.get("/api/creators/")
        assert resp.status_code == 200
        ids = [c["id"] for c in resp.json()]
        assert ids == [creator_a.id]

    def test_creador_cannot_see_other_creator_by_id(self, logged_in_creador, creator_b):
        assert logged_in_creador.get(f"/api/creators/{creator_b.id}").status_code == 403

    def test_creador_can_see_own_creator_by_id(self, logged_in_creador, creator_a):
        assert logged_in_creador.get(f"/api/creators/{creator_a.id}").status_code == 200

    def test_creador_cannot_see_kpi(self, logged_in_creador):
        assert logged_in_creador.get("/api/creators/kpi").status_code == 403

    def test_creador_cannot_create_creator(self, logged_in_creador):
        resp = logged_in_creador.post("/api/creators/", json={"name": "Nuevo", "initial_budget": 100})
        assert resp.status_code == 403

    def test_creador_cannot_update_creator(self, logged_in_creador, creator_a):
        resp = logged_in_creador.put(f"/api/creators/{creator_a.id}", json={"name": "Hackeado"})
        assert resp.status_code == 403

    def test_admin_can_list_all_creators(self, logged_in_admin, creator_a, creator_b):
        resp = logged_in_admin.get("/api/creators/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_admin_can_create_and_update_creator(self, logged_in_admin):
        resp = logged_in_admin.post(
            "/api/creators/",
            json={"name": "Nuevo", "cycle_budget_amount": 500, "cycle_period": "mensual"},
        )
        assert resp.status_code == 201
        assert resp.json()["cycle_amount"] == 500
        cid = resp.json()["id"]
        assert logged_in_admin.put(f"/api/creators/{cid}", json={"is_active": False}).status_code == 200

    def test_superadmin_can_see_kpi(self, logged_in_superadmin, creator_a):
        assert logged_in_superadmin.get("/api/creators/kpi").status_code == 200

    def test_creador_cannot_see_other_creators_cycles_idor(self, logged_in_creador, creator_b):
        assert logged_in_creador.get(f"/api/creators/{creator_b.id}/ciclos").status_code == 403

    def test_creador_can_see_own_cycles(self, logged_in_creador, creator_a):
        assert logged_in_creador.get(f"/api/creators/{creator_a.id}/ciclos").status_code == 200

    def test_admin_can_see_any_creator_cycles(self, logged_in_admin, creator_a):
        assert logged_in_admin.get(f"/api/creators/{creator_a.id}/ciclos").status_code == 200


class TestBrandsPermissions:
    def test_creador_can_read_brands(self, logged_in_creador, brand_a):
        assert logged_in_creador.get("/api/brands/").status_code == 200

    def test_creador_cannot_create_brand(self, logged_in_creador):
        assert logged_in_creador.post("/api/brands/", json={"name": "Nueva"}).status_code == 403

    def test_creador_cannot_update_brand(self, logged_in_creador, brand_a):
        resp = logged_in_creador.put(f"/api/brands/{brand_a.id}", json={"name": "Hackeada"})
        assert resp.status_code == 403

    def test_admin_can_create_brand(self, logged_in_admin):
        assert logged_in_admin.post("/api/brands/", json={"name": "Nueva"}).status_code == 201


class TestTicketsPermissionsAndIDOR:
    def test_creador_ticket_list_scoped_to_self(self, logged_in_creador, db, creator_a, creator_b, brand_a):
        make_ticket(db, creator=creator_a, brand=brand_a, amount=50)
        make_ticket(db, creator=creator_b, brand=brand_a, amount=75)

        resp = logged_in_creador.get("/api/tickets/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["creator_id"] == creator_a.id

    def test_creador_ticket_list_ignores_creator_name_filter_override(
        self, logged_in_creador, db, creator_a, creator_b, brand_a
    ):
        make_ticket(db, creator=creator_a, brand=brand_a, amount=50)
        make_ticket(db, creator=creator_b, brand=brand_a, amount=75)

        # Intenta usar el filtro para ver los tickets de otro creador; debe seguir viendo solo los propios.
        resp = logged_in_creador.get(f"/api/tickets/?creator_name={creator_b.name}")
        assert resp.status_code == 200
        assert all(t["creator_id"] == creator_a.id for t in resp.json())

    def test_creador_cannot_download_other_creators_file_idor(self, logged_in_creador, db, creator_b, brand_a):
        ticket = make_ticket(db, creator=creator_b, brand=brand_a, amount=75)
        resp = logged_in_creador.get(f"/api/tickets/file/{ticket.id}")
        assert resp.status_code == 403

    def test_creador_can_download_own_file(self, logged_in_creador, db, creator_a, brand_a):
        ticket = make_ticket(db, creator=creator_a, brand=brand_a, amount=75)
        resp = logged_in_creador.get(f"/api/tickets/file/{ticket.id}")
        assert resp.status_code == 200

    def test_admin_can_download_any_file(self, logged_in_admin, db, creator_a, brand_a):
        ticket = make_ticket(db, creator=creator_a, brand=brand_a, amount=75)
        resp = logged_in_admin.get(f"/api/tickets/file/{ticket.id}")
        assert resp.status_code == 200

    def test_download_nonexistent_ticket_is_404_not_403(self, logged_in_admin):
        assert logged_in_admin.get("/api/tickets/file/999999").status_code == 404

    def test_creador_cannot_create_ticket_for_other_creator_idor(self, logged_in_creador, creator_b, brand_a):
        resp = logged_in_creador.post(
            "/api/tickets/",
            data={"creator_id": str(creator_b.id), "brand_id": str(brand_a.id), "amount": "50"},
            files={"file": ("f.pdf", b"%PDF-1.4", "application/pdf")},
        )
        assert resp.status_code == 403

    def test_creador_can_create_ticket_for_self(self, logged_in_creador, creator_a, brand_a):
        resp = logged_in_creador.post(
            "/api/tickets/",
            data={"creator_id": str(creator_a.id), "brand_id": str(brand_a.id), "amount": "50"},
            files={"file": ("f.pdf", b"%PDF-1.4", "application/pdf")},
        )
        assert resp.status_code == 201

    def test_admin_can_create_ticket_for_any_creator(self, logged_in_admin, creator_a, brand_a):
        resp = logged_in_admin.post(
            "/api/tickets/",
            data={"creator_id": str(creator_a.id), "brand_id": str(brand_a.id), "amount": "50"},
            files={"file": ("f.pdf", b"%PDF-1.4", "application/pdf")},
        )
        assert resp.status_code == 201

    def test_creador_cannot_see_brand_spend(self, logged_in_creador):
        assert logged_in_creador.get("/api/tickets/brand-spend").status_code == 403

    def test_admin_can_see_brand_spend(self, logged_in_admin):
        assert logged_in_admin.get("/api/tickets/brand-spend").status_code == 200


class TestDashboardPermissions:
    @pytest.mark.parametrize(
        "path", ["/api/dashboard/summary", "/api/dashboard/monthly-spend", "/api/dashboard/creator-usage"]
    )
    def test_creador_forbidden(self, logged_in_creador, path):
        assert logged_in_creador.get(path).status_code == 403

    @pytest.mark.parametrize(
        "path", ["/api/dashboard/summary", "/api/dashboard/monthly-spend", "/api/dashboard/creator-usage"]
    )
    def test_admin_allowed(self, logged_in_admin, path):
        assert logged_in_admin.get(path).status_code == 200
