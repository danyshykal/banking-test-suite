"""Transaction history: order, running balance, and only successful operations recorded."""
from decimal import Decimal

import pytest

pytestmark = pytest.mark.regression


def test_TC_TXN_01_history_is_newest_first(bank):
    """REQ-11"""
    acc = bank.new_account()
    bank.deposit(acc, "100.00")
    bank.withdraw(acc, "30.00")
    bank.deposit(acc, "5.00")
    assert [t["type"] for t in bank.transactions(acc)] == ["deposit", "withdrawal", "deposit"]
    assert bank.transactions(acc)[0]["amount"] == "5.00"


def test_TC_TXN_02_balance_after_matches_running_total(bank):
    """REQ-11: every entry's balance_after is the previous balance plus its amount."""
    acc = bank.new_account()
    for amount in ("250.00", "99.99", "0.01"):
        bank.deposit(acc, amount)
    bank.withdraw(acc, "150.00")
    running = Decimal("0.00")
    for entry in reversed(bank.transactions(acc)):      # oldest first
        running += Decimal(entry["amount"])
        assert Decimal(entry["balance_after"]) == running
    assert bank.balance(acc) == "200.00"


def test_TC_TXN_03_failed_operations_are_not_recorded(bank):
    """REQ-11: a rejected withdrawal must not appear in the history."""
    acc = bank.new_account(balance="10.00")
    bank.withdraw(acc, "999.00")          # rejected: insufficient funds
    bank.deposit(acc, "-5.00")            # rejected: negative amount
    assert len(bank.transactions(acc)) == 1
