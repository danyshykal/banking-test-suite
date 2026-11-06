"""
Account status. Technique: state transition testing.

    active --freeze--> frozen --unfreeze--> active
    frozen --freeze--> (invalid, 409)      active --unfreeze--> (invalid, 409)
"""
import pytest

pytestmark = pytest.mark.regression


def test_TC_ST_01_freeze_then_unfreeze(bank):
    """REQ-09: valid transitions, and the account works again after unfreezing."""
    acc = bank.new_account(balance="100.00")
    assert bank.freeze(acc).json()["status"] == "frozen"
    assert bank.unfreeze(acc).json()["status"] == "active"
    assert bank.withdraw(acc, "10.00").status_code == 200


def test_TC_ST_02_freeze_an_already_frozen_account(bank):
    """REQ-09: invalid transition"""
    acc = bank.new_account()
    bank.freeze(acc)
    assert bank.freeze(acc).status_code == 409


def test_TC_ST_03_unfreeze_an_active_account(bank):
    """REQ-09: invalid transition"""
    acc = bank.new_account()
    assert bank.unfreeze(acc).status_code == 409


def test_TC_ST_04_frozen_account_can_still_be_viewed(bank):
    """REQ-08: frozen blocks money movement, not viewing."""
    acc = bank.new_account(balance="100.00")
    bank.freeze(acc)
    response = bank.get(acc)
    assert response.status_code == 200
    assert response.json()["balance"] == "100.00"
    assert len(bank.transactions(acc)) == 1
