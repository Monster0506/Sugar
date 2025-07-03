#!/usr/bin/env python3
"""
Debug script to understand AST structure
"""

import sys
from sugar_parser import SugarParser

def print_ast(node, indent=0):
    prefix = '  ' * indent
    if hasattr(node, 'data'):
        print(f"{prefix}{node.data}")
        for child in getattr(node, 'children', []):
            print_ast(child, indent + 1)
    else:
        # Token or leaf
        print(f"{prefix}{repr(node)}")


def debug_ast(file_path):
    parser = SugarParser()
    ast = parser.parse_file(file_path)
    print("=== AST Structure ===")
    print_ast(ast)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_ast.py <file>")
        sys.exit(1)
    debug_ast(sys.argv[1]) 