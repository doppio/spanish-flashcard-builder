#!/usr/bin/env python3

from pathlib import Path
import sys

from .mw_api import look_up
from .commands import AcceptCommand, RejectCommand, UndoCommand, QuitCommand
from .input_handler import handle_command_input
from .models import Word, DictionaryEntry
from .state import State
from .vocab_bank import VocabBank
from config import CLEANED_SEARCH_WORD_FILE, VOCAB_BANK_DIR 

def main():
    word_list_path = Path(CLEANED_SEARCH_WORD_FILE)
    if not word_list_path.exists():
        print(f"File not found: {word_list_path}")
        sys.exit(1)

    vocab_bank = VocabBank(VOCAB_BANK_DIR)
    state = State(vocab_bank)

    all_commands = [
        AcceptCommand,
        RejectCommand,
        UndoCommand,
        QuitCommand,
    ]

    with state:  # Use context manager to ensure state is saved
        while True:
            current_word = state.current_word()
            if not current_word:
                print("All words processed!")
                break

            # Skip if word is already fully processed
            if state.has_processed_word(current_word):
                continue

            # Get dictionary data for the word
            word = look_up(current_word)
            if not word:
                print(f"Skipping '{current_word}' because no exact match was found.")
                state.skip_word(current_word)
                continue
            
            # Keep processing entries until the whole word is handled
            while current_word is state.current_word() and not state.has_processed_word(current_word):
                # Show each unprocessed entry
                for entry in word.entries:
                    if not state.has_processed_entry(entry.id):
                        handle_command_input(entry, word, all_commands, vocab_bank, state)
                        break  # Process one entry at a time to handle undos properly

if __name__ == "__main__":
    main()
