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

# Load data
df = pd.read_csv(csv_path)

# Expected features in the notebook
feature_cols = [
    'lighting_norm',
    'visibility_norm',
    'connectivity_norm',
    'enclosure_norm',
    'dominant_land_use_score_norm',
    'public_transport_proximity_m_norm',
    'pedestrian_priority_score_norm',
]

feature_labels = [
    'Lighting',
    'Visibility',
    'Connectivity',
    'Enclosure',
    'Land Use',
    'Transit Proximity',
    'Pedestrian Priority',
]

print('=== MODEL & SCALER INFO ===\n')

# Get X and scale it
X = df[feature_cols].fillna(0).values
X_scaled = scaler.transform(X)

print(f'Model classes: {list(model.classes_)}')
print(f'Model coefficients shape: {model.coef_.shape}')

# Print model coefficients
print(f'\nModel Coefficients (by class):')
for class_idx, class_name in enumerate(model.classes_):
    print(f'\n{class_name.upper()} risk:')
    for feat_idx, feat_label in enumerate(feature_labels):
        coef_val = model.coef_[class_idx, feat_idx]
        print(f'  {feat_label:18} : {coef_val:10.6f}')

# Check scaled values for pedestrian priority
ped_idx = 6  # pedestrian_priority_score_norm is index 6
print(f'\n=== PEDESTRIAN PRIORITY SCALED VALUES ===')
ped_scaled = X_scaled[:, ped_idx]
print(f'Min/Max: {ped_scaled.min():.6f} / {ped_scaled.max():.6f}')
print(f'Mean: {ped_scaled.mean():.6f}')
print(f'Std: {ped_scaled.std():.6f}')
print(f'Unique values: {len(np.unique(ped_scaled))}')
print(f'First 10 values: {ped_scaled[:10]}')

# Compare with other features
print(f'\n=== ALL FEATURES SCALED STATISTICS ===')
for feat_idx, feat_label in enumerate(feature_labels):
    feat_scaled = X_scaled[:, feat_idx]
    print(f'{feat_label:18}: min={feat_scaled.min():8.4f}, max={feat_scaled.max():8.4f}, std={feat_scaled.std():8.4f}')
