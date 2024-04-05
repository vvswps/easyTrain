from flask import Flask, render_template, request, send_from_directory
import os
from werkzeug.utils import secure_filename

# Import TensorFlow/Keras for the placeholder model for now
import tensorflow as tf
from tensorflow import keras
from keras.models import load_model
import subprocess
import json
from google.cloud import firestore

app = Flask(__name__)

# db = firestore.Client()

# Replace with your desired upload location for now
UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def preprocess_image(image, target_size):
    # Assuming image is a PIL Image object or similar
    image = image.resize(target_size)
    image = tf.keras.preprocessing.image.img_to_array(image)
    image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
    return image


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return "No image uploaded", 400

    image_file = request.files["image"]
    filename = secure_filename(image_file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image_file.save(filepath)
    return "Image uploaded successfully!", 200


@app.route("/train", methods=["POST"])
def train_model():
    try:
        result = subprocess.run(["python", "train.py"], capture_output=True, text=True)
        output = result.stdout
        error = result.stderr

        if error:
            return json.dumps({"success": False, "error": error}), 500
        else:
            return json.dumps({"success": True, "message": output}), 200
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}), 500


@app.route("/predict", methods=["POST"])
def predict():
    # Placeholder until you integrate an actual model
    if "image" not in request.files:
        return "No image provided", 400

    # ... (Load your model, process image, generate prediction) ...
    return "Prediction: ...", 200


if __name__ == "__main__":
    app.run(debug=True)
