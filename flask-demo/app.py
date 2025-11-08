from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import io, re, shutil, tempfile, zipfile
from urllib.parse import urlparse
import requests

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "AutoDeployr Backend Running"}), 200

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200


# ------------ STATIC SITE DEPLOY ANALYZER (NO GIT) ------------ #

def guess_branch_from_url(url):
    m = re.search(r"/tree/([^/]+)", url)
    return m.group(1) if m else None

def to_codeload_url(repo_url, branch=None):
    u = urlparse(repo_url)
    parts = u.path.strip("/").split("/")
    if len(parts) < 2:
        raise ValueError("Invalid GitHub repo URL format")
    owner, repo = parts[0], parts[1].replace(".git", "")
    br = branch or guess_branch_from_url(repo_url) or "main"
    return f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{br}", owner, repo, br

def download_and_extract(repo_url):
    # Try main → master
    for branch in [guess_branch_from_url(repo_url) or "main", "master"]:
        url, owner, repo, br = to_codeload_url(repo_url, branch)
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            tmpdir = tempfile.mkdtemp(prefix="repo_")
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                z.extractall(tmpdir)
            extracted_root = os.path.join(tmpdir, f"{repo}-{br}")
            return extracted_root, (owner, repo, br)
    raise RuntimeError("Could not download repo ZIP")

def detect_static_root(base):
    for folder in ["dist", "build", "public", ""]:
        path = os.path.join(base, folder) if folder else base
        if os.path.isfile(os.path.join(path, "index.html")):
            return path
    return None

@app.route('/deploy-static', methods=['POST'])
def deploy_static():
    data = request.get_json()
    repo_url = data.get("url")
    if not repo_url:
        return jsonify({"error": "Missing url"}), 400

    try:
        repo_path, meta = download_and_extract(repo_url)
        static_root = detect_static_root(repo_path)

        if not static_root:
            shutil.rmtree(repo_path, ignore_errors=True)
            return jsonify({"error": "No index.html found"}), 400

        shutil.rmtree(repo_path, ignore_errors=True)
        return jsonify({
            "status": "ok",
            "repo_owner": meta[0],
            "repo_name": meta[1],
            "branch": meta[2],
            "static_root_found": True
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------ SERVER START ------------ #

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

