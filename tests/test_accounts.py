"""Account management. Technique: equivalence partitioning on account type."""
import pytest

pytestmark = pytest.mark.regression


@pytest.mark.parametrize("account_type", ["checking", "savings"],
                         ids=["TC_ACC_01_open_checking", "TC_ACC_02_open_savings"])
def test_open_account(bank, account_type):
    """REQ-01: valid partition. A new account starts empty and active."""
    response = bank.open_account("Aisyah", account_type)
    assert response.status_code == 201
    account = response.json()
    assert account["type"] == account_type
    assert account["balance"] == "0.00"
    assert account["status"] == "active"
    assert account["number"].isdigit() and len(account["number"]) == 10


@pytest.mark.parametrize("account_type", ["current", "", None, "SAVINGS"],
                         ids=["TC_ACC_03a_unknown_type", "TC_ACC_03b_empty_type",
                              "TC_ACC_03c_missing_type", "TC_ACC_03d_wrong_case"])
def test_invalid_account_type(bank, account_type):
    """REQ-02: invalid partition. Anything other than the two exact types is rejected."""
    response = bank.open_account("Aisyah", account_type)
    assert response.status_code == 400


@pytest.mark.parametrize("owner", ["", "   ", None], ids=["TC_ACC_04a_empty_owner",
                                                        "TC_ACC_04b_blank_owner", "TC_ACC_04c_missing_owner"])
def test_owner_required(bank, owner):
    """REQ-02"""
    assert bank.open_account(owner, "checking").status_code == 400


def test_TC_ACC_05_unknown_account_returns_404(bank):
    """REQ-03"""
    assert bank.get("9999999999").status_code == 404


def test_TC_ACC_06_account_numbers_are_unique(bank):
    """REQ-01"""
    numbers = {bank.new_account("Aisyah") for _ in range(5)}
    assert len(numbers) == 5
