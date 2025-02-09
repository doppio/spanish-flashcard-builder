import json
import openai
from typing import List
from pathlib import Path
from .models import AugmentedTerm
from spanish_flashcard_builder.config import openai_config

class OpenAIClient:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.prompt_template = self._load_prompt_file("prompt_template.txt")
        self.system_instruction = self._load_prompt_file("system_instruction.txt")

    def _load_prompt_file(self, filename: str) -> str:
        prompt_path = Path(__file__).parent / "prompts" / filename
        with open(prompt_path, "r") as f:
            return f.read()

    def augment_term(self, word: str, part_of_speech: str, definitions: List[str]) -> AugmentedTerm:
        prompt = self._build_prompt(word, part_of_speech, definitions)
        
        response = openai.ChatCompletion.create(
            model=openai_config.model,
            temperature=openai_config.temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self.system_instruction},
                {"role": "user", "content": prompt}
            ]
        )

        print(response.choices[0].message.content)
        return self._parse_response(response.choices[0].message.content)

    def _build_prompt(self, word: str, part_of_speech: str, definitions: List[str]) -> str:
        definitions_text = "\n".join(f"- {d}" for d in definitions)
        return self.prompt_template.format(
            word=word,
            part_of_speech=part_of_speech,
            definitions_text=definitions_text
        )

    def _parse_response(self, response_text: str) -> AugmentedTerm:
        try:
            data = json.loads(response_text)

            example_sentences = [
                (sent["es"], sent["en"]) 
                for sent in data["example_sentences"]
            ]
            return AugmentedTerm(
                display_form=data["display_form"],
                definition=data["definition"],
                frequency_rating=data["frequency_rating"],
                example_sentences=example_sentences,
                image_search_query=data["image_search_query"],
                part_of_speech=data["part_of_speech"],
                gender=data.get("gender", None)
            )
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Failed to parse OpenAI response: {e}")