from typing import List, Dict

class DictionaryTerm:
    """Represents a word with its dictionary entries."""
    
    def __init__(self, headword: str, entries: List['DictionaryEntry']) -> None:
        self.headword = headword
        self.entries = entries 

class DictionaryEntry:
    """Represents a single dictionary entry from Merriam-Webster."""

    def __init__(self, raw_entry: Dict) -> None:
        self.id = raw_entry['meta']['id']
        self.headword = raw_entry.get('hwi', {}).get('hw', '').replace('*', '')
        self.part_of_speech = raw_entry.get('fl', '')
        self.definitions = raw_entry.get('shortdef', [])
        self.raw_data = raw_entry

    def __str__(self) -> str:
        defs = '\n  '.join(self.definitions)
        return f"{self.headword} ({self.part_of_speech})\n  {defs}"