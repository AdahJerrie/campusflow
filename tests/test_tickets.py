
import unittest

from campusflow.tickets import (
    create_ticket,
    calculate_priority,
    get_ticket_by_id,
    list_tickets,
)


class TestTicketCreation(unittest.TestCase):

    def test_create_ticket_successfully(self):
        tickets = []

        ticket = create_ticket(
            tickets,
            "Campus Wi-Fi is down",
            "network",
            "high",
            12,
        )

        self.assertEqual(ticket["id"], "T001")
        self.assertEqual(ticket["title"], "Campus Wi-Fi is down")
        self.assertEqual(ticket["category"], "Network")
        self.assertEqual(ticket["urgency"], "high")
        self.assertEqual(ticket["affected_users"], 12)
        self.assertEqual(ticket["priority"], "critical")
        self.assertEqual(ticket["status"], "open")
        self.assertIsNone(ticket["assigned_to"])

    def test_calculate_critical_priority(self):
        self.assertEqual(calculate_priority("high", 12), "critical")

    def test_calculate_high_priority(self):
        self.assertEqual(calculate_priority("high", 2), "high")

    def test_calculate_medium_priority(self):
        self.assertEqual(calculate_priority("low", 4), "medium")

    def test_calculate_low_priority(self):
        self.assertEqual(calculate_priority("low", 1), "low")

    def test_reject_blank_title(self):
        with self.assertRaises(ValueError):
            create_ticket([], "   ", "Network", "high", 5)

    def test_reject_invalid_category(self):
        with self.assertRaises(ValueError):
            create_ticket([], "Wi-Fi issue", "Food", "high", 5)

    def test_reject_invalid_urgency(self):
        with self.assertRaises(ValueError):
            create_ticket([], "Wi-Fi issue", "Network", "urgent", 5)

    def test_reject_zero_affected_users(self):
        with self.assertRaises(ValueError):
            create_ticket([], "Wi-Fi issue", "Network", "high", 0)


    def test_find_ticket_by_id(self):
        tickets = []
        ticket = create_ticket(
            tickets, "Wi-Fi issue", "Network", "high", 5
        )
        tickets.append(ticket)

        result = get_ticket_by_id(tickets, "T001")

        self.assertEqual(result["title"], "Wi-Fi issue")

    def test_find_ticket_with_lowercase_id(self):
        tickets = []
        ticket = create_ticket(
            tickets, "Wi-Fi issue", "Network", "high", 5
        )
        tickets.append(ticket)

        result = get_ticket_by_id(tickets, "t001")

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "T001")

    def test_missing_ticket_returns_none(self):
        result = get_ticket_by_id([], "T999")

        self.assertIsNone(result)


    def test_list_tickets_displays_ticket_details(self):
        from io import StringIO
        from unittest.mock import patch

        tickets = [
            create_ticket(
                [], "Wi-Fi issue", "Network", "high", 12
            )
        ]

        with patch("sys.stdout", new_callable=StringIO) as output:
            list_tickets(tickets)

        self.assertIn("T001", output.getvalue())
        self.assertIn("Wi-Fi issue", output.getvalue())
        self.assertIn("critical", output.getvalue())
        self.assertIn("open", output.getvalue())

    def test_list_empty_tickets(self):
        from io import StringIO
        from unittest.mock import patch

        with patch("sys.stdout", new_callable=StringIO) as output:
            list_tickets([])

        self.assertIn("No tickets found.", output.getvalue())


if __name__ == "__main__":
    unittest.main()