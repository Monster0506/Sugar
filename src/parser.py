import os

from lark import Lark

from src.transformer import SugarTransformer

# Construct the absolute path to the grammar file
GRAMMAR_FILE = os.path.join(os.path.dirname(__file__), "sugar_grammar.lark")


class Parser:
    def __init__(self):
        with open(GRAMMAR_FILE, "r", encoding="utf-8") as f:
            grammar = f.read()
        self.lark_parser = Lark(
            grammar,
            start="program",
            parser="lalr",
            transformer=SugarTransformer(),
        )

    def parse(self, code: str):
        """Parses Sugar code and returns the AST."""
        try:
            self.lark_parser.lex(code)
        except Exception as e:
            raise RuntimeError(f"Error during lexing: {e}")
        return self.lark_parser.parse(code)


def parse_to_ast(code: str):
    """Helper function to parse code directly to AST for testing."""
    return Parser().parse(code)
