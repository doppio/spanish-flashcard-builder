from dataclasses import dataclass

@dataclass
class EnrichmentData:
    display_form: str  # e.g., "la silla", "el/la estudiante"
    definitions: list 
    frequency_rating: int
    example_sentences: list  # List of (Spanish, English) pairs
    image_search_query: str
    part_of_speech: str
    gender: str

    def to_dict(self):
        return {
            "display_form": self.display_form,
            "part_of_speech": self.part_of_speech,
            "gender": self.gender,
            "definitions": self.definitions,
            "example_sentences": [
                {"es": es, "en": en} 
                for es, en in self.example_sentences
            ],
            "frequency_rating": self.frequency_rating,
            "image_search_query": self.image_search_query
        }
