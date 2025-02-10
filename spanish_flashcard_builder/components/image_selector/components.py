"""UI components for the image selector."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List

from PIL import Image, ImageTk

from .constants import (
    BODY_FONT,
    GRID_COLUMNS,
    ITALIC_FONT,
    PADDING,
    PREVIEW_SIZE,
    SUBTITLE_FONT,
    TITLE_FONT,
)


class ScrollableFrame:
    """A scrollable frame container with mouse wheel support."""

    def __init__(self, parent: tk.Widget):
        self.canvas: tk.Canvas = tk.Canvas(parent)
        self.scrollbar: ttk.Scrollbar = ttk.Scrollbar(
            parent, orient="vertical", command=self.canvas.yview
        )
        self.frame: ttk.Frame = ttk.Frame(self.canvas)

        self.frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        scroll_direction = 1 if (event.num == 5 or event.delta < 0) else -1
        self.canvas.yview_scroll(scroll_direction, "units")

    def pack(self, **kwargs):
        self.canvas.pack(side="left", fill="both", expand=True, padx=PADDING)
        self.scrollbar.pack(side="right", fill="y")


class TermInfoPanel:
    """Panel displaying term information including definition and example sentences."""

    def __init__(self, parent: ttk.Frame, term_data: Dict):
        self.frame: ttk.Frame = ttk.Frame(parent, padding="10")
        self.term_data: Dict = term_data
        self._create_widgets()

    def _create_widgets(self):
        ttk.Label(
            self.frame,
            text=f"Term: {self.term_data.get('display_form', '')}",
            font=TITLE_FONT,
        ).pack(anchor="w")

        ttk.Label(
            self.frame,
            text=f"Definition: {self.term_data.get('definitions', '')}",
            font=SUBTITLE_FONT,
        ).pack(anchor="w")

        ttk.Label(
            self.frame,
            text=f"Search Query: {self.term_data.get('image_search_query', '')}",
            font=BODY_FONT,
        ).pack(anchor="w")

        if "example_sentences" in self.term_data:
            self._add_example_sentences()

    def _add_example_sentences(self):
        ttk.Label(self.frame, text="\nExample Sentences:", font=SUBTITLE_FONT).pack(
            anchor="w"
        )

        for i, example in enumerate(self.term_data["example_sentences"], 1):
            ttk.Label(
                self.frame, text=f"{i}. {example.get('es', '')}", font=BODY_FONT
            ).pack(anchor="w")

            ttk.Label(
                self.frame, text=f"   {example.get('en', '')}", font=ITALIC_FONT
            ).pack(anchor="w", padx=(20, 0))

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)


class ImageGrid:
    """Grid display of selectable images with keyboard shortcuts (1-9, 0)."""

    def __init__(self, parent: ttk.Frame, on_select: Callable[[int], None]):
        self.frame: ttk.Frame = ttk.Frame(parent)
        self.on_select: Callable[[int], None] = on_select
        self.image_refs: List[ImageTk.PhotoImage] = []  # Prevent garbage collection

    def display_images(self, loaded_images: List[tuple[int, Image.Image]]) -> None:
        for grid_idx, (image_idx, image) in enumerate(loaded_images):
            frame = ttk.Frame(self.frame)
            row = (grid_idx // GRID_COLUMNS) + 1
            col = grid_idx % GRID_COLUMNS
            frame.grid(row=row, column=col, padx=10, pady=10)

            display_number = "0" if image_idx == 9 else str(image_idx + 1)
            number_label = ttk.Label(frame, text=display_number, font=BODY_FONT)
            number_label.pack()

            preview_image = image.copy()
            preview_image.thumbnail(PREVIEW_SIZE, Image.Resampling.LANCZOS)
            photo_image = ImageTk.PhotoImage(preview_image)
            self.image_refs.append(photo_image)

            img_label = ttk.Label(frame, image=photo_image)
            img_label.pack()

            for widget in (frame, number_label, img_label):
                widget.bind("<Button-1>", lambda e, idx=image_idx: self.on_select(idx))

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)
