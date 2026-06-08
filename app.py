from datetime import datetime, timezone
import os

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import pandas as pd

from train import train_and_serialize

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

MODEL_VERSION = os.getenv('MODEL_VERSION', '1.0.0-beta')
MODEL_CREATED_AT = os.getenv('MODEL_CREATED_AT', datetime.now(timezone.utc).isoformat())

REQUIRED_FIELDS = ['Team', 'Task Completed', 'Imposter Kills', 'Game Length Sec']
ALLOWED_TEAMS = {'Crewmate', 'Imposter'}

# Global model storage
survive_model = None
sabotage_model = None

def ensure_models():
    """Ensure models exist; train them if missing."""
    global survive_model, sabotage_model
    
    model_dir = 'models'
    survive_path = os.path.join(model_dir, 'survive_model.pkl')
    sabotage_path = os.path.join(model_dir, 'sabotage_model.pkl')
    
    if not os.path.exists(survive_path) or not os.path.exists(sabotage_path):
        print("Models not found. Training models...")
        survive_model, sabotage_model = train_and_serialize()
    else:
        survive_model = joblib.load(survive_path)
        sabotage_model = joblib.load(sabotage_path)
    
    print("Models loaded successfully!")

def validate_payload(data):
    if not isinstance(data, dict):
        return False, 'Payload must be a JSON object.'

    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"

    team = str(data.get('Team', '')).strip()
    if team not in ALLOWED_TEAMS:
        return False, "Team must be either 'Crewmate' or 'Imposter'."

    try:
        tasks = float(data.get('Task Completed', 0))
        kills = float(data.get('Imposter Kills', 0))
        game_length = float(data.get('Game Length Sec', 0))
    except (TypeError, ValueError):
        return False, 'Task Completed, Imposter Kills, and Game Length Sec must be numeric.'

    if tasks < 0 or kills < 0 or game_length < 0:
        return False, 'Numeric values must be non-negative.'

    if game_length > 7200:
        return False, 'Game Length Sec looks too large. Please use a value up to 7200 seconds.'

    return True, None


def build_confidence(survive_prob):
    # Confidence score reflects how far probability is from the decision boundary.
    confidence_score = round(abs(survive_prob - 50.0) * 2, 2)
    if confidence_score >= 70:
        confidence_band = 'High'
    elif confidence_score >= 40:
        confidence_band = 'Medium'
    else:
        confidence_band = 'Low'
    return confidence_score, confidence_band


@app.route('/', methods=['GET'])
def serve_home():
    """Serve the main HTML page."""
    return send_from_directory('.', 'index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({'status': 'ok'}), 200

@app.route('/model-info', methods=['GET'])
def model_info():
    return jsonify({
        'status': 'success',
        'model_version': MODEL_VERSION,
        'trained_at_utc': MODEL_CREATED_AT,
        'features': REQUIRED_FIELDS,
        'targets': ['survival_percentage', 'predicted_sabotages_fixed'],
        'models': {
            'survival': 'models/survive_model.pkl',
            'sabotage': 'models/sabotage_model.pkl'
        }
    })

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Extract JSON payload
        data = request.get_json(silent=True)

        is_valid, error_message = validate_payload(data)
        if not is_valid:
            return jsonify({'status': 'error', 'message': error_message}), 400

        clean_data = {
            'Team': str(data['Team']).strip(),
            'Task Completed': float(data['Task Completed']),
            'Imposter Kills': float(data['Imposter Kills']),
            'Game Length Sec': float(data['Game Length Sec'])
        }
        
        # Convert to a single-row DataFrame
        df = pd.DataFrame([clean_data])
        
        # Predict survival probability (fetch the probability of class 1)
        survive_prob = survive_model.predict_proba(df)[0][1] * 100
        confidence_score, confidence_band = build_confidence(survive_prob)
        
        # Predict number of sabotages fixed
        sabotage_pred = sabotage_model.predict(df)[0]
        
        return jsonify({
            'status': 'success',
            'model_version': MODEL_VERSION,
            'survival_percentage': round(survive_prob, 2),
            'predicted_sabotages_fixed': round(sabotage_pred, 2),
            'confidence_score': confidence_score,
            'confidence_band': confidence_band
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    ensure_models()
    app.run(host='0.0.0.0', port=5000, debug=True)