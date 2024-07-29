import customtkinter as ctk
import tkinter as tk
from tkinter import font as tkfont
import subprocess
import re
import os
import logging
from commandrex.nlp import process_command
from commandrex.features.tab_completion import complete
from commandrex.features.help_feature import process_help_command
from commandrex.features.clipboard_manager import process_clipboard_command
from commandrex.features.status_bar import StatusBar

# Set up logging to file
logging.basicConfig(filename='commandrex_debug.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TerminalGUI:
    def __init__(self, master):
        self.master = master
        master.title("CommandRex Terminal")
        master.geometry("800x600")

        # Set CustomTkinter appearance mode and color theme
        self.current_mode = "dark"
        ctk.set_appearance_mode(self.current_mode)
        ctk.set_default_color_theme("blue")

        # Create a custom font using CustomTkinter's CTkFont
        self.custom_font = ctk.CTkFont(family="Consolas", size=12)

        # Create main frame with glassmorphism effect
        self.main_frame = ctk.CTkFrame(master, corner_radius=20)
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Create text widget with glassmorphism effect
        self.terminal = ctk.CTkTextbox(self.main_frame, wrap="word", font=self.custom_font,
                                       corner_radius=10, border_width=2)
        self.terminal.pack(expand=True, fill='both', padx=10, pady=(10, 5))

        # Create status bar
        self.status_bar = StatusBar(self.main_frame, font=self.custom_font)

        # Configure tags for colored output
        self.configure_colors()

        # Initial prompt
        self.prompt = "CommandRex> "
        self.terminal.insert("end", self.prompt)
        
        # Bind keys
        self.terminal.bind("<Key>", self.on_key_press)
        self.terminal.bind("<Return>", self.process_input)
        self.terminal.bind("<BackSpace>", self.handle_backspace)
        self.terminal.bind("<Tab>", self.handle_tab)
        self.terminal.bind("<Up>", self.previous_command)
        self.terminal.bind("<Down>", self.next_command)

        # Initialize command history
        self.command_history = []
        self.history_index = 0

        # Create a frame for buttons with glassmorphism effect
        self.button_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.button_frame.pack(fill='x', padx=10, pady=5)

        # Add buttons
        self.clear_button = ctk.CTkButton(self.button_frame, text="Clear", command=self.clear_terminal,
                                          corner_radius=10)
        self.clear_button.pack(side='left', padx=5, pady=5)

        self.theme_button = ctk.CTkButton(self.button_frame, text="🌙 Night Mode" if self.current_mode == "light" else "☀️ Day Mode", 
                                          command=self.toggle_theme, corner_radius=10)
        self.theme_button.pack(side='left', padx=5, pady=5)

        self.help_button = ctk.CTkButton(self.button_frame, text="Help", command=self.show_help,
                                         corner_radius=10)
        self.help_button.pack(side='left', padx=5, pady=5)

        logger.debug("TerminalGUI initialized")

        # Schedule focus to be set after GUI is fully initialized
        self.master.after(100, self.set_focus)

    def configure_colors(self):
        if self.current_mode == "dark":
            self.terminal.configure(fg_color="#2B2B2B", text_color="#FFFFFF")
            self.terminal.tag_config("input", foreground="#4FC3F7")  # Light Blue
            self.terminal.tag_config("output", foreground="#FFFFFF")  # White
            self.terminal.tag_config("success", foreground="#66BB6A")  # Light Green
            self.terminal.tag_config("error", foreground="#FF5252")  # Light Red
            self.terminal.tag_config("warning", foreground="#FFD740")  # Amber
            self.terminal.tag_config("system", foreground="#B39DDB")  # Light Purple
        else:
            self.terminal.configure(fg_color="#F5F5F5", text_color="#000000")
            self.terminal.tag_config("input", foreground="#0277BD")  # Dark Blue
            self.terminal.tag_config("output", foreground="#000000")  # Black
            self.terminal.tag_config("success", foreground="#2E7D32")  # Dark Green
            self.terminal.tag_config("error", foreground="#C62828")  # Dark Red
            self.terminal.tag_config("warning", foreground="#F9A825")  # Dark Amber
            self.terminal.tag_config("system", foreground="#4527A0")  # Dark Purple

        # Configure status bar colors
        if self.current_mode == "dark":
            self.status_bar.frame.configure(fg_color="#1E1E1E")
            self.status_bar.label.configure(text_color="#B39DDB")  # Light Purple
        else:
            self.status_bar.frame.configure(fg_color="#E0E0E0")
            self.status_bar.label.configure(text_color="#4527A0")  # Dark Purple

    def toggle_theme(self):
        self.current_mode = "light" if self.current_mode == "dark" else "dark"
        ctk.set_appearance_mode(self.current_mode)
        self.theme_button.configure(text="🌙 Night Mode" if self.current_mode == "light" else "☀️ Day Mode")
        self.configure_colors()

    def set_focus(self):
        self.terminal.focus_set()
        self.terminal.mark_set("insert", "end-1c")

    def on_key_press(self, event):
        logger.debug(f"Key pressed: {event.keysym}")
        return "break" if event.keysym in ["Up", "Down", "Left", "Right"] else None

    def process_input(self, event):
        logger.debug("process_input method called")
        # Get the input from the last line
        input_text = self.terminal.get("end-1c linestart", "end-1c")
        if input_text.startswith(self.prompt):
            input_text = input_text[len(self.prompt):]  # Remove the prompt
        
        logger.debug(f"User input: {input_text}")

        # Add command to history
        if input_text.strip():
            self.command_history.append(input_text.strip())
            self.history_index = len(self.command_history)

        # Insert a newline
        self.terminal.insert("end", "\n")

        # Process the command
        if input_text.strip().lower() == "exit":
            logger.debug("Exit command received")
            self.master.quit()
        else:
            logger.debug(f"Executing command: {input_text}")
            self.execute_command(input_text)

        # Scroll to the end
        self.terminal.see("end")
        
        # Prevent the default behavior of the Return key
        return "break"

    def previous_command(self, event):
        if self.history_index > 0:
            self.history_index -= 1
            self.replace_current_input(self.command_history[self.history_index])
        return "break"

    def next_command(self, event):
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.replace_current_input(self.command_history[self.history_index])
        elif self.history_index == len(self.command_history) - 1:
            self.history_index = len(self.command_history)
            self.replace_current_input("")
        return "break"

    def handle_tab(self, event):
        # Get the current input
        input_text = self.terminal.get("end-1c linestart", "end-1c")
        if input_text.startswith(self.prompt):
            input_text = input_text[len(self.prompt):]  # Remove the prompt

        # Complete the input
        completed = complete(input_text)

        # Replace the current input with the completed text
        self.replace_current_input(completed)

        return "break"  # Prevent the default Tab behavior

    def handle_backspace(self, event):
        logger.debug("Backspace pressed")
        # Get the current input line
        input_start = self.terminal.index("end-1c linestart")
        input_end = self.terminal.index("end-1c")
        current_input = self.terminal.get(input_start, input_end)

        # Check if we're at or before the prompt
        if current_input == self.prompt or self.terminal.index("insert") <= f"{input_start}+{len(self.prompt)}c":
            logger.debug("Backspace prevented (at prompt)")
            return "break"  # Prevent deletion of or within the prompt
        
        logger.debug("Backspace allowed")
        return  # Allow normal backspace behavior

    def replace_current_input(self, new_input):
        input_start = self.terminal.index("end-1c linestart")
        input_end = self.terminal.index("end-1c")
        self.terminal.delete(input_start, input_end)
        self.terminal.insert(input_start, f"{self.prompt}{new_input}")

    def execute_command(self, user_input):
        print(f"Executing command: {user_input}")  # Console print for immediate feedback
        logger.debug(f"User input: {user_input}")

        # Display the user input
        self.terminal.insert("end", f"{self.prompt}{user_input}\n", "input")

        # Handle empty input
        if not user_input.strip():
            self.terminal.insert("end", "Please enter a command. Type 'help' for assistance.\n", "warning")
            self.terminal.insert("end", self.prompt, "system")
            return

        # Check if it's a help command
        help_output = process_help_command(user_input)
        if help_output:
            self.terminal.insert("end", help_output + "\n", "output")
            self.terminal.insert("end", self.prompt, "system")
            return
        
        # Check if it's a clipboard command
        clipboard_output = process_clipboard_command(user_input)
        if clipboard_output:
            self.terminal.insert("end", clipboard_output + "\n", "output")
            self.terminal.insert("end", self.prompt, "system")
            return

        windows_command = process_command(user_input)
        logger.debug(f"Processed command: {windows_command}")
        
        if windows_command:
            try:
                result = subprocess.run(windows_command, shell=True, text=True, capture_output=True)
                logger.debug(f"Command result: {result}")
                if result.returncode == 0:
                    output = result.stdout.strip()
                    if output:
                        # For 'net user' command, clean up the output
                        if windows_command.lower().startswith('net user'):
                            output = self.clean_net_user_output(output)
                        self.terminal.insert("end", f"{output}\n", "output")
                    else:
                        self.terminal.insert("end", "Command executed successfully (no output).\n", "success")
                else:
                    error_msg = f"Error: {result.stderr.strip()}"
                    self.terminal.insert("end", f"{error_msg}\n", "error")
            except subprocess.CalledProcessError as e:
                error_msg = f"Error executing command: {e}"
                logger.error(error_msg)
                self.terminal.insert("end", f"{error_msg}\n", "error")
        else:
            error_msg = "Sorry, I couldn't process that command. Could you try rephrasing it? Type 'help' for assistance."
            logger.warning(error_msg)
            self.terminal.insert("end", f"{error_msg}\n", "warning")
        
        # Update status bar after command execution
        self.status_bar.update_status()

        self.terminal.insert("end", self.prompt, "system")
        self.terminal.see("end")

    def clean_net_user_output(self, output):
        """Clean up the output of the 'net user' command."""
        lines = output.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip() and not line.startswith('The command completed')]
        return '\n'.join(cleaned_lines)

    def clean_dir_output(self, output):
        lines = output.split('\n')
        cleaned_lines = []
        for line in lines:
            # Use regex to match file/directory entries
            match = re.search(r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}\s+(PM|AM)\s+(<DIR>)?\s*([\w\s.-]+)$', line)
            if match:
                item_type = "Directory" if match.group(2) else "File"
                name = match.group(3).strip()
                cleaned_lines.append(f"{item_type}: {name}")
        return "\n".join(cleaned_lines)

    def clear_terminal(self):
        self.terminal.delete("1.0", "end")
        self.terminal.insert("end", self.prompt)

    def show_help(self):
        help_text = process_help_command("help")
        self.terminal.insert("end", help_text + "\n", "output")
        self.terminal.insert("end", self.prompt)
        self.terminal.see("end")

    def start(self):
        self.master.mainloop()

def main():
    logger.debug("Starting CommandRex GUI")
    root = ctk.CTk()
    gui = TerminalGUI(root)
    gui.start()

if __name__ == "__main__":
    main()