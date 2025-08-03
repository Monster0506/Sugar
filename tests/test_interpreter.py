from pathlib import Path
from typing import Any

import pytest

from src.ast_nodes import Program, PropertyDeclaration, SugarClass, SugarInstance
from src.interpreter import Function, Interpreter, Variable
from src.parser import Parser


example_path = Path("examples").resolve()
interpreting_tests_path = (example_path / "interpreting_tests").resolve()
type_errors_path = (example_path / "type_errors").resolve()


def check_variable_helper(interpreter: Interpreter, expected: dict[str, Any]) -> bool:
    for k, v in expected.items():
        item = interpreter.environment.get(k)
        if not isinstance(item, Variable):
            print(f"Error: Variable '{k}' not found or not a Variable object.")
            return False

        if isinstance(item.value, SugarInstance):
            if not isinstance(v, dict):
                print(
                    f"Error: Expected dictionary for SugarInstance '{k}', got {type(v).__name__}."
                )
                return False

            instance_env = item.value.environment
            for prop_k, prop_v in v.items():
                try:
                    instance_prop_wrapper = instance_env.get(prop_k)
                    if not isinstance(instance_prop_wrapper, Variable):
                        print(
                            f"Error: Property '{prop_k}' of instance '{k}' is not a Variable object."
                        )
                        return False

                    if instance_prop_wrapper.value != prop_v:
                        print(
                            f"Error: Property '{prop_k}' of instance '{k}' expected {prop_v}, got {instance_prop_wrapper.value}."
                        )
                        return False
                except NameError:
                    print(f"Error: Property '{prop_k}' not found in instance '{k}'.")
                    return False
        else:
            if item.value != v:
                print(f"Error: Variable '{k}' expected {v}, got {item.value}.")
                return False
    return True


def test_variable_declaration():
    with open(f"{interpreting_tests_path}/01_var_decl.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"x": 4}
    assert check_variable_helper(interpreter, expected)


def test_variable_assignment():
    with open(f"{interpreting_tests_path}/02_var_assign.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"x": 7}
    assert check_variable_helper(interpreter, expected)


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
    with open(f"{type_errors_path}/01_type_mismatch.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    with pytest.raises(TypeError):
        interpreter.interpret(ast)


def test_array_type_mismatch():
    with open(f"{type_errors_path}/02_array_type_mismatch.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    with pytest.raises(TypeError):
        interpreter.interpret(ast)


def test_map_type_mismatch():
    with open(f"{type_errors_path}/03_map_type_mismatch.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    with pytest.raises(TypeError):
        interpreter.interpret(ast)


def test_tuple_type_mismatch():
    with open(f"{type_errors_path}/04_tuple_type_mismatch.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    with pytest.raises(TypeError):
        interpreter.interpret(ast)


def test_interface_class_mismatch():
    with open(f"{type_errors_path}/05_no_interface_match.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    with pytest.raises(TypeError):
        interpreter.interpret(ast)


def test_function_overloading_duplicate_parameters():
    with open(f"{type_errors_path}/06_overloading.sugar", "r") as f:
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
    expected = {"m": {"c": 6, "d": 4, "a": 5}, "v": 6}
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


def test_function_return():
    with open(f"{interpreting_tests_path}/14_func_return.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"b": 11}
    assert check_variable_helper(interpreter, expected)


def test_boolean_logic_and_operators():
    with open(f"{interpreting_tests_path}/15_bool_logic.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {
        "t": True,
        "b": True,
        "c": True,
        "f": False,
        "d": True,
        "e": True,
        "r": False,
        "g": False,
        "h": True,
        "i": True,
        "j": True,
        "k": True,
        "l": True,
        "m": False,
        "n": True,
        "o": True,
    }

    assert check_variable_helper(interpreter, expected)


def test_tuple_declaration():
    with open(f"{interpreting_tests_path}/16_tuple_decl.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {
        "t": (1, "hi"),
    }

    assert check_variable_helper(interpreter, expected)


def test_nested_if_statements():
    with open(f"{interpreting_tests_path}/17_nested_if.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"y": 1}
    assert check_variable_helper(interpreter, expected)


def test_function_with_no_parameters():
    with open(f"{interpreting_tests_path}/18_func_no_params.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"x": 5}
    assert check_variable_helper(interpreter, expected)


def test_default_function():
    with open(f"{interpreting_tests_path}/19_func_default.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    assert isinstance(interpreter.environment.get("foo"), list)
    assert isinstance(interpreter.environment.get("foo")[0], Function)
    assert len(interpreter.environment.get("foo")[0].params) == 0


def test_array_map_method():
    with open(f"{interpreting_tests_path}/20_array_map.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"doubled": [2, 4, 6], "arr": [1, 2, 3]}
    assert check_variable_helper(interpreter, expected)


def test_method_call_pipeline():
    with open(f"{interpreting_tests_path}/21_pipeline.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"result": 24, "arr": [1, 2, 3, 4, 5]}
    assert check_variable_helper(interpreter, expected)


def test_basic_match_statements():
    with open(f"{interpreting_tests_path}/22_match_basic.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {
        "y": 1,
    }
    assert check_variable_helper(interpreter, expected)


def test_boolean_function():
    with open(f"{interpreting_tests_path}/23_func_bool_return.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {
        "b": True,
    }
    assert check_variable_helper(interpreter, expected)


def test_nested_function_calls():
    with open(f"{interpreting_tests_path}/24_nested_func_call.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {
        "y": 6,
    }
    assert check_variable_helper(interpreter, expected)


def test_array_filter_method():
    with open(f"{interpreting_tests_path}/25_array_filter.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {
        "evens": [2, 4],
    }
    assert check_variable_helper(interpreter, expected)


def test_void_function():
    with open(f"{interpreting_tests_path}/26_func_void.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    assert isinstance(interpreter.environment.get("print_hello"), list)
    assert isinstance(interpreter.environment.get("print_hello")[0], Function)
    assert len(interpreter.environment.get("print_hello")[0].params) == 0


def test_character_function():
    with open(f"{interpreting_tests_path}/27_func_char.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {
        "c": "A",
    }
    assert check_variable_helper(interpreter, expected)


def test_map_setting():
    with open(f"{interpreting_tests_path}/28_map_set.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"m": {"a": 1, "b": 2}}
    assert check_variable_helper(interpreter, expected)


def test_any_and_all_for_arrays():
    with open(f"{interpreting_tests_path}/29_array_any_all.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"has_two": True, "all_pos": True}
    assert check_variable_helper(interpreter, expected)


def test_nested_scopes_for_functions():
    with open(f"{interpreting_tests_path}/30_func_nested_scope.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"r": 4}
    assert check_variable_helper(interpreter, expected)


def test_function_parameter_shadowing():
    with open(f"{interpreting_tests_path}/31_func_param_shadow.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"r": 5}
    assert check_variable_helper(interpreter, expected)


def test_array_insert_operation():
    with open(f"{interpreting_tests_path}/32_array_insert.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"arr": [1, 99, 2, 3]}
    assert check_variable_helper(interpreter, expected)


def test_missing_value_in_map_get_operation():
    with open(f"{interpreting_tests_path}/33_map_get_missing.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    with pytest.raises(KeyError):
        interpreter.interpret(ast)


def test_string_concatenation():
    with open(f"{interpreting_tests_path}/34_func_str_concat.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"msg": "Hello, World"}
    assert check_variable_helper(interpreter, expected)


def test_array_function():
    with open(f"{interpreting_tests_path}/35_func_array_return.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"arr": [1, 2, 3]}
    assert check_variable_helper(interpreter, expected)


def test_map_function():
    with open(f"{interpreting_tests_path}/36_func_map_return.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"m": {"a": 1, "b": 2}}
    assert check_variable_helper(interpreter, expected)


def test_tuple_function():
    with open(f"{interpreting_tests_path}/37_func_tuple_return.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"t": (1, "a")}
    assert check_variable_helper(interpreter, expected)


def test_type_declaration():
    with open(f"{interpreting_tests_path}/38_type_decl.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"p": {"name": "Alice", "age": 30}}
    assert check_variable_helper(interpreter, expected)


def test_class_declaration():
    with open(f"{interpreting_tests_path}/39_class_decl.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)

    c_var = interpreter.environment.get("c")
    c_instance = c_var.value

    assert isinstance(c_instance.sugar_class, SugarClass)
    assert c_instance.sugar_class.name == "Counter"

    assert "value" in c_instance.sugar_class.properties
    value_prop_decl = c_instance.sugar_class.properties["value"]
    assert isinstance(value_prop_decl, PropertyDeclaration)
    assert value_prop_decl.name.name == "value"
    assert value_prop_decl.property_type.name == "int"

    assert c_instance.sugar_class.constructor is not None
    assert isinstance(c_instance.sugar_class.constructor, Function)
    assert len(c_instance.sugar_class.constructor.params) == 0

    expected = {"c": {"value": 0}}
    assert check_variable_helper(interpreter, expected)


def test_class_method():
    with open(f"{interpreting_tests_path}/40_class_method.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)

    a_var = interpreter.environment.get("a")
    a_instance = a_var.value

    assert isinstance(a_instance.sugar_class, SugarClass)
    assert a_instance.sugar_class.name == "Adder"

    assert "value" in a_instance.sugar_class.properties
    value_prop_decl = a_instance.sugar_class.properties["value"]
    assert isinstance(value_prop_decl, PropertyDeclaration)
    assert value_prop_decl.name.name == "value"
    assert value_prop_decl.property_type.name == "int"

    assert a_instance.sugar_class.constructor is not None
    assert isinstance(a_instance.sugar_class.constructor, Function)
    assert len(a_instance.sugar_class.constructor.params) == 0

    expected = {"a": {"value": 10}, "r": 5, "b": 10}
    assert check_variable_helper(interpreter, expected)


def test_static_method():
    with open(f"{interpreting_tests_path}/41_static_method.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"s": 16}
    assert check_variable_helper(interpreter, expected)


def test_access_modifiers():
    with open(f"{interpreting_tests_path}/42_access_modifiers.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"x": 1}
    assert check_variable_helper(interpreter, expected)


def test_inheritance():
    with open(f"{interpreting_tests_path}/43_inheritance.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"r": 2}
    assert check_variable_helper(interpreter, expected)


def test_super_usage():
    with open(f"{interpreting_tests_path}/44_super_usage.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"v": 6}
    assert check_variable_helper(interpreter, expected)


def test_interface():
    with open(f"{interpreting_tests_path}/45_interface.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"r": 5}
    assert check_variable_helper(interpreter, expected)


def test_visibility_error():
    with open(f"{interpreting_tests_path}/46_visibility_error.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    with pytest.raises(TypeError):
        interpreter.interpret(ast)


def test_custom_error_type():
    with open(f"{interpreting_tests_path}/47_custom_error_type.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    with pytest.raises(Exception):
        interpreter.interpret(ast)


def test_try_catch():
    with open(f"{interpreting_tests_path}/48_try_catch.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"x": "fail!", "y": "done"}
    assert check_variable_helper(interpreter, expected)
    pass


def test_throw_builtin():
    with open(f"{interpreting_tests_path}/49_throw_builtin.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    with pytest.raises(ValueError) as e:
        interpreter.interpret(ast)


def test_spawn_basic():
    with open(f"{interpreting_tests_path}/50_spawn_basic.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"x": 1}
    assert check_variable_helper(interpreter, expected)


def test_spawn_join():
    with open(f"{interpreting_tests_path}/51_spawn_join.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"r": 42}
    assert check_variable_helper(interpreter, expected)


def test_stdlib_math():
    with open(f"{interpreting_tests_path}/52_stdlib_math.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {
        "pi_val": 3.141592653589793,
        "e_val": 2.718281828459045,
        "s_val": 4.0,
        "f_val": 5,
        "c_val": 6,
        "r_val": 6,
        "r_val2": 5,
        "p_val": 8.0,
        "a_val": 10.5,
        "min_val": 2.0,
        "min_single": 7.0,
        "max_val": 20.0,
        "max_single": 15.0,
        "sin_val": 1.0,
        "cos_val": -1.0,
        "tan_val": 0.9999999999999999,
        "asin_val": 1.5707963267948966,
        "acos_val": 1.5707963267948966,
        "atan_val": 0.7853981633974483,
        "log_val": 2.0,
        "log10_val": 3.0,
        "exp_val": 2.718281828459045,
        "fact_val": 120,
        "gcd_val": 6,
        "gcd_multi": 6,
        "lcm_val": 12,
        "lcm_multi": 12,
        "deg_val": 180.0,
        "rad_val": 3.141592653589793,
    }
    assert check_variable_helper(interpreter, expected)


def test_stdlib_io():
    with open(f"{interpreting_tests_path}/53_stdlib_io.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    # This test requires user input, so we can't fully automate it.
    # We'll just check that it doesn't crash.
    pass


def test_stdlib_time():
    with open(f"{interpreting_tests_path}/54_stdlib_time.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"for_test": "5/25/30"}
    assert check_variable_helper(interpreter, expected)
    pass


def test_stdlib_random():
    with open(f"{interpreting_tests_path}/55_stdlib_random.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"r": 7, "f": 0.7579544029403025}
    assert check_variable_helper(interpreter, expected)


def test_pattern_destructuring():
    with open(f"{interpreting_tests_path}/56_pattern_destructuring.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"s": "a"}
    assert check_variable_helper(interpreter, expected)


def test_complex_oop_inheritance():
    with open(f"{interpreting_tests_path}/57_COMPLEX_oop_inheritance.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {
        "c": {
            "x": 1,
            "y": 2,
            "radius": 3,
        },
        "u": {
            "x": 0,
            "y": 0,
            "radius": 1,
        },
    }
    assert check_variable_helper(interpreter, expected)


def test_complex_error_handling():
    with open(f"{interpreting_tests_path}/58_COMPLEX_error_handling.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    with pytest.raises(Exception):
        interpreter.interpret(ast)
    expected = {"y": "done"}
    assert check_variable_helper(interpreter, expected)


def test_tuple_pattern_matching():
    with open(f"{interpreting_tests_path}/59_tuple_pattern_matching.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"s": "match"}
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


def test_list_pattern_matching():
    with open(f"{interpreting_tests_path}/62_list_pattern_matching.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"s": "match"}
    assert check_variable_helper(interpreter, expected)


def test_object_pattern_matching():
    with open(f"{interpreting_tests_path}/63_object_pattern_matching.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {"s": "match"}
    assert check_variable_helper(interpreter, expected)


def test_match_statements_with_guard():
    with open(f"{interpreting_tests_path}/64_match_with_guard.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {
        "x": 2,
    }
    assert check_variable_helper(interpreter, expected)


def test_map_operations():
    with open(f"{interpreting_tests_path}/65_map_operations.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    expected = {
        "m": {
            "b": 2,
            "c": 3,
            "d": 4,
            "e": 5,
            "f": 6,
        },
        "to_update": {},
        "b": 2,
        "has_c": True,
        "keys": ["a", "b", "c"],
        "values": [1, 2, 3],
        "length": 3,
        "removed_a": 1,
        "default_x": 0,
    }
    assert check_variable_helper(interpreter, expected)


def test_import_from_module():
    with open(f"{interpreting_tests_path}/66_import.sugar", "r") as f:
        code = f.read()
    parser = Parser()
    ast = parser.parse(code)
    assert isinstance(ast, Program)
    path = Path(interpreting_tests_path / "66_import.sugar").resolve()
    interpreter = Interpreter(path)
    interpreter.interpret(ast)
    expected = {"r": 5, "c": 6}
    assert check_variable_helper(interpreter, expected)
