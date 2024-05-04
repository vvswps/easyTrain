from flask import Flask, render_template, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
from zipfile import ZipFile
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras.models import load_model
import subprocess
import json
from google.cloud import firestore
from PIL import Image
import io

app = Flask(__name__)

# db = firestore.Client()

# Replace with your desired upload location for now
UPLOAD_FOLDER = "uploads"
IMAGE_SIZE = 224
# delete all files and folders in the uploads folder
subprocess.run(["rm", "-rf", UPLOAD_FOLDER])

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CLASSNAMES = []


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
    from train import start_training

    data = request.get_json()
    classNames = data["classNames"]
    global CLASSNAMES
    CLASSNAMES = classNames
    data_dir = "uploads"
    try:
        start_training(data_dir, classNames)
        return json.dumps({"success": True}), 200
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}), 500


@app.route("/predict", methods=["POST"])
def predict():
    try:
        if "image" not in request.files:
            print("No image provided")
            return jsonify(error="No image provided"), 400

        print("Model name: ", f"predict_{'_'.join(CLASSNAMES)}.keras")
        model = load_model(f"predict_{'_'.join(CLASSNAMES)}.keras")

        image = request.files["image"].read()
        image = Image.open(io.BytesIO(image))
        image = image.resize((IMAGE_SIZE, IMAGE_SIZE))
        image = img_to_array(image)
        image = np.expand_dims(image, axis=0)

        prediction = model.predict(image)
        predicted_class = np.argmax(prediction, axis=1)

        print("Prediction: ", CLASSNAMES[predicted_class[0]])
        return jsonify(prediction=CLASSNAMES[predicted_class[0]]), 200
    except Exception as e:
        print("Error: ", str(e))
        return jsonify(error=str(e)), 500


@app.route("/upload_images", methods=["POST"])
def upload_images():
    if "zip" in request.files:  # Check for a zip file
        zipfile = request.files["zip"]
        zip_filename = secure_filename(zipfile.filename)
        # zip_filepath = os.path.join(app.config["UPLOAD_FOLDER"], zip_filename)
        # zipfile.save(zip_filepath)

        # Extract images
        with ZipFile(zipfile, "r") as zip:
            extract_folder = os.path.splitext(zip_filename)[
                0
            ]  # Create folder from zip name
            extract_path = os.path.join(app.config["UPLOAD_FOLDER"], extract_folder)
            os.makedirs(extract_path, exist_ok=True)  # Create the folder
            zip.extractall(extract_path)

        return jsonify({"message": "Images extracted successfully"}), 200
    else:
        return jsonify({"error": "Invalid request"}), 400


@app.route("/download_model", methods=["GET"])
def download_model():
    model_name = f"predict_{'_'.join(CLASSNAMES)}.keras"
    try:
        return send_file(model_name, as_attachment=True)
    except Exception as e:
        print("Error: ", str(e))
        return jsonify(error=str(e)), 500


if __name__ == "__main__":
    app.run(debug=True)
