
import json


ALLOWED_CATEGORIES = {"Network", "Hardware", "Software", "Other"}
ALLOWED_URGENCIES = {"low", "medium", "high"}
ALLOWED_STATUSES = {"open", "in_progress", "resolved"}
ALLOWED_PRIORITIES = {"critical", "high", "medium", "low"}

REQUIRED_TICKET_FIELDS = {
    "id",
    "title",
    "category",
    "urgency",
    "affected_users",
    "priority",
    "status",
    "assigned_to",
    "notes",
}

REQUIRED_NOTE_FIELDS = {"note_id", "author", "message"}


def calculate_priority(urgency, affected_users):
    if urgency == "high" and affected_users >= 10:
        return "critical"

    if urgency == "high" or affected_users >= 10:
        return "high"

    if urgency == "medium" or affected_users >= 3:
        return "medium"

    return "low"


def validate_tickets(tickets):
    """Validate a complete ticket collection without modifying it."""
    if not isinstance(tickets, list):
        raise ValueError("Tickets must be provided as a list.")

    seen_ids = set()

    for ticket in tickets:
        if not isinstance(ticket, dict):
            raise ValueError("Each ticket must be a dictionary.")

        missing = REQUIRED_TICKET_FIELDS - ticket.keys()
        if missing:
            raise ValueError(
                f"Ticket is missing required fields: {', '.join(sorted(missing))}."
            )

        ticket_id = ticket["id"]
        if (
            not isinstance(ticket_id, str)
            or not ticket_id.startswith("T")
            or not ticket_id[1:].isdigit()
        ):
            raise ValueError("Each ticket must have a valid ticket ID.")

        if ticket_id in seen_ids:
            raise ValueError(f"Duplicate ticket ID '{ticket_id}'.")

        seen_ids.add(ticket_id)

        title = ticket["title"]
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Ticket title must not be blank.")

        category = ticket["category"]
        if (
            not isinstance(category, str)
            or category not in ALLOWED_CATEGORIES
        ):
            raise ValueError(f"Invalid category '{category}'.")

        urgency = ticket["urgency"]
        if (
            not isinstance(urgency, str)
            or urgency not in ALLOWED_URGENCIES
        ):
            raise ValueError(f"Invalid urgency '{urgency}'.")

        status = ticket["status"]
        if (
            not isinstance(status, str)
            or status not in ALLOWED_STATUSES
        ):
            raise ValueError(f"Invalid status '{status}'.")

        affected_users = ticket["affected_users"]
        if (
            isinstance(affected_users, bool)
            or not isinstance(affected_users, int)
            or affected_users <= 0
        ):
            raise ValueError("affected_users must be a positive integer.")

        expected_priority = calculate_priority(urgency, affected_users)
        priority = ticket["priority"]

        if (
            not isinstance(priority, str)
            or priority not in ALLOWED_PRIORITIES
            or priority != expected_priority
        ):
            raise ValueError(
                f"Priority for ticket '{ticket_id}' must be "
                f"'{expected_priority}'."
            )

        assigned_to = ticket["assigned_to"]
        if assigned_to is not None and (
            not isinstance(assigned_to, str) or not assigned_to.strip()
        ):
            raise ValueError(
                "assigned_to must be None or a nonblank staff name."
            )

        notes = ticket["notes"]
        if not isinstance(notes, list):
            raise ValueError("Ticket notes must be a list.")

        seen_note_ids = set()
        seen_note_numbers = set()

        for note in notes:
            if not isinstance(note, dict):
                raise ValueError("Each note must be a dictionary.")

            if not REQUIRED_NOTE_FIELDS.issubset(note):
                raise ValueError(
                    "Each note needs note_id, author, and message."
                )

            note_id = note["note_id"]
            if (
                not isinstance(note_id, str)
                or not note_id.startswith("N")
                or not note_id[1:].isdigit()
            ):
                raise ValueError("Each note must have a valid note ID.")

            note_number = int(note_id[1:])
            if note_number < 1 or note_id in seen_note_ids:
                raise ValueError(
                    "Note IDs must be positive and unique within each ticket."
                )

            # Prevent equivalent numeric IDs such as N001 and N1.
            if note_number in seen_note_numbers:
                raise ValueError(
                    "Note IDs must be numerically unique within each ticket."
                )

            seen_note_ids.add(note_id)
            seen_note_numbers.add(note_number)

            author = note["author"]
            if not isinstance(author, str) or not author.strip():
                raise ValueError("Note author must not be blank.")

            message = note["message"]
            if (
                not isinstance(message, str)
                or not 5 <= len(message.strip()) <= 300
            ):
                raise ValueError(
                    "Note message must be between 5 and 300 characters."
                )


def save_tickets(tickets, path):
    """Validate tickets before saving them to JSON."""
    # Validate before opening the file, so invalid data won't truncate it.
    validate_tickets(tickets)

    data = {
        "schema_version": 1,
        "tickets": tickets,
    }

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_tickets(path):
    """Load and validate tickets from JSON."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(
                f"Cannot load tickets from '{path}': expected a JSON object."
            )

        schema_version = data.get("schema_version")
        if (
            isinstance(schema_version, bool)
            or not isinstance(schema_version, int)
            or schema_version != 1
        ):
            raise ValueError(
                f"Cannot load tickets from '{path}': "
                "unsupported or missing schema version."
            )

        tickets = data.get("tickets")

        try:
            validate_tickets(tickets)
        except ValueError as error:
            raise ValueError(
                f"Cannot load tickets from '{path}': {error}"
            ) from error

        return tickets

    except FileNotFoundError:
        # A missing file means a fresh start.
        return []

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Cannot load tickets from '{path}': "
            f"invalid JSON at line {error.lineno}, column {error.colno}."
        ) from error


def generate_ticket_id(tickets):
    """Generate the next ticket ID from the highest existing numeric ID."""
    highest_id = 0

    for ticket in tickets:
        ticket_id = ticket.get("id", "")

        if (
            isinstance(ticket_id, str)
            and ticket_id.startswith("T")
            and ticket_id[1:].isdigit()
        ):
            highest_id = max(highest_id, int(ticket_id[1:]))

    return f"T{highest_id + 1:03d}"
