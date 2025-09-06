from dataclasses import dataclass
from typing import Any

from src.ast_nodes import (
    ArrayLiteral,
    ArrayType,
    Expression,
    ExpressionStatement,
    FunctionDeclaration,
    Identifier,
    Literal,
    MapLiteral,
    Node,
    Parameter,
    Program,
    ReturnStatement,
    TupleLiteral,
    TupleType,
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
        if isinstance(item, ArrayLiteral):
            theoretical_elements = []
            for thingy in item.elements if item.elements else []:
                theoretical_elements.append(self._get_value(thingy))
            return theoretical_elements
        if isinstance(item, TupleLiteral):
            theoretical_elements = []
            for thingy in item.elements if item.elements else []:
                theoretical_elements.append(self._get_value(thingy))
            return tuple(theoretical_elements)

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
        if isinstance(item, list):
            if not item:
                # For an empty list, we can say its base type is 'any',
                # making it assignable to any array type.
                return ArrayType(
                    meta=None, name="array", base_type=Type(meta=None, name="any")
                )

            # Determine the common type of the elements
            base_type = self._get_literal_type(item[0])
            for element in item[1:]:
                element_type = self._get_literal_type(element)
                if not self._is_assignable(element_type, base_type):
                    base_type = Type(meta=None, name="any")
                    break
            return ArrayType(meta=None, name="array", base_type=base_type)
        if isinstance(item, tuple):
            types = [self._get_literal_type(e) for e in item]
            return TupleType(meta=None, name="tuple", types=types)

        tchecker = TypeChecker()
        return tchecker.get_runtime_type(item)

    def _is_assignable(self, item1: Type | Any, item2: Type | Any):
        if hasattr(item2, "name") and item2.name == "any":
            return True
        if isinstance(item2, ArrayType):
            # If we are assigning an empty list to an array type, it's always valid.
            if item1 == []:
                return True

            if not isinstance(item1, (ArrayType, list)):
                return False

            if isinstance(item1, list):
                item1 = self._get_literal_type(item1)

            if not isinstance(item1, ArrayType):
                return False

            # If the target base_type is any, we can assign anything
            if item2.base_type and item2.base_type.name == "any":
                return True

            # if the source base_type is any, it can be assigned to any target type
            if item1.base_type and item1.base_type.name == "any":
                return True

            # Check if the base types are assignable
            if not item1.base_type or not self._is_assignable(
                item1.base_type, item2.base_type
            ):
                return False
            return True

        if isinstance(item2, TupleType):
            if not isinstance(item1, (TupleType, tuple)):
                return False

            if isinstance(item1, tuple):
                item1 = self._get_literal_type(item1)

            if not isinstance(item1, TupleType):
                return False

            if len(item1.types) != len(item2.types):
                return False

            for t1, t2 in zip(item1.types, item2.types):
                if not self._is_assignable(t1, t2):
                    return False
            return True

        if isinstance(item1, Type) and isinstance(item2, Type):
            if item1.name == "null":
                return True
            if item1.name == "char" and item2.name == "str":
                return True
            if item2.name == "char" and item1.name == "str":
                return True
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
            if isinstance(expected_type, ArrayType) and isinstance(value, list):
                for element in value:
                    element_type = self._get_literal_type(element)
                    if not self._is_assignable(element_type, expected_type.base_type):
                        raise TypeCheckingError(
                            f"Cannot assign an array containing an element of type '{element_type.name}' to an array of type '{expected_type.base_type.name if expected_type.base_type else expected_type.name}'",
                            node.meta,
                        )
                return
            if isinstance(expected_type, TupleType) and isinstance(value, tuple):
                if len(value) != len(expected_type.types):
                    raise TypeCheckingError(
                        f"Cannot assign a tuple of length {len(value)} to a tuple of length {len(expected_type.types)}",
                        node.meta,
                    )
                for i, (element, expected_element_type) in enumerate(
                    zip(value, expected_type.types)
                ):
                    element_type = self._get_literal_type(element)
                    if not self._is_assignable(element_type, expected_element_type):
                        raise TypeCheckingError(
                            f"Cannot assign a tuple with an element of type '{element_type.name}' at index {i} to a tuple with an element of type '{expected_element_type.name}' at that index",
                            node.meta,
                        )
                return

            raise TypeCheckingError(
                f"'{type_of_value.name}' is not assignable to '{expected_type.name}'",
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

    def visit_Literal(self, node: Literal):
        # Literals don't need further visiting
        pass

    def visit_ArrayLiteral(self, node: ArrayLiteral):

        # Visit all elements
        if node.elements:
            for element in node.elements:
                self.visit(element)

    def visit_MapLiteral(self, node: MapLiteral):
        # Visit all entries
        for entry in node.entries:
            self.visit(entry)

    def visit_TupleLiteral(self, node: TupleLiteral):
        # Visit all elements
        for element in node.elements:
            self.visit(element)
