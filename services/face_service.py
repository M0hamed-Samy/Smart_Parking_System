import os
import pickle

import tkinter as tk
from tkinter import messagebox
import face_recognition


def recognize(img_path, db_path):

    img = face_recognition.load_image_file(img_path)

    embeddings_unknown = face_recognition.face_encodings(img)

    if len(embeddings_unknown) == 0:
        return 'no_persons_found'

    embeddings_unknown = embeddings_unknown[0]

    db_dir = sorted(os.listdir(db_path))

    match = False
    j = 0

    while not match and j < len(db_dir):

        path_ = os.path.join(db_path, db_dir[j])

        with open(path_, 'rb') as file:
            embeddings = pickle.load(file)

        match = face_recognition.compare_faces(
            [embeddings],
            embeddings_unknown
        )[0]

        j += 1

    if match:
        return db_dir[j - 1].replace(".pkl", "")

    return 'unknown_person'