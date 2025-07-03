import logging
from typing import Any, Dict, List, Optional, Union
from sugar_parser import Tree, Token

class SugarValue:
    """Base class for all Sugar runtime values."""
    pass

class SugarInt(SugarValue):
    def __init__(self, value: int):
        self.value = value
    def __repr__(self):
        return f"SugarInt({self.value=})"

class SugarFloat(SugarValue):
    def __init__(self, value: float):
        self.value = value
    def __repr__(self):
        return f"SugarFloat({self.value=})"
class SugarBool(SugarValue):
    def __init__(self, value: bool):
        self.value = value
    def __repr__(self):
        return f"SugarBool({self.value=})"
class SugarChar(SugarValue):
    def __init__(self, value: str):
        self.value = value
    def __repr__(self):
        return f"SugarChar({self.value=})"
class SugarStr(SugarValue):
    def __init__(self, value: str):
        self.value = value
    def __repr__(self):
        return f"SugarStr({self.value=})"
class SugarArray(SugarValue):
    def __init__(self, elements: List[SugarValue]):
        self.elements = elements
    def __repr__(self):
        return f"SugarArray({self.elements=})"
class SugarMap(SugarValue):
    def __init__(self, mapping: Dict[Any, SugarValue]):
        self.mapping = mapping
    def __repr__(self):
        return f"SugarMap({self.mapping=})"
class SugarTuple(SugarValue):
    def __init__(self, elements: List[SugarValue]):
        self.elements = elements
    def __repr__(self):
        return f"SugarTuple({self.elements=})"
class SugarObject(SugarValue):
    def __init__(self, class_name: str, fields: Dict[str, SugarValue]):
        self.class_name = class_name
        self.fields = fields
    def __repr__(self):
        return f"SugarObject({self.class_name=}, {self.fields=})"

class SugarEnvironment:
    """Represents a runtime environment (scope) for variables and functions."""
    def __init__(self, parent: Optional['SugarEnvironment'] = None):
        self.parent = parent
        self.variables: Dict[str, SugarValue] = {}

    def get(self, name: str) -> SugarValue:
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise NameError(f"Variable '{name}' not found")

    def set(self, name: str, value: SugarValue):
        self.variables[name] = value

    def __repr__(self):
        return f"SugarEnvironment({self.variables})"

class SugarCallFrame:
    """Represents a call stack frame for function/method calls."""
    def __init__(self, env: SugarEnvironment, function_name: Optional[str] = None):
        self.env = env
        self.function_name = function_name

class SugarInterpreter:
    def __init__(self, ast: Any, symbol_table: Any):
        self.ast = ast
        self.symbol_table = symbol_table
        self.global_env = SugarEnvironment()
        self.call_stack: List[SugarCallFrame] = []
        self.logger = logging.getLogger("SugarInterpreter")

    def run(self):
        self.logger.info("Interpreter started.")
        if hasattr(self.ast, 'data') and self.ast.data == 'program':
            for stmt in self.ast.children:
                self.execute_statement(stmt, self.global_env)
        self.logger.info(f"Global environment after execution: {self.global_env}")

    def execute_statement(self, node, env: SugarEnvironment):
        if hasattr(node, 'data') and node.data == 'variable_declaration':
            self.execute_variable_declaration(node, env)
        elif hasattr(node, 'data') and node.data == 'variable_assignment':
            self.execute_variable_assignment(node, env)
        # Ignore all other statements for now

    def execute_variable_declaration(self, node, env: SugarEnvironment):
        # Only handle DEF x #int = <int> and DEF x #float = <float> for now
        # Structure: [IDENTIFIER, type_tree, expr]
        name_token = node.children[0]
        type_tree = node.children[1]
        expr = node.children[2]
        if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
            name = str(name_token.value)
        else:
            name = str(name_token)
        # Handle type: type -> primitive_type -> INT_TYPE, FLOAT_TYPE, BOOL_TYPE, CHAR_TYPE, STR_TYPE
        # OR type -> array_type -> type -> primitive_type -> INT_TYPE, etc.
        type_name = None
        is_array = False
        if hasattr(type_tree, 'data') and type_tree.data == 'type':
            if type_tree.children and hasattr(type_tree.children[0], 'data') and type_tree.children[0].data == 'primitive_type':
                prim_type_node = type_tree.children[0]
                if prim_type_node.children and hasattr(prim_type_node.children[0], 'type'):
                    ttype = prim_type_node.children[0].type
                    if ttype == 'INT_TYPE':
                        type_name = 'int'
                    elif ttype == 'FLOAT_TYPE':
                        type_name = 'float'
                    elif ttype == 'BOOL_TYPE':
                        type_name = 'bool'
                    elif ttype == 'CHAR_TYPE':
                        type_name = 'char'
                    elif ttype == 'STR_TYPE':
                        type_name = 'str'
            elif type_tree.children and hasattr(type_tree.children[0], 'data') and type_tree.children[0].data == 'array_type':
                is_array = True
                # Extract the element type from array_type -> type -> primitive_type
                array_type_node = type_tree.children[0]
                if array_type_node.children and hasattr(array_type_node.children[0], 'data') and array_type_node.children[0].data == 'type':
                    element_type_node = array_type_node.children[0]
                    if element_type_node.children and hasattr(element_type_node.children[0], 'data') and element_type_node.children[0].data == 'primitive_type':
                        prim_type_node = element_type_node.children[0]
                        if prim_type_node.children and hasattr(prim_type_node.children[0], 'type'):
                            ttype = prim_type_node.children[0].type
                            if ttype == 'INT_TYPE':
                                type_name = 'int'
                            elif ttype == 'FLOAT_TYPE':
                                type_name = 'float'
                            elif ttype == 'BOOL_TYPE':
                                type_name = 'bool'
                            elif ttype == 'CHAR_TYPE':
                                type_name = 'char'
                            elif ttype == 'STR_TYPE':
                                type_name = 'str'
        
        if is_array:
            # Handle array declaration
            if hasattr(expr, 'data') and expr.data == 'array_literal':
                elements = self.evaluate_array_literal(expr, env)
                env.set(name, SugarArray(elements))
                self.logger.info(f"Declared array variable {name} = {elements}")
                return
            else:
                self.logger.warning(f"Non-array literal in DEF {name} #[#...] = ... not handled yet.")
        elif type_name == 'int':
            # expr is a literal node or expression
            if hasattr(expr, 'data') and expr.data == 'literal':
                if expr.children and hasattr(expr.children[0], 'type') and expr.children[0].type == 'INTEGER':
                    value = int(expr.children[0].value)
                    env.set(name, SugarInt(value))
                    self.logger.info(f"Declared int variable {name} = {value}")
                    return
                else:
                    self.logger.warning(f"Non-integer literal in DEF {name} #int = ... not handled yet.")
            elif hasattr(expr, 'data') and expr.data == 'postfix_expression':
                # Handle method calls like arr :GET: (0)
                value = self.evaluate_expression(expr, env)
                if isinstance(value, SugarInt):
                    env.set(name, value)
                    self.logger.info(f"Declared int variable {name} = {value}")
                    return
                else:
                    self.logger.warning(f"Expression result is not int for {name}.")
            else:
                self.logger.warning(f"Non-literal expr in DEF {name} #int = ... not handled yet.")
        elif type_name == 'float':
            if hasattr(expr, 'data') and expr.data == 'literal':
                if expr.children and hasattr(expr.children[0], 'type') and expr.children[0].type == 'FLOAT':
                    value = float(expr.children[0].value)
                    env.set(name, SugarFloat(value))
                    self.logger.info(f"Declared float variable {name} = {value}")
                    return
                else:
                    self.logger.warning(f"Non-float literal in DEF {name} #float = ... not handled yet.")
            else:
                self.logger.warning(f"Non-literal expr in DEF {name} #float = ... not handled yet.")
        elif type_name == 'bool':
            if hasattr(expr, 'data') and expr.data == 'literal':
                if expr.children and hasattr(expr.children[0], 'type') and expr.children[0].type == 'BOOLEAN':
                    token_val = expr.children[0].value
                    value = True if token_val == ':T:' else False
                    env.set(name, SugarBool(value))
                    self.logger.info(f"Declared bool variable {name} = {value}")
                    return
                else:
                    self.logger.warning(f"Non-bool literal in DEF {name} #bool = ... not handled yet.")
            else:
                self.logger.warning(f"Non-literal expr in DEF {name} #bool = ... not handled yet.")
        elif type_name == 'char':
            if hasattr(expr, 'data') and expr.data == 'literal':
                if expr.children and hasattr(expr.children[0], 'type') and expr.children[0].type == 'CHAR':
                    value = expr.children[0].value
                    env.set(name, SugarChar(value))
                    self.logger.info(f"Declared char variable {name} = {value}")
                    return
                else:
                    self.logger.warning(f"Non-char literal in DEF {name} #char = ... not handled yet.")
            else:
                self.logger.warning(f"Non-literal expr in DEF {name} #char = ... not handled yet.")
        elif type_name == 'str':
            if hasattr(expr, 'data') and expr.data == 'literal':
                if expr.children and hasattr(expr.children[0], 'type') and expr.children[0].type == 'STRING':
                    value = expr.children[0].value
                    env.set(name, SugarStr(value))
                    self.logger.info(f"Declared str variable {name} = {value}")
                    return
                else:
                    self.logger.warning(f"Non-string literal in DEF {name} #str = ... not handled yet.")
            else:
                self.logger.warning(f"Non-literal expr in DEF {name} #str = ... not handled yet.")
        else:
            self.logger.warning(f"UNSUPPORTED TYPE in DEF {name} #... not handled yet.")

    def evaluate_array_literal(self, node, env: SugarEnvironment) -> List[SugarValue]:
        """Evaluate an array literal node and return a list of SugarValues."""
        if hasattr(node, 'data') and node.data == 'array_literal':
            if node.children and hasattr(node.children[0], 'data') and node.children[0].data == 'argument_list':
                arg_list = node.children[0]
                elements = []
                for child in arg_list.children:
                    if hasattr(child, 'data') and child.data == 'literal':
                        element = self.evaluate_literal(child)
                        elements.append(element)
                return elements
        return []

    def evaluate_literal(self, node) -> SugarValue:
        """Evaluate a literal node and return a SugarValue."""
        if hasattr(node, 'data') and node.data == 'literal':
            if node.children and hasattr(node.children[0], 'type'):
                ttype = node.children[0].type
                if ttype == 'INTEGER':
                    return SugarInt(int(node.children[0].value))
                elif ttype == 'FLOAT':
                    return SugarFloat(float(node.children[0].value))
                elif ttype == 'BOOLEAN':
                    token_val = node.children[0].value
                    return SugarBool(True if token_val == ':T:' else False)
                elif ttype == 'CHAR':
                    return SugarChar(node.children[0].value)
                elif ttype == 'STRING':
                    return SugarStr(node.children[0].value)
        return SugarInt(0)  # Default fallback

    def evaluate_expression(self, node, env: SugarEnvironment) -> SugarValue:
        """Evaluate an expression node and return a SugarValue."""
        if hasattr(node, 'data') and node.data == 'postfix_expression':
            # Handle postfix expressions like arr :GET: (0)
            if len(node.children) >= 2:
                # First child is the identifier (arr)
                # Second child is the method call (:GET: (0))
                identifier = node.children[0]
                method_call = node.children[1]
                
                if hasattr(identifier, 'type') and identifier.type == 'IDENTIFIER':
                    var_name = str(identifier.value)
                    var_value = env.get(var_name)
                    
                    if isinstance(var_value, SugarArray) and hasattr(method_call, 'data') and method_call.data == 'method_call':
                        # Handle array access method call
                        return self.evaluate_method_call(method_call, var_value, env)
        
        return SugarInt(0)  # Default fallback

    def evaluate_method_call(self, node, target: SugarValue, env: SugarEnvironment) -> SugarValue:
        """Evaluate a method call node and return a SugarValue."""
        if hasattr(node, 'data') and node.data == 'method_call':
            if len(node.children) >= 2:
                method_name_node = node.children[0]
                argument_list_node = node.children[1]
                
                # For now, assume it's a GET method call
                if isinstance(target, SugarArray):
                    # Extract the index from argument_list
                    if hasattr(argument_list_node, 'data') and argument_list_node.data == 'argument_list':
                        if argument_list_node.children and hasattr(argument_list_node.children[0], 'data') and argument_list_node.children[0].data == 'literal':
                            index_literal = argument_list_node.children[0]
                            index_value = self.evaluate_literal(index_literal)
                            if isinstance(index_value, SugarInt):
                                index = index_value.value
                                if 0 <= index < len(target.elements):
                                    return target.elements[index]
                                else:
                                    self.logger.error(f"Array index {index} out of bounds")
                                    return SugarInt(0)
        
        return SugarInt(0)  # Default fallback

    def execute_variable_assignment(self, node, env: SugarEnvironment):
        # Structure: [IDENTIFIER, expr]
        name_token = node.children[0]
        expr = node.children[1]
        if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
            name = str(name_token.value)
        else:
            name = str(name_token)
        old_val = env.get(name)
        # int assignment
        if hasattr(expr, 'data') and expr.data == 'literal':
            if expr.children and hasattr(expr.children[0], 'type'):
                ttype = expr.children[0].type
                if ttype == 'INTEGER' and isinstance(old_val, SugarInt):
                    value = int(expr.children[0].value)
                    env.set(name, SugarInt(value))
                    self.logger.info(f"Assigned int variable {name} := {value}")
                elif ttype == 'FLOAT' and isinstance(old_val, SugarFloat):
                    value = float(expr.children[0].value)
                    env.set(name, SugarFloat(value))
                    self.logger.info(f"Assigned float variable {name} := {value}")
                elif ttype == 'BOOLEAN' and isinstance(old_val, SugarBool):
                    token_val = expr.children[0].value
                    value = True if token_val == ':T:' else False
                    env.set(name, SugarBool(value))
                    self.logger.info(f"Assigned bool variable {name} := {value}")
                elif ttype == 'CHAR' and isinstance(old_val, SugarChar):
                    value = expr.children[0].value
                    env.set(name, SugarChar(value))
                    self.logger.info(f"Assigned char variable {name} := {value}")
                elif ttype == 'STRING' and isinstance(old_val, SugarStr):
                    value = expr.children[0].value
                    env.set(name, SugarStr(value))
                    self.logger.info(f"Assigned str variable {name} := {value}")
                else:
                    self.logger.warning(f"Assignment type mismatch or unsupported type for {name}.")
            else:
                self.logger.warning(f"Malformed literal in assignment to {name}.")
        elif hasattr(expr, 'data') and expr.data == 'array_literal':
            # Array assignment
            if isinstance(old_val, SugarArray):
                elements = self.evaluate_array_literal(expr, env)
                env.set(name, SugarArray(elements))
                self.logger.info(f"Assigned array variable {name} := {elements}")
            else:
                self.logger.warning(f"Assignment type mismatch: {name} is not an array.")
        elif hasattr(expr, 'data') and expr.data == 'postfix_expression':
            # Handle expressions like arr :GET: (2)
            value = self.evaluate_expression(expr, env)
            if isinstance(value, type(old_val)):
                env.set(name, value)
                self.logger.info(f"Assigned variable {name} := {value}")
            else:
                self.logger.warning(f"Assignment type mismatch for {name}.")
        else:
            self.logger.warning(f"Non-literal expr in assignment to {name} not handled yet.") 