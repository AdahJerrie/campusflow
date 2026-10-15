"""CLI tests: scripted input replaces typing; stdout is captured."""
import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import main
from campusflow.question_bank import QUESTIONS
from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket
from campusflow.workflow import assign_ticket, update_ticket_status


class CliTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.data_file = Path(self.tmp.name) / "tickets.json"
        self.notes_file = Path(self.tmp.name) / "understanding_notes.txt"

    def seed(self, tickets):
        save_tickets(tickets, self.data_file)

    def run_cli(self, inputs):
        """Run main() with scripted inputs; return everything it printed."""
        output = io.StringIO()
        with mock.patch.object(main, "DATA_FILE", self.data_file), \
             mock.patch.object(main, "NOTES_FILE", self.notes_file), \
             mock.patch("builtins.input", side_effect=inputs), \
             contextlib.redirect_stdout(output):
            main.main()
        return output.getvalue()

    def two_tickets(self):
        tickets = []
        for title, category, urgency, users in (
            ("WiFi down in Lab", "Network", "high", 12),
            ("WiFi login slow", "Network", "low", 1),
        ):
            tickets.append(create_ticket(tickets, title, category, urgency, users))
        return tickets


class TestMenuChoices(CliTestCase):
    def test_invalid_menu_choices_are_rejected_politely(self):
        output = self.run_cli(["99", "abc", "", "0"])
        self.assertEqual(output.count("Invalid choice. Enter a number from 0 to 12."), 3)
        self.assertIn("Goodbye!", output)

    def test_ctrl_d_exits_cleanly_instead_of_crashing(self):
        output = self.run_cli(EOFError())
        self.assertIn("Goodbye!", output)

    def test_open_work_queue_excludes_in_progress_tickets(self):
        tickets = self.two_tickets()
        assign_ticket(tickets, "T001", "Sam")
        update_ticket_status(tickets, "T001", "in_progress")
        self.seed(tickets)

        output = self.run_cli(["7", "0"])
        self.assertIn("T002", output)
        self.assertNotIn("T001 |", output)

    def test_report_menu_shows_new_totals(self):
        self.seed(self.two_tickets())
        output = self.run_cli(["8", "0"])
        self.assertIn("Unresolved (open + in_progress): 2", output)
        self.assertIn("Resolution rate: 0.0%", output)


class TestNoteMenus(CliTestCase):
    def test_add_then_view_note_and_it_survives_reload(self):
        self.seed(self.two_tickets())
        output = self.run_cli([
            "9", "t001", "Mentor A", "Wi-Fi router reboot attempted",
            "10", "T001",
            "0",
        ])
        self.assertIn("Note N001 added to T001.", output)
        self.assertIn("N001 | Mentor A: Wi-Fi router reboot attempted", output)

        reloaded = load_tickets(self.data_file)
        self.assertEqual(reloaded[0]["notes"][0]["note_id"], "N001")

    def test_rejected_note_shows_error_and_leaves_file_unchanged(self):
        tickets = self.two_tickets()
        assign_ticket(tickets, "T001", "Sam")
        update_ticket_status(tickets, "T001", "in_progress")
        update_ticket_status(tickets, "T001", "resolved")
        self.seed(tickets)
        before = self.data_file.read_bytes()

        output = self.run_cli([
            "9", "T001", "Mentor A", "This should be refused",   # resolved ticket
            "9", "T002", "Mentor A", "tiny",                     # too short
            "9", "T002", "   ", "A perfectly fine message",      # blank author
            "9", "T999", "Mentor A", "Unknown ticket here",      # unknown ticket
            "0",
        ])
        self.assertIn("Notes can only be added to open or in_progress", output)
        self.assertEqual(output.count("Error:"), 4)
        self.assertEqual(self.data_file.read_bytes(), before)

    def test_view_notes_for_ticket_without_notes_or_unknown_ticket(self):
        self.seed(self.two_tickets())
        output = self.run_cli(["10", "T001", "10", "T404", "0"])
        self.assertIn("This ticket has no notes yet.", output)
        self.assertIn("Unknown ticket ID", output)


class TestSearchMenu(CliTestCase):
    def test_invalid_filter_reprompts_then_results_and_priority_sort(self):
        self.seed(self.two_tickets())
        before = self.data_file.read_bytes()

        output = self.run_cli([
            "11",
            "WIFI",          # title
            "plumbing",      # invalid category -> asked again
            "network",       # valid
            "",              # no status filter
            "",              # no priority filter
            "y",             # sort by priority
            "0",
        ])
        self.assertIn("Invalid input.", output)
        self.assertIn("T001 | WiFi down in Lab | Network | critical | open | Unassigned", output)
        self.assertIn("Sorted by priority, then ticket ID:", output)
        self.assertEqual(self.data_file.read_bytes(), before)  # search is read-only

    def test_search_with_no_match_says_so(self):
        self.seed(self.two_tickets())
        output = self.run_cli(["11", "printer", "", "", "", "0"])
        self.assertIn("No tickets match your search.", output)


class TestUnderstandingCheckMenu(CliTestCase):
    def test_quiz_through_the_menu_scores_and_saves_explanations(self):
        answers = [q["answer"] for q in QUESTIONS]
        output = self.run_cli(
            ["12", "Jerrie"] + answers
            + ["1", "Unassigned work has no owner yet",
               "5", "Validate everything before replacing memory"]
            + ["0"]
        )
        self.assertIn("Final score: 6 / 6", output)
        self.assertTrue(self.notes_file.exists())
        saved = self.notes_file.read_text(encoding="utf-8")
        self.assertIn("Jerrie", saved)
        self.assertIn("Validate everything before replacing memory", saved)


if __name__ == "__main__":
    unittest.main()
