"""Interactive image selector for Spanish vocabulary terms."""

import concurrent.futures
import json
import logging
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from PIL import Image

from spanish_flashcard_builder.config import image_config, paths

from .google_search import GoogleImageSearch, ImageResult, ImageSearchError
from .gui import ImageSelectorGUI
from .image_processor import ImageProcessor


class ImageSelector:
    """Manages image selection workflow for vocabulary terms.

    Handles finding terms needing images, searching for images,
    displaying options to user, and saving selected images.
    """

    def __init__(self) -> None:
        """Initialize with term data."""
        self.search_client = GoogleImageSearch()
        self.current_results: List[ImageResult] = []
        self.selected_index: Optional[int] = None
        self.gui: Optional[ImageSelectorGUI] = None
        self.terms_dir = paths.terms_dir
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self.loading_futures: List[
            concurrent.futures.Future[Optional[Image.Image]]
        ] = []

    def _load_augmented_term(self, term_dir: Path) -> Optional[Dict[str, Any]]:
        """Load the augmented term data from a term directory."""
        try:
            augmented_file = term_dir / paths.flashcard_filename
            if not augmented_file.exists():
                logging.warning(f"No augmented term file found in {term_dir}")
                return None

            with open(augmented_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    logging.error(f"Invalid JSON format in {term_dir}: expected dict")
                    return None
                return data
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing augmented term file in {term_dir}: {e}")
            return None
        except Exception as e:
            logging.error(
                f"Unexpected error loading augmented term from {term_dir}: {e}"
            )
            return None

    def _get_pending_term_dirs(self) -> List[Path]:
        """Get directories of vocabulary terms that still need images."""
        terms_path = Path(self.terms_dir)
        if not terms_path.exists():
            logging.error(f"Terms directory not found: {terms_path}")
            return []

        pending_dirs = []
        for term_dir in terms_path.iterdir():
            if not term_dir.is_dir():
                continue

            image_path = term_dir / paths.get_image_filename(term_dir)
            if not image_path.exists():
                pending_dirs.append(term_dir)
            else:
                logging.debug(f"Skipping {term_dir.name}: image already exists")

        return pending_dirs

    def _fetch_image(self, url: str) -> Optional[bytes]:
        try:
            response = requests.get(url, timeout=(1.5, 3))
            response.raise_for_status()
            return response.content
        except Exception as e:
            logging.error(f"Failed to fetch image from {url}: {e}")
            return None

    def _load_image_async(
        self, result: ImageResult
    ) -> concurrent.futures.Future[Optional[Image.Image]]:
        """Start async loading of an image."""
        return self.executor.submit(self._load_image, result)

    def _load_image(self, result: ImageResult) -> Optional[Image.Image]:
        """Load a single image."""
        try:
            response = requests.get(result.full_url, stream=True, timeout=10)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except Exception as e:
            logging.error(f"Failed to load image from {result.full_url}: {e}")
            return None

    def _handle_search(self, query: str) -> None:
        """Handle new search request."""
        logging.info(f"Searching for '{query}'...")

        try:
            self.current_results = self.search_client.search_images(query)

            # Start async loading and update GUI
            self.loading_futures = [
                self._load_image_async(result)
                for result in self.current_results[:10]  # Limit to first 10 images
            ]
            if self.gui:
                self.gui.update_image_futures(self.loading_futures)

        except ImageSearchError as e:
            logging.error(f"Error during image search: {e}")
            self.current_results = []

    def _handle_select(self, index: int, image: Optional[Image.Image]) -> None:
        """Handle select action."""
        self.selected_index = index
        self.selected_image = image
        logging.info("Selected image")

    def _handle_skip(self) -> None:
        """Handle skip action."""
        self.selected_index = -1
        logging.info("Skipped image selection")

    def _handle_quit(self) -> None:
        """Handle quit action."""
        self.selected_index = None
        logging.info("Quit image selection")

    def _search_images_for_term(
        self, term_dir: Path, term_data: Dict[str, Any]
    ) -> Optional[List[ImageResult]]:
        """Search for images based on the term data."""
        logging.info(f"Searching for images matching term '{term_dir.name}'")
        results = self.search_client.search_images(term_data["image_search_query"])

        if not results:
            logging.warning(f"No images found for term {term_dir.name}")
            return None

        images = {}
        for i, result in enumerate(results[:10]):
            if img_bytes := self._fetch_image(result.full_url):
                images[i] = img_bytes

        return results if images else None

    def process_terms(self) -> None:
        """Process all vocabulary terms that need images."""
        processor = ImageProcessor(image_config.max_dimension)
        pending_terms = self._get_pending_term_dirs()

        if not pending_terms:
            logging.info("No terms need images")
            return

        # Create single GUI instance
        self.gui = ImageSelectorGUI(
            on_search=self._handle_search,
            on_select=self._handle_select,
            on_skip=self._handle_skip,
            on_quit=self._handle_quit,
        )

        try:
            for term_dir in pending_terms:
                if term_data := self._load_augmented_term(term_dir):
                    # Initial search and update GUI
                    self._handle_search(term_data["image_search_query"])
                    if not self.current_results:
                        continue

                    if self.gui:
                        self.gui.update_term(term_data)
                        self.gui.run()

                    # Handle selection result
                    if self.selected_index is None:  # User quit
                        break
                    if self.selected_index == -1:  # Skip
                        continue
                    # Valid selection
                    if self.selected_image:
                        processor.process_and_save(
                            self.selected_image,
                            term_dir / paths.get_image_filename(term_dir),
                        )
        finally:
            if self.gui:
                self.gui.destroy()
                self.gui = None
            self.executor.shutdown(wait=False)
