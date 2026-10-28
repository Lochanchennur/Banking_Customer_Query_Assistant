import pytest

def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "operational"
    assert "demo_mode" in data

def test_login_success(client):
    res = client.post("/api/auth/login", json={
        "email": "demo.rajesh@nexabank.internal",
        "password": "demo123"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["customer"]["name"] == "Rajesh Kumar"

def test_login_failure(client):
    res = client.post("/api/auth/login", json={
        "email": "demo.rajesh@nexabank.internal",
        "password": "wrongpassword"
    })
    assert res.status_code == 401

def test_auth_me(client, rajesh_token):
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {rajesh_token}"})
    assert res.status_code == 200
    assert res.json()["id"] == "cust_rajesh"

def test_auth_missing_token(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401

def test_cross_customer_isolation_explicit_proof(client, rajesh_token, priya_token):
    """
    CRITICAL SECURITY TEST:
    Explicitly proves that Customer A (Rajesh) CANNOT access Customer B's (Priya's)
    account details or balance, and receives a 403 Forbidden.
    """
    # Priya's account is 'acc_priya_chk'
    priya_account_id = "acc_priya_chk"

    # 1. Priya can access her own account
    priya_res = client.get(
        f"/api/accounts/{priya_account_id}",
        headers={"Authorization": f"Bearer {priya_token}"}
    )
    assert priya_res.status_code == 200
    assert priya_res.json()["customer_id"] == "cust_priya"

    # 2. Rajesh attempts to access Priya's account
    rajesh_res = client.get(
        f"/api/accounts/{priya_account_id}",
        headers={"Authorization": f"Bearer {rajesh_token}"}
    )
    assert rajesh_res.status_code == 403
    assert "Access forbidden" in rajesh_res.json()["detail"]

    # 3. Rajesh attempts to query balance of Priya's account
    rajesh_bal_res = client.get(
        f"/api/accounts/{priya_account_id}/balance",
        headers={"Authorization": f"Bearer {rajesh_token}"}
    )
    assert rajesh_bal_res.status_code == 403

    # 4. Rajesh lists transactions: ensure NO transactions belonging to Priya are ever returned
    rajesh_txns = client.get(
        "/api/transactions",
        headers={"Authorization": f"Bearer {rajesh_token}"}
    ).json()
    for txn in rajesh_txns["items"]:
        assert txn["customer_id"] == "cust_rajesh"
        assert txn["account_id"] != priya_account_id
