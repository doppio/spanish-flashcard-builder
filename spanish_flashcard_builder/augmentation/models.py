from dataclasses import dataclass
from typing import Optional

@dataclass
class AugmentedTerm:
    display_form: str  # e.g., "la silla", "el/la estudiante"
    definition: str
    frequency_rating: int
    example_sentences: list  # List of (Spanish, English) pairs
    image_search_query: str
    part_of_speech: str
    gender: Optional[str] = None

    def to_dict(self):
        result = {
            "display_form": self.display_form,
            "part_of_speech": self.part_of_speech,
            "definition": self.definition,
            "example_sentences": [
                {"es": es, "en": en} 
                for es, en in self.example_sentences
            ],
            "frequency_rating": self.frequency_rating,
            "image_search_query": self.image_search_query
        }
        if self.gender is not None:
            result["gender"] = self.gender
        return result
