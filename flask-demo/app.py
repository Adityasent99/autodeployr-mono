from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import tempfile
import shutil
import zipfile
import requests
import json
import base64

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "AutoDeployr Backend Running"}), 200

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/deploy-static', methods=['POST'])
def deploy_static():
    try:
@app.route('/deploy-static', methods=['POST'])
def deploy_static():
    try:
        data = request.get_json()
        repo_url = data.get("url")

        if not repo_url:
            return jsonify({"error": "Missing repo URL"}), 400

        # Create temp workspace
        tmp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(tmp_dir, "repo.zip")

        # Download ZIP
        zip_url = repo_url.rstrip("/") + "/archive/refs/heads/main.zip"
        r = requests.get(zip_url, timeout=20)

        if r.status_code != 200:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return jsonify({"error": "Failed to download repo ZIP"}), 400

        with open(zip_path, "wb") as f:
            f.write(r.content)

        # Extract ZIP
        extract_dir = os.path.join(tmp_dir, "repo")
        os.makedirs(extract_dir, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        # Detect extraction root
        extracted_root = os.listdir(extract_dir)[0]
        repo_path = os.path.join(extract_dir, extracted_root)

        # Detect static root (folder containing index.html)
        static_root = None
        for root, dirs, files in os.walk(repo_path):
            if "index.html" in files:
                static_root = root
                break

        if not static_root:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return jsonify({"error": "No index.html found"}), 400

        return jsonify({
            "status": "ok",
            "repo_name": extracted_root,
            "static_root": static_root
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

