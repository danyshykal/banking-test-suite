"""Smoke tests: the fastest checks that the build is alive and the core flow works. Run these first."""
import pytest

pytestmark = [pytest.mark.smoke, pytest.mark.regression]


def test_TC_SMK_01_health_check(base_url, release):
    """REQ-13"""
    import requests
    response = requests.get(f"{base_url}/health", timeout=10)
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "release": release}


def test_TC_SMK_02_core_banking_flow(bank):
    """REQ-01, REQ-04, REQ-05: open an account, deposit, withdraw, check balance."""
    acc = bank.new_account("Aisyah")
    assert bank.deposit(acc, "500.00").status_code == 200
    assert bank.withdraw(acc, "120.50").status_code == 200
    assert bank.balance(acc) == "379.50"
