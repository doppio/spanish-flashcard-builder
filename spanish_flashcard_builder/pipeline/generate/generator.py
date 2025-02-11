"""Content generation for vocabulary terms."""

import logging
from pathlib import Path

from spanish_flashcard_builder.config import paths
from spanish_flashcard_builder.exceptions import ContentGenerationError

from .data_loader import DictionaryDataLoader
from .openai_api import OpenAIClient
from .persistence import ContentPersistence

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Generates AI content for vocabulary terms."""

    def __init__(self) -> None:
        self.openai_client = OpenAIClient()
        self.data_loader = DictionaryDataLoader()
        self.persistence = ContentPersistence()

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

    def _get_pending_folders(self, terms_dir: Path) -> list[Path]:
        """Get list of folders that need content generation."""
        return [
            path
            for path in sorted(terms_dir.iterdir())
            if path.is_dir() and self.persistence.needs_generation(path)
        ]

    def generate_word(self, folder_path: Path) -> bool:
        """Generate content for a single vocabulary word."""
        try:
            # Load and parse dictionary data
            entry = self.data_loader.load_entry(folder_path)
            if not entry:
                raise ContentGenerationError("Failed to load dictionary entry")

            # Generate content using OpenAI
            generated_data = self.openai_client.generate_term(
                entry.word, entry.part_of_speech, entry.definitions
            )

            # Save content after user review
            return self.persistence.save_content(folder_path, generated_data.to_dict())

        except Exception as e:
            logger.exception(f"Unexpected error generating content for {folder_path}")
            raise ContentGenerationError(str(e)) from e
