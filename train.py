import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import joblib
import os

# Configuration
DEFAULT_DATA_PATH = 'data/User1_Cleaned.csv'
DEFAULT_MODEL_DIR = 'models'

def parse_time(t):
    """Convert game length string (e.g., '07m 04s') to total seconds."""
    if pd.isna(t) or t == '-':
        return 0
    parts = str(t).replace('s', '').split('m ')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    return 0

def load_data(filepath=DEFAULT_DATA_PATH):
    """Load data from CSV file."""
    return pd.read_csv(filepath)

def engineer_features(data):
    """Apply feature engineering and preprocessing."""
    df_clean = data.copy()
    
    # Target 1: Survival (1 if Not Murdered AND Not Ejected, else 0)
    df_clean['Survived'] = ((df_clean['Murdered'] == 'No') & (df_clean['Ejected'] == 'No')).astype(int)
    
    # Target 2: Sabotages Fixed (handle N/A and hyphens)
    df_clean['Sabotages Fixed'] = pd.to_numeric(
        df_clean['Sabotages Fixed'].replace(['N/A', '-'], 0), errors='coerce'
    ).fillna(0)
    
    # Feature: Convert Game Length to total seconds
    df_clean['Game Length Sec'] = df_clean['Game Length'].apply(parse_time)
    
    # Clean up numeric features with hyphens
    df_clean['Task Completed'] = pd.to_numeric(df_clean['Task Completed'].replace('-', 0), errors='coerce').fillna(0)
    df_clean['Imposter Kills'] = pd.to_numeric(df_clean['Imposter Kills'].replace('-', 0), errors='coerce').fillna(0)
    
    return df_clean

def build_preprocessor():
    """Build the scikit-learn preprocessor pipeline."""
    categorical_features = ['Team']
    numeric_features = ['Task Completed', 'Imposter Kills', 'Game Length Sec']
    
    return ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])

def build_models(preprocessor):
    """Build the survival and sabotage prediction models."""
    survive_pipe = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    sabotage_pipe = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    
    return survive_pipe, sabotage_pipe

def train_and_serialize(data_path=DEFAULT_DATA_PATH, model_dir=DEFAULT_MODEL_DIR):
    """Load data, engineer features, train models, and save to disk."""
    # Load and process data
    df = load_data(data_path)
    df_processed = engineer_features(df)
    
    # Define features and targets
    X = df_processed[['Team', 'Task Completed', 'Imposter Kills', 'Game Length Sec']]
    y_survive = df_processed['Survived']
    y_sabotage = df_processed['Sabotages Fixed']
    
    # Build and train models
    preprocessor = build_preprocessor()
    survive_pipe, sabotage_pipe = build_models(preprocessor)
    
    X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(X, y_survive, test_size=0.2, random_state=42)
    survive_pipe.fit(X_train_s, y_train_s)
    
    X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(X, y_sabotage, test_size=0.2, random_state=42)
    sabotage_pipe.fit(X_train_b, y_train_b)
    
    # Save models
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(survive_pipe, os.path.join(model_dir, 'survive_model.pkl'))
    joblib.dump(sabotage_pipe, os.path.join(model_dir, 'sabotage_model.pkl'))
    
    return survive_pipe, sabotage_pipe

if __name__ == '__main__':
    train_and_serialize()
    print("Pipelines trained and serialized successfully!")