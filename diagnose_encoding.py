import pandas as pd
import os

# Find the classified CSV
output_dir = r'C:\Users\maria\Documents\GitHub\MaCAD26-G01-DataEncoding - Barcelona\MaCAD26-G01-DataEncoding-BarcelonaVersion\output\eixample_barcelona_spain'
csv_path = os.path.join(output_dir, 'eixample_barcelona_spain_classified.csv')

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    print('=== COLUMN NAMES ENCODING CHECK ===\n')
    print('All columns:')
    for i, col in enumerate(df.columns):
        # Show the column name and its raw bytes
        print(f'{i:2d}. {col!r}')
        # Check for mojibake patterns (UTF-8 decoded as Latin-1, etc.)
        if any(ord(c) > 127 for c in col):
            print(f'    ⚠️  Contains non-ASCII characters!')
    
    print('\n=== LOOKING FOR PEDESTRIAN PRIORITY ===')
    ped_related = [col for col in df.columns if 'pedestrian' in col.lower() or 'priority' in col.lower()]
    print(f'Found {len(ped_related)} columns:')
    for col in ped_related:
        print(f'  - {col!r}')
    
    print('\n=== SCALER INFO (if in separate file) ===')
    model_dir = r'C:\Users\maria\Documents\GitHub\MaCAD26-G01-DataEncoding - Barcelona\MaCAD26-G01-DataEncoding-BarcelonaVersion\models'
    scaler_path = os.path.join(model_dir, 'scaler.pkl')
    if os.path.exists(scaler_path):
        import joblib
        scaler = joblib.load(scaler_path)
        if hasattr(scaler, 'feature_names_in_'):
            print(f'Scaler feature names:')
            for i, name in enumerate(scaler.feature_names_in_):
                print(f'  {i}. {name!r}')
else:
    print(f'CSV not found at: {csv_path}')
