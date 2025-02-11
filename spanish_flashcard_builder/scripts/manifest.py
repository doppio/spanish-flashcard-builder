import os
from pathlib import Path
from typing import Callable, List, Union

from spanish_flashcard_builder.config import paths

# ANSI escape codes
BOLD_START = "\033[1m"
BOLD_END = "\033[0m"

# Constants for repeated strings
HEADER_LINE = "-" * 80
PIPELINE_EXISTS_SYMBOL = "✅"
PIPELINE_MISSING_SYMBOL = "❌"
HEADER_FORMAT = "{:<20} "
PIPELINE_FORMAT = "{:<12}"

# Define pipeline stages to check using config values
PIPELINE_STAGES = {
    "Dictionary": paths.dictionary_entry_filename,
    "Flashcard": paths.augmented_term_filename,
}


def bold(text: str) -> str:
    """Wrap text in bold ANSI codes."""
    return f"{BOLD_START}{text}{BOLD_END}"


def check_pipeline_stage(vocab_path: str, filename: str) -> bool:
    """Check if a pipeline stage exists for a vocabulary item."""
    return os.path.exists(os.path.join(vocab_path, filename))


def check_media_stage(
    vocab_path: Path, get_filename_func: Callable[[Path], Union[str, Path]]
) -> bool:
    """Check if a media stage exists using the filename function."""
    try:
        return (vocab_path / get_filename_func(vocab_path)).exists()
    except Exception:
        return False


def get_vocab_dirs() -> List[str]:
    """Get sorted list of vocabulary directories."""
    return sorted(
        [
            d
            for d in os.listdir(paths.terms_dir)
            if os.path.isdir(os.path.join(paths.terms_dir, d))
        ]
    )


def _is_valid_file(file_path: str) -> bool:
    """Check if file exists and is not empty."""
    try:
        return os.path.exists(file_path) and os.path.getsize(file_path) > 0
    except OSError:
        return False


def main() -> None:
    """Display the manifest of vocabulary entries and their pipeline stages."""
    vocab_dirs = get_vocab_dirs()

    if not vocab_dirs:
        print("No vocabulary entries found.")
        return

    print(HEADER_LINE)
    print(f"Found {len(vocab_dirs)} vocabulary entries:")
    print(HEADER_LINE)

    # Print header
    print(HEADER_FORMAT.format("Word"), end="")
    print(PIPELINE_FORMAT.format("Dictionary"), end="")
    print(PIPELINE_FORMAT.format("Flashcard"), end="")
    print(PIPELINE_FORMAT.format("Audio"), end="")
    print(PIPELINE_FORMAT.format("Image"), end="")
    print()
    print(HEADER_LINE)

    # Print each word's status
    for vocab_dir in vocab_dirs:
        vocab_path = Path(os.path.join(paths.terms_dir, vocab_dir))
        print(HEADER_FORMAT.format(vocab_dir), end="")

        # Check regular pipeline stages
        for _, filename in PIPELINE_STAGES.items():
            symbol = (
                PIPELINE_EXISTS_SYMBOL
                if check_pipeline_stage(str(vocab_path), filename)
                else PIPELINE_MISSING_SYMBOL
            )
            print(PIPELINE_FORMAT.format(symbol), end="")

        # Check audio
        symbol = (
            PIPELINE_EXISTS_SYMBOL
            if check_media_stage(vocab_path, paths.get_pronunciation_filename)
            else PIPELINE_MISSING_SYMBOL
        )
        print(PIPELINE_FORMAT.format(symbol), end="")

        # Check image
        symbol = (
            PIPELINE_EXISTS_SYMBOL
            if check_media_stage(vocab_path, paths.get_image_filename)
            else PIPELINE_MISSING_SYMBOL
        )
        print(PIPELINE_FORMAT.format(symbol), end="")
        print()


if __name__ == "__main__":
    main()
