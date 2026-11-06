# Requirements

The functional requirements the test suite verifies. Every test's docstring names the requirement(s) it covers.

| ID | Requirement | Since |
|---|---|---|
| REQ-01 | A customer can open a **checking** or **savings** account. It starts at 0.00, status *active*, with a unique 10-digit number. | 1.0 |
| REQ-02 | The owner is required, and the type must be exactly `checking` or `savings`. | 1.0 |
| REQ-03 | Asking for an account that doesn't exist returns 404. | 1.0 |
| REQ-04 | Deposits must be more than 0, have at most 2 decimal places, and be no more than RM 50,000.00 each. | 1.0 |
| REQ-05 | Withdrawals follow the same amount rules, with a limit of RM 5,000.00 each, and cannot exceed the balance. Withdrawing the exact balance is allowed. | 1.0 |
| REQ-06 | A transfer moves money between two different, existing accounts. The source must cover the amount plus any fee. No balance may ever go negative. Money is never created or lost. | 1.0 |
| REQ-07 | A transfer between **different customers** costs a RM 1.00 fee, recorded as its own `fee` transaction. Transfers between a customer's own accounts stay **free**. | 1.1 |
| REQ-08 | A frozen account cannot receive deposits, make withdrawals, or send or receive transfers (409). It can still be viewed. | 1.0 |
| REQ-09 | Accounts move active → frozen → active. Freezing a frozen account, or unfreezing an active one, returns 409. | 1.0 |
| REQ-10 | Savings accounts earn monthly interest of balance × 2.5% ÷ 12, rounded **half-up** to the nearest sen. Checking accounts earn none (400). | 1.0 |
| REQ-11 | Every successful operation appears in the history, newest first, with the balance after it. Incoming transfers appear on the receiving account. Failed operations are not recorded. | 1.0 |
| REQ-12 | All money arithmetic is exact (no floating-point errors). | 1.0 |
| REQ-13 | A health endpoint reports status and the running release. | 1.0 |

## Traceability matrix

Which tests cover each requirement. Every requirement has at least one test.

| Requirement | Tests |
|---|---|
| REQ-01 | TC_ACC_01, 02, 06 · TC_SMK_02 |
| REQ-02 | TC_ACC_03a-d, 04a-c |
| REQ-03 | TC_ACC_05 |
| REQ-04 | TC_DEP_01, 02a-b, 03a-d, 04, 05a-d · TC_SMK_02 |
| REQ-05 | TC_WD_01, 02, 03, 04a-b · TC_SMK_02 |
| REQ-06 | TC_TRF_01, 04, 05, 07, 08, 10 |
| REQ-07 | TC_TRF_01, 02, 03, 08 |
| REQ-08 | TC_DEP_07 · TC_WD_05 · TC_TRF_06a-b · TC_ST_04 |
| REQ-09 | TC_ST_01, 02, 03 |
| REQ-10 | TC_INT_01, 02, 03, 04 |
| REQ-11 | TC_DEP_01 · TC_TRF_03, 09 · TC_TXN_01, 02, 03 |
| REQ-12 | TC_DEP_06 · TC_TRF_10 · TC_TXN_02 |
| REQ-13 | TC_SMK_01 |
