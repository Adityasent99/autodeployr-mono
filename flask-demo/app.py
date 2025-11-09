from flask import Flask, jsonify, request
from flask_cors import CORS
import os, shutil, tempfile, zipfile
from urllib.parse import urlparse
import requests

app = Flask(__name__)
CORS(app)

@app.get("/")
def home():
    return jsonify({"message": "AutoDeployr Backend Running"}), 200

@app.get("/health")
def health():
    return jsonify({"status": "healthy"}), 200

def github_zip_url(repo_url: str) -> str:
    parsed = urlparse(repo_url)
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL")

    owner, repo = parts[0], parts[1]
    branch = "main"
    if len(parts) >= 4 and parts[2] == "tree":
        branch = parts[3]

    return f"https://codeload.github.com/{owner}/{repo}/zip/{branch}"

@app.post("/deploy-static")
def deploy_static():
    try:
        data = request.get_json(silent=True) or {}
        repo_url = data.get("url", "").strip()
        if not repo_url:
            return jsonify({"error": "Missing 'url'"}), 400

        zip_url = github_zip_url(repo_url)
        r = requests.get(zip_url, timeout=60)
        if r.status_code != 200:
            return jsonify({"error": "Could not download repo ZIP"}), 400

        tmp_dir = tempfile.mkdtemp(prefix="autodeployr_")
        zip_path = os.path.join(tmp_dir, "repo.zip")
        with open(zip_path, "wb") as f:
            f.write(r.content)

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_dir)

        extracted_roots = [d for d in os.listdir(tmp_dir) if os.path.isdir(os.path.join(tmp_dir, d))]
        if not extracted_roots:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return jsonify({"error": "ZIP extraction failed"}), 500

        repo_root = os.path.join(tmp_dir, extracted_roots[0])

        static_root = None
        for root, dirs, files in os.walk(repo_root):
            if "index.html" in files:
                static_root = root
                break

        if not static_root:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return jsonify({"error": "No index.html found"}), 400

        return jsonify({
            "status": "ok",
            "repo_root": repo_root,
            "static_root": static_root
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)

