import copy
import re

def validate_title(title):
    if not isinstance(title, str):
        raise ValueError("Title must be text.")

    title = title.strip()

    if not title:
        raise ValueError("Title cannot be blank.")

    return title


def validate_category(category):
    allowed_categories = {
        "network": "Network",
        "hardware": "Hardware",
        "software": "Software",
        "other": "Other",
    }

    if not isinstance(category, str):
        raise ValueError("Category must be text.")

    category = category.strip().lower()

    if category not in allowed_categories:
        raise ValueError(
            "Invalid category. Choose Network, Hardware, Software, or Other."
        )

    return allowed_categories[category]


def validate_urgency(urgency):
    allowed_urgencies = {
        "low": "low",
        "medium": "medium",
        "high": "high",
    }

    if not isinstance(urgency, str):
        raise ValueError("Urgency must be text.")

    urgency = urgency.strip().lower()

    if urgency not in allowed_urgencies:
        raise ValueError(
            "Invalid urgency. Choose low, medium, or high."
        )

    return allowed_urgencies[urgency]


def validate_affected_users(affected_users):
    if (
        isinstance(affected_users, bool)
        or not isinstance(affected_users, int)
    ):
        raise ValueError("Affected users must be a positive integer.")

    if affected_users <= 0:
        raise ValueError("Affected users must be a positive integer.")

    return affected_users

VALID_STATUSES = ("open", "in_progress", "resolved")
VALID_PRIORITIES = ("critical", "high", "medium", "low")


def validate_ticket_id(ticket_id):
    if not isinstance(ticket_id, str):
        raise ValueError("Ticket ID must be text.")

    ticket_id = ticket_id.strip().upper()
    digits = ticket_id[1:]

    # isascii() guards against characters like "²", which pass isdigit()
    # but make int() raise.
    if not (ticket_id.startswith("T") and digits.isascii() and digits.isdigit()):
        raise ValueError(f"Invalid ticket ID: '{ticket_id}'.")

    return ticket_id


def validate_staff_name(name):
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Staff name must not be blank.")

    return name.strip()


MIN_NOTE_LENGTH = 5
MAX_NOTE_LENGTH = 300
REQUIRED_TICKET_KEYS = (
    "id", "title", "category", "urgency", "affected_users",
    "priority", "status", "assigned_to",
)
NOTE_KEYS = {"note_id", "author", "message"}


def calculate_priority(urgency, affected_users):
    if urgency == "high" and affected_users >= 10:
        return "critical"
    if urgency == "high" or affected_users >= 10:
        return "high"
    if urgency == "medium" or affected_users >= 3:
        return "medium"
    return "low"


def validate_note_id(note_id):
    # [0-9], not \d: \d also matches non-ASCII digits
    if not isinstance(note_id, str) or not re.fullmatch(r"N[0-9]{3,}", note_id):
        raise ValueError(f"Invalid note ID: {note_id!r}.")
    return note_id


def validate_note_author(author):
    if not isinstance(author, str) or not author.strip():
        raise ValueError("Note author must not be blank.")
    return author.strip()


def validate_note_message(message):
    if not isinstance(message, str):
        raise ValueError("Note message must be text.")
    message = message.strip()
    if not MIN_NOTE_LENGTH <= len(message) <= MAX_NOTE_LENGTH:
        raise ValueError(
            f"Note message must be {MIN_NOTE_LENGTH}-{MAX_NOTE_LENGTH} "
            "characters after trimming."
        )
    return message


def validate_note(note):
    if not isinstance(note, dict):
        raise ValueError("Each note must be an object.")
    if set(note) != NOTE_KEYS:
        raise ValueError("A note needs exactly note_id, author and message.")
    validate_note_id(note["note_id"])
    validate_note_author(note["author"])
    validate_note_message(note["message"])


def validate_ticket(ticket):
    """Return a validated deep copy of a stored ticket (v1 tickets get notes=[])."""
    if not isinstance(ticket, dict):
        raise ValueError("each ticket must be a JSON object.")

    missing = [k for k in REQUIRED_TICKET_KEYS if k not in ticket]
    if missing:
        raise ValueError(f"ticket is missing keys: {', '.join(missing)}.")

    ticket_id = ticket["id"]
    if validate_ticket_id(ticket_id) != ticket_id:
        raise ValueError(f"ticket ID '{ticket_id}' is not in canonical form.")

    validate_title(ticket["title"])

    for field, validator in (("category", validate_category),
                             ("urgency", validate_urgency)):
        if validator(ticket[field]) != ticket[field]:
            raise ValueError(f"{field} {ticket[field]!r} is not canonical.")

    users = validate_affected_users(ticket["affected_users"])
    if ticket["priority"] != calculate_priority(ticket["urgency"], users):
        raise ValueError("priority does not match urgency and affected_users.")

    status = ticket["status"]
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status {status!r}.")

    assigned = ticket["assigned_to"]
    if assigned is not None:
        validate_staff_name(assigned)
    if status in ("in_progress", "resolved") and assigned is None:
        raise ValueError(f"a {status} ticket must be assigned.")

    notes = ticket.get("notes", [])
    if not isinstance(notes, list):
        raise ValueError("notes must be a list.")
    seen = set()
    for note in notes:
        validate_note(note)
        if note["note_id"] in seen:
            raise ValueError(f"duplicate note ID {note['note_id']}.")
        seen.add(note["note_id"])

    clean = copy.deepcopy(ticket)
    clean["notes"] = copy.deepcopy(notes)
    return clean