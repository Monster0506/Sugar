from .values import SugarArray, SugarMap, SugarInt, SugarBool
from .method_eval import MethodCallEvaluator
from .literal_eval import LiteralEvaluator

class ExpressionEvaluator:
    """Handles evaluation of expressions."""
    @staticmethod
    def evaluate_expression(node, env):
        """Evaluate an expression node and return a SugarValue."""
        if not hasattr(node, 'data'):
            return SugarInt(0)
            
        # Handle different expression types
        if node.data == 'postfix_expression':
            return ExpressionEvaluator._evaluate_postfix_expression(node, env)
        elif node.data == 'relational_expression':
            return ExpressionEvaluator._evaluate_relational_expression(node, env)
        elif node.data == 'and_expression':
            return ExpressionEvaluator._evaluate_and_expression(node, env)
        elif node.data == 'or_expression':
            return ExpressionEvaluator._evaluate_or_expression(node, env)
        elif node.data == 'equality_expression':
            return ExpressionEvaluator._evaluate_equality_expression(node, env)
        elif node.data == 'additive_expression':
            return ExpressionEvaluator._evaluate_additive_expression(node, env)
        elif node.data == 'multiplicative_expression':
            return ExpressionEvaluator._evaluate_multiplicative_expression(node, env)
        elif node.data == 'unary_expression':
            return ExpressionEvaluator._evaluate_unary_expression(node, env)
        elif node.data == 'primary_expression':
            return ExpressionEvaluator._evaluate_primary_expression(node, env)
        
        return SugarInt(0)
    
    @staticmethod
    def _evaluate_postfix_expression(node, env):
        """Handle postfix expressions like arr :GET: (0)."""
        if len(node.children) < 2:
            return SugarInt(0)
            
        identifier = node.children[0]
        method_call = node.children[1]
        
        if not hasattr(identifier, 'type') or identifier.type != 'IDENTIFIER':
            return SugarInt(0)
            
        var_name = str(identifier.value)
        try:
            var_value = env.get(var_name)
        except NameError:
            return SugarInt(0)
        
        if (isinstance(var_value, (SugarArray, SugarMap)) and 
            hasattr(method_call, 'data') and method_call.data == 'method_call'):
            return MethodCallEvaluator.evaluate_method_call(method_call, var_value, env)
        
        return SugarInt(0)
    
    @staticmethod
    def _evaluate_relational_expression(node, env):
        """Handle relational expressions like 3 :LT: 5."""
        if len(node.children) != 3:
            return SugarBool(False)
            
        left_expr = node.children[0]
        op_node = node.children[1]
        right_expr = node.children[2]
        
        # Evaluate left and right operands
        left_val = ExpressionEvaluator._evaluate_operand(left_expr, env)
        right_val = ExpressionEvaluator._evaluate_operand(right_expr, env)
        
        # Get the operator
        if not hasattr(op_node, 'data') or op_node.data != 'relational_op':
            return SugarBool(False)
            
        if not op_node.children or not hasattr(op_node.children[0], 'type'):
            return SugarBool(False)
            
        op_type = op_node.children[0].type
        
        # Perform the comparison
        if isinstance(left_val, SugarInt) and isinstance(right_val, SugarInt):
            left_num = left_val.value
            right_num = right_val.value
            
            if op_type == 'LESS_THAN':  # :LT:
                return SugarBool(left_num < right_num)
            elif op_type == 'GREATER_THAN':  # :GT:
                return SugarBool(left_num > right_num)
            elif op_type == 'LESS_THAN_OR_EQUAL_TO':  # :LE:
                return SugarBool(left_num <= right_num)
            elif op_type == 'GREATER_THAN_OR_EQUAL_TO':  # :GE:
                return SugarBool(left_num >= right_num)
        
        return SugarBool(False)
    
    @staticmethod
    def _evaluate_and_expression(node, env):
        """Handle AND expressions like a && b."""
        if len(node.children) != 3:
            return SugarBool(False)
            
        left_expr = node.children[0]
        op_node = node.children[1]
        right_expr = node.children[2]
        
        # Evaluate left operand
        left_val = ExpressionEvaluator._evaluate_operand(left_expr, env)
        
        # Short-circuit: if left is false, return false
        if isinstance(left_val, SugarBool) and not left_val.value:
            return SugarBool(False)
        
        # Evaluate right operand
        right_val = ExpressionEvaluator._evaluate_operand(right_expr, env)
        
        # Both must be true
        if isinstance(left_val, SugarBool) and isinstance(right_val, SugarBool):
            return SugarBool(left_val.value and right_val.value)
        
        return SugarBool(False)
    
    @staticmethod
    def _evaluate_or_expression(node, env):
        """Handle OR expressions like a || b."""
        if len(node.children) != 3:
            return SugarBool(False)
            
        left_expr = node.children[0]
        op_node = node.children[1]
        right_expr = node.children[2]
        
        # Evaluate left operand
        left_val = ExpressionEvaluator._evaluate_operand(left_expr, env)
        
        # Short-circuit: if left is true, return true
        if isinstance(left_val, SugarBool) and left_val.value:
            return SugarBool(True)
        
        # Evaluate right operand
        right_val = ExpressionEvaluator._evaluate_operand(right_expr, env)
        
        # At least one must be true
        if isinstance(left_val, SugarBool) and isinstance(right_val, SugarBool):
            return SugarBool(left_val.value or right_val.value)
        
        return SugarBool(False)
    
    @staticmethod
    def _evaluate_equality_expression(node, env):
        """Handle equality expressions like a == b."""
        if len(node.children) != 3:
            return SugarBool(False)
            
        left_expr = node.children[0]
        op_node = node.children[1]
        right_expr = node.children[2]
        
        left_val = ExpressionEvaluator._evaluate_operand(left_expr, env)
        right_val = ExpressionEvaluator._evaluate_operand(right_expr, env)
        
        if not hasattr(op_node, 'data') or op_node.data != 'equality_op':
            return SugarBool(False)
            
        if not op_node.children or not hasattr(op_node.children[0], 'type'):
            return SugarBool(False)
            
        op_type = op_node.children[0].type
        
        if op_type == 'EQUAL_TO':  # ==
            return SugarBool(left_val.value == right_val.value)
        elif op_type == 'NOT_EQUAL_TO':  # !=
            return SugarBool(left_val.value != right_val.value)
        
        return SugarBool(False)
    
    @staticmethod
    def _evaluate_additive_expression(node, env):
        """Handle additive expressions like a + b."""
        if len(node.children) != 3:
            return SugarInt(0)
            
        left_expr = node.children[0]
        op_node = node.children[1]
        right_expr = node.children[2]
        
        left_val = ExpressionEvaluator._evaluate_operand(left_expr, env)
        right_val = ExpressionEvaluator._evaluate_operand(right_expr, env)
        
        if isinstance(left_val, SugarInt) and isinstance(right_val, SugarInt):
            left_num = left_val.value
            right_num = right_val.value
            
            # For now, just handle + and -
            return SugarInt(left_num + right_num)  # Simplified
        
        return SugarInt(0)
    
    @staticmethod
    def _evaluate_multiplicative_expression(node, env):
        """Handle multiplicative expressions like a * b."""
        if len(node.children) != 3:
            return SugarInt(0)
            
        left_expr = node.children[0]
        op_node = node.children[1]
        right_expr = node.children[2]
        
        left_val = ExpressionEvaluator._evaluate_operand(left_expr, env)
        right_val = ExpressionEvaluator._evaluate_operand(right_expr, env)
        
        if isinstance(left_val, SugarInt) and isinstance(right_val, SugarInt):
            left_num = left_val.value
            right_num = right_val.value
            
            # For now, just handle *
            return SugarInt(left_num * right_num)  # Simplified
        
        return SugarInt(0)
    
    @staticmethod
    def _evaluate_unary_expression(node, env):
        """Handle unary expressions like !a."""
        if len(node.children) != 2:
            return SugarInt(0)
            
        op_node = node.children[0]
        operand_expr = node.children[1]
        
        operand_val = ExpressionEvaluator._evaluate_operand(operand_expr, env)
        
        if not hasattr(op_node, 'type'):
            return SugarInt(0)
            
        op_type = op_node.type
        
        if op_type == 'NOT' and isinstance(operand_val, SugarBool):
            return SugarBool(not operand_val.value)
        
        return SugarInt(0)
    
    @staticmethod
    def _evaluate_primary_expression(node, env):
        """Handle primary expressions like literals and identifiers."""
        if not node.children:
            return SugarInt(0)
            
        child = node.children[0]
        
        if hasattr(child, 'data') and child.data == 'literal':
            return LiteralEvaluator.evaluate_literal(child)
        elif hasattr(child, 'type') and child.type == 'IDENTIFIER':
            var_name = str(child.value)
            try:
                return env.get(var_name)
            except NameError:
                return SugarInt(0)
        
        return SugarInt(0)
    
    @staticmethod
    def _evaluate_operand(operand, env):
        """Evaluate an operand (could be a literal, identifier, or expression)."""
        if hasattr(operand, 'data'):
            if operand.data == 'literal':
                return LiteralEvaluator.evaluate_literal(operand)
            elif operand.data in ['relational_expression', 'and_expression', 'or_expression', 
                                'equality_expression', 'additive_expression', 'multiplicative_expression',
                                'unary_expression', 'primary_expression']:
                return ExpressionEvaluator.evaluate_expression(operand, env)
        elif hasattr(operand, 'type') and operand.type == 'IDENTIFIER':
            var_name = str(operand.value)
            try:
                return env.get(var_name)
            except NameError:
                return SugarInt(0)
        
        return SugarInt(0) 