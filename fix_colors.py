#!/usr/bin/env python3
import re

# Read the file
with open('navigator.py', 'r') as f:
    content = f.read()

# Replace all instances of color(#HEXCODE) with just #HEXCODE
updated = re.sub(r'color\(#([0-9a-fA-F]+)\)', r'#\1', content)

# Write back
with open('navigator.py', 'w') as f:
    f.write(updated)

print("✓ Fixed all color syntax errors")
print("  Changed: color(#HEXCODE) → #HEXCODE")
