from spanish_flashcard_builder.config import anki_config, paths

from .generator import AnkiDeckGenerator


def main() -> None:
    """Generate the Anki deck."""
    generator = AnkiDeckGenerator(
        deck_name=anki_config.deck_name,
        deck_id=anki_config.deck_id,
    )

    generator.generate()
    print(f"Deck generated successfully at {paths.deck_file}")


if __name__ == "__main__":
    main()
