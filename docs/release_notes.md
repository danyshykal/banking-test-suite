# Release notes and test results

## v1.0: stable release
Accounts, deposits, withdrawals, transfers, interest, freeze/unfreeze, history.

**Test result:** 52 passed, 3 skipped (the fee tests: that feature doesn't exist yet). ✅ Released.

## v1.1: release candidate
**New:** RM 1.00 fee on transfers between different customers (REQ-07).

During development, changes to the transfer, deposit and interest code accidentally broke existing behaviour.

**Test result:** 48 passed, **7 failed**. ❌ **Release blocked.**

| Regression | What broke | Caught by |
|---|---|---|
| R1 | The fee is also charged on transfers between a customer's own accounts | TC_TRF_01, TC_TRF_10 |
| R2 | The funds check ignores the fee, so a balance can go to -1.00 | TC_TRF_08 |
| R3 | Interest uses banker's rounding (half-even) instead of half-up | TC_INT_02 |
| R4 | Withdrawing the exact balance is refused (`>=` instead of `>`) | TC_WD_02 |
| R5 | Deposits into frozen accounts are accepted again | TC_DEP_07 |
| R6 | Incoming transfers no longer appear in the receiver's history | TC_TRF_09 |

Note: 2 of the 3 new-feature tests **passed** on v1.1. The new fee looked fine in isolation, and it was the existing regression tests that showed what the change broke elsewhere.

## v1.2: fix release (latest)
Fee feature kept, all six regressions fixed.

**Test result:** 55 passed. ✅ Released.
