"""Content generation for vocabulary terms."""

import json
import logging
from pathlib import Path
from typing import Any, Dict

from spanish_flashcard_builder.config import paths
from spanish_flashcard_builder.exceptions import SpanishFlashcardError

from .openai_api import OpenAIClient
from .persistence import ContentPersistence
from .reviewer import ContentReviewer

logger = logging.getLogger(__name__)


class ContentGenerationError(SpanishFlashcardError):
    """Raised when content generation fails."""

    pass


class ContentGenerator:
    """Generates AI content for vocabulary terms."""

    def __init__(self) -> None:
        self.openai_client = OpenAIClient()
        self.persistence = ContentPersistence()
        self.reviewer = ContentReviewer()

    def process_all_pending(self) -> bool:
        """Generate content for all pending vocabulary words."""
        terms_dir = Path(paths.terms_dir)
        if not terms_dir.exists():
            logger.error(f"Terms directory not found: {terms_dir}")
            return False

        words_processed = False
        for folder_path in self._get_pending_folders(terms_dir):
            logger.info(f"Generating content for: {folder_path.name}")
            try:
                words_processed |= self.generate_word(folder_path)
            except ContentGenerationError as e:
                logger.error(f"Failed to generate content for {folder_path}: {e}")
                continue

        return words_processed

    def generate_word(self, folder_path: Path) -> bool:
        """Generate content for a single vocabulary word."""
        print(f"Generating content for '{folder_path.name}'...")
        try:
            dict_file = folder_path / paths.dictionary_entry_filename
            with open(dict_file, encoding="utf-8") as f:
                data: Dict[str, Any] = json.load(f)

            try:
                word = data["meta"]["id"]
                part_of_speech = data["fl"]
                definitions = data["shortdef"]
            except KeyError as e:
                raise ContentGenerationError(
                    f"Missing required field in dictionary data: {e}"
                ) from e

            generated_data = self.openai_client.generate_term(
                word, part_of_speech, definitions
            )
            term_dict = generated_data.to_dict()

            if not self.reviewer.review_content(term_dict):
                return False

            return self.persistence.save_content(folder_path, term_dict)

        except json.JSONDecodeError as e:
            raise ContentGenerationError(f"Invalid JSON in dictionary file: {e}") from e
        except FileNotFoundError as e:
            raise ContentGenerationError(
                f"Dictionary file not found: {dict_file}"
            ) from e
        except Exception as e:
            logger.exception(f"Unexpected error generating content for '{folder_path}'")
            raise ContentGenerationError(str(e)) from e

    def _get_pending_folders(self, terms_dir: Path) -> list[Path]:
        """Get list of folders that need content generation."""
        return [
            path
            for path in sorted(terms_dir.iterdir())
            if path.is_dir() and self.persistence.needs_generation(path)
        ]
