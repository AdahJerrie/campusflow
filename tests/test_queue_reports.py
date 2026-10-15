import unittest

from campusflow.queue import get_queue
from campusflow.reports import generate_report


class TestQueue(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            {"id": "T003", "priority": "low", "status": "open"},
            {"id": "T002", "priority": "critical", "status": "open"},
            {"id": "T001", "priority": "high", "status": "open"},
            {"id": "T004", "priority": "critical", "status": "resolved"},
            {"id": "T005", "priority": "high", "status": "open"},
        ]

    def test_queue_sorts_by_priority_then_id(self):
        result = get_queue(self.tickets)
        self.assertEqual(
            [ticket["id"] for ticket in result],
            ["T002", "T001", "T005", "T003"],
        )

    def test_queue_excludes_resolved_tickets(self):
        result = get_queue(self.tickets)
        self.assertNotIn("T004", [ticket["id"] for ticket in result])

    def test_empty_queue(self):
        self.assertEqual(get_queue([]), [])

    def test_original_queue_shows_only_open_tickets(self):
        tickets = self.tickets + [
            {"id": "T006", "priority": "critical", "status": "in_progress"},
        ]
        result = get_queue(tickets)
        self.assertNotIn("T006", [ticket["id"] for ticket in result])
        self.assertTrue(all(ticket["status"] == "open" for ticket in result))

    def test_queue_breaks_ties_by_numeric_id_not_text(self):
        tickets = [
            {"id": "T10", "priority": "high", "status": "open"},
            {"id": "T2", "priority": "high", "status": "open"},
        ]
        self.assertEqual([t["id"] for t in get_queue(tickets)], ["T2", "T10"])


class TestReports(unittest.TestCase):
    def test_report_counts_status_and_priority(self):
        tickets = [
            {"status": "open", "priority": "high"},
            {"status": "open", "priority": "high"},
            {"status": "resolved", "priority": "low"},
        ]

        report = generate_report(tickets)

        self.assertEqual(report["total"], 3)
        self.assertEqual(
            report["by_status"], {"open": 2, "resolved": 1}
        )
        self.assertEqual(
            report["by_priority"], {"high": 2, "low": 1}
        )

    def test_empty_report(self):
        self.assertEqual(
            generate_report([]),
            {
                "total": 0,
                "by_status": {},
                "by_priority": {},
                "by_category": {},
                "unresolved": 0,
                "resolved": 0,
                "resolution_percent": 0.0,
            },
        )


if __name__ == "__main__":
    unittest.main()
