# CampusFlow AI Learning Log

This log records AI-assisted learning during development. Keep the entries
accurate to the interactions you actually had, and add your own examples
if your assignment requires a minimum number of interactions per fellow.

## Interaction 1: Understanding ticket creation

- **Goal:** Organize ticket creation and validation.
- **AI assistance:** Helped break the feature into validation, priority
  calculation, ticket creation, and lookup responsibilities.
- **What I learned:** Separating responsibilities makes the code easier
  to test and explain.
- **My verification:** Ran the ticket unit tests and checked validation
  and priority cases.

## Interaction 2: Implementing the unresolved queue

- **Goal:** Display unresolved tickets in priority order.
- **AI assistance:** Helped design a queue that sorts by priority and then
  numeric ticket ID, while excluding resolved tickets.
- **What I learned:** A sort key can express more than one ordering rule.
- **My verification:** Added tests for ordering, resolved-ticket
  exclusion, and an empty queue.

## Interaction 3: Reports and persistence

- **Goal:** Summarize tickets and retain data between application runs.
- **AI assistance:** Helped structure status and priority counts and
  connect the command-line interface to JSON storage.
- **What I learned:** Persistence and reporting are easier to maintain
  when implemented in separate modules.
- **My verification:** Ran the unit tests, including empty-report and
  save/load cases.

## Reflection

AI assistance helped me break the assignment into smaller tasks and
identify useful tests. I ran the test suite to check the implementation
rather than treating generated code as automatically correct. I should
be able to explain each module, validation rule, workflow transition,
and test in my own words.

## Engineer A: Cycle 1, unhashable status

- **Concept gap:** I assumed `x not in some_set` is a safe check for any value.
- **Question asked:** "Review update_ticket_status and name inputs that could raise a
  non-ValueError exception. Don't rewrite it."
- **AI guidance (summary):** `in` on a set hashes the value, so a list or dict raises
  TypeError; None and 5 are hashable and would fall through to ValueError.
- **Tiny experiment:** `python3 -c 'print([] in {"a"})'` raised TypeError: unhashable type.
- **Independent verification:** wrote `test_non_string_status_rejected_with_value_error`
  BEFORE the fix. Red: 2 subtest errors (list, dict), 2 passes (None, 5), exactly as
  predicted. Output saved in <<FILL: path>>.
- **Decision:** added `isinstance(new_status, str)` as the first line of
  `update_ticket_status`. Green: 17 workflow tests, then 45 total.
- **Guard test:** the test above. **Defence prompt 2:** this is the test that failed first.

## Engineer A: Cycle 2, schema_version and booleans
<<ONLY WRITE THIS AFTER YOU RUN THE EXPERIMENT YOURSELF>>
- **Concept gap:** `json.load` succeeding does not mean the data is safe.
- **Question asked:** "Why might json.load succeed but return unsafe or inconsistent data?"
- **AI guidance:** JSON `true` becomes Python `True`, and `True == 1`, so `version != 1` accepts it.
- **Tiny experiment:** `python3 -c 'print(True == 1, type(True) is int)'` printed <<FILL>>.
- **Verification:** `test_boolean_schema_version_rejected` plus the strict `type(version) is not int` check.
  <<FILL: did this test fail first? If you wrote it with the fix, say so.>>
- **Decision:** loader requires `type(version) is int and version == 1`.

## Team requirement: AI suggestion that was wrong
- **Suggestion:** replace the import block at the top of `tests/test_storage.py` with a
  shorter one.
- **Evidence:** the run showed 23 errors, all `NameError: name 'json'/'copy' is not defined`.
  The new tests used both modules and the replacement block had dropped them. No
  production code was at fault.
- **Decision:** imports restored, and `"notes": []` added to the old fixture. Committed as
  `test: add missing json/copy imports ...`. I also committed `storage.py` while the suite
  was red (9f9be05); I left that commit in history rather than rewriting it.

## Reflection (Engineer A)
Before: I thought a passing test suite meant the business rules were safe. AI explained
that tests only cover what they assert. I tested that claim by checking which of my
areas had no test (only `affected_users == 0`) and by comparing a snapshot of the whole
collection before and after each rejected call. The change I made was a `deepcopy` snapshot
assertion in every rejection test. I can explain this choice without AI in the room: <<WRITE ONE SENTENCE>>.