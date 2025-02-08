import sys
from typing import Optional

class Command:
    key: Optional[str] = None
    help_text: Optional[str] = None
    
    def __init__(self, entry=None, vocab_bank=None, state=None, word=None) -> None:
        self.entry = entry
        self.vocab_bank = vocab_bank
        self.state = state
        self.word = word
    
    def execute(self) -> None:
        raise NotImplementedError("Subclasses must implement the execute method.")

class AcceptCommand(Command):
    key = 'y'
    help_text = "yes"

    def execute(self) -> None:
        self.vocab_bank.save_entry(self.entry)
        self.state.commit_entry()

class RejectCommand(Command):
    key = 'n'
    help_text = "no"

    def execute(self) -> None:
        self.state.commit_entry()

class UndoCommand(Command):
    key = 'u'
    help_text = "undo previous"

    def execute(self) -> None:
        self.state.undo()
        self.vocab_bank.delete_entry(self.state.current_entry().id)

class QuitCommand(Command):
    key = 'q'
    help_text = "quit program"

    def execute(self) -> None:
        print("Quitting...")
        sys.exit(0)

all_commands = [
    AcceptCommand,
    RejectCommand,
    UndoCommand,
    QuitCommand
] 