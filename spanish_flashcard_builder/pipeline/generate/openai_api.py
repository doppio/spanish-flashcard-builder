"""OpenAI API client for content generation."""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from openai import OpenAI

from spanish_flashcard_builder.config import openai_config
from spanish_flashcard_builder.exceptions import ContentGenerationError

logger = logging.getLogger(__name__)


@dataclass
class GeneratedContent:
    """Generated content from OpenAI."""

    term: str
    definitions: str
    frequency_rating: int
    example_sentences: List[Dict[str, str]]
    image_search_query: str
    part_of_speech: str
    gender: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
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


class OpenAIClient:
    """Client for interacting with OpenAI API."""

    def __init__(self) -> None:
        """Initialize OpenAI client with configuration."""
        self.client = OpenAI()
        self.config = openai_config

    def generate_term(
        self, word: str, part_of_speech: str, definitions: List[str]
    ) -> GeneratedContent:
        """Generate enriched content for a vocabulary term.

        Args:
            word: The vocabulary word
            part_of_speech: Part of speech (noun, verb, etc.)
            definitions: List of dictionary definitions

        Returns:
            Generated content for the term

        Raises:
            ContentGenerationError: If content generation fails
        """
        try:
            # Load system prompt template
            with open("prompts/system_instruction.txt") as f:
                system_prompt = f.read()

            # Format user prompt
            user_prompt = self._format_user_prompt(word, part_of_speech, definitions)

            # Make API call
            response = self.client.chat.completions.create(
                model=self.config.model,
                temperature=self.config.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                stream=False,
            )

            # Parse response
            content = response.choices[0].message.content
            if not content:
                raise ContentGenerationError("Empty response from OpenAI")

            # Parse content
            try:
                data = self._parse_response(content)
                return GeneratedContent(**data)
            except Exception as err:
                raise ContentGenerationError(
                    f"Failed to parse OpenAI response: {err}"
                ) from err

        except Exception as err:
            logger.error(f"OpenAI API error for term '{word}': {err}")
            raise ContentGenerationError(f"OpenAI API error: {err}") from err

    def _format_user_prompt(
        self, word: str, part_of_speech: str, definitions: List[str]
    ) -> str:
        """Format the user prompt for OpenAI.

        This formats the input data into a clear prompt that will generate
        the desired output format.
        """
        definitions_str = "\n".join(f"- {d}" for d in definitions)
        return f"""Generate Spanish vocabulary content for:
Word: {word}
Part of Speech: {part_of_speech}
Definitions:
{definitions_str}

Please provide:
1. A clear, concise definition
2. 2-3 example sentences with translations
3. A frequency rating (1-10)
4. A descriptive image search query
5. Gender (for nouns only)"""

    def _parse_response(self, content: str) -> Dict:
        """Parse the OpenAI response into structured data.

        This is a placeholder - in reality, you'd want to implement proper
        response parsing based on your prompt engineering and expected format.
        """
        # TODO: Implement proper response parsing
        raise NotImplementedError("Response parsing not implemented")
