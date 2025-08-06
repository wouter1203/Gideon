import os
import cv2
import json
from deepface import DeepFace
import pyttsx3

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def authenticate():
    # Load label-to-name mapping from JSON
    with open("label_to_name.json", "r") as f:
        label_to_name = json.load(f)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Unable to access the camera.")
        return False

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Error: Unable to read from the camera.")
                break

            # Use DeepFace for face detection and recognition
            for label, name in label_to_name.items():
                stored_image_path = f"/Users/woutervanderwal/GitHub/Gideon/faces/{name}/{name}_1.jpg"
                try:
                    result = DeepFace.verify(frame, stored_image_path, model_name="VGG-Face")
                    confidence = result.get("distance", None)  # Extract confidence score
                    print(f"Confidence rate for {name}: {confidence}")
                    if result["verified"]:
                        print(f"✅ {name} recognized with confidence: {confidence}")
                        speak(f"✅ Success! Welcome, {name}!")
                        return True
                except Exception as e:
                    print(f"Error during verification: {e}")

            print("❌ Fail")
            cv2.imshow('Authenticating', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

    return False

if __name__ == "__main__":
    if authenticate():
        print("Welcome!")
    else:
        print("Access Denied.")