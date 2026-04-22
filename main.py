#!/usr/bin/env python3
"""
Smart Attendance System using Face Recognition
Main entry point for the application
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from src.utils import setup_logging

def main():
    """Main function to run the application"""
    try:
        # Setup logging
        setup_logging()
        
        # Create main window
        root = tk.Tk()
        
        # Set window icon (optional - add your own icon file)
        # root.iconbitmap('icon.ico')
        
        # Create application
        app = MainWindow(root)
        
        # Handle closing event
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # Start main loop
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()