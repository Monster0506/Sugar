#!/usr/bin/env python3

import sys
from pathlib import Path
from lark import Lark

def test_raw_parse():
    grammar_file = Path(__file__).parent / "sugar_grammar.lark"
    with open(grammar_file, "r") as f:
        grammar = f.read()
    
    # Create parser without transformer
    parser = Lark(grammar, parser="lalr", propagate_positions=True)
    
    # Test the NOT operator
    code = "DEF x #bool = !:T:"
    print(f"Testing: {code}")
    
    try:
        tree = parser.parse(code)
        print("Raw parse tree:")
        print(tree.pretty())
    except Exception as e:
        print(f"Parse error: {e}")

if __name__ == "__main__":
    test_raw_parse() 