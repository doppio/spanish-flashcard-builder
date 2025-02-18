"""Factory for creating Anki notes."""

from pathlib import Path
from typing import List, Optional

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
        image_path = self._get_image_path(term_dir)
        audio_path = self._get_audio_path(term_dir)
        if image_path is not None:
            self.media_files.append(str(image_path))
        if audio_path is not None:
            self.media_files.append(str(audio_path))

        example_sentences = [
            (example["es"], example["en"]) for example in term.example_sentences
        ]

        note_data = AnkiNote(
            term=term.term,
            definitions=term.definitions,
            part_of_speech=term.part_of_speech,
            gender=term.gender,
            example_sentences=example_sentences,
            image_path=Path(image_path.name) if image_path else None,
            audio_path=Path(audio_path.name) if audio_path else None,
            frequency_rating=term.frequency_rating,
            guid=term_dir.name,
        )

        return genanki.Note(
            model=self.model,
            fields=note_data.to_fields(),
            guid=term_dir.name,
            sort_field=f"""
                {int(10000 - note_data.frequency_rating):05d}
                -{term.term.lower()}
            """,
        )

    def _get_image_path(self, term_dir: Path) -> Optional[Path]:
        """Get and validate image path."""
        image_path = term_dir / (term_dir.name + ".png")
        if not image_path.exists():
            return None

        return image_path

    def _get_audio_path(self, term_dir: Path) -> Optional[Path]:
        """Get and validate audio path."""
        audio_path = term_dir / (term_dir.name + ".mp3")
        if not audio_path.exists():
            return None

        return audio_path
