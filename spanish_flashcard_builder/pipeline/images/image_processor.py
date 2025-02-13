import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PIL import Image


@dataclass
class ProcessedImage:
    path: Path
    dimensions: tuple[int, int]


class ImageProcessor:
    def __init__(self, max_dimension: int):
        self.max_dimension = max_dimension

    def process_and_save(
        self, image: Image.Image, output_path: Path
    ) -> Optional[ProcessedImage]:
        try:
            processed = image.copy()
            original_dims = processed.size
            processed.thumbnail(
                (self.max_dimension, self.max_dimension), Image.Resampling.LANCZOS
            )
            processed.save(output_path, "PNG")
            return ProcessedImage(output_path, original_dims)
        except Exception as e:
            logging.error(f"Failed to process image: {e}")
            return None
