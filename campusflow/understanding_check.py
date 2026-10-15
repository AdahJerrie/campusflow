"""Engineering Understanding Check: scoring and quiz flow.

The questions live in question_bank.py. This module never contains a question
or an answer key of its own. input and output are passed in as functions so
tests can feed scripted answers instead of typing.
"""
from datetime import datetime

from campusflow.question_bank import QUESTIONS

VALID_LETTERS = ("A", "B", "C", "D")
EXPLANATIONS_REQUIRED = 2
MIN_EXPLANATION_LENGTH = 10


def normalize_answer(text):
    """Return 'A', 'B', 'C' or 'D' for input like ' b '. Anything else: ValueError."""
    if not isinstance(text, str):
        raise ValueError("Answer must be A, B, C, or D.")
    letter = text.strip().upper()
    if letter not in VALID_LETTERS:
        raise ValueError("Answer must be A, B, C, or D.")
    return letter


def score_answers(questions, answers):
    """One point per correct answer. Pure: no printing, no input.

    answers is a list of submitted letters, one per question, in order.
    Raises ValueError if the counts differ or a letter is not A-D.
    """
    if len(answers) != len(questions):
        raise ValueError("Need exactly one answer per question.")
    score = 0
    for question, answer in zip(questions, answers):
        if normalize_answer(answer) == question["answer"]:
            score += 1
    return score


def _show_question(question, number, total, output_fn):
    output_fn(f"\nQuestion {number} of {total}")
    output_fn(question["prompt"])
    for letter in VALID_LETTERS:
        output_fn(f"  {letter}. {question['options'][letter]}")


def _ask_letter(input_fn, output_fn):
    """Keep asking until the learner types A, B, C or D."""
    while True:
        try:
            return normalize_answer(input_fn("Your answer (A/B/C/D): "))
        except ValueError as error:
            output_fn(f"Invalid choice. {error}")


def _ask_explanations(questions, answers, input_fn, output_fn):
    """Ask for short written explanations of TWO answers (the learner picks which).

    The explanations are stored as written. They are never marked right or
    wrong by the program: a mentor discusses them.
    """
    total = len(questions)
    explanations = {}
    output_fn(
        f"\nNow explain {EXPLANATIONS_REQUIRED} of your answers in your own words."
    )
    while len(explanations) < EXPLANATIONS_REQUIRED:
        position = len(explanations) + 1
        raw = input_fn(
            f"Choose a question number 1-{total} to explain "
            f"({position} of {EXPLANATIONS_REQUIRED}): "
        ).strip()
        if not raw.isascii() or not raw.isdigit() or not 1 <= int(raw) <= total:
            output_fn(f"Please enter a number from 1 to {total}.")
            continue
        number = int(raw)
        if number in explanations:
            output_fn("You already explained that one. Pick a different question.")
            continue

        output_fn(
            f"Q{number}: you answered {answers[number - 1]}. "
            f"Why is that correct? Use an example from the code."
        )
        while True:
            text = input_fn(
                f"Your explanation (at least {MIN_EXPLANATION_LENGTH} characters): "
            ).strip()
            if len(text) >= MIN_EXPLANATION_LENGTH:
                break
            output_fn("That is too short. Write a little more.")
        explanations[number] = text
    return explanations


def run_check(questions=None, input_fn=None, output_fn=None):
    """Run the quiz and return {'score', 'total', 'answers', 'explanations'}.

    The FIRST valid answer to each question is the one that is scored.
    Feedback is shown after the answer is recorded and cannot change it.
    """
    if questions is None:
        questions = QUESTIONS
    if input_fn is None:
        input_fn = input   # looked up now, so tests can patch builtins.input
    if output_fn is None:
        output_fn = print

    total = len(questions)
    answers = []
    for number, question in enumerate(questions, start=1):
        _show_question(question, number, total, output_fn)
        letter = _ask_letter(input_fn, output_fn)
        answers.append(letter)  # recorded before any feedback

        if letter == question["answer"]:
            output_fn("Recorded: correct.")
        else:
            output_fn(f"Recorded: not quite. The correct answer is {question['answer']}.")
        output_fn(f"Why: {question['why']}")

    score = score_answers(questions, answers)
    output_fn(f"\nFinal score: {score} / {total}")

    explanations = _ask_explanations(questions, answers, input_fn, output_fn)
    return {
        "score": score,
        "total": total,
        "answers": answers,
        "explanations": explanations,
    }


def format_notes(name, result, questions=None, timestamp=None):
    """Build the text saved to the learning note. Pure: returns a string."""
    if questions is None:
        questions = QUESTIONS
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"Engineering Understanding Check | {name} | {timestamp}",
        f"Score: {result['score']} / {result['total']}",
        f"Answers: {' '.join(result['answers'])}",
    ]
    for number in sorted(result["explanations"]):
        question = questions[number - 1]
        lines.append(f"Q{number} ({question['id']}): {question['prompt']}")
        lines.append(f"  Answered: {result['answers'][number - 1]}")
        lines.append(f"  Explanation: {result['explanations'][number]}")
    lines.append("-" * 60)
    return "\n".join(lines) + "\n"


def save_notes(path, name, result, questions=None, timestamp=None):
    """Append one learner's explanations to the notes file (never overwrites)."""
    text = format_notes(name, result, questions, timestamp)
    with open(path, "a", encoding="utf-8") as file:
        file.write(text)
