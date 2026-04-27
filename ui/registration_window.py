import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import os

from src.camera_handler import CameraHandler
from src.utils import generate_student_id, validate_face_image

class RegistrationWindow:
    def __init__(self, root, face_recognizer, db_handler):
        self.root = root
        self.face_recognizer = face_recognizer
        self.db_handler = db_handler
        self.root.title("Register New Student")
        self.root.geometry("800x600")
        
        self.captured_image = None
        self.setup_ui()
        self.start_camera()
    
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - Camera feed
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.video_label = tk.Label(left_frame, bg='black', width=400, height=300)
        self.video_label.pack(pady=10)
        
        tk.Button(left_frame, text="Capture Photo", command=self.capture_photo,
                 bg='#3498db', fg='white', font=('Arial', 11), padx=20).pack(pady=10)
        
        # Right side - Form
        right_frame = tk.Frame(main_frame, padx=20)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(right_frame, text="Student Registration", 
                font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Form fields
        fields = [
            ("Student ID:", "auto"),
            ("Full Name:", "entry"),
            ("Department:", "entry"),
            ("Year:", "combobox"),
            ("Email:", "entry"),
            ("Phone:", "entry")
        ]
        
        self.entries = {}
        
        for label, type_ in fields:
            frame = tk.Frame(right_frame)
            frame.pack(fill=tk.X, pady=5)
            
            tk.Label(frame, text=label, width=15, anchor='w').pack(side=tk.LEFT)
            
            if type_ == "auto":
                self.student_id = generate_student_id()
                var = tk.StringVar(value=self.student_id)
                entry = tk.Entry(frame, textvariable=var, state='readonly', width=25)
                entry.pack(side=tk.LEFT)
                self.entries['student_id'] = var
            elif type_ == "combobox":
                entry = ttk.Combobox(frame, values=[1, 2, 3, 4], width=23)
                entry.pack(side=tk.LEFT)
                self.entries['year'] = entry
            else:
                entry = tk.Entry(frame, width=25)
                entry.pack(side=tk.LEFT)
                self.entries[label.lower().replace(":", "").replace(" ", "_")] = entry
        
        # Photo preview
        tk.Label(right_frame, text="Captured Photo:").pack(pady=(10,0))
        self.photo_label = tk.Label(right_frame, bg='gray', width=200, height=150)
        self.photo_label.pack(pady=5)
        
        # Submit button
        tk.Button(right_frame, text="Register Student", command=self.register_student,
                 bg='#2ecc71', fg='white', font=('Arial', 12), padx=30, pady=10).pack(pady=20)
    
    def start_camera(self):
        """Start camera for registration"""
        self.camera = CameraHandler()
        self.camera.start()
        self.update_camera()
    
    def update_camera(self):
        """Update camera feed"""
        if hasattr(self, 'camera') and self.camera.running:
            frame = self.camera.get_frame()
            if frame is not None:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame_rgb)
                image = image.resize((400, 300))
                photo = ImageTk.PhotoImage(image)
                self.video_label.config(image=photo)
                self.video_label.image = photo
            
            self.root.after(30, self.update_camera)
    
    def capture_photo(self):
        """Capture current frame as photo"""
        frame = self.camera.get_frame()
        if frame is not None:
            self.captured_image = frame
            # Display captured photo
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            image = image.resize((200, 150))
            photo = ImageTk.PhotoImage(image)
            self.photo_label.config(image=photo)
            self.photo_label.image = photo
            messagebox.showinfo("Success", "Photo captured successfully!")
    
    def register_student(self):
        """Register new student"""
        # Validate inputs
        name = self.entries['full_name'].get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter student name")
            return
        
        if self.captured_image is None:
            messagebox.showerror("Error", "Please capture a photo first")
            return
        
        # Validate face
        valid, msg = validate_face_image(self.captured_image)
        if not valid:
            messagebox.showerror("Error", msg)
            return
        
        # Get form data
        student_id = self.student_id
        department = self.entries['department'].get()
        year = self.entries['year'].get()
        email = self.entries['email'].get()
        phone = self.entries['phone'].get()
        
        # Add face to recognizer
        success, msg = self.face_recognizer.add_new_face(
            cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2RGB),
            name, student_id
        )
        
        if success:
            # Save to database
            self.db_handler.insert_student(student_id, name, department, year, email, phone)
            messagebox.showinfo("Success", f"Student {name} registered successfully!\nID: {student_id}")
            self.root.destroy()
        else:
            messagebox.showerror("Error", msg)
    
    def on_closing(self):
        """Clean up on close"""
        if hasattr(self, 'camera'):
            self.camera.stop()
        self.root.destroy()