"""
Defines the Abstract Syntax Tree (AST) nodes for the Sugar language.

These classes are used by the transformer to build a structured representation
of the parsed code, which can then be used by an interpreter or compiler.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# Base class for all AST nodes
@dataclass
class Node:
    pass


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
    operator: str  # e.g., "||", "&&", "==", "!=", ">", "<", "+", "-", "*", "/", "%"
    right: Expression


@dataclass
class OrExpression(BinaryOperation):
    # operator will be "||"
    pass


@dataclass
class AndExpression(BinaryOperation):
    # operator will be "&&"
    pass


@dataclass
class EqualityExpression(BinaryOperation):
    # operator will be "==" or "!="
    pass


@dataclass
class RelationalExpression(BinaryOperation):
    # operator will be ">", "<", ">=", "<="
    pass


@dataclass
class AdditiveExpression(BinaryOperation):
    # operator will be "+" or "-"
    pass


@dataclass
class MultiplicativeExpression(BinaryOperation):
    # operator will be "*", "/", or "%"
    pass


# Unary Operations
# These classes represent expressions with a single operand and an operator.
@dataclass
class UnaryOperation(Expression):
    operator: str  # e.g., "!", "-", "+"
    expression: Expression | None


@dataclass
class NotExpression(UnaryOperation):
    # operator will be "!"
    pass


@dataclass
class UnaryMinusExpression(UnaryOperation):
    # operator will be "-"
    pass


@dataclass
class UnaryPlusExpression(UnaryOperation):
    # operator will be "+"
    pass


# Postfix Expressions
@dataclass
class MethodCall(Expression):
    # Represents `postfix_expression :method_name: (arguments?)` or `postfix_expression :method_name:`
    base: (
        Expression | None
    )  # The expression on which the method is called (e.g., an Identifier or PropertyAccess)
    function_name: Identifier
    arguments: list[Expression] | None = None


@dataclass
class PropertyAccess(Expression):
    # Represents `postfix_expression . IDENTIFIER`
    base: Expression  # The expression from which the property is accessed
    property_name: Identifier


@dataclass
class ArrayAccess(Expression):
    # Represents `postfix_expression [ expression ]`
    base: Expression  # The array/list expression being accessed
    index: Expression  # The expression used as an index


# Primary Expressions
@dataclass
class FunctionCall(MethodCall):
    # Represents `IDENTIFIER (argument_list?)`
    base = None
    function_name: Identifier
    arguments: list[Expression] | None = None


@dataclass
class ParenthesizedExpression(Expression):
    # Represents `( expression )`
    expression: Expression


@dataclass
class ArrayLiteral(Expression):
    # Represents `[ argument_list? ]`
    elements: list[Expression] | None = None


@dataclass
class MapEntry(Node):
    # Helper for map_literal: `expression ARROW_OP expression`
    key: Expression
    value: Expression


@dataclass
class MapLiteral(Expression):
    # Represents `{ map_entries+ }`
    entries: list[MapEntry]


@dataclass
class DictEntry(Node):
    # Helper for object_literal: `IDENTIFIER COLON expression`
    key: Identifier  # Property name in an object literal
    value: Expression


@dataclass
class ObjectLiteral(Expression):
    # Represents `{ dict_entries+ }` or `{}` (empty_object_literal)
    entries: list[DictEntry]


@dataclass
class TupleLiteral(Expression):
    # Represents `( expression COMMA expression (COMMA expression)* )`
    elements: list[Expression]  # Guarantees at least two elements from grammar


@dataclass
class LambdaExpression(Expression):
    # Represents `FUNC LPAR parameter_list? RPAR ARROW_OP expression`
    parameters: list[Parameter] | None
    body: Expression  # A single expression as the lambda's body


@dataclass
class AnonymousFunction(Expression):
    # Represents `FUNC LPAR parameter_list? RPAR function_body END`
    parameters: list[Parameter] | None
    body: list[Statement]  # A block of statements as the function's body
    type: Type | None = None  # Optional return type


@dataclass
class ThisExpression(Expression):
    # Represents the `THIS` keyword
    pass


@dataclass
class SuperCall(Expression):
    # Represents `SUPER (argument_list?)`
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
    dotted_name: list[str]  # list of identifiers in the dotted name


@dataclass
class TypeField(Node):
    name: Identifier
    field_type: Type


@dataclass
class TypeDeclaration(Statement):
    name: Identifier
    type_body: list["TypeField"]
    extends_clause: list[Identifier] | None


@dataclass
class AccessModifier(Node):
    modifier: str  # "PUBLIC", "PRIVATE", "PROTECTED"


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
    return_type: Type | None
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
    entries: list[MapEntryPattern]  # Similar to MapEntry, but with patterns


@dataclass
class TuplePattern(Pattern):
    patterns: list[Pattern]


@dataclass
class ObjectPattern(Pattern):
    entries: list[DictEntryPattern]  # Similar to DictEntry, but with patterns


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
    constructor: 'Function' | None


@dataclass
class SugarInstance(Node):
    sugar_class: SugarClass
    environment: 'Environment'
