from requirments import *

app = Flask(__name__)

nimgs = 10



imgBackground=cv2.imread("background.png")

datetoday = date.today().strftime("%m_%d_%y")
datetoday2 = date.today().strftime("%d-%B-%Y")


face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


if not os.path.isdir('Logs'):
    os.makedirs('Logs')
if not os.path.isdir('static'):
    os.makedirs('static')
if not os.path.isdir('static/faces'):
    os.makedirs('static/faces')
if f'Logs-{datetoday}.csv' not in os.listdir('Logs'):
    with open(f'Logs/Logs-{datetoday}.csv', 'w') as f:
        f.write('Name,Roll,Time\n')   # 👈 مهم جدًا

def totalreg():
    return len(os.listdir('static/faces'))

def extract_faces(img):
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_points = face_detector.detectMultiScale(gray, 1.2, 5, minSize=(20, 20))
        return face_points
    except:
        return []

def identify_face(facearray):
    model = joblib.load('static/face_recognition_model.pkl')
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

def extract_logs():
    conn = sqlite3.connect("database/system.db")
    cur = conn.cursor()

    cur.execute("SELECT name, user_id, time FROM logs ORDER BY id DESC")
    rows = cur.fetchall()

    conn.close()

    names = [r[0] for r in rows]
    rolls = [r[1] for r in rows]
    times = [r[2] for r in rows]

    return names, rolls, times, len(rows)

def add_logs(user_id, username):
    current_time = datetime.now().strftime("%H:%M:%S")

    conn = sqlite3.connect("database/system.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO logs (user_id, name, time, date)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, current_time, datetoday))

    conn.commit()
    conn.close()
    
    
def get_username_from_db(user_id):
    conn = sqlite3.connect("database/system.db")
    cur = conn.cursor()

    cur.execute("SELECT name FROM users WHERE id=?", (user_id,))
    result = cur.fetchone()

    conn.close()
    return result[0] if result else "Unknown"
    
def getallusers():
    userlist = os.listdir('static/faces')
    names = []
    rolls = []
    l = len(userlist)

    for i in userlist:
        name, roll = i.split('_')
        names.append(name)
        rolls.append(roll)

    return userlist, names, rolls, l


@app.route('/')
def home():
    names, rolls, times, l = extract_logs()
    return render_template('home.html', names=names, rolls=rolls, times=times, l=l, totalreg=totalreg(), datetoday2=datetoday2)

@app.route('/start', methods=['GET'])
def start():
    names, rolls, times, l = extract_logs()

    if 'face_recognition_model.pkl' not in os.listdir('static'):
        return render_template('home.html', names=names, rolls=rolls, times=times, l=l, totalreg=totalreg(), datetoday2=datetoday2, mess='There is no trained model in the static folder. Please add a new face to continue.')

    ret = True
    cap = cv2.VideoCapture(0)
    while ret:
        ret, frame = cap.read()

        faces = extract_faces(frame)

        if len(faces) > 0:
            (x, y, w, h) = faces[0]

            cv2.rectangle(frame, (x, y), (x+w, y+h), (86, 32, 251), 2)

            face = cv2.resize(frame[y:y+h, x:x+w], (50, 50))
            identified_person = identify_face(face.reshape(1, -1))[0]

            cv2.putText(frame, f'{identified_person}', (x, y-15),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 2)

            cv2.putText(frame, "Press ENTER to mark log",
                        (30, 60), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 255, 0), 2)

        cv2.imshow('Logs', frame)

        key = cv2.waitKey(1)

        # ⬇️ ENTER key
        if key == 13:
            if len(faces) > 0:
                user_id = str(identified_person)
                username = get_username_from_db(user_id)
                add_logs(user_id, username)
                print("Logs saved for:", username, user_id)
                break
            
        # ESC to exit
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    names, rolls, times, l = extract_logs()
    return render_template('home.html', names=names, rolls=rolls, times=times, l=l, totalreg=totalreg(), datetoday2=datetoday2)

def add_user_db(name, role):
    conn = sqlite3.connect("database/system.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (name, role, created_at)
        VALUES (?, ?, ?)
    """, (name, role, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    user_id = cur.lastrowid  # 🔥 المهم هنا

    conn.commit()
    conn.close()

    return user_id

@app.route('/add', methods=['POST'])
def add():

    newusername = request.form['newusername']
    role = request.form['role']   # 👈 أضف role بدل newuserid

    # 🔥 create user in DB
    user_id = add_user_db(newusername, role)

    # folder based on DB ID
    userimagefolder = f'static/faces/{user_id}'

    if not os.path.isdir(userimagefolder):
        os.makedirs(userimagefolder)

    i, j = 0, 0
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        faces = extract_faces(frame)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 20), 2)

            cv2.putText(frame,
                        f'Images Captured: {i}/{nimgs}',
                        (30, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1, (255, 0, 20), 2, cv2.LINE_AA)

            if j % 5 == 0:
                name = f"{i}.jpg"
                cv2.imwrite(f"{userimagefolder}/{name}", frame[y:y+h, x:x+w])
                i += 1

            j += 1

        if j == nimgs * 5:
            break

        cv2.imshow('Adding new User', frame)

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

    print("Training Model...")
    train_model()

    names, rolls, times, l = extract_logs()

    return render_template(
        'home.html',
        names=names,
        rolls=rolls,
        times=times,
        l=l,
        totalreg=totalreg(),
        datetoday2=datetoday2
    )
if __name__ == '__main__':
    app.run(debug=True)
