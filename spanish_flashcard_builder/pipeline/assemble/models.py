from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple

import genanki

from spanish_flashcard_builder.config import anki_config

from .templates import load_template, render_template

# Type aliases for clarity
ExampleSentence = Tuple[str, str]  # (Spanish, English)

# Constants
SPANISH_MODEL_ID = anki_config.model_id


class AnkiFields(str, Enum):
    """Field names for Anki notes, order defines field order"""

    TERM = "Term"
    GENDER = "Gender"
    PART_OF_SPEECH = "PartOfSpeech"
    DEFINITION = "Definition"
    EXAMPLE_SENTENCES = "ExampleSentences"
    IMAGE = "Image"
    AUDIO = "Audio"
    FREQUENCY_RATING = "FrequencyRating"
    GUID = "GUID"  # Hidden field for reimporting


@dataclass
class AnkiNote:
    """A Spanish vocabulary note with all required fields."""

    term: str
    definitions: str
    part_of_speech: str
    gender: Optional[str]
    example_sentences: List[ExampleSentence]
    image_path: Path
    audio_path: Path
    frequency_rating: int
    guid: str

    def to_fields(self) -> List[str]:
        """Convert note data to ordered fields for Anki."""
        formatted_sentences = render_template(
            "example_sentences.html",
            {
                "sentences": [
                    {"spanish": es, "english": en} for es, en in self.example_sentences
                ]
            },
        )

        field_values = {
            str(AnkiFields.TERM): self.term,
            str(AnkiFields.GENDER): self.gender or "",
            str(AnkiFields.PART_OF_SPEECH): self.part_of_speech,
            str(AnkiFields.DEFINITION): self.definitions,
            str(AnkiFields.EXAMPLE_SENTENCES): formatted_sentences,
            str(AnkiFields.IMAGE): f'<img src="{self.image_path.name}">',
            str(AnkiFields.AUDIO): f"[sound:{self.audio_path.name}]",
            str(AnkiFields.FREQUENCY_RATING): str(self.frequency_rating),
            str(AnkiFields.GUID): self.guid,
        }

        return [field_values[str(field)] for field in AnkiFields]

    def _validate_fields(self) -> None:
        """Validate all required fields are present and correctly formatted."""
        if not self.term:
            raise ValueError("Term is required")
        if not self.definitions:
            raise ValueError("Definitions are required")
        if not self.part_of_speech:
            raise ValueError("Part of speech is required")
        if not self.example_sentences:
            raise ValueError("Example sentences are required")
        if not self.image_path:
            raise ValueError("Image path is required")
        if not self.audio_path:
            raise ValueError("Audio path is required")


class SpanishVocabModel(genanki.Model):
    """Anki model for Spanish vocabulary cards."""

    def __init__(self) -> None:
        super().__init__(
            model_id=SPANISH_MODEL_ID,
            name="Spanish Vocabulary",
            fields=[{"name": field.value} for field in AnkiFields],
            templates=[
                {
                    "name": "Spanish -> English",
                    "qfmt": load_template("spanish_vocab_front.html"),
                    "afmt": load_template("spanish_vocab_back.html"),
                }
            ],
            css=load_template("spanish_vocab.css"),
        )
