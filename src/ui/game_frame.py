from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from ..config import TIMER_SECONDS
from ..models.quiz_question import QuizQuestion
from ..models.quiz_result import QuizResult
from ..models.quiz_session import QuizSession
from .image_reveal_canvas import ImageRevealCanvas


class GameFrame(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        category: str,
        questions: list[QuizQuestion],
        on_finish: Callable[[QuizResult], None],
        on_exit: Callable[[], None],
    ) -> None:
        super().__init__(master, padding=20)
        self.category = category
        self.on_finish = on_finish
        self.on_exit = on_exit
        self.session = QuizSession(questions)
        self.seconds_left = TIMER_SECONDS
        self.timer_job: str | None = None
        self.total_points = 0
        self.revealedLetters: set[str] = set()

        self.bind("<Configure>", self._on_resize)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=0)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        self.category_label = ttk.Label(header, text=f"Category: {category}", style="Heading.TLabel")
        self.category_label.grid(row=0, column=0, sticky="w")

        self.timer_label = ttk.Label(header, text=self._format_time(self.seconds_left), style="Heading.TLabel")
        self.timer_label.grid(row=0, column=1, sticky="e")

        self.progress_label = ttk.Label(self, text="", style="Body.TLabel")
        self.progress_label.grid(row=1, column=0, sticky="w", pady=(14, 8))

        self.board_container = ttk.Frame(self)
        self.board_container.grid(row=2, column=0, sticky="nsew", pady=12)
        self.board_container.columnconfigure(0, weight=1)
        self.board_container.rowconfigure(0, weight=1)

        self.points_label = ttk.Label(self, text="Current image value: 10 points", style="Heading.TLabel")
        self.points_label.grid(row=4, column=0, sticky="ew", pady=(0, 12))

        self.characters_label = ttk.Label(self, text="", style="Hint.TLabel")
        self.characters_label.grid(row=5, column=0, sticky="w", pady=(0, 12))

        initial_image = questions[0].image_path if questions else ""
        self.board = ImageRevealCanvas(self.board_container, image_path=initial_image, parent=self)
        self.board.on_reveal_change = self._update_points_label
        self.board.grid(row=0, column=0, sticky="nsew")
        self._update_points_label()

        self.instruction_label = ttk.Label(
            self,
            text="Click blocks to reveal the image, then type your guess.",
            wraplength=600,
            justify="center",
            style="Body.TLabel",
        )
        self.instruction_label.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        entry_frame = ttk.Frame(self)
        entry_frame.grid(row=6, column=0, sticky="ew", pady=(0, 12))
        entry_frame.columnconfigure(0, weight=1)

        self.answer_var = tk.StringVar()
        self.answer_entry = ttk.Entry(entry_frame, textvariable=self.answer_var, style="Game.TEntry")
        self.answer_entry.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.answer_entry.bind("<Return>", lambda _: self.submit_answer())

        submit_button = ttk.Button(entry_frame, text="Submit Answer", command=self.submit_answer, style="Game.TButton")
        submit_button.grid(row=0, column=1)

        skip_button = ttk.Button(entry_frame, text="Skip Question", command=self.skip_question, style="Game.TButton")
        skip_button.grid(row=0, column=2, padx=(12, 0))

        revealLetterButton = ttk.Button(entry_frame, text="Reveal Letter (-2 points)", command=self._reveal_letter, style="Game.TButton")
        revealLetterButton.grid(row=0, column=3, padx=(12, 0))

        self.feedback_label = ttk.Label(self, text="", wraplength=600, style="Feedback.TLabel")
        self.feedback_label.grid(row=7, column=0, pady=(8, 0))

        footer = ttk.Frame(self)
        footer.grid(row=8, column=0, sticky="ew", pady=(18, 0))
        footer.columnconfigure(0, weight=1)

        ttk.Button(footer, text="Exit to Menu", command=self._exit_to_menu, style="Menu.TButton").grid(row=0, column=0, sticky="w")

        self._begin_game()

    def _begin_game(self) -> None:
        first_question = self.session.start()
        if first_question is None:
            self._finish_game()
            return

        self._render_question(first_question)
        self.answer_entry.focus_set()
        self._schedule_tick()

    def _render_question(self, question: QuizQuestion) -> None:
        self.progress_label.config(text=f"Question {self.session.questions_seen} of {len(self.session.questions)}")
        self.board.reset(question.image_path)
        self._update_points_label()
        self._update_characters_label(question.answer)
        self.answer_var.set("")
        self.feedback_label.config(text="")
        self.revealedLetters.clear()

    def _current_question_points(self) -> int:
        return self.board.current_points()

    def _reveal_letter(self) -> None:
        allLetters = set(self.session.current_question.answer.replace(" ", ""))
        unrevealedLetters = allLetters - self.revealedLetters
        if self.revealedLetters.__len__() > allLetters.__len__()//2:
            self.feedback_label.config(text="You have revealed too many letters already.")
            return
        letter = unrevealedLetters.pop()
        self.revealedLetters.add(letter)
        self._update_characters_label(self.session.current_question.answer)
        self._update_points_label()

    def _update_points_label(self) -> None:
        self.points_label.config(text=f"Current image value: {self.board.current_points()} points")

    def _update_characters_label(self, answer: str) -> None:
        text_ = ""
        if answer:
            for char in answer:
                if char not in self.revealedLetters:
                    text_ += "_ " if char != " " else "  "
                else:
                    text_ += char
        self.characters_label.config(text=text_)

    def submit_answer(self) -> None:
        user_guess = self.answer_var.get().strip()
        if not user_guess:
            self.feedback_label.config(text="Type an answer first.")
            return

        correct, next_question = self.session.submit_answer(user_guess)
        if not correct:
            self.feedback_label.config(text="Not quite. Try again.")
            self.answer_entry.focus_set()
            return

        points_earned = self._current_question_points()
        self.total_points += points_earned

        if next_question is None:
            self.feedback_label.config(text=f"Correct! You earned {points_earned} points.")
            self._finish_game()
            return

        self.feedback_label.config(text=f"Correct! You earned {points_earned} points. Next image coming up.")
        self._render_question(next_question)
        self.answer_entry.focus_set()

    def skip_question(self) -> None:
        next_question = self.session.skip_question()

        if next_question is None:
            self.feedback_label.config(text="Question skipped.")
            self._finish_game()
            return

        self.feedback_label.config(text="Question skipped.")
        self._render_question(next_question)
        self.answer_entry.focus_set()

    def _schedule_tick(self) -> None:
        self._cancel_tick()
        self.timer_job = self.after(1000, self._tick)

    def _tick(self) -> None:
        self.seconds_left -= 1
        self.timer_label.config(text=self._format_time(self.seconds_left))

        if self.seconds_left <= 0:
            self._finish_game()
            return

        self._schedule_tick()

    def _finish_game(self) -> None:
        self._cancel_tick()
        self.answer_entry.config(state="disabled")
        result = QuizResult(
            category=self.category,
            correct_answers=self.session.correct_answers,
            questions_seen=self.session.questions_seen,
            total_points=self.total_points,
            time_left=max(0, self.seconds_left),
        )
        self.on_finish(result)

    def _exit_to_menu(self) -> None:
        self._cancel_tick()
        self.on_exit()

    def _cancel_tick(self) -> None:
        if self.timer_job is not None:
            self.after_cancel(self.timer_job)
            self.timer_job = None

    @staticmethod
    def _format_time(seconds: int) -> str:
        minutes, remaining_seconds = divmod(max(0, seconds), 60)
        return f"Time Left: {minutes:02d}:{remaining_seconds:02d}"

    def _on_resize(self, event: tk.Event) -> None:
        wraplength = max(380, int(event.width) - 100)
        self.instruction_label.configure(wraplength=wraplength)
        self.feedback_label.configure(wraplength=wraplength)
        self.points_label.configure(wraplength=wraplength)
