#!/usr/bin/env python3

import sys

from spanish_flashcard_builder.config import paths

from .commands import AcceptCommand, QuitCommand, RejectCommand, UndoCommand
from .input_handler import handle_command_input
from .state import State
from .vocab_bank import VocabBank


def main() -> None:
    word_list_path = paths.cleaned_vocab
    if not word_list_path.exists():
        print(f"File not found: {word_list_path}")
        sys.exit(1)

    vocab_bank = VocabBank(paths.terms_dir)
    state = State()

    all_commands = [
        AcceptCommand,
        RejectCommand,
        UndoCommand,
        QuitCommand,
    ]

    with state:  # Use context manager to ensure state is saved
        while True:
            handle_command_input(
                state.current_entry(),
                state.current_term(),
                all_commands,
                vocab_bank,
                state,
            )


if __name__ == "__main__":
    main()
