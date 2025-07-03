from .var_decl import VariableDeclarationHandler
from .var_assign import VariableAssignmentHandler
from .expression_eval import ExpressionEvaluator
from .values import SugarArray

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
            'expression_statement': self._handle_expression_statement,
            'if_statement': self._handle_if_statement,
            'for_statement': self._handle_for_statement
        }
        handler = statement_handlers.get(node.data)
        if handler:
            handler(node, env)
    def _handle_expression_statement(self, node, env):
        if (node.children and hasattr(node.children[0], 'data') and node.children[0].data == 'postfix_expression'):
            ExpressionEvaluator.evaluate_expression(node.children[0], env)
    def _handle_if_statement(self, node, env):
        """Handle if statement execution."""
        if not node.children:
            return
        
        # Evaluate condition (first child)
        condition_expr = node.children[0]
        condition_result = ExpressionEvaluator.evaluate_expression(condition_expr, env)
        
        # Check if condition is true
        if self._is_truthy(condition_result):
            # Execute if body (second child)
            if len(node.children) > 1:
                if_body = node.children[1]
                # Check if the body is a single statement or a block
                if hasattr(if_body, 'data') and if_body.data == 'variable_declaration':
                    # Single statement - execute directly
                    self.handle_statement(if_body, env)
                else:
                    # Block of statements - execute as block
                    self._execute_block(if_body, env)
        
        # Handle elif clauses (third child onwards, except the last one if it's an else_clause)
        elif_start = 2
        elif_end = len(node.children) - 1 if (node.children and 
                                             hasattr(node.children[-1], 'data') and 
                                             node.children[-1].data == 'else_clause') else len(node.children)
        
        for i in range(elif_start, elif_end):
            elif_node = node.children[i]
            if hasattr(elif_node, 'data') and elif_node.data == 'elif_clause':
                self._handle_elif_clause(elif_node, env)
        
        # Handle else clause (last child) if present
        if (node.children and hasattr(node.children[-1], 'data') and 
            node.children[-1].data == 'else_clause'):
            self._handle_else_clause(node.children[-1], env)
    def _handle_elif_clause(self, node, env):
        """Handle elif clause execution."""
        if not node.children or len(node.children) < 2:
            return
        
        # Evaluate condition (first child)
        condition_expr = node.children[0]
        condition_result = ExpressionEvaluator.evaluate_expression(condition_expr, env)
        
        # Check if condition is true
        if self._is_truthy(condition_result):
            # Execute elif body (second child)
            self._execute_block(node.children[1], env)
    def _handle_else_clause(self, node, env):
        """Handle else clause execution."""
        if not node.children:
            return
        
        # Execute else body (first child)
        self._execute_block(node.children[0], env)
    def _handle_for_statement(self, node, env):
        """Handle for statement execution."""
        if not node.children or len(node.children) < 4:
            return
        
        # Extract for loop components:
        # children[0] = iterator variable name (Token)
        # children[1] = iterator variable type (Tree)
        # children[2] = collection to iterate over (Token or Tree)
        # children[3:] = loop body statements (Tree)
        
        iterator_name = node.children[0]
        if hasattr(iterator_name, 'value'):
            iterator_name = iterator_name.value
        
        collection_expr = node.children[2]
        loop_body_statements = node.children[3:]
        
        # Evaluate the collection
        if hasattr(collection_expr, 'type') and collection_expr.type == 'IDENTIFIER':
            # Direct identifier - get from environment
            collection_name = str(collection_expr.value)
            try:
                collection_result = env.get(collection_name)
            except NameError:
                self.logger.warning(f"Collection variable '{collection_name}' not found")
                return
        else:
            # Expression node - evaluate it
            collection_result = ExpressionEvaluator.evaluate_expression(collection_expr, env)
        
        # Check if it's an array
        if isinstance(collection_result, SugarArray):
            # Iterate over array elements
            for element in collection_result.elements:
                # Set the iterator variable
                env.set(iterator_name, element)
                
                # Execute all statements in the loop body
                for statement in loop_body_statements:
                    self.handle_statement(statement, env)
        else:
            self.logger.warning(f"For loop collection is not an array: {collection_result}")
    def _execute_block(self, block_node, env):
        """Execute a block of statements."""
        if not hasattr(block_node, 'children'):
            return
        
        for i, child in enumerate(block_node.children):
            self.handle_statement(child, env)
    def _is_truthy(self, value):
        """Check if a value is truthy."""
        if hasattr(value, 'value'):
            return bool(value.value)
        return bool(value) 