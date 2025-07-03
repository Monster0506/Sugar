import logging
from .values import SugarArray, SugarMap, SugarStr, SugarInt
from .literal_eval import LiteralEvaluator

class MethodCallEvaluator:
    """Handles evaluation of method calls."""
    @staticmethod
    def evaluate_method_call(node, target, env):
        if not hasattr(node, 'data') or node.data != 'method_call':
            return SugarInt(0)
        if len(node.children) < 2:
            return SugarInt(0)
        method_name_node = node.children[0]
        argument_list_node = node.children[1]
        if isinstance(target, SugarArray):
            return MethodCallEvaluator._handle_array_method(method_name_node, argument_list_node, target)
        elif isinstance(target, SugarMap):
            return MethodCallEvaluator._handle_map_method(method_name_node, argument_list_node, target)
        return SugarInt(0)
    @staticmethod
    def _handle_array_method(method_name_node, argument_list_node, target):
        if not hasattr(argument_list_node, 'data') or argument_list_node.data != 'argument_list':
            return SugarInt(0)
        if not argument_list_node.children:
            return SugarInt(0)
        index_literal = argument_list_node.children[0]
        index_value = LiteralEvaluator.evaluate_literal(index_literal)
        if isinstance(index_value, SugarInt):
            index = index_value.value
            if 0 <= index < len(target.elements):
                return target.elements[index]
            else:
                logging.getLogger("SugarInterpreter").error(f"Array index {index} out of bounds")
                return SugarInt(0)
        return SugarInt(0)
    @staticmethod
    def _handle_map_method(method_name_node, argument_list_node, target):
        if not hasattr(argument_list_node, 'data') or argument_list_node.data != 'argument_list':
            return SugarInt(0)
        if len(argument_list_node.children) == 1:
            return MethodCallEvaluator._handle_map_get(argument_list_node.children[0], target)
        elif len(argument_list_node.children) == 2:
            return MethodCallEvaluator._handle_map_set(argument_list_node.children[0], argument_list_node.children[1], target)
        return SugarInt(0)
    @staticmethod
    def _handle_map_get(key_literal, target):
        key = LiteralEvaluator.evaluate_literal(key_literal)
        if isinstance(key, SugarStr):
            if key.value in target.mapping:
                return target.mapping[key.value]
            else:
                logging.getLogger("SugarInterpreter").error(f"Map key '{key.value}' not found")
                return SugarInt(0)
        return SugarInt(0)
    @staticmethod
    def _handle_map_set(key_literal, value_literal, target):
        key = LiteralEvaluator.evaluate_literal(key_literal)
        value = LiteralEvaluator.evaluate_literal(value_literal)
        if isinstance(key, SugarStr):
            target.mapping[key.value] = value
            logging.getLogger("SugarInterpreter").info(f"Set map key '{key.value}' = {value}")
            return value
        else:
            logging.getLogger("SugarInterpreter").error(f"Invalid map key type")
            return SugarInt(0) 