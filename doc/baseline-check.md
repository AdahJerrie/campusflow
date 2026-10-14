## Engineer A baseline
**Audited commit:** <<FILL: SHA>>   **Python:** 3.12.3
**Run:** `python3 main.py`   **Tests:** `python3 -m unittest discover -s tests -v`

### Test results at the audited commit
Ran 40 tests: 36 passed, 4 ERROR (`test_load_rejects_*` in test_storage.py).
Cause: `FileNotFoundError: data/test_unittest_tickets.json`, because `data/`
did not exist in a clean checkout. ERROR, not FAIL: the tests never reached
their assertions, so they gave no evidence about the loader either way.
After `data/` existed: 40/40 passed.
<<FILL: result of the fresh-clone run, and whether `git ls-files data` was empty>>

### Probes (snapshot comparison with copy.deepcopy)
| # | Action | Expected | Actual | Data changed? | Status |
|---|--------|----------|--------|---------------|--------|
| 1 | CLI: category `network`, high, 5 users | Network, high | Created T001, priority high | n/a | confirmed OK |
| 2 | Ctrl-C at the menu | clean exit | raw KeyboardInterrupt traceback | n/a | confirmed (CLI issue, reported to B) |
| 3 | `update_ticket_status(..., ["in_progress"])` | ValueError | TypeError: unhashable type: 'list' (workflow.py line 45) | no | confirmed |
| 4 | same with `{"a": 1}` | ValueError | TypeError: unhashable type: 'dict' | no | confirmed |
| 5 | same with `None` and `5` | ValueError | ValueError (invalid transition) | no | confirmed OK |
| 6 | load a file with duplicate IDs | rejected | <<FILL>> | <<FILL>> | <<FILL>> |
| 7 | ticket without "id" key, then create | friendly error | <<FILL>> | <<FILL>> | <<FILL>> |

### Existing coverage in A's areas at baseline
Covered: unassigned to in_progress, resolved assignment, reopen path, max-based ticket ID.
Not covered: bool/float/string/negative `affected_users`, priority boundaries (9 vs 10, 2 vs 3),
duplicate IDs, "whole collection unchanged" assertions, non-string status.

### Peer-reported, not mine to confirm
`get_queue` keeps `in_progress` tickets (`status != "resolved"`); the brief says the original
queue is OPEN only. Not changed by A; raised with Engineer B and the mentor.