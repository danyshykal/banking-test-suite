"""
A small banking API used as the system under test.

    create_app(release="1.0")  stable release
    create_app(release="1.1")  adds the transfer fee, but accidentally introduces regressions [R1]..[R6]
    create_app(release="1.2")  fee kept, regressions fixed (latest)

Money is stored as whole cents (int) and parsed with Decimal, never float,
so 0.10 + 0.20 is exactly 0.30.
"""
import itertools
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal, InvalidOperation

from flask import Flask, jsonify, request

RELEASES = {
    "1.0": {"transfer_fee": False, "regressions": False},
    "1.1": {"transfer_fee": True, "regressions": True},
    "1.2": {"transfer_fee": True, "regressions": False},
}

ACCOUNT_TYPES = ("checking", "savings")
MAX_DEPOSIT = 5_000_000          # RM 50,000.00 per deposit
MAX_WITHDRAWAL = 500_000         # RM 5,000.00 per withdrawal
TRANSFER_FEE = 100               # RM 1.00, only between different customers (from v1.1)
SAVINGS_ANNUAL_RATE = Decimal("0.025")   # 2.5% a year, applied monthly


class BankError(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message


def parse_amount(value, maximum=None):
    """Turn user input into cents. Rejects zero, negatives, >2 decimals, text, booleans."""
    if value is None or isinstance(value, bool):
        raise BankError(400, "amount is required and must be a number")
    try:
        amount = Decimal(str(value))
    except InvalidOperation:
        raise BankError(400, "amount must be a number")
    if not amount.is_finite():
        raise BankError(400, "amount must be a number")
    if amount <= 0:
        raise BankError(400, "amount must be greater than 0")
    if amount.as_tuple().exponent < -2:
        raise BankError(400, "amount can have at most 2 decimal places")
    cents = int(amount * 100)
    if maximum is not None and cents > maximum:
        raise BankError(400, f"amount exceeds the limit of {money(maximum)}")
    return cents


def money(cents):
    return f"{Decimal(cents) / 100:.2f}"


def create_app(release: str = "1.2") -> Flask:
    if release not in RELEASES:
        raise ValueError(f"Unknown release {release}")
    fee_enabled = RELEASES[release]["transfer_fee"]
    buggy = RELEASES[release]["regressions"]

    app = Flask(__name__)
    accounts = {}                       # number -> account dict
    history = {}                        # number -> list of transactions
    next_number = itertools.count(1000000001)
    next_txn = itertools.count(1)

    # ---------- helpers ----------

    def body():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            raise BankError(400, "Request body must be a JSON object")
        return data

    def get_account(number):
        account = accounts.get(str(number))
        if account is None:
            raise BankError(404, f"Account {number} not found")
        return account

    def require_active(account):
        if account["status"] == "frozen":
            raise BankError(409, f"Account {account['number']} is frozen")

    def record(account, txn_type, signed_cents, description):
        history[account["number"]].append({
            "id": next(next_txn),
            "type": txn_type,
            "amount": money(signed_cents),
            "balance_after": money(account["balance"]),
            "description": description,
        })

    def view(account):
        return {
            "number": account["number"],
            "owner": account["owner"],
            "type": account["type"],
            "balance": money(account["balance"]),
            "status": account["status"],
        }

    @app.errorhandler(BankError)
    def bank_error(err):
        return jsonify(error=err.message), err.status

    @app.errorhandler(404)
    def not_found(_):
        return jsonify(error="Not found"), 404

    @app.errorhandler(405)
    def method_not_allowed(_):
        return jsonify(error="Method not allowed"), 405

    # ---------- routes ----------

    @app.get("/health")
    def health():
        return jsonify(status="ok", release=release)

    @app.post("/accounts")
    def open_account():
        data = body()
        owner, account_type = data.get("owner"), data.get("type")
        if not isinstance(owner, str) or not owner.strip():
            raise BankError(400, "owner is required")
        if account_type not in ACCOUNT_TYPES:
            raise BankError(400, "type must be 'checking' or 'savings'")
        number = str(next(next_number))
        accounts[number] = {"number": number, "owner": owner.strip(), "type": account_type,
                            "balance": 0, "status": "active"}
        history[number] = []
        return jsonify(view(accounts[number])), 201

    @app.get("/accounts/<number>")
    def account_details(number):
        return jsonify(view(get_account(number)))

    @app.get("/accounts/<number>/transactions")
    def transactions(number):
        get_account(number)
        return jsonify(transactions=list(reversed(history[number])))   # newest first

    @app.post("/accounts/<number>/deposit")
    def deposit(number):
        account = get_account(number)
        cents = parse_amount(body().get("amount"), MAX_DEPOSIT)
        if not buggy:                      # [R5] v1.1 refactor dropped the frozen check on deposits
            require_active(account)
        account["balance"] += cents
        record(account, "deposit", cents, "Deposit")
        return jsonify(view(account))

    @app.post("/accounts/<number>/withdraw")
    def withdraw(number):
        account = get_account(number)
        require_active(account)
        cents = parse_amount(body().get("amount"), MAX_WITHDRAWAL)
        insufficient = cents >= account["balance"] if buggy else cents > account["balance"]   # [R4] boundary
        if insufficient:
            raise BankError(400, "Insufficient funds")
        account["balance"] -= cents
        record(account, "withdrawal", -cents, "Withdrawal")
        return jsonify(view(account))

    @app.post("/transfers")
    def transfer():
        data = body()
        source_no, dest_no = str(data.get("from") or ""), str(data.get("to") or "")
        if not source_no or not dest_no:
            raise BankError(400, "from and to are required")
        if source_no == dest_no:
            raise BankError(400, "Cannot transfer to the same account")
        cents = parse_amount(data.get("amount"))
        source, dest = get_account(source_no), get_account(dest_no)
        require_active(source)
        require_active(dest)

        fee = 0
        if fee_enabled and (buggy or source["owner"] != dest["owner"]):   # [R1] fee on own-account transfers
            fee = TRANSFER_FEE
        needed = cents if buggy else cents + fee                            # [R2] fee ignored in funds check
        if needed > source["balance"]:
            raise BankError(400, "Insufficient funds")

        source["balance"] -= cents
        record(source, "transfer_out", -cents, f"Transfer to {dest_no}")
        dest["balance"] += cents
        if not buggy:                                                       # [R6] incoming entry not recorded
            record(dest, "transfer_in", cents, f"Transfer from {source_no}")
        if fee:
            source["balance"] -= fee
            record(source, "fee", -fee, "Transfer fee")
        return jsonify(source=view(source), destination=view(dest), fee=money(fee)), 201

    @app.post("/accounts/<number>/apply-interest")
    def apply_interest(number):
        account = get_account(number)
        if account["type"] != "savings":
            raise BankError(400, "Interest only applies to savings accounts")
        rounding = ROUND_HALF_EVEN if buggy else ROUND_HALF_UP                # [R3] wrong rounding mode
        interest = int((Decimal(account["balance"]) * SAVINGS_ANNUAL_RATE / 12)
                       .quantize(Decimal("1"), rounding=rounding))
        if interest > 0:
            account["balance"] += interest
            record(account, "interest", interest, "Monthly interest")
        return jsonify(interest=money(interest), balance=money(account["balance"]))

    @app.post("/accounts/<number>/freeze")
    def freeze(number):
        account = get_account(number)
        if account["status"] == "frozen":
            raise BankError(409, "Account is already frozen")
        account["status"] = "frozen"
        return jsonify(view(account))

    @app.post("/accounts/<number>/unfreeze")
    def unfreeze(number):
        account = get_account(number)
        if account["status"] == "active":
            raise BankError(409, "Account is not frozen")
        account["status"] = "active"
        return jsonify(view(account))

    return app
