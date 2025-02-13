from typing import List, Type

from spanish_flashcard_builder.utils import get_key_press

from .commands import Command
from .models import DictionaryEntry, DictionaryTerm
from .mw_api import log_mw_data_summary
from .state import State
from .vocab_bank import VocabBank


def format_help_text(commands: List[Type[Command]]) -> str:
    """Formats help text for a list of commands."""

    return ", ".join(f"{cmd.key}={cmd.help_text}" for cmd in commands)


def handle_command_input(
    entry: DictionaryEntry,
    word: DictionaryTerm,
    commands: List[Type[Command]],
    vocab_bank: VocabBank,
    state: State,
) -> None:
    """Handles command input loop with specific available commands."""

    log_mw_data_summary(entry.headword, [entry.raw_data])

    total_entries = len(word.entries)
    if len(word.entries) > 1:
        current_entry_idx = word.entries.index(entry) + 1
        print(f"[Meaning {current_entry_idx} of {total_entries}]")

    print("\nDo you want to learn this word?")
    print(f"({format_help_text(commands)})")

    while True:
        choice = get_key_press()
        matching_command = next((cmd for cmd in commands if cmd.key == choice), None)

        if matching_command is None:
            print(f"Invalid input. Available commands: {format_help_text(commands)}")
            continue

        command = matching_command(entry, vocab_bank, state, word)
        command.execute()
        return
