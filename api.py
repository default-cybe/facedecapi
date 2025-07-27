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
