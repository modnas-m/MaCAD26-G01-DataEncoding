#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix mojibake encoding in notebooks"""

from pathlib import Path
import sys

# Working with the files directly
notebooks = [
    Path("notebooks/06_CityClassification.ipynb"),
    Path("notebooks/07_SHAP.ipynb")
]

# Replacement patterns - using byte sequences to avoid parsing issues
# Reading the notebooks directly in binary mode
import io

for nb in notebooks:
    if not nb.exists():
        print(f"Error: {nb} not found")
        continue
    
    # Read as binary to preserve exact encoding
    with open(nb, 'rb') as f:
        data = f.read()
    
    # Convert to string for processing
    content = data.decode('utf-8', errors='replace')
    fixed = content
    total = 0
    
    # Simple replacements that should work even with mojibake
    bad_strings = [
        'â"€',  # Horizontal lines
        'â€"',  # Em dash
        'âœ"',  # Checkmark
        'Â·',   # Middle dot
        'Ã—',   # Multiply
        'â†'',  # Arrow
        'âš ',   # Warning
    ]
    
    good_strings = [
        '—',  # EM DASH U+2014
        '—',  # EM DASH U+2014
        '✓',  # CHECK MARK U+2713
        '·',  # MIDDLE DOT U+00B7
        '×',  # MULTIPLICATION SIGN U+00D7
        '→',  # RIGHTWARDS ARROW U+2192
        '⚠',  # WARNING SIGN U+26A0
    ]
    
    for bad, good in zip(bad_strings, good_strings):
        n = fixed.count(bad)
        if n > 0:
            fixed = fixed.replace(bad, good)
            total += n
            print(f"  {nb.name}: found {n} instances")
    
    if total > 0:
        # Write back
        with open(nb, 'w', encoding='utf-8') as f:
            f.write(fixed)
        print(f"✓ {nb.name}: Fixed {total} encoding issues\n")
    else:
        print(f"  {nb.name}: No mojibake found\n")

print("Done!")
