"""
Transfers. Technique: decision table.

| Same account? | Both exist? | Both active? | Enough for amount + fee? | Different owners? | Result          |
|---------------|-------------|--------------|--------------------------|-------------------|-----------------|
| yes           | -           | -            | -                        | -                 | 400             |
| no            | no          | -            | -                        | -                 | 404             |
| no            | yes         | no           | -                        | -                 | 409             |
| no            | yes         | yes          | no                       | -                 | 400             |
| no            | yes         | yes          | yes                      | no                | 201, no fee     |
| no            | yes         | yes          | yes                      | yes               | 201, RM1.00 fee |
"""
from decimal import Decimal

import pytest


@pytest.mark.smoke
@pytest.mark.regression
def test_TC_TRF_01_transfer_between_own_accounts(bank):
    """REQ-06, REQ-07: own-account transfers move money and are always free (regression R1 in v1.1)."""
    checking = bank.new_account("Aisyah", "checking", balance="500.00")
    savings = bank.new_account("Aisyah", "savings")
    response = bank.transfer(checking, savings, "200.00")
    assert response.status_code == 201
    assert response.json()["fee"] == "0.00"
    assert bank.balance(checking) == "300.00"
    assert bank.balance(savings) == "200.00"


@pytest.mark.new_feature
@pytest.mark.since("1.1")
def test_TC_TRF_02_fee_charged_between_different_customers(bank):
    """REQ-07 (new in v1.1): RM1.00 fee when sender and receiver are different customers."""
    sender = bank.new_account("Aisyah", balance="500.00")
    receiver = bank.new_account("Ravi")
    response = bank.transfer(sender, receiver, "100.00")
    assert response.status_code == 201
    assert response.json()["fee"] == "1.00"
    assert bank.balance(sender) == "399.00"       # 500 - 100 - 1 fee
    assert bank.balance(receiver) == "100.00"     # receiver gets the full amount


@pytest.mark.new_feature
@pytest.mark.since("1.1")
def test_TC_TRF_03_fee_recorded_as_separate_transaction(bank):
    """REQ-07, REQ-11"""
    sender = bank.new_account("Aisyah", balance="500.00")
    receiver = bank.new_account("Ravi")
    bank.transfer(sender, receiver, "100.00")
    latest_two = [(t["type"], t["amount"]) for t in bank.transactions(sender)[:2]]
    assert latest_two == [("fee", "-1.00"), ("transfer_out", "-100.00")]


@pytest.mark.regression
def test_TC_TRF_04_cannot_transfer_to_same_account(bank):
    """REQ-06, decision table row 1"""
    acc = bank.new_account(balance="100.00")
    assert bank.transfer(acc, acc, "10.00").status_code == 400
    assert bank.balance(acc) == "100.00"


@pytest.mark.regression
def test_TC_TRF_05_unknown_destination(bank):
    """REQ-06, decision table row 2: no money leaves the source."""
    acc = bank.new_account(balance="100.00")
    assert bank.transfer(acc, "9999999999", "10.00").status_code == 404
    assert bank.balance(acc) == "100.00"


@pytest.mark.regression
@pytest.mark.parametrize("frozen_side", ["source", "destination"],
                         ids=["TC_TRF_06a_frozen_source", "TC_TRF_06b_frozen_destination"])
def test_transfer_with_frozen_account(bank, frozen_side):
    """REQ-08, decision table row 3"""
    source = bank.new_account("Aisyah", balance="100.00")
    dest = bank.new_account("Aisyah")
    bank.freeze(source if frozen_side == "source" else dest)
    assert bank.transfer(source, dest, "10.00").status_code == 409
    assert bank.balance(source) == "100.00"
    assert bank.balance(dest) == "0.00"


@pytest.mark.regression
def test_TC_TRF_07_insufficient_funds(bank):
    """REQ-06, decision table row 4: both balances unchanged."""
    source = bank.new_account("Aisyah", balance="50.00")
    dest = bank.new_account("Aisyah")
    assert bank.transfer(source, dest, "50.01").status_code == 400
    assert bank.balance(source) == "50.00"
    assert bank.balance(dest) == "0.00"


@pytest.mark.new_feature
@pytest.mark.since("1.1")
def test_TC_TRF_08_funds_must_cover_amount_plus_fee(bank):
    """REQ-06, REQ-07, BVA: sending your exact balance to another customer leaves no room
    for the fee, so it must be rejected, never leave a negative balance (regression R2 in v1.1)."""
    sender = bank.new_account("Aisyah", balance="100.00")
    receiver = bank.new_account("Ravi")
    assert bank.transfer(sender, receiver, "100.00").status_code == 400
    assert bank.balance(sender) == "100.00"


@pytest.mark.regression
def test_TC_TRF_09_receiver_history_shows_incoming_transfer(bank):
    """REQ-11 (regression R6 in v1.1)"""
    source = bank.new_account("Aisyah", balance="300.00")
    dest = bank.new_account("Aisyah", "savings")
    bank.transfer(source, dest, "120.00")
    history = bank.transactions(dest)
    assert len(history) == 1
    assert history[0]["type"] == "transfer_in"
    assert history[0]["amount"] == "120.00"


@pytest.mark.regression
def test_TC_TRF_10_money_is_conserved_between_own_accounts(bank):
    """REQ-06: no money is created or lost when moving it between your own accounts."""
    a = bank.new_account("Aisyah", balance="1000.00")
    b = bank.new_account("Aisyah", "savings", balance="250.00")
    total_before = Decimal(bank.balance(a)) + Decimal(bank.balance(b))   # Decimal, never float, for money
    bank.transfer(a, b, "333.33")
    bank.transfer(b, a, "100.01")
    total_after = Decimal(bank.balance(a)) + Decimal(bank.balance(b))
    assert total_after == total_before
