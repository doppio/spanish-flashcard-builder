from .generator import ContentGenerator


def main() -> None:
    """Main entry point for content generation."""
    generator = ContentGenerator()
    if not generator.process_all_pending():
        print("No terms to process")


if __name__ == "__main__":
    main()
