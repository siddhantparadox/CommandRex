from commandrex.nlp_advanced import AdvancedNLP
from commandrex.nlp import process_command

def test_advanced_nlp():
    nlp = AdvancedNLP()
    
    print("Matcher patterns:")
    for name, patterns in nlp.matcher._patterns.items():
        print(f"  {name}: {patterns}")
    print()

    test_commands = [
        "Create a new folder called Project Files",
        "Delete the file named old_report.txt",
        "Show me all running processes",
        "Make a directory named Backups",
        "Remove the folder temp_data",
        "List all files in the current directory",
        "What's the current time?",
        "Open notepad",
    ]

    print("Testing AdvancedNLP directly:")
    print("-----------------------------")
    for command in test_commands:
        doc = nlp.nlp(command)
        matches = nlp.matcher(doc)
        
        print(f"Command: {command}")
        print(f"Tokens: {[token.text for token in doc]}")
        print(f"Matches: {matches}")
        
        result = nlp.process_command(command)
        print(f"Interpretation: {result}")
        
        # Debug print for _interpret_match method
        if matches:
            match_id, start, end = matches[0]
            span = doc[start:end]
            debug_interpret = nlp._interpret_match(span)
            print(f"Debug _interpret_match: {debug_interpret}")
        
        print()

    print("\nTesting process_command (combined AdvancedNLP and Claude API):")
    print("--------------------------------------------------------------")
    for command in test_commands:
        result = process_command(command)
        print(f"Command: {command}")
        print(f"Windows Command: {result}")
        print()

if __name__ == "__main__":
    test_advanced_nlp()