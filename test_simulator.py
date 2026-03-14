#!/usr/bin/env python3
"""Quick test to verify simulator file is syntactically correct"""

import sys
import ast

def test_syntax():
    """Test if the simulator file has valid Python syntax"""
    try:
        with open('robot_navigation_simulator.py', 'r') as f:
            code = f.read()
        
        # Try to parse the code
        ast.parse(code)
        print("✓ Syntax is valid!")
        print("✓ File structure is correct")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error found:")
        print(f"  Line {e.lineno}: {e.msg}")
        print(f"  {e.text}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_imports():
    """Test if core components can be imported"""
    print("\nTesting imports...")
    try:
        print("  Checking for PySide6...", end=" ")
        try:
            from PySide6.QtWidgets import QApplication
            print("✓")
        except ImportError:
            print("✗ (not installed)")
            return False
        
        print("  Checking for qt-material...", end=" ")
        try:
            import qt_material
            print("✓")
        except ImportError:
            print("⚠ (optional)")
        
        print("  Checking for pyqtgraph...", end=" ")
        try:
            import pyqtgraph
            print("✓")
        except ImportError:
            print("⚠ (optional)")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    print("Robot Navigation AI Simulator - File Verification\n")
    print("=" * 50)
    
    if test_syntax():
        print("\n✓ Code is syntactically valid!")
        print("\nTo run the simulator:")
        print("  1. Install dependencies: pip install pyside6 qt-material pyqtgraph")
        print("  2. Run: python robot_navigation_simulator.py")
        
        if test_imports():
            print("\n✓ All required dependencies appear to be installed!")
            print("✓ Ready to launch the simulator!")
    else:
        print("\n✗ Please fix the syntax errors above")
        sys.exit(1)
