from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class QuizQuestion:
    image_path: str
    answer: str
