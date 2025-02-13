"""Factory for creating Anki notes."""

from pathlib import Path
from typing import List, Tuple

import genanki

from spanish_flashcard_builder.exceptions import SpanishFlashcardError
from spanish_flashcard_builder.pipeline.generate.models import GeneratedTerm

from .models import AnkiNote, SpanishVocabModel


class MediaProcessingError(SpanishFlashcardError):
    """Raised when processing media files fails."""

    pass


class AnkiNoteFactory:
    """Creates Anki notes from vocabulary terms."""

    def __init__(self) -> None:
        self.model = SpanishVocabModel()
        self.media_files: List[str] = []

    def create_note(self, term_dir: Path, term: GeneratedTerm) -> genanki.Note:
        """Create an Anki note from a term.

        Args:
            term_dir: Directory containing the term's files
            term: The term data

        Returns:
            A genanki Note object

        Raises:
            MediaProcessingError: If media files are missing or invalid
        """
        image_path, audio_path = self._get_media_paths(term_dir)

        # Convert dict to list of tuples for example sentences
        example_sentences = [(es, en) for es, en in term.example_sentences.items()]

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

        return genanki.Note(
            model=self.model,
            fields=note_data.to_fields(),
            guid=term_dir.name,
            sort_field=f"{10000 - note_data.frequency_rating:05d}-{term.term.lower()}",
        )

    def _get_media_paths(self, term_dir: Path) -> Tuple[Path, Path]:
        """Get and validate media paths."""
        image_path = term_dir / "image.png"  # Using hardcoded paths for now
        audio_path = term_dir / "audio.mp3"  # Using hardcoded paths for now

        if not image_path.exists():
            raise MediaProcessingError(f"Missing image file: {image_path}")
        if not audio_path.exists():
            raise MediaProcessingError(f"Missing audio file: {audio_path}")

        self.media_files.extend([str(image_path), str(audio_path)])
        return image_path, audio_path
