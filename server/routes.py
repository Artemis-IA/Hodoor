import os
import shutil
from datetime import datetime, timedelta
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


# Route générique pour l'analyse DeepFace
@app.post("/{analysis_type}")
async def deepface_analysis(analysis_type: str, file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    try:
        temp_file_path = save_temp_file(file)

        # Sélection de l'action en fonction du type d'analyse
        actions = ['emotion', 'age', 'gender', 'race']
        if analysis_type not in actions:
            raise HTTPException(status_code=400, detail="Type d'analyse non supporté")

        result = DeepFace.analyze(img_path=temp_file_path, actions=[analysis_type])

        remove_temp_file(temp_file_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# DeepFace Routes
@app.post("/recognize-face")
async def recognize_face(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    try:
        # Sauvegarde temporaire de l'image téléchargée
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Utilisation de DeepFace pour la reconnaissance faciale
        result = DeepFace.find(img_path=temp_file_path, db_path="path_to_your_database", model_name="VGG-Face", distance_metric="cosine")

        # Suppression du fichier temporaire
        os.remove(temp_file_path)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/analyze-emotion")
async def analyze_emotion(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    try:
        # Sauvegarde temporaire de l'image téléchargée
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Utilisation de DeepFace pour l'analyse des émotions
        result = DeepFace.analyze(img_path=temp_file_path, actions=['emotion'])

        # Suppression du fichier temporaire
        os.remove(temp_file_path)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/find-face")
async def find_face(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    try:
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Recherche du visage dans la base de données
        db_path = "path_to_your_face_database"
        result = DeepFace.find(img_path=temp_file_path, db_path=db_path, model_name="VGG-Face", distance_metric="cosine")

        os.remove(temp_file_path)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify-identity")
async def verify_identity(user_id: str, file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    try:
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Chemin vers l'image de référence de l'utilisateur
        user_image_path = f"path_to_your_face_database/{user_id}.jpg"  # Assurez-vous que le chemin et le format sont corrects

        # Vérification de l'identité
        result = DeepFace.verify(img1_path=temp_file_path, img2_path=user_image_path, model_name="VGG-Face", distance_metric="cosine")

        os.remove(temp_file_path)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect-age")
async def detect_age(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    try:
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Analyse de l'âge
        result = DeepFace.analyze(img_path=temp_file_path, actions=['age'])

        os.remove(temp_file_path)

        return {"age": result["age"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect-gender")
async def detect_gender(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    try:
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Analyse du genre
        result = DeepFace.analyze(img_path=temp_file_path, actions=['gender'])

        os.remove(temp_file_path)

        return {"gender": result["gender"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-race")
async def analyze_race(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    try:
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Analyse de la race
        result = DeepFace.analyze(img_path=temp_file_path, actions=['race'])

        os.remove(temp_file_path)

        return {"race": result["dominant_race"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

