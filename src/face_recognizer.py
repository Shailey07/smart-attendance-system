import cv2
import numpy as np
import os
import pickle
import logging

class FaceRecognizer:
    def __init__(self, known_faces_path, tolerance=0.6, model='hog'):
        self.known_faces_path = known_faces_path
        self.known_names = []
        self.known_ids = []
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.trained = False
        self.label_map = {}
        self.load_known_faces()
        logging.info(f"FaceRecognizer initialized with {len(self.known_names)} faces")
    
    def load_known_faces(self):
        """Load and train with known faces"""
        faces = []
        labels = []
        current_label = 0
        
        if not os.path.exists(self.known_faces_path):
            os.makedirs(self.known_faces_path)
            return
        
        for filename in os.listdir(self.known_faces_path):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                parts = filename.replace('.jpg', '').replace('.png', '').split('_')
                if len(parts) >= 2:
                    student_id = parts[0]
                    name = '_'.join(parts[1:])
                    
                    img_path = os.path.join(self.known_faces_path, filename)
                    try:
                        img = cv2.imread(img_path)
                        if img is None:
                            print(f"Warning: Could not read image {filename}")
                            continue
                        
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        gray = cv2.resize(gray, (200, 200))
                        
                        faces.append(gray)
                        self.label_map[current_label] = (student_id, name)
                        labels.append(current_label)
                        current_label += 1
                        
                        self.known_names.append(name)
                        self.known_ids.append(student_id)
                        print(f"Loaded: {name} ({student_id})")
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
                        continue
        
        if faces:
            self.recognizer.train(faces, np.array(labels))
            self.trained = True
            os.makedirs('data', exist_ok=True)
            with open('data/label_map.pkl', 'wb') as f:
                pickle.dump(self.label_map, f)
            print(f"Trained on {len(faces)} faces")
    
    def detect_faces(self, frame):
        """Detect faces in frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
        return faces
    
    def recognize_face(self, face_image):
        """Recognize face using LBPH"""
        if not self.trained or face_image is None or face_image.size == 0:
            return None, None, 0
        
        try:
            if len(face_image.shape) == 3:
                gray = cv2.cvtColor(face_image, cv2.COLOR_RGB2GRAY)
            else:
                gray = face_image
            
            gray = cv2.resize(gray, (200, 200))
            label, confidence = self.recognizer.predict(gray)
            
            if confidence < 100:
                if label in self.label_map:
                    student_id, name = self.label_map[label]
                    confidence_score = 1 - (confidence / 100)
                    return name, student_id, confidence_score
            
            return None, None, 0
        except Exception as e:
            logging.error(f"Face recognition error: {e}")
            return None, None, 0
    
    def add_new_face(self, image, name, student_id):
        """Add new face to known faces database"""
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            gray = cv2.resize(gray, (200, 200))
            filename = f"{student_id}_{name}.jpg"
            filepath = os.path.join(self.known_faces_path, filename)
            cv2.imwrite(filepath, gray)
            
            self.load_known_faces()
            return True, "Face added successfully"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_face_count(self):
        return len(self.known_names)