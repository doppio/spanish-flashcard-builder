import json
import os
import sys

from config import VOCAB_FILE, STATE_FILE
from .spacy import canonicalize_word

class State:
    """Manages the program's state and progress through the vocabulary list"""
    def __init__(self):
        self.index = 0
        self.processed_indices = []  # Stack of processed word indices
        self.rejected_words = []  # List of rejected words
        self._load()

    def _load_vocab_list(self):
        """Load vocabulary list from file"""
        vocab = []
        try:
            with open(VOCAB_FILE, encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split()
                    if parts:
                        vocab.append(parts[0])
        except IOError as e:
            print(f"Error loading vocabulary file: {e}")
            sys.exit(1)
        return vocab

    def _load(self):
        """Load state from file if available"""
        self.vocab_list = self._load_vocab_list()
        
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    file_contents = json.load(f)
                    self.index = file_contents.get("current_index", 0)
                    self.processed_indices = file_contents.get("processed_indices", [])
                    
                    # Handle old format with decisions dict
                    decisions = file_contents.get("decisions", {})
                    if decisions:
                        # Convert old decisions format to rejected_words list
                        self.rejected_words = [
                            word for word, decision in decisions.items() 
                            if decision == "n"
                        ]
                    else:
                        # Use new format if available
                        self.rejected_words = file_contents.get("rejected_words", [])
            except (IOError, json.JSONDecodeError) as e:
                print(f"Error loading state: {e}")

    def _save(self):
        """Save current state to file using new format"""
        file_contents = {
            'current_index': self.index,
            'processed_indices': self.processed_indices,
            'rejected_words': self.rejected_words
        }
        try:
            with open(STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(file_contents, f, indent=2)
        except IOError as e:
            print(f"Error saving state: {e}")

    def current_word(self):
        """Get the current word"""
        if self.index < len(self.vocab_list):
            return self.vocab_list[self.index]
        return None

    def can_undo(self):
        """Check if undo is possible"""
        return bool(self.processed_indices)

    def undo(self):
        """
        Undo the last action by moving back to the last processed word
        Returns the previous word
        """
        if not self.can_undo():
            return None
            
        last_index = self.processed_indices.pop()
        self.index = last_index
        self._save()
        return canonicalize_word(self.vocab_list[self.index])

    def advance_to_next(self):
        """
        Advance to the next unskipped word and save the state.
        Automatically skips previously rejected words.
        """
        self.index += 1
        while self.index < len(self.vocab_list):
            word = self.vocab_list[self.index]
            canonical_word = canonicalize_word(word)
            if canonical_word and canonical_word not in self.rejected_words:
                break
            self.index += 1
        self._save()

    def accept_current_word(self):
        """Mark the current word as processed and accepted"""
        self.processed_indices.append(self.index)
        self._save()

    def reject_current_word(self):
        """Mark the current word as processed and rejected"""
        self.processed_indices.append(self.index)
        current_word = canonicalize_word(self.vocab_list[self.index])
        if current_word:
            self.rejected_words.append(current_word)
        self._save()

    def is_complete(self):
        return self.index >= len(self.vocab_list)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._save() 