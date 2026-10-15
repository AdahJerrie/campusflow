import os
import tempfile
import unittest

from campusflow.question_bank import QUESTIONS
from campusflow.understanding_check import (
    format_notes,
    normalize_answer,
    run_check,
    save_notes,
    score_answers,
)


class ScriptedInput:
    """Feeds pre-written answers to the quiz; fails loudly if it asks for more."""

    def __init__(self, answers):
        self.answers = list(answers)
        self.prompts = []

    def __call__(self, prompt=""):
        self.prompts.append(prompt)
        if not self.answers:
            raise AssertionError(f"Quiz asked for more input than scripted: {prompt!r}")
        return self.answers.pop(0)


def correct_letters():
    return [question["answer"] for question in QUESTIONS]


def wrong_letter(question):
    return next(letter for letter in "ABCD" if letter != question["answer"])


class TestQuestionBank(unittest.TestCase):
    def test_bank_has_six_well_formed_questions(self):
        self.assertEqual(len(QUESTIONS), 6)
        for question in QUESTIONS:
            with self.subTest(question=question["id"]):
                self.assertEqual(set(question["options"]), {"A", "B", "C", "D"})
                self.assertIn(question["answer"], question["options"])
                self.assertTrue(question["prompt"].strip())
                self.assertTrue(question["why"].strip())


class TestScoring(unittest.TestCase):
    def test_normalize_answer_accepts_a_to_d_in_any_case(self):
        self.assertEqual(normalize_answer(" b "), "B")
        self.assertEqual(normalize_answer("d"), "D")

    def test_normalize_answer_rejects_everything_else(self):
        for bad in ("", " ", "E", "AB", "1", "yes", None, 3):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    normalize_answer(bad)

    def test_score_is_zero_to_six(self):
        self.assertEqual(score_answers(QUESTIONS, correct_letters()), 6)
        self.assertEqual(
            score_answers(QUESTIONS, [wrong_letter(q) for q in QUESTIONS]), 0)

        answers = correct_letters()
        answers[0] = wrong_letter(QUESTIONS[0])
        answers[3] = wrong_letter(QUESTIONS[3])
        self.assertEqual(score_answers(QUESTIONS, answers), 4)

    def test_score_rejects_wrong_count_or_bad_letter(self):
        with self.assertRaises(ValueError):
            score_answers(QUESTIONS, ["A"])
        with self.assertRaises(ValueError):
            score_answers(QUESTIONS, ["A", "B", "C", "D", "A", "Z"])

    def test_scoring_uses_whatever_bank_it_is_given(self):
        bank = [
            {"id": "X1", "prompt": "p", "options": dict.fromkeys("ABCD", "o"),
             "answer": "A", "why": "w"},
            {"id": "X2", "prompt": "p", "options": dict.fromkeys("ABCD", "o"),
             "answer": "D", "why": "w"},
        ]
        self.assertEqual(score_answers(bank, ["A", "D"]), 2)
        self.assertEqual(score_answers(bank, ["A", "A"]), 1)


class TestRunCheck(unittest.TestCase):
    def run_quiz(self, script):
        output = []
        scripted = ScriptedInput(script)
        result = run_check(input_fn=scripted, output_fn=output.append)
        return result, "\n".join(output), scripted

    def test_invalid_answers_retry_and_first_valid_answer_is_scored(self):
        answers = correct_letters()
        answers[2] = wrong_letter(QUESTIONS[2])  # Q3 answered wrongly on purpose

        script = ["E", "", "9", answers[0].lower()]       # Q1: three invalid tries, then valid
        script += answers[1:]                             # Q2..Q6
        script += ["7", "x", "1", "too short",            # bad number, bad number, Q1, short text
                   "Unassigned work has no owner",
                   "1", "3",                              # duplicate Q1 rejected, then Q3
                   "AND means every filter must match"]

        result, output, scripted = self.run_quiz(script)

        self.assertEqual(result["score"], 5)
        self.assertEqual(result["total"], 6)
        self.assertEqual(result["answers"], answers)
        self.assertEqual(sorted(result["explanations"]), [1, 3])
        self.assertIn("Invalid choice", output)
        self.assertIn("Final score: 5 / 6", output)
        self.assertEqual(scripted.answers, [])  # every scripted input was used

    def test_feedback_does_not_change_the_recorded_answer(self):
        answers = [wrong_letter(q) for q in QUESTIONS]
        script = answers + ["1", "I picked this one first",
                            "2", "and this one second too"]
        result, output, _ = self.run_quiz(script)
        self.assertEqual(result["answers"], answers)
        self.assertEqual(result["score"], 0)
        self.assertIn("not quite", output)

    def test_two_explanations_are_required_and_not_auto_graded(self):
        script = correct_letters() + ["1", "a" * 10, "2", "b" * 10]
        result, output, _ = self.run_quiz(script)
        self.assertEqual(len(result["explanations"]), 2)
        # Nonsense of the right length is stored as written, not marked.
        self.assertEqual(result["explanations"][1], "a" * 10)
        self.assertNotIn("correct explanation", output.lower())


class TestNotesFile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "understanding_notes.txt")
        self.result = {
            "score": 5, "total": 6, "answers": list("BCBCCB"),
            "explanations": {1: "No owner means no work", 5: "Validate before replacing"},
        }

    def test_notes_contain_name_score_and_explanations(self):
        text = format_notes("Jerrie", self.result, timestamp="2026-10-15 10:00")
        self.assertIn("Jerrie", text)
        self.assertIn("Score: 5 / 6", text)
        self.assertIn("No owner means no work", text)
        self.assertIn("Validate before replacing", text)

    def test_saving_appends_and_never_overwrites(self):
        save_notes(self.path, "Engineer A", self.result)
        save_notes(self.path, "Jerrie", self.result)
        with open(self.path, encoding="utf-8") as file:
            text = file.read()
        self.assertIn("Engineer A", text)
        self.assertIn("Jerrie", text)


if __name__ == "__main__":
    unittest.main()
