import os
import sys

from .mw_api import print_mw_summary

def get_key_press():
    """Get a single keypress from the user"""
    if os.name == "nt":
        import msvcrt
        return msvcrt.getch().decode().lower()
    else:
        import tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch.lower()

def format_help_text(commands):
    """Format help text for a list of commands"""
    return ", ".join(f"{cmd.key}={cmd.help_text}" for cmd in commands)

def handle_command_input(entry, word, commands, vocab_bank, state):
    """
    Handle command input loop with specific available commands
    """

    print_mw_summary(entry.headword, [entry.raw_data])
    
    total_entries = len(word.entries)
    if len(word.entries) > 1:
        current_entry_idx = word.entries.index(entry) + 1
        print(f"[Meaning {current_entry_idx} of {total_entries}]")

    print(f"\nDo you want to learn this word?")
    print(f"({format_help_text(commands)})")
    
    while True:
        choice = get_key_press()
        matching_command = next(
            (cmd for cmd in commands if cmd.key == choice),
            None
        )
        
        if matching_command is None:
            print(f"Invalid input. Available commands: {format_help_text(commands)}")
            continue
            
        command = matching_command(entry, vocab_bank, state, word)
        command.execute()
        return 