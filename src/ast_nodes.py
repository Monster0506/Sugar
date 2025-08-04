"""
Defines the Abstract Syntax Tree (AST) nodes for the Sugar language.

These classes are used by the transformer to build a structured representation
of the parsed code, which can then be used by an interpreter or compiler.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from src.interpreter import Environment  # Only imports for type checking


# Base class for all AST nodes
@dataclass
class Node:
    pass


@dataclass
class Variable:
    value: Any
    var_type: Type


@dataclass
class Function:
    params: list
    body: list
    return_type: Type
    is_static: bool = False
    is_override: bool = False


# Expressions
@dataclass
class Expression(Node):
    pass


@dataclass
class Literal(Expression):
    value: Any


@dataclass
class Identifier(Expression):
    name: str


# Types
@dataclass
class Type(Node):
    name: str


@dataclass
class Parameter(Node):
    name: Identifier
    param_type: Type


# Statements
@dataclass
class Statement(Node):
    pass


@dataclass
class VariableDeclaration(Statement):
    name: Identifier
    var_type: Type
    value: Expression


@dataclass
class VariableAssignment(Statement):
    name: Identifier
    value: Expression


@dataclass
class ThisAssignment(Statement):
    property_name: Identifier
    value: Expression


@dataclass
class FunctionDeclaration(Statement):
    name: Identifier
    parameters: list[Parameter]
    return_type: Type
    body: list[Statement]


@dataclass
class ReturnStatement(Statement):
    value: Expression | None


@dataclass
class ElifClause(Node):
    condition: Expression
    body: list[Statement]


@dataclass
class ElseClause(Node):
    body: list[Statement]


@dataclass
class IfStatement(Statement):
    condition: Expression
    body: list[Statement]
    elif_clauses: list[ElifClause]
    else_clause: ElseClause | None


@dataclass
class Program(Node):
    statements: list[Statement]


@dataclass
class BinaryOperation(Expression):
    left: Expression
    operator: str
    right: Expression


@dataclass
class OrExpression(BinaryOperation):
    pass


@dataclass
class AndExpression(BinaryOperation):
    pass


@dataclass
class EqualityExpression(BinaryOperation):
    pass


@dataclass
class RelationalExpression(BinaryOperation):
    pass


@dataclass
class AdditiveExpression(BinaryOperation):
    pass


@dataclass
class MultiplicativeExpression(BinaryOperation):
    pass


@dataclass
class UnaryOperation(Expression):
    operator: str
    expression: Expression | None


@dataclass
class NotExpression(UnaryOperation):
    pass


@dataclass
class UnaryMinusExpression(UnaryOperation):
    pass


@dataclass
class UnaryPlusExpression(UnaryOperation):
    pass


@dataclass
class MethodCall(Expression):
    base: Expression | None
    function_name: Identifier
    arguments: list[Expression] | None = None


@dataclass
class PropertyAccess(Expression):
    base: Expression
    property_name: Identifier


@dataclass
class ArrayAccess(Expression):
    base: Expression
    index: Expression


@dataclass
class FunctionCall(MethodCall):
    base = None
    function_name: Identifier
    arguments: list[Expression] | None = None


@dataclass
class ParenthesizedExpression(Expression):
    expression: Expression


@dataclass
class ArrayLiteral(Expression):
    elements: list[Expression] | None = None


@dataclass
class MapEntry(Node):
    key: Expression
    value: Expression


@dataclass
class MapLiteral(Expression):
    entries: list[MapEntry]


@dataclass
class DictEntry(Node):
    key: Identifier
    value: Expression


@dataclass
class ObjectLiteral(Expression):
    entries: list[DictEntry]


@dataclass
class TupleLiteral(Expression):
    elements: list[Expression]


@dataclass
class LambdaExpression(Expression):
    parameters: list[Parameter] | None
    body: Expression


@dataclass
class AnonymousFunction(Expression):
    parameters: list[Parameter] | None
    body: list[Statement]
    type: Type | None = None


@dataclass
class ThisExpression(Expression):
    pass


@dataclass
class SuperCall(Expression):
    arguments: list[Expression] | None = None


@dataclass
class ForStatement(Statement):
    iterator_name: Identifier
    iterator_type: Type
    collection: Expression
    body: list[Statement]


@dataclass
class WhileStatement(Statement):
    condition: Expression
    body: list[Statement]


@dataclass
class CatchClause(Node):
    exception_name: Identifier
    exception_type: Type
    body: list[Statement]


@dataclass
class FinallyClause(Node):
    body: list[Statement]


@dataclass
class TryStatement(Statement):
    body: list[Statement]
    catch_clauses: list[CatchClause]
    finally_clause: FinallyClause | None


@dataclass
class ThrowStatement(Statement):
    exception: Expression


@dataclass
class ExpressionStatement(Statement):
    expression: Expression


@dataclass
class SpawnStatement(Statement):
    expression: Expression


@dataclass
class ImportStatement(Statement):
    dotted_name: list[str]


@dataclass
class TypeField(Node):
    name: Identifier
    field_type: Type


@dataclass
class TypeDeclaration(Statement):
    name: Identifier
    type_body: list[TypeField]
    extends_clause: list[Identifier] | None


@dataclass
class AccessModifier(Node):
    modifier: str


@dataclass
class ClassMember(Node):
    access_modifier: AccessModifier | None
    is_static: bool
    is_override: bool


@dataclass
class PropertyDeclaration(ClassMember):
    name: Identifier
    property_type: Type
    value: Expression | None


@dataclass
class MethodDeclaration(ClassMember):
    name: Identifier
    parameters: list[Parameter]
    return_type: Type
    body: list[Statement]


@dataclass
class ConstructorDeclaration(ClassMember):
    parameters: list[Parameter]
    body: list[Statement]


@dataclass
class ClassDeclaration(Statement):
    name: Identifier
    extends_clause: list[Identifier] | None
    implements_clause: list[Identifier] | None
    body: list[ClassMember]


@dataclass
class ErrorDeclaration(Statement):
    name: Identifier
    extends_clause: list[Identifier] | None


@dataclass
class InterfaceMethodDeclaration(Node):
    name: Identifier
    parameters: list[Parameter]
    return_type: Type | None


@dataclass
class InterfaceDeclaration(Statement):
    name: Identifier
    body: list[InterfaceMethodDeclaration]


@dataclass
class ArrayType(Type):
    name: str
    base_type: Type | None


@dataclass
class MapType(Type):
    name: str
    key_type: Type
    value_type: Type


@dataclass
class TupleType(Type):
    name: str
    types: list[Type]


@dataclass
class QualifiedIdentifier(Expression):
    parts: list[Identifier]


# Patterns for match statements (example)
@dataclass
class Pattern(Node):
    pass


@dataclass
class CaseClause(Node):
    pattern: Pattern
    guard: Expression | None
    body: list[Statement]


@dataclass
class DefaultClause(Node):
    body: list[Statement]


@dataclass
class MatchStatement(Statement):
    expression: Expression
    case_clauses: list[CaseClause]
    default_clause: DefaultClause | None


@dataclass
class LiteralPattern(Pattern):
    literal: Literal


@dataclass
class IdentifierPattern(Pattern):
    name: Identifier


@dataclass
class TypedIdentifierPattern(Pattern):
    var_type: Type
    name: Identifier


@dataclass
class ArrayPattern(Pattern):
    patterns: list[Pattern] | None


@dataclass
class DictEntryPattern(Node):
    key: Identifier
    value: Pattern


@dataclass
class MapEntryPattern(Node):
    key: Pattern
    value: Pattern


@dataclass
class MapPattern(Pattern):
    entries: list[MapEntryPattern]


@dataclass
class TuplePattern(Pattern):
    patterns: list[Pattern]


@dataclass
class ObjectPattern(Pattern):
    entries: list[DictEntryPattern]


@dataclass
class End(Node):
    pass


@dataclass
class CustomType(Node):
    declaration: TypeDeclaration


@dataclass
class SugarClass(Node):
    name: str
    methods: dict
    properties: dict[str, PropertyDeclaration]
    constructor: Function | None
    superclass: "SugarClass | None" = None

    def find_property(self, name: str) -> PropertyDeclaration | None:
        if name in self.properties:
            return self.properties[name]
        if self.superclass:
            return self.superclass.find_property(name)
        return None


@dataclass
class SugarInstance(Node):
    sugar_class: SugarClass
    environment: "Environment"


@dataclass(frozen=True)
class StdLibCall:
    func: Callable[..., Any]

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)


class SugarError(Exception):
    def __init__(self, base_class, args=None):
        if args is None:
            args = []
        self.base_class = base_class
        self.args = args
        super().__init__(*args)

    @property
    def base_class_name(self):
        return self.base_class.__name__

    def trigger(self):
        raise self.base_class(*self.args)


class SugarTask:
    def __init__(self, func_node, environment, run_path):
        self.func_node = func_node
        self.environment = environment
        self.run_path = run_path
        self._result = None
        self._error = None
        self._done = False
        self._success = False
        self._thread = None
        self._cancellation_requested = threading.Event()  # For cooperative cancellation
        self._state_lock = threading.Lock()

    def _target_run(self):
        from src.interpreter import Interpreter

        """Internal method executed by the thread."""
        try:
            interpreter = Interpreter(self.run_path)
            interpreter.environment = self.environment
            func = interpreter.visit(self.func_node)
            self._result = func()
            self._success = True
        except Exception as e:
            self._error = e
            self._success = False
        finally:
            with self._state_lock:
                self._done = True

    def start(self):
        if self._thread is not None:
            raise RuntimeError("Task already started.")
        self._thread = threading.Thread(target=self._target_run)
        self._thread.start()

    def join(self):
        """Waits for the task to complete and returns its result."""
        if self._thread:
            self._thread.join()

        with self._state_lock:
            if not self._done:
                raise RuntimeError("Task not finished when join() completed.")
            if not self._success:
                raise self._error
            return self._result

    def is_done(self):
        """Checks if the task has completed its execution."""
        with self._state_lock:
            return self._done

    def is_success(self):
        """Checks if the task completed successfully (without an error).
        Only meaningful if is_done() is True."""
        with self._state_lock:
            return self._done and self._success

    def get_error(self):
        """Retrieves the exception object if the task failed.
        Only meaningful if is_done() is True and is_success() is False."""
        with self._state_lock:
            return self._error

    def cancel(self):
        """Requests the task to cancel its execution.
        The task's function must be designed to check for this."""
        self._cancellation_requested.set()

    def timeout_join(self, timeout_ms):
        """Waits for the task to complete for a specified duration.
        Returns True if the task completed, False otherwise."""
        if self._thread:
            # threading.Thread.join() takes timeout in seconds
            self._thread.join(timeout_ms / 1000.0)
            with self._state_lock:
                return self._done  # Check if it completed within the timeout
        return True  # If task was never started, consider it 'done' instantly.


class CancellationToken:
    def __init__(self):
        self._cancelled = threading.Event()

    # This method will be exposed as 'token:CANCEL:()' in Sugar
    def cancel(self):
        self._cancelled.set()
        # print("DEBUG: CancellationToken set to cancelled.") # For debugging

    # This method will be exposed as 'token:IS_CANCELLED:()' in Sugar
    def is_cancelled(self):
        # print(f"DEBUG: CancellationToken is_cancelled called, state: {self._cancelled.is_set()}") # For debugging
        return self._cancelled.is_set()
