import cv2
import os
from flask import Flask, request, render_template
from datetime import date
from datetime import datetime
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import joblib
from services.log_service import *
from services.face_service import *
model = joblib.load('static/face_recognition_model.pkl')

face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')



#face service functions

def extract_faces(img):
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_points = face_detector.detectMultiScale(gray, 1.2, 5, minSize=(20, 20))
        return face_points
    except:
        return []
    
def identify_face(facearray):
    return model.predict(facearray)

def train_model():
    faces = []
    labels = []
    userlist = os.listdir('static/faces')
    for user in userlist:
        for imgname in os.listdir(f'static/faces/{user}'):
            img = cv2.imread(f'static/faces/{user}/{imgname}')
            resized_face = cv2.resize(img, (50, 50))
            faces.append(resized_face.ravel())
            labels.append(user)
    faces = np.array(faces)
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(faces, labels)
    joblib.dump(knn, 'static/face_recognition_model.pkl')
    
def recognize_and_log(datetoday):
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        faces = extract_faces(frame)

        if len(faces) > 0:
            (x, y, w, h) = faces[0]

            face = cv2.resize(frame[y:y+h, x:x+w], (50, 50))
            identified_person = identify_face(face.reshape(1, -1))[0]

            cv2.putText(frame, str(identified_person), (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

        cv2.imshow("Recognition", frame)

        key = cv2.waitKey(1)

        if key == 13:
            user_id = str(identified_person)
            username = get_username_from_db(user_id)
            add_logs(user_id, username)
            break

        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


