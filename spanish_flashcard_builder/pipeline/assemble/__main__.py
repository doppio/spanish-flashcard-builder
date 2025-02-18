from spanish_flashcard_builder.config import anki_config, paths

from .assembler import AnkiDeckAssembler


def main() -> None:
    """Assemble the Anki deck."""
    assembler = AnkiDeckAssembler(
        deck_name=anki_config.deck_name,
        deck_id=anki_config.deck_id,
    )

    assembler.assemble()
    print(f"Deck assembled successfully at {paths.deck_file}")


if __name__ == "__main__":
    main()
