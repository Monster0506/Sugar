from dataclasses import dataclass
from typing import Any

from lark import LarkError

from src.ast_nodes import (
    Expression,
    Identifier,
    Literal,
    Node,
    Program,
    Type,
    VariableAssignment,
    VariableDeclaration,
)
from src.type_checker import TypeChecker


@dataclass
class Variable:
    type: Type
    name: str


class Fail:
    pass


class UndefinedSymbolError(Exception):
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
        self.values: dict[str, Variable] = {}

    def get(self, key) -> Variable | Fail:
        if key in self.values:
            return self.values[key]
        elif self.enclosing and key in self.enclosing:
            return self.enclosing[key]
        return Fail()

    def __getitem__(self, key: str) -> Variable | Fail:
        if key in self.values:
            return self.values[key]
        elif self.enclosing and key in self.enclosing:
            return self.enclosing[key]
        return Fail()

    def __setitem__(self, index: str, value: Variable):
        self.values[index] = value

    def __contains__(self, item):
        return item in self.values


class StaticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()

    def analyze(self, node: Program):
        for statement in node.statements:
            method_name = f"visit_{statement.__class__.__name__}"
            visitor = getattr(self, method_name, self.generic_visit)
            visitor(statement)

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

        expected_type = value.type
        assignee_value = self._get_value(node.value)
        type_of_value = self._get_literal_type(assignee_value)
        if not self._is_assignable(type_of_value, expected_type):
            raise TypeError(
                f"{type_of_value.name} is not assignable to {expected_type.name}"
            )

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
