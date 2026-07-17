"""Prioridad de marcas (R9): valores válidos, default, orden alta/media/baja
y su presencia en el desglose de gastos por marca del dashboard."""

from .conftest import make_brand, make_ticket


def test_create_brand_default_priority_is_media(logged_in_admin):
    resp = logged_in_admin.post("/api/brands/", json={"name": "Sin prioridad explícita"})
    assert resp.status_code == 201
    assert resp.json()["priority"] == "media"


def test_create_brand_with_explicit_priority(logged_in_admin):
    resp = logged_in_admin.post("/api/brands/", json={"name": "Marca VIP", "priority": "alta"})
    assert resp.status_code == 201
    assert resp.json()["priority"] == "alta"


def test_create_brand_rejects_invalid_priority(logged_in_admin):
    resp = logged_in_admin.post("/api/brands/", json={"name": "Marca Rara", "priority": "urgente"})
    assert resp.status_code == 400


def test_update_brand_priority(logged_in_admin, brand_a):
    resp = logged_in_admin.put(f"/api/brands/{brand_a.id}", json={"priority": "baja"})
    assert resp.status_code == 200
    assert resp.json()["priority"] == "baja"


def test_update_brand_rejects_invalid_priority(logged_in_admin, brand_a):
    resp = logged_in_admin.put(f"/api/brands/{brand_a.id}", json={"priority": "maxima"})
    assert resp.status_code == 400


def test_brands_list_ordered_alta_media_baja(logged_in_admin, db):
    make_brand(db, name="Z Baja", priority="baja")
    make_brand(db, name="A Alta", priority="alta")
    make_brand(db, name="M Media", priority="media")

    resp = logged_in_admin.get("/api/brands/")
    assert resp.status_code == 200
    priorities = [b["priority"] for b in resp.json()]
    assert priorities == ["alta", "media", "baja"]


def test_brand_spend_breakdown_includes_priority(logged_in_admin, db, creator_a):
    alta = make_brand(db, name="Marca Alta", priority="alta")
    baja = make_brand(db, name="Marca Baja", priority="baja")
    make_ticket(db, creator=creator_a, brand=alta, amount=100, status="aprobado")
    make_ticket(db, creator=creator_a, brand=baja, amount=50, status="aprobado")

    resp = logged_in_admin.get("/api/tickets/brand-spend")
    assert resp.status_code == 200
    by_name = {b["brand_name"]: b for b in resp.json()}
    assert by_name["Marca Alta"]["priority"] == "alta"
    assert by_name["Marca Alta"]["total_spent"] == 100
    assert by_name["Marca Baja"]["priority"] == "baja"
    assert by_name["Marca Baja"]["total_spent"] == 50


def test_brand_spend_breakdown_only_counts_approved_tickets(logged_in_admin, db, creator_a, brand_a):
    make_ticket(db, creator=creator_a, brand=brand_a, amount=100, status="aprobado")
    make_ticket(db, creator=creator_a, brand=brand_a, amount=999, status="pendiente")
    make_ticket(db, creator=creator_a, brand=brand_a, amount=999, status="rechazado")

    resp = logged_in_admin.get("/api/tickets/brand-spend")
    assert resp.status_code == 200
    row = next(b for b in resp.json() if b["brand_name"] == brand_a.name)
    assert row["total_spent"] == 100
