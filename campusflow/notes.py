from campusflow.validation import (
    validate_ticket_id,
    validate_note_id,
    validate_note_author,
    validate_note_message,
)

NOTE_ELIGIBLE_STATUSES = ("open", "in_progress")


def _find_ticket(tickets, ticket_id):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket
    raise ValueError(f"Unknown ticket ID: '{ticket_id}'.")


def next_note_id(ticket):
    """Next per-ticket ID: highest existing N### plus one (never len + 1)."""
    highest = 0
    for note in ticket.get("notes", []):
        try:
            number = int(validate_note_id(note.get("note_id"))[1:])
        except ValueError:
            continue
        highest = max(highest, number)
    return f"N{highest + 1:03d}"


def add_note(tickets, ticket_id, author, message):
    """Append a note and return it.

    Before: tickets is a list of valid tickets.
    After success: exactly one note appended to one open/in_progress ticket.
    After failure: ValueError, nothing changed, no note ID consumed.
    """
    author = validate_note_author(author)
    message = validate_note_message(message)
    ticket_id = validate_ticket_id(ticket_id)
    ticket = _find_ticket(tickets, ticket_id)

    if ticket["status"] not in NOTE_ELIGIBLE_STATUSES:
        raise ValueError(
            "Notes can only be added to open or in_progress tickets. "
            "Reopen the ticket first."
        )

    note = {"note_id": next_note_id(ticket), "author": author, "message": message}
    ticket.setdefault("notes", []).append(note)   # the only mutation
    return note


def get_notes(tickets, ticket_id):
    """Read-only: copies of a ticket's notes in note-ID order."""
    ticket = _find_ticket(tickets, validate_ticket_id(ticket_id))
    notes = sorted(ticket.get("notes", []), key=lambda n: int(n["note_id"][1:]))
    return [dict(note) for note in notes]