"""Flask face-recognition API.

Loads a set of known faces from the reference_images/ folder on startup and
exposes a single endpoint that reports which of those known people appear in an
uploaded image.
"""

from flask import Flask, jsonify, request
import cv2
import face_recognition
import numpy as np
import os

app = Flask(__name__)

# Folder holding one reference photo per known person.
reference_images_folder = 'reference_images'
reference_encodings = []


def load_reference_encodings(folder):
    """Encode the first face in each image in ``folder``.

    Returns a list of ``{'image_name', 'encoding'}`` dicts. Files that contain
    no detectable face are skipped rather than raising, so a bad reference image
    can't take the whole app down at startup.
    """
    encodings = []
    for filename in os.listdir(folder):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(folder, filename)
            reference_image = face_recognition.load_image_file(image_path)
            found = face_recognition.face_encodings(reference_image)
            if not found:
                continue
            encodings.append({'image_name': filename, 'encoding': found[0]})
    return encodings


# Encode the reference set once, at startup.
reference_encodings = load_reference_encodings(reference_images_folder)
