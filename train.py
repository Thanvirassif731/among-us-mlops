import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import joblib
import os

# 1. Load Data (assuming you use one of the user CSVs)
df = pd.read_csv('data/User1_Cleaned.csv')  # Update with the actual cleaned data file path

# 2. Feature Engineering & Preprocessing
def engineer_features(data):
    df_clean = data.copy()
    
    # Target 1: Survival (1 if Not Murdered AND Not Ejected, else 0)
    df_clean['Survived'] = ((df_clean['Murdered'] == 'No') & (df_clean['Ejected'] == 'No')).astype(int)
    
    # Target 2: Sabotages Fixed (handle N/A and hyphens)
    df_clean['Sabotages Fixed'] = pd.to_numeric(
        df_clean['Sabotages Fixed'].replace(['N/A', '-'], 0), errors='coerce'
    ).fillna(0)
    
    # Feature: Convert Game Length (e.g., '07m 04s') to total seconds
    def parse_time(t):
        if pd.isna(t) or t == '-': return 0
        parts = str(t).replace('s', '').split('m ')
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        return 0
        
    df_clean['Game Length Sec'] = df_clean['Game Length'].apply(parse_time)
    
    # Clean up numeric features with hyphens
    df_clean['Task Completed'] = pd.to_numeric(df_clean['Task Completed'].replace('-', 0), errors='coerce').fillna(0)
    df_clean['Imposter Kills'] = pd.to_numeric(df_clean['Imposter Kills'].replace('-', 0), errors='coerce').fillna(0)
    
    return df_clean

df_processed = engineer_features(df)

# 3. Define Features and Targets
X = df_processed[['Team', 'Task Completed', 'Imposter Kills', 'Game Length Sec']]
y_survive = df_processed['Survived']
y_sabotage = df_processed['Sabotages Fixed']

# 4. Scikit-Learn Pipelines
categorical_features = ['Team']
numeric_features = ['Task Completed', 'Imposter Kills', 'Game Length Sec']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

# Model 1: Classifier for Survival Percentage
survive_pipe = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
])

# Model 2: Regressor for Sabotages
sabotage_pipe = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
])

# 5. Train Models
X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(X, y_survive, test_size=0.2, random_state=42)
survive_pipe.fit(X_train_s, y_train_s)

X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(X, y_sabotage, test_size=0.2, random_state=42)
sabotage_pipe.fit(X_train_b, y_train_b)

# 6. Export Artifacts for Production
os.makedirs('models', exist_ok=True)
joblib.dump(survive_pipe, 'models/survive_model.pkl')
joblib.dump(sabotage_pipe, 'models/sabotage_model.pkl')
print("Pipelines trained and serialized successfully!")