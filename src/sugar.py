import argparse

from src.interpreter import Interpreter
from src.parser import parse_to_ast


def main():
    arg_parser = argparse.ArgumentParser(description="Parse Sugar code.")
    arg_parser.add_argument("file", help="The Sugar file to parse.")
    args = arg_parser.parse_args()

    with open(args.file, "r") as f:
        code = f.read()

    try:
        ast = parse_to_ast(code)
        interpreter = Interpreter()
        interpreter.interpret(ast)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
