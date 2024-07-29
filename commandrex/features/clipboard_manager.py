# File: commandrex/features/clipboard_manager.py

import pyperclip
import re

class ClipboardManager:
    def __init__(self):
        self.clipboard_history = []
        self.max_history = 10

    def copy(self, text):
        """Copy text to clipboard and add to history."""
        pyperclip.copy(text)
        self.clipboard_history.append(text)
        if len(self.clipboard_history) > self.max_history:
            self.clipboard_history.pop(0)

    def paste(self):
        """Paste the most recent clipboard entry."""
        return self.clipboard_history[-1] if self.clipboard_history else ""

    def list_history(self):
        """Return a formatted string of clipboard history."""
        if not self.clipboard_history:
            return "Clipboard history is empty."
        return "\n".join(f"{i+1}. {text[:50]}..." for i, text in enumerate(reversed(self.clipboard_history)))

    def clear_history(self):
        """Clear the clipboard history."""
        self.clipboard_history.clear()
        return "Clipboard history cleared."

clipboard_manager = ClipboardManager()

def process_clipboard_command(command):
    """Process clipboard-related commands."""
    copy_match = re.match(r'copy\s+"(.+)"', command, re.IGNORECASE)
    if copy_match:
        text = copy_match.group(1)
        clipboard_manager.copy(text)
        return f'Copied to clipboard: "{text[:50]}..."'

    if command.lower() == 'paste':
        return clipboard_manager.paste()

    if command.lower() == 'clipboard history':
        return clipboard_manager.list_history()

    if command.lower() == 'clear clipboard history':
        return clipboard_manager.clear_history()

    return None