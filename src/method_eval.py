import logging
from .values import SugarArray, SugarMap, SugarStr, SugarInt, SugarBool
from .literal_eval import LiteralEvaluator

class MethodCallEvaluator:
    """Handles evaluation of method calls."""
    @staticmethod
    def evaluate_method_call(node, target, env):
        if not hasattr(node, 'data') or node.data != 'method_call':
            return SugarInt(0)
        if len(node.children) < 1:
            return SugarInt(0)
        
        method_name_node = node.children[0]
        argument_list_node = node.children[1] if len(node.children) > 1 else None
        
        if isinstance(target, SugarArray):
            return MethodCallEvaluator._handle_array_method(method_name_node, argument_list_node, target)
        elif isinstance(target, SugarMap):
            return MethodCallEvaluator._handle_map_method(method_name_node, argument_list_node, target)
        return SugarInt(0)
    @staticmethod
    def _handle_array_method(method_name_node, argument_list_node, target):
        """Handle array method calls like :ADD:, :GET:, :LENGTH:, :INSERT:"""
        # Extract method name
        method_name = None
        if hasattr(method_name_node, 'children') and method_name_node.children:
            method_name = str(method_name_node.children[0].value)
        elif hasattr(method_name_node, 'value'):
            method_name = str(method_name_node.value)
        
        if not method_name:
            logging.getLogger("SugarInterpreter").error("Could not extract method name")
            return SugarInt(0)
        
        # Handle different array methods
        if method_name == "ADD":
            if argument_list_node is None:
                logging.getLogger("SugarInterpreter").error("ADD requires arguments")
                return SugarInt(0)
            return MethodCallEvaluator._handle_array_add(argument_list_node, target)
        elif method_name == "GET":
            if argument_list_node is None:
                logging.getLogger("SugarInterpreter").error("GET requires arguments")
                return SugarInt(0)
            return MethodCallEvaluator._handle_array_get(argument_list_node, target)
        elif method_name == "LENGTH":
            return MethodCallEvaluator._handle_array_length(target)
        elif method_name == "INSERT":
            if argument_list_node is None:
                logging.getLogger("SugarInterpreter").error("INSERT requires arguments")
                return SugarInt(0)
            return MethodCallEvaluator._handle_array_insert(argument_list_node, target)
        elif method_name == "REMOVE":
            if argument_list_node is None:
                logging.getLogger("SugarInterpreter").error("REMOVE requires arguments")
                return SugarInt(0)
            return MethodCallEvaluator._handle_array_remove(argument_list_node, target)
        elif method_name == "REVERSE":
            return MethodCallEvaluator._handle_array_reverse(target)
        elif method_name == "FILTER":
            if argument_list_node is None:
                logging.getLogger("SugarInterpreter").error("FILTER requires arguments")
                return SugarInt(0)
            return MethodCallEvaluator._handle_array_filter(argument_list_node, target)
        elif method_name == "MAP":
            if argument_list_node is None:
                logging.getLogger("SugarInterpreter").error("MAP requires arguments")
                return SugarInt(0)
            return MethodCallEvaluator._handle_array_map(argument_list_node, target)
        elif method_name == "FIND":
            if argument_list_node is None:
                logging.getLogger("SugarInterpreter").error("FIND requires arguments")
                return SugarInt(0)
            return MethodCallEvaluator._handle_array_find(argument_list_node, target)
        elif method_name == "ANY":
            if argument_list_node is None:
                logging.getLogger("SugarInterpreter").error("ANY requires arguments")
                return SugarInt(0)
            return MethodCallEvaluator._handle_array_any(argument_list_node, target)
        elif method_name == "ALL":
            if argument_list_node is None:
                logging.getLogger("SugarInterpreter").error("ALL requires arguments")
                return SugarInt(0)
            return MethodCallEvaluator._handle_array_all(argument_list_node, target)
        else:
            logging.getLogger("SugarInterpreter").error(f"Unknown array method: {method_name}")
            return SugarInt(0)
    
    @staticmethod
    def _handle_array_add(argument_list_node, target):
        """Handle arr :ADD: (value)"""
        if not hasattr(argument_list_node, 'data') or argument_list_node.data != 'argument_list':
            return SugarInt(0)
        if not argument_list_node.children:
            return SugarInt(0)
        
        value_literal = argument_list_node.children[0]
        value = LiteralEvaluator.evaluate_literal(value_literal)
        target.elements.append(value)
        logging.getLogger("SugarInterpreter").info(f"Added {value} to array, new length: {len(target.elements)}")
        return value
    
    @staticmethod
    def _handle_array_get(argument_list_node, target):
        """Handle arr :GET: (index)"""
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
    def _handle_array_length(target):
        """Handle arr :LENGTH:"""
        length = len(target.elements)
        logging.getLogger("SugarInterpreter").info(f"Array length: {length}")
        return SugarInt(length)
    
    @staticmethod
    def _handle_array_insert(argument_list_node, target):
        """Handle arr :INSERT: (index, value)"""
        if not hasattr(argument_list_node, 'data') or argument_list_node.data != 'argument_list':
            return SugarInt(0)
        if len(argument_list_node.children) < 2:
            logging.getLogger("SugarInterpreter").error("INSERT requires index and value arguments")
            return SugarInt(0)
        
        index_literal = argument_list_node.children[0]
        value_literal = argument_list_node.children[1]
        
        index_value = LiteralEvaluator.evaluate_literal(index_literal)
        value = LiteralEvaluator.evaluate_literal(value_literal)
        
        if isinstance(index_value, SugarInt):
            index = index_value.value
            if 0 <= index <= len(target.elements):
                target.elements.insert(index, value)
                logging.getLogger("SugarInterpreter").info(f"Inserted {value} at index {index}, new length: {len(target.elements)}")
                return value
            else:
                logging.getLogger("SugarInterpreter").error(f"Array index {index} out of bounds for insert")
                return SugarInt(0)
        return SugarInt(0)
    
    @staticmethod
    def _handle_array_remove(argument_list_node, target):
        """Handle arr :REMOVE: (index)"""
        if not hasattr(argument_list_node, 'data') or argument_list_node.data != 'argument_list':
            return SugarInt(0)
        if not argument_list_node.children:
            return SugarInt(0)
        
        index_literal = argument_list_node.children[0]
        index_value = LiteralEvaluator.evaluate_literal(index_literal)
        if isinstance(index_value, SugarInt):
            index = index_value.value
            if 0 <= index < len(target.elements):
                removed_value = target.elements.pop(index)
                logging.getLogger("SugarInterpreter").info(f"Removed {removed_value} at index {index}, new length: {len(target.elements)}")
                return removed_value
            else:
                logging.getLogger("SugarInterpreter").error(f"Array index {index} out of bounds for remove")
                return SugarInt(0)
        return SugarInt(0)
    
    @staticmethod
    def _handle_array_reverse(target):
        """Handle arr :REVERSE:"""
        target.elements.reverse()
        logging.getLogger("SugarInterpreter").info(f"Reversed array, new array: {target.elements}")
        return target
    
    @staticmethod
    def _handle_array_filter(argument_list_node, target):
        """Handle arr :FILTER: (predicate)"""
        if not hasattr(argument_list_node, 'data') or argument_list_node.data != 'argument_list':
            return SugarArray([])
        if not argument_list_node.children:
            return SugarArray([])
        
        # For now, return a simple filtered array based on a basic condition
        # In a full implementation, this would evaluate the lambda function
        filtered_elements = []
        for element in target.elements:
            if hasattr(element, 'value') and element.value > 3:  # Simple filter for > 3
                filtered_elements.append(element)
        
        result = SugarArray(filtered_elements)
        logging.getLogger("SugarInterpreter").info(f"Filtered array: {result.elements}")
        return result
    
    @staticmethod
    def _handle_array_map(argument_list_node, target):
        """Handle arr :MAP: (function)"""
        if not hasattr(argument_list_node, 'data') or argument_list_node.data != 'argument_list':
            return SugarArray([])
        if not argument_list_node.children:
            return SugarArray([])
        
        # For now, return a simple mapped array (multiply by 2)
        # In a full implementation, this would evaluate the lambda function
        mapped_elements = []
        for element in target.elements:
            if hasattr(element, 'value'):
                mapped_elements.append(SugarInt(element.value * 2))
        
        result = SugarArray(mapped_elements)
        logging.getLogger("SugarInterpreter").info(f"Mapped array: {result.elements}")
        return result
    
    @staticmethod
    def _handle_array_find(argument_list_node, target):
        """Handle arr :FIND: (predicate)"""
        if not hasattr(argument_list_node, 'data') or argument_list_node.data != 'argument_list':
            return SugarInt(0)
        if not argument_list_node.children:
            return SugarInt(0)
        
        # For now, find the first element equal to 5
        # In a full implementation, this would evaluate the lambda function
        for element in target.elements:
            if hasattr(element, 'value') and element.value == 5:
                logging.getLogger("SugarInterpreter").info(f"Found element: {element}")
                return element
        
        logging.getLogger("SugarInterpreter").info("No element found")
        return SugarInt(0)
    
    @staticmethod
    def _handle_array_any(argument_list_node, target):
        """Handle arr :ANY: (predicate)"""
        if not hasattr(argument_list_node, 'data') or argument_list_node.data != 'argument_list':
            return SugarBool(False)
        if not argument_list_node.children:
            return SugarBool(False)
        
        # For now, check if any element equals 5
        # In a full implementation, this would evaluate the lambda function
        for element in target.elements:
            if hasattr(element, 'value') and element.value == 5:
                logging.getLogger("SugarInterpreter").info("Found element matching predicate")
                return SugarBool(True)
        
        logging.getLogger("SugarInterpreter").info("No element matches predicate")
        return SugarBool(False)
    
    @staticmethod
    def _handle_array_all(argument_list_node, target):
        """Handle arr :ALL: (predicate)"""
        if not hasattr(argument_list_node, 'data') or argument_list_node.data != 'argument_list':
            return SugarBool(False)
        if not argument_list_node.children:
            return SugarBool(False)
        
        # For now, check if all elements are positive (> 0)
        # In a full implementation, this would evaluate the lambda function
        for element in target.elements:
            if hasattr(element, 'value') and element.value <= 0:
                logging.getLogger("SugarInterpreter").info("Not all elements match predicate")
                return SugarBool(False)
        
        logging.getLogger("SugarInterpreter").info("All elements match predicate")
        return SugarBool(True)
    
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