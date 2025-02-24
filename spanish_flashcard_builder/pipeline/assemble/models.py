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
class NoteData:
    """A Spanish vocabulary note."""

    term: str
    definitions: str
    part_of_speech: str
    gender: Optional[str]
    example_sentences: List[ExampleSentence]
    image_path: Optional[Path]
    audio_path: Optional[Path]
    frequency_rating: int
    guid: str
    sort_key: str

    def to_fields(self) -> List[Optional[str]]:
        """Convert to Anki fields."""
        return [
            self.term,
            self.gender or "",
            self.part_of_speech,
            self.definitions,
            self._format_sentences(),
            f'<img src="{self.image_path.name}">' if self.image_path else "",
            f"[sound:{self.audio_path.name}]" if self.audio_path else "",
            str(self.frequency_rating),
            self.guid,
            self.sort_key,
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
            {"name": "SortKey"},
        ]

        template_dir = Path(__file__).parent / "templates"
        templates = [
            {
                "name": "Spanish -> English",
                "qfmt": (template_dir / "spanish_to_english_front.html").read_text(),
                "afmt": (template_dir / "spanish_to_english_back.html").read_text(),
            },
            {
                "name": "English -> Spanish",
                "qfmt": (template_dir / "english_to_spanish_front.html").read_text(),
                "afmt": (template_dir / "english_to_spanish_back.html").read_text(),
            },
        ]

        css = (template_dir / "spanish_vocab.css").read_text()

        super().__init__(
            model_id=SPANISH_MODEL_ID,
            name="Spanish Vocabulary",
            fields=fields,
            sort_field_index=len(fields) - 1,
            templates=templates,
            css=css,
        )
