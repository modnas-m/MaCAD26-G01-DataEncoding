import joblib
import os

base_dir = r'C:\Users\maria\Documents\GitHub\MaCAD26-G01-DataEncoding - Barcelona\MaCAD26-G01-DataEncoding-BarcelonaVersion'
model_dir = os.path.join(base_dir, 'models')
scaler = joblib.load(os.path.join(model_dir, 'scaler.pkl'))

print('=== SCALER STATISTICS ===\n')

feature_cols = [
    'lighting_norm',
    'visibility_norm',
    'connectivity_norm',
    'enclosure_norm',
    'dominant_land_use_score_norm',
    'public_transport_proximity_m_norm',
    'pedestrian_priority_score_norm',
]

print('Feature                           Mean (μ)        Std Dev (σ)')
print('─' * 65)
for i, feat in enumerate(feature_cols):
    mean_val = scaler.mean_[i]
    std_val = scaler.scale_[i]
    marker = ' ⚠️' if std_val == 0 or std_val == 1 else ''
    print(f'{feat:35s} {mean_val:12.6f}  {std_val:12.6f}{marker}')

print(f'\n⚠️ ISSUE: Pedestrian Priority has scale_={scaler.scale_[6]:.6f}')
print('This means it was NOT standardized during scaler.fit_transform()')
print('When scale is 1.0 (or any constant), features are not being rescaled.')
