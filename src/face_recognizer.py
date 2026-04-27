import cv2
import numpy as np
import os
import pickle

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
    
    def load_known_faces(self):
        faces = []
        labels = []
        current_label = 0
        self.label_map = {}
        
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
                    img = cv2.imread(img_path)
                    if img is not None:
                        # Image already cropped face (200x200 grayscale)
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        gray = cv2.resize(gray, (200, 200))
                        gray = cv2.equalizeHist(gray)
                        faces.append(gray)
                        self.label_map[current_label] = (student_id, name)
                        labels.append(current_label)
                        current_label += 1
                        self.known_names.append(name)
                        self.known_ids.append(student_id)
                        print(f"Loaded: {name} ({student_id})")
        
        if faces:
            self.recognizer.train(faces, np.array(labels))
            self.trained = True
            os.makedirs('data', exist_ok=True)
            with open('data/label_map.pkl', 'wb') as f:
                pickle.dump(self.label_map, f)
            print(f"Trained on {len(faces)} faces")
        else:
            print("No faces found")
    
    def detect_faces(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
        return faces
    
    def recognize_face(self, face_image):
        if not self.trained or face_image is None:
            return None, None, 0
        try:
            if len(face_image.shape) == 3:
                gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = face_image
            gray = cv2.resize(gray, (200, 200))
            gray = cv2.equalizeHist(gray)
            label, confidence = self.recognizer.predict(gray)
            print(f"DEBUG: label={label}, confidence={confidence}")
            
            # STRICT THRESHOLD: Only accept if confidence < 60 (good match)
            THRESHOLD = 60
            if confidence < THRESHOLD and label in self.label_map:
                student_id, name = self.label_map[label]
                confidence_score = 1 - (confidence / 100)
                print(f"✅ Recognized: {name}")
                return name, student_id, confidence_score
            else:
                print(f"❌ Unknown (confidence {confidence} >= {THRESHOLD})")
                return None, None, 0
        except Exception as e:
            print(f"Recognition error: {e}")
            return None, None, 0
    
    def add_new_face(self, image, name, student_id):
        try:
            # Detect face in the captured frame
            gray_full = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray_full, 1.1, 5)
            if len(faces) == 0:
                return False, "No face detected. Please position your face clearly."
            
            # Take the largest face
            (x, y, w, h) = max(faces, key=lambda rect: rect[2]*rect[3])
            face_roi = image[y:y+h, x:x+w]
            if face_roi.size == 0:
                return False, "Face region empty."
            
            # Preprocess
            face_gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            face_resized = cv2.resize(face_gray, (200, 200))
            face_equalized = cv2.equalizeHist(face_resized)
            
            # Save
            filename = f"{student_id}_{name}.jpg"
            filepath = os.path.join(self.known_faces_path, filename)
            cv2.imwrite(filepath, face_equalized)
            print(f"Saved cropped face: {filepath}")
            
            # Retrain
            self.load_known_faces()
            return True, f"Successfully registered {name}"
        except Exception as e:
            return False, str(e)
    
    def get_face_count(self):
        return len(self.known_names)