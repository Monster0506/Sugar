#!/usr/bin/env python3
"""
Sugar Programming Language Parser
Uses Lark to parse Sugar code according to the grammar specification.
"""

import sys
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from lark import Lark, Transformer, v_args, Tree, Token
from lark.exceptions import LarkError

from utils import debug_class_wrapper

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s] %(message)s",
)

logger = logging.getLogger("SugarParser")


@debug_class_wrapper
class SugarASTTransformer(Transformer):
    """Transforms Lark parse tree into a clean, semantic AST (dicts/lists/primitives only)."""

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("SugarASTTransformer")
        self.logger.setLevel(logging.DEBUG)

    def _log_transform(self, method_name, items):
        """Log transformation details for debugging."""
        self.logger.debug(f"TRANSFORM {method_name}: {len(items)} items")
        for i, item in enumerate(items):
            if hasattr(item, "data"):
                self.logger.debug(
                    f"  {i}: Tree({item.data}) with {len(item.children)} children"
                )
            elif isinstance(item, Token):
                self.logger.debug(f"  {i}: Token({item.type}) = '{item.value}'")
            else:
                self.logger.debug(f"  {i}: {type(item)} = {item}")

    def program(self, items):
        return Tree("program", items)

    def variable_declaration(self, items):
        return Tree("variable_declaration", items)

    def variable_assignment(self, items):
        return Tree("variable_assignment", items)

    def this_assignment(self, items):
        return Tree("this_assignment", items)

    def function_declaration(self, items):
        return Tree("function_declaration", items)

    def function_declaration_qualified(self, items):
        return Tree("function_declaration_qualified", items)

    def parameter_list(self, items):
        return Tree("parameter_list", items)

    def parameter(self, items):
        return Tree("parameter", items)

    def function_body(self, items):
        return Tree("function_body", items)

    def type_declaration(self, items):
        return Tree("type_declaration", items)

    def type_body(self, items):
        return Tree("type_body", items)

    def type_field(self, items):
        return Tree("type_field", items)

    def class_declaration(self, items):
        return Tree("class_declaration", items)

    def class_body(self, items):
        return Tree("class_body", items)

    def class_member(self, items):
        print(f"DEBUG class_member items: {[repr(i) for i in items]}")

        # Handle access_modifier, STATIC, OVERRIDE
        is_static = False
        is_override = False
        access_modifier = None
        idx = 0
        # Check for access modifier

        if items and isinstance(items[0], Tree) and items[0].data == "access_modifier":

            access_modifier = str(items[0])
            print(f"===============Access modifier: {access_modifier}================")
            idx += 1

        # Check for static/override
        if items and isinstance(items[idx], Token):
            if str(items[idx]) == "STATIC":
                is_static = True
                idx += 1
            elif str(items[idx]) == "OVERRIDE":
                is_override = True
                idx += 1

        member = items[idx] if idx < len(items) else None
        t = Tree("class_member", [member])
        # Attach flags as meta attributes
        t.meta.is_static = is_static
        t.meta.is_override = is_override
        t.meta.access_modifier = access_modifier
        return t

    def access_modifier(self, items):
        return Tree("access_modifier", items)

    def property_declaration(self, items):
        return Tree("property_declaration", items)

    def method_declaration(self, items):
        return Tree("method_declaration", items)

    def constructor_declaration(self, items):
        return Tree("constructor_declaration", items)

    def interface_declaration(self, items):
        return Tree("interface_declaration", items)

    def interface_body(self, items):
        return Tree("interface_body", items)

    def interface_member(self, items):
        return Tree("interface_member", items)

    def if_statement(self, items):
        return Tree("if_statement", items)

    def elif_clause(self, items):
        return Tree("elif_clause", items)

    def else_clause(self, items):
        return Tree("else_clause", items)

    def for_statement(self, items):
        return Tree("for_statement", items)

    def while_statement(self, items):
        return Tree("while_statement", items)

    def try_statement(self, items):
        return Tree("try_statement", items)

    def catch_clause(self, items):
        return Tree("catch_clause", items)

    def finally_clause(self, items):
        return Tree("finally_clause", items)

    def match_statement(self, items):
        return Tree("match_statement", items)

    def case_clause(self, items):
        return Tree("case_clause", items)

    def default_clause(self, items):
        return Tree("default_clause", items)

    def pattern(self, items):
        return Tree("pattern", items)

    def guard(self, items):
        return Tree("guard", items)

    def pattern_list(self, items):
        return Tree("pattern_list", items)

    def dict_literal_pattern(self, items):
        return Tree("dict_literal_pattern", items)

    def pattern_dict(self, items):
        return Tree("pattern_dict", items)

    def return_statement(self, items):
        return Tree("return_statement", items)

    def throw_statement(self, items):
        return Tree("throw_statement", items)

    def expression_statement(self, items):
        return Tree("expression_statement", items)

    def spawn_statement(self, items):
        return Tree("spawn_statement", items)

    def pipeline_expression(self, items):
        return Tree("pipeline_expression", items)

    def or_expression(self, items):
        return Tree("or_expression", items)

    def and_expression(self, items):
        return Tree("and_expression", items)

    def equality_expression(self, items):
        return Tree("equality_expression", items)

    def equality_op(self, items):
        return Tree("equality_op", items)

    def relational_expression(self, items):
        return Tree("relational_expression", items)

    def relational_op(self, items):
        return Tree("relational_op", items)

    def additive_expression(self, items):
        return Tree("additive_expression", items)

    def multiplicative_expression(self, items):
        return Tree("multiplicative_expression", items)

    def unary_expression(self, items):
        return Tree("unary_expression", items)

    def postfix_expression(self, items):
        return Tree("postfix_expression", items)

    def method_call(self, items):
        return Tree("method_call", items)

    def method_name(self, items):
        # The items should contain the method name token
        if items:
            return Tree("method_name", items)
        return Tree("method_name", [])

    def property_access(self, items):
        return Tree("property_access", items)

    def array_access(self, items):
        return Tree("array_access", items)

    def primary_expression(self, items):
        return Tree("primary_expression", items)

    def literal(self, items):
        return Tree("literal", items)

    def array_literal(self, items):
        return Tree("array_literal", items)

    def dict_literal(self, items):
        return Tree("dict_literal", items)

    def dict_entries(self, items):
        return Tree("dict_entries", items)

    def dict_entry(self, items):
        return Tree("dict_entry", items)

    def tuple_literal(self, items):
        return Tree("tuple_literal", items)

    def lambda_expression(self, items):
        return Tree("lambda_expression", items)

    def argument_list(self, items):
        return Tree("argument_list", items)

    def type(self, items):
        return Tree("type", items)

    def primitive_type(self, items):
        return Tree("primitive_type", items)

    def array_type(self, items):
        return Tree("array_type", items)

    def map_type(self, items):
        return Tree("map_type", items)

    def tuple_type(self, items):
        return Tree("tuple_type", items)

    def custom_type(self, items):
        return Tree("custom_type", items)

    def IDENTIFIER(self, token):
        return token

    def INTEGER(self, token):
        return token

    def FLOAT(self, token):
        return token

    def STRING(self, token):
        return token

    def CHAR(self, token):
        return token

    def BOOLEAN(self, token):
        return token

    def TRUE(self, token):
        return token

    def FALSE(self, token):
        return token

    def INT_TYPE(self, token):
        return token

    def FLOAT_TYPE(self, token):
        return token

    def BOOL_TYPE(self, token):
        return token

    def CHAR_TYPE(self, token):
        return token

    def STR_TYPE(self, token):
        return token

    def VOID_TYPE(self, token):
        return token

    def ANY_TYPE(self, token):
        return token

    def GREATER_THAN(self, token):
        return token

    def LESS_THAN(self, token):
        return token

    def GREATER_THAN_OR_EQUAL_TO(self, token):
        return token

    def LESS_THAN_OR_EQUAL_TO(self, token):
        return token

    def EQUAL_TO(self, token):
        return token

    def NOT_EQUAL_TO(self, token):
        return token

    def PLUS(self, token):
        return token

    def MINUS(self, token):
        return token

    def TIMES(self, token):
        return token

    def DIVIDE(self, token):
        return token

    def MODULO(self, token):
        return token

    def NOT(self, token):
        return token

    def AND(self, token):
        return token

    def OR(self, token):
        return token

    def qualified_identifier(self, items):
        # Join identifiers with colons for qualified names
        name = ":".join(str(item) for item in items)
        return name

    def PUBLIC(self, token):
        return token

    def PRIVATE(self, token):
        return token

    def PROTECTED(self, token):
        return token

    def OVERRIDE(self, token):
        return token

    def STATIC(self, token):
        return token

    # Method name tokens
    def ADD(self, token):
        return token

    def REMOVE(self, token):
        return token

    def GET(self, token):
        return token

    def REVERSE(self, token):
        return token

    def LENGTH(self, token):
        return token

    def INSERT(self, token):
        return token

    def UPPER(self, token):
        return token

    def LOWER(self, token):
        return token

    def ALNUM(self, token):
        return token

    def SPLIT(self, token):
        return token

    def MAP(self, token):
        return token

    def FILTER(self, token):
        return token

    def REDUCE(self, token):
        return token

    def FIND(self, token):
        return token

    def ANY(self, token):
        return token

    def ALL(self, token):
        return token

    def JOIN(self, token):
        return token

    def __default__(self, data, children, meta):
        return Tree(data, children)


@debug_class_wrapper
class SugarParser:
    """Main parser for the Sugar programming language."""

    def __init__(self, grammar_file: Optional[str] = None):
        """Initialize the parser with the grammar file."""
        if grammar_file is None:
            grammar_file = str(Path(__file__).parent / "sugar_grammar.lark")
        with open(grammar_file, "r") as f:
            grammar = f.read()
        logger.info(f"Loaded grammar from {grammar_file}")
        self.parser = Lark(
            grammar,
            parser="lalr",
            transformer=SugarASTTransformer(),
            propagate_positions=True,
        )

    def parse(self, code: str) -> Any:
        """Parse Sugar code and return an AST."""
        logger.info("Starting parse of code...")
        try:
            tree = self.parser.parse(code)
            logger.info("Parse successful!")
            return tree
        except LarkError as e:
            logger.error(f"Parse error: {e}")
            raise SyntaxError(f"Parse error: {e}")

    def parse_file(self, file_path: str) -> Any:
        """Parse a Sugar file and return an AST."""
        logger.info(f"Parsing file: {file_path}")
        with open(file_path, "r") as f:
            code = f.read()
        return self.parse(code)


def main():
    """Main entry point for testing the parser."""
    if len(sys.argv) != 2:
        print("Usage: uv run sugar_parser.py <sugar_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    parser = SugarParser()

    try:
        ast = parser.parse_file(file_path)
        print("Parse successful!")
        print("AST:")
        print(f"DEBUG: type(ast) = {type(ast)}")
        # The transformer now produces clean dictionaries directly
        print(f"DEBUG: ast = {ast}")

        print(ast.pretty())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

