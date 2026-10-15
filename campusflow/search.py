"""Read-only ticket search with combined (AND) filters.

Nothing here prints or asks for input, so it can be tested directly.
"""
import copy

from campusflow.validation import (
    validate_category,
    VALID_STATUSES,
    VALID_PRIORITIES,
)


def _is_blank(value):
    return value is None or (isinstance(value, str) and not value.strip())


def normalize_category_filter(value):
    """'' (no filter) or a canonical category such as 'Network'. Else ValueError."""
    if _is_blank(value):
        return ""
    return validate_category(value)


def normalize_status_filter(value):
    """'' (no filter) or one of open / in_progress / resolved. Else ValueError."""
    if _is_blank(value):
        return ""
    if not isinstance(value, str):
        raise ValueError("Status filter must be text.")
    status = value.strip().lower()
    if status not in VALID_STATUSES:
        raise ValueError("Invalid status. Choose open, in_progress, or resolved.")
    return status


def normalize_priority_filter(value):
    """'' (no filter) or one of critical / high / medium / low. Else ValueError."""
    if _is_blank(value):
        return ""
    if not isinstance(value, str):
        raise ValueError("Priority filter must be text.")
    priority = value.strip().lower()
    if priority not in VALID_PRIORITIES:
        raise ValueError("Invalid priority. Choose critical, high, medium, or low.")
    return priority


def search_tickets(tickets, title_query="", category="", status="", priority=""):
    """Return COPIES of the tickets that match EVERY supplied filter (AND).

    Before: tickets is a list of ticket dicts; filters are strings or empty.
    After success: a new list in the original ticket order; `tickets` is not
        modified and the returned dicts are independent copies.
    After failure: ValueError for an invalid filter value; nothing changed.
    An empty filter means "do not filter on this field".
    """
    if _is_blank(title_query):
        needle = ""
    elif isinstance(title_query, str):
        needle = title_query.strip().casefold()
    else:
        raise ValueError("Title search must be text.")

    # Validate every filter BEFORE looking at a single ticket.
    category = normalize_category_filter(category)
    status = normalize_status_filter(status)
    priority = normalize_priority_filter(priority)

    results = []
    for ticket in tickets:
        if needle and needle not in str(ticket.get("title", "")).casefold():
            continue
        if category and ticket.get("category") != category:
            continue
        if status and ticket.get("status") != status:
            continue
        if priority and ticket.get("priority") != priority:
            continue
        results.append(copy.deepcopy(ticket))
    return results
