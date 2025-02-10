"""Image loading utilities."""

import logging
from io import BytesIO
import requests
from PIL import Image
from typing import List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from .google_search import ImageResult

class ImageLoader:
    """Handles loading and processing of images from URLs."""
    
    @staticmethod
    def fetch_image(url: str) -> Optional[Image.Image]:
        """Download and convert an image from a URL to PIL format."""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            return img.convert('RGB') if img.mode in ('RGBA', 'P') else img
        except Exception as e:
            logging.warning(f"Error loading image from {url}: {e}")
            return None
    
    @classmethod
    def load_images(cls, results: List[ImageResult], max_workers: int = 10) -> List[Tuple[int, Image.Image]]:
        """Load multiple images in parallel and return them in index order."""
        loaded_images = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(cls.fetch_image, result.full_url): i 
                for i, result in enumerate(results[:10])
            }
            
            for future in as_completed(futures):
                pos = futures[future]
                img = future.result()
                if img is not None:
                    loaded_images.append((pos, img))
        
        return sorted(loaded_images, key=lambda x: x[0])
    
    @staticmethod
    def resize_image(image: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """Resize image while maintaining aspect ratio."""
        img = image.copy()
        img.thumbnail(size, Image.Resampling.LANCZOS)
        return img 