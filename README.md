# facedecapi

A small Flask API for face recognition. It loads a set of known faces from a
`reference_images/` folder on startup, then accepts an uploaded image and reports
which of the known people (if any) appear in it.

Built on top of [`face_recognition`](https://github.com/ageitgey/face_recognition)
(dlib) for the encoding/matching and OpenCV for image decoding.

## How it works

At startup the app scans `reference_images/` for `.jpg`, `.jpeg` and `.png`
files, computes a 128-dimension face encoding for the first face found in each
one, and keeps them in memory keyed by filename. When a request comes in, every
face detected in the uploaded image is compared against all of the reference
encodings and the matching filenames are returned.

