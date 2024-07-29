import spacy
from spacy.matcher import Matcher
from typing import Dict, Any

class AdvancedNLP:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.matcher = Matcher(self.nlp.vocab)
        self._setup_matcher()

    def _setup_matcher(self):
        file_operation_pattern = [
            {"LEMMA": {"IN": ["create", "make", "delete", "remove"]}},
            {"OP": "*"},
            {"LOWER": {"IN": ["file", "folder", "directory"]}},
            {"OP": "*"},
            {"POS": {"IN": ["PROPN", "NOUN", "ADJ"]}, "OP": "+"}
        ]
        self.matcher.add("FILE_OPERATION", [file_operation_pattern])

    def process_command(self, user_input: str) -> Dict[str, Any]:
        doc = self.nlp(user_input)
        matches = self.matcher(doc)

        print(f"Debug - process_command matches: {matches}")  # Debug print

        if matches:
            _, start, end = matches[-1]  # Use the last match
            span = doc[start:end]
            return self._interpret_match(span)

        return self._fallback_interpretation(doc)

    def _interpret_match(self, span: spacy.tokens.Span) -> Dict[str, Any]:
        print(f"Debug - _interpret_match called with span: {span}")  # Debug print

        operation = span[0].lemma_.lower()
        target_type = next((token.text.lower() for token in span if token.text.lower() in ["file", "folder", "directory"]), None)
        name = " ".join([token.text for token in span if token.pos_ in ["PROPN", "NOUN", "ADJ"] and token.text.lower() not in ["file", "folder", "directory", "new"]])
        
        result = {
            "operation": "create" if operation in ["create", "make"] else "delete",
            "target_type": "directory" if target_type in ["folder", "directory"] else "file",
            "name": name.strip(),
            "unmatched": False
        }
        print(f"Debug - _interpret_match result: {result}")  # Debug print
        return result

    def _fallback_interpretation(self, doc: spacy.tokens.Doc) -> Dict[str, Any]:
        verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]
        nouns = [token.text for token in doc if token.pos_ == "NOUN"]
        
        return {
            "operation": verbs[0] if verbs else None,
            "target": nouns[0] if nouns else None,
            "unmatched": True
        }

def construct_windows_command(interpretation: Dict[str, Any]) -> str:
    """
    Construct a Windows command based on the AdvancedNLP interpretation.
    """
    if interpretation['operation'] == 'create':
        if interpretation['target_type'] == 'directory':
            return f"mkdir \"{interpretation['name']}\""
        elif interpretation['target_type'] == 'file':
            return f"type nul > \"{interpretation['name']}\""
    elif interpretation['operation'] in ['delete', 'remove']:
        if interpretation['target_type'] == 'directory':
            return f"rmdir \"{interpretation['name']}\""
        elif interpretation['target_type'] == 'file':
            return f"del \"{interpretation['name']}\""
    
    return ""

# Example usage
if __name__ == "__main__":
    nlp_processor = AdvancedNLP()
    test_commands = [
        "Create a new folder called Project Files",
        "Delete the file named old_report.txt",
        "Show me all running processes",
        "Remove the folder temp_data"
    ]
    
    for command in test_commands:
        result = nlp_processor.process_command(command)
        print(f"Command: {command}")
        print(f"Interpretation: {result}")
        windows_command = construct_windows_command(result)
        print(f"Windows Command: {windows_command}\n")