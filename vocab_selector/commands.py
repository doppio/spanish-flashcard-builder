import sys

from .input_handler import handle_command_input
from .models import VocabWord
from .mw_api import print_mw_summary

class Command:
    key = None
    help_text = None
    
    def __init__(self, vocab_word=None, storage=None, state=None):
        self.vocab_word = vocab_word
        self.storage = storage
        self.state = state
    
    def execute(self):
        raise NotImplementedError("Subclasses must implement the execute method.")

class AcceptCommand(Command):
    key = 'y'
    help_text = "accept word"

    def execute(self):
        self.storage.save(self.vocab_word)
        self.state.accept_current_word()
        self.state.advance_to_next()

class RejectCommand(Command):
    key = 'n'
    help_text = "reject word"

    def execute(self):
        self.state.reject_current_word()
        self.state.advance_to_next()

class UndoCommand(Command):
    key = 'u'
    help_text = "undo previous"

    def execute(self):
        if not self.state.can_undo():
            print("No previous entry to undo.")
            return
            
        prev_word = self.state.undo()
        if prev_word:
            self.storage.remove(prev_word)

class QuitCommand(Command):
    key = 'q'
    help_text = "quit program"

    def execute(self):
        print("Quitting...")
        sys.exit(0)

def format_help_text(commands):
    """Format help text for a list of commands"""
    return ", ".join(f"{cmd.key}={cmd.help_text}" for cmd in commands)

all_commands = [
    AcceptCommand,
    RejectCommand,
    UndoCommand,
    QuitCommand
] 