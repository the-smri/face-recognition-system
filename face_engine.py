import face_recognition
import cv2
import numpy as np
import os
import pickle
import base64

ENCODINGS_FILE = 'encodings/faces.pkl'

def load_known_encodings():
    if os.path.exists(ENCODINGS_FILE):
        with open(ENCODINGS_FILE, 'rb') as f:
            return pickle.load(f)
    return {"names": [], "encodings": [], "student_ids": []}

def save_known_encodings(data):
    with open(ENCODINGS_FILE, 'wb') as f:
        pickle.dump(data, f)

def decode_base64_image(base64_string):
    img_data = base64.b64decode(base64_string)
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def register_user(name, student_id, base64_images):
    known_data = load_known_encodings()
    encodings_found = []
    
    for b64_img in base64_images:
        img = decode_base64_image(b64_img)
        # Convert BGR (OpenCV) to RGB (face_recognition)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        boxes = face_recognition.face_locations(rgb_img)
        encodings = face_recognition.face_encodings(rgb_img, boxes)
        
        if len(encodings) > 0:
            encodings_found.append(encodings[0])
            
            # Save top 3 face images to dataset folder for reference
            if len(encodings_found) <= 3:
                filename = f"dataset/{student_id}_{len(encodings_found)}.jpg"
                cv2.imwrite(filename, img)
    
    if len(encodings_found) == 0:
        return False, "No faces detected in the provided images."
        
    # Average the encodings for a more robust representation
    avg_encoding = np.mean(encodings_found, axis=0)
    
    known_data["names"].append(name)
    known_data["student_ids"].append(student_id)
    known_data["encodings"].append(avg_encoding)
    
    save_known_encodings(known_data)
    
    return True, f"Successfully registered. Found {len(encodings_found)} valid frames."

def recognize_faces(base64_image_str):
    known_data = load_known_encodings()
    
    if not known_data["encodings"]:
        return [] # No users registered
        
    img = decode_base64_image(base64_image_str)
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    face_locations = face_recognition.face_locations(rgb_img)
    face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
    
    results = []
    
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_data["encodings"], face_encoding, tolerance=0.5)
        
        name = "Unknown"
        student_id = "Unknown"
        confidence = 0.0
        
        if True in matches:
            # Use the known face with the smallest distance
            face_distances = face_recognition.face_distance(known_data["encodings"], face_encoding)
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index]:
                name = known_data["names"][best_match_index]
                student_id = known_data["student_ids"][best_match_index]
                confidence = round((1 - face_distances[best_match_index]) * 100, 2)
                
        results.append({
            "box": [top, right, bottom, left],
            "name": name,
            "student_id": student_id,
            "confidence": confidence
        })
        
    return results
