
import json
import os


def save_tickets(tickets, path):
    data = {
        "schema_version": 1,
        "tickets": tickets
    }

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_tickets(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(
                f"Cannot load tickets from '{path}': "
                "expected a JSON object."
            )

        if data.get("schema_version") != 1:
            raise ValueError(
                f"Cannot load tickets from '{path}': "
                "unsupported or missing schema version."
            )

        tickets = data.get("tickets")

        if not isinstance(tickets, list):
            raise ValueError(
                f"Cannot load tickets from '{path}': "
                "expected 'tickets' to be a list."
            )

        for ticket in tickets:
            if not isinstance(ticket, dict):
                raise ValueError(
                    f"Cannot load tickets from '{path}': "
                    "each ticket must be a JSON object."
                )

        return tickets

    except FileNotFoundError:
        return []

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Cannot load tickets from '{path}': "
            f"invalid JSON at line {error.lineno}, "
            f"column {error.colno}."
        ) from error


def generate_ticket_id(tickets):
    highest_id = 0

    for ticket in tickets:
        ticket_id = ticket["id"]

        if ticket_id.startswith("T") and ticket_id[1:].isdigit():
            number = int(ticket_id[1:])

            if number > highest_id:
                highest_id = number

    next_number = highest_id + 1

    return f"T{next_number:03d}"

