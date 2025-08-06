from pathlib import Path

from pytest import raises

from src.parser import parse_to_ast
from src.static_analysis import (
    AlreadyDefinedSymbolError,
    StaticAnalyzer,
    UndefinedSymbolError,
)

example_path = Path("examples").resolve()
errors_path = (example_path / "errors").resolve()
static_errors_path = (errors_path / "static_errors").resolve()


def test_variable_declaration():
    with open(f"{static_errors_path}/01_variable_declaration.sugar", "r") as f:
        code = f.read()
    ast = parse_to_ast(code)
    analyzer = StaticAnalyzer()
    analyzer.analyze(ast)


def test_mismatch_type_variable_declaration():
    with open(f"{static_errors_path}/02_BAD_variable_declaration.sugar", "r") as f:
        code = f.read()
    ast = parse_to_ast(code)
    analyzer = StaticAnalyzer()
    with raises(TypeError):
        analyzer.analyze(ast)


def test_variable_assignment():
    with open(f"{static_errors_path}/03_variable_assignment.sugar", "r") as f:
        code = f.read()
    ast = parse_to_ast(code)
    analyzer = StaticAnalyzer()
    analyzer.analyze(ast)


def test_mismatch_type_variable_assignment():
    with open(f"{static_errors_path}/04_BAD_variable_assignment.sugar", "r") as f:
        code = f.read()
    ast = parse_to_ast(code)
    analyzer = StaticAnalyzer()
    with raises(TypeError):
        analyzer.analyze(ast)


def test_redeclare_existing_variable():
    with open(
        f"{static_errors_path}/05_BAD_redeclare_existing_variable.sugar", "r"
    ) as f:
        code = f.read()
    ast = parse_to_ast(code)
    analyzer = StaticAnalyzer()
    with raises(AlreadyDefinedSymbolError):
        analyzer.analyze(ast)


def test_assign_to_undefined_variable():
    with open(f"{static_errors_path}/06_BAD_assign_undefined_variable.sugar", "r") as f:
        code = f.read()
    ast = parse_to_ast(code)
    analyzer = StaticAnalyzer()
    with raises(UndefinedSymbolError):
        analyzer.analyze(ast)


def test_function_declaration():
    with open(f"{static_errors_path}/07_function_declaration.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        analyzer.analyze(ast)
