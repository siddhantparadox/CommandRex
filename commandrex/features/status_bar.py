# File: commandrex/features/status_bar.py

import customtkinter as ctk
import os

class StatusBar:
    def __init__(self, master, font):
        self.frame = ctk.CTkFrame(master, height=25)
        self.frame.pack(side='bottom', fill='x')
        
        self.label = ctk.CTkLabel(self.frame, text="", font=font)
        self.label.pack(side='left', padx=5)
        
        self.update_status()

    def update_status(self):
        current_dir = os.getcwd()
        self.label.configure(text=f"Current Directory: {current_dir}")

    def set_text(self, text):
        self.label.configure(text=text)