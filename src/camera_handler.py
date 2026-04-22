import cv2
import threading
from datetime import datetime
import os
import logging

class CameraHandler:
    def __init__(self, camera_id=0, width=640, height=480):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.camera = None
        self.running = False
        self.frame = None
        self.lock = threading.Lock()
        self.thread = None
        self.init_camera()
    
    def init_camera(self):
        """Initialize camera"""
        self.camera = cv2.VideoCapture(self.camera_id)
        if not self.camera.isOpened():
            logging.error("Failed to open camera")
            return False
        
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        return True
    
    def start(self):
        """Start video capture thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._capture_frames)
            self.thread.daemon = True
            self.thread.start()
            logging.info("Camera started")
    
    def _capture_frames(self):
        """Capture frames continuously"""
        while self.running:
            ret, frame = self.camera.read()
            if ret:
                with self.lock:
                    self.frame = frame
            else:
                logging.warning("Failed to capture frame")
    
    def get_frame(self):
        """Get current frame"""
        with self.lock:
            if self.frame is not None:
                return self.frame.copy()
            return None
    
    def save_snapshot(self, path):
        """Save current frame as image"""
        frame = self.get_frame()
        if frame is not None:
            cv2.imwrite(path, frame)
            return True
        return False
    
    def stop(self):
        """Stop camera capture"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.camera:
            self.camera.release()
        logging.info("Camera stopped")