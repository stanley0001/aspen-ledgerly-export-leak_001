"""Load-bearing legitimate-flow smoke tests for ledgerly."""


def test_login_admin_returns_token(client):
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token"]
    assert body["role"] == "ADMIN"


def test_login_user_returns_token(client):
    response = client.post(
        "/auth/login",
        json={"username": "alice", "password": "alice123"},
    )
    assert response.status_code == 200
    assert response.json()["token"]


def test_login_wrong_password_is_401(client):
    response = client.post(
        "/auth/login",
        json={"username": "alice", "password": "wrong"},
    )
    assert response.status_code == 401


def test_list_invoices_returns_only_owned_rows_for_user(client, user_token, auth_header):
    response = client.get("/invoices", headers=auth_header(user_token))
    assert response.status_code == 200
    rows = response.json()
    assert [row["invoice_id"] for row in rows] == ["inv-1001", "inv-1002"]


def test_list_invoices_returns_all_rows_for_admin(client, admin_token, auth_header):
    response = client.get("/invoices", headers=auth_header(admin_token))
    assert response.status_code == 200
    rows = response.json()
    assert {row["invoice_id"] for row in rows} == {"inv-1001", "inv-1002", "inv-2001"}


def test_get_invoice_detail_is_customer_safe(client, user_token, auth_header):
    response = client.get("/invoices/inv-1001", headers=auth_header(user_token))
    assert response.status_code == 200
    body = response.json()
    assert body["invoice_id"] == "inv-1001"
    assert body["customer_name"] == "Acme Retail"
    assert body["visible_notes"]
    assert "collection_notes" not in body
    assert "fraud_score" not in body
    assert "payment_token_hint" not in body
    assert "supplier_cost_cents" not in body["line_items"][0]


def test_owner_customer_preview_export_works(client, user_token, auth_header):
    response = client.get(
        "/invoices/inv-1001/export-preview",
        headers=auth_header(user_token),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["scope"] == "customer"
    assert body["customer_name"] == "Acme Retail"
    assert body["line_items"][0]["sku"] == "plan-pro"
    assert "collection_notes" not in body


def test_owner_customer_download_export_works(client, user_token, auth_header):
    response = client.get(
        "/invoices/inv-1001/export-download",
        headers=auth_header(user_token),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["file_name"] == "inv-1001-customer.json"
    assert body["export"]["scope"] == "customer"
    assert body["export"]["visible_notes"]
    assert "payment_token_hint" not in body["export"]


def test_owner_customer_share_export_works(client, user_token, auth_header):
    response = client.post(
        "/invoices/inv-1001/share-export",
        headers=auth_header(user_token),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["share_id"] == "shr-inv-1001-customer"
    assert body["export"]["scope"] == "customer"
    assert body["export"]["customer_name"] == "Acme Retail"


def test_admin_internal_preview_export_works(client, admin_token, auth_header):
    response = client.get(
        "/invoices/inv-1001/export-preview?scope=internal",
        headers=auth_header(admin_token),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["scope"] == "internal"
    assert body["collection_notes"] == "Needs CFO sign-off before discounting."
    assert body["line_items"][0]["supplier_cost_cents"] == 45000


def test_cross_owner_access_is_403_for_non_admin(client, bob_token, auth_header):
    response = client.get(
        "/invoices/inv-1001/export-preview",
        headers=auth_header(bob_token),
    )
    assert response.status_code == 403


def test_unauthenticated_export_preview_is_401(client):
    response = client.get("/invoices/inv-1001/export-preview")
    assert response.status_code == 401
