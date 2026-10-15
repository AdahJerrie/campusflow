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
- Display the Open Work Queue: OPEN tickets only, ordered by priority
  (critical, high, medium, low) and then numeric ticket ID. `in_progress`
  and `resolved` tickets never appear in it.
- Search tickets by title text (case-insensitive substring) with optional
  category, status and priority filters. All supplied filters must match
  (AND); a blank filter means "do not filter on this". Search is read-only,
  and the results can optionally be sorted by priority then ticket ID.
- Add and view structured follow-up notes on tickets (open or in_progress only).
- Generate reports: total, counts by status, priority and category,
  unresolved (open + in_progress), resolved, and resolution percentage
  (0% when there are no tickets).
- Take the Engineering Understanding Check: six A/B/C/D questions about this
  application, scored 0-6, plus two written explanations saved to
  `understanding_notes.txt` for mentor discussion.
- Save and load ticket data using JSON persistence.
- Validate saved data and report malformed or unsupported files.

## Requirements

- Python 3.10 or later recommended.
- Python standard library only; no external packages required.

## Run the application

From the project root, run:

    python3 main.py

Follow the numbered menu to use the application (options 9-12 are follow-up
notes, viewing notes, search, and the Understanding Check). Ticket data is
stored in `data/tickets.json`. Understanding Check explanations are appended
to `understanding_notes.txt`.

## Run tests

Run the complete test suite with:

    python3 -m unittest discover -s tests -v

The tests cover ticket creation, validation, priority calculation, ticket
lookup, assignment, workflow rules, JSON persistence, queue ordering,
resolved-ticket exclusion, and reporting.

## Project structure

    main.py           Command-line menu and application entry point
    campusflow/
        tickets.py            Ticket creation, validation, and lookup
        validation.py         Shared validators and priority rule
        workflow.py           Assignment and status transitions
        notes.py              Structured follow-up notes
        queue.py              Open Work Queue and priority sorting
        search.py             Read-only title search with combined filters
        reports.py            Ticket summary reports
        storage.py            JSON persistence and ticket ID generation
        menus.py              Prompt screens for notes, search and the check
        question_bank.py      Understanding Check questions (data only)
        understanding_check.py  Quiz flow and scoring
    tests/
        test_tickets.py
        test_validation.py
        test_workflow.py
        test_notes.py
        test_storage.py
        test_queue_reports.py
        test_search.py
        test_reports.py
        test_understanding.py
        test_cli.py
        test_ticket_id_consistency.py
    doc/
        baseline-check.md
        ai-learning-log.md
        design-decisions.md

## Data and validation

The application validates ticket information before creating a ticket.
Ticket data is stored locally in JSON. The `data/` directory is excluded
from Git so local runtime data is not accidentally committed.
