PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}


def _ticket_number(ticket):
    """Numeric part of a ticket ID, so 'T10' sorts after 'T2' (not before)."""
    ticket_id = ticket.get("id", "")
    if (
        isinstance(ticket_id, str)
        and ticket_id.startswith("T")
        and ticket_id[1:].isascii()
        and ticket_id[1:].isdigit()
    ):
        return int(ticket_id[1:])
    return float("inf")


def sort_by_priority(tickets):
    """Return a NEW list: critical > high > medium > low, then numeric ID.

    Does not filter and does not modify the tickets. Shared by the Open Work
    Queue and the "sort search results" view so both order tickets identically.
    """
    def sort_key(ticket):
        return PRIORITY_ORDER.get(ticket.get("priority"), 4), _ticket_number(ticket)

    return sorted(tickets, key=sort_key)


def get_queue(tickets):
    """The original Open Work Queue: OPEN tickets only, in priority order.

    in_progress and resolved tickets are deliberately excluded.
    """
    open_tickets = [
        ticket for ticket in tickets
        if ticket.get("status") == "open"
    ]
    return sort_by_priority(open_tickets)


def display_queue(tickets):
    queue = get_queue(tickets)

    if not queue:
        print("The open work queue is empty.")
        return

    for ticket in queue:
        print(
            f"{ticket['id']} | {ticket['title']} | "
            f"{ticket['priority']} | {ticket['status']}"
        )
