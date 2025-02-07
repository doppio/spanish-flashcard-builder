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

def handle_command_input(available_commands, vocab_word, storage, state):
    """
    Handle command input loop with specific available commands
    """
    print_mw_summary(vocab_word.word, vocab_word.mw_data)
    print(f"\nDo you want to learn this word?")
    print(f"({format_help_text(available_commands)})")
    
    while True:
        choice = get_key_press()
        matching_command = next(
            (cmd for cmd in available_commands if cmd.key == choice),
            None
        )
        
        if matching_command is None:
            print(f"Invalid input. Available commands: {format_help_text(available_commands)}")
            continue
            
        command = matching_command(vocab_word, storage, state)
        command.execute()
        return 