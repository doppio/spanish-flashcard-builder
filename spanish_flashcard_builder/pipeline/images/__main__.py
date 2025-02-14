import logging

from .selector import ImageSelector

logging.basicConfig(level=logging.INFO)


def main() -> None:
    """Main entry point for the image selector."""
    selector = ImageSelector()
    selector.process_terms()


if __name__ == "__main__":
    main()
