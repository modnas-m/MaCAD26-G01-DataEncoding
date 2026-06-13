from pathlib import Path

# Comprehensive mojibake-to-correct character mappings
replacements = [
    # Em dash variants (most common)
    (b'\xc3\xa2\xe2\x80\x9d', b'\xe2\x80\x94'),  # â€" -> —
    (b'\xc3\xa2\xe2\x80\x9c', b'\xe2\x80\x94'),  # Another variant
    (b'\xc3\xa2\xc5\x93', b'\xe2\x80\x94'),      # Rare variant
    (b'\xc3\xa2\xe2\x82\xac', b'\xe2\x80\x94'),  # Currency mojibake
    
    # Checkmarks and symbols
    (b'\xc3\xa2\x9c\x93', b'\xe2\x9c\x93'),      # âœ" -> ✓
    
    # Dots and dividers
    (b'\xc3\x82\xc2\xb7', b'\xc2\xb7'),          # Â· -> ·
    (b'\xc3\x83\xc3\x97', b'\xc3\x97'),          # Ã— -> ×
    
    # Arrows
    (b'\xc3\xa2\x86\x92', b'\xe2\x86\x92'),      # â†' -> →
    
    # Warning signs
    (b'\xc3\xa2\x9a\xa0', b'\xe2\x9a\xa0'),      # âš  -> ⚠
]

print("Fixing mojibake encoding in notebooks...\n")

for nb_name in ['notebooks/07_SHAP.ipynb', 'notebooks/06_CityClassification.ipynb']:
    nb = Path(nb_name)
    if not nb.exists():
        print(f"NOT FOUND: {nb_name}")
        continue
    
    data = nb.read_bytes()
    fixed_data = data
    total_count = 0
    
    for mojibake_bytes, correct_bytes in replacements:
        count = fixed_data.count(mojibake_bytes)
        if count > 0:
            fixed_data = fixed_data.replace(mojibake_bytes, correct_bytes)
            total_count += count
    
    if total_count > 0:
        nb.write_bytes(fixed_data)
        print(f"✓ {nb_name}: Fixed {total_count} encoding issues")
    else:
        print(f"  {nb_name}: No changes needed")

print("\n✓ Done!")
