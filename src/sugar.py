import argparse
import logging
from pathlib import Path
from typing import NoReturn

from lark.exceptions import LarkError

from src.interpreter import Interpreter
from src.parser import parse_to_ast


def setup_logging(verbose: bool) -> None:
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def run_file(file_path: Path, interpreter: Interpreter) -> None:
    """Reads, parses, and interprets a single Sugar file."""
    logging.info(f"Executing file: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        ast = parse_to_ast(code)
        interpreter.interpret(ast)
    except FileNotFoundError:
        logging.error(f"Error: File not found at '{file_path}'")
        exit(1)
    except LarkError as e:
        logging.error(f"\nSyntax Error in '{file_path}':\n{e}")
        exit(1)
    except Exception as e:
        logging.error(f"\nRuntime Error in '{file_path}':\n{e}")
        # Optionally re-raise for debugging if verbose
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            raise e
        exit(1)


def main() -> NoReturn:
    """Main entry point for the Sugar interpreter."""
    arg_parser = argparse.ArgumentParser(description="The Sugar Programming Language.")
    arg_parser.add_argument("file", help="The Sugar file to execute.")
    arg_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose debug logging."
    )
    args = arg_parser.parse_args()

    setup_logging(args.verbose)

    file_path = Path(args.file)
    interpreter = Interpreter(file_path)

    run_file(file_path, interpreter)

    exit(0)


if __name__ == "__main__":
    main()