#!/usr/bin/env python3
import sys
try:
    import navigator
    print("✓ Module imported successfully")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
