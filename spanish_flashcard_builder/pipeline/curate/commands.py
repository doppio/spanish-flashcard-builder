import sys
from typing import Optional

from .models import DictionaryEntry, DictionaryTerm
from .state import State
from .vocab_bank import VocabBank


class Command:
    key: Optional[str] = None
    help_text: Optional[str] = None

    def __init__(
        self,
        entry: Optional[DictionaryEntry] = None,
        vocab_bank: Optional[VocabBank] = None,
        state: Optional[State] = None,
        word: Optional[DictionaryTerm] = None,
    ) -> None:
        self.entry = entry
        self.vocab_bank = vocab_bank
        self.state = state
        self.word = word

    def execute(self) -> None:
        raise NotImplementedError("Subclasses must implement the execute method.")


class AcceptCommand(Command):
    key = "y"
    help_text = "yes"

    def execute(self) -> None:
        if not self.vocab_bank or not self.entry or not self.state:
            raise ValueError("Missing required dependencies for AcceptCommand")
        self.vocab_bank.save_entry(self.entry)
        self.state.commit_entry()


class RejectCommand(Command):
    key = "n"
    help_text = "no"

    def execute(self) -> None:
        if not self.state:
            raise ValueError("Missing required state for RejectCommand")
        self.state.commit_entry()


class UndoCommand(Command):
    key = "u"
    help_text = "undo previous"

    def execute(self) -> None:
        if not self.state or not self.vocab_bank:
            raise ValueError("Missing required dependencies for UndoCommand")
        self.state.undo()
        current_entry = self.state.current_entry()
        self.vocab_bank.delete_entry(current_entry.id)


class QuitCommand(Command):
    key = "q"
    help_text = "quit program"

    def execute(self) -> None:
        print("Quitting...")
        sys.exit(0)


all_commands = [AcceptCommand, RejectCommand, UndoCommand, QuitCommand]
