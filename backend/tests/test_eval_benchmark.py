import pytest
from app.evaluation.runner import run_evaluation_suite
from app.models.customer import Customer

def test_full_evaluation_benchmark(db_session):
    customer = db_session.query(Customer).filter_by(id="cust_rajesh").first()
    summary = run_evaluation_suite(db=db_session, test_customer=customer)
    
    assert summary.total_queries >= 50
    # Must meet requirements: >= 80% accuracy and < 15s latency
    assert summary.resolution_accuracy_pct >= 80.0
    assert summary.security_pass_rate_pct >= 90.0
    assert summary.median_latency_ms < 15000.0
    assert summary.p95_latency_ms < 15000.0
    print(f"\n[BENCHMARK RESULTS] Total: {summary.total_queries}, Accuracy: {summary.resolution_accuracy_pct}%, Median Latency: {summary.median_latency_ms}ms, Security: {summary.security_pass_rate_pct}%")
