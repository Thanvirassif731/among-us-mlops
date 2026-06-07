import kagglehub
import pandas as pd
import numpy as np
import os

# ==========================================
# PHASE 1: EXTRACT (Download from Kaggle)
# ==========================================
print("Downloading dataset from Kaggle...")
file_path = kagglehub.dataset_download(
    "ruchi798/among-us-dataset",
    path="User1.csv"
)
print(f"File successfully downloaded to: {file_path}")

# ==========================================
# PHASE 2: TRANSFORM (Clean the Data)
# ==========================================
print("Loading data and starting cleaning pipeline...")
df = pd.read_csv(file_path)

# 1. Replace all hyphens with proper NaN (Not a Number) values
df.replace('-', np.nan, inplace=True)

# 2. Split the 'Region/Game Code' into two separate columns
if 'Region/Game Code' in df.columns:
    df[['Region', 'Game Code']] = df['Region/Game Code'].str.split(' / ', expand=True)
    df.drop('Region/Game Code', axis=1, inplace=True)

# 3. Convert string ranks (+++) into numeric values
def parse_rank_change(val):
    if pd.isna(val): 
        return 0
    val = str(val).strip()
    if '+' in val: 
        return len(val)
    if '-' in val: 
        return -len(val)
    return 0

df['Rank Numeric'] = df['Rank Change'].apply(parse_rank_change)

# 4. Convert '09m 48s' strings into total integer seconds
def parse_time_to_seconds(t):
    if pd.isna(t): 
        return 0
    parts = str(t).replace('s', '').split('m ')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    return 0

if 'Time to complete all tasks' in df.columns:
    df['Game Length Sec'] = df['Time to complete all tasks'].apply(parse_time_to_seconds)

# ==========================================
# PHASE 3: LOAD (Save the Cleaned Data)
# ==========================================
# Ensure the local 'data' folder exists
os.makedirs('data', exist_ok=True)

# Save to a new CSV file
clean_file_path = 'data/User1_Cleaned.csv'
df.to_csv(clean_file_path, index=False)

print("\nCleaning complete! Here is a peek at the sanitized data:")
print(df[['Team', 'Outcome', 'Region', 'Rank Numeric', 'Game Length Sec']].head())
print(f"\n🚀 Ready for training! Cleaned data saved locally at: {clean_file_path}")