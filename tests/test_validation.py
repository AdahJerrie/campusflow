import copy
import unittest
from campusflow.validation import validate_ticket_id, validate_staff_name


from campusflow.tickets import (
    validate_affected_users,
    validate_category,
    validate_title,
    calculate_priority,
    create_ticket,
)


class TestValidation(unittest.TestCase):
    def test_affected_users_rejects_bad_types_and_values(self):
        for bad in (0, -1, 2.5, "5", True, False, None):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    validate_affected_users(bad)

    def test_affected_users_accepts_positive_int(self):
        self.assertEqual(validate_affected_users(1), 1)

    def test_category_is_normalised_and_bad_values_rejected(self):
        self.assertEqual(validate_category("  network "), "Network")
        for bad in ("Banana", "", 5, None):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    validate_category(bad)

    def test_title_is_trimmed_and_blank_rejected(self):
        self.assertEqual(validate_title("  Wi-Fi down "), "Wi-Fi down")
        with self.assertRaises(ValueError):
            validate_title("   ")

    def test_priority_rule_boundaries_and_precedence(self):
        cases = [
            ("high", 10, "critical"),   # critical beats high
            ("high", 9, "high"),
            ("low", 10, "high"),
            ("medium", 1, "medium"),
            ("low", 3, "medium"),
            ("low", 2, "low"),
        ]
        for urgency, users, expected in cases:
            with self.subTest(urgency=urgency, users=users):
                self.assertEqual(calculate_priority(urgency, users), expected)

    def test_failed_create_does_not_touch_collection(self):
        tickets = [{"id": "T001"}]
        before = copy.deepcopy(tickets)
        with self.assertRaises(ValueError):
            create_ticket(tickets, "Title", "Network", "high", True)
        self.assertEqual(tickets, before)

        from campusflow.validation import validate_ticket_id, validate_staff_name

class TestNewValidators(unittest.TestCase):
    def test_ticket_id_normalised_and_bad_values_rejected(self):
        self.assertEqual(validate_ticket_id(" t001 "), "T001")
        for bad in ("", "T", "X001", "T0O1", "T²", 5, None):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    validate_ticket_id(bad)

    def test_staff_name_trimmed_and_blank_rejected(self):
        self.assertEqual(validate_staff_name("  Ada "), "Ada")
        for bad in ("", "   ", None, 5):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    validate_staff_name(bad)


if __name__ == "__main__":
    unittest.main()