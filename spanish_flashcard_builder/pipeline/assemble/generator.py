"""Generates Anki decks from processed vocabulary terms."""

import json
import logging
from pathlib import Path
from typing import Optional

import genanki

from spanish_flashcard_builder.config import paths
from spanish_flashcard_builder.exceptions import ContentGenerationError
from spanish_flashcard_builder.pipeline.generate.models import GeneratedTerm

from .note_factory import AnkiNoteFactory

logger = logging.getLogger(__name__)


class AnkiDeckGenerator:
    """Generates an Anki deck from processed Spanish vocabulary terms."""

    def __init__(self, deck_name: str, deck_id: int):
        """Initialize the deck generator.

        Args:
            deck_name: Display name for the Anki deck
            deck_id: Unique identifier for the deck
        """
        self.deck = genanki.Deck(deck_id, deck_name)
        self.note_factory = AnkiNoteFactory()

    def _load_term(self, term_dir: Path) -> Optional[GeneratedTerm]:
        """Load term data from json file."""
        try:
            term_path = term_dir / paths.flashcard_filename
            return GeneratedTerm(**json.loads(term_path.read_text()))
        except Exception as e:
            logger.error(f"Failed to load term data from {term_dir}: {e}")
            return None

    def generate(self) -> None:
        """Generate the Anki deck package with all terms and media."""
        terms_dir = Path(paths.terms_dir)

        for term_dir in terms_dir.iterdir():
            if not term_dir.is_dir():
                continue

            try:
                if term := self._load_term(term_dir):
                    note = self.note_factory.create_note(term_dir, term)
                    self.deck.add_note(note)
            except (ContentGenerationError, Exception) as e:
                logger.error(f"Failed to process term in {term_dir}: {e}")
                continue

        # Create and save package
        package = genanki.Package(self.deck)
        package.media_files = self.note_factory.get_media_files()
        package.write_to_file(str(paths.deck_file))
        logger.info(f"Generated deck at {paths.deck_file}")
