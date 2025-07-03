from .var_decl import VariableDeclarationHandler
from .var_assign import VariableAssignmentHandler
from .expression_eval import ExpressionEvaluator

class StatementHandler:
    """Handles different types of statements."""
    def __init__(self, logger):
        self.logger = logger
        self.declaration_handler = VariableDeclarationHandler(logger)
        self.assignment_handler = VariableAssignmentHandler(logger)
    def handle_statement(self, node, env):
        if not hasattr(node, 'data'):
            return
        statement_handlers = {
            'variable_declaration': self.declaration_handler.handle_declaration,
            'variable_assignment': self.assignment_handler.handle_assignment,
            'expression_statement': self._handle_expression_statement
        }
        handler = statement_handlers.get(node.data)
        if handler:
            handler(node, env)
    def _handle_expression_statement(self, node, env):
        if (node.children and hasattr(node.children[0], 'data') and node.children[0].data == 'postfix_expression'):
            ExpressionEvaluator.evaluate_expression(node.children[0], env) 