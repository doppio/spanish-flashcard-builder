"""GUI component for image selection."""

import logging
import tkinter
import tkinter as tk
from io import BytesIO
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast

import requests
from PIL import Image, ImageTk

from .google_search import ImageResult

# Type aliases
FontConfig = Union[Tuple[str, int], Tuple[str, int, str]]
ImageSize = Tuple[int, int]

# UI Constants
PREVIEW_SIZE: ImageSize = (300, 300)
GRID_COLUMNS: int = 5
PADDING: int = 20
HEADER_HEIGHT: int = 250

TITLE_FONT: FontConfig = ("Arial", 18, "bold")
SUBTITLE_FONT: FontConfig = ("Arial", 16)
BODY_FONT: FontConfig = ("Arial", 14)
ITALIC_FONT: FontConfig = ("Arial", 14, "italic")

INSTRUCTIONS: str = (
    "Click an image or press its number key to select\n"
    "Press 'n' if no image is suitable, or 'q' to quit"
)
PROCESSING_MSG: str = "Saving image {} for '{}'..."
NO_IMAGES_MSG: str = "No suitable image found, skipping."
QUIT_MSG: str = "Quitting image selection."


class ScrollableFrame:
    """A scrollable frame container with mouse wheel support."""

    def __init__(self, parent: tk.Widget) -> None:
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

    def _on_mousewheel(self, event: tk.Event) -> None:
        scroll_direction = 1 if (event.num == 5 or event.delta < 0) else -1
        self.canvas.yview_scroll(scroll_direction, "units")

    def pack(self, **kwargs: Any) -> None:
        self.canvas.pack(side="left", fill="both", expand=True, padx=PADDING)
        self.scrollbar.pack(side="right", fill="y")


class TermInfoPanel:
    """Panel displaying term information including definition and example sentences."""

    def __init__(self, parent: ttk.Frame, term_data: Dict[str, Any]) -> None:
        self.frame: ttk.Frame = ttk.Frame(parent, padding="10")
        self.term_data: Dict[str, Any] = term_data
        self._create_widgets()

    def _create_widgets(self) -> None:
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

    def _add_example_sentences(self) -> None:
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

    def grid(self, **kwargs: Any) -> None:
        self.frame.grid(**kwargs)


class ImageGrid:
    """Grid display of selectable images with keyboard shortcuts (1-9, 0)."""

    def __init__(self, parent: ttk.Frame, on_select: Callable[[int], None]) -> None:
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

            def click_handler(e: tk.Event, idx: int = image_idx) -> None:
                return self.on_select(idx)

            for widget in (frame, number_label, img_label):
                widget.bind("<Button-1>", click_handler)

    def grid(self, **kwargs: Any) -> None:
        self.frame.grid(**kwargs)


class ImageSelectorGUI:
    """GUI window for selecting images."""

    def __init__(self, results: List[ImageResult], term_data: Dict[str, Any]) -> None:
        """Initialize the GUI with search results and term data."""
        self.results = results
        self.term_data = term_data
        self.selection: Optional[int] = None
        self.full_images: Dict[int, Image.Image] = {}

        # Create and configure the main window
        self.root = tk.Tk()
        self._setup_window()
        self._create_layout()
        self._load_and_display_images()

    def _setup_window(self) -> None:
        """Configure the main window properties."""
        self.root.title("Flashcard Image Selector")

        # Calculate window dimensions
        window_width = PADDING * 2 + GRID_COLUMNS * (PREVIEW_SIZE[0] + PADDING * 2)
        window_height = (
            PADDING * 2 + HEADER_HEIGHT + 2 * (PREVIEW_SIZE[1] + PADDING * 2)
        )
        self.root.geometry(f"{window_width}x{window_height}")

        # Add keyboard shortcuts
        self.root.bind("<Key>", self._handle_key)

    def _create_layout(self) -> None:
        """Create and arrange the GUI components."""
        # Add instructions
        ttk.Label(self.root, text=INSTRUCTIONS, padding=10, font=BODY_FONT).pack()

        # Create scrollable content area
        self.scroll_container = ScrollableFrame(cast(tk.Widget, self.root))
        self.scroll_container.pack()

        # Add term information
        self.term_info = TermInfoPanel(self.scroll_container.frame, self.term_data)
        self.term_info.grid(
            row=0, column=0, columnspan=GRID_COLUMNS, sticky="ew", padx=15, pady=(0, 15)
        )

        # Add image grid
        self.image_grid = ImageGrid(self.scroll_container.frame, self._handle_selection)
        self.image_grid.grid(row=1, column=0, columnspan=GRID_COLUMNS)

    def _load_and_display_images(self) -> None:
        """Load and display the images."""
        loaded_images: List[Tuple[int, Image.Image]] = []
        for idx, result in enumerate(self.results):
            try:
                response = requests.get(result.full_url, stream=True, timeout=10)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content))
                self.full_images[idx] = img
                loaded_images.append((idx, img))
            except Exception as e:
                logging.error(f"Failed to load image {idx}: {e}")

        # Sort images by index and display in main thread
        loaded_images.sort(key=lambda x: x[0])
        self.image_grid.display_images(loaded_images)

    def _show_processing_message(self, index: int) -> None:
        """Show the processing message after selection."""
        term = self.term_data.get("display_form", "term")

        # Clear existing content
        for widget in self.root.winfo_children():
            widget.destroy()

        # Show processing message
        container = ttk.Frame(self.root)
        container.pack(expand=True, fill="both")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        ttk.Label(
            container,
            text=PROCESSING_MSG.format(index + 1, term),
            font=BODY_FONT,
            padding=20,
        ).grid(row=0, column=0)

        self.root.update()
        logging.info(f"Selected image {index + 1} for '{term}', processing...")

    def _handle_selection(self, index: int) -> None:
        """Handle image selection."""
        if 0 <= index < len(self.results) and index in self.full_images:
            self.selection = index
            self._show_processing_message(index)
            self.root.quit()

    def _handle_key(self, event: tk.Event) -> None:
        """Handle keyboard input."""
        if event.char == "q":
            logging.info(QUIT_MSG)
            self.selection = None
            self.root.quit()
        elif event.char == "n":
            logging.info(NO_IMAGES_MSG)
            self.selection = -1
            self.root.quit()
        elif event.char in "0123456789":
            selection = 0 if event.char == "0" else int(event.char)
            if 1 <= selection <= len(self.results):
                self._handle_selection(selection - 1)

    def run(self) -> Optional[int]:
        """Run the GUI and return the selected index."""
        try:
            self.root.mainloop()
        except Exception as e:
            logging.error(f"Error in GUI: {e}")
            self.selection = None
        finally:
            try:
                if self.root and self.root.winfo_exists():
                    self.root.destroy()
            except tkinter.TclError:
                pass
        return self.selection
