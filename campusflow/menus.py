"""Interactive menu screens for notes, search and the understanding check.

Every function takes input_fn and output_fn (defaulting to input and print) so
tests can pass scripted answers. The business rules stay in notes.py,
search.py, queue.py and understanding_check.py; this module only asks, calls
them, and prints friendly messages.
"""
from campusflow.notes import add_note, get_notes
from campusflow.queue import sort_by_priority
from campusflow.search import (
    search_tickets,
    normalize_category_filter,
    normalize_status_filter,
    normalize_priority_filter,
)
from campusflow.understanding_check import run_check, save_notes


def _io(input_fn, output_fn):
    """Resolve input/print when a screen runs (not when it is defined).

    A default of `input_fn=input` would capture the real input() at import
    time, so tests that patch builtins.input could not replace it.
    """
    return (input if input_fn is None else input_fn,
            print if output_fn is None else output_fn)


# ---------- notes ----------

def add_note_menu(tickets, save_fn, input_fn=None, output_fn=None):
    """Ask for a ticket, author and message, then call notes.add_note.

    Returns the new note, or None if it was rejected. A rejected note changes
    nothing. If saving to disk fails, the note is removed from memory again so
    memory and file agree.
    """
    input_fn, output_fn = _io(input_fn, output_fn)
    ticket_id = input_fn("Ticket ID: ")
    author = input_fn("Author: ")
    message = input_fn("Note message (5-300 characters): ")

    try:
        note = add_note(tickets, ticket_id, author, message)
    except ValueError as error:
        output_fn(f"Error: {error}")
        return None

    try:
        save_fn(tickets)
    except OSError:
        for ticket in tickets:
            ticket["notes"][:] = [n for n in ticket["notes"] if n is not note]
        raise

    output_fn(f"Note {note['note_id']} added to {ticket_id.strip().upper()}.")
    return note


def view_notes_menu(tickets, input_fn=None, output_fn=None):
    """Show every note on a ticket in note-ID order. Read-only."""
    input_fn, output_fn = _io(input_fn, output_fn)
    ticket_id = input_fn("Ticket ID: ")
    try:
        notes = get_notes(tickets, ticket_id)
    except ValueError as error:
        output_fn(f"Error: {error}")
        return None

    if not notes:
        output_fn("This ticket has no notes yet.")
        return notes

    for note in notes:
        output_fn(f"{note['note_id']} | {note['author']}: {note['message']}")
    return notes


# ---------- search ----------

def display_search_results(results, output_fn=print):
    if not results:
        output_fn("No tickets match your search.")
        return

    output_fn("ID | Title | Category | Priority | Status | Assigned to")
    for ticket in results:
        assigned = ticket.get("assigned_to") or "Unassigned"
        output_fn(
            f"{ticket['id']} | {ticket['title']} | {ticket['category']} | "
            f"{ticket['priority']} | {ticket['status']} | {assigned}"
        )


def _prompt_filter(prompt, normalizer, input_fn, output_fn):
    """Re-ask until the filter is blank (no filter) or valid."""
    while True:
        try:
            return normalizer(input_fn(prompt))
        except ValueError as error:
            output_fn(f"Invalid input. {error}")


def _ask_yes_no(prompt, input_fn, output_fn):
    while True:
        answer = input_fn(prompt).strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("", "n", "no"):
            return False
        output_fn("Please answer y or n.")


def search_menu(tickets, input_fn=None, output_fn=None):
    """Search by title text plus optional category, status and priority filters.

    Read-only. Leave a prompt blank to skip that filter. Returns the results
    that were shown.
    """
    input_fn, output_fn = _io(input_fn, output_fn)
    title = input_fn("Title contains (blank for any): ")
    category = _prompt_filter(
        "Category (Network/Hardware/Software/Other, blank for any): ",
        normalize_category_filter, input_fn, output_fn,
    )
    status = _prompt_filter(
        "Status (open/in_progress/resolved, blank for any): ",
        normalize_status_filter, input_fn, output_fn,
    )
    priority = _prompt_filter(
        "Priority (critical/high/medium/low, blank for any): ",
        normalize_priority_filter, input_fn, output_fn,
    )

    results = search_tickets(tickets, title, category, status, priority)
    display_search_results(results, output_fn)

    if len(results) > 1 and _ask_yes_no(
        "Sort these results by priority, then ticket ID? (y/N): ",
        input_fn, output_fn,
    ):
        results = sort_by_priority(results)
        output_fn("Sorted by priority, then ticket ID:")
        display_search_results(results, output_fn)
    return results


# ---------- understanding check ----------

def understanding_check_menu(notes_path, input_fn=None, output_fn=None):
    """Take the quiz, show the explanations, and append them to the notes file."""
    input_fn, output_fn = _io(input_fn, output_fn)
    name = ""
    while not name:
        name = input_fn("Your name: ").strip()
        if not name:
            output_fn("Name cannot be blank.")

    result = run_check(input_fn=input_fn, output_fn=output_fn)

    output_fn("\nYour explanations (for mentor discussion):")
    for number in sorted(result["explanations"]):
        output_fn(f"  Q{number} ({result['answers'][number - 1]}): "
                  f"{result['explanations'][number]}")

    try:
        save_notes(notes_path, name, result)
        output_fn(f"Saved to {notes_path}.")
    except OSError as error:
        output_fn(f"Could not save the notes file: {error}")
    return result
