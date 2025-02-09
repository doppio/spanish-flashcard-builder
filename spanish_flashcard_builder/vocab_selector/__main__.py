#!/usr/bin/env python3

from pathlib import Path
import sys

from .commands import AcceptCommand, RejectCommand, UndoCommand, QuitCommand
from .input_handler import handle_command_input
from .state import State
from .vocab_bank import VocabBank
from spanish_flashcard_builder.config import CLEANED_SEARCH_WORD_FILE, VOCAB_BANK_DIR

def main() -> None:
    word_list_path = Path(CLEANED_SEARCH_WORD_FILE)
    if not word_list_path.exists():
        print(f"File not found: {word_list_path}")
        sys.exit(1)

    vocab_bank = VocabBank(VOCAB_BANK_DIR)
    state = State()

    all_commands = [
        AcceptCommand,
        RejectCommand,
        UndoCommand,
        QuitCommand,
    ]

    with state:  # Use context manager to ensure state is saved
        while True:
            handle_command_input(state.current_entry(), state.current_term(), all_commands, vocab_bank, state)
        
if __name__ == "__main__":
    main()
