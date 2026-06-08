import pytest
import json
from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'

def test_model_info(client):
    """Test the model info endpoint."""
    response = client.get('/model-info')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'model_version' in data
    assert 'features' in data
    assert 'Team' in data['features']
    assert 'Task Completed' in data['features']
    assert 'Imposter Kills' in data['features']
    assert 'Game Length Sec' in data['features']

def test_predict(client):
    """Test the prediction endpoint."""
    payload = {
        'Team': 'Crewmate',
        'Task Completed': 5,
        'Imposter Kills': 0,
        'Game Length Sec': 300
    }
    
    response = client.post('/predict', 
                          data=json.dumps(payload),
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'survival_percentage' in data
    assert 'predicted_sabotages_fixed' in data
    assert 'confidence_score' in data
    assert 'confidence_band' in data
    assert 0 <= data['survival_percentage'] <= 100
    assert data['confidence_band'] in ['Low', 'Medium', 'High']
