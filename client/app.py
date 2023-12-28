# ./client/app.py
from flask import Flask, render_template, request, redirect, url_for, Response, session
import requests
import cv2
import base64
import io
import base64


app = Flask(__name__)

SERVEUR_URL = 'http://127.0.0.1:8000'
SECRET_KEY = "your_secret_key"
app.secret_key = SECRET_KEY



def decode_image(image_data):
    image_data = image_data.replace('data:image/jpeg;base64,', '')
    image_data = image_data.replace(' ', '+')
    image = base64.b64decode(image_data)
    return io.BytesIO(image)

def is_logged_in():
    return 'is_logged_in' in session and 'jwt_token' in session


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    if not is_logged_in():
        return redirect(url_for('login'))
    video = cv2.VideoCapture(0)
    def generate_frames():
        while True:
            success, frame = video.read()
            if not success:
                break
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    if request.method == 'POST':
        image_data = request.form.get('image_data')
        image = decode_image(image_data)
        response = requests.post(f'{SERVEUR_URL}/login', files={'file': ('image.jpg', image)})

        if response.status_code == 200:
            response_json = response.json()
            if 'access_token' in response_json:
                session['jwt_token'] = response_json['access_token']
                session['is_logged_in'] = True
                user_uuid = response_json.get("user_id", "Unknown User ID")
                return render_template('welcome.html', user_uuid=user_uuid)
            else:
                error_message = "Erreur de réponse du serveur"
        elif response.status_code == 500:
            error_message = "Erreur serveur: Impossible de détecter le visage"
        else:
            error_message = "Échec de la connexion"

    return render_template('login.html', error_message=error_message)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        images = [decode_image(request.form.get(f'image_data{i}')) for i in range(1, 4)]
        files = [('files', ('image.jpg', image, 'image/jpeg')) for image in images]
        
        response = requests.post(f'{SERVEUR_URL}/register', files=files)
        
        if response.status_code == 200:
            response_data = response.json()
            user_uuid = response_data.get("uuid")
            return render_template('welcome.html', user_uuid=user_uuid)
        else:
            return f"Échec de l'enregistrement: {response.status_code}", response.status_code
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('is_logged_in', None)
    session.pop('jwt_token', None)
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('dashboard.html')


def serialize_mongo_document(document):
    document['_id'] = str(document['_id'])
    return document

@app.route('/users')
def get_users():
    headers = {'Authorization': f'Bearer {session.get("jwt_token")}'}
    response = requests.get(f'{SERVEUR_URL}/users', headers=headers)

    if response.status_code == 200:
        users_list = response.json()
        return render_template('users.html', users=users_list)
    else:
        return f"Error retrieving users: {response.status_code}", 500


@app.route('/deepface-analysis/<analysis_type>', methods=['GET', 'POST'])
def deepface_analysis(analysis_type):
    if not is_logged_in():
        return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files['file']
        headers = {'Authorization': f'Bearer {session["jwt_token"]}'}
        response = requests.post(f'{SERVEUR_URL}/{analysis_type}', files={'file': (file.filename, file.read(), file.content_type)}, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return "Analysis Failed", 500
    return render_template('deepface_analysis.html', analysis_type=analysis_type)

@app.route('/recognize-face', methods=['GET', 'POST'])
def recognize_face():
    if not is_logged_in():
        return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files['file']
        headers = {'Authorization': f'Bearer {session["jwt_token"]}'}
        file_tuple = (file.filename, file.read(), file.content_type)
        response = requests.post(f'{SERVEUR_URL}/recognize-face', files={'file': file_tuple}, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return "Face Recognition Failed", 500
    return render_template('dashboard.html')

@app.route('/find-face', methods=['GET', 'POST'])
def find_face():
    if not is_logged_in():
        return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files['file']
        headers = {'Authorization': f'Bearer {session["jwt_token"]}'}
        file_tuple = (file.filename, file.read(), file.content_type)
        response = requests.post(f'{SERVEUR_URL}/find-face', files={'file': file_tuple}, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return "Find Face Failed", 500
    return render_template('dashboard.html')

@app.route('/verify-identity', methods=['GET', 'POST'])
def verify_identity():
    if not is_logged_in():
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_id = request.form['user_id']
        file = request.files['file']
        headers = {'Authorization': f'Bearer {session["jwt_token"]}'}
        response = requests.post(f'{SERVEUR_URL}/verify-identity', data={'user_id': user_id}, files={'file': file}, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return "Verification Failed", 500
    return render_template('verify_identity.html')

@app.route('/detect-age', methods=['GET', 'POST'])
def detect_age():
    if not is_logged_in():
        return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files['file']
        headers = {'Authorization': f'Bearer {session["jwt_token"]}'}
        file_tuple = (file.filename, file.read(), file.content_type)
        response = requests.post(f'{SERVEUR_URL}/detect-age', files={'file': file_tuple}, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return "Age Detection Failed", 500
    return render_template('detect_age.html')

@app.route('/detect-gender', methods=['GET', 'POST'])
def detect_gender():
    if not is_logged_in():
        return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files['file']
        headers = {'Authorization': f'Bearer {session["jwt_token"]}'}
        file_tuple = ('file', file, file.content_type)
        response = requests.post(f'{SERVEUR_URL}/detect-gender', files=[file_tuple], headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return "Gender Detection Failed", 500
    return render_template('detect_gender.html')



@app.route('/analyze-race', methods=['GET', 'POST'])
def analyze_race():
    if not is_logged_in():
        return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files['file']
        headers = {'Authorization': f'Bearer {session["jwt_token"]}'}
        file_tuple = ('file', file, file.content_type)
        response = requests.post(f'{SERVEUR_URL}/analyze-race', files=[file_tuple], headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return "Race Analysis Failed", 500
    return render_template('analyze_race.html')


if __name__ == '__main__':
    app.run(debug=True)
