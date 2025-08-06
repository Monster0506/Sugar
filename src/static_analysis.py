from dataclasses import dataclass
from typing import Any

from src.ast_nodes import (
    Expression,
    FunctionDeclaration,
    Identifier,
    Literal,
    Node,
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


class Fail:
    pass


class UndefinedSymbolError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidReturnError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class AlreadyDefinedSymbolError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class AnalyzerError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class SymbolTable:
    def __init__(self, enclosing=None) -> None:
        self.enclosing = enclosing
        self.values: dict[str, Variable | Function] = {}

    def get(self, key) -> Variable | Function | Fail:
        if key in self.values:
            return self.values[key]
        elif self.enclosing and key in self.enclosing:
            return self.enclosing[key]
        return Fail()

    def __getitem__(self, key: str) -> Variable | Function | Fail:
        if key in self.values:
            return self.values[key]
        elif self.enclosing and key in self.enclosing:
            return self.enclosing[key]
        return Fail()

    def __setitem__(self, index: str, value: Variable | Function):
        if isinstance(value, Variable):
            self.values[index] = value
        elif isinstance(value, Function):
            ...

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
        if isinstance(item, str):
            return Type(meta=None, name="str")
        if isinstance(item, float):
            return Type(meta=None, name="bool")
        tchecker = TypeChecker()
        return tchecker.get_runtime_type(item)

    def _is_assignable(self, item1: Type | Any, item2: Type | Any):
        if isinstance(item1, Type) and isinstance(item2, Type):
            return item1.name == item2.name
        tchecker = TypeChecker()
        return tchecker.is_assignable(item1, item2)

    def visit(self, node: Node):
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        visitor(node)

    def analyze(self, node: Program):
        for statement in node.statements:
            self.visit(statement)

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
            raise TypeError(
                f"{type_of_value.name} is not assignable to {expected_type.name}"
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
            raise TypeError(
                f"{type_of_value.name} is not assignable to {expected_type.name}"
            )

    def visit_FunctionDeclaration(self, node: FunctionDeclaration):
        original_table = self.symbol_table
        self.symbol_table = SymbolTable(self.symbol_table)
        identifier = node.name.name
        return_statement = None
        for statement in node.body:
            if isinstance(statement, ReturnStatement):
                return_statement = statement
                continue
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
            raise TypeError(
                f"{type_of_value.name} is not assignable to {return_type.name}"
            )
        information = Function(return_type=return_type, name=identifier)
        self.symbol_table[identifier] = information
