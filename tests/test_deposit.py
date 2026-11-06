"""Deposits. Techniques: boundary value analysis on the amount, equivalence partitioning on input type."""
import pytest

pytestmark = pytest.mark.regression


def test_TC_DEP_01_deposit_increases_balance(bank):
    """REQ-04, REQ-11"""
    acc = bank.new_account()
    response = bank.deposit(acc, "100.00")
    assert response.status_code == 200
    assert response.json()["balance"] == "100.00"
    latest = bank.transactions(acc)[0]
    assert latest["type"] == "deposit"
    assert latest["amount"] == "100.00"


@pytest.mark.parametrize("amount", ["0.01", "50000.00"],
                         ids=["TC_DEP_02a_minimum_0.01", "TC_DEP_02b_maximum_50000.00"])
def test_deposit_valid_boundaries(bank, amount):
    """REQ-04, BVA: the smallest and largest allowed amounts are accepted."""
    acc = bank.new_account()
    assert bank.deposit(acc, amount).status_code == 200
    assert bank.balance(acc) == amount


@pytest.mark.parametrize("amount", ["0", "0.00", "-10.00", "50000.01"],
                         ids=["TC_DEP_03a_zero", "TC_DEP_03b_zero_with_cents",
                              "TC_DEP_03c_negative", "TC_DEP_03d_just_over_max"])
def test_deposit_invalid_boundaries(bank, amount):
    """REQ-04, BVA: values just outside the allowed range are rejected and nothing changes."""
    acc = bank.new_account()
    assert bank.deposit(acc, amount).status_code == 400
    assert bank.balance(acc) == "0.00"


def test_TC_DEP_04_more_than_two_decimals_rejected(bank):
    """REQ-04: there is no such thing as a tenth of a sen."""
    acc = bank.new_account()
    assert bank.deposit(acc, "10.005").status_code == 400


@pytest.mark.parametrize("amount", ["abc", None, True, "NaN"],
                         ids=["TC_DEP_05a_text", "TC_DEP_05b_missing", "TC_DEP_05c_boolean", "TC_DEP_05d_nan"])
def test_deposit_non_numeric_rejected(bank, amount):
    """REQ-04, EP: invalid input types."""
    acc = bank.new_account()
    assert bank.deposit(acc, amount).status_code == 400


def test_TC_DEP_06_amounts_add_up_exactly(bank):
    """REQ-12: with floats, 0.1 + 0.2 = 0.30000000000000004. A bank must get exactly 0.30."""
    acc = bank.new_account()
    bank.deposit(acc, 0.1)
    bank.deposit(acc, 0.2)
    assert bank.balance(acc) == "0.30"


def test_TC_DEP_07_deposit_to_frozen_account_rejected(bank):
    """REQ-08 (regression R5 in v1.1)"""
    acc = bank.new_account(balance="50.00")
    bank.freeze(acc)
    assert bank.deposit(acc, "10.00").status_code == 409
    assert bank.balance(acc) == "50.00"
