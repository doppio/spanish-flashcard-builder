import os
from config import VOCAB_BANK_DIR

def remove_flashcard_data():
    """Remove all flashcard_data.json files from vocabulary entries."""
    count = 0
    
    # Ensure the vocab directory exists
    if not os.path.exists(VOCAB_BANK_DIR):
        print(f"Vocabulary directory not found: {VOCAB_BANK_DIR}")
        return
    
    # Iterate through all word folders
    for folder_name in os.listdir(VOCAB_BANK_DIR):
        folder_path = os.path.join(VOCAB_BANK_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue
            
        flashcard_path = os.path.join(folder_path, "flashcard_data.json")
        if os.path.exists(flashcard_path):
            try:
                os.remove(flashcard_path)
                count += 1
                print(f"Removed flashcard data for: {folder_name}")
            except Exception as e:
                print(f"Error removing flashcard data for {folder_name}: {e}")
    
    print(f"\nRemoved {count} flashcard data files")

if __name__ == "__main__":
    response = input("This will remove all flashcard data files. Are you sure? (y/N): ")
    if response.lower() == 'y':
        remove_flashcard_data()
    else:
        print("Operation cancelled")