from __future__ import annotations

import json
from pathlib import Path

from ..config import CATEGORY_FILES, DATA_DIR, SECRET_KEY
from ..models.quiz_question import QuizQuestion
from .encryption import decrypt_text


class QuizRepository:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or DATA_DIR

    def available_categories(self) -> list[str]:
        return list(CATEGORY_FILES.keys())

    def load_questions(self, category: str) -> list[QuizQuestion]:
        if category not in CATEGORY_FILES:
            raise ValueError(f"Unknown category: {category}")

        file_path = self.data_dir / CATEGORY_FILES[category]
        with file_path.open("r", encoding="utf-8") as file_handle:
            raw_items = json.load(file_handle)

        questions: list[QuizQuestion] = []
        for item in raw_items:
            image_path = self.data_dir / item["image_path"]
            questions.append(
                QuizQuestion(
                    image_path=str(image_path.resolve()),
                    answer=decrypt_text(item["answer"], SECRET_KEY),
                )
            )
        return questions
