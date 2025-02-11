"""Interactive image selector for Spanish vocabulary terms."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image

from spanish_flashcard_builder.config import image_config, paths

from .google_search import GoogleImageSearch, ImageResult
from .gui import ImageSelectorGUI


class ImageSelector:
    """Manages image selection workflow for vocabulary terms.

    Handles finding terms needing images, searching for images,
    displaying options to user, and saving selected images.
    """

    def __init__(self) -> None:
        self.search = GoogleImageSearch()
        self.terms_dir = paths.terms_dir

    def _load_augmented_term(self, term_dir: Path) -> Optional[Dict[str, Any]]:
        """Load the augmented term data from a term directory."""
        try:
            augmented_file = term_dir / paths.augmented_term_filename
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

    def _save_image(self, image: Image.Image, term_dir: Path) -> bool:
        """Save and resize image for Anki flashcards."""
        try:
            processed_image = image.copy()
            original_dimensions = processed_image.size
            max_dimension = image_config.max_dimension
            processed_image.thumbnail(
                (max_dimension, max_dimension), Image.Resampling.LANCZOS
            )
            logging.info(
                f"Resized image from {original_dimensions} to {processed_image.size}"
            )

            output_path = term_dir / paths.get_image_filename(term_dir)
            processed_image.save(output_path, "PNG")
            logging.info(f"Successfully saved image to {output_path}")
            return True

        except Exception as e:
            logging.error(f"Failed to save image to {term_dir}: {e}")
            return False

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

    def _search_images_for_term(
        self, term_dir: Path, term_data: Dict[str, Any]
    ) -> Optional[List[ImageResult]]:
        """Search for images based on the term data."""
        logging.info(f"Searching for images matching term '{term_dir.name}'")
        image_results = self.search.search_images(term_data["image_search_query"])

        if not image_results:
            logging.warning(f"No images found for term {term_dir.name}")
            return None

        return image_results

    def _handle_selection_result(
        self,
        term_dir: Path,
        selection_index: Optional[int],
        selected_image: Optional[Image.Image],
    ) -> bool:
        """Process the user's image selection result.

        Returns:
            True to continue to next term, False to stop completely
        """
        if selection_index is None:
            logging.info("User quit the image selection process")
            return False
        elif selection_index == -1:
            logging.info(f"No suitable image found for term {term_dir.name}")
            return True

        if selected_image and self._save_image(selected_image, term_dir):
            logging.info(f"Successfully processed image for term {term_dir.name}")
        else:
            logging.error(f"Failed to process image for term {term_dir.name}")

        return True

    def _process_single_term(self, term_dir: Path) -> bool:
        """Process a single term to select and save an appropriate image."""
        term_data = self._load_augmented_term(term_dir)
        if not term_data:
            return True

        image_results = self._search_images_for_term(term_dir, term_data)
        if not image_results:
            return True

        logging.info(f"Displaying image options for term '{term_dir.name}'...")
        selection_index, selected_image = self._handle_image_selection(
            image_results, term_data
        )

        return self._handle_selection_result(term_dir, selection_index, selected_image)

    def _handle_image_selection(
        self, image_results: List[ImageResult], term_data: Dict[str, Any]
    ) -> Tuple[Optional[int], Optional[Image.Image]]:
        """Display image options and handle user selection.

        Returns:
            Tuple of (selection index, selected image)
            selection index: None=quit, -1=no suitable image
        """
        gui = ImageSelectorGUI(image_results, term_data)
        selection_index = gui.run()

        if selection_index is None or selection_index == -1:
            return selection_index, None

        return selection_index, gui.full_images.get(selection_index)

    def process_terms(self) -> None:
        """Process all vocabulary terms that need images."""
        try:
            pending_terms = self._get_pending_term_dirs()

            for term_dir in pending_terms:
                if not self._process_single_term(term_dir):
                    break

        except Exception as e:
            logging.error(f"Unexpected error during term processing: {e}")
            raise
