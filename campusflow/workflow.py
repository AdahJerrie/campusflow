from campusflow.validation import validate_staff_name, validate_ticket_id


ALLOWED_STATUS_TRANSITIONS = {
    "open": {"in_progress"},
    "in_progress": {"resolved"},
    "resolved": set(),
}


def _find_ticket(tickets, ticket_id):
    # Same normalisation as notes.py: 't001' and ' T001 ' mean T001.
    ticket_id = validate_ticket_id(ticket_id)

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
    staff_name = validate_staff_name(staff_name)

    ticket = _find_ticket(tickets, ticket_id)
    _reject_if_resolved(ticket)

    ticket["assigned_to"] = staff_name
    return ticket


def update_ticket_status(tickets, ticket_id, new_status):

    if not isinstance(new_status, str):
        raise ValueError("Status must be text.")
    
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
