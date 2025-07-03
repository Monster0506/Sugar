import sys
import logging
from sugar_parser import SugarParser
from sugar_symbol_table import SymbolTableGenerator
from sugar_interpreter import SugarInterpreter

def main():
    if len(sys.argv) != 2:
        print("Usage: main_interpreter.py <file.sugar>")
        sys.exit(1)
    sugar_file = sys.argv[1]
    logging.basicConfig(level=logging.INFO)
    try:
        # Parse
        parser = SugarParser()
        ast = parser.parse_file(sugar_file)
        print("[INFO] Parsing successful.")
        # Symbol Table
        generator = SymbolTableGenerator()
        symbol_table = generator.generate(ast)
        if symbol_table.has_errors():
            print("[ERROR] Symbol table errors:")
            for err in symbol_table.get_errors():
                print(f"  {err}")
            sys.exit(2)
        print("[INFO] Symbol table generated.")
        # Interpret
        interpreter = SugarInterpreter(ast, symbol_table)
        interpreter.run()
        print("[INFO] Interpretation complete.")
    except Exception as e:
        print(f"[FATAL] {e}")
        sys.exit(3)

if __name__ == "__main__":
    main() 