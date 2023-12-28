# ./server/main.py
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from jose import jwt
from datetime import datetime, timedelta
from deepface import DeepFace
import shutil
import os
import uuid
from typing import Optional
from pymongo import MongoClient
from bson import ObjectId
from numpy.linalg import norm
import numpy as np

app = FastAPI()

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
client = MongoClient('mongodb://root:example@0.0.0.0:27017/')
db = client['face_recognition']
users = db['users']

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def save_temp_file(file: UploadFile):
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return temp_file_path

def remove_temp_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)

def serialize_mongo_document(document):
    document = dict(document)
    for key, value in document.items():
        if isinstance(value, ObjectId):
            document[key] = str(value)  # Convertit ObjectId en string
    return document


def get_face_embedding(image_path):
    try:
        # Analyser le visage et obtenir l'embedding
        embedding = DeepFace.represent(img_path=image_path, model_name='Facenet')
        if embedding is not None and len(embedding) == 128:  # Assurez-vous que la taille est correcte
            return np.array(embedding)
        else:
            return None
    except Exception as e:
        print(f"Erreur lors de la génération de l'embedding : {str(e)}")
        return None


@app.post("/login")
async def login(file: UploadFile = File(...)):
    temp_file_path = save_temp_file(file)
    embedding = get_face_embedding(temp_file_path)
    remove_temp_file(temp_file_path)

    if embedding is not None:
        # Recherche dans la base de données pour une correspondance
        for user in users.find():
            stored_embedding = np.array(user['embedding'])
            similarity = np.dot(embedding, stored_embedding) / (norm(embedding) * norm(stored_embedding))
            if similarity > 0.8:  # Seuil de similarité
                return {"access_token": create_access_token({"sub": user["uuid"]}), "token_type": "bearer"}
    return {"message": "Authentication failed"}, 401

@app.post("/register")
async def register(file: UploadFile = File(...)):
    temp_file_path = save_temp_file(file) 
    embedding = get_face_embedding(temp_file_path)
    remove_temp_file(temp_file_path)

    if embedding is not None:
        user_uuid = str(uuid.uuid4())
        new_user = {
            "uuid": user_uuid,
            "embedding": embedding
        }
        users.insert_one(new_user)
        return {"message": "User registered successfully", "uuid": user_uuid}
    return {"message": "Registration failed"}, 400

@app.get("/users")
async def get_users():
    try:
        users_list = []
        for user in users.find():
            serialized_user = serialize_mongo_document(user)
            users_list.append(serialized_user)
        return users_list
    except Exception as e:
        return JSONResponse(status_code=500, content={"message":
        f"Erreur lors de la récupération des utilisateurs: {str(e)}"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
