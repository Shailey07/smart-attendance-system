import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime, timedelta

class AttendanceViewer:
    def __init__(self, root, attendance_manager):
        self.root = root
        self.attendance_manager = attendance_manager
        self.root.title("Attendance Report Viewer")
        self.root.geometry("900x600")
        
        self.setup_ui()
        self.load_today_data()
    
    def setup_ui(self):
        # Date selection frame
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack(fill=tk.X)
        
        tk.Label(frame, text="Select Date:").pack(side=tk.LEFT, padx=5)
        
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = tk.Entry(frame, textvariable=self.date_var, width=15)
        date_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame, text="Load", command=self.load_attendance,
                 bg='#3498db', fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame, text="Export", command=self.export_data,
                 bg='#2ecc71', fg='white').pack(side=tk.LEFT, padx=5)
        
        # Treeview for displaying data
        self.tree = ttk.Treeview(self.root, columns=('ID', 'Name', 'Check In', 'Check Out', 'Status'), show='headings')
        
        # Define headings
        self.tree.heading('ID', text='Student ID')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Check In', text='Check In Time')
        self.tree.heading('Check Out', text='Check Out Time')
        self.tree.heading('Status', text='Status')
        
        # Set column widths
        self.tree.column('ID', width=100)
        self.tree.column('Name', width=150)
        self.tree.column('Check In', width=120)
        self.tree.column('Check Out', width=120)
        self.tree.column('Status', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def load_attendance(self):
        """Load attendance for selected date"""
        date_str = self.date_var.get().replace('-', '_')
        df = self.attendance_manager.get_attendance_report(date_str)
        self.display_data(df)
    
    def load_today_data(self):
        """Load today's data"""
        self.load_attendance()
    
    def display_data(self, df):
        """Display data in treeview"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if df.empty:
            messagebox.showinfo("No Data", "No attendance data for selected date")
            return
        
        # Insert data
        for _, row in df.iterrows():
            self.tree.insert('', tk.END, values=(
                row['student_id'], row['name'], 
                row['check_in'], row.get('check_out', '-'), 
                row.get('status', 'present')
            ))
    
    def export_data(self):
        """Export current view to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )
        
        if filename:
            # Get data from treeview
            data = []
            for item in self.tree.get_children():
                values = self.tree.item(item)['values']
                data.append(values)
            
            df = pd.DataFrame(data, columns=['Student ID', 'Name', 'Check In', 'Check Out', 'Status'])
            df.to_csv(filename, index=False)
            messagebox.showinfo("Success", f"Data exported to {filename}")