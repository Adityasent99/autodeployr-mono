from flask import Flask, jsonify, request from flask_cors import CORS import os import tempfile import shutil 
import zipfile import requests import json import base64

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
            return jsonify({"error": "No repo URL provided"}), 400

        # Download repo ZIP
        repo_zip_url = repo_url.rstrip('/') + '/archive/refs/heads/main.zip'
        response = requests.get(repo_zip_url)

        if response.status_code != 200:
            return jsonify({"error": "Could not download repo ZIP"}), 400

        tmp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(tmp_dir, "repo.zip")

        with open(zip_path, "wb") as f:
            f.write(response.content)

        # Extract ZIP
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)

        # Find extracted folder name
        dirs = [d for d in os.listdir(tmp_dir) if os.path.isdir(os.path.join(tmp_dir, d))]
        repo_path = os.path.join(tmp_dir, dirs[0])

        # Detect folder containing index.html
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
            "repo_name": dirs[0],
            "static_root": static_root
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

