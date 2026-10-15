
import unittest
import os
import json

from campusflow.storage import (
    save_tickets,
    load_tickets,
    generate_ticket_id,
)


class TestStorage(unittest.TestCase):

    def setUp(self):
        os.makedirs("data", exist_ok=True)
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
                "assigned_to": None,
                "notes": [],
            }
        ]

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_save_and_load_tickets(self):
        save_tickets(self.tickets, self.path)
        loaded_tickets = load_tickets(self.path)
        self.assertEqual(loaded_tickets, self.tickets)

    def test_load_rejects_duplicate_ticket_ids(self):
        ticket_one = self.tickets[0].copy()
        ticket_two = self.tickets[0].copy()

        ticket_one["id"] = "T001"
        ticket_two["id"] = "T001"

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "schema_version": 1,
                    "tickets": [ticket_one, ticket_two],
                },
                file,
            )

        with self.assertRaisesRegex(ValueError, "Duplicate ticket ID"):
            load_tickets(self.path)

    def test_load_rejects_invalid_ticket_id(self):
        invalid_ticket = {**self.tickets[0], "id": "BAD-ID"}

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {"schema_version": 1, "tickets": [invalid_ticket]},
                file,
            )

        with self.assertRaisesRegex(ValueError, "valid ticket ID"):
            load_tickets(self.path)

    def test_load_rejects_invalid_urgency(self):
        invalid_ticket = self.tickets[0].copy()
        invalid_ticket["urgency"] = "extreme"

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {"schema_version": 1, "tickets": [invalid_ticket]},
                file,
            )

        with self.assertRaisesRegex(ValueError, "urgency"):
            load_tickets(self.path)

    def test_load_rejects_incorrect_priority(self):
        invalid_ticket = self.tickets[0].copy()
        invalid_ticket["priority"] = "low"

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {"schema_version": 1, "tickets": [invalid_ticket]},
                file,
            )

        with self.assertRaisesRegex(ValueError, "Priority"):
            load_tickets(self.path)

    def test_load_rejects_invalid_status(self):
        invalid_ticket = self.tickets[0].copy()
        invalid_ticket["status"] = "pending"

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {"schema_version": 1, "tickets": [invalid_ticket]},
                file,
            )

        with self.assertRaisesRegex(ValueError, "status"):
            load_tickets(self.path)

    def test_load_rejects_invalid_category(self):
        invalid_ticket = {**self.tickets[0], "category": "Food"}

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {"schema_version": 1, "tickets": [invalid_ticket]},
                file,
            )

        with self.assertRaisesRegex(ValueError, "category"):
            load_tickets(self.path)

    def test_load_rejects_unhashable_category(self):
        invalid_ticket = {
            **self.tickets[0],
            "category": ["Network"],
        }

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {"schema_version": 1, "tickets": [invalid_ticket]},
                file,
            )

        with self.assertRaisesRegex(ValueError, "category"):
            load_tickets(self.path)

    def test_load_rejects_non_dictionary_ticket(self):
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "schema_version": 1,
                    "tickets": ["not a valid ticket"],
                },
                file,
            )

        with self.assertRaisesRegex(ValueError, "dictionary"):
            load_tickets(self.path)

    def test_load_missing_file_returns_empty_list(self):
        missing_path = "data/file_that_does_not_exist.json"
        if os.path.exists(missing_path):
            os.remove(missing_path)

        self.assertEqual(load_tickets(missing_path), [])

    def test_load_rejects_malformed_json(self):
        with open(self.path, "w", encoding="utf-8") as file:
            file.write('{"schema_version": 1, "tickets": [}')

        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            load_tickets(self.path)

    def test_load_rejects_unsupported_schema_version(self):
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {"schema_version": 2, "tickets": []},
                file,
            )

        with self.assertRaisesRegex(
            ValueError, "unsupported or missing schema version"
        ):
            load_tickets(self.path)

    def test_load_rejects_boolean_schema_version(self):
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {"schema_version": True, "tickets": []},
                file,
            )

        with self.assertRaisesRegex(
            ValueError, "unsupported or missing schema version"
        ):
            load_tickets(self.path)

    def test_load_rejects_non_list_tickets(self):
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "schema_version": 1,
                    "tickets": "not a list",
                },
                file,
            )

        with self.assertRaisesRegex(ValueError, "list"):
            load_tickets(self.path)

    def test_generate_first_ticket_id(self):
        self.assertEqual(generate_ticket_id([]), "T001")

    def test_generate_next_ticket_id(self):
        tickets = [
            {"id": "T001"},
            {"id": "T005"},
            {"id": "T003"},
        ]

        self.assertEqual(generate_ticket_id(tickets), "T006")

    def test_ticket_ids_remain_unique_after_save_and_reload(self):
        save_tickets(self.tickets, self.path)
        loaded_tickets = load_tickets(self.path)

        next_id = generate_ticket_id(loaded_tickets)
        existing_ids = [ticket["id"] for ticket in loaded_tickets]

        self.assertNotIn(next_id, existing_ids)
        self.assertEqual(next_id, "T002")


if __name__ == "__main__":
    unittest.main()
