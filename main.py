# main.py
import sys
import os
import json
import webview
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from backend.screenshot_analyze import ScreenshotAnalyzer
import threading

# Initialize Flask app
app = Flask(__name__, static_folder='frontend/dist', static_url_path='')

# Configure CORS properly
CORS(app, resources={
    r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]},
    r"/screenshots/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}
})

# Add your API key here
API_KEY = "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"
analyzer = ScreenshotAnalyzer(api_key=API_KEY)

# Start the screenshot monitoring in a separate thread
monitor_thread = threading.Thread(target=analyzer.monitor_clipboard, daemon=True)
monitor_thread.start()

@app.route('/')
def serve_root():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/assets/<path:path>')
def serve_assets(path):
    return send_from_directory(os.path.join(app.static_folder, 'assets'), path)

@app.route('/api/analyses')
def get_analyses():
    try:
        # Ensure the screenshots directory exists
        os.makedirs('screenshots', exist_ok=True)
        
        # Ensure the analysis file exists
        analysis_file = os.path.join('screenshots', 'screenshot_analysis.json')
        if not os.path.exists(analysis_file):
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False)
        
        # Read and return the analyses
        with open(analysis_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return jsonify(data)
    except Exception as e:
        print(f"Error loading analyses: {e}")
        # Return empty object on error
        return jsonify({})

@app.route('/screenshots/<path:filename>')
def serve_screenshot(filename):
    try:
        return send_from_directory('screenshots', filename)
    except Exception as e:
        print(f"Error serving screenshot {filename}: {e}")
        return jsonify({'error': str(e)}), 404

def start_app():
    """Start the application in webview mode"""
    webview.create_window('SnapFix', app)
    webview.start()

if __name__ == '__main__':
    # Create screenshots directory if it doesn't exist
    os.makedirs('screenshots', exist_ok=True)
    
    # Create empty JSON file if it doesn't exist
    if not os.path.exists('screenshots/screenshot_analysis.json'):
        with open('screenshots/screenshot_analysis.json', 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False)
    
    if getattr(sys, 'frozen', False):
        start_app()
    else:
        print("Starting development server...")
        # Run the Flask app
        app.run(host='127.0.0.1', port=5000, debug=False)