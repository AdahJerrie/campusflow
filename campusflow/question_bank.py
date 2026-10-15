"""Question bank for the Engineering Understanding Check.

Data only: no input(), no print(), no scoring. Scoring lives in
understanding_check.py, so questions can change without touching the logic.

Each question has:
    id       short label
    prompt   the scenario text
    options  dict with the letters A, B, C and D
    answer   the correct letter
    why      one-line reason shown AFTER the learner has answered
"""

QUESTIONS = [
    {
        "id": "Q1",
        "prompt": (
            "Ticket T001 is open and unassigned. A user tries to move it to "
            "in_progress. What should happen?"
        ),
        "options": {
            "A": "Accept",
            "B": "Reject and preserve all data",
            "C": "Resolve it automatically",
            "D": "Remove ticket",
        },
        "answer": "B",
        "why": (
            "Work cannot start without an owner, so the change is rejected and "
            "the ticket stays exactly as it was."
        ),
    },
    {
        "id": "Q2",
        "prompt": "The app has zero tickets. What should resolution percentage display?",
        "options": {
            "A": "Crash",
            "B": "100%",
            "C": "0%",
            "D": "Divide by one without explanation",
        },
        "answer": "C",
        "why": (
            "resolved / total would divide by zero, so an empty report is "
            "handled explicitly and shows 0%."
        ),
    },
    {
        "id": "Q3",
        "prompt": (
            "Filter title='wifi', category='Network', status='open'. "
            "Which records should match?"
        ),
        "options": {
            "A": "Any record matching one filter",
            "B": "Only records matching all supplied filters",
            "C": "All network records",
            "D": "All open records",
        },
        "answer": "B",
        "why": (
            "Filters are combined with AND: a ticket must satisfy every filter "
            "that was supplied."
        ),
    },
    {
        "id": "Q4",
        "prompt": "A resolved ticket receives 'Add note'. What should happen?",
        "options": {
            "A": "Append anyway",
            "B": "Delete old notes",
            "C": "Reject until reopened",
            "D": "Change status silently",
        },
        "answer": "C",
        "why": (
            "Only open or in_progress tickets accept notes; a resolved ticket "
            "must be reopened first, and its earlier notes are kept."
        ),
    },
    {
        "id": "Q5",
        "prompt": "The JSON file includes two tickets with the same ID. What should load do?",
        "options": {
            "A": "Keep both",
            "B": "Replace memory with duplicates",
            "C": "Reject the load without changing current memory",
            "D": "Rename IDs silently",
        },
        "answer": "C",
        "why": (
            "The whole file is validated first; if anything is invalid the load "
            "is rejected and the data already in memory is untouched."
        ),
    },
    {
        "id": "Q6",
        "prompt": "A PR changes validation but has no negative-case tests. Best review action?",
        "options": {
            "A": "Approve because it runs",
            "B": "Request focused tests and reasoning",
            "C": "Merge immediately",
            "D": "Ask AI to approve it",
        },
        "answer": "B",
        "why": (
            "Code that runs can still accept bad input; a reviewer asks for "
            "tests that prove invalid input is rejected."
        ),
    },
]
