from .literal_eval import LiteralEvaluator
from .collections_eval import CollectionEvaluator
from .expression_eval import ExpressionEvaluator
from .values import SugarArray, SugarMap

class VariableAssignmentHandler:
    """Handles variable assignments."""
    def __init__(self, logger):
        self.logger = logger
    def handle_assignment(self, node, env):
        if not hasattr(node, 'data') or node.data != 'variable_assignment':
            return
        if len(node.children) < 2:
            return
        name_token = node.children[0]
        expr = node.children[1]
        name = self._extract_identifier_name(name_token)
        old_val = env.get(name)
        if hasattr(expr, 'data') and expr.data == 'literal':
            self._handle_literal_assignment(name, expr, old_val, env)
        elif hasattr(expr, 'data') and expr.data == 'array_literal':
            self._handle_array_assignment(name, expr, old_val, env)
        elif hasattr(expr, 'data') and expr.data == 'dict_literal':
            self._handle_dict_assignment(name, expr, old_val, env)
        elif hasattr(expr, 'data') and expr.data == 'postfix_expression':
            self._handle_expression_assignment(name, expr, old_val, env)
        else:
            self.logger.warning(f"Non-literal expr in assignment to {name} not handled yet.")
    def _extract_identifier_name(self, name_token):
        if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
            return str(name_token.value)
        return str(name_token)
    def _handle_literal_assignment(self, name, expr, old_val, env):
        value = LiteralEvaluator.evaluate_literal(expr)
        if isinstance(value, type(old_val)):
            env.set(name, value)
            self.logger.info(f"Assigned {type(value).__name__} variable {name} := {value}")
        else:
            self.logger.warning(f"Assignment type mismatch or unsupported type for {name}.")
    def _handle_array_assignment(self, name, expr, old_val, env):
        if isinstance(old_val, SugarArray):
            elements = CollectionEvaluator.evaluate_array_literal(expr, env)
            env.set(name, SugarArray(elements))
            self.logger.info(f"Assigned array variable {name} := {elements}")
        else:
            self.logger.warning(f"Assignment type mismatch: {name} is not an array.")
    def _handle_dict_assignment(self, name, expr, old_val, env):
        if isinstance(old_val, SugarMap):
            mapping = CollectionEvaluator.evaluate_dict_literal(expr, env)
            env.set(name, SugarMap(mapping))
            self.logger.info(f"Assigned map variable {name} := {mapping}")
        else:
            self.logger.warning(f"Assignment type mismatch: {name} is not a map.")
    def _handle_expression_assignment(self, name, expr, old_val, env):
        value = ExpressionEvaluator.evaluate_expression(expr, env)
        if isinstance(value, type(old_val)):
            env.set(name, value)
            self.logger.info(f"Assigned variable {name} := {value}")
        else:
            self.logger.warning(f"Assignment type mismatch for {name}.") 