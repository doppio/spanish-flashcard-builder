import argparse
import glob
import os
from typing import Dict, List, Optional

from spanish_flashcard_builder.config import paths

TARGETS: Dict[str, Optional[str]] = {
    "flashcard-data": paths.augmented_term_filename,
    "image": "*.png",
    "audio": "*.mp3",
    "dictionary-entry": paths.dictionary_entry_filename,
    "history": paths.curator_history,
    "sanitized-vocab": paths.sanitized_vocab,
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


def _clean_audio() -> None:
    """Remove audio files."""
    audio_files = glob.glob(os.path.join(paths.terms_dir, "*", "*.mp3"))
    _remove_files(audio_files)


def _clean_images() -> None:
    """Remove image files."""
    image_files = glob.glob(os.path.join(paths.terms_dir, "*", "*.jpg"))
    _remove_files(image_files)


def _clean_flashcard_data() -> None:
    """Remove generated flashcard data."""
    data_files = glob.glob(os.path.join(paths.terms_dir, "*", "*.json"))
    _remove_files(data_files)


def _clean_history() -> None:
    """Remove curator history."""
    if os.path.exists(paths.curator_history):
        _remove_files([paths.curator_history])


def _clean_sanitized_vocab() -> None:
    """Remove sanitized vocabulary."""
    if os.path.exists(paths.sanitized_vocab):
        _remove_files([paths.sanitized_vocab])


def clean(component: str) -> None:
    """Remove files based on target type.

    Args:
        component: The target type to remove. Valid options:
            - "audio": Remove audio files
            - "image": Remove image files
            - "flashcard-data": Remove generated flashcard data
            - "history": Remove curator history
            - "sanitized-vocab": Remove sanitized vocabulary
            - "all": Remove all generated files
    """
    if component == "all":
        _clean_audio()
        _clean_images()
        _clean_flashcard_data()
        _clean_history()
        _clean_sanitized_vocab()
        return

    component_cleaners = {
        "audio": _clean_audio,
        "image": _clean_images,
        "flashcard-data": _clean_flashcard_data,
        "history": _clean_history,
        "sanitized-vocab": _clean_sanitized_vocab,
    }

    if component not in component_cleaners:
        print(f"Unknown component: {component}")
        print("Valid components:", ", ".join(component_cleaners.keys()))
        return

    component_cleaners[component]()


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
