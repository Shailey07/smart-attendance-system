import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import threading
from datetime import datetime
import os

from src.face_recognizer import FaceRecognizer
from src.attendance_manager import AttendanceManager
from src.camera_handler import CameraHandler
from src.database_handler import DatabaseHandler
from src.utils import setup_logging, draw_text_with_background
from ui.attendance_viewer import AttendanceViewer
from ui.registration_window import RegistrationWindow

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Attendance System")
        self.root.geometry("1300x750")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize components
        self.init_components()
        
        # Setup UI
        self.setup_ui()
        
        # Start camera
        self.start_camera()
        
        # Recognition flag
        self.recognition_running = True
        self.last_recognition_time = {}
        
    def init_components(self):
        """Initialize all components"""
        setup_logging()
        self.db_handler = DatabaseHandler()
        self.camera_handler = CameraHandler()
        self.face_recognizer = FaceRecognizer("data/known_faces/")
        self.attendance_manager = AttendanceManager("data/attendance/", self.db_handler)
    
    def setup_ui(self):
        """Setup GUI layout"""
        # Title
        title_label = tk.Label(self.root, text="Smart Attendance System", 
                               font=('Arial', 24, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=10)
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left frame - Video feed
        left_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        self.video_label = tk.Label(left_frame, bg='black', width=640, height=480)
        self.video_label.pack(padx=10, pady=10)
        
        # Status label
        self.status_label = tk.Label(left_frame, text="Status: Ready", 
                                     font=('Arial', 12), bg='white')
        self.status_label.pack(pady=5)
        
        # Right frame - Controls
        right_frame = tk.Frame(main_frame, bg='#f0f0f0')
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        # Info frame
        info_frame = tk.LabelFrame(right_frame, text="Today's Attendance", 
                                   font=('Arial', 12, 'bold'), bg='white', padx=10, pady=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.attendance_text = tk.Text(info_frame, height=15, width=30, font=('Arial', 10))
        self.attendance_text.pack()
        
        # Buttons
        btn_frame = tk.Frame(right_frame, bg='#f0f0f0')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Register New Student", command=self.open_registration,
                 bg='#3498db', fg='white', font=('Arial', 11), padx=20, pady=10).pack(pady=5)
        
        tk.Button(btn_frame, text="View Attendance Report", command=self.view_attendance,
                 bg='#2ecc71', fg='white', font=('Arial', 11), padx=20, pady=10).pack(pady=5)
        
        tk.Button(btn_frame, text="Export Today's Report", command=self.export_report,
                 bg='#e67e22', fg='white', font=('Arial', 11), padx=20, pady=10).pack(pady=5)
        
        tk.Button(btn_frame, text="Stop Recognition", command=self.toggle_recognition,
                 bg='#e74c3c', fg='white', font=('Arial', 11), padx=20, pady=10).pack(pady=5)
    
    def start_camera(self):
        """Start video capture"""
        self.camera_handler.start()
        self.update_frame()
    
    def update_frame(self):
        """Update video frame"""
        if not self.camera_handler.running:
            return
        
        frame = self.camera_handler.get_frame()
        if frame is not None:
            # Process frame for face recognition
            if self.recognition_running:
                frame = self.process_face_recognition(frame)
            
            # Convert to PIL format
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image)
            
            self.video_label.config(image=photo)
            self.video_label.image = photo
        
        # Update attendance display
        self.update_attendance_display()
        
        # Schedule next update
        self.root.after(30, self.update_frame)
    
    def process_face_recognition(self, frame):
        """Process frame for face recognition"""
        # Detect and recognize faces
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Get face locations
        face_locations = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        ).detectMultiScale(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 1.1, 5)
        
        for (x, y, w, h) in face_locations:
            face_img = rgb_frame[y:y+h, x:x+w]
            
            # Recognize face
            name, student_id, confidence = self.face_recognizer.recognize_face(face_img)
            
            # Draw rectangle
            color = (0, 255, 0) if name else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            
            # Display name or "Unknown"
            if name:
                text = f"{name} ({confidence:.2f})"
                draw_text_with_background(frame, text, (x, y-10))
                
                # Mark attendance (once per minute per person)
                current_time = datetime.now()
                last_mark = self.last_recognition_time.get(student_id)
                
                if last_mark is None or (current_time - last_mark).seconds > 60:
                    status, action = self.attendance_manager.mark_attendance(student_id, name, confidence)
                    self.last_recognition_time[student_id] = current_time
                    
                    if status:
                        self.status_label.config(text=f"Marked {action}: {name}")
            else:
                draw_text_with_background(frame, "Unknown", (x, y-10), color=(0, 0, 255))
        
        return frame
    
    def update_attendance_display(self):
        """Update attendance text display"""
        self.attendance_text.delete(1.0, tk.END)
        
        if self.attendance_manager.today_attendance:
            self.attendance_text.insert(tk.END, "Present Today:\n\n")
            for sid, data in self.attendance_manager.today_attendance.items():
                status = "✓" if not data.get('check_out') else "✓✓"
                self.attendance_text.insert(tk.END, 
                    f"{status} {data['name']}\n")
                self.attendance_text.insert(tk.END, 
                    f"   IN: {data['check_in']}\n")
                if data.get('check_out'):
                    self.attendance_text.insert(tk.END, 
                        f"   OUT: {data['check_out']}\n")
                self.attendance_text.insert(tk.END, "\n")
        else:
            self.attendance_text.insert(tk.END, "No attendance marked yet")
    
    def open_registration(self):
        """Open registration window"""
        reg_window = tk.Toplevel(self.root)
        RegistrationWindow(reg_window, self.face_recognizer, self.db_handler)
    
    def view_attendance(self):
        """View attendance reports"""
        viewer_window = tk.Toplevel(self.root)
        AttendanceViewer(viewer_window, self.attendance_manager)
    
    def export_report(self):
        """Export today's report"""
        from datetime import datetime
        filename = f"attendance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join("data/attendance/", filename)
        
        import shutil
        current_file = f"data/attendance/attendance_{self.attendance_manager.current_date}.csv"
        
        if os.path.exists(current_file):
            shutil.copy(current_file, filepath)
            messagebox.showinfo("Success", f"Report exported to {filepath}")
        else:
            messagebox.showwarning("No Data", "No attendance data for today")
    
    def toggle_recognition(self):
        """Toggle face recognition on/off"""
        self.recognition_running = not self.recognition_running
        status = "ON" if self.recognition_running else "OFF"
        self.status_label.config(text=f"Recognition: {status}")
    
    def on_closing(self):
        """Clean up on closing"""
        self.camera_handler.stop()
        self.db_handler.close()
        self.root.destroy()