import os
import cv2
import numpy as np
from datetime import datetime
import hashlib
import logging

def setup_logging(log_path="logs/system.log"):
    """Setup logging configuration"""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )

def get_current_timestamp():
    """Get current timestamp as string"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_date_string():
    """Get current date as string"""
    return datetime.now().strftime("%Y_%m_%d")

def resize_image(image, width=None, height=None):
    """Resize image maintaining aspect ratio"""
    if width is None and height is None:
        return image
    
    h, w = image.shape[:2]
    
    if width is None:
        ratio = height / h
        width = int(w * ratio)
    elif height is None:
        ratio = width / w
        height = int(h * ratio)
    else:
        ratio = min(width/w, height/h)
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        width, height = new_w, new_h
    
    return cv2.resize(image, (width, height))

def draw_text_with_background(img, text, position, font_scale=0.7, 
                              color=(0, 255, 0), thickness=2):
    """Draw text with background for better visibility"""
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)
    
    x, y = position
    cv2.rectangle(img, (x-5, y-text_h-5), (x+text_w+5, y+5), (0, 0, 0), -1)
    cv2.putText(img, text, (x, y), font, font_scale, color, thickness)

def generate_student_id():
    """Generate unique student ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_hash = hashlib.md5(timestamp.encode()).hexdigest()[:6]
    return f"STU{random_hash.upper()}"

def validate_face_image(image):
    """Validate if image contains a proper face"""
    if image is None or image.size == 0:
        return False, "Empty image"
    
    # Check image quality
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_value = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    if blur_value < 50:
        return False, "Image too blurry"
    
    return True, "Valid image"