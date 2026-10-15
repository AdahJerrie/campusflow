import copy
import unittest

from campusflow.queue import sort_by_priority
from campusflow.search import search_tickets


def make_ticket(ticket_id, title, category="Network", priority="low",
                status="open", assigned_to=None):
    return {
        "id": ticket_id, "title": title, "category": category,
        "urgency": "low", "affected_users": 1, "priority": priority,
        "status": status, "assigned_to": assigned_to, "notes": [],
    }


class TestSearchTickets(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            make_ticket("T001", "WiFi down in Lab 2", "Network", "high", "open"),
            make_ticket("T002", "wifi login slow", "Network", "low", "in_progress", "Sam"),
            make_ticket("T003", "WiFi dongle broken", "Hardware", "medium", "open"),
            make_ticket("T004", "Printer jam", "Hardware", "low", "open"),
            make_ticket("T005", "Wi-Fi password reset", "Software", "low", "resolved", "Ann"),
        ]

    def ids(self, results):
        return [ticket["id"] for ticket in results]

    def test_title_search_ignores_case_and_matches_substring(self):
        self.assertEqual(self.ids(search_tickets(self.tickets, "WIFI")),
                         ["T001", "T002", "T003"])
        self.assertEqual(self.ids(search_tickets(self.tickets, "lab 2")), ["T001"])
        # Same punctuation matches regardless of case.
        self.assertEqual(self.ids(search_tickets(self.tickets, "WI-FI")), ["T005"])
        self.assertEqual(self.ids(search_tickets(self.tickets, "wi-fi")), ["T005"])

    def test_combined_filters_use_and_not_or(self):
        results = search_tickets(self.tickets, "wifi", "Network", "open")
        # OR logic would also return T002 (network), T003 (wifi) and T004 (open).
        self.assertEqual(self.ids(results), ["T001"])

    def test_empty_filters_mean_do_not_filter(self):
        results = search_tickets(self.tickets, "", "", "", "")
        self.assertEqual(self.ids(results), ["T001", "T002", "T003", "T004", "T005"])
        results = search_tickets(self.tickets)
        self.assertEqual(len(results), 5)

    def test_category_status_priority_filters_are_normalised(self):
        results = search_tickets(self.tickets, category=" network ", status="IN_PROGRESS")
        self.assertEqual(self.ids(results), ["T002"])
        self.assertEqual(self.ids(search_tickets(self.tickets, priority="HIGH")), ["T001"])

    def test_invalid_filters_are_rejected(self):
        bad_filters = [
            {"category": "Plumbing"},
            {"status": "closed"},
            {"priority": "urgent"},
            {"title_query": 123},
            {"status": 5},
        ]
        for kwargs in bad_filters:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    search_tickets(self.tickets, **kwargs)

    def test_search_never_modifies_the_collection(self):
        before = copy.deepcopy(self.tickets)

        results = search_tickets(self.tickets, "wifi", "Network")
        self.assertEqual(self.tickets, before)

        # Changing a returned ticket must not leak back into the collection.
        results[0]["title"] = "CHANGED"
        results[0]["notes"].append({"note_id": "N001"})
        self.assertEqual(self.tickets, before)

    def test_no_match_returns_empty_list(self):
        self.assertEqual(search_tickets(self.tickets, "nonexistent"), [])
        self.assertEqual(search_tickets([], "wifi"), [])

    def test_sort_results_by_priority_then_numeric_id(self):
        tickets = [
            make_ticket("T10", "a", priority="high"),
            make_ticket("T2", "b", priority="high"),
            make_ticket("T3", "c", priority="critical"),
            make_ticket("T1", "d", priority="low"),
        ]
        before = copy.deepcopy(tickets)
        result = sort_by_priority(tickets)
        # T2 before T10: numeric, not text, comparison of the tie-breaker.
        self.assertEqual([t["id"] for t in result], ["T3", "T2", "T10", "T1"])
        self.assertEqual(tickets, before)


if __name__ == "__main__":
    unittest.main()
