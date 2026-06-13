#!/usr/bin/env python3
"""Binary-level mojibake fixes"""

from pathlib import Path

def fix_binary(path):
    """Read file as binary, replace byte patterns, write back"""
    with open(path, 'rb') as f:
        data = f.read()
    
    original_len = len(data)
    
    # Binary replacement patterns (UTF-8 encoded mojibake -> UTF-8 correct)
    replacements = [
        (b'\xc3\xa2\x22\x80', b'\xe2\x80\x94'),  # Mojibake line -> em-dash
        (b'\xc3\xa2\x80\x9c', b'\xe2\x80\x94'),  # Mojibake dash -> em-dash  
        (b'\xc3\xa2\x9c\x93', b'\xe2\x9c\x93'),  # Mojibake check -> checkmark
        (b'\xc3\x82\xc2\xb7', b'\xc2\xb7'),      # Mojibake dot -> middle dot
        (b'\xc3\x83\xc3\x97', b'\xc3\x97'),      # Mojibake mult -> multiply
        (b'\xc3\xa2\x86\x92', b'\xe2\x86\x92'),  # Mojibake arrow -> arrow
        (b'\xc3\xa2\x9a\xa0', b'\xe2\x9a\xa0'),  # Mojibake warn -> warning
    ]
    
    fixed_data = data
    total_replacements = 0
    
    for mojibake_bytes, correct_bytes in replacements:
        count = fixed_data.count(mojibake_bytes)
        if count > 0:
            fixed_data = fixed_data.replace(mojibake_bytes, correct_bytes)
            total_replacements += count
            print(f"  Replaced {count} instances")
    
    if total_replacements > 0:
        with open(path, 'wb') as f:
            f.write(fixed_data)
        return total_replacements
    return 0

# Fix notebooks
notebooks = [
    Path("notebooks/06_CityClassification.ipynb"),
    Path("notebooks/07_SHAP.ipynb")
]

print("Fixing mojibake encoding...\n")
for nb in notebooks:
    if nb.exists():
        count = fix_binary(nb)
        if count > 0:
            print(f"✓ {nb.name}: Fixed {count} encoding issues\n")
        else:
            print(f"  {nb.name}: No changes needed\n")
    else:
        print(f"ERROR: {nb} not found\n")

print("Done!")
