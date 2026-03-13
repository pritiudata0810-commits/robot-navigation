import ast
import sys

try:
    with open('D:\\robot-navigation\\navigator.py', 'r') as f:
        code = f.read()
    ast.parse(code)
    print("✓ Syntax is valid")
except SyntaxError as e:
    print(f"❌ Syntax error: {e}")
    sys.exit(1)
