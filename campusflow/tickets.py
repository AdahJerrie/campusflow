
from campusflow.storage import generate_ticket_id


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


def calculate_priority(urgency, affected_users):
    if urgency == "high" and affected_users >= 10:
        return "critical"

    if urgency == "high" or affected_users >= 10:
        return "high"

    if urgency == "medium" or affected_users >= 3:
        return "medium"

    return "low"


def create_ticket(tickets, title, category, urgency, affected_users):
    title = validate_title(title)
    category = validate_category(category)
    urgency = validate_urgency(urgency)
    affected_users = validate_affected_users(affected_users)

    ticket_id = generate_ticket_id(tickets)
    priority = calculate_priority(urgency, affected_users)

    ticket = {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": priority,
        "status": "open",
        "assigned_to": None,
    }

    return ticket


def list_tickets(tickets):
    if not tickets:
        print("No tickets found.")
        return

    for ticket in tickets:
        print(
            f"{ticket['id']} | "
            f"{ticket['title']} | "
            f"{ticket['priority']} | "
            f"{ticket['status']}"
        )


def get_ticket_by_id(tickets, ticket_id):
    if not isinstance(ticket_id, str):
        return None

    ticket_id = ticket_id.strip().upper()

    for ticket in tickets:
        if ticket["id"].upper() == ticket_id:
            return ticket

    return None