
from campusflow.storage import generate_ticket_id
from campusflow.validation import (
    validate_title,
    validate_category,
    validate_urgency,
    validate_affected_users,
    calculate_priority,
)

        


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
        "notes": [],
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