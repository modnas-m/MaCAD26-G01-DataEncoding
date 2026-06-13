from pathlib import Path

# Read the file and look for exact mojibake byte sequences
nb = Path('notebooks/07_SHAP.ipynb')
data = nb.read_bytes()

# Find patterns to get their hex
idx = data.find(b'EDIT HERE')
if idx > 0:
    start = max(0, idx - 60)
    end = min(len(data), idx + 120)
    snippet = data[start:end]
    
    print("Context around 'EDIT HERE' (bytes):")
    print(snippet[:30])
    print("...")
    print(snippet[-30:])
    print()

# Find all \xc3\xa2 sequences and their continuations
print("Finding \\xc3\\xa2 mojibake patterns:")
idx = 0
sequences = {}
while idx < len(data):
    idx = data.find(b'\xc3\xa2', idx)
    if idx < 0:
        break
    
    # Get 4 bytes to see the pattern
    if idx + 3 < len(data):
        pattern = data[idx:idx+4]
        pattern_hex = pattern.hex()
        sequences[pattern_hex] = sequences.get(pattern_hex, 0) + 1
    idx += 1

print("Top mojibake sequences found:")
for seq_hex, count in sorted(sequences.items(), key=lambda x: -x[1])[:5]:
    try:
        as_bytes = bytes.fromhex(seq_hex)
        print(f"  {seq_hex}: {count}x (as string: {as_bytes})")
    except:
        print(f"  {seq_hex}: {count}x")
