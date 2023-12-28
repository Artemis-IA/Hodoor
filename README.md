![Logo Hodoor](README.md/assets/Hodoor_logo.png)


# Hodoor: Facial Recognition System

## Introduction
Hodoor is an advanced facial recognition system inspired by the iconic character Hodor from "Game of Thrones". The system utilizes state-of-the-art technology for accurate and secure face recognition, suitable for various applications including security, authentication, and surveillance.

## Features
- **Facial Recognition:** Leverages deep learning algorithms for accurate face detection and recognition.
- **User Authentication:** Enhances security by using facial data for user authentication.
- **Surveillance:** Capable of monitoring and identifying individuals in real-time for security purposes.
- **User-Friendly Interface:** Simple and intuitive interface for easy operation and management.

## System Architecture
Hodoor's architecture is split into two main components: the Server (Backend) and the Client (Frontend).

### Server (Backend)
- **FastAPI Framework:** Robust and efficient framework for building APIs.
- **DeepFace and MTCNN:** Deep learning models for facial recognition.
- **MongoDB:** NoSQL database for storing user data and facial embeddings.
- **Python:** Primary programming language for backend development.

### Client (Frontend)
- **Flask Framework:** Lightweight WSGI web application framework.
- **JavaScript, HTML, CSS:** Technologies used for building a responsive and dynamic user interface.
- **OpenCV:** For real-time video processing and face detection.

## Installation & Setup
Detailed steps to set up the Hodoor system on different platforms.

### Prerequisites
- Python 3.8+
- MongoDB
- Other dependencies listed in `requirements.txt`.

### Running the Server
```bash
# Navigate to the server directory
cd path/to/server

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --reload
```

### Running the Client
```bash
# Navigate to the client directory
cd path/to/client

# Install dependencies
pip install -r requirements.txt

# Start the Flask server
flask run
```

## Usage
Detailed steps to use the Hodoor system.

### Registering a User
1. Navigate to the registration page.
2. Enter the user's name and click on the "Register" button.
3. The user's face will be captured and stored in the database.

### Authenticating a User
1. Navigate to the authentication page.
2. PLace you're face in front of your camera and click on the "Authenticate" button.
3. The user's face will be captured and compared with the stored facial embeddings.
4. If the user is authenticated, the door will be unlocked.

### User's dashboard
1. Navigate to the dashboard page.
2. The user's information will be displayed along with the user's facial embeddings.


