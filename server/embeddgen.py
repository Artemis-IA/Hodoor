import cv2
from deepface import DeepFace
import numpy as np
import os

def capture_face():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break
        cv2.imshow('Capture - Press q to quit', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    return frame

def save_image(image, filename="captured_face.jpg"):
    cv2.imwrite(filename, image)
    return filename

def get_face_embedding(image_path):
    try:
        embedding = DeepFace.represent(img_path=image_path, model_name='Facenet')
        return embedding
    except Exception as e:
        print(f"Erreur lors de la génération de l'embedding: {e}")
        return None

def main():
    face_image = capture_face()
    image_path = save_image(face_image)
    face_embedding = get_face_embedding(image_path)
    if face_embedding is not None:
        print("Embedding généré avec succès:")
        print(face_embedding)
    else:
        print("Impossible de générer l'embedding.")
    if os.path.exists(image_path):
        os.remove(image_path)

if __name__ == "__main__":
    main()
