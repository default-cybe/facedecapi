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


@app.route('/process_image', methods=['POST'])
def process_image():
    """Detect faces in the uploaded image and match them against the references.

    Expects a multipart upload with an ``image`` field. Returns a JSON array
    with one entry per detected face, or an empty array when none are found.
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    try:
        # Read the image from the request
        image = request.files['image'].read()
        nparr = np.frombuffer(image, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Convert frame from BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Find all face locations and encodings in the frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        results = []

        # If no faces are found, return an empty result
        if len(face_encodings) == 0:
            return jsonify([])

        # Compare each face encoding with the reference encodings
        for face_encoding in face_encodings:
            # Compare the current face encoding with the reference encodings
            matches = []
            for ref_encoding in reference_encodings:
                match = face_recognition.compare_faces([ref_encoding['encoding']], face_encoding)
                if True in match:
                    matches.append(ref_encoding['image_name'])

            if matches:
                results.append({'match': True, 'image_names': matches})
            else:
                results.append({'match': False, 'image_names': ['unknown']})

        return jsonify(results)

    except Exception as e:
        # Handle errors gracefully
