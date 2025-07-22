from pathlib import Path
from typing import Any

import pytest

from src.interpreter import Interpreter, Variable
from src.parser import Parser

example_path = Path("examples").resolve()
interpreting_tests_path = (example_path / "interpreting_tests").resolve()


def test_variable_declaration():
    with open(f"{interpreting_tests_path}/01_var_decl.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    assert isinstance(interpreter.environment.get("x"), Variable)
    assert (interpreter.environment.get("x")).value == 4


def test_variable_assignment():
    with open(f"{interpreting_tests_path}/02_var_assign.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    assert isinstance(interpreter.environment.get("x"), Variable)
    assert (interpreter.environment.get("x")).value == 7


def test_variable_types():
    with open(f"{interpreting_tests_path}/03_var_types.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"a": 2, "b": 3.5, "c": False, "d": "B", "e": "world"}
    assert check_variable_helper(interpreter, expected)


def test_array_declaration():
    with open(f"{interpreting_tests_path}/04_array_decl.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"arr": [4, 5, 6]}
    assert check_variable_helper(interpreter, expected)


def test_type_mismatch():
    with open("examples\\type_errors\\01_type_mismatch.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    interpreter = Interpreter()
    with pytest.raises(TypeError):
        interpreter.interpret(ast)


def test_array_type_mismatch():
    with open("examples\\type_errors\\02_array_type_mismatch.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    interpreter = Interpreter()
    with pytest.raises(TypeError):
        interpreter.interpret(ast)


def test_map_type_mismatch():
    with open("examples\\type_errors\\03_map_type_mismatch.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    interpreter = Interpreter()
    with pytest.raises(TypeError):
        interpreter.interpret(ast)


def test_tuple_type_mismatch():
    with open("examples\\type_errors\\04_tuple_type_mismatch.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    interpreter = Interpreter()
    with pytest.raises(TypeError):
        interpreter.interpret(ast)


def test_map_declaration():
    with open(f"{interpreting_tests_path}/05_map_decl.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"m": {"c": 3, "d": 4}}
    assert check_variable_helper(interpreter, expected)


def test_if_statement():
    with open(f"{interpreting_tests_path}/06_if_basic.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"y": 1}
    assert check_variable_helper(interpreter, expected)


def test_if_else_statement():
    with open(f"{interpreting_tests_path}/07_if_else.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"y": 0}
    assert check_variable_helper(interpreter, expected)


def test_for_loop():
    with open(f"{interpreting_tests_path}/08_for_loop.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"sum": 12}  # (1*2) + (2*2) + (3*2) = 2 + 4 + 6 = 12
    assert check_variable_helper(interpreter, expected)


def test_function_declaration_and_call():
    with open(f"{interpreting_tests_path}/09_func_decl_call.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"result": 11, "fibr": 5}
    print(interpreter.environment)
    assert check_variable_helper(interpreter, expected)


def test_function_overload():
    with open(f"{interpreting_tests_path}/10_func_overload.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"x": 5, "y": 4, "z": 5}
    assert check_variable_helper(interpreter, expected)


def check_variable_helper(interpreter: Interpreter, expected: dict[str, Any]) -> bool:
    results = []
    for k, v in expected.items():
        item = interpreter.environment.get(k)
        isvar = isinstance(item, Variable)
        correct_value = item.value == v
        results.append(isvar and correct_value)
    return all(results)

