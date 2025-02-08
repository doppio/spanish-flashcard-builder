from dataclasses import dataclass
from typing import List, Set, Optional
import json
import os
import sys

from config import CLEANED_SEARCH_WORD_FILE, SELECTOR_HISTORY_FILE
from vocab_selector.models import DictionaryEntry, Word
from vocab_selector.vocab_bank import VocabBank
from vocab_selector.mw_api import look_up

@dataclass
class _StateData:
    """Data structure for serializable state that stores progress through vocabulary selection"""
    processed_search_words: List[str]  # Fully processed search words (all entries handled)
    processed_entry_ids: List[str]  # Individual dictionary entry IDs that were processed
    
    @classmethod
    def from_json(cls, json_data: dict) -> '_StateData':
        return cls(**json_data)
    
    def to_json(self) -> dict:
        return self.__dict__

class State:
    """Manages the program's history and progress through the vocabulary list.
    
    Handles loading/saving history, tracking processed words, and navigating through
    the vocabulary list while maintaining the processing history.
    """
    def __init__(self, vocab_bank: 'VocabBank') -> None:
        self._vocab_bank = vocab_bank
        self._index: int = 0
        # Track fully processed search words
        self._processed_searchwords_list: List[str] = []
        self._processed_searchwords_set: Set[str] = set()
        # Track individual processed entries
        self._processed_entries_list: List[str] = []
        self._processed_entries_set: Set[str] = set()
        self._searchwords_dataset: List[str] = self._load_search_words()
        self._load_from_file()

    def current_word(self) -> Optional[str]:
        """Get the current word or None if complete"""
        return self._searchwords_dataset[self._index] if self._index < len(self._searchwords_dataset) else None

    def _advance_to_next_word(self):
        self._index += 1

    def skip_word(self, word: str) -> None:
        """Mark a word as processed and skip it"""
        self._mark_word_processed(word)
        self._advance_to_next_word()

    def accept_entry(self, entry: DictionaryEntry, word: Word) -> None:
        """Mark an entry as processed and accepted"""
        self._mark_entry_processed(entry.id)
        if self._all_entries_processed(word):
            self._mark_word_processed(entry.headword)
            self._advance_to_next_word()
        self._save_to_file()

    def reject_entry(self, entry: DictionaryEntry, word: Word) -> None:
        """Mark an entry as processed and rejected"""
        self._mark_entry_processed(entry.id)
        if self._all_entries_processed(word):
            self._mark_word_processed(entry.headword)
            self._advance_to_next_word()
        self._save_to_file()

    def undo(self) -> Optional[DictionaryEntry]:
        """Undo the last processed entry and update word status"""
        if not self._processed_entries_list:
            return None
        
        last_entry_id = self._processed_entries_list.pop()
        self._processed_entries_set.discard(last_entry_id)
        
        searchword = last_entry_id.split(':')[0]
        print(f"Should undo word {searchword}?")
        if self._processed_searchwords_list[-1] == searchword:
            print(f"Undoing: {searchword}")
            self._processed_searchwords_set.discard(searchword)
            self._processed_searchwords_list.pop()
            self._index -= 1
            
        # Delete the entry ID from the vocab bank, if it exists
        self._vocab_bank.delete_entry(last_entry_id)

        self._save_to_file()
                

    def can_undo(self):
        """Check if undo is possible"""
        return bool(self._processed_entries_list)

    def has_processed_entry(self, entry_id: str) -> bool:
        """Check if a specific entry has been processed"""
        return entry_id in self._processed_entries_set

    def has_processed_word(self, word: str) -> bool:
        """Check if all entries for a word have been processed"""
        return word in self._processed_searchwords_set

    def _all_entries_processed(self, word: Word) -> bool:
        """Check if all entries for a word have been processed"""
        return all(self.has_processed_entry(entry.id) for entry in word.entries)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._save_to_file()

    def _should_process_searchword(self, search_word: str) -> bool:
        """Check if a word should be processed"""
        if search_word in self._processed_searchwords_set:
            return False
        
        # Look up the entry to get its ID for storage check
        word = look_up(search_word)
        if not word or not word.entries:
            return False
        
        # If the word has at least one unprocessed entry, we should process it
        return not all(self.has_processed_entry(e.id) for e in word.entries)

    def _mark_word_processed(self, word: str) -> None:
        """Helper method to mark a word as processed"""
        if word not in self._processed_searchwords_set:
            self._processed_searchwords_list.append(word)
            self._processed_searchwords_set.add(word)  # Update set along with list

    def _mark_entry_processed(self, entry_id: str) -> None:
        """Helper method to mark an entry as processed"""
        if entry_id not in self._processed_entries_set:
            self._processed_entries_list.append(entry_id)
            self._processed_entries_set.add(entry_id)

    def _load_search_words(self) -> List[str]:
        """Load and return search words from vocabulary file.
        
        Returns the first word from each non-empty line in the file.
        """
        try:
            with open(CLEANED_SEARCH_WORD_FILE, encoding='utf-8') as f:
                return [line.strip().split()[0] for line in f if line.strip()]
        except IOError as e:
            print(f"Error loading vocabulary file '{CLEANED_SEARCH_WORD_FILE}': {e}")
            sys.exit(1)

    def _load_from_file(self) -> None:
        """Load previous processing history from file if available"""
        if not os.path.exists(SELECTOR_HISTORY_FILE):
            return

        try:
            with open(SELECTOR_HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = _StateData.from_json(json.load(f))
                self._processed_searchwords_list = data.processed_search_words
                self._processed_searchwords_set = set(data.processed_search_words)
                self._processed_entries_list = data.processed_entry_ids
                self._processed_entries_set = set(data.processed_entry_ids)
                
                # Find the first unprocessed word that should be processed
                self._index = 0
                while self._index < len(self._searchwords_dataset):
                    if self._should_process_searchword(self._searchwords_dataset[self._index]):
                        break
                    self._index += 1

        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading history from '{SELECTOR_HISTORY_FILE}': {e}")

    def _save_to_file(self) -> None:
        """Save current history to file"""
        try:
            history = _StateData(
                processed_search_words=self._processed_searchwords_list,
                processed_entry_ids=self._processed_entries_list
            )
            with open(SELECTOR_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history.to_json(), f, indent=2)
        except IOError as e:
            print(f"Error saving history: {e}") 