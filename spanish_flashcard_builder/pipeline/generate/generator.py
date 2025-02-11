import json
import os
from typing import Any, Dict, List, Optional, Tuple

from spanish_flashcard_builder.config import paths

from .io import JSONFileEditor
from .openai_api import OpenAIClient


class ContentGenerator:
    """Generates AI content for vocabulary terms."""

    def __init__(self) -> None:
        self.openai_client = OpenAIClient()
        self.json_editor = JSONFileEditor()

    def process_all_pending(self) -> bool:
        """Generate content for all pending vocabulary words."""
        if not self._check_terms_dir():
            return False

        words_processed = False
        for folder_path in self._get_pending_word_folders():
            print(f"Generating content for: {os.path.basename(folder_path)}")
            words_processed |= self.generate_word(folder_path)

        return words_processed

    def _check_terms_dir(self) -> bool:
        """Check if terms directory exists."""
        if not os.path.exists(paths.terms_dir):
            print(f"Terms directory not found: {paths.terms_dir}")
            return False
        return True

    def _get_pending_word_folders(self) -> List[str]:
        """Get list of folders that need content generation."""
        pending_folders = []
        for folder_name in sorted(os.listdir(paths.terms_dir)):
            folder_path = os.path.join(paths.terms_dir, folder_name)
            if not os.path.isdir(folder_path):
                continue

            if self._needs_generation(folder_path):
                pending_folders.append(folder_path)
        return pending_folders

    def _needs_generation(self, folder_path: str) -> bool:
        """Check if folder needs content generation."""
        mw_path = os.path.join(folder_path, paths.dictionary_entry_filename)
        output_path = os.path.join(folder_path, paths.augmented_term_filename)
        return os.path.exists(mw_path) and not os.path.exists(output_path)

    def generate_word(self, folder_path: str) -> bool:
        """Generate content for a single vocabulary word."""
        entry = self._load_mw_data(folder_path)
        if not entry:
            return False

        word_data = self._parse_mw_data(entry)
        if not word_data:
            return False

        term_data = self._generate_content(*word_data)
        if not term_data:
            return False

        return self._save_content(folder_path, term_data)

    def _load_mw_data(self, folder_path: str) -> Optional[Dict[str, Any]]:
        """Load Merriam-Webster dictionary data."""
        try:
            with open(os.path.join(folder_path, paths.dictionary_entry_filename)) as f:
                result: Dict[str, Any] = json.load(f)
                return result
        except Exception as e:
            print(f"Error loading dictionary entry: {e}")
            return None

    def _parse_mw_data(self, entry: Dict) -> Optional[Tuple[str, str, List[str]]]:
        """Parse required fields from MW data."""
        try:
            word = entry.get("hwi", {}).get("hw", "")
            pos = entry.get("fl", "")
            definitions = entry.get("shortdef", [])

            if not word or not pos or not definitions:
                print(
                    "Missing required data in MW entry: "
                    f"word={word}, pos={pos}, defs={definitions}"
                )
                return None
            return word, pos, definitions
        except Exception as e:
            print(f"Error parsing MW data: {e}")
            return None

    def _generate_content(
        self, word: str, part_of_speech: str, definitions: List[str]
    ) -> Optional[Dict]:
        """Generate enriched content using OpenAI."""
        try:
            generated_data = self.openai_client.generate_term(
                word, part_of_speech, definitions
            )
            return generated_data.to_dict()
        except Exception as e:
            print(f"Error generating content: {e}")
            return None

    def _save_content(self, folder_path: str, term_data: Dict) -> bool:
        """Save generated content after user review."""
        try:
            print("\nGenerated content. Opening editor...")
            if not self.json_editor.edit_json_in_editor(term_data):
                print("Content generation was cancelled")
                return False

            output_path = os.path.join(folder_path, paths.augmented_term_filename)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(term_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving content: {e}")
            return False
