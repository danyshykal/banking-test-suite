"""Withdrawals. Technique: boundary value analysis around the balance and the RM 5,000 limit."""
import pytest

pytestmark = pytest.mark.regression


def test_TC_WD_01_withdraw_within_balance(bank):
    """REQ-05"""
    acc = bank.new_account(balance="200.00")
    response = bank.withdraw(acc, "75.25")
    assert response.status_code == 200
    assert response.json()["balance"] == "124.75"


def test_TC_WD_02_withdraw_exact_full_balance(bank):
    """REQ-05, BVA on the balance: amount == balance is allowed (regression R4 in v1.1)."""
    acc = bank.new_account(balance="80.00")
    assert bank.withdraw(acc, "80.00").status_code == 200
    assert bank.balance(acc) == "0.00"


def test_TC_WD_03_withdraw_one_sen_over_balance(bank):
    """REQ-05, BVA: balance + 0.01 is rejected and the balance is untouched."""
    acc = bank.new_account(balance="80.00")
    response = bank.withdraw(acc, "80.01")
    assert response.status_code == 400
    assert response.json()["error"] == "Insufficient funds"
    assert bank.balance(acc) == "80.00"


@pytest.mark.parametrize("amount, expected_status", [("5000.00", 200), ("5000.01", 400)],
                         ids=["TC_WD_04a_limit_exactly_5000", "TC_WD_04b_limit_plus_0.01"])
def test_withdrawal_limit(bank, amount, expected_status):
    """REQ-05, BVA on the per-transaction limit (account has enough money either way)."""
    acc = bank.new_account(balance="10000.00")
    assert bank.withdraw(acc, amount).status_code == expected_status


def test_TC_WD_05_withdraw_from_frozen_account_rejected(bank):
    """REQ-08"""
    acc = bank.new_account(balance="100.00")
    bank.freeze(acc)
    assert bank.withdraw(acc, "10.00").status_code == 409
    assert bank.balance(acc) == "100.00"
