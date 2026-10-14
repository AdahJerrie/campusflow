import json
import os
import tempfile

from campusflow.validation import validate_ticket

SCHEMA_VERSION = 1


def validate_collection(tickets):
    """Validate every record before anything is used. Returns a NEW list.

    Before: tickets is anything json.load produced.
    After success: a list of validated deep copies with unique IDs.
    After failure: ValueError; the caller's data is untouched.
    """
    if not isinstance(tickets, list):
        raise ValueError("expected 'tickets' to be a list.")

    validated, seen_ids = [], set()
    for index, ticket in enumerate(tickets, start=1):
        try:
            clean = validate_ticket(ticket)
        except ValueError as error:
            raise ValueError(f"record {index}: {error}") from error
        if clean["id"] in seen_ids:
            raise ValueError(f"duplicate ticket ID '{clean['id']}'.")
        seen_ids.add(clean["id"])
        validated.append(clean)
    return validated


def save_tickets(tickets, path):
    """Validate first, write to a temp file, then atomically replace."""
    data = {"schema_version": SCHEMA_VERSION, "tickets": validate_collection(tickets)}

    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)

    fd, temp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        os.replace(temp_path, path)
    except BaseException:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


def load_tickets(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(
                f"Cannot load tickets from '{path}': expected a JSON object."
            )

        version = data.get("schema_version")
        # type(...) is int rejects True, which == 1 in Python
        if type(version) is not int or version != SCHEMA_VERSION:
            raise ValueError(
                f"Cannot load tickets from '{path}': "
                "unsupported or missing schema version."
            )

        try:
            return validate_collection(data.get("tickets"))
        except ValueError as error:
            raise ValueError(f"Cannot load tickets from '{path}': {error}") from error

    except FileNotFoundError:
        return []

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Cannot load tickets from '{path}': "
            f"invalid JSON at line {error.lineno}, column {error.colno}."
        ) from error


def reload_into(tickets, path):
    """Replace the in-memory list only if the whole file is valid.

    A missing file counts as an empty collection (same as load_tickets).
    """
    loaded = load_tickets(path)      # raises before we touch `tickets`
    tickets[:] = loaded
    return tickets


def generate_ticket_id(tickets):
    highest_id = 0
    for ticket in tickets:
        ticket_id = ticket.get("id") if isinstance(ticket, dict) else None
        if (
            isinstance(ticket_id, str)
            and ticket_id.startswith("T")
            and ticket_id[1:].isascii()
            and ticket_id[1:].isdigit()
        ):
            highest_id = max(highest_id, int(ticket_id[1:]))
    return f"T{highest_id + 1:03d}"