from __future__ import annotations

from importlib.resources import path
from io import BytesIO
import math
import tkinter as tk
from pathlib import Path
from typing import Callable
from tkinter import Image, ttk
from ..config import SECRET_KEY
from ..services.encryption import decrypt_bytes


class ImageRevealCanvas(ttk.Frame):
    def __init__(self, master: tk.Misc, image_path: str, blocks: int = 8, on_reveal_change: Callable[[], None] | None = None, parent: tk.Misc | None = None) -> None:
        super().__init__(master)
        self.blocks = blocks
        self.parent = parent
        self.image_path = image_path
        self.on_reveal_change = on_reveal_change
        self.revealed_cells: set[tuple[int, int]] = set()
        self._base_image: tk.PhotoImage | None = None
        self._photo_image: tk.PhotoImage | None = None
        self._display_bounds = (0.0, 0.0, 0.0, 0.0)
        self._cell_width = 0.0
        self._cell_height = 0.0

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, highlightthickness=0, background="#111827")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind("<Button-1>", self._on_click)

        self.load_image(image_path)

    def load_image(self, image_path: str) -> None:
        image = decrypt_bytes(Path(image_path).read_bytes(), SECRET_KEY)
        self._base_image = tk.PhotoImage(data=image)
        self._redraw()

    def reset(self, image_path: str) -> None:
        self.load_image(image_path)
        self.revealed_cells.clear()
        self._redraw()

    def revealed_count(self) -> int:
        return len(self.revealed_cells)

    def current_points(self) -> int:
        count = self.revealed_count() - 1 + self.parent.revealedLetters.__len__()
        if count < 0:
            count = 0
        points = max(1, 10 - (2 * count))
        return points

    def reveal_all(self) -> None:
        self.revealed_cells = {(row, column) for row in range(self.blocks) for column in range(self.blocks)}
        self._redraw()

    def _on_canvas_resize(self, _: tk.Event) -> None:
        self._redraw()

    def _on_click(self, event: tk.Event) -> None:
        row, column = self._cell_at(event.x, event.y)
        if row is None or column is None:
            return

        cell = (row, column)
        if cell in self.revealed_cells:
            return

        self.revealed_cells.add(cell)
        self._redraw()
        if self.on_reveal_change is not None:
            self.on_reveal_change()

    def _cell_at(self, x: int, y: int) -> tuple[int | None, int | None]:
        left, top, right, bottom = self._display_bounds
        if not (left <= x < right and top <= y < bottom):
            return None, None

        if self._cell_width <= 0 or self._cell_height <= 0:
            return None, None

        column = min(self.blocks - 1, int((x - left) / self._cell_width))
        row = min(self.blocks - 1, int((y - top) / self._cell_height))
        return row, column

    def _redraw(self) -> None:
        self.canvas.delete("all")

        if self._base_image is None:
            return

        canvas_width = max(1, self.canvas.winfo_width())
        canvas_height = max(1, self.canvas.winfo_height())
        image_width = max(1, self._base_image.width())
        image_height = max(1, self._base_image.height())
        scale_ratio = max(image_width / canvas_width, image_height / canvas_height)
        factor = max(1, math.ceil(scale_ratio))

        if factor > 1:
            self._photo_image = self._base_image.subsample(factor, factor)
        else:
            self._photo_image = self._base_image

        render_width = self._photo_image.width()
        render_height = self._photo_image.height()

        left = (canvas_width - render_width) / 2
        top = (canvas_height - render_height) / 2
        right = left + render_width
        bottom = top + render_height
        self._display_bounds = (left, top, right, bottom)
        self._cell_width = render_width / self.blocks
        self._cell_height = render_height / self.blocks

        self.canvas.create_image(canvas_width / 2, canvas_height / 2, image=self._photo_image)

        for row in range(self.blocks):
            for column in range(self.blocks):
                if (row, column) in self.revealed_cells:
                    continue

                x1 = left + (column * self._cell_width)
                y1 = top + (row * self._cell_height)
                x2 = left + ((column + 1) * self._cell_width)
                y2 = top + ((row + 1) * self._cell_height)
                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill="#243244",
                    outline="#3f4d63",
                    width=1,
                )
