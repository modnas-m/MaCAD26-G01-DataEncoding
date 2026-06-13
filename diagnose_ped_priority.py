import pandas as pd
import os

# Find the classified CSV
output_dir = r'C:\Users\maria\Documents\GitHub\MaCAD26-G01-DataEncoding - Barcelona\MaCAD26-G01-DataEncoding-BarcelonaVersion\output\eixample_barcelona_spain'
csv_path = os.path.join(output_dir, 'eixample_barcelona_spain_classified.csv')

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    print('=== PEDESTRIAN PRIORITY DIAGNOSTIC ===\n')
    
    ped_col = 'pedestrian_priority_score_norm'
    if ped_col in df.columns:
        print(f'Column: {ped_col}')
        print(f'Data type: {df[ped_col].dtype}')
        print(f'Shape: {len(df)} rows')
        print(f'Unique values: {df[ped_col].nunique()}')
        print(f'Min/Max: {df[ped_col].min()} / {df[ped_col].max()}')
        print(f'Mean: {df[ped_col].mean():.6f}')
        print(f'Std: {df[ped_col].std():.6f}')
        print(f'NaN count: {df[ped_col].isna().sum()}')
        print(f'\nValue counts (top 10):')
        print(df[ped_col].value_counts().head(10))
    else:
        print(f'ERROR: {ped_col} not found!')
        print(f'Available columns: {list(df.columns)}')
else:
    print(f'CSV not found at: {csv_path}')
