import contextlib
import io
import unittest

from campusflow.reports import display_report, generate_report
from campusflow.tickets import create_ticket
from campusflow.workflow import assign_ticket, reopen_ticket, update_ticket_status


def build_fixture():
    """Three tickets created the real way: T001 high/Network, T002 low/Hardware, T003 medium/Software."""
    tickets = []
    for title, category, urgency, users in (
        ("Router down", "Network", "high", 12),
        ("Mouse broken", "Hardware", "low", 1),
        ("Install IDE", "Software", "medium", 2),
    ):
        tickets.append(create_ticket(tickets, title, category, urgency, users))
    return tickets


class TestReports(unittest.TestCase):
    def test_empty_report_returns_zero_percent_without_crashing(self):
        report = generate_report([])
        self.assertEqual(report["total"], 0)
        self.assertEqual(report["unresolved"], 0)
        self.assertEqual(report["resolved"], 0)
        self.assertEqual(report["resolution_percent"], 0.0)

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            display_report([])
        self.assertIn("Resolution rate: 0.0%", output.getvalue())

    def test_counts_match_known_fixture_after_resolve_and_reopen(self):
        tickets = build_fixture()
        assign_ticket(tickets, "T001", "Sam")
        update_ticket_status(tickets, "T001", "in_progress")
        update_ticket_status(tickets, "T001", "resolved")

        report = generate_report(tickets)
        self.assertEqual(report["by_status"], {"resolved": 1, "open": 2})
        self.assertEqual(report["unresolved"], 2)
        self.assertEqual(report["resolved"], 1)
        self.assertEqual(report["resolution_percent"], 33.3)

        # Reopened tickets count by their CURRENT status, not their history.
        reopen_ticket(tickets, "T001")
        report = generate_report(tickets)
        self.assertEqual(report["by_status"], {"open": 3})
        self.assertEqual(report["unresolved"], 3)
        self.assertEqual(report["resolved"], 0)
        self.assertEqual(report["resolution_percent"], 0.0)

    def test_in_progress_counts_as_unresolved(self):
        tickets = build_fixture()
        assign_ticket(tickets, "T002", "Sam")
        update_ticket_status(tickets, "T002", "in_progress")

        report = generate_report(tickets)
        self.assertEqual(report["by_status"]["in_progress"], 1)
        self.assertEqual(report["unresolved"], 3)  # 2 open + 1 in_progress
        self.assertEqual(report["resolved"], 0)

    def test_no_ticket_is_double_counted(self):
        tickets = build_fixture()
        assign_ticket(tickets, "T001", "Sam")
        update_ticket_status(tickets, "T001", "in_progress")

        report = generate_report(tickets)
        total = report["total"]
        self.assertEqual(sum(report["by_status"].values()), total)
        self.assertEqual(sum(report["by_priority"].values()), total)
        self.assertEqual(sum(report["by_category"].values()), total)
        self.assertEqual(report["unresolved"] + report["resolved"], total)

    def test_category_and_priority_counts(self):
        report = generate_report(build_fixture())
        self.assertEqual(report["by_category"],
                         {"Network": 1, "Hardware": 1, "Software": 1})
        self.assertEqual(report["by_priority"],
                         {"critical": 1, "low": 1, "medium": 1})

    def test_full_resolution_is_one_hundred_percent(self):
        tickets = [{"status": "resolved", "priority": "low", "category": "Other"}]
        self.assertEqual(generate_report(tickets)["resolution_percent"], 100.0)

    def test_display_report_prints_every_required_line(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            display_report(build_fixture())
        text = output.getvalue()
        for expected in ("Total tickets: 3", "By status:", "By priority:",
                         "By category:", "Network: 1",
                         "Unresolved (open + in_progress): 3", "Resolved: 0",
                         "Resolution rate: 0.0%"):
            self.assertIn(expected, text)


if __name__ == "__main__":
    unittest.main()
