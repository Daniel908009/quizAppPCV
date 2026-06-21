from __future__ import annotations

import re
from dataclasses import dataclass

from .quiz_question import QuizQuestion


@dataclass
class QuizSession:
    questions: list[QuizQuestion]
    current_index: int = 0
    correct_answers: int = 0
    questions_seen: int = 0

    def start(self) -> QuizQuestion | None:
        if not self.questions:
            return None
        self.current_index = 0
        self.correct_answers = 0
        self.questions_seen = 1
        return self.current_question

    @property
    def current_question(self) -> QuizQuestion | None:
        if 0 <= self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    @property
    def finished(self) -> bool:
        return self.current_index >= len(self.questions)

    def submit_answer(self, guess: str) -> tuple[bool, QuizQuestion | None]:
        question = self.current_question
        if question is None:
            return False, None

        if self._normalize(guess) != self._normalize(question.answer):
            return False, question

        self.correct_answers += 1
        self.current_index += 1

        if self.current_index < len(self.questions):
            self.questions_seen += 1
            return True, self.current_question

        return True, None

    def skip_question(self) -> QuizQuestion | None:
        question = self.current_question
        if question is None:
            return None

        self.current_index += 1
        if self.current_index < len(self.questions):
            self.questions_seen += 1
            return self.current_question

        return None

    @staticmethod
    def _normalize(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", value.lower().strip())
