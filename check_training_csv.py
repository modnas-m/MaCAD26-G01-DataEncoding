import pandas as pd
import os

base_dir = r'C:\Users\maria\Documents\GitHub\MaCAD26-G01-DataEncoding - Barcelona\MaCAD26-G01-DataEncoding-BarcelonaVersion'
csv_path = os.path.join(base_dir, 'csv', 'segment_risk_classified.csv')

print(f'Checking: {csv_path}')
print(f'Exists: {os.path.exists(csv_path)}\n')

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    print(f'Shape: {df.shape}')
    print(f'Columns: {list(df.columns)}\n')
    
    # Check for pedestrian priority
    ped_col = 'pedestrian_priority_score_norm'
    if ped_col in df.columns:
        print(f'✓ Column "{ped_col}" found')
        print(f'  Unique values: {df[ped_col].nunique()}')
        print(f'  Min/Max: {df[ped_col].min():.6f} / {df[ped_col].max():.6f}')
        print(f'  Mean: {df[ped_col].mean():.6f}')
        print(f'  Std: {df[ped_col].std():.6f}')
        print(f'  NaN count: {df[ped_col].isna().sum()}')
        print(f'  All zeros?: {(df[ped_col] == 0).all()}')
        print(f'  All same value?: {df[ped_col].nunique() == 1}')
    else:
        print(f'✗ Column "{ped_col}" NOT FOUND')
        print('Available columns:')
        for col in df.columns:
            print(f'  - {col}')
