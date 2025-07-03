from .type_analysis import TypeAnalyzer
from .literal_eval import LiteralEvaluator
from .expression_eval import ExpressionEvaluator
from .collections_eval import CollectionEvaluator
from .values import SugarArray, SugarMap

class VariableDeclarationHandler:
    """Handles variable declarations."""
    def __init__(self, logger):
        self.logger = logger
    def handle_declaration(self, node, env):
        if not hasattr(node, 'data') or node.data != 'variable_declaration':
            return
        if len(node.children) < 3:
            return
        name_token = node.children[0]
        type_tree = node.children[1]
        expr = node.children[2]
        name = self._extract_identifier_name(name_token)
        type_name, is_array, is_map = TypeAnalyzer.extract_type_info(type_tree)
        
        if is_map:
            self._handle_map_declaration(name, expr, env)
        elif is_array:
            self._handle_array_declaration(name, expr, env)
        elif type_name:
            self._handle_primitive_declaration(name, type_name, expr, env)
        else:
            self.logger.warning(f"UNSUPPORTED TYPE in DEF {name} #... not handled yet.")
    def _extract_identifier_name(self, name_token):
        if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
            return str(name_token.value)
        return str(name_token)
    def _handle_map_declaration(self, name, expr, env):
        if hasattr(expr, 'data') and expr.data == 'dict_literal':
            mapping = CollectionEvaluator.evaluate_dict_literal(expr, env)
            env.set(name, SugarMap(mapping))
            self.logger.info(f"Declared map variable {name} = {mapping}")
        else:
            self.logger.warning(f"Non-dict literal in DEF {name} #{{#...}} = ... not handled yet.")
    def _handle_array_declaration(self, name, expr, env):
        if hasattr(expr, 'data') and expr.data == 'array_literal':
            elements = CollectionEvaluator.evaluate_array_literal(expr, env)
            env.set(name, SugarArray(elements))
            self.logger.info(f"Declared array variable {name} = {elements}")
        else:
            self.logger.warning(f"Non-array literal in DEF {name} #[#...] = ... not handled yet.")
    def _handle_primitive_declaration(self, name, type_name, expr, env):
        """Handle primitive variable declaration."""
        # Handle literal expressions
        if hasattr(expr, 'data') and expr.data == 'literal':
            self._handle_literal_declaration(name, type_name, expr, env)
        # Handle all other expression types
        elif hasattr(expr, 'data'):
            self._handle_expression_declaration(name, type_name, expr, env)
        else:
            self.logger.warning(f"Non-literal expr in DEF {name} #{type_name} = ... not handled yet.")
    def _handle_literal_declaration(self, name, type_name, expr, env):
        value = LiteralEvaluator.evaluate_literal(expr)
        env.set(name, value)
        self.logger.info(f"Declared {type_name} variable {name} = {value}")
    def _handle_expression_declaration(self, name, type_name, expr, env):
        value = ExpressionEvaluator.evaluate_expression(expr, env)
        env.set(name, value)
        self.logger.info(f"Declared {type_name} variable {name} = {value}") 