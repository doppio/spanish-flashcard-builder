from dataclasses import dataclass
from typing import Optional


@dataclass
class GeneratedTerm:
    """A vocabulary term with AI-generated content."""

    term: str
    definitions: str
    frequency_rating: int
    example_sentences: dict[str, str]
    image_search_query: str
    part_of_speech: str
    gender: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        data = {
            "term": self.term,
            "definitions": self.definitions,
            "frequency_rating": self.frequency_rating,
            "example_sentences": self.example_sentences,
            "image_search_query": self.image_search_query,
            "part_of_speech": self.part_of_speech,
        }
        if self.gender:
            data["gender"] = self.gender
        return data
