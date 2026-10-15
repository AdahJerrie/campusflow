# CampusFlow

CampusFlow is a Python command-line helpdesk application for managing support tickets. It supports ticket creation, priority calculation, assignment, status changes, an open-work queue, reporting, JSON storage, and automated tests.

## Features

- Create and manage support tickets.
- Calculate ticket priority from urgency and the number of affected users.
- Assign tickets to staff members.
- Manage ticket status transitions and reopen resolved tickets.
- Add notes to open and in-progress tickets.
- Generate an open-work queue and ticket reports.
- Save tickets to JSON and load them when the application starts.
- Validate ticket data and reject invalid operations safely.
- Run automated tests using Python's standard library.

## Ticket Validation and Workflow Safety

CampusFlow validates ticket data before accepting changes.

- Ticket titles must not be blank.
- Categories must be `Network`, `Hardware`, `Software`, or `Other`.
- Urgency must be `low`, `medium`, or `high`.
- The number of affected users must be a positive integer.
- Ticket IDs must be valid and unique.
- Assigned staff names must not be blank.
- An unassigned ticket cannot move to `in_progress`.
- Tickets follow the permitted status transitions: `open` → `in_progress` → `resolved`.
- A resolved ticket must be explicitly reopened before it can be reassigned or receive new notes.

Rejected operations should leave the affected ticket data unchanged.

## Ticket Notes

Each note contains:

- `note_id`: a sequential ID such as `N001`.
- `author`: the staff member who added the note.
- `message`: the note content.

Note IDs are unique within each ticket. Authors must not be blank, and messages must contain between 5 and 300 characters after trimming surrounding whitespace.

Notes can be added only to open or in-progress tickets. Existing notes are preserved when a ticket is resolved and later reopened.

## JSON Storage

Tickets are stored in JSON using a versioned structure:

```json
{
    "schema_version": 1,
    "tickets": []
}
```

The `tickets` list contains the saved ticket records.

Storage validation checks required ticket fields, unique ticket IDs, valid categories and urgency values, legal statuses, priority consistency, assignment values, and note structure.

- A missing storage file returns an empty ticket list.
- Malformed JSON produces a clear error.
- Invalid ticket data is rejected instead of being silently accepted.
- Ticket data is validated before it is saved.
- Ticket IDs are generated using the highest existing numeric ID to avoid collisions after reloading saved tickets.

## Running the Tests

Run the following command from the project root:

```bash
python3 -m unittest discover -s tests -v
```

The tests cover JSON storage, ticket ID generation, invalid data, assignments, status transitions, reopening, and note validation.

## Requirements

- Python 3.12 or a compatible Python 3 version.
- Python standard library; no external packages are required for the current storage and test functionality.

## Team Development

CampusFlow is developed collaboratively. Changes are made on feature branches, tested before submission, and submitted through pull requests for review before merging into the main branch.