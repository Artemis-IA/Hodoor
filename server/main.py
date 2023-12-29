# ./server/main.py
from datetime import datetime, timedelta
from io import BytesIO
import logging
import shutil
import uuid
from bson import ObjectId
from deepface.basemodels import Facenet
from faker import Faker
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from mtcnn import MTCNN
import numpy as np
from PIL import Image, ImageEnhance
from pymongo import MongoClient
import base64
from typing import List


app = FastAPI()

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
client = MongoClient('mongodb://root:example@0.0.0.0:27017/')
db = client['face_recognition']
users = db['users']

facenet_model = Facenet.loadModel()
mtcnn_detector = MTCNN()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logging.basicConfig(level=logging.INFO)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "roles": ["admin", "user"]})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def serialize_mongo_document(document):
    return {key: str(value) if isinstance(value, ObjectId) else value for key, value in dict(document).items()}

def open_image(upload_file: UploadFile):
    contents = upload_file.file.read()
    return Image.open(BytesIO(contents))

def save_image(image: UploadFile) -> str:
    file_name = f"temp_{uuid.uuid4()}.jpg"
    with open(file_name, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    return file_name

def detect_face(image):
    attempts = 0
    while attempts < 3:
        detected_faces = mtcnn_detector.detect_faces(np.array(image))
        if len(detected_faces) > 0:
            return detected_faces[0]['box']
        attempts += 1
        image = ImageEnhance.Contrast(image).enhance(1.5)  # Enhance contrast and try again
    raise ValueError("No face detected")

def get_face_embedding(image):
    try:
        face_coords = detect_face(image)
        cropped_face = image.crop((face_coords[0], face_coords[1], face_coords[0]+face_coords[2], face_coords[1]+face_coords[3]))
        cropped_face = cropped_face.resize((160, 160))
        face_array = np.asarray(cropped_face)
        face_pixels = face_array.astype('float32')
        mean, std = face_pixels.mean(), face_pixels.std()
        face_pixels = (face_pixels - mean) / std
        samples = np.expand_dims(face_pixels, axis=0)
        embedding = facenet_model.predict(samples)
        if len(embedding[0]) != 128:
            raise ValueError("Invalid embedding dimension")
        return embedding[0]
    except Exception as e:
        logging.error(f"Error in embedding generation: {e}")
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub", "")  # Provide a default value of an empty string
        if username == "":
            raise credentials_exception
        roles: list = payload.get("roles", [])
        if "admin" not in roles:  # Vérifier si l'utilisateur a le rôle 'admin'
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Insufficient permissions",
            )
        return username
    except JWTError:
        raise credentials_exception

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
)

@app.post("/login")
async def login(file: UploadFile = File(...)):
    image = open_image(file)
    embedding = get_face_embedding(image)

    max_similarity = 0.8  # Seuil de similarité
    user_id_with_max_similarity = None

    if embedding is not None:
        for user in users.find():
            if 'embeddings' in user:  # Vérifiez si les embeddings sont présents
                for stored_embedding in user['embeddings']:
                    stored_embedding_array = np.array(stored_embedding, dtype=np.float32)  # Convert to float32
                    embedding_array = np.array(embedding, dtype=np.float32)  # Convert to float32
                    similarity = np.dot(embedding_array, stored_embedding_array) / (np.linalg.norm(embedding_array) * np.linalg.norm(stored_embedding_array))
                    if np.isscalar(similarity) and float(similarity) > max_similarity:
                        max_similarity = float(similarity)
                        user_id_with_max_similarity = user["uuid"]
        if user_id_with_max_similarity:
            # Créez un token d'accès avec l'UUID de l'utilisateur
            return {
                "access_token": create_access_token({"sub": user_id_with_max_similarity}),
                "token_type": "bearer",
                "user_id": user_id_with_max_similarity  # Retour de l'ID utilisateur
            }

    return {"message": "Échec de l'authentification"}, 401


@app.post("/register")
async def register(files: List[UploadFile] = File(...)):
    if len(files) != 3:
        return {"message": "Exactly 3 images are required"}, 400

    # Générer un nom d'utilisateur aléatoire
    fake = Faker()
    username = fake.first_name()

    # Process images and generate embeddings
    embeddings = []
    for file in files:
        image = open_image(file)
        embedding = get_face_embedding(image)
        if embedding is None:
            return {"message": "Failed to detect face or generate embedding"}, 400
        embeddings.append(embedding)

    # Save one of the images as profile picture
    profile_image_path = save_image(files[0])

    # Create new user with UUID, embeddings, and profile image path
    user_uuid = str(uuid.uuid4())
    new_user = {
        "uuid": user_uuid,
        "username": username,  # Utiliser le nom d'utilisateur généré
        "embeddings": [embedding.tolist() for embedding in embeddings],
        "registered_at": datetime.utcnow(),
        "profile_image": profile_image_path
    }
    users.insert_one(new_user)
    logging.info(f"User {user_uuid} registered successfully")

    return {
        "message": "User registered successfully",
        "uuid": user_uuid,
        "profile_image": profile_image_path
    }



@app.get("/users")
async def get_users():
    try:
        user_list = []
        for user in users.find():
            user_data = serialize_mongo_document(user)
            if 'profile_image' in user_data:
                image_path = user_data['profile_image']
                with open(image_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()
                    user_data['profile_image_base64'] = encoded_string
            user_list.append(user_data)
        return user_list
    except Exception as e:
        return HTTPException(status_code=500, detail=f"Error retrieving users: {e}")

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    try:
        user = users.find_one({"uuid": user_id})
        if user is None:
            return HTTPException(status_code=404, detail="User not found")
        user_data = serialize_mongo_document(user)
        if 'profile_image' in user_data:
            image_path = user_data['profile_image']
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                user_data['profile_image_base64'] = encoded_string
        return user_data
    except Exception as e:
        return HTTPException(status_code=500, detail=f"Error retrieving user: {e}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
