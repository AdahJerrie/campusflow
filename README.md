# CampusFlow Helpdesk

CampusFlow is a Python command-line helpdesk application for creating,
tracking, assigning, and resolving IT support tickets.

## Features

- Create tickets with validated titles, categories, urgency, and affected users.
- Automatically calculate ticket priority.
- List tickets and view ticket details.
- Assign tickets to staff members.
- Manage ticket status through the supported workflow.
- Reopen resolved tickets.
- Display an unresolved queue ordered by priority and ticket ID.
- Generate reports grouped by status and priority.
- Save and load ticket data using JSON persistence.
- Validate saved data and report malformed or unsupported files.

## Requirements

- Python 3.10 or later recommended.
- Python standard library only; no external packages required.

## Run the application

From the project root, run:

    python3 -m campusflow.main

Follow the numbered menu to use the application. Ticket data is stored in
`data/tickets.json`.

## Run tests

Run the complete test suite with:

    python3 -m unittest discover -s tests -v

The tests cover ticket creation, validation, priority calculation, ticket
lookup, assignment, workflow rules, JSON persistence, queue ordering,
resolved-ticket exclusion, and reporting.

## Project structure

    campusflow/
        main.py       Command-line menu and application entry point
        tickets.py    Ticket creation, validation, and lookup
        workflow.py   Assignment and status transitions
        queue.py      Unresolved ticket queue
        reports.py    Ticket summary reports
        storage.py    JSON persistence and ticket ID generation
    tests/
        test_tickets.py
        test_workflow.py
        test_storage.py
        test_queue_reports.py
    ai-learning-log.md
    design-decisions.md

## Data and validation

The application validates ticket information before creating a ticket.
Ticket data is stored locally in JSON. The `data/` directory is excluded
from Git so local runtime data is not accidentally committed.
