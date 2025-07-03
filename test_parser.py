#!/usr/bin/env python3
"""
Test script to run the Sugar parser against all example files.
"""

import os
import sys
from pathlib import Path
from sugar_parser import SugarParser

def test_parser():
    """Test the parser against all example files."""
    parser = SugarParser()
    examples_dir = Path("examples")
    
    if not examples_dir.exists():
        print("Examples directory not found!")
        return
    
    example_files = list(examples_dir.glob("*.sugar"))
    
    if not example_files:
        print("No .sugar files found in examples directory!")
        return
    
    print(f"Found {len(example_files)} example files to test:")
    print("-" * 50)
    
    success_count = 0
    total_count = len(example_files)
    
    for example_file in sorted(example_files):
        print(f"\nTesting: {example_file.name}")
        print("=" * 40)
        
        try:
            ast = parser.parse_file(str(example_file))
            print(f" SUCCESS: {example_file.name}")
            print(f"   AST type: {type(ast)}")
            
            # Show a brief summary of the AST structure
            if hasattr(ast, 'data'):
                print(f"   Root node: {ast.data}")
                if hasattr(ast, 'children') and ast.children:
                    print(f"   Children count: {len(ast.children)}")
            
            success_count += 1
            
        except Exception as e:
            print(f"FAILED: {example_file.name}")
            print(f"   Error: {e}")
            print(f"   Type: {type(e).__name__}")
    
    print("\n" + "=" * 50)
    print(f"SUMMARY: {success_count}/{total_count} files parsed successfully")
    
    if success_count == total_count:
        print(" All examples parsed successfully!")
        return True
    else:
        print("Some examples failed to parse")
        return False

def test_specific_file(filename):
    """Test the parser against a specific file."""
    parser = SugarParser()
    
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return False
    
    try:
        print(f"Testing: {filename}")
        print("=" * 40)
        
        ast = parser.parse_file(filename)
        print(f" SUCCESS: {filename}")
        print(f"   AST type: {type(ast)}")
        
        # The transformer now produces clean dictionaries directly
        # Show a brief summary
        if isinstance(ast, dict) and 'type' in ast and ast['type'] == 'program':
            statements = ast.get('statements', [])
            print(f"   Statements count: {len(statements)}")
        
        return True
        
    except Exception as e:
        print(f" FAILED: {filename}")
        print(f"   Error: {e}")
        print(f"   Type: {type(e).__name__}")
        return False

def debug_file(filename, show_tokens=True, show_parsing=True):
    """Debug a specific file with detailed tokenization and parsing information."""
    parser = SugarParser()
    
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return False
    
    print(f"DEBUGGING: {filename}")
    print("=" * 60)
    
    # Read the file content
    with open(filename, 'r') as f:
        code = f.read()
    
    print(f"Code:\n{code}")
    
    # Step 1: Tokenization
    if show_tokens:
        print(f"\n--- TOKENIZATION ---")
        try:
            lexer = parser.parser.lex(code)
            tokens = list(lexer)
            
            print("Tokens:")
            for i, token in enumerate(tokens):
                print(f"  {i:2d}: {token.type:15s} = '{token.value}' (line {token.line}, col {token.column})")
                
        except Exception as e:
            print(f"Tokenization failed: {e}")
            return False
    
    # Step 2: Parsing
    if show_parsing:
        print(f"\n--- PARSING ---")
        try:
            tree = parser.parser.parse(code)
            print(" Parse successful!")
            print(f"Root node: {tree.data}")
            print(f"Children count: {len(tree.children)}")
            
            # Show tree structure
            def print_tree(node, indent=0):
                print("  " * indent + f"{node.data}: {len(node.children)} children")
                for child in node.children:
                    if hasattr(child, 'data'):
                        print_tree(child, indent + 1)
                    else:
                        print("  " * (indent + 1) + f"Token: {child}")
            
            print("\nTree structure:")
            print_tree(tree)
            
        except Exception as e:
            print(f" Parse failed: {e}")
            print(f"Error type: {type(e).__name__}")
            
            # Try to get more details about the error (Lark exceptions have line/column)
            from lark.exceptions import LarkError
            if isinstance(e, LarkError) and hasattr(e, 'line') and hasattr(e, 'column'):
                print(f"Error location: line {e.line}, column {e.column}")
                
                # Show context around the error
                lines = code.split('\n')
                if e.line <= len(lines):
                    print(f"Context:")
                    start = max(0, e.line - 2)
                    end = min(len(lines), e.line + 1)
                    for i in range(start, end):
                        marker = ">>> " if i == e.line - 1 else "    "
                        print(f"{marker}{i+1:2d}: {lines[i]}")
            
            return False
    
    return True

def debug_code(code, show_tokens=True, show_parsing=True):
    """Debug a specific code snippet with detailed tokenization and parsing information."""
    parser = SugarParser()
    
    print(f"DEBUGGING CODE SNIPPET")
    print("=" * 60)
    print(f"Code:\n{code}")
    
    # Step 1: Tokenization
    if show_tokens:
        print(f"\n--- TOKENIZATION ---")
        try:
            lexer = parser.parser.lex(code)
            tokens = list(lexer)
            
            print("Tokens:")
            for i, token in enumerate(tokens):
                print(f"  {i:2d}: {token.type:15s} = '{token.value}' (line {token.line}, col {token.column})")
                
        except Exception as e:
            print(f"Tokenization failed: {e}")
            return False
    
    # Step 2: Parsing
    if show_parsing:
        print(f"\n--- PARSING ---")
        try:
            tree = parser.parser.parse(code)
            print(" Parse successful!")
            print(f"Root node: {tree.data}")
            
        except Exception as e:
            print(f" Parse failed: {e}")
            print(f"Error type: {type(e).__name__}")
            
            # Try to get more details about the error
            if hasattr(e, 'line') and hasattr(e, 'column'):
                print(f"Error location: line {e.line}, column {e.column}")
            
            return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--debug" and len(sys.argv) > 2:
            # Debug mode: python test_parser.py --debug filename
            debug_file(sys.argv[2])
        elif sys.argv[1] == "--debug-code" and len(sys.argv) > 2:
            # Debug code snippet: python test_parser.py --debug-code "code here"
            debug_code(sys.argv[2])
        else:
            # Test specific file
            filename = sys.argv[1]
            test_specific_file(filename)
    else:
        # Test all examples
        test_parser() 