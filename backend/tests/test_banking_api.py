import pytest

def test_dashboard_summary(client, rajesh_token):
    res = client.get("/api/dashboard", headers={"Authorization": f"Bearer {rajesh_token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["customer_name"] == "Rajesh Kumar"
    assert data["total_balance"] > 0
    assert len(data["accounts"]) == 2
    assert "recent_transactions" in data
    assert "category_spending" in data

def test_list_accounts(client, rajesh_token):
    res = client.get("/api/accounts", headers={"Authorization": f"Bearer {rajesh_token}"})
    assert res.status_code == 200
    accounts = res.json()
    assert len(accounts) == 2
    for acc in accounts:
        assert acc["customer_id"] == "cust_rajesh"
        assert "••••" in acc["account_number_masked"]

def test_transactions_filtering(client, rajesh_token):
    # Filter by DINING
    res = client.get(
        "/api/transactions?category=DINING",
        headers={"Authorization": f"Bearer {rajesh_token}"}
    )
    assert res.status_code == 200
    data = res.json()
    for item in data["items"]:
        assert item["category"] == "DINING"

    # Search filter
    res_search = client.get(
        "/api/transactions?search=Swiggy",
        headers={"Authorization": f"Bearer {rajesh_token}"}
    )
    assert res_search.status_code == 200
    search_data = res_search.json()
    assert search_data["total_count"] >= 1
    assert "Swiggy" in search_data["items"][0]["merchant_or_description"]

def test_spending_insights(client, rajesh_token):
    res = client.get(
        "/api/insights/spending?period=this_month",
        headers={"Authorization": f"Bearer {rajesh_token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["period"] == "this_month"
    assert "by_category" in data
    assert "largest_expenses" in data
    assert "monthly_trends" in data

def test_products_and_rates(client):
    res = client.get("/api/products/rates")
    assert res.status_code == 200
    data = res.json()
    assert "rates" in data
    assert len(data["rates"]) >= 4

def test_loan_eligibility_approved(client, rajesh_token):
    # Rajesh has 1.45L income and 785 credit score
    res = client.post(
        "/api/loans/eligibility",
        json={
            "product_type": "PERSONAL_LOAN",
            "requested_amount": 300000,
            "tenure_months": 36,
            "declared_existing_emis": 5000
        },
        headers={"Authorization": f"Bearer {rajesh_token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["eligible"] is True
    assert data["status"] in ["APPROVED", "CONDITIONAL"]
    assert "disclaimer" in data
    assert "Illustrative demonstration" in data["disclaimer"]

def test_loan_eligibility_rejected_excessive_amount(client, priya_token):
    # Priya requests 50L personal loan (exceeds product max and DTI ceiling)
    res = client.post(
        "/api/loans/eligibility",
        json={
            "product_type": "PERSONAL_LOAN",
            "requested_amount": 50000000,
            "tenure_months": 12,
            "declared_existing_emis": 40000
        },
        headers={"Authorization": f"Bearer {priya_token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["eligible"] is False
    assert data["status"] == "REJECTED"
