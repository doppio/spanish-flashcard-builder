"""Image loading utilities."""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from typing import Dict, List, Optional

import requests
from PIL import Image

from .google_search import ImageResult


class ImageLoader:
    """Handles loading and processing of images from URLs."""

    def __init__(self):
        self.session = requests.Session()
        self.session.request = requests.api.request

    def _fetch_image_bytes(self, url: str) -> Optional[bytes]:
        """Download image bytes from a URL."""
        try:
            response = self.session.get(url, stream=True, timeout=(1.5, 3))
            response.raise_for_status()
            return response.content
        except Exception as e:
            logging.debug(f"Failed to load image from {url}: {e}")
            return None

    def _bytes_to_image(self, image_bytes: bytes) -> Optional[Image.Image]:
        """Convert bytes to PIL Image."""
        try:
            img = Image.open(BytesIO(image_bytes))
            return img.convert("RGB") if img.mode in ("RGBA", "P") else img
        except Exception as e:
            logging.warning(f"Error converting image bytes: {e}")
            return None

    def load_images(
        self, results: List[ImageResult], max_workers: int = 10
    ) -> Dict[int, bytes]:
        """Load multiple images in parallel and return their bytes data."""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._fetch_image_bytes, result.full_url): i
                for i, result in enumerate(results[:10])
            }

            return {
                pos: img_bytes
                for future in as_completed(futures)
                if (img_bytes := future.result()) is not None
                and (pos := futures[future]) is not None
            }

    @staticmethod
    def resize_image(image: Image.Image, size: tuple[int, int]) -> Image.Image:
        """Resize image while maintaining aspect ratio."""
        img = image.copy()
        img.thumbnail(size, Image.Resampling.LANCZOS)
        return img
