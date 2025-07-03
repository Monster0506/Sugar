import sys
import logging
from sugar_parser import SugarParser
from sugar_symbol_table import SymbolTableGenerator
from src.interpreter import SugarInterpreter

def main():
    if len(sys.argv) < 2:
        print("Usage: uv run main_interpreter.py <file.sugar>")
        sys.exit(1)
    filename = sys.argv[1]
    logging.basicConfig(level=logging.INFO)
    try:
        parser = SugarParser()
        ast = parser.parse_file(filename)
        print("[INFO] Parsing successful.")
        generator = SymbolTableGenerator()
        symbol_table = generator.generate(ast)
        interpreter = SugarInterpreter(ast, symbol_table)
        interpreter.run()
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 