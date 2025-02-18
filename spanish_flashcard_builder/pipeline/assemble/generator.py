"""Generates Anki decks from processed vocabulary terms."""

import json
import logging
from pathlib import Path
from typing import Optional

import genanki

from spanish_flashcard_builder.config import paths
from spanish_flashcard_builder.pipeline.generate.models import GeneratedTerm

from .note_factory import AnkiNoteFactory

logger = logging.getLogger(__name__)


class AnkiDeckGenerator:
    """Generates an Anki deck from vocabulary terms."""

    def __init__(self, deck_name: str, deck_id: int):
        self.deck = genanki.Deck(deck_id, deck_name)
        self.note_factory = AnkiNoteFactory()

    def generate(self) -> None:
        """Generate the Anki deck package."""
        terms_dir = Path(paths.terms_dir)

        for term_dir in terms_dir.iterdir():
            if not term_dir.is_dir():
                continue

            try:
                if term_data := self._load_term_data(term_dir):
                    note = self.note_factory.create_note(term_dir, term_data)
                    self.deck.add_note(note)
            except Exception as e:
                logger.error(f"Failed to process {term_dir}: {e}")

        self._save_deck()

    def _save_deck(self) -> None:
        """Save the deck with media files."""
        package = genanki.Package(self.deck)
        package.media_files = self.note_factory.media_files
        package.write_to_file(str(paths.deck_file))
        logger.info(f"Generated deck at {paths.deck_file}")

    @staticmethod
    def _load_term_data(term_dir: Path) -> Optional[GeneratedTerm]:
        """Load term data from json."""
        try:
            term_path = term_dir / paths.flashcard_filename
            if term_path.exists():
                return GeneratedTerm(**json.loads(term_path.read_text()))
        except Exception as e:
            logger.error(f"Failed to load term data at {term_dir}: {e}")

        return None
