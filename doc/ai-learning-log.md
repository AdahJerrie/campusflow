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
