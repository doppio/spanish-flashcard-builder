import sys

class Command:
    key = None
    help_text = None
    
    def __init__(self, entry=None, vocab_bank=None, state=None, word=None):
        self.entry = entry
        self.vocab_bank = vocab_bank
        self.state = state
        self.word = word
    
    def execute(self):
        raise NotImplementedError("Subclasses must implement the execute method.")

class AcceptCommand(Command):
    key = 'y'
    help_text = "accept"

    def execute(self):
        self.vocab_bank.save_entry(self.entry)
        self.state.commit_entry()

class RejectCommand(Command):
    key = 'n'
    help_text = "reject"

    def execute(self):
        self.state.commit_entry()

class UndoCommand(Command):
    key = 'u'
    help_text = "undo previous"

    def execute(self):
        self.state.undo()
        self.vocab_bank.delete_entry(self.state.current_entry().id)

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