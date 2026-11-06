"""
A thin client for the bank API, so tests read like business steps:
    bank.deposit(acc, "100.00")   instead of   requests.post(f"{url}/accounts/{n}/deposit", json=...)
Same idea as the Page Object Model in project 1, applied to an API.
"""
import requests


class BankClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def _post(self, path, json=None):
        return requests.post(f"{self.base_url}{path}", json=json, timeout=10)

    def _get(self, path):
        return requests.get(f"{self.base_url}{path}", timeout=10)

    # --- raw calls: return the Response, so negative tests can check status codes ---

    def open_account(self, owner, account_type="checking"):
        return self._post("/accounts", {"owner": owner, "type": account_type})

    def get(self, number):
        return self._get(f"/accounts/{number}")

    def deposit(self, number, amount):
        return self._post(f"/accounts/{number}/deposit", {"amount": amount})

    def withdraw(self, number, amount):
        return self._post(f"/accounts/{number}/withdraw", {"amount": amount})

    def transfer(self, source, dest, amount):
        return self._post("/transfers", {"from": source, "to": dest, "amount": amount})

    def apply_interest(self, number):
        return self._post(f"/accounts/{number}/apply-interest")

    def freeze(self, number):
        return self._post(f"/accounts/{number}/freeze")

    def unfreeze(self, number):
        return self._post(f"/accounts/{number}/unfreeze")

    def transactions(self, number):
        return self._get(f"/accounts/{number}/transactions").json()["transactions"]

    # --- shortcuts for test setup (Arrange step) ---

    def balance(self, number) -> str:
        return self.get(number).json()["balance"]

    def new_account(self, owner="Aisyah", account_type="checking", balance=None) -> str:
        """Open an account, optionally fund it, and return its number."""
        response = self.open_account(owner, account_type)
        assert response.status_code == 201, f"Setup failed: {response.text}"
        number = response.json()["number"]
        if balance is not None:
            funded = self.deposit(number, balance)
            assert funded.status_code == 200, f"Setup deposit failed: {funded.text}"
        return number
