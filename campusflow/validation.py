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