from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import requests


app = Flask(__name__)

CORS(app)

@app.route('/')
def hello():
    return jsonify({
        'message': 'Hello from AutoDeploy AI Flask Demo!',
        'framework': 'Flask',
        'status': 'running'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})
import requests

@app.route('/analyze-repo')
def analyze_repo():
    repo_url = request.args.get('url')
    if not repo_url:
        return jsonify({"error": "No URL provided"}), 400

    # Convert GitHub URL to raw content API
    # Example: https://github.com/user/repo -> https://api.github.com/repos/user/repo/contents
    try:
        parts = repo_url.rstrip('/').split('/')
        owner, repo = parts[-2], parts[-1]
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    except:
        return jsonify({"error": "Invalid GitHub URL format"}), 400

    response = requests.get(api_url)

    if response.status_code != 200:
        return jsonify({"error": "Unable to access repository"}), 400

    files = [item['name'] for item in response.json()]

    if 'index.html' in files:
        return jsonify({
            "type": "static-site",
            "deploy_target": "vercel",
            "deployable": True
        })
    else:
        return jsonify({
            "deployable": False,
            "reason": "No index.html found in repository"
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
