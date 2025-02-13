import json
import logging
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from spanish_flashcard_builder.config import paths

from .models import DictionaryEntry, DictionaryTerm
from .mw_api import look_up


class CurationError(Exception):
    """Raised when curation state becomes invalid"""

    pass


@dataclass
class _StateData:
    headword_index: int = 0
    entry_index: int = 0
    headword_entry_count: Dict[str, int] = field(default_factory=dict)


class State:
    def __init__(self) -> None:
        self._headwords: List[str] = self._load_headword_list()
        self._data: _StateData = _StateData()
        self._lookup_cache: Dict[str, DictionaryTerm] = {}
        self._load_history()
        self._ensure_valid_state()

    def _ensure_valid_state(self) -> None:
        """Ensures current state points to valid entries"""
        while not self._get_term_for_headword(self._current_word()):
            if not self._go_to_next_headword():
                raise CurationError("No headwords with entries found!")

    def _current_word(self) -> str:
        try:
            return self._headwords[self._data.headword_index]
        except IndexError as e:
            raise CurationError("Global headword index out of range") from e

    def current_term(self) -> DictionaryTerm:
        term = self._get_term_for_headword(self._current_word())
        if not term:
            if self._go_to_next_headword():
                return self.current_term()
            raise CurationError("No more valid terms found")
        return term

    def current_entry(self) -> DictionaryEntry:
        term = self.current_term()
        if not term.entries:
            raise CurationError(f"No entries found for term: {term.headword}")

        try:
            return term.entries[self._data.entry_index]
        except IndexError as e:
            raise CurationError(f"""
                Entry index {self._data.entry_index} out of range
                for '{term.headword}'
            """) from e

    def commit_entry(self) -> None:
        self._data.entry_index += 1
        current_word = self.current_term().headword
        entry_count = self._data.headword_entry_count.get(current_word, 0)

        if self._data.entry_index >= entry_count:
            if not self._go_to_next_headword():
                logging.info("Reached the end of the vocabulary list.")
        self._save_history()

    def undo(self) -> None:
        if self._data.entry_index > 0:
            self._data.entry_index -= 1
        elif self._data.headword_index > 0 and self._go_to_previous_headword():
            prev_word = self.current_term().headword
            count = self._data.headword_entry_count.get(prev_word, 0)
            self._data.entry_index = max(0, count - 1)
        else:
            logging.info("Already at the first entry")
            return

        self._save_history()

    def _get_term_for_headword(self, word: str) -> Optional[DictionaryTerm]:
        if word in self._lookup_cache:
            return self._lookup_cache[word]

        try:
            term = look_up(word)
            if term and term.entries:
                self._lookup_cache[word] = term
                self._data.headword_entry_count[word] = len(term.entries)
                return term
        except Exception as e:
            logging.error(f"Error looking up word '{word}': {e}")
        return None

    def _advance_headword(self, step: int) -> bool:
        while True:
            new_index = self._data.headword_index + step
            if not 0 <= new_index < len(self._headwords):
                return False

            self._data.headword_index = new_index
            self._data.entry_index = 0
            word = self._current_word()

            if self._get_term_for_headword(word):
                return True

    def _go_to_next_headword(self) -> bool:
        return self._advance_headword(1)

    def _go_to_previous_headword(self) -> bool:
        return self._advance_headword(-1)

    def _load_headword_list(self) -> List[str]:
        try:
            with open(paths.sanitized_vocab, encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            raise CurationError(f"Error loading word list: {e}") from e

    def _load_history(self) -> None:
        if not os.path.exists(paths.curator_history):
            return
        try:
            with open(paths.curator_history, "r", encoding="utf-8") as f:
                self._data = _StateData(**json.load(f))
        except Exception as e:
            logging.error(f"Error loading history: {e}")

    def _save_history(self) -> None:
        try:
            with open(paths.curator_history, "w", encoding="utf-8") as f:
                json.dump(self._data.__dict__, f, indent=2)
        except IOError as e:
            logging.error(f"Error saving history: {e}")

    def __enter__(self) -> "State":
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[object],
    ) -> None:
        self._save_history()
