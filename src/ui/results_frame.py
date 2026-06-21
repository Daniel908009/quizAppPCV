from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from ..models.quiz_result import QuizResult


class ResultsFrame(ttk.Frame):
    def __init__(self, master: tk.Misc, result: QuizResult, on_play_again: Callable[[], None], on_main_menu: Callable[[], None]) -> None:
        super().__init__(master, padding=24)
        self.on_play_again = on_play_again
        self.on_main_menu = on_main_menu

        self.bind("<Configure>", self._on_resize)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        container = ttk.Frame(self, padding=24)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        self.title_label = ttk.Label(container, text="Game Over", style="Title.TLabel")
        self.title_label.grid(row=0, column=0, pady=(0, 16))

        self.summary_label = ttk.Label(
            container,
            text=self._build_summary(result),
            justify="center",
            wraplength=520,
            style="Body.TLabel",
        )
        self.summary_label.grid(row=1, column=0, pady=(0, 24))

        button_row = ttk.Frame(container)
        button_row.grid(row=2, column=0, pady=6)

        ttk.Button(button_row, text="Play Again", command=self.on_play_again, style="Menu.TButton").grid(row=0, column=0, padx=(0, 10), ipadx=10, ipady=6)
        ttk.Button(button_row, text="Main Menu", command=self.on_main_menu, style="Menu.TButton").grid(row=0, column=1, ipadx=10, ipady=6)

    @staticmethod
    def _build_summary(result: QuizResult) -> str:
        return (
            f"Category: {result.category}\n\n"
            f"You guessed {result.correct_answers} out of {result.questions_seen} questions correctly.\n"
            f"You earned {result.total_points} points.\n"
            f"Time remaining: {result.time_left:02d} seconds"
        )

    def _on_resize(self, event: tk.Event) -> None:
        wraplength = max(360, int(event.width) - 120)
        self.summary_label.configure(wraplength=wraplength)
