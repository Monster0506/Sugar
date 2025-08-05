from __future__ import annotations

from typing import TYPE_CHECKING

from src.ast_nodes import *
from src.builtin_functions import (
    all_operations,
    array_operations,
    base_errors,
    map_operations,
    standard_functions,
    str_operations,
    task_operations,
    token_operations,
)
from src.type_checker import TypeChecker

if TYPE_CHECKING:
    from src.error import ErrorReporter


class Symbol:
    """Represents a symbol in the table (variable, function, type, etc.)."""

    def __init__(
        self, name: str, type: Type, node: Node, is_function=False, is_type=False
    ):
        self.name = name
        self.type = type
        self.node = node
        self.is_function = is_function
        self.is_type = is_type


class SymbolTable:
    """Manages scopes and the symbols defined within them."""

    def __init__(self, enclosing: SymbolTable | None = None):
        self.symbols: dict[str, Symbol] = {}
        self.enclosing = enclosing

    def define(self, name: str, type: Type, node: Node, **kwargs):
        """Define a new symbol in the current scope."""
        if name in self.symbols:
            # This check is more robust as it can point to the original definition.
            original_symbol_node = self.symbols[name].node
            line = (
                original_symbol_node.meta.line if original_symbol_node.meta else "N/A"
            )
            raise NameError(
                f"Symbol '{name}' is already defined in this scope at line {line}."
            )
        self.symbols[name] = Symbol(name, type, node, **kwargs)

    def resolve(self, name: str) -> Symbol | None:
        """Resolve a symbol by searching from the current scope outwards."""
        if name in self.symbols:
            return self.symbols[name]
        if self.enclosing:
            return self.enclosing.resolve(name)
        return None

    def get(self, name: str):
        symbol = self.resolve(name)
        if symbol:
            return symbol.node  # Return the AST node associated with the symbol
        return None

    def prepopulate(self):
        # Pre-populate with built-in types
        for type_name in [
            "int",
            "float",
            "str",
            "bool",
            "char",
            "void",
            "any",
            "dynamic",
        ]:
            self.define(
                type_name,
                Type(name=type_name, meta=None),
                Type(name=type_name, meta=None),
                is_type=True,
            )

        # Pre-populate with built-in functions
        for name, func in standard_functions.items():
            # This is a simplification. We'd need to know the function signature.
            # For now, we'll assume they are functions that can take any arguments.
            # A more robust implementation would store function signature info.
            self.define(
                name,
                Type(name="function", meta=None),
                FunctionDeclaration(
                    name=Identifier(name=name, meta=None),
                    parameters=[],
                    return_type=Type(name="any", meta=None),
                    body=[],
                    meta=None,
                ),
                is_function=True,
            )

        for name, _ in array_operations.items():
            self.define(
                name,
                Type(name="function", meta=None),
                FunctionDeclaration(
                    name=Identifier(name=name, meta=None),
                    parameters=[],
                    return_type=Type(name="any", meta=None),
                    body=[],
                    meta=None,
                ),
                is_function=True,
            )
        for name, _ in str_operations.items():
            self.define(
                name,
                Type(name="function", meta=None),
                FunctionDeclaration(
                    name=Identifier(name=name, meta=None),
                    parameters=[],
                    return_type=Type(name="any", meta=None),
                    body=[],
                    meta=None,
                ),
                is_function=True,
            )
        for name, _ in map_operations.items():
            self.define(
                name,
                Type(name="function", meta=None),
                FunctionDeclaration(
                    name=Identifier(name=name, meta=None),
                    parameters=[],
                    return_type=Type(name="any", meta=None),
                    body=[],
                    meta=None,
                ),
                is_function=True,
            )
        for name, _ in task_operations.items():
            self.define(
                name,
                Type(name="function", meta=None),
                FunctionDeclaration(
                    name=Identifier(name=name, meta=None),
                    meta=None,
                    parameters=[],
                    return_type=Type(name="any", meta=None),
                    body=[],
                ),
                is_function=True,
            )
        for name, _ in token_operations.items():
            self.define(
                name,
                Type(name="function", meta=None),
                FunctionDeclaration(
                    name=Identifier(name=name, meta=None),
                    meta=None,
                    parameters=[],
                    return_type=Type(name="any", meta=None),
                    body=[],
                ),
                is_function=True,
            )
        for name, _ in all_operations.items():
            self.define(
                name,
                Type(name="function", meta=None),
                FunctionDeclaration(
                    name=Identifier(name=name, meta=None),
                    meta=None,
                    parameters=[],
                    return_type=Type(name="any", meta=None),
                    body=[],
                ),
                is_function=True,
            )
        for name, _ in base_errors.items():
            self.define(
                name,
                Type(name="Error", meta=None),
                CustomType(declaration=None, meta=None),
                is_type=True,
            )

    def __repr__(self):
        return f"SymbolTable(symbols={list(self.symbols.keys())}, enclosing={self.enclosing is not None})"


class StaticAnalyzer:
    """
    Walks the AST to perform static analysis, such as type checking,
    scope resolution, and other semantic validation before interpretation.
    """

    def __init__(self, ast: Program, error_reporter: ErrorReporter):
        self.ast = ast
        self.error_reporter = error_reporter
        self.scope = SymbolTable()
        self.scope.prepopulate()
        # The TypeChecker needs a way to resolve types, which the SymbolTable can do.
        # We adapt it to use our static scope instead of a runtime environment.
        self.type_checker = TypeChecker(self.scope)
        self.had_error = False
        self._current_function_return_type: Type | None = None

    def analyze(self) -> bool:
        """Performs the static analysis and returns True if errors were found."""
        self.visit(self.ast)
        return self.had_error

    def error(self, message: str, node: Node):
        """Reports a semantic error and sets the error flag."""
        self.error_reporter.report_semantic(message, node)
        self.had_error = True

    def visit(self, node: Node | list | None):
        if node is None:
            return
        if isinstance(node, list):
            for item in node:
                self.visit(item)
            return

        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: Node):
        """A generic visitor to traverse children of nodes we don't care about."""
        for field in node.__dict__.values():
            if isinstance(field, Node):
                self.visit(field)
            elif isinstance(field, list):
                for item in field:
                    if isinstance(item, Node):
                        self.visit(item)

    def enter_scope(self):
        self.scope = SymbolTable(enclosing=self.scope)

    def exit_scope(self):
        if self.scope.enclosing:
            self.scope = self.scope.enclosing

    def visit_Program(self, node: Program):
        self.visit(node.statements)

    def visit_VariableDeclaration(self, node: VariableDeclaration):
        value_type = self.visit(node.value)
        if value_type is None:
            # Error was already reported in the expression's visitor
            return

        declared_type = node.var_type

        if not self.type_checker.is_assignable(value_type, declared_type):
            print("here")
            self.error(
                f"Cannot assign value of type '{value_type.name}' to variable of type '{declared_type.name}'.",
                node.value,
            )

        try:
            self.scope.define(node.name.name, declared_type, node)
        except NameError as e:
            self.error(str(e), node)

    def visit_VariableAssignment(self, node: VariableAssignment):
        var_symbol = self.scope.resolve(node.name.name)
        if not var_symbol:
            self.error(f"Cannot assign to undefined variable '{node.name.name}'.", node)
            return

        value_type = self.visit(node.value)
        if value_type is None:
            return

        if not self.type_checker.is_assignable(value_type, var_symbol.type):
            print("here2")
            self.error(
                f"Cannot assign value of type '{value_type.name}' to variable '{var_symbol.name}' of type '{var_symbol.type.name}'.",
                node.value,
            )

    def visit_FunctionDeclaration(self, node: FunctionDeclaration):
        try:
            self.scope.define(node.name.name, node.return_type, node, is_function=True)
        except NameError as e:
            self.error(str(e), node)

        self.enter_scope()

        # Set current function context for return statement checking
        previous_function_return_type = self._current_function_return_type
        self._current_function_return_type = node.return_type

        for param in node.parameters:
            try:
                self.scope.define(param.name.name, param.param_type, param)
            except NameError as e:
                self.error(str(e), param)

        self.visit(node.body)

        # Restore previous function context
        self._current_function_return_type = previous_function_return_type

        self.exit_scope()

    def visit_ReturnStatement(self, node: ReturnStatement):
        if self._current_function_return_type is None:
            self.error("Return statement found outside of a function.", node)
            return

        if node.value:
            returned_type = self.visit(node.value)
            if returned_type and not self.type_checker.is_assignable(
                returned_type, self._current_function_return_type
            ):
                self.error(
                    f"Cannot return value of type '{returned_type.name}' from a function with declared return type '{self._current_function_return_type.name}'.",
                    node.value,
                )
        elif self._current_function_return_type.name != "void":
            self.error(
                f"Function with return type '{self._current_function_return_type.name}' must return a value.",
                node,
            )

    def visit_FunctionCall(self, node: FunctionCall):
        func_symbol = self.scope.resolve(node.function_name.name)
        if not func_symbol:
            self.error(f"Call to undefined function '{node.function_name.name}'.", node)
            return Type(name="any", meta=node.meta)

        if not func_symbol.is_function:
            self.error(
                f"'{node.function_name.name}' is not a function and cannot be called.",
                node,
            )
            return Type(name="any", meta=node.meta)

        # This assumes the symbol's node is a FunctionDeclaration
        func_decl_node = func_symbol.node

        expected_params = func_decl_node.parameters
        provided_args = node.arguments or []

        if len(expected_params) != len(provided_args):
            self.error(
                f"Function '{node.function_name.name}' expects {len(expected_params)} arguments, but got {len(provided_args)}.",
                node,
            )
            return func_symbol.type  # Return expected type to reduce cascading errors

        for i, arg_node in enumerate(provided_args):
            arg_type = self.visit(arg_node)
            param_type = expected_params[i].param_type
            if arg_type and not self.type_checker.is_assignable(arg_type, param_type):
                self.error(
                    f"Argument {i+1} to function '{node.function_name.name}' has incorrect type. Expected '{param_type.name}', but got '{arg_type.name}'.",
                    arg_node,
                )

        return func_symbol.type

    def visit_IfStatement(self, node: IfStatement):
        condition_type = self.visit(node.condition)
        if condition_type and condition_type.name != "bool":
            self.error(
                "If statement condition must be a boolean expression.", node.condition
            )

        self.enter_scope()
        self.visit(node.body)
        self.exit_scope()

        for elif_clause in node.elif_clauses:
            self.visit(elif_clause)

        if node.else_clause:
            self.visit(node.else_clause)

    def visit_ElifClause(self, node: ElifClause):
        condition_type = self.visit(node.condition)
        if condition_type and condition_type.name != "bool":
            self.error("Elif condition must be a boolean expression.", node.condition)

        self.enter_scope()
        self.visit(node.body)
        self.exit_scope()

    def visit_ElseClause(self, node: ElseClause):
        self.enter_scope()
        self.visit(node.body)
        self.exit_scope()

    def visit_WhileStatement(self, node: WhileStatement):
        condition_type = self.visit(node.condition)
        if condition_type and condition_type.name != "bool":
            self.error(
                "While loop condition must be a boolean expression.", node.condition
            )

        self.enter_scope()
        self.visit(node.body)
        self.exit_scope()

    def visit_ForStatement(self, node: ForStatement):
        collection_type = self.visit(node.collection)

        # Basic check for iterability (is it an array?)
        # A more robust system would have an 'Iterable' interface.
        if collection_type and not isinstance(collection_type, ArrayType):
            self.error("For loop can only iterate over arrays.", node.collection)

        self.enter_scope()
        # Define the loop variable in the new scope
        try:
            # Infer the type of the iterator from the collection type
            iterator_type = (
                collection_type.base_type
                if isinstance(collection_type, ArrayType)
                else Type(name="any", meta=node.iterator_name.meta)
            )
            self.scope.define(
                node.iterator_name.name, iterator_type, node.iterator_name
            )
        except NameError as e:
            self.error(str(e), node.iterator_name)

        self.visit(node.body)
        self.exit_scope()

    def visit_BinaryOperation(self, node: BinaryOperation) -> Type | None:
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if not left_type or not right_type:
            return None

        # This is still a simplification, but better.
        # A real system would use the type checker to see if the operation
        # is defined for the given types.
        numeric = ["int", "float"]
        if node.operator in ["+", "-", "*", "/"]:
            if left_type.name not in numeric or right_type.name not in numeric:
                self.error(
                    f"Operator '{node.operator}' cannot be used on non-numeric types '{left_type.name}' and '{right_type.name}'.",
                    node,
                )
                return None
            # Type promotion: int + float -> float
            if left_type.name == "float" or right_type.name == "float":
                return Type(name="float", meta=node.meta)
            return Type(name="int", meta=node.meta)

        if node.operator in ["<", ">", "<=", ">="]:
            if left_type.name not in numeric or right_type.name not in numeric:
                self.error(
                    f"Operator '{node.operator}' cannot be used on non-numeric types '{left_type.name}' and '{right_type.name}'.",
                    node,
                )
                return None
            return Type(name="bool", meta=node.meta)

        if node.operator in ["==", "!="]:
            # Allow comparison between any two types, for now.
            return Type(name="bool", meta=node.meta)

        if node.operator in ["&&", "||"]:
            if left_type.name != "bool" or right_type.name != "bool":
                self.error(
                    f"Logical operator '{node.operator}' can only be used on booleans.",
                    node,
                )
                return None
            return Type(name="bool", meta=node.meta)

        self.error(f"Unsupported binary operator '{node.operator}'.", node)
        return None

    def visit_Identifier(self, node: Identifier) -> Type | None:
        symbol = self.scope.resolve(node.name)
        if not symbol:
            self.error(f"Use of undefined variable '{node.name}'.", node)
            return None
        return symbol.type

    def visit_Literal(self, node: Literal) -> Type:
        if isinstance(node.value, bool):
            return Type(name="bool", meta=node.meta)
        elif isinstance(node.value, int):
            return Type(name="int", meta=node.meta)
        elif isinstance(node.value, float):
            return Type(name="float", meta=node.meta)
        elif isinstance(node.value, str):
            if len(node.value) == 1:
                return Type(name="char", meta=node.meta)
            return Type(name="str", meta=node.meta)
        # Add other literal types as needed
        return Type(name="any", meta=node.meta)  # Fallback

    def visit_ExpressionStatement(self, node: ExpressionStatement):
        self.visit(node.expression)

    def visit_ArrayLiteral(self, node: ArrayLiteral) -> ArrayType:
        if not node.elements:
            # Cannot infer type of empty array, treat as 'any'
            return ArrayType(
                name="[]", base_type=Type(name="any", meta=node.meta), meta=node.meta
            )

        element_types = [self.visit(elem) for elem in node.elements]

        # For simplicity, ensure all elements are of the same type.
        # A more advanced system might find a common supertype.
        first_type = element_types[0]
        for i, elem_type in enumerate(element_types[1:]):
            if not self.type_checker.is_assignable(elem_type, first_type):
                self.error(
                    f"Array elements must have a consistent type. Found '{elem_type.name}' where '{first_type.name}' was expected.",
                    node.elements[i + 1],
                )

        return ArrayType(
            name=f"[{first_type.name}]", base_type=first_type, meta=node.meta
        )
