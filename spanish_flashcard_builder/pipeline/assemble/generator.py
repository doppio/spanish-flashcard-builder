import json
from pathlib import Path
from typing import List, Optional

import genanki

from spanish_flashcard_builder.config import paths
from spanish_flashcard_builder.pipeline.generate.models import GeneratedTerm

from .models import AnkiNote, SpanishVocabModel


class AnkiDeckGenerator:
    """Generates an Anki deck from processed Spanish vocabulary terms.

    Handles the creation of Anki notes with text, images, and audio,
    packaging them into a complete deck file that can be imported into Anki.
    """

    def __init__(self, deck_name: str, deck_id: int):
        """Initialize the deck generator.

        Args:
            deck_name: Display name for the Anki deck
            deck_id: Unique identifier for the deck
        """
        self.deck = genanki.Deck(deck_id, deck_name)
        self.model = SpanishVocabModel()
        self.media_files: List[str] = []

    def _load_term(self, term_dir: Path) -> Optional[GeneratedTerm]:
        """Load term data from json file."""
        try:
            term_path = term_dir / paths.augmented_term_filename
            return GeneratedTerm(**json.loads(term_path.read_text()))
        except Exception as e:
            print(f"Failed to load term data from {term_dir}: {e}")
            return None

    def _get_media_paths(
        self, term_dir: Path, term: GeneratedTerm
    ) -> Optional[tuple[Path, Path]]:
        """Get and validate image and audio paths."""
        image_path = term_dir / paths.get_image_filename(term_dir)
        audio_path = term_dir / paths.get_pronunciation_filename(term_dir)

        if not image_path.exists() or not audio_path.exists():
            return None

        return image_path, audio_path

    def _create_note(self, term_dir: Path) -> Optional[genanki.Note]:
        """Create an Anki note from a term directory."""
        # Load and validate data
        if not (term := self._load_term(term_dir)):
            return None

        if not (media := self._get_media_paths(term_dir, term)):
            return None

        # Track media files with full paths
        image_path, audio_path = media
        self.media_files.extend(map(str, [image_path, audio_path]))

        # Convert example sentences from dict to tuple format
        example_sentences = [
            (sent["es"], sent["en"]) for sent in term.example_sentences
        ]

        # Create note data structure
        note_data = AnkiNote(
            term=term.term,
            definitions=term.definitions,
            part_of_speech=term.part_of_speech,
            gender=term.gender,
            example_sentences=example_sentences,
            image_path=Path(image_path.name),
            audio_path=Path(audio_path.name),
            frequency_rating=term.frequency_rating,
            guid=term_dir.name,
        )

        # Create actual genanki Note
        note = genanki.Note(
            model=self.model,
            fields=note_data.to_fields(),
            guid=term_dir.name,
            sort_field=(
                f"{10000 - note_data.frequency_rating:05d}-{note_data.term.lower()}"
            ),
        )

        return note

    def generate(self) -> None:
        """Generate the Anki deck package with all terms and media."""
        # Process all term directories
        terms_dir = Path(paths.terms_dir)

        for term_dir in terms_dir.iterdir():
            if term_dir.is_dir():
                if note := self._create_note(term_dir):
                    self.deck.add_note(note)

        # Create and save package
        package = genanki.Package(self.deck)
        package.media_files = self.media_files
        package.write_to_file(str(paths.deck_file))
