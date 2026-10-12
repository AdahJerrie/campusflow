
def assign_ticket(tickets, ticket_id, staff_name):
    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff name must not be blank.")

    name = staff_name.strip()

    for ticket in tickets:
        if ticket["id"] == ticket_id:
            ticket["assigned_to"] = name
            return ticket

    raise ValueError(f"Unknown ticket ID: '{ticket_id}'.")
