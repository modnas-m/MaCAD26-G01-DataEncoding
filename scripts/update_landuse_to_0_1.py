#!/usr/bin/env python3
"""Update dominant_land_use_score in the augmented CSV from [-1, 1] -> [0, 1].

Creates a backup of the original file before overwriting.

Usage:
    python scripts/update_landuse_to_0_1.py
    python scripts/update_landuse_to_0_1.py --path csv/features_all_boroughs_with_location_id_augmented.csv
"""
from pathlib import Path
import shutil
import argparse
import pandas as pd


def convert(path: Path, make_backup: bool = True) -> int:
    if not path.exists():
        print(f'File not found: {path}')
        return 2

    df = pd.read_csv(path)
    col = 'dominant_land_use_score'
    if col not in df.columns:
        print(f'Column not found in CSV: {col}')
        return 3

    # Coerce to numeric, preserving NaNs
    df[col] = pd.to_numeric(df[col], errors='coerce')

    # Summary before
    before_nonnull = df[col].notna().sum()
    before_min = df[col].min()
    before_max = df[col].max()
    before_na = df[col].isna().sum()

    # Transform: new = (old + 1) / 2  (maps -1->0, 0->0.5, 1->1)
    df[col] = (df[col] + 1.0) / 2.0

    # Summary after
    after_min = df[col].min()
    after_max = df[col].max()

    if make_backup:
        backup = path.with_name(path.stem + '.bak.csv')
        shutil.copy2(path, backup)
        print(f'Backup created: {backup}')

    df.to_csv(path, index=False)

    print('Updated dominant_land_use_score:')
    print(f'  non-null before : {before_nonnull}')
    print(f'  NaNs preserved   : {before_na}')
    print(f'  original range   : {before_min} to {before_max}')
    print(f'  new range        : {after_min} to {after_max}')
    print(f'Wrote {path}')
    return 0


def main():
    p = argparse.ArgumentParser(description='Convert dominant_land_use_score to 0..1 in augmented CSV')
    p.add_argument('--path', '-p', default='csv/features_all_boroughs_with_location_id_augmented.csv')
    p.add_argument('--no-backup', dest='backup', action='store_false')
    args = p.parse_args()
    path = Path(args.path)
    return convert(path, make_backup=args.backup)


if __name__ == '__main__':
    raise SystemExit(main())
