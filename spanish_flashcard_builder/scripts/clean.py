import argparse
import glob
import os
from typing import Dict, List, Optional

from spanish_flashcard_builder.config import paths

TARGETS: Dict[str, Optional[str]] = {
    "flashcard-data": paths.flashcard_filename,
    "dictionary-entry": paths.dictionary_entry_filename,
    "images": "*.png",
    "audio": "*.mp3",
    "all": None,  # Special case handled in clean function
}


def _remove_files(files: List[str]) -> None:
    """Remove a list of files."""
    for file in files:
        try:
            os.remove(file)
            print(f"Removed {file}")
        except OSError as e:
            print(f"Error removing {file}: {e}")


def clean(component: str) -> None:
    """Remove files based on target type.

    Args:
        component: The target type to remove. Valid options:
            - "audio": Remove audio files
            - "images": Remove image files
            - "dictionary-entries": Remove dictionary entries
            - "flashcard-data": Remove generated flashcard data
            - "all": Remove all generated files
    """
    if component == "all":
        for target, _pattern in TARGETS.items():
            if target != "all":
                clean(target)
        return

    if component not in TARGETS:
        print(f"Unknown component: {component}")
        print("Valid components:", ", ".join(TARGETS.keys()))
        return

    pattern = TARGETS[component]
    if pattern is None:
        return
    files = glob.glob(os.path.join(paths.terms_dir, "*", pattern))
    _remove_files(files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove component data")
    parser.add_argument(
        "component",
        choices=list(TARGETS.keys()),
        help="Target type to remove",
    )
    parser.add_argument(
        "--force", "-f", action="store_true", help="Skip confirmation prompt"
    )
    args = parser.parse_args()

    if (
        args.force
        or input(
            f"This will remove all {args.component} files. Are you sure? (y/N): "
        ).lower()
        == "y"
    ):
        clean(args.component)
    else:
        print("Operation cancelled")
