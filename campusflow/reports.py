from collections import Counter


def generate_report(tickets):
    """Return summary totals and status/priority breakdowns."""
    status_counts = Counter(
        ticket.get("status", "unknown") for ticket in tickets
    )
    priority_counts = Counter(
        ticket.get("priority", "unknown") for ticket in tickets
    )

    return {
        "total": len(tickets),
        "by_status": dict(status_counts),
        "by_priority": dict(priority_counts),
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
