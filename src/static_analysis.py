from dataclasses import dataclass
from typing import Any

from src.ast_nodes import (
    Expression,
    ExpressionStatement,
    FunctionDeclaration,
    Identifier,
    Literal,
    Node,
    Parameter,
    Program,
    ReturnStatement,
    Type,
    VariableAssignment,
    VariableDeclaration,
)
from src.type_checker import TypeChecker


@dataclass
class Variable:
    type: Type
    name: str


@dataclass
class Function:
    return_type: Type
    name: str
    parameters: list[Parameter]


class Fail:
    pass


class StaticError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class UndefinedSymbolError(StaticError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidReturnError(StaticError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class DuplicateFunctionOverloadError(StaticError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class AlreadyDefinedSymbolError(StaticError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class AnalyzerError(StaticError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TypeCheckingError(StaticError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class SymbolTable:
    def __init__(self, enclosing=None) -> None:
        self.enclosing = enclosing
        self.values: dict[str, Variable | list[Function]] = {}

    def get(self, key) -> Variable | list[Function] | Fail:
        if key in self.values:
            return self.values[key]
        elif self.enclosing and key in self.enclosing:
            return self.enclosing[key]
        return Fail()

    def __getitem__(self, key: str) -> Variable | list[Function] | Fail:
        if key in self.values:
            return self.values[key]
        elif self.enclosing and key in self.enclosing:
            return self.enclosing[key]
        return Fail()

    def __setitem__(self, index: str, value: Variable | Function):
        if isinstance(value, Variable):
            if index in self.values and isinstance(self.values[index], list):
                raise AlreadyDefinedSymbolError(
                    f"Cannot redefine function '{index}' as a variable"
                )
            self.values[index] = value
        elif isinstance(value, Function):
            if index in self.values and isinstance(self.values[index], Variable):
                raise AlreadyDefinedSymbolError(
                    f"Cannot redefine variable '{index}' as a function"
                )
            if index not in self.values or not isinstance(self.values[index], list):
                self.values[index] = []
            funcs = self.values[index]
            assert isinstance(funcs, list)  # type narrowing for mypy/pyright
            funcs.append(value)

    def __contains__(self, item):
        return item in self.values

    def __repr__(self) -> str:
        return f"{self.values=}, {self.enclosing=}"


class StaticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()

    def _get_value(self, item: Literal | Identifier | Expression):
        if isinstance(item, Literal):
            return item.value
        elif isinstance(item, Identifier):
            result = self.symbol_table.get(item.name)
            if result is Fail():
                raise UndefinedSymbolError(
                    f"Could not find identifier {item.name}", item.meta
                )

    def _get_literal_type(self, item: Any):
        if isinstance(item, bool):
            return Type(meta=None, name="bool")
        if isinstance(item, int):
            return Type(meta=None, name="int")
        if isinstance(item, float):
            return Type(meta=None, name="float")
        if isinstance(item, str):
            return Type(meta=None, name="str")
        if item is None:
            return Type(meta=None, name="null")
        tchecker = TypeChecker()
        return tchecker.get_runtime_type(item)

    def _is_assignable(self, item1: Type | Any, item2: Type | Any):
        if isinstance(item1, Type) and isinstance(item2, Type):
            # Null values can be assigned to any type (represents optional/not yet full)
            if item1.name == "null":
                return True
            # But non-null values cannot be assigned to null type
            if item2.name == "null":
                return item1.name == "null"
            if item1.name == "char" and item2.name == "str":
                return True
            if item2.name == "char" and item1.name == "str":
                return True
            return item1.name == item2.name
        
        # For now, use the type checker for complex type comparisons
        # This will handle arrays, maps, tuples, etc.
        tchecker = TypeChecker()
        return tchecker.is_assignable(item1, item2)

    def visit(self, node: Node):
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        visitor(node)

    def analyze(self, node: Program):
        for statement in node.statements:
            self.visit(statement)

    def visit_ExpressionStatement(self, node: ExpressionStatement):
        pass

    def generic_visit(self, node: Node):
        raise NotImplementedError(f"Generic visit to node {node}")

    def visit_VariableDeclaration(self, node: VariableDeclaration):
        identifier = node.name.name
        if identifier in self.symbol_table:
            raise AlreadyDefinedSymbolError(
                f"{identifier} has already been defined", node.meta
            )
        else:
            value = self._get_value(node.value)
            type_of_value = self._get_literal_type(value)
        expected_type = node.var_type

        if not self._is_assignable(type_of_value, expected_type):
            raise TypeCheckingError(
                f"{type_of_value.name} is not assignable to {expected_type.name}",
                node.meta,
            )
        information = Variable(name=identifier, type=type_of_value)
        self.symbol_table[identifier] = information

    def visit_VariableAssignment(self, node: VariableAssignment):
        identifier = node.name.name
        if identifier not in self.symbol_table:
            raise UndefinedSymbolError(
                f"Could not find identifier {identifier}", node.meta
            )
        value = self.symbol_table[identifier]
        if isinstance(value, Fail):
            raise AnalyzerError(f"Failed to find type for {identifier}", node.meta)

        if not isinstance(value, Variable):
            raise AnalyzerError("How did we get here?", node.meta)

        expected_type = value.type
        assignee_value = self._get_value(node.value)
        type_of_value = self._get_literal_type(assignee_value)
        if not self._is_assignable(type_of_value, expected_type):
            raise TypeCheckingError(
                f"{type_of_value.name} is not assignable to {expected_type.name}",
                node.meta,
            )

    def visit_FunctionDeclaration(self, node: FunctionDeclaration):
        original_table = self.symbol_table
        self.symbol_table = SymbolTable(self.symbol_table)
        identifier = node.name.name
        if identifier in self.symbol_table:
            raise AlreadyDefinedSymbolError(
                f"{identifier} has already been defined", node.meta
            )
        return_statement = None
        for statement in node.body:
            if isinstance(statement, ReturnStatement):
                return_statement = statement
            else:
                # Visit the statement and check if it contains return statements
                self.visit(statement)

        if node.return_type is None:
            return_type = Type(meta=None, name="void")
        else:
            return_type = node.return_type
        if return_type.name == "void" and return_statement:
            raise InvalidReturnError(
                f"Void function {identifier} cannot return a value, but has a return statement",
                node.meta,
            )

        if return_type.name != "void" and (
            not return_statement or not return_statement.value
        ):
            raise InvalidReturnError(
                f"Non-void function '{identifier}' must return a value.",
                node.meta,
            )

        if return_statement is None or (
            return_type.name == "void" and not return_statement.value
        ):
            self.symbol_table = original_table
            return

        if not return_statement.value or not isinstance(
            return_statement.value, Expression
        ):
            raise AnalyzerError(f"Invalid return statement for {identifier}", node.meta)

        value = self._get_value(return_statement.value)
        type_of_value = self._get_literal_type(value)

        self.symbol_table = original_table
        if not self._is_assignable(type_of_value, return_type):
            raise TypeCheckingError(
                f"{type_of_value.name} is not assignable to {return_type.name}",
                node.meta,
            )

        # Parse parameters
        user_params = []
        for param in node.parameters if node.parameters else []:
            user_params.append(
                Parameter(
                    meta=node.meta,
                    name=param.name,
                    param_type=param.param_type,
                )
            )

        information = Function(
            return_type=return_type,
            name=identifier,
            parameters=user_params,
        )

        # Check for duplicate function overloads
        existing_functions = self.symbol_table.get(identifier)
        if isinstance(existing_functions, list):
            for function in existing_functions:
                if function.name == identifier:
                    match = True
                    if len(user_params) == len(function.parameters):
                        for a, b in zip(user_params, function.parameters):
                            if a.param_type.name != b.param_type.name:
                                match = False
                        if match:
                            raise DuplicateFunctionOverloadError(
                                f"Function overload attempted for {identifier} with duplicate signature",
                                node.meta,
                            )

        self.symbol_table[identifier] = information

    def visit_IfStatement(self, node):
        # Visit the condition
        self.visit(node.condition)
        # Visit the body statements
        for statement in node.body:
            self.visit(statement)
        # Visit elif clauses
        for elif_clause in node.elif_clauses:
            self.visit(elif_clause)
        # Visit else clause
        if node.else_clause:
            self.visit(node.else_clause)

    def visit_ElifClause(self, node):
        # Visit the condition
        self.visit(node.condition)
        # Visit the body statements
        for statement in node.body:
            self.visit(statement)

    def visit_ElseClause(self, node):
        # Visit the body statements
        for statement in node.body:
            self.visit(statement)

    def visit_ReturnStatement(self, node):
        # Visit the return value if it exists
        if node.value:
            self.visit(node.value)

    def visit_EqualityExpression(self, node):
        # Visit left and right operands
        self.visit(node.left)
        self.visit(node.right)

    def visit_AdditiveExpression(self, node):
        # Visit left and right operands
        self.visit(node.left)
        self.visit(node.right)

    def visit_Identifier(self, node):
        # Identifiers don't need special handling for static analysis
        pass

    def visit_Literal(self, node):
        # Literals don't need special handling for static analysis
        pass

    def visit_ArrayLiteral(self, node):
        # Visit all elements in the array
        if node.elements:
            for element in node.elements:
                self.visit(element)

    def visit_MapLiteral(self, node):
        # Visit all entries in the map
        if node.entries:
            for entry in node.entries:
                self.visit(entry)

    def visit_TupleLiteral(self, node):
        # Visit all elements in the tuple
        if node.elements:
            for element in node.elements:
                self.visit(element)
