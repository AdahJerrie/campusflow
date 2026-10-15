"""Bug-hunter test (Engineer B -> Engineer A's modules).

Invariant made visible: every function that takes a ticket ID treats the same
spellings as the same ticket ('T001', 't001', ' T001 ').

Initial state: one open ticket T001, one resolved ticket T002 (both assigned).
Input:         the lowercase / padded ID spellings.
Expected:      notes, assignment, status change and reopen all accept them.
Actual (before the fix): add_note accepted 't001' but assign_ticket,
    update_ticket_status and reopen_ticket raised "Unknown ticket ID: 't001'",
    because workflow._find_ticket compared the raw text.
"""
import unittest

from campusflow.notes import add_note
from campusflow.workflow import assign_ticket, reopen_ticket, update_ticket_status


def make_ticket(ticket_id, status, assigned_to):
    return {
        "id": ticket_id, "title": "Sample", "category": "Network",
        "urgency": "low", "affected_users": 1, "priority": "low",
        "status": status, "assigned_to": assigned_to, "notes": [],
    }


class TestTicketIdConsistency(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            make_ticket("T001", "open", "Sam"),
            make_ticket("T002", "resolved", "Ann"),
        ]

    def test_lookup_accepts_the_same_id_spellings_everywhere(self):
        for spelling in ("T001", "t001", " T001 ", " t001"):
            with self.subTest(spelling=spelling):
                add_note(self.tickets, spelling, "Mentor A", "Consistent lookup check")
                assign_ticket(self.tickets, spelling, "Sam")

        update_ticket_status(self.tickets, "t001", "in_progress")
        self.assertEqual(self.tickets[0]["status"], "in_progress")

        reopen_ticket(self.tickets, " t002 ")
        self.assertEqual(self.tickets[1]["status"], "open")

    def test_malformed_or_unknown_ids_still_raise_value_error(self):
        for bad in ("", "abc", "T", "T99", None, 7):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    assign_ticket(self.tickets, bad, "Sam")


if __name__ == "__main__":
    unittest.main()
