import os
import json
from typing import Dict, List
from spanish_flashcard_builder.config import paths

# ANSI escape codes
BOLD_START = '\033[1m'
BOLD_END = '\033[0m'

# Constants for repeated strings
HEADER_LINE = "-" * 80
COMPONENT_EXISTS_SYMBOL = "✅"
COMPONENT_MISSING_SYMBOL = "❌"
HEADER_FORMAT = "{:<20} "
COMPONENT_FORMAT = "{:<12}"

# Define components to check using config values
COMPONENTS = {
    'Dictionary': paths.dictionary_entry_filename,
    'Audio': paths.pronunciation_filename,
    'Flashcard': paths.augmented_term_filename,
    'Image': paths.image_filename
}

def bold(text: str) -> str:
    """Wrap text in bold ANSI codes."""
    return f"{BOLD_START}{text}{BOLD_END}"

def check_component(vocab_path: str, filename: str) -> bool:
    """Check if a component exists for a vocabulary item."""
    return os.path.exists(os.path.join(vocab_path, filename))

def get_vocab_dirs() -> List[str]:
    """Get sorted list of vocabulary directories."""
    return sorted([d for d in os.listdir(paths.terms_dir) 
                  if os.path.isdir(os.path.join(paths.terms_dir, d))])

def main() -> None:
    """Display the manifest of vocabulary entries and their components."""
    vocab_dirs = get_vocab_dirs()
    
    if not vocab_dirs:
        print("No vocabulary entries found.")
        return
        
    print(HEADER_LINE)
    print(f"Found {len(vocab_dirs)} vocabulary entries:")
    print(HEADER_LINE)
    
    # Print header
    print(HEADER_FORMAT.format("Word"), end="")
    for component in COMPONENTS:
        print(COMPONENT_FORMAT.format(component), end="")
    print()
    print(HEADER_LINE)
    
    # Print each word's status
    for vocab_dir in vocab_dirs:
        vocab_path = os.path.join(paths.terms_dir, vocab_dir)
        print(HEADER_FORMAT.format(vocab_dir), end="")
        
        for component, filename in COMPONENTS.items():
            symbol = COMPONENT_EXISTS_SYMBOL if check_component(vocab_path, filename) else COMPONENT_MISSING_SYMBOL
            print(COMPONENT_FORMAT.format(symbol), end="")
        print()

if __name__ == "__main__":
    main()
