"""
More comprehensive mojibake fix using pattern analysis
"""
from pathlib import Path
import re

def fix_remaining_mojibake(file_path):
    """Fix all remaining mojibake encoding issues"""
    
    nb = Path(file_path)
    content = nb.read_text(encoding='utf-8', errors='replace')
    
    # Pattern-based replacements for common remaining mojibake
    replacements = [
        # Remove mixed em-dash euro patterns
        (r'—€+', '—'),              # —€€... -> —
        (r'â€"', '—'),              # Remaining â€" -> —
        (r'â"€', '—'),              # â"€ -> —
        (r'âœ"', '✓'),              # âœ" -> ✓
        
        # Clean up any remaining odd characters
        (r'[â€™""–—\u201d\u201c]+', '—'),  # Various quotes to em-dash for separators
    ]
    
    fixed = content
    total_changes = 0
    
    for pattern, replacement in replacements:
        matches = len(re.findall(pattern, fixed))
        if matches > 0:
            fixed = re.sub(pattern, replacement, fixed)
            total_changes += matches
    
    if fixed != content:
        nb.write_text(fixed, encoding='utf-8')
        return total_changes
    return 0

# Fix both notebooks
notebooks = [
    Path('notebooks/06_CityClassification.ipynb'),
    Path('notebooks/07_SHAP.ipynb')
]

print("Additional mojibake cleanup pass...\n")

for nb in notebooks:
    if nb.exists():
        count = fix_remaining_mojibake(nb)
        if count > 0:
            print(f"✓ {nb.name}: Fixed {count} remaining issues")
        else:
            print(f"  {nb.name}: No additional changes needed")
    else:
        print(f"ERROR: {nb} not found")

print("\nDone!")
