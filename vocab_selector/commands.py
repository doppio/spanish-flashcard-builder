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
        self.state.accept_entry(self.entry, self.word)

class RejectCommand(Command):
    key = 'n'
    help_text = "reject"

    def execute(self):
        self.state.reject_entry(self.entry, self.word)

class UndoCommand(Command):
    key = 'u'
    help_text = "undo previous"

    def execute(self):
        if not self.state.can_undo():
            print("No previous entry to undo.")
            return
            
        prev_entry = self.state.undo()
        if prev_entry:
            self.vocab_bank.remove(prev_entry.id)

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