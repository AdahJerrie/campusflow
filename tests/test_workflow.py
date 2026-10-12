
import unittest

from campusflow.workflow import assign_ticket


class TestAssignTicket(unittest.TestCase):

    def setUp(self):
        self.tickets = [
            {
                "id": "T001",
                "title": "Network connection is down",
                "category": "Network",
                "urgency": "high",
                "affected_users": 12,
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
            }
        ]

    def test_assign_sets_staff_name(self):
        ticket = assign_ticket(self.tickets, "T001", "Ada")

        self.assertIs(ticket, self.tickets[0])
        self.assertEqual(ticket["assigned_to"], "Ada")

    def test_assign_trims_staff_name(self):
        ticket = assign_ticket(self.tickets, "T001", "  Ada  ")

        self.assertEqual(ticket["assigned_to"], "Ada")

    def test_assign_rejects_unknown_ticket_id(self):
        with self.assertRaisesRegex(ValueError, "Unknown ticket ID"):
            assign_ticket(self.tickets, "T999", "Ada")

        self.assertIsNone(self.tickets[0]["assigned_to"])

    def test_assign_rejects_blank_staff_name(self):
        with self.assertRaisesRegex(ValueError, "Staff name must not be blank"):
            assign_ticket(self.tickets, "T001", "   ")

        self.assertIsNone(self.tickets[0]["assigned_to"])


if __name__ == "__main__":
    unittest.main()
