"""GUI component for image selection."""

import concurrent.futures
import logging
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast

from PIL import Image, ImageTk

# Type aliases
FontConfig = Union[Tuple[str, int], Tuple[str, int, str]]
ImageSize = Tuple[int, int]
OnSearchCallback = Callable[[str], None]
OnSelectCallback = Callable[[int, Optional[Image.Image]], None]

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

    def __init__(
        self,
        parent: ttk.Frame,
        term_data: Dict[str, Any],
        on_search: OnSearchCallback,
    ) -> None:
        self.frame: ttk.Frame = ttk.Frame(parent, padding="10")
        self.term_data: Dict[str, Any] = term_data
        self.on_search: OnSearchCallback = on_search
        self._create_widgets()

    def _create_widgets(self) -> None:
        ttk.Label(
            self.frame,
            text=f"Term: {self.term_data['term']}",
            font=TITLE_FONT,
        ).pack(anchor="w")

        ttk.Label(
            self.frame,
            text=f"Definition: {self.term_data.get('definitions', '')}",
            font=SUBTITLE_FONT,
        ).pack(anchor="w")

        self.query_panel = QueryPanel(
            self.frame,
            initial_query=self.term_data["image_search_query"],
            on_search=self.on_search,
        )
        self.query_panel.pack(anchor="w", pady=10)

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


class QueryPanel:
    """Panel for entering and submitting a search query."""

    def __init__(
        self,
        parent: ttk.Frame,
        initial_query: str,
        on_search: OnSearchCallback,
    ) -> None:
        self.frame: ttk.Frame = ttk.Frame(parent)
        self.query_var = tk.StringVar(value=initial_query)
        self.on_search = on_search
        self._create_widgets()

    def _create_widgets(self) -> None:
        query_label = ttk.Label(self.frame, text="Search Query:", font=BODY_FONT)
        query_label.pack(side=tk.LEFT, padx=5)

        self.query_entry = ttk.Entry(
            self.frame, textvariable=self.query_var, font=BODY_FONT
        )
        self.query_entry.pack(side=tk.LEFT, padx=5)
        self.query_entry.bind("<Return>", self._handle_input)

        search_button = ttk.Button(
            self.frame, text="Search", command=self._handle_input
        )
        search_button.pack(side=tk.LEFT, padx=5)

    def _handle_input(self, event: Optional[tk.Event] = None) -> None:
        self.on_search(self.query_var.get())

    def pack(self, **kwargs: Any) -> None:
        self.frame.pack(**kwargs)

    def get_query(self) -> str:
        return self.query_var.get()


class ImageGrid:
    """Grid display of selectable images with keyboard shortcuts (1-9, 0)."""

    def __init__(self, parent: ttk.Frame, on_select: OnSelectCallback) -> None:
        self.frame: ttk.Frame = ttk.Frame(parent)
        self.on_select: OnSelectCallback = on_select
        self.image_refs: List[ImageTk.PhotoImage] = []  # Prevent garbage collection
        self.loading_labels: Dict[int, ttk.Label] = {}  # Track loading indicators
        self.image_labels: Dict[int, ttk.Label] = {}  # Track image labels
        self.futures: List[concurrent.futures.Future[Optional[Image.Image]]] = []

    def display_futures(
        self, futures: List[concurrent.futures.Future[Optional[Image.Image]]]
    ) -> None:
        """Display loading states and set up future callbacks."""
        self.futures = futures
        self.image_refs.clear()

        # Clear existing grid
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.loading_labels.clear()
        self.image_labels.clear()

        # Create grid slots for each future
        for idx, future in enumerate(futures):
            frame = ttk.Frame(self.frame)
            row = (idx // GRID_COLUMNS) + 1
            col = idx % GRID_COLUMNS
            frame.grid(row=row, column=col, padx=10, pady=10)

            # Add number label
            display_number = "0" if idx == 9 else str(idx + 1)
            number_label = ttk.Label(frame, text=display_number, font=BODY_FONT)
            number_label.pack()

            # Add loading indicator
            loading_label = ttk.Label(frame, text="Loading...", font=ITALIC_FONT)
            loading_label.pack()
            self.loading_labels[idx] = loading_label

            # Create empty image label
            img_label = ttk.Label(frame)
            img_label.pack()
            self.image_labels[idx] = img_label

            # Set up callback for when future completes
            def make_callback(
                index: int,
            ) -> Callable[[concurrent.futures.Future[Optional[Image.Image]]], None]:
                return lambda f: self._handle_loaded_image(f, index)

            future.add_done_callback(make_callback(idx))

            def click_handler(
                e: tk.Event,
                index: int = idx,
                bound_future: concurrent.futures.Future[Optional[Image.Image]] = future,
            ) -> None:
                if bound_future.done():
                    self.on_select(index, bound_future.result())
                    e.widget.winfo_toplevel().quit()

            for widget in (frame, number_label, img_label):
                widget.bind("<Button-1>", click_handler)

    def _handle_loaded_image(
        self, future: concurrent.futures.Future[Optional[Image.Image]], idx: int
    ) -> None:
        """Handle a completed image load."""
        try:
            if img := future.result():
                # Remove loading indicator
                if loading_label := self.loading_labels.get(idx):
                    loading_label.destroy()

                # Display image
                preview_image = img.copy()
                preview_image.thumbnail(PREVIEW_SIZE, Image.Resampling.LANCZOS)
                photo_image = ImageTk.PhotoImage(preview_image)
                self.image_refs.append(photo_image)

                if img_label := self.image_labels.get(idx):
                    img_label.configure(image=photo_image)
            else:
                # Show error state
                if loading_label := self.loading_labels.get(idx):
                    loading_label.configure(text="Failed to load")
        except Exception as e:
            logging.error(f"Error handling loaded image: {e}")
            if loading_label := self.loading_labels.get(idx):
                loading_label.configure(text="Error")

    def grid(self, **kwargs: Any) -> None:
        self.frame.grid(**kwargs)


class ImageSelectorGUI:
    """GUI window for selecting images."""

    def __init__(
        self,
        on_search: OnSearchCallback,
        on_select: OnSelectCallback,
        on_skip: Callable[[], None],
        on_quit: Callable[[], None],
    ) -> None:
        """Initialize the GUI with callbacks."""
        self.on_search = on_search
        self.on_select = on_select
        self.on_skip = on_skip
        self.on_quit = on_quit

        # Initialize state
        self.term_data: Optional[Dict[str, Any]] = None
        self.image_refs: List[ImageTk.PhotoImage] = []
        self.image_grid: Optional[ImageGrid] = None

        # Create and configure the main window
        self.root = tk.Tk()
        self._setup_window()
        self._create_layout()

    def _setup_window(self) -> None:
        """Configure the main window properties."""
        self.root.title("Flashcard Image Selector")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Calculate window dimensions
        window_width = PADDING * 2 + GRID_COLUMNS * (PREVIEW_SIZE[0] + PADDING * 2)
        window_height = (
            PADDING * 2 + HEADER_HEIGHT + 2 * (PREVIEW_SIZE[1] + PADDING * 2)
        )
        self.root.geometry(f"{window_width}x{window_height}")

        # Add keyboard shortcuts
        self.root.bind("<Key>", self._handle_key)
        self.root.bind("<Button-1>", self._focus_on_click)

    def _create_layout(self) -> None:
        """Create and arrange the GUI components."""
        # Add instructions
        ttk.Label(self.root, text=INSTRUCTIONS, padding=10, font=BODY_FONT).pack()

        # Create scrollable content area
        self.scroll_container = ScrollableFrame(cast(tk.Widget, self.root))
        self.scroll_container.pack()

        # Create empty frames for dynamic content
        self.term_frame = ttk.Frame(self.scroll_container.frame)
        self.term_frame.grid(
            row=0, column=0, columnspan=GRID_COLUMNS, sticky="ew", padx=15, pady=(0, 15)
        )

        self.grid_frame = ttk.Frame(self.scroll_container.frame)
        self.grid_frame.grid(row=1, column=0, columnspan=GRID_COLUMNS)

        # Create image grid
        self.image_grid = ImageGrid(self.grid_frame, self.on_select)
        self.image_grid.grid()

    def update_term(self, term_data: Dict[str, Any]) -> None:
        """Update the term information displayed."""
        self.term_data = term_data

        # Clear existing widgets
        for widget in self.term_frame.winfo_children():
            widget.destroy()

        # Create new term info panel
        self.term_info = TermInfoPanel(self.term_frame, term_data, self.on_search)
        self.term_info.grid(sticky="ew")

    def update_image_futures(
        self, futures: List[concurrent.futures.Future[Optional[Image.Image]]]
    ) -> None:
        """Update the display with new image futures."""
        if self.image_grid:
            self.image_grid.display_futures(futures)

    def _focus_on_click(self, event: tk.Event) -> None:
        """Set focus to the root window when clicking outside of the input field."""
        if (
            hasattr(self, "term_info")
            and event.widget != self.term_info.query_panel.query_entry
        ):
            self.root.focus_set()

    def _handle_key(self, event: tk.Event) -> None:
        """Handle keyboard shortcuts."""
        # Ignore keyboard shortcuts when focused on search entry
        if (
            hasattr(self, "term_info")
            and event.widget == self.term_info.query_panel.query_entry
        ):
            return

        key = event.char.lower()

        if key == "n":
            self.on_skip()
            self.root.quit()
        elif key == "q":
            self.on_quit()
            self.root.quit()
        elif key in "123456789":
            idx = int(key) - 1
            # Only allow selection if image is loaded
            if self.image_grid and idx < len(self.image_grid.futures):
                future = self.image_grid.futures[idx]
                if future.done():
                    self.on_select(idx, future.result())
                    self.root.quit()
        elif key == "0":  # Handle 0 as the 10th image
            if self.image_grid and len(self.image_grid.futures) > 9:
                future = self.image_grid.futures[9]
                if future.done():
                    self.on_select(9, future.result())
                    self.root.quit()

    def _on_close(self) -> None:
        """Handle window close button."""
        self.on_quit()
        self.root.quit()

    def run(self) -> None:
        """Start the GUI event loop."""
        self.root.mainloop()

    def destroy(self) -> None:
        """Clean up resources and destroy the window."""
        if hasattr(self, "root"):
            self.root.destroy()
            delattr(self, "root")
