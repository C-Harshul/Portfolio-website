"""Flask server for Portfolio Website Chat Interface - UI only."""

import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Get backend URL from environment or use default (gst-guru-chat backend)
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8001')

# Set static folder to frontend directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)
frontend_dir = os.path.join(project_root, 'frontend')

app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    """Serve the main HTML file."""
    return send_from_directory(frontend_dir, 'index.html')

@app.route('/chat.html')
def chat_page():
    """Serve the chat page."""
    return send_from_directory(frontend_dir, 'chat.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS, etc.)."""
    return send_from_directory(frontend_dir, path)

@app.route('/api/session', methods=['POST'])
def session():
    """Proxy session creation requests to backend session endpoint."""
    try:
        response = requests.post(
            f'{BACKEND_URL}/session',
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Error proxying session request: {str(e)}")
        return jsonify({
            'error': f'Error connecting to backend: {str(e)}'
        }), 500
    except Exception as e:
        print(f"Error processing session request: {str(e)}")
        return jsonify({
            'error': f'Error creating session: {str(e)}'
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Proxy chat API requests to backend query endpoint."""
    try:
        data = request.get_json()
        # Convert message to question format if needed
        payload = {
            'question': data.get('question') or data.get('message', ''),
            'force_refresh': data.get('force_refresh', False)
        }
        # Include session_id if provided
        if data.get('session_id'):
            payload['session_id'] = data.get('session_id')
        response = requests.post(
            f'{BACKEND_URL}/query',
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=120  # 2 minute timeout to match frontend
        )
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Error proxying chat request: {str(e)}")
        return jsonify({
            'error': f'Error connecting to backend: {str(e)}'
        }), 500
    except Exception as e:
        print(f"Error processing chat request: {str(e)}")
        return jsonify({
            'error': f'Error processing your message: {str(e)}'
        }), 500

@app.route('/api/ingest', methods=['POST'])
def ingest():
    """Proxy ingestion API requests to backend."""
    try:
        data = request.get_json()
        response = requests.post(
            f'{BACKEND_URL}/api/ingest',
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=300  # Longer timeout for ingestion
        )
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Error proxying ingest request: {str(e)}")
        return jsonify({
            'error': f'Error connecting to backend: {str(e)}'
        }), 500
    except Exception as e:
        print(f"Error processing ingest request: {str(e)}")
        return jsonify({
            'error': f'Error processing ingestion: {str(e)}'
        }), 500

@app.route('/api/retrieve', methods=['POST'])
def retrieve():
    """Proxy retrieval API requests to backend query endpoint."""
    try:
        data = request.get_json()
        payload = {
            'question': data.get('question') or data.get('message', ''),
            'force_refresh': data.get('force_refresh', False)
        }
        # Include session_id if provided
        if data.get('session_id'):
            payload['session_id'] = data.get('session_id')
        response = requests.post(
            f'{BACKEND_URL}/query',
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=120  # 2 minute timeout to match frontend
        )
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Error proxying retrieve request: {str(e)}")
        return jsonify({
            'error': f'Error connecting to backend: {str(e)}'
        }), 500
    except Exception as e:
        print(f"Error processing retrieve request: {str(e)}")
        return jsonify({
            'error': f'Error processing retrieval: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"Starting UI server on http://0.0.0.0:{port}")
    print(f"Backend URL: {BACKEND_URL}")
    app.run(host='0.0.0.0', port=port, debug=True)

