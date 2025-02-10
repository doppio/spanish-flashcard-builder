import os
from typing import Any, Dict, List, Optional, Tuple, cast

from spanish_flashcard_builder.config import paths

from .io import JSONFileEditor
from .openai_api import OpenAIClient


class _KeyboardInput:
    """Cross-platform keyboard input handler."""

    @staticmethod
    def getch() -> str:
        """Get a single character from stdin."""
        try:
            import msvcrt  # Windows

            msvcrt_any = cast(Any, msvcrt)  # Cast to Any to handle missing type hints
            return cast(str, msvcrt_any.getch().decode())
        except ImportError:
            import sys
            import termios
            import tty

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return cast(str, ch)


class VocabAugmentor:
    def __init__(self, vocab_dir: Optional[str] = None) -> None:
        self.vocab_dir = vocab_dir or paths.terms_dir
        self.openai_client = OpenAIClient()
        self.json_editor = JSONFileEditor()
        self._keyboard = _KeyboardInput()

    def process_all_pending(self) -> bool:
        """Augment all pending vocabulary words that need processing."""
        words_processed = False

        # Sort the directory listing alphabetically
        for folder_name in sorted(os.listdir(self.vocab_dir)):
            folder_path = os.path.join(self.vocab_dir, folder_name)
            if self._needs_augmentation(folder_path):
                print(f"Augmenting word in: {folder_path}")
                words_processed |= self.augment_word(folder_path)

        return words_processed

    def augment_word(self, folder_path: str) -> bool:
        """Augment a single vocabulary word with additional data."""
        mw_data = self.json_editor.load_json(self._get_mw_path(folder_path))
        if not isinstance(mw_data, dict):
            print(f"Invalid MW data format in {folder_path}")
            return False

        word, pos, definitions = self._parse_mw_data(mw_data)
        if not all([word, pos, definitions]):
            return False

        # Type assertions since we checked all values are not None
        word_str = cast(str, word)
        pos_str = cast(str, pos)
        defs_list = cast(List[str], definitions)

        return self._generate_augmented_term_file(
            folder_path, word_str, pos_str, defs_list
        )

    def _needs_augmentation(self, folder_path: str) -> bool:
        """Check if a word needs augmentation."""
        if not os.path.isdir(folder_path):
            return False

        mw_path = self._get_mw_path(folder_path)
        flashcard_path = self._get_flashcard_path(folder_path)
        return os.path.exists(mw_path) and not os.path.exists(flashcard_path)

    def _parse_mw_data(
        self, entry: Dict[str, Any]
    ) -> Tuple[Optional[str], Optional[str], Optional[List[str]]]:
        """Parse Merriam-Webster API response data."""
        try:
            # Verify we have the expected structure before accessing
            if "meta" not in entry:
                print("Invalid Merriam-Webster entry format: missing 'meta' field")
                return None, None, None

            return (
                entry.get("hwi", {}).get("hw", ""),
                entry.get("fl", ""),  # part of speech
                entry.get("shortdef", []),  # definitions
            )
        except (IndexError, KeyError, AttributeError) as e:
            print(f"Error parsing MW data: {e}")
            return None, None, None

    def _generate_augmented_term_file(
        self, folder_path: str, word: str, pos: str, definitions: List[str]
    ) -> bool:
        """Generate AI-augmented data and save after user review."""
        try:
            augmented_data = self.openai_client.augment_term(word, pos, definitions)
            augmented_term = {"word": word, **augmented_data.to_dict()}

            # Ask user if they want to edit
            print(
                "\nGenerated augmented data. "
                "Press 'e' to edit or SPACE to continue without editing..."
            )
            user_input = self._keyboard.getch()

            if user_input.lower() == "e":
                if not self.json_editor.edit_json_in_editor(augmented_term):
                    print("Augmented data editing was cancelled")
                    return False
            elif user_input == " ":
                print("Continuing without editing...")

            return bool(
                self.json_editor.save_json(
                    self._get_flashcard_path(folder_path), augmented_term
                )
            )
        except Exception as e:
            print(f"Error generating augmented term file: {e}")
            return False

    def _get_mw_path(self, folder_path: str) -> str:
        """Get path to Merriam-Webster data file."""
        return os.path.join(folder_path, paths.dictionary_entry_filename)

    def _get_flashcard_path(self, folder_path: str) -> str:
        """Get path to augmented flashcard data file."""
        return os.path.join(folder_path, paths.augmented_term_filename)
