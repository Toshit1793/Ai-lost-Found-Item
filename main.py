# AI-Powered Lost & Found - Flask API with Image Matching

import os
import numpy as np
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load pretrained model (without final classification layer)
base_model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

# Function to convert image to embedding
def get_image_embedding(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_data = image.img_to_array(img)
    img_data = np.expand_dims(img_data, axis=0)
    img_data = preprocess_input(img_data)
    embedding = base_model.predict(img_data)
    return embedding[0]

# Route to handle image match
@app.route('/match', methods=['POST'])
def match_images():
    if 'lost_image' not in request.files:
        return jsonify({"error": "No lost image uploaded"}), 400

    lost_file = request.files['lost_image']
    found_files = request.files.getlist('found_images')

    lost_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(lost_file.filename))
    lost_file.save(lost_path)

    found_paths = []
    for f in found_files:
        path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
        f.save(path)
        found_paths.append(path)

    # Matching logic
    lost_embedding = get_image_embedding(lost_path)
    found_embeddings = [get_image_embedding(p) for p in found_paths]
    similarities = cosine_similarity([lost_embedding], found_embeddings)[0]
    best_idx = int(np.argmax(similarities))
    best_match = found_paths[best_idx]
    score = float(similarities[best_idx])

    return jsonify({
        "best_match": os.path.basename(best_match),
        "confidence": round(score, 2)
    })

if __name__ == '__main__':
    app.run(debug=True)
