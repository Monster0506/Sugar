from pathlib import Path

from pytest import raises

from src.parser import parse_to_ast
from src.static_analysis import (
    AlreadyDefinedSymbolError,
    DuplicateFunctionOverloadError,
    StaticAnalyzer,
    TypeCheckingError,
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
    with raises(TypeCheckingError):
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
    with raises(TypeCheckingError):
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


def test_function_overload_declaration():
    with open(f"{static_errors_path}/08_function_overload.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        analyzer.analyze(ast)


def test_function_return_type_mismatch():
    with open(f"{static_errors_path}/09_BAD_function_return.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        with raises(TypeCheckingError):
            analyzer.analyze(ast)


def test_duplicate_function_signatures():
    with open(f"{static_errors_path}/10_BAD_function_overload.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        with raises(DuplicateFunctionOverloadError):
            analyzer.analyze(ast)


def test_function_and_variable_with_same_name():
    with open(
        f"{static_errors_path}/11_BAD_function_and_variable_same_name.sugar", "r"
    ) as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        with raises(AlreadyDefinedSymbolError):
            analyzer.analyze(ast)


def test_function_call():

    with open(f"{static_errors_path}/12_function_call.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        analyzer.analyze(ast)


def test_assignment_from_function_call():

    with open(f"{static_errors_path}/13_assignment_from_function_call.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        analyzer.analyze(ast)


def test_assigning_all_variable_types():

    with open(f"{static_errors_path}/20_all_variable_types.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        analyzer.analyze(ast)


def test_null_type_declaration():
    with open(f"{static_errors_path}/21_null_type_declaration.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        analyzer.analyze(ast)


def test_null_type_assignment():
    with open(f"{static_errors_path}/22_null_type_assignment.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        analyzer.analyze(ast)


def test_null_in_collections():
    with open(f"{static_errors_path}/23_null_in_collections.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        analyzer.analyze(ast)


def test_null_collection_assignment():
    with open(f"{static_errors_path}/24_null_collection_assignment.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        analyzer.analyze(ast)


def test_null_function_parameters():
    with open(f"{static_errors_path}/25_null_function_parameters.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        analyzer.analyze(ast)


def test_null_function_usage():
    with open(f"{static_errors_path}/26_null_function_usage.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        analyzer.analyze(ast)


def test_bad_null_type_invalid_assignment():
    with open(f"{static_errors_path}/27_BAD_null_type_invalid_assignment.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        with raises(TypeCheckingError):
            analyzer.analyze(ast)


def test_array_type_declaration():
    with open(f"{static_errors_path}/28_array_type_declaration.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        analyzer.analyze(ast)


def test_bad_array_type_mismatch():
    with open(f"{static_errors_path}/29_BAD_array_type_mismatch.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        with raises(TypeCheckingError):
            analyzer.analyze(ast)


def test_map_type_declaration():
    with open(f"{static_errors_path}/30_map_type_declaration.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        analyzer.analyze(ast)


def test_bad_map_type_mismatch():
    with open(f"{static_errors_path}/31_BAD_map_type_mismatch.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        with raises(TypeCheckingError):
            analyzer.analyze(ast)


def test_tuple_type_declaration():
    with open(f"{static_errors_path}/32_tuple_type_declaration.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        analyzer.analyze(ast)


def test_bad_tuple_type_mismatch():
    with open(f"{static_errors_path}/33_BAD_tuple_type_mismatch.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        with raises(TypeCheckingError):
            analyzer.analyze(ast)


def test_function_parameter_types():
    with open(f"{static_errors_path}/34_function_parameter_types.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        analyzer.analyze(ast)


def test_bad_function_parameter_mismatch():
    with open(f"{static_errors_path}/35_BAD_function_parameter_mismatch.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        with raises(TypeCheckingError):
            analyzer.analyze(ast)


def test_control_flow_types():
    with open(f"{static_errors_path}/36_control_flow_types.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        analyzer.analyze(ast)


def test_bad_control_flow_type_mismatch():
    with open(f"{static_errors_path}/37_BAD_control_flow_type_mismatch.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        with raises(TypeCheckingError):
            analyzer.analyze(ast)


def test_expression_types():
    with open(f"{static_errors_path}/38_expression_types.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        analyzer.analyze(ast)


def test_bad_expression_type_mismatch():
    with open(f"{static_errors_path}/39_BAD_expression_type_mismatch.sugar", "r") as f:
        code = f.read()
        ast = parse_to_ast(code)
        analyzer = StaticAnalyzer()
        with raises(TypeCheckingError):
            analyzer.analyze(ast)
