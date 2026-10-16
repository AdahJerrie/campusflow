import copy
import unittest

from campusflow.notes import add_note, get_notes, next_note_id
from campusflow.workflow import assign_ticket, update_ticket_status, reopen_ticket


def make_ticket(ticket_id="T001", status="open", assigned_to=None, notes=None):
    return {
        "id": ticket_id, "title": "Sample", "category": "Network",
        "urgency": "low", "affected_users": 1, "priority": "low",
        "status": status, "assigned_to": assigned_to,
        "notes": notes if notes is not None else [],
    }


class TestAddNote(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            make_ticket("T001"),
            make_ticket("T002", "resolved", "Sam", notes=[
                {"note_id": "N001", "author": "Mentor A", "message": "Earlier note"}
            ]),
        ]

    def test_valid_note_added_with_first_id(self):
        note = add_note(self.tickets, "T001", "  Mentor A ", "  Router reboot tried  ")
        self.assertEqual(note, {"note_id": "N001", "author": "Mentor A",
                                "message": "Router reboot tried"})
        self.assertEqual(self.tickets[0]["notes"], [note])

    def test_second_note_gets_next_id(self):
        add_note(self.tickets, "T001", "A", "first note")
        self.assertEqual(add_note(self.tickets, "T001", "B", "second note")["note_id"], "N002")

    def test_rejected_notes_do_not_consume_an_id(self):
        bad_inputs = [("", "valid message"), ("   ", "valid message"),
                      ("A", "abcd"), ("A", "   abc   "), ("A", "x" * 301),
                      (None, "valid message"), ("A", None), ("A", 12345)]
        for author, message in bad_inputs:
            with self.subTest(author=author, message=message):
                before = copy.deepcopy(self.tickets)
                with self.assertRaises(ValueError):
                    add_note(self.tickets, "T001", author, message)
                self.assertEqual(self.tickets, before)
        self.assertEqual(add_note(self.tickets, "T001", "A", "valid message")["note_id"], "N001")

    def test_message_length_boundaries_after_trimming(self):
        self.assertEqual(add_note(self.tickets, "T001", "A", "abcde")["message"], "abcde")
        self.assertEqual(len(add_note(self.tickets, "T001", "A", "x" * 300)["message"]), 300)

    def test_resolved_ticket_rejects_note_and_stays_unchanged(self):
        before = copy.deepcopy(self.tickets)
        with self.assertRaises(ValueError):
            add_note(self.tickets, "T002", "A", "should be rejected")
        self.assertEqual(self.tickets, before)

    def test_unknown_ticket_rejected_and_unchanged(self):
        before = copy.deepcopy(self.tickets)
        for bad_id in ("T999", "bogus", "T²", None):
            with self.subTest(ticket_id=bad_id):
                with self.assertRaises(ValueError):
                    add_note(self.tickets, bad_id, "A", "valid message")
                self.assertEqual(self.tickets, before)

    def test_in_progress_ticket_accepts_note(self):
        assign_ticket(self.tickets, "T001", "Ada")
        update_ticket_status(self.tickets, "T001", "in_progress")
        self.assertEqual(add_note(self.tickets, "T001", "A", "working on it")["note_id"], "N001")

    def test_full_lifecycle_from_the_brief(self):
        tickets = [make_ticket("T001")]
        add_note(tickets, "T001", "Mentor A", "Wi-Fi router reboot attempted")
        add_note(tickets, "T001", "Mentor B", "Investigating switch ports")
        assign_ticket(tickets, "T001", "Ada")
        update_ticket_status(tickets, "T001", "in_progress")
        update_ticket_status(tickets, "T001", "resolved")

        before = copy.deepcopy(tickets)
        with self.assertRaises(ValueError):
            add_note(tickets, "T001", "Mentor A", "late note")
        self.assertEqual(tickets, before)          # rejected, N003 not consumed

        reopen_ticket(tickets, "T001")
        self.assertEqual(add_note(tickets, "T001", "Mentor A", "back again")["note_id"], "N003")
        self.assertEqual([n["note_id"] for n in tickets[0]["notes"]], ["N001", "N002", "N003"])

    def test_next_note_id_uses_max_not_count(self):
        ticket = make_ticket(notes=[
            {"note_id": "N001", "author": "A", "message": "first one"},
            {"note_id": "N005", "author": "A", "message": "fifth one"},
        ])
        self.assertEqual(next_note_id(ticket), "N006")

    def test_note_ids_are_per_ticket(self):
        add_note(self.tickets, "T001", "A", "first note")
        self.assertEqual(next_note_id(self.tickets[1]), "N002")

    def test_get_notes_returns_id_order_and_copies(self):
        self.tickets[0]["notes"] = [
            {"note_id": "N010", "author": "A", "message": "tenth note"},
            {"note_id": "N002", "author": "A", "message": "second note"},
        ]
        notes = get_notes(self.tickets, "T001")
        self.assertEqual([n["note_id"] for n in notes], ["N002", "N010"])
        notes[0]["message"] = "tampered"
        self.assertEqual(self.tickets[0]["notes"][1]["message"], "second note")

    def test_resolved_ticket_notes_can_still_be_read(self):
        self.assertEqual(len(get_notes(self.tickets, "T002")), 1)


if __name__ == "__main__":
    unittest.main()