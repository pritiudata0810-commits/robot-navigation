#!/usr/bin/env python
"""Check dependencies and test imports."""

import sys
import importlib

print("=" * 60)
print("CHECKING PYTHON DEPENDENCIES")
print("=" * 60)

# List of packages to check
packages_to_check = [
    ('pyside6', 'PySide6'),
    ('qt_material', 'qt_material'),
    ('pyqtgraph', 'pyqtgraph'),
]

missing_packages = []

for import_name, display_name in packages_to_check:
    try:
        importlib.import_module(import_name)
        print(f"✓ {display_name} is installed")
    except ImportError as e:
        print(f"✗ {display_name} is NOT installed")
        print(f"  Error: {e}")
        missing_packages.append(display_name.lower() if display_name != 'qt_material' else 'qt-material')

print()
print("=" * 60)
print("TESTING robot_navigation_simulator IMPORT")
print("=" * 60)

try:
    import robot_navigation_simulator
    print("✓ robot_navigation_simulator imported successfully")
except ImportError as e:
    print(f"✗ robot_navigation_simulator import FAILED")
    print(f"  Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error during import")
    print(f"  Error: {type(e).__name__}: {e}")
    sys.exit(1)

print()
if missing_packages:
    print("=" * 60)
    print("MISSING PACKAGES - INSTALLATION COMMAND")
    print("=" * 60)
    print(f"pip install {' '.join(missing_packages)}")
else:
    print("=" * 60)
    print("All dependencies are installed!")
    print("=" * 60)
