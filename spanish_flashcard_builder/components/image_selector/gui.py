"""GUI component for image selection."""

import tkinter as tk
from tkinter import ttk
from PIL import Image
import logging
from typing import List, Optional, Dict

from .google_search import ImageResult
from .components import TermInfoPanel, ImageGrid, ScrollableFrame
from .image_loader import ImageLoader
from .constants import (
    PREVIEW_SIZE, GRID_COLUMNS, PADDING, HEADER_HEIGHT,
    INSTRUCTIONS, PROCESSING_MSG, NO_IMAGES_MSG, QUIT_MSG,
    BODY_FONT
)

class ImageSelectorGUI:
    """GUI window for selecting images."""
    
    def __init__(self, results: List[ImageResult], term_data: Dict):
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
        
    def _setup_window(self):
        """Configure the main window properties."""
        self.root.title("Flashcard Image Selector")
        
        # Calculate window dimensions
        window_width = PADDING * 2 + GRID_COLUMNS * (PREVIEW_SIZE[0] + PADDING * 2)
        window_height = PADDING * 2 + HEADER_HEIGHT + 2 * (PREVIEW_SIZE[1] + PADDING * 2)
        self.root.geometry(f"{window_width}x{window_height}")
        
        # Add keyboard shortcuts
        self.root.bind('<Key>', self._handle_key)

    def _create_layout(self):
        """Create and arrange the GUI components."""
        # Add instructions
        ttk.Label(
            self.root,
            text=INSTRUCTIONS,
            padding=10,
            font=BODY_FONT
        ).pack()
        
        # Create scrollable content area
        self.scroll_container = ScrollableFrame(self.root)
        self.scroll_container.pack()
        
        # Add term information
        self.term_info = TermInfoPanel(self.scroll_container.frame, self.term_data)
        self.term_info.grid(
            row=0,
            column=0,
            columnspan=GRID_COLUMNS,
            sticky='ew',
            padx=15,
            pady=(0, 15)
        )
        
        # Add image grid
        self.image_grid = ImageGrid(self.scroll_container.frame, self._handle_selection)
        self.image_grid.grid(row=1, column=0, columnspan=GRID_COLUMNS)

    def _load_and_display_images(self):
        """Load and display the images."""
        # First load image bytes in background threads
        loader = ImageLoader()
        image_bytes_dict = loader.load_images(self.results)
        
        # Process images in the main thread
        loaded_images = []
        for idx, img_bytes in image_bytes_dict.items():
            img = loader._bytes_to_image(img_bytes)
            if img is not None:
                self.full_images[idx] = img
                loaded_images.append((idx, img))
        
        # Sort images by index and display in main thread
        loaded_images.sort(key=lambda x: x[0])
        self.image_grid.display_images(loaded_images)

    def _show_processing_message(self, index: int):
        """Show the processing message after selection."""
        term = self.term_data.get('display_form', 'term')
        
        # Clear existing content
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Show processing message
        container = ttk.Frame(self.root)
        container.pack(expand=True, fill='both')
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        ttk.Label(
            container,
            text=PROCESSING_MSG.format(index + 1, term),
            font=BODY_FONT,
            padding=20
        ).grid(row=0, column=0)
        
        self.root.update()
        logging.info(f"Selected image {index + 1} for '{term}', processing...")

    def _handle_selection(self, index: int):
        """Handle image selection."""
        if 0 <= index < len(self.results) and index in self.full_images:
            self.selection = index
            self._show_processing_message(index)
            self.root.quit()

    def _handle_key(self, event):
        """Handle keyboard input."""
        if event.char == 'q':
            logging.info(QUIT_MSG)
            self.selection = None
            self.root.quit()
        elif event.char == 'n':
            logging.info(NO_IMAGES_MSG)
            self.selection = -1
            self.root.quit()
        elif event.char in '0123456789':
            selection = 0 if event.char == '0' else int(event.char)
            if 1 <= selection <= len(self.results):
                self._handle_selection(selection - 1)

    def run(self) -> Optional[int]:
        """Run the GUI and return the selected index."""
        try:
            self.root.mainloop()
        finally:
            try:
                self.root.destroy()
            except:
                pass
        return self.selection 