import pandas as pd
from datetime import datetime
import csv
import os
import json
import logging

class AttendanceManager:
    def __init__(self, attendance_path, db_handler=None):
        self.attendance_path = attendance_path
        self.db_handler = db_handler
        self.today_attendance = {}
        self.current_date = datetime.now().strftime("%Y_m_%d")
        self.load_today_attendance()
        
        # Create directory if not exists
        os.makedirs(attendance_path, exist_ok=True)
    
    def load_today_attendance(self):
        """Load today's attendance from file"""
        filename = f"attendance_{self.current_date}.csv"
        filepath = os.path.join(self.attendance_path, filename)
        
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            for _, row in df.iterrows():
                self.today_attendance[row['student_id']] = {
                    'name': row['name'],
                    'check_in': row['check_in'],
                    'check_out': row.get('check_out', ''),
                    'status': row.get('status', 'present')
                }
    
    def mark_attendance(self, student_id, name, confidence=1.0):
        """Mark attendance for a student"""
        current_time = datetime.now().strftime("%H:%M:%S")
        
        if student_id not in self.today_attendance:
            # First time marking today
            self.today_attendance[student_id] = {
                'name': name,
                'check_in': current_time,
                'check_out': '',
                'status': 'present',
                'confidence': confidence
            }
            self.save_attendance()
            logging.info(f"Marked IN: {name} ({student_id}) at {current_time}")
            return True, "IN"
        elif not self.today_attendance[student_id]['check_out']:
            # Already marked IN, now mark OUT
            self.today_attendance[student_id]['check_out'] = current_time
            self.save_attendance()
            logging.info(f"Marked OUT: {name} ({student_id}) at {current_time}")
            return True, "OUT"
        
        return False, "Already marked"
    
    def save_attendance(self):
        """Save attendance to CSV file"""
        filename = f"attendance_{self.current_date}.csv"
        filepath = os.path.join(self.attendance_path, filename)
        
        with open(filepath, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['student_id', 'name', 'check_in', 'check_out', 'status', 'confidence'])
            
            for sid, data in self.today_attendance.items():
                writer.writerow([
                    sid, data['name'], data['check_in'], 
                    data.get('check_out', ''), data.get('status', 'present'),
                    data.get('confidence', 1.0)
                ])
        
        # Also save to database if available
        if self.db_handler:
            self.save_to_database()
    
    def save_to_database(self):
        """Save attendance to SQLite database"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        for sid, data in self.today_attendance.items():
            query = """
                INSERT OR REPLACE INTO attendance (student_id, date, check_in_time, check_out_time, status)
                VALUES (?, ?, ?, ?, ?)
            """
            self.db_handler.execute_query(query, (
                sid, current_date, data['check_in'], 
                data.get('check_out', ''), data.get('status', 'present')
            ))
    
    def get_attendance_report(self, date=None):
        """Get attendance report for specific date"""
        if date is None:
            date = self.current_date
        
        filename = f"attendance_{date}.csv"
        filepath = os.path.join(self.attendance_path, filename)
        
        if os.path.exists(filepath):
            return pd.read_csv(filepath)
        return pd.DataFrame()
    
    def export_to_excel(self, start_date, end_date):
        """Export attendance between dates to Excel"""
        all_data = []
        # Implementation for exporting range of dates
        pass