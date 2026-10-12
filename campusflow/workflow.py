
ALLOWED_STATUS_TRANSITIONS = {
    "open": {"in_progress"},
    "in_progress": {"resolved"},
    "resolved": set(),
}


def _find_ticket(tickets, ticket_id):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    raise ValueError(f"Unknown ticket ID: '{ticket_id}'.")


def _reject_if_resolved(ticket):
    if ticket["status"] == "resolved":
        raise ValueError(
            "Resolved tickets can only be modified after an explicit reopen."
        )


def assign_ticket(tickets, ticket_id, staff_name):
    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff name must not be blank.")

    ticket = _find_ticket(tickets, ticket_id)
    _reject_if_resolved(ticket)

    ticket["assigned_to"] = staff_name.strip()
    return ticket


def update_ticket_status(tickets, ticket_id, new_status):
    ticket = _find_ticket(tickets, ticket_id)
    _reject_if_resolved(ticket)

    if new_status == "in_progress" and not ticket.get("assigned_to"):
        raise ValueError("Cannot move an unassigned ticket to in_progress.")

    current_status = ticket["status"]
    allowed = ALLOWED_STATUS_TRANSITIONS.get(current_status, set())

    if new_status not in allowed:
        raise ValueError(
            f"Invalid status transition from '{current_status}' to '{new_status}'."
        )

    ticket["status"] = new_status
    return ticket


def reopen_ticket(tickets, ticket_id):
    ticket = _find_ticket(tickets, ticket_id)

    if ticket["status"] != "resolved":
        raise ValueError("Only resolved tickets can be reopened.")

    ticket["status"] = "open"
    return ticket
