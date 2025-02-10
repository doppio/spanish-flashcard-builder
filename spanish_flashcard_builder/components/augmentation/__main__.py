from .augmentor import VocabAugmentor


def main() -> None:
    augmentor = VocabAugmentor()
    if not augmentor.process_all_pending():
        print("No words to process!")


if __name__ == "__main__":
    main()
