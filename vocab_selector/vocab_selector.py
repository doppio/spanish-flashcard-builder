#!/usr/bin/env python3

import sys
import spacy

from config import VOCAB_DIR
from .commands import all_commands, QuitCommand
from .input_handler import handle_command_input
from .models import VocabWord
from .mw_api import get_mw_data
from .spacy import canonicalize_word
from .state import State
from .storage import VocabStorage

def interactive_loop():
    """Main interactive loop for processing vocabulary words"""
    state = State()
    storage = VocabStorage(VOCAB_DIR)

    print(f"Press '{QuitCommand.key}' at any time to quit.")

    try:
        while not state.is_complete():
            raw_word = state.current_word()
            word = canonicalize_word(raw_word)
            
            if not word:
                state.advance_to_next()
                continue

            # Skip words with no valid MW data
            mw_data = get_mw_data(word)
            if not mw_data:
                state.advance_to_next()
                continue

            vocab_word = VocabWord(word, mw_data)
            handle_command_input(all_commands, vocab_word, storage, state)

        print("\nCompleted processing the vocabulary list.")
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Saving state...")
        state._save()
        sys.exit(0)


if __name__ == "__main__":
    interactive_loop()
