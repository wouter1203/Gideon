import cv2
import os

def capture_face_data(name):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(1)  # Use index 0 for the default camera
    if not cap.isOpened():
        print("❌ Error: Unable to access the camera.")
        return

    count = 0
    save_path = f"faces/{name}"
    os.makedirs(save_path, exist_ok=True)

    while count < 500:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("❌ Error: Unable to read a frame from the camera.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            count += 1
            face = gray[y:y+h, x:x+w]
            cv2.imwrite(f"{save_path}/{name}_{count}.jpg", face)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow('Capturing Faces', frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or count >= 500:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    name = input("Enter your name: ")
    capture_face_data(name)