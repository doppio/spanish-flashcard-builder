"""Content persistence for generated vocabulary terms."""

import json
import logging
from pathlib import Path
from typing import Dict

from spanish_flashcard_builder.config import paths
from spanish_flashcard_builder.exceptions import ValidationError

from .io import JSONFileEditor

logger = logging.getLogger(__name__)


class ContentPersistence:
    """Handles saving and loading of generated content."""

    def __init__(self) -> None:
        self.json_editor = JSONFileEditor()

    def save_content(self, folder_path: Path, term_data: Dict) -> bool:
        """Save generated content after user review.

        Args:
            folder_path: Directory to save content in
            term_data: Generated term data to save

        Returns:
            True if content was saved successfully

        Raises:
            ValidationError: If content is invalid or saving fails
        """
        try:
            logger.info("Opening editor for content review...")
            if not self.json_editor.edit_json_in_editor(term_data):
                logger.info("Content generation was cancelled by user")
                return False

            output_path = folder_path / paths.flashcard_filename
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(term_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Content saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save content: {e}")
            raise ValidationError(f"Failed to save content: {e}") from e

    def needs_generation(self, folder_path: Path) -> bool:
        """Check if folder needs content generation."""
        mw_path = folder_path / paths.dictionary_entry_filename
        output_path = folder_path / paths.flashcard_filename
        return mw_path.exists() and not output_path.exists()
