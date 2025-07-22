from dataclasses import dataclass

from lark.tree import ParseTree

from src.ast_nodes import *
from src.type_checker import TypeChecker


@dataclass
class Variable:
    value: str
    var_type: Type


@dataclass
class Function:
    params: list
    body: list
    return_type: Type


class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing
        self.type_checker = TypeChecker()

    def define(self, name, value, var_type: Type):
        if isinstance(value, Function):

            if name in self.values.keys() and self.values[name]:
                self.values[name].append(value)
            else:
                self.values[name] = [value]
        else:
            self.type_checker.assert_type(value, var_type)
            self.values[name] = Variable(value, var_type)

    def assign(self, name, value):
        if name in self.values:
            if isinstance(self.values[name], Variable):
                self.type_checker.assert_type(value, self.values[name].var_type)
                self.values[name] = Variable(value, self.values[name].var_type)
            else:
                raise TypeError(f"Cannot assign to function '{name}'.")
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        raise NameError(f"Undefined variable '{name}'.")

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise NameError(f"Undefined variable '{name}'.")

    def __repr__(self) -> str:
        attrs: str = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"


class Interpreter:
    def __init__(self):
        self.environment = Environment()
        self.return_value = None

    def interpret(self, program: Program | ParseTree):
        for statement in program.statements:
            self.visit(statement)

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        print(f"visiting {method_name} with {node}")
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, method_name):
        print(f"Calling generic_visit with {method_name}")
        raise NotImplemented

    def visit_Identifier(self, node: Identifier):
        return (
            self.environment.get(node.name).value
            if isinstance(self.environment.get(node.name), Variable)
            else self.environment.get(node.name)
        )

    def visit_VariableDeclaration(self, node: VariableDeclaration):
        value = self.visit(node.value)
        var_type = node.var_type
        self.environment.define(node.name.name, value, var_type)

    def visit_ArrayLiteral(self, node: ArrayLiteral):
        values = []
        if node.elements:
            for element in node.elements:
                values.append(self.visit(element))
        return values

    def visit_MapLiteral(self, node: MapLiteral):
        values = {}
        if node.entries:
            for entry in node.entries:
                value = self.visit(entry)
                values.update(value)
        return values

    def visit_MapEntry(self, node: MapEntry) -> dict:
        return {self.visit(node.key): self.visit(node.value)}

    def visit_VariableAssignment(self, node: VariableAssignment):
        value = self.visit(node.value)
        self.environment.assign(node.name.name, value)

    def visit_ExpressionStatement(self, node: ExpressionStatement):
        return self.visit(node.expression)

    def visit_Literal(self, node: Literal):
        return node.value

    def visit_BinaryOperation(self, node: BinaryOperation):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if node.operator == "+":
            return left + right
        elif node.operator == "-":
            return left - right
        elif node.operator == "*":
            return left * right
        elif node.operator == "/":
            return left / right
        elif node.operator == "%":
            return left % right
        elif node.operator == "==":
            return left == right
        elif node.operator == "!=":
            return left != right
        elif node.operator == ">":
            return left > right
        elif node.operator == "<":
            return left < right
        elif node.operator == ">=":
            return left >= right
        elif node.operator == "<=":
            return left <= right
        elif node.operator == "&&":
            return left and right
        elif node.operator == "||":
            return left or right

    def visit_MultiplicativeExpression(self, node: MultiplicativeExpression):
        return self.visit_BinaryOperation(node)

    def visit_RelationalExpression(self, node: RelationalExpression):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if node.operator == ">":
            return left > right
        elif node.operator == "<":
            return left < right
        elif node.operator == ">=":
            return left >= right
        elif node.operator == "<=":
            return left <= right
        elif node.operator == "==":
            return left == right
        elif node.operator == "!=":
            return left != right

    def visit_IfStatement(self, node: IfStatement):
        if self.visit(node.condition):
            for statement in node.body:
                self.visit(statement)
        else:
            for elif_clause in node.elif_clauses:
                if self.visit(elif_clause.condition):
                    for statement in elif_clause.body:
                        self.visit(statement)
                    return
            if node.else_clause:
                for statement in node.else_clause.body:
                    self.visit(statement)

    def visit_ForStatement(self, node: ForStatement):
        collection = self.visit(node.collection)
        original_environment = self.environment
        for element in collection:
            self.environment = Environment(original_environment)
            self.environment.define(
                node.iterator_name.name, element, node.iterator_type
            )
            for statement in node.body:
                self.visit(statement)
        self.environment = original_environment

    def visit_FunctionDeclaration(self, node: FunctionDeclaration):
        func = Function(node.parameters, node.body, node.return_type)
        self.environment.define(node.name.name, func, node.return_type)

    def visit_FunctionCall(self, node: FunctionCall):
        if not node.base:
            func_name = node.function_name

        functions = self.environment.get(func_name.name)

        if isinstance(functions, list) and not all([isinstance(x, Function) for x in functions]):
            raise TypeError(f"{func_name} is not a function.")

        # Evaluate arguments once
        evaluated_args = [self.visit(arg) for arg in node.arguments]

        func_to_call = self._get_correct_function(functions, evaluated_args)
        
        if not func_to_call:
            raise TypeError(f"No matching function found for {func_name} with provided arguments.")

        # Save the current environment
        calling_environment = self.environment
        # Create a new environment for the function call, enclosing the calling environment
        self.environment = Environment(calling_environment)

        for param, arg_value in zip(func_to_call.params, evaluated_args):
            self.environment.define(param.name.name, arg_value, param.param_type)

        for statement in func_to_call.body:
            self.visit(statement)
            if self.return_value is not None:
                break

        result = self.return_value
        self.return_value = None  # Reset for next calls
        # Restore the original environment after the function call
        self.environment = calling_environment
        print(result)
        return result

    def visit_ReturnStatement(self, node: ReturnStatement):
        self.return_value = self.visit(node.value)

    def visit_AdditiveExpression(self, node: AdditiveExpression):
        return self.visit_BinaryOperation(node)

    def visit_EqualityExpression(self, node: EqualityExpression):
        return self.visit_BinaryOperation(node)

    def _get_correct_function(self, funcs: list[Function], evaluated_args: list):
        for func in funcs:
            if len(evaluated_args) == len(func.params):
                types_match = True
                for i, param in enumerate(func.params):
                    # Use the type checker to compare the evaluated argument with the parameter type
                    if not self.environment.type_checker.is_assignable(evaluated_args[i], param.param_type):
                        types_match = False
                        break
                if types_match:
                    return func
        return None
