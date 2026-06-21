from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class QuizResult:
    category: str
    correct_answers: int
    questions_seen: int
    total_points: int
    time_left: int
