
import unittest

from campusflow.workflow import (
    assign_ticket,
    get_work_queue,
    reopen_ticket,
    update_ticket_status,
)


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


class TestTicketWorkflow(unittest.TestCase):

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

    def test_unassigned_ticket_cannot_move_to_in_progress(self):
        with self.assertRaisesRegex(ValueError, "unassigned"):
            update_ticket_status(self.tickets, "T001", "in_progress")

        self.assertEqual(self.tickets[0]["status"], "open")

    def test_assigned_ticket_progresses_open_in_progress_resolved(self):
        assign_ticket(self.tickets, "T001", "Ada")

        in_progress = update_ticket_status(self.tickets, "T001", "in_progress")
        self.assertEqual(in_progress["status"], "in_progress")

        resolved = update_ticket_status(self.tickets, "T001", "resolved")
        self.assertEqual(resolved["status"], "resolved")
        self.assertIs(resolved, self.tickets[0])

    def test_rejects_skipping_from_open_to_resolved(self):
        assign_ticket(self.tickets, "T001", "Ada")

        with self.assertRaisesRegex(ValueError, "Invalid status transition"):
            update_ticket_status(self.tickets, "T001", "resolved")

        self.assertEqual(self.tickets[0]["status"], "open")

    def test_resolved_ticket_cannot_change_status_without_reopen(self):
        assign_ticket(self.tickets, "T001", "Ada")
        update_ticket_status(self.tickets, "T001", "in_progress")
        update_ticket_status(self.tickets, "T001", "resolved")

        with self.assertRaisesRegex(ValueError, "explicit reopen"):
            update_ticket_status(self.tickets, "T001", "in_progress")

        self.assertEqual(self.tickets[0]["status"], "resolved")

    def test_reopen_sets_resolved_ticket_to_open(self):
        assign_ticket(self.tickets, "T001", "Ada")
        update_ticket_status(self.tickets, "T001", "in_progress")
        update_ticket_status(self.tickets, "T001", "resolved")

        ticket = reopen_ticket(self.tickets, "T001")

        self.assertEqual(ticket["status"], "open")
        self.assertEqual(ticket["assigned_to"], "Ada")

    def test_reopen_rejects_ticket_that_is_not_resolved(self):
        with self.assertRaisesRegex(ValueError, "Only resolved tickets"):
            reopen_ticket(self.tickets, "T001")

        self.assertEqual(self.tickets[0]["status"], "open")

    def test_assign_rejects_resolved_ticket_until_reopen(self):
        assign_ticket(self.tickets, "T001", "Ada")
        update_ticket_status(self.tickets, "T001", "in_progress")
        update_ticket_status(self.tickets, "T001", "resolved")

        with self.assertRaisesRegex(ValueError, "explicit reopen"):
            assign_ticket(self.tickets, "T001", "Ben")

        self.assertEqual(self.tickets[0]["assigned_to"], "Ada")

    def test_update_status_rejects_unknown_ticket_id(self):
        with self.assertRaisesRegex(ValueError, "Unknown ticket ID"):
            update_ticket_status(self.tickets, "T999", "in_progress")


def make_ticket(ticket_id, priority, status="open", assigned_to=None):
    return {
        "id": ticket_id,
        "title": f"Ticket {ticket_id}",
        "category": "Network",
        "urgency": "high",
        "affected_users": 1,
        "priority": priority,
        "status": status,
        "assigned_to": assigned_to,
    }


class TestWorkQueue(unittest.TestCase):

    def test_queue_sorts_by_priority_then_numeric_id(self):
        tickets = [
            make_ticket("T010", "critical"),
            make_ticket("T002", "low"),
            make_ticket("T005", "high"),
            make_ticket("T001", "critical"),
            make_ticket("T007", "medium"),
        ]

        queue = get_work_queue(tickets)
        queue_ids = [ticket["id"] for ticket in queue]

        self.assertEqual(queue_ids, ["T001", "T010", "T005", "T007", "T002"])

    def test_queue_excludes_in_progress_and_resolved_tickets(self):
        tickets = [
            make_ticket("T001", "low", status="open"),
            make_ticket("T002", "critical", status="in_progress", assigned_to="Ada"),
            make_ticket("T003", "high", status="resolved", assigned_to="Ada"),
        ]

        queue = get_work_queue(tickets)
        queue_ids = [ticket["id"] for ticket in queue]

        self.assertEqual(queue_ids, ["T001"])

    def test_queue_does_not_change_original_list_order(self):
        tickets = [
            make_ticket("T002", "low"),
            make_ticket("T001", "critical"),
        ]

        get_work_queue(tickets)

        original_ids = [ticket["id"] for ticket in tickets]
        self.assertEqual(original_ids, ["T002", "T001"])

    def test_empty_queue_when_no_open_tickets(self):
        tickets = [
            make_ticket("T001", "critical", status="resolved", assigned_to="Ada"),
        ]

        self.assertEqual(get_work_queue(tickets), [])


if __name__ == "__main__":
    unittest.main()


