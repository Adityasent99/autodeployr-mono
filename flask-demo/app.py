from flask import Flask, jsonify
from flask_cors import CORS

import os

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
