"""Monthly interest on savings: balance x 2.5% / 12, rounded half-up to the nearest sen."""
import pytest

pytestmark = pytest.mark.regression


def test_TC_INT_01_monthly_interest_on_savings(bank):
    """REQ-10: 1200.00 x 0.025 / 12 = 2.50 exactly."""
    acc = bank.new_account(account_type="savings", balance="1200.00")
    response = bank.apply_interest(acc)
    assert response.status_code == 200
    assert response.json() == {"interest": "2.50", "balance": "1202.50"}
    assert bank.transactions(acc)[0]["type"] == "interest"


def test_TC_INT_02_interest_rounds_half_up(bank):
    """REQ-10, BVA on rounding: 12.00 x 0.025 / 12 = 0.025, exactly half a sen.
    Half-up gives 0.03. Banker's rounding (half-even) would give 0.02 (regression R3 in v1.1)."""
    acc = bank.new_account(account_type="savings", balance="12.00")
    assert bank.apply_interest(acc).json()["interest"] == "0.03"
    assert bank.balance(acc) == "12.03"


def test_TC_INT_03_no_interest_on_checking(bank):
    """REQ-10, EP: checking accounts are outside the valid partition."""
    acc = bank.new_account(account_type="checking", balance="1200.00")
    assert bank.apply_interest(acc).status_code == 400
    assert bank.balance(acc) == "1200.00"


def test_TC_INT_04_zero_balance_earns_nothing(bank):
    """REQ-10, BVA: lowest possible balance. No interest, and no empty transaction recorded."""
    acc = bank.new_account(account_type="savings")
    assert bank.apply_interest(acc).json()["interest"] == "0.00"
    assert bank.transactions(acc) == []
