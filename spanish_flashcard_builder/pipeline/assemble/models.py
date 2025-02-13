"""Models for Anki note generation."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import genanki
from jinja2 import Environment, FileSystemLoader, Template

from spanish_flashcard_builder.config import anki_config

# Type aliases for clarity
ExampleSentence = Tuple[str, str]  # (Spanish, English)

# Constants
SPANISH_MODEL_ID = anki_config.model_id

# Template setup
env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates"))
)


def render_template(template_name: str, context: Dict[str, Any]) -> str:
    """Render a template with given context."""
    template: Template = env.get_template(template_name)
    rendered: str = template.render(**context)
    return rendered


@dataclass(frozen=True)
class AnkiNote:
    """A Spanish vocabulary note."""

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
        """Convert to Anki fields."""
        return [
            self.term,
            self.gender or "",
            self.part_of_speech,
            self.definitions,
            self._format_sentences(),
            f'<img src="{self.image_path.name}">',
            f"[sound:{self.audio_path.name}]",
            str(self.frequency_rating),
            self.guid,
        ]

    def _format_sentences(self) -> str:
        """Format example sentences with template."""
        return render_template(
            "example_sentences.html",
            {
                "sentences": [
                    {"spanish": es, "english": en} for es, en in self.example_sentences
                ]
            },
        )


class SpanishVocabModel(genanki.Model):
    """Anki model for Spanish vocabulary cards."""

    def __init__(self) -> None:
        fields = [
            {"name": "Term"},
            {"name": "Gender"},
            {"name": "PartOfSpeech"},
            {"name": "Definition"},
            {"name": "ExampleSentences"},
            {"name": "Image"},
            {"name": "Audio"},
            {"name": "FrequencyRating"},
            {"name": "GUID"},
        ]

        templates = [
            {
                "name": "Spanish -> English",
                "qfmt": env.get_template("spanish_vocab_front.html").render(),
                "afmt": env.get_template("spanish_vocab_back.html").render(),
            }
        ]

        css = env.get_template("spanish_vocab.css").render()

        super().__init__(
            model_id=SPANISH_MODEL_ID,
            name="Spanish Vocabulary",
            fields=fields,
            templates=templates,
            css=css,
        )
