from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable


class MainMenuFrame(ttk.Frame):
    def __init__(self, master: tk.Misc, categories: list[str], on_start: Callable[[str], None]) -> None:
        super().__init__(master, padding=24)
        self.on_start = on_start

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        container = ttk.Frame(self, padding=24)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)

        self.title_label = ttk.Label(container, text="Quiz Challenge", style="Title.TLabel")
        self.title_label.grid(row=0, column=0, pady=(0, 12))

        self.subtitle_label = ttk.Label(
            container,
            text="Pick a category and start guessing before the timer runs out.",
            wraplength=520,
            justify="center",
            style="Body.TLabel",
        )
        self.subtitle_label.grid(row=1, column=0, pady=(0, 24))

        button_frame = ttk.Frame(container)
        button_frame.grid(row=2, column=0)
        button_frame.columnconfigure(0, weight=0)

        max_button_chars = 50

        for row, category in enumerate(categories):
            label = category if len(category) <= max_button_chars else category[: max_button_chars - 3] + "..."

            button = ttk.Button(
                button_frame,
                text=label,
                command=lambda selected=category: self.on_start(selected),
                style="Menu.TButton",
                width=max_button_chars,
            )
            button.grid(row=row, column=0, pady=8, ipady=8)