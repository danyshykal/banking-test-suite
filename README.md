# Banking Application Test Suite

A **functional and regression** test suite for a banking API, written in **Python + pytest + requests**.

The bank app in `app/` has three releases, so the suite can show a full regression cycle:

| Release | What changed | Result |
|---|---|---|
| **v1.0** | Stable release | ✅ 52 passed, 3 skipped (fee feature not yet built) |
| **v1.1** | Adds a RM 1.00 transfer fee, but accidentally breaks 6 existing behaviours | ❌ **7 failed: release blocked** |
| **v1.2** | Fee kept, all 6 regressions fixed | ✅ 55 passed |

Details: [`docs/release_notes.md`](docs/release_notes.md)

## What's covered
| Area | Tests | Test design technique |
|---|---|---|
| Accounts | 11 | Equivalence partitioning |
| Deposits | 14 | Boundary value analysis, equivalence partitioning |
| Withdrawals | 6 | Boundary value analysis |
| Transfers | 11 | Decision table |
| Interest | 4 | Boundary value analysis (rounding) |
| Account state | 4 | State transition |
| Transaction history | 3 | - |
| Smoke | 2 | - |

Every test maps to a requirement: see the traceability matrix in [`docs/requirements.md`](docs/requirements.md).
Manual test cases: [`docs/test_cases.csv`](docs/test_cases.csv)

## Regressions caught in v1.1
| ID | What broke | Caught by |
|---|---|---|
| R1 | Fee charged on transfers between a customer's own accounts | TC_TRF_01, TC_TRF_10 |
| R2 | Funds check ignores the fee, so a balance can go negative | TC_TRF_08 |
| R3 | Interest rounds half-even instead of half-up | TC_INT_02 |
| R4 | Withdrawing the exact balance is refused | TC_WD_02 |
| R5 | Frozen accounts accept deposits | TC_DEP_07 |
| R6 | Incoming transfers missing from the receiver's history | TC_TRF_09 |

## Run it
```bash
python -m venv venv
venv\Scripts\activate          # Windows  (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt

pytest                          # latest release (1.2): all pass
pytest --release 1.1            # the release with regressions
pytest --release 1.0            # previous stable release
pytest -m smoke                 # smoke tests only
pytest -m regression            # regression suite only
pytest -m new_feature           # tests for the v1.1 fee feature
```
Report: `reports/report.html`. The tests start the API themselves.

To explore the API by hand (e.g. in Postman), run `python run_server.py` (or `python run_server.py 1.1`) and use `http://127.0.0.1:5001`.

## CI
GitHub Actions runs smoke tests first, then the full suite on v1.2 and v1.0 (must pass), then v1.1 as a
**regression gate demo** (must fail). A failing regression suite is what should stop a real release.
