import os
import pandas as pd
import numpy as np
import joblib
import shap
from pathlib import Path

BASE_DIR = r'C:\Users\maria\Documents\GitHub\MaCAD26-G01-DataEncoding - Barcelona\MaCAD26-G01-DataEncoding-BarcelonaVersion'
MODEL_DIR = os.path.join(BASE_DIR, 'models')
OUTPUT_ROOT = os.path.join(BASE_DIR, 'output')

# Load CSV for Eixample
output_dir = os.path.join(OUTPUT_ROOT, 'eixample_barcelona_spain')
csv_files = [f for f in os.listdir(output_dir) if f.endswith('_classified.csv')]
csv_path = os.path.join(output_dir, csv_files[0])
df = pd.read_csv(csv_path)

FEATURE_COLS = [
    'lighting_norm',
    'visibility_norm',
    'connectivity_norm',
    'enclosure_norm',
    'dominant_land_use_score_norm',
    'public_transport_proximity_m_norm',
    'pedestrian_priority_score_norm',
]

# Load scaler and model
scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler.pkl'))
model = joblib.load(os.path.join(MODEL_DIR, 'logistic_regression.pkl'))

X = df[FEATURE_COLS].fillna(0).values
X_scaled = scaler.transform(X)
X_df = pd.DataFrame(X_scaled, columns=['Lighting', 'Visibility', 'Connectivity', 'Enclosure', 'Land Use', 'Transit Proximity', 'Pedestrian Priority'])
classes = list(model.classes_)

print("Computing SHAP values...")
explainer = shap.Explainer(model.predict_proba, shap.maskers.Independent(X_df), output_names=classes)
shap_values = explainer(X_df)

print(f"\nSHAP values shape: {shap_values.values.shape}")
print(f"Number of classes: {shap_values.values.shape[2] if len(shap_values.values.shape) == 3 else 1}")

# Get mean absolute SHAP values for each feature (class 0 = high risk)
mean_shap_per_feature = np.abs(shap_values.values[:, :, 0]).mean(axis=0)
print(f"\nMean |SHAP| per feature (class 0 - High Risk):")
for feat_idx, col in enumerate(FEATURE_COLS):
    print(f"  {col:40s}: {mean_shap_per_feature[feat_idx]:.6f}")

# Check pedestrian priority specifically
ped_idx = FEATURE_COLS.index('pedestrian_priority_score_norm')
ped_shap = shap_values.values[:, ped_idx, 0]
print(f"\nPedestrian Priority SHAP values (class 0):")
print(f"  Min: {ped_shap.min():.6f}")
print(f"  Max: {ped_shap.max():.6f}")
print(f"  Mean: {ped_shap.mean():.6f}")
print(f"  Std: {ped_shap.std():.6f}")
print(f"  Mean |SHAP|: {np.abs(ped_shap).mean():.6f}")
print(f"\nFirst 10 SHAP values for pedestrian priority:")
print(ped_shap[:10])
