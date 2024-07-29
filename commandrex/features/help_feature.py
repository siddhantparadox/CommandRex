# File: commandrex/features/help_feature.py

def get_help_text():
    """
    Returns a string containing help information for CommandRex.
    """
    help_text = """
CommandRex Help:

CommandRex is a natural language command-line interface that translates your plain English commands into Windows commands.

Available Commands:
1. File and Directory Operations:
   - "Show me all files in the current directory"
   - "Create a new folder called [folder_name]"
   - "Delete the file [file_name]"

2. System Information:
   - "Show me system information"
   - "What's my current working directory?"
   - "Display the date and time"

3. Process Management:
   - "Show me all running processes"
   - "List all Python processes"

4. Network Operations:
   - "What's my IP address?"
   - "Ping google.com"

5. General Commands:
   - "exit" : Exit CommandRex

6. Clipboard Operations:
       - "copy \"text to copy\"" : Copy text to clipboard
       - "paste" : Paste the most recent clipboard entry
       - "clipboard history" : Show clipboard history
       - "clear clipboard history" : Clear the clipboard history

Tips:
- Use natural language to describe what you want to do.
- If a command doesn't work, try rephrasing it.
- Use the up and down arrow keys to navigate through command history.
- Use tab for auto-completion of file and directory names.

For more information, visit: [Your project website or documentation URL]
"""
    return help_text

def process_help_command(command):
    """
    Processes help-related commands and returns appropriate responses.
    """
    command = command.lower().strip()
    if command == "help" or command == "show help":
        return get_help_text()
    elif command.startswith("help "):
        # TODO: Implement specific help topics
        return "Specific help topics are not yet implemented. Use 'help' for general information."
    else:
        return None