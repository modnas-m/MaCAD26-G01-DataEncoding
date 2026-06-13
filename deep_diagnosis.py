import pandas as pd
import numpy as np
import joblib
import os

base_dir = r'C:\Users\maria\Documents\GitHub\MaCAD26-G01-DataEncoding - Barcelona\MaCAD26-G01-DataEncoding-BarcelonaVersion'
model_dir = os.path.join(base_dir, 'models')
output_dir = os.path.join(base_dir, 'output', 'eixample_barcelona_spain')
csv_path = os.path.join(output_dir, 'eixample_barcelona_spain_classified.csv')

# Load model and scaler
scaler = joblib.load(os.path.join(model_dir, 'scaler.pkl'))
model = joblib.load(os.path.join(model_dir, 'logistic_regression.pkl'))

print('=== SCALER INFO ===')
if hasattr(scaler, 'feature_names_in_'):
    print(f'Scaler feature_names_in_: {list(scaler.feature_names_in_)}')
    print(f'N features: {len(scaler.feature_names_in_)}')
else:
    print('No feature_names_in_ attribute')

print(f'Scaler scale_ shape: {scaler.scale_.shape}')
print(f'Scaler mean_ shape: {scaler.mean_.shape}')

print('\n=== MODEL INFO ===')
print(f'Model coef_ shape: {model.coef_.shape}')
print(f'Model classes: {list(model.classes_)}')

# Expected features
feature_cols = [
    'lighting_norm',
    'visibility_norm',
    'connectivity_norm',
    'enclosure_norm',
    'dominant_land_use_score_norm',
    'public_transport_proximity_m_norm',
    'pedestrian_priority_score_norm',
]

print(f'\nExpected {len(feature_cols)} features:')
for i, feat in enumerate(feature_cols):
    print(f'  {i}: {feat}')

# Load data and check
df = pd.read_csv(csv_path)
X = df[feature_cols].fillna(0).values

print(f'\n=== DATA CHECK ===')
print(f'Data shape: {X.shape}')
print(f'Data types: {X.dtype}')
print(f'Pedestrian priority (col 6) stats:')
print(f'  Min: {X[:, 6].min():.6f}')
print(f'  Max: {X[:, 6].max():.6f}')
print(f'  Mean: {X[:, 6].mean():.6f}')
print(f'  Std: {X[:, 6].std():.6f}')

# Try to scale it
print(f'\n=== SCALING TEST ===')
X_scaled = scaler.transform(X)
print(f'Scaled pedestrian priority (col 6) stats:')
print(f'  Min: {X_scaled[:, 6].min():.6f}')
print(f'  Max: {X_scaled[:, 6].max():.6f}')
print(f'  Mean: {X_scaled[:, 6].mean():.6f}')
print(f'  Std: {X_scaled[:, 6].std():.6f}')

# Get predictions
print(f'\n=== PREDICTIONS ===')
proba = model.predict_proba(X_scaled)
print(f'Predicted probabilities shape: {proba.shape}')
print(f'First 3 rows:')
for i in range(min(3, len(proba))):
    print(f'  Sample {i}: {proba[i]}')

# Check if pedestrian priority has any contribution
print(f'\n=== MODEL COEFFICIENTS (detailed) ===')
for class_idx, class_name in enumerate(model.classes_):
    coefs = model.coef_[class_idx]
    print(f'\nClass: {class_name}')
    print(f'Intercept: {model.intercept_[class_idx]:.6f}')
    for feat_idx, feat in enumerate(feature_cols):
        coef = coefs[feat_idx]
        print(f'  {feat_idx}: {feat:35s} = {coef:10.6f}')
