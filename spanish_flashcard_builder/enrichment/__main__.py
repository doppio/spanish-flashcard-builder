from .enricher import VocabEnricher

def main():
    enricher = VocabEnricher()
    if not enricher.process_all_pending():
        print("No words to process!")
    
if __name__ == "__main__":
    main()
