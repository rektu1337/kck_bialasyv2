from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

# Ścieżka do pliku profiles.json zlokalizowanego w głównym katalogu projektu
PROFILES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "profiles.json")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/profiles')
def get_profiles():
    if os.path.exists(PROFILES_PATH):
        with open(PROFILES_PATH, 'r') as f:
            try:
                return jsonify(json.load(f))
            except json.JSONDecodeError:
                return jsonify({})
    return jsonify({})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
