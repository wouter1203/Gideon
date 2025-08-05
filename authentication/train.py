import cv2
import numpy as np
import os
import json  # Import JSON module to save the mapping

def train_model():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    faces, labels = [], []
    label_map = {}
    label_id = 0

    for person in os.listdir("faces"):
        person_path = os.path.join("faces", person)
        if os.path.isdir(person_path):
            label_map[label_id] = person  # Map label ID to the person's name
            for image in os.listdir(person_path):
                img_path = os.path.join(person_path, image)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                
                # Detect faces in the image
                face = face_cascade.detectMultiScale(img, 1.3, 5)
                for (x, y, w, h) in face:
                    face_region = img[y:y+h, x:x+w]
                    face_region = cv2.resize(face_region, (100, 100))
                    faces.append(face_region)
                    labels.append(label_id)
                    
            label_id += 1

    recognizer.train(faces, np.array(labels))
    recognizer.write("face_model.yml")
    print("Model trained and saved.")

    # Save the label-to-name mapping to a JSON file
    with open("label_to_name.json", "w") as f:
        json.dump(label_map, f)
    print("Label-to-name mapping saved to 'label_to_name.json'.")

    # Optionally, print the mapping
    print("Trained IDs and Names:")
    for label, name in label_map.items():
        print(f"ID: {label}, Name: {name}")

if __name__ == "__main__":
    train_model()