# CampusFlow Design Decisions

## 1. Modular structure

Ticket creation, workflow rules, queue handling, reporting, persistence,
and the command-line interface are separated into modules. This makes each
part easier to understand, test, and maintain.

## 2. Ticket validation

Ticket titles cannot be blank. Categories and urgency values must be
supported choices. The affected-user count must be a positive integer.
Validation prevents invalid ticket data from being created.

## 3. Priority calculation

Priority is calculated from urgency and the number of affected users.
High urgency affecting at least 10 users becomes critical. Other high
urgency tickets or tickets affecting at least 10 users become high.
Medium urgency or at least 3 affected users becomes medium. Remaining
tickets become low.

## 4. Workflow rules

Tickets follow the supported progression from open to in_progress to
resolved. An unassigned ticket cannot move to in_progress. A resolved
ticket must be reopened before further status changes.

## 5. Queue ordering

The original Open Work Queue shows OPEN tickets only. in_progress and
resolved tickets are excluded. Tickets are ordered by priority (critical,
high, medium, low), then by NUMERIC ticket ID, so T2 comes before T10.
"Unresolved" (open + in_progress) is a reporting measure, not the queue.
sort_by_priority is shared with the optional "sort search results" view.

## 6. JSON persistence

JSON provides a simple, human-readable format using Python's standard
library. The storage module checks the schema and ticket data when loading
saved files and reports invalid data instead of silently accepting it.

## 7. Testing

The unittest framework is used because it is included with Python.
Tests cover successful operations, validation failures, workflow rules,
persistence errors, queue ordering, and empty reports.


## 8. Error convention
Every business-layer function raises ValueError on rejection and mutates nothing on failure.
The CLI catches ValueError and OSError and prints a friendly message.

## 9. Validate before mutate
add_note validates author, message, ticket ID and ticket status, then computes the note ID,
then appends. The append is the only mutation, so a rejected note cannot consume an ID.

## 10. Note IDs
Per ticket, N001, N002...; the next ID is highest existing number + 1 (not len + 1),
so reloaded or gapped data never collides.

## 11. Leaf validation module
validation.py imports nothing from campusflow. storage.py needs the validators and
tickets.py imports storage, so a shared leaf module avoids a circular import.

## 12. Load and save safety
load_tickets validates the whole decoded collection into a new list (keys, canonical
category/urgency, priority consistency, statuses, assignment rule, note shapes, duplicate
ticket and note IDs) and returns it only if every record passes. reload_into replaces
memory only after that. save_tickets validates, writes a temp file in the same directory,
then os.replace, so a failed save leaves the old file intact.


## 13. Search
search_tickets is a pure function in search.py: it validates every filter first, then
returns deep copies of the tickets that match ALL supplied filters (AND). A blank filter
means "do not filter". Titles are compared with casefold(). Results come back in the
original ticket order; priority sorting is a separate, optional step.

## 14. Reports
Every ticket is counted once, by its current status, priority and category.
unresolved = open + in_progress. resolution_percent = resolved / total * 100, and an
empty collection returns 0.0 instead of dividing by zero.

## 15. Testable CLI
Prompt screens live in menus.py and take input_fn and output_fn, resolved when the screen
runs, so tests pass scripted answers (or patch builtins.input) instead of typing.
Questions live in question_bank.py; scoring lives in understanding_check.py.
