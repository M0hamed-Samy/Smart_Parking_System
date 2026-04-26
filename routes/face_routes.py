from flask import Blueprint, render_template
from services.face_service import *
from services.log_service import *
import cv2
import os
from datetime import date
import time

face = Blueprint('face', __name__)

datetoday2 = date.today().strftime("%d-%B-%Y")

@face.route('/start')
def start():

    names, rolls, times, l = extract_logs()

    if 'face_recognition_model.pkl' not in os.listdir('static'):
        return render_template(
            'home.html',
            names=names, rolls=rolls, times=times, l=l,
            totalreg=len(os.listdir('static/faces')),
            datetoday2=datetoday2,
            mess='No trained model'
        )

    cap = cv2.VideoCapture(0)

    last_user = None
    last_time = 0
    cooldown = 5  # seconds

    while True:
        ret, frame = cap.read()
        faces = extract_faces(frame)

        if len(faces) > 0:
            x, y, w, h = faces[0]

            face_img = cv2.resize(frame[y:y+h, x:x+w], (50, 50))
            user_id = identify_face(face_img.reshape(1, -1))[0]

            current_time = time.time()

            # 🚫 ignore unknown
            if user_id != "Unknown":

                # ⏱️ cooldown + no spam logs
                if user_id != last_user or (current_time - last_time > cooldown):

                    username = get_username_from_db(user_id)
                    add_logs(user_id, username)

                    print(f"Logged: {username}")

                    last_user = user_id
                    last_time = current_time

        cv2.imshow("Logs", frame)

        key = cv2.waitKey(1)

        if key == 13:  # ENTER
            break

        if key == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()

    names, rolls, times, l = extract_logs()

    return render_template(
        'home.html',
        names=names,
        rolls=rolls,
        times=times,
        l=l,
        totalreg=len(os.listdir('static/faces')),
        datetoday2=datetoday2
    )