"""Constants for the image selector module."""

from typing import Tuple, Union

# Type aliases
FontConfig = Union[Tuple[str, int], Tuple[str, int, str]]
ImageSize = Tuple[int, int]

# Image dimensions
PREVIEW_SIZE: ImageSize = (300, 300)  # For selection UI

# UI layout
GRID_COLUMNS: int = 5
PADDING: int = 20
HEADER_HEIGHT: int = 250

# Font styles
TITLE_FONT: FontConfig = ("Arial", 18, "bold")
SUBTITLE_FONT: FontConfig = ("Arial", 16)
BODY_FONT: FontConfig = ("Arial", 14)
ITALIC_FONT: FontConfig = ("Arial", 14, "italic")

# UI messages
INSTRUCTIONS: str = (
    "Click an image or press its number key to select\n"
    "Press 'n' if no image is suitable, or 'q' to quit"
)
PROCESSING_MSG: str = "Saving image {} for '{}'..."
NO_IMAGES_MSG: str = "No suitable image found, skipping."
QUIT_MSG: str = "Quitting image selection."
