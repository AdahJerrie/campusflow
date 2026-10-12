PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}


def get_queue(tickets):
    """Return unresolved tickets by priority, then numeric ticket ID."""
    unresolved = [
        ticket for ticket in tickets
        if ticket.get("status") != "resolved"
    ]

    def sort_key(ticket):
        ticket_id = ticket.get("id", "")
        number = (
            int(ticket_id[1:])
            if ticket_id.startswith("T") and ticket_id[1:].isdigit()
            else float("inf")
        )
        priority = PRIORITY_ORDER.get(ticket.get("priority"), 4)
        return priority, number

    return sorted(unresolved, key=sort_key)


def display_queue(tickets):
    queue = get_queue(tickets)

    if not queue:
        print("The queue is empty.")
        return

    for ticket in queue:
        print(
            f"{ticket['id']} | {ticket['title']} | "
            f"{ticket['priority']} | {ticket['status']}"
        )
