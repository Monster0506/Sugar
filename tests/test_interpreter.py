from pathlib import Path
from typing import Any

import pytest

from src.ast_nodes import Program
from src.interpreter import Interpreter, Variable
from src.parser import Parser


example_path = Path("examples").resolve()
interpreting_tests_path = (example_path / "interpreting_tests").resolve()


def test_variable_declaration():
    with open(f"{interpreting_tests_path}/01_var_decl.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    assert isinstance(interpreter.environment.get("x"), Variable)
    assert (interpreter.environment.get("x")).value == 4


def test_variable_assignment():
    with open(f"{interpreting_tests_path}/02_var_assign.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    assert isinstance(interpreter.environment.get("x"), Variable)
    assert (interpreter.environment.get("x")).value == 7


def test_variable_types():
    with open(f"{interpreting_tests_path}/03_var_types.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"a": 2, "b": 3.5, "c": False, "d": "B", "e": "world"}
    assert check_variable_helper(interpreter, expected)


def test_array_declaration():
    with open(f"{interpreting_tests_path}/04_array_decl.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"arr": [4, 5, 6]}
    assert check_variable_helper(interpreter, expected)


def test_type_mismatch():
    with open("examples\\type_errors\\01_type_mismatch.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    with pytest.raises(TypeError):
        interpreter.interpret(ast)


def test_array_type_mismatch():
    with open("examples\\type_errors\\02_array_type_mismatch.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    with pytest.raises(TypeError):
        interpreter.interpret(ast)


def test_map_type_mismatch():
    with open("examples\\type_errors\\03_map_type_mismatch.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    with pytest.raises(TypeError):
        interpreter.interpret(ast)


def test_tuple_type_mismatch():
    with open("examples\\type_errors\\04_tuple_type_mismatch.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    with pytest.raises(TypeError):
        interpreter.interpret(ast)


def test_map_declaration():
    with open(f"{interpreting_tests_path}/05_map_decl.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"m": {"c": 3, "d": 4}}
    assert check_variable_helper(interpreter, expected)


def test_if_statement():
    with open(f"{interpreting_tests_path}/06_if_basic.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"y": 1}
    assert check_variable_helper(interpreter, expected)


def test_if_else_statement():
    with open(f"{interpreting_tests_path}/07_if_else.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"y": 0}
    assert check_variable_helper(interpreter, expected)


def test_for_loop():
    with open(f"{interpreting_tests_path}/08_for_loop.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"sum": 12}  # (1*2) + (2*2) + (3*2) = 2 + 4 + 6 = 12
    assert check_variable_helper(interpreter, expected)


def test_function_declaration_and_call():
    with open(f"{interpreting_tests_path}/09_func_decl_call.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"result": 11, "fibr": 5}
    assert check_variable_helper(interpreter, expected)


def test_function_overload():
    with open(f"{interpreting_tests_path}/10_func_overload.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)

    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"x": 5, "y": 4, "z": 5}
    assert check_variable_helper(interpreter, expected)


def test_array_operations():
    with open(f"{interpreting_tests_path}/11_array_ops.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {
        "len": 2,
        "val": 2,
        "first": 3,
        "last": 2,
        "filtered": [2],
        "mapped": [4, 6, 10, 14],
        "found": False,
        "has_five": True,
        "arr": [2, 3, 5, 7],
        "all_positive": True,
    }
    assert check_variable_helper(interpreter, expected)


def test_advanced_array_operations():
    with open(f"{interpreting_tests_path}/60_new_array_ops.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {
        "arr": [10, 2, 3, 4, 5],
        "first": 10,
        "has_three": True,
        "has_nine": False,
        "index_of_three": 2,
        "index_of_nine": -1,
        "slice_result": [2, 3, 4],
        "total": 24,
        "unsorted": [1, 2, 5, 8, 9],
        "sorted_first": 1,
    }
    assert check_variable_helper(interpreter, expected)


def test_string_operations():
    with open(f"{interpreting_tests_path}/12_string_ops.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"l": 5, "up": "HELLO", "lo": "hello", "s": "HAello"}
    assert check_variable_helper(interpreter, expected)


def test_advanced_string_operations():
    with open(f"{interpreting_tests_path}/61_string_array_operations.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {
        "after_remove_first": "e",
        "copy": "cba",
        "final_length": 7,
        "final_string": "Heorld!",
        "first_after_insert": "X",
        "first_char": "H",
        "h_index": -1,
        "has_h": False,
        "has_z": False,
        "last_char": "o",
        "len": 5,
        "len_after_add": 6,
        "lower_s": "hello",
        "multi": "Heorld!",
        "reversed_first": "c",
        "s": "XYello!",
        "second_char": "Y",
        "test_remove": "est",
        "upper_s": "HELLO",
        "z_index": -1,
    }
    assert check_variable_helper(interpreter, expected)


def test_while_loop():
    with open(f"{interpreting_tests_path}/13_while_loop.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"x": 0}
    assert check_variable_helper(interpreter, expected)


def test_func_return():
    with open(f"{interpreting_tests_path}/14_func_return.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"b": 11}
    assert check_variable_helper(interpreter, expected)


def check_variable_helper(interpreter: Interpreter, expected: dict[str, Any]) -> bool:
    results = []
    for k, v in expected.items():
        item = interpreter.environment.get(k)
        isvar = isinstance(item, Variable)
        correct_value = item.value == v
        results.append(isvar and correct_value)
    return all(results)
