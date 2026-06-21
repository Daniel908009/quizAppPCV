from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from ..config import APP_TITLE
from ..models.quiz_result import QuizResult
from ..services.quiz_repository import QuizRepository
from .game_frame import GameFrame
from .main_menu_frame import MainMenuFrame
from .results_frame import ResultsFrame


class QuizApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.style = ttk.Style(self.root)
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        self.title_font = tkfont.Font(root=self.root, family="TkDefaultFont", size=24, weight="bold")
        self.heading_font = tkfont.Font(root=self.root, family="TkDefaultFont", size=16, weight="bold")
        self.body_font = tkfont.Font(root=self.root, family="TkDefaultFont", size=14)
        self.hint_font = tkfont.Font(root=self.root, family="TkDefaultFont", size=13, slant="italic")
        self.button_font = tkfont.Font(root=self.root, family="TkDefaultFont", size=12)
        self.entry_font = tkfont.Font(root=self.root, family="TkDefaultFont", size=13)

        self.style.configure("Title.TLabel", font=self.title_font)
        self.style.configure("Heading.TLabel", font=self.heading_font)
        self.style.configure("Body.TLabel", font=self.body_font)
        self.style.configure("Hint.TLabel", font=self.hint_font)
        self.style.configure("Feedback.TLabel", font=self.body_font)
        self.style.configure("Menu.TButton", font=self.button_font, padding=(14, 8))
        self.style.configure("Game.TButton", font=self.button_font, padding=(12, 8))
        self.style.configure("Game.TEntry", font=self.entry_font, padding=8)

        self._base_width = 720
        self._base_height = 480

        self.repository = QuizRepository()
        self.current_frame: ttk.Frame | None = None
        self.show_main_menu()

    def run(self) -> None:
        self.root.mainloop()

    def _swap_frame(self, frame: ttk.Frame) -> None:
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def show_main_menu(self) -> None:
        frame = MainMenuFrame(self.root, self.repository.available_categories(), self.start_game)
        self._swap_frame(frame)

    def start_game(self, category: str) -> None:
        questions = self.repository.load_questions(category)
        frame = GameFrame(self.root, category, questions, self.show_results, self.show_main_menu)
        self._swap_frame(frame)

    def show_results(self, result: QuizResult) -> None:
        frame = ResultsFrame(
            self.root,
            result,
            lambda: self.start_game(result.category),
            self.show_main_menu,
        )
        self._swap_frame(frame)