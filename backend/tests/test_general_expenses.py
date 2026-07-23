"""Gastos generales (R12.1): gastos operativos vinculados a una marca.
Solo admin/superadmin; sin ciclo ni validacion — se registran de inmediato.
Ver doc/gastos-generales-manual.md."""

from pathlib import Path


def _create(client, brand_id, amount=100, description="Suscripcion software"):
    return client.post(
        "/api/general-expenses/",
        data={"brand_id": str(brand_id), "amount": str(amount), "description": description},
        files={"file": ("f.pdf", b"%PDF-1.4", "application/pdf")},
    )


def test_create_general_expense_as_admin(logged_in_admin, brand_a):
    resp = _create(logged_in_admin, brand_id=brand_a.id, amount=1500, description="Licencia Adobe")
    assert resp.status_code == 201
    body = resp.json()
    assert body["amount"] == 1500
    assert body["description"] == "Licencia Adobe"
    assert body["is_deleted"] is False
    assert body["brand_id"] == brand_a.id
    assert body["brand_name"] == "Marca A"


def test_create_general_expense_as_creator(logged_in_creador, brand_a):
    assert _create(logged_in_creador, brand_id=brand_a.id).status_code == 403


def test_create_general_expense_unauthenticated(client, brand_a):
    assert _create(client, brand_id=brand_a.id).status_code == 401


def test_create_general_expense_nonexistent_brand(logged_in_admin):
    resp = _create(logged_in_admin, brand_id=9999)
    assert resp.status_code == 404


def test_create_general_expense_inactive_brand(logged_in_admin, db):
    from app import models
    brand = models.Brand(name="Inactiva", priority="media", is_active=False)
    db.add(brand)
    db.commit()
    db.refresh(brand)

    resp = _create(logged_in_admin, brand_id=brand.id)
    assert resp.status_code == 400


def test_list_general_expenses(logged_in_admin, brand_a):
    _create(logged_in_admin, brand_id=brand_a.id, amount=100)
    _create(logged_in_admin, brand_id=brand_a.id, amount=200)

    resp = logged_in_admin.get("/api/general-expenses/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_list_general_expenses_excludes_deleted(logged_in_admin, brand_a):
    e1 = _create(logged_in_admin, brand_id=brand_a.id, amount=100).json()
    _create(logged_in_admin, brand_id=brand_a.id, amount=200)
    logged_in_admin.post(f"/api/general-expenses/{e1['id']}/soft-delete")

    resp = logged_in_admin.get("/api/general-expenses/")
    ids = [e["id"] for e in resp.json()]
    assert e1["id"] not in ids
    assert len(resp.json()) == 1


def test_soft_delete_general_expense(logged_in_admin, brand_a):
    expense = _create(logged_in_admin, brand_id=brand_a.id).json()
    resp = logged_in_admin.post(f"/api/general-expenses/{expense['id']}/soft-delete")
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_deleted"] is True
    assert body["deleted_at"] is not None


def test_hard_delete_general_expense(logged_in_admin, brand_a):
    expense = _create(logged_in_admin, brand_id=brand_a.id).json()
    file_path = Path(expense["file_path"])
    assert file_path.exists()

    resp = logged_in_admin.delete(f"/api/general-expenses/{expense['id']}/permanent")
    assert resp.status_code == 200
    assert not file_path.exists()
    assert logged_in_admin.get("/api/general-expenses/").json() == []


def test_soft_delete_as_creator_forbidden(logged_in_admin, logged_in_creador, brand_a):
    expense = _create(logged_in_admin, brand_id=brand_a.id).json()
    resp = logged_in_creador.post(f"/api/general-expenses/{expense['id']}/soft-delete")
    assert resp.status_code == 403


def test_hard_delete_as_creator_forbidden(logged_in_admin, logged_in_creador, brand_a):
    expense = _create(logged_in_admin, brand_id=brand_a.id).json()
    resp = logged_in_creador.delete(f"/api/general-expenses/{expense['id']}/permanent")
    assert resp.status_code == 403


def test_monthly_endpoint(logged_in_admin, brand_a):
    _create(logged_in_admin, brand_id=brand_a.id, amount=1000)
    _create(logged_in_admin, brand_id=brand_a.id, amount=500)

    resp = logged_in_admin.get("/api/dashboard/general-expenses-monthly")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["total"] == 1500
    assert body[0]["count"] == 2


def test_monthly_excludes_deleted(logged_in_admin, brand_a):
    e1 = _create(logged_in_admin, brand_id=brand_a.id, amount=1000).json()
    _create(logged_in_admin, brand_id=brand_a.id, amount=500)
    logged_in_admin.post(f"/api/general-expenses/{e1['id']}/soft-delete")

    resp = logged_in_admin.get("/api/dashboard/general-expenses-monthly")
    body = resp.json()
    assert body[0]["total"] == 500
    assert body[0]["count"] == 1


def test_monthly_forbidden_for_creador(logged_in_creador):
    assert logged_in_creador.get("/api/dashboard/general-expenses-monthly").status_code == 403


def test_export_endpoint(logged_in_admin, brand_a):
    e1 = _create(logged_in_admin, brand_id=brand_a.id, amount=1000).json()
    month = e1["upload_date"][:7]

    resp = logged_in_admin.get(f"/api/general-expenses/export?months={month}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1000
    assert len(body["items"]) == 1
    assert body["months"] == [month]


def test_export_excludes_deleted(logged_in_admin, brand_a):
    e1 = _create(logged_in_admin, brand_id=brand_a.id, amount=1000).json()
    e2 = _create(logged_in_admin, brand_id=brand_a.id, amount=500).json()
    month = e1["upload_date"][:7]
    logged_in_admin.post(f"/api/general-expenses/{e1['id']}/soft-delete")

    resp = logged_in_admin.get(f"/api/general-expenses/export?months={month}")
    body = resp.json()
    assert body["total"] == 500
    assert len(body["items"]) == 1
    assert body["items"][0]["id"] == e2["id"]


def test_export_requires_at_least_one_month(logged_in_admin):
    resp = logged_in_admin.get("/api/general-expenses/export?months=")
    assert resp.status_code == 400


def test_download_general_expense_file(logged_in_admin, brand_a):
    expense = _create(logged_in_admin, brand_id=brand_a.id).json()
    resp = logged_in_admin.get(f"/api/general-expenses/{expense['id']}/file")
    assert resp.status_code == 200


def test_download_deleted_general_expense_file_is_404(logged_in_admin, brand_a):
    expense = _create(logged_in_admin, brand_id=brand_a.id).json()
    logged_in_admin.post(f"/api/general-expenses/{expense['id']}/soft-delete")
    resp = logged_in_admin.get(f"/api/general-expenses/{expense['id']}/file")
    assert resp.status_code == 404
