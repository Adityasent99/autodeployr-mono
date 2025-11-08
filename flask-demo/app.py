from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import io, re, shutil, tempfile, zipfile
from urllib.parse import urlparse
import requests
import base64
import json
import random
import string


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
VERCEL_TOKEN = os.environ.get("VERCEL_TOKEN")

def random_suffix(n=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

def deploy_to_vercel(static_root):
    if not VERCEL_TOKEN:
        raise RuntimeError("Missing VERCEL_TOKEN environment variable")

    project_name = f"autodeployr-auto-{random_suffix()}"

    # 1) Create a Vercel project
    r = requests.post(
        "https://api.vercel.com/v9/projects",
        headers={
            "Authorization": f"Bearer {VERCEL_TOKEN}",
            "Content-Type": "application/json"
        },
        json={"name": project_name}
    )

    if r.status_code not in (200, 201):
        raise RuntimeError(f"Project creation failed: {r.text}")

    # 2) Upload static files
    files = {}
    for root, _, filenames in os.walk(static_root):
        for f in filenames:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, static_root)
            with open(full, "rb") as fp:
                files[rel] = base64.b64encode(fp.read()).decode()

    deploy_payload = {
        "project": project_name,
        "files": [{"file": path, "data": content} for path, content in files.items()]
    }

    r = requests.post(
        "https://api.vercel.com/v13/deployments",
        headers={
            "Authorization": f"Bearer {VERCEL_TOKEN}",
            "Content-Type": "application/json"
        },
        data=json.dumps(deploy_payload)
    )

    if r.status_code not in (200, 201):
        raise RuntimeError(f"Deployment failed: {r.text}")

    deployment = r.json()
    return f"https://{deployment['url']}"


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

        deployed_url = deploy_to_vercel(static_root)

        shutil.rmtree(repo_path, ignore_errors=True)

        return jsonify({
            "status": "deployed",
            "url": deployed_url
        }), 200

       

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------ SERVER START ------------ #

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

