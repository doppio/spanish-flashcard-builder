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
            logging.debug(f"Original image dimensions: {original_dims}")

            # Ensure image is in a format that supports RGBA
            if processed.mode not in ("RGB", "RGBA"):
                logging.info(f"Converting image from {processed.mode} to RGB")
                processed = processed.convert("RGB")

            processed.thumbnail(
                (self.max_dimension, self.max_dimension), Image.Resampling.LANCZOS
            )
            logging.debug(f"Resized image dimensions: {processed.size}")

            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                processed.save(output_path, "PNG")
            except Exception as e:
                logging.error(f"Failed to save image: {str(e)}")
                return None

            if not output_path.exists():
                logging.error(f"Image file was not created at {output_path}")
                return None

            try:
                # Verify the saved image can be loaded
                Image.open(output_path)
            except Exception as e:
                logging.error(f"Saved image is corrupted: {str(e)}")
                if output_path.exists():
                    output_path.unlink()
                return None

            result = ProcessedImage(output_path, original_dims)
            logging.debug(f"Successfully created ProcessedImage: {result}")
            return result

        except Exception as e:
            logging.error(f"Failed to process image: {str(e)}", exc_info=True)
            if output_path.exists():
                try:
                    output_path.unlink()
                except Exception as del_e:
                    logging.error(
                        f"Failed to delete corrupted output file: {str(del_e)}"
                    )
            return None
