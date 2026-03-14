import py_compile
import sys

try:
    py_compile.compile('D:\\robot-navigation\\navigator_professional.py', doraise=True)
    print("✓ Syntax check passed!")
    sys.exit(0)
except py_compile.PyCompileError as e:
    print(f"✗ Syntax error: {e}")
    sys.exit(1)
