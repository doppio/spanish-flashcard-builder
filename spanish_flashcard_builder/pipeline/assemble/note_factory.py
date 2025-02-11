"""Factory for creating Anki notes."""

from pathlib import Path
from typing import List

import genanki

from spanish_flashcard_builder.exceptions import ValidationError
from spanish_flashcard_builder.pipeline.generate.models import GeneratedTerm

from .media import AnkiMediaHandler
from .models import AnkiNote, SpanishVocabModel


class AnkiNoteFactory:
    """Creates Anki notes from vocabulary terms."""

    def __init__(self) -> None:
        self.model = SpanishVocabModel()
        self.media_handler = AnkiMediaHandler()

    def create_note(self, term_dir: Path, term: GeneratedTerm) -> genanki.Note:
        """Create an Anki note from a term.

        Args:
            term_dir: Directory containing the term's files
            term: The term data

        Returns:
            A genanki Note object

        Raises:
            ValidationError: If term data is invalid
            MediaProcessingError: If media files are missing or invalid
        """
        # Get media paths
        media = self.media_handler.get_media_paths(term_dir, term)
        if not media:
            raise ValidationError(f"Missing media files for term: {term.term}")

        image_path, audio_path = media

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

    def get_media_files(self) -> List[str]:
        """Get list of media files used in notes."""
        return self.media_handler.get_tracked_media()
