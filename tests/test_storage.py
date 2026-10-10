
import unittest
import os

from campusflow.storage import (
    save_tickets,
    load_tickets,
    generate_ticket_id,
)


class TestStorage(unittest.TestCase):

    def setUp(self):
        self.path = "data/test_unittest_tickets.json"

        self.tickets = [
            {
                "id": "T001",
                "title": "Network connection is down",
                "category": "Network",
                "urgency": "high",
                "affected_users": 12,
                "priority": "critical",
                "status": "open",
                "assigned_to": None
            }
        ]

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_save_and_load_tickets(self):
        save_tickets(self.tickets, self.path)

        loaded_tickets = load_tickets(self.path)

        self.assertEqual(loaded_tickets, self.tickets)

    def test_load_rejects_non_dictionary_ticket(self):
        with open(self.path, "w", encoding="utf-8") as file:
            file.write(
                '{"schema_version": 1, "tickets": ["not a valid ticket"]}'
            )

        with self.assertRaises(ValueError):
            load_tickets(self.path)

    def test_load_missing_file_returns_empty_list(self):
        loaded_tickets = load_tickets(
            "data/file_that_does_not_exist.json"
        )

        self.assertEqual(loaded_tickets, [])

    def test_load_rejects_malformed_json(self):
        with open(self.path, "w", encoding="utf-8") as file:
            file.write('{"schema_version": 1, "tickets": [}')

        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            load_tickets(self.path)

    def test_load_rejects_unsupported_schema_version(self):
        with open(self.path, "w", encoding="utf-8") as file:
            file.write('{"schema_version": 2, "tickets": []}')

        with self.assertRaisesRegex(
            ValueError, "unsupported or missing schema version"
        ):
            load_tickets(self.path)

    def test_load_rejects_non_list_tickets(self):
        with open(self.path, "w", encoding="utf-8") as file:
            file.write(
                '{"schema_version": 1, "tickets": "not a list"}'
            )

        with self.assertRaisesRegex(
            ValueError, "expected 'tickets' to be a list"
        ):
            load_tickets(self.path)

    def test_generate_first_ticket_id(self):
        ticket_id = generate_ticket_id([])

        self.assertEqual(ticket_id, "T001")

    def test_generate_next_ticket_id(self):
        tickets = [
            {"id": "T001"},
            {"id": "T005"},
            {"id": "T003"},
        ]

        ticket_id = generate_ticket_id(tickets)

        self.assertEqual(ticket_id, "T006")

    def test_ticket_ids_remain_unique_after_save_and_reload(self):
        # Save the existing ticket to the JSON file.
        save_tickets(self.tickets, self.path)

        # Load the saved tickets, simulating a program restart.
        loaded_tickets = load_tickets(self.path)

        # Generate the next ID from the loaded tickets.
        next_id = generate_ticket_id(loaded_tickets)

        # Collect the IDs that already exist.
        existing_ids = [
            ticket["id"] for ticket in loaded_tickets
        ]

        # Confirm the new ID is not a duplicate.
        self.assertNotIn(next_id, existing_ids)
        self.assertEqual(next_id, "T002")


if __name__ == "__main__":
    unittest.main()