class Word:
    """
    Represents a word with its dictionary entries.
    A single word can have multiple entries (e.g., different parts of speech).
    """
    def __init__(self, search_word, entries):
        self.search_word = search_word
        self.entries = entries 

class DictionaryEntry:
    """
    Represents a single dictionary entry from Merriam-Webster.
    One word can have multiple entries (e.g., "bear" as noun vs verb).
    """
    def __init__(self, raw_entry):
        self.id = raw_entry['meta']['id']
        self.headword = raw_entry.get('hwi', {}).get('hw', '').replace('*', '')
        self.part_of_speech = raw_entry.get('fl', '')
        self.definitions = raw_entry.get('shortdef', [])
        self.raw_data = raw_entry

    def __str__(self):
        defs = '\n  '.join(self.definitions)
        return f"{self.headword} ({self.part_of_speech})\n  {defs}"