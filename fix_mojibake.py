import json
from pathlib import Path

# Notebook paths
nb06 = Path("notebooks/06_CityClassification.ipynb")
nb07 = Path("notebooks/07_SHAP.ipynb")

# Mojibake replacements mapping
replacements = {
    'â"€': '—',      # Horizontal line separator
    'â€"': '—',      # Em dash
    'âœ"': '✓',      # Checkmark  
    'Â·': '·',       # Middle dot
    'Ã—': '×',       # Multiplication sign
    'â†'': '→',      # Right arrow
    'âš ': '⚠',      # Warning sign
}

def fix_notebook(notebook_path):
    print(f"Processing: {notebook_path}")
    
    if not notebook_path.exists():
        print(f"  ERROR: File not found")
        return
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixed_content = content
    changes = []
    
    for mojibake, correct in replacements.items():
        count = fixed_content.count(mojibake)
        if count > 0:
            msg = f"  Found {count}x '{mojibake}' → replacing with '{correct}'"
            print(msg)
            changes.append(msg)
            fixed_content = fixed_content.replace(mojibake, correct)
    
    if fixed_content != content:
        with open(notebook_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"  ✓ Saved fixed version")
        return True
    else:
        print(f"  No changes needed")
        return False

# Fix both notebooks
results = []
results.append(fix_notebook(nb06))
results.append(fix_notebook(nb07))

if any(results):
    print("\n✓ All notebooks fixed!")
else:
    print("\nNo mojibake found")
