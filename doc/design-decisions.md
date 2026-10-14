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

Resolved tickets are excluded from the active queue. Remaining tickets
are ordered by priority (critical, high, medium, low), then by numeric
ticket ID for predictable ordering when priorities match.

## 6. JSON persistence

JSON provides a simple, human-readable format using Python's standard
library. The storage module checks the schema and ticket data when loading
saved files and reports invalid data instead of silently accepting it.

## 7. Testing

The unittest framework is used because it is included with Python.
Tests cover successful operations, validation failures, workflow rules,
persistence errors, queue ordering, and empty reports.
