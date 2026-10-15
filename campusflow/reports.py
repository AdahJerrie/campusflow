from collections import Counter


def generate_report(tickets):
    """Return summary totals and breakdowns.

    Every ticket is counted once, by its CURRENT status, priority and category.
    unresolved = open + in_progress; resolved = resolved.
    resolution_percent = resolved / total * 100, or 0.0 when there are no tickets.
    """
    status_counts = Counter(
        ticket.get("status", "unknown") for ticket in tickets
    )
    priority_counts = Counter(
        ticket.get("priority", "unknown") for ticket in tickets
    )
    category_counts = Counter(
        ticket.get("category", "unknown") for ticket in tickets
    )

    total = len(tickets)
    resolved = status_counts.get("resolved", 0)
    unresolved = status_counts.get("open", 0) + status_counts.get("in_progress", 0)

    # An empty collection would divide by zero, so report 0% explicitly.
    resolution_percent = round(resolved / total * 100, 1) if total else 0.0

    return {
        "total": total,
        "by_status": dict(status_counts),
        "by_priority": dict(priority_counts),
        "by_category": dict(category_counts),
        "unresolved": unresolved,
        "resolved": resolved,
        "resolution_percent": resolution_percent,
    }


def display_report(tickets):
    report = generate_report(tickets)

    print(f"Total tickets: {report['total']}")

    print("By status:")
    for status in ("open", "in_progress", "resolved"):
        print(f"  {status}: {report['by_status'].get(status, 0)}")

    print("By priority:")
    for priority in ("critical", "high", "medium", "low"):
        print(f"  {priority}: {report['by_priority'].get(priority, 0)}")

    print("By category:")
    for category in ("Network", "Hardware", "Software", "Other"):
        print(f"  {category}: {report['by_category'].get(category, 0)}")

    print(f"Unresolved (open + in_progress): {report['unresolved']}")
    print(f"Resolved: {report['resolved']}")
    print(f"Resolution rate: {report['resolution_percent']}%")
