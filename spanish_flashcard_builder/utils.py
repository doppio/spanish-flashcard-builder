import os
import sys
from typing import Any, cast


def get_key_press() -> str:
    """Gets single keypress from the user."""
    if os.name == "nt":
        import msvcrt

        msvcrt_any = cast(Any, msvcrt)
        return cast(str, msvcrt_any.getch().decode())
    else:
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
