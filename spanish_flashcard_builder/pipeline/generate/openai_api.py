import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from openai import OpenAI

from spanish_flashcard_builder.config import api_keys, openai_config

from .models import GeneratedTerm


class OpenAIClient:
    """Client for interacting with OpenAI API."""

    def __init__(self) -> None:
        self.client = OpenAI(api_key=api_keys.openai)
        with open(
            Path(__file__).parent / "prompts" / "prompt_template.txt", encoding="utf-8"
        ) as f:
            self.prompt_template = f.read()
        self.system_instruction = self._load_prompt_file("system_instruction.txt")

    def _load_prompt_file(self, filename: str) -> str:
        prompt_path = Path(__file__).parent / "prompts" / filename
        with open(prompt_path, "r") as f:
            return f.read()

    def generate_term(
        self, word: str, part_of_speech: str, definitions: List[str]
    ) -> GeneratedTerm:
        """Generate enriched content for a vocabulary term using OpenAI."""
        prompt = self.prompt_template.format(
            word=word,
            part_of_speech=part_of_speech,
            definitions="\n".join(f"- {d}" for d in definitions),
        )

        try:
            response = self.client.chat.completions.create(
                model=openai_config.model,
                temperature=openai_config.temperature,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}],
            )
            response_text = response.choices[0].message.content
            if not response_text:
                raise ValueError("Empty response from OpenAI API")
            response_data = self._parse_response(response_text)
            return GeneratedTerm(**response_data)
        except Exception as e:
            logging.error(f"Error calling OpenAI API: {e}")
            raise

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the response from OpenAI API."""
        if not response:
            raise ValueError("Empty response from OpenAI API")
        try:
            result: Dict[str, Any] = json.loads(response)
            return result
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse OpenAI response as JSON: {e}") from e
