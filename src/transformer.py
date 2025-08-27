"""
Transforms the Lark parse tree into a structured AST.
"""

import logging

from lark import Token, Transformer, Tree, tree, v_args

from src.ast_nodes import (
    AccessModifier,
    AdditiveExpression,
    AndExpression,
    AnonymousFunction,
    ArrayAccess,
    ArrayLiteral,
    ArrayPattern,
    ArrayType,
    CaseClause,
    CatchClause,
    ClassDeclaration,
    ClassMember,
    ConstructorDeclaration,
    DefaultClause,
    DictEntry,
    DictEntryPattern,
    ElifClause,
    ElseClause,
    End,
    EqualityExpression,
    Expression,
    ExpressionStatement,
    FinallyClause,
    ForStatement,
    FunctionCall,
    FunctionDeclaration,
    Identifier,
    IdentifierPattern,
    IfStatement,
    ImportStatement,
    InterfaceDeclaration,
    InterfaceMethodDeclaration,
    LambdaExpression,
    Literal,
    LiteralPattern,
    MapEntry,
    MapEntryPattern,
    MapLiteral,
    MapPattern,
    MapType,
    MatchStatement,
    MethodCall,
    MethodDeclaration,
    MultiplicativeExpression,
    NotExpression,
    ObjectLiteral,
    ObjectPattern,
    OrExpression,
    Parameter,
    Program,
    PropertyAccess,
    PropertyDeclaration,
    QualifiedIdentifier,
    RelationalExpression,
    ReturnStatement,
    SpawnStatement,
    Statement,
    SuperCall,
    ThisAssignment,
    ThisExpression,
    ThrowStatement,
    TryStatement,
    TupleLiteral,
    TuplePattern,
    TupleType,
    Type,
    TypeDeclaration,
    TypedIdentifierPattern,
    TypeField,
    UnaryMinusExpression,
    UnaryPlusExpression,
    VariableAssignment,
    VariableDeclaration,
    WhileStatement,
)
from src.utils import debug_class_wrapper


@v_args(inline=True, meta=True)
@debug_class_wrapper
class SugarTransformer(Transformer):

    def program(self, meta, *statements):

        return Program(statements=list(statements), meta=meta)

    def primary_expression(self, meta, *children):

        if len(children) == 1:
            return children[0]
        if (
            len(children) == 3
            and isinstance(children[0], Token)
            and children[0].type == "LPAR"
            and isinstance(children[2], Token)
            and children[2].type == "RPAR"
        ):
            # The actual expression is the middle child
            return children[1]
        if isinstance(children[0], Identifier) and children[1].type == "LPAR":
            func_name_node = children[0]
            arguments = []
            if len(children) == 4 and isinstance(children[2], list):
                arguments = list(
                    self._filter_tokens_out(children[2])
                )  # argument_list method returns a list of expressions
            elif len(children) == 3 and children[2].type == "RPAR":
                arguments = []  # No arguments

            return FunctionCall(
                function_name=func_name_node, arguments=arguments, base=None, meta=meta
            )

        # Case 3: THIS (if not handled by postfix_expression for method calls)
        # If 'THIS' directly means a 'This' AST node.
        if (
            len(children) == 1
            and isinstance(children[0], Token)
            and children[0].type == "THIS"
        ):
            return ThisExpression(meta=meta)

        if (
            isinstance(children[0], Token)
            and len(children) == 4
            and isinstance(children[0], Token)
            and isinstance(children[1], Token)
            and children[0].type == "SUPER"
            and children[1].type == "LPAR"
        ):
            arguments = []
            if len(children) == 4 and isinstance(children[2], list):
                arguments = children[2]
                arguments = list(self._filter_tokens_out(arguments))
            return SuperCall(arguments=arguments, meta=meta)
        if (
            isinstance(children[0], Token)
            and len(children) == 5
            and children[0].type == "SUPER"
        ):
            arguments = children[3]
            arguments = list(self._filter_tokens_out(arguments))
            return SuperCall(arguments=arguments, meta=meta)

        logging.warning(f"Unhandled primary_expression children: {children}")
        return Tree("primary_expression", list(children))

    def variable_declaration(self, meta, _def, name, *rest):

        var_type = list(filter(lambda x: isinstance(x, Type), rest))[0]
        value = list(
            filter(
                lambda x: isinstance(x, Expression) or isinstance(x, Statement), rest
            )
        )[0]
        # property_access = list(filter(lambda x: isinstance(x, PropertyAccess), rest))
        # if property_access:
        #     property_access = property_access[0]
        #     name = Identifier(name=property_access.property_name.name)

        logging.debug(
            f"variable_declaration: name={name}, var_type={var_type}, value={value}"
        )
        return VariableDeclaration(name=name, var_type=var_type, value=value, meta=meta)

    def variable_assignment(self, meta, name, _equals, value):

        return VariableAssignment(name=name, value=value, meta=meta)

    def this_assignment(self, meta, _this, _colon, property_name, assign, value):

        return ThisAssignment(property_name=property_name, value=value, meta=meta)

    def this_method_call(
        self, meta, _this, _colon1, method_name, _colon2, _lparen, *other
    ):
        logging.debug(f"this_method_call: method_name={method_name}, other={other}")

        arguments = []
        if other and isinstance(other[0], list):
            arguments = list(self._filter_tokens_out(other[0]))
        elif other and isinstance(other[0], Token) and other[0].type == "RPAR":
            arguments = []

        return MethodCall(
            base=ThisExpression(meta=meta),
            function_name=method_name,
            arguments=arguments,
            meta=meta,
        )

    def function_declaration(self, meta, _func, name, _lparen, *everythingelse):
        logging.debug(
            f"function_declaration: name={name}, everythingelse={everythingelse}"
        )

        parameters = list(filter(lambda x: isinstance(x, Parameter), everythingelse[0]))
        return_type_list = list(filter(lambda x: isinstance(x, Type), everythingelse))
        return_type = (
            return_type_list[0] if return_type_list else Type(name="void", meta=meta)
        )
        body = list(self._filter_body_for_statements(everythingelse[-2]))

        logging.debug(
            f"  Parsed: parameters={parameters}, return_type={return_type}, body={body}"
        )
        return FunctionDeclaration(
            meta=meta,
            name=name,
            parameters=parameters,
            return_type=return_type,
            body=body,
        )

    def parameter_list(self, *parameters):

        return list(self._filter_tokens_out(parameters))

    def parameter(self, meta, name, param_type):

        return Parameter(name=name, param_type=param_type, meta=meta)

    def function_body(self, *statements):

        return list(statements)

    def return_statement(self, meta, _return, value=None):

        return ReturnStatement(value=value, meta=meta)

    def if_statement(
        self,
        meta,
        _if_kw,
        _dollar1,
        condition,
        _dollar2,
        _do,
        *body,
        elif_clauses=None,
        else_clause=None,
        _end_kw=None,
    ):
        logging.debug(
            f"if_statement: condition={condition}, body={body}, elif_clauses={elif_clauses}, else_clause={else_clause}"
        )
        # condiion looks like: Tree(Token('RULE', 'relational_expression'), [Identifier(name='x'), Tree(Token('RULE', 'relational_op'), [Token('GREATER_THAN', '>')]), Literal(value=10)])
        if elif_clauses is None:
            elif_clauses = []
        body, elif_cs, else_c = self._filter_if_body(body)
        if else_clause is None:
            else_clause = else_c
        elif_clauses.extend(elif_cs)

        return IfStatement(
            meta=meta,
            condition=condition,
            body=body,
            elif_clauses=elif_clauses,
            else_clause=else_clause,
        )

    def elif_clause(self, meta, _elif, _dollar1, condition, _dollar2, _do, *body):

        body = self._filter_if_body(body)[0]  # Filter body to get only statements
        return ElifClause(condition=condition, body=body, meta=meta)

    def else_clause(self, meta, _else, _do, *body):
        body = self._filter_if_body(body)[0]  # Filter body to get only statements

        return ElseClause(body=body, meta=meta)

    def for_statement(
        self, meta, _for, _def, variable, var_type, _in, iterable, _do, *body, _end=None
    ):
        logging.debug(
            f"for_statement: body={body}, variable={variable}, iterable={iterable}"
        )
        return ForStatement(
            meta=meta,
            iterator_name=variable,
            iterator_type=var_type,
            collection=iterable,
            body=list(self._filter_body_for_statements(body)),
        )

    def while_statement(
        self, meta, _while, _dollar1, condition, _dollar2, _do_kw, *body
    ):

        body = list(self._filter_body_for_statements(body))
        return WhileStatement(
            condition=condition,
            body=body,
            meta=meta,
        )

    def try_statement(self, meta, _try, *body, catch_clauses=None, finally_clause=None):
        logging.debug(
            f"try_statement: body={body}, catch_clauses={catch_clauses}, finally_clause={finally_clause}"
        )

        catch_clauses = list(filter(lambda x: isinstance(x, CatchClause), body))

        found_finally_clauses = list(
            filter(lambda x: isinstance(x, FinallyClause), body)
        )
        if found_finally_clauses:
            finally_clause = found_finally_clauses[0]
        else:
            finally_clause = None

        processed_body_statements = list(self._filter_body_for_statements(body))

        return TryStatement(
            meta=meta,
            body=processed_body_statements,
            catch_clauses=catch_clauses,
            finally_clause=finally_clause,
        )

    def throw_statement(self, meta, _throw, exception):
        return ThrowStatement(exception=exception, meta=meta)

    def catch_clause(self, meta, _catch, exception_name, exception_type, _do, *body):
        return CatchClause(
            exception_name=exception_name,
            exception_type=exception_type,
            body=list(self._filter_body_for_statements(body)),
            meta=meta,
        )

    def finally_clause(self, meta, _finally, _do, *body):
        return FinallyClause(
            body=list(self._filter_body_for_statements(body)), meta=meta
        )

    def type(self, meta, hash_token, type_specifier):

        return type_specifier

    def type_specifier(self, meta, specifier):

        return specifier

    def custom_type(self, meta, identifier):

        return Type(name=identifier.name, meta=meta)

    def PRIMITIVE_TYPE(self, token):

        return Type(name=token.value, meta=None)

    def expression(self, meta, value):

        return value

    def literal(self, meta, value):

        return value  # Literals are handled by their respective token types

    def BOOLEAN(self, token):

        if token.value == ":T:":
            return Literal(value=True, meta=None)
        elif token.value == ":F:":
            return Literal(value=False, meta=None)
        elif token.value == ":N:":
            return Literal(value=None, meta=None)
        else:
            raise ValueError(f"Unknown boolean/null literal: {token.value}")

    def IDENTIFIER(self, token):

        if token.value == "END":
            return End
        return Identifier(name=token.value, meta=None)

    def INTEGER(self, token):

        return Literal(value=int(token.value), meta=None)

    def FLOAT(self, token):

        return Literal(value=float(token.value), meta=None)

    def STRING(self, token):

        return Literal(value=token.value[1:-1], meta=None)  # Remove quotes

    def CHAR(self, token):

        return Literal(value=token.value[1:-1], meta=None)  # Remove quotes

    def argument_list(self, *expressions):
        return list(expressions)

    def or_expression(self, meta, left, op_token, right):
        return OrExpression(left=left, operator=op_token.value, right=right, meta=meta)

    def and_expression(self, meta, left, op_token, right):
        return AndExpression(left=left, operator=op_token.value, right=right, meta=meta)

    def equality_expression(self, meta, left, op_token, right):
        return EqualityExpression(
            left=left, operator=op_token.value, right=right, meta=meta
        )

    def equality_op(self, meta, op_token):
        return Token(type=op_token.type, value=op_token.value)

    def relational_expression(self, meta, left, op_token, right):
        return RelationalExpression(
            left=left, operator=op_token.value, right=right, meta=meta
        )

    def relational_op(self, meta, op_token):
        return Token(type=op_token.type, value=op_token.value)

    def additive_expression(self, meta, left, op_token, right):
        return AdditiveExpression(
            left=left, operator=op_token.value, right=right, meta=meta
        )

    def multiplicative_expression(self, meta, left, op_token, right):
        return MultiplicativeExpression(
            left=left, operator=op_token.value, right=right, meta=meta
        )

    # Unary Expressions (need to distinguish operator based on token)
    def unary_expression(self, meta, first_child, second_child=None):
        if isinstance(first_child, Token):  # It's an operator
            op_str = first_child.value
            if op_str == "!":
                return NotExpression(
                    operator=op_str, expression=second_child, meta=meta
                )
            elif op_str == "-":
                return UnaryMinusExpression(
                    operator=op_str, expression=second_child, meta=meta
                )
            elif op_str == "+":
                return UnaryPlusExpression(
                    operator=op_str, expression=second_child, meta=meta
                )
            else:
                raise ValueError(f"Unknown unary operator: {op_str}")
        else:  # It's a postfix_expression (the base case for recursion in the grammar)
            return first_child

    # Postfix Expressions
    def postfix_expression(
        self,
        meta,
        base_expr: Expression,
        *modifiers: MethodCall | PropertyAccess | ArrayAccess,
    ):
        # The first child is the primary_expression, subsequent children are modifiers
        #
        current_expr = base_expr
        for modifier in modifiers:
            if isinstance(modifier, MethodCall):
                # We need to set the base of the method call here
                modifier.base = current_expr
                current_expr = modifier
            elif isinstance(modifier, PropertyAccess):
                modifier.base = current_expr
                current_expr = modifier
            elif isinstance(modifier, ArrayAccess):
                modifier.base = current_expr
                current_expr = modifier

            else:
                # This should not happen if the grammar and previous transformers are correct
                raise TypeError(
                    f"Unexpected postfix modifier type: {type(modifier)}: {modifier}"
                )
        return current_expr

    def property_access(self, meta, _dot, property_name):

        base = Identifier(
            name="THIS SHOULD NOT SHOW UP, WE FIX IT IN POSTFIX EXPRESSION", meta=meta
        )
        return PropertyAccess(base=base, property_name=property_name, meta=meta)

    def array_access(self, meta, _lbracket, expression, _rbracket):

        base = Identifier(
            name="THIS SHOULD NOT SHOW UP, WE FIX IT IN POSTFIX EXPRESSION", meta=meta
        )
        return ArrayAccess(base=base, index=expression, meta=meta)

    def match_statement(
        self,
        meta,
        _match,
        expr,
        *body,
    ):

        default_clause = list(filter(lambda x: isinstance(x, DefaultClause), body))[0]
        case_clauses = list(filter(lambda x: isinstance(x, CaseClause), body))
        return MatchStatement(
            meta=meta,
            expression=expr,
            default_clause=default_clause,
            case_clauses=case_clauses,
        )

    def default_clause(self, meta, _default, _do, *body):

        body = list(self._filter_body_for_statements(body))
        return DefaultClause(meta=meta, body=body)

    def case_clause(self, meta, _case, pattern, *body):

        guard_p = list(filter(lambda x: isinstance(x, Expression), body))
        guard = guard_p[0] if guard_p else None
        return CaseClause(
            pattern=pattern,
            body=list(
                self._filter_body_for_statements(body),
            ),
            guard=guard,
            meta=meta,
        )

    def guard(self, meta, _if, _dollar1, condition, _dollar2):

        return self.expression(value=condition, meta=meta)

    def spawn_statement(self, meta, _spawn, expression):

        return SpawnStatement(
            expression=expression, meta=meta
        )  # Assuming expression is a valid statement

    def import_statement(self, meta, _import, dotted_name):

        return ImportStatement(dotted_name=dotted_name.split("."), meta=meta)

    def type_declaration(self, meta, *args):

        _type, name, *rest = args

        extends_clause = []
        type_body = []

        # The last element is always END
        for i in range(len(rest) - 1):
            item = rest[i]
            if isinstance(item[0], Token) and item[0].value == "EXTENDS":
                extends_clause.append(item[1])
            else:
                type_body.extend(item)

        return TypeDeclaration(
            name=name,
            type_body=type_body,
            extends_clause=extends_clause,
            meta=meta,
        )

    def type_body(self, meta, *fields):

        return list(fields)

    def type_field(self, meta, name, field_type):

        return TypeField(name=name, field_type=field_type, meta=meta)

    def extends_clause(self, meta, _extends, *identifiers):

        return [_extends] + list(identifiers)

    def implements_clause(self, meta, _implements, *identifiers):

        return [_implements] + list(identifiers)

    def class_declaration(self, meta, *args):

        _class, name, *rest = args
        extends_clause = []
        implements_clause = []
        class_body = []
        for item in rest:
            if isinstance(item, list):
                if isinstance(item[0], Token) and item[0].value == "IMPLEMENTS":
                    implements_clause.append(item[1])
                elif isinstance(item[0], Token) and item[0].value == "EXTENDS":
                    extends_clause.append(item[1])
                else:
                    class_body = item

        return ClassDeclaration(
            meta=meta,
            name=name,
            extends_clause=extends_clause,
            implements_clause=implements_clause,
            body=class_body,
        )

    def class_body(self, meta, *members):

        return list(members)

    def class_member(self, meta, *parts):

        access_modifier = None
        is_static = False
        is_override = False
        declaration = None

        for part in parts:
            if isinstance(part, AccessModifier):
                access_modifier = part
            elif isinstance(part, Token) and part.type == "STATIC":
                is_static = True
            elif isinstance(part, Token) and part.type == "OVERRIDE":
                is_override = True
            else:
                declaration = part

        if isinstance(declaration, ClassMember):
            declaration.access_modifier = access_modifier
            declaration.is_static = is_static
            declaration.is_override = is_override

        return declaration

    def access_modifier(self, meta, modifier):

        return AccessModifier(modifier=modifier.value, meta=meta)

    def property_declaration(self, meta, name, prop_type, *rest):
        logging.debug(
            f"property_declaration: name={name}, prop_type={prop_type}, rest={rest}"
        )
        value = rest[1] if len(rest) > 1 else None
        return PropertyDeclaration(
            name=name,
            meta=meta,
            property_type=prop_type,
            value=value,
            access_modifier=None,
            is_static=False,
            is_override=False,
        )

    def method_declaration(self, meta, _func, name, _lpar, *rest):

        parameters = rest[0] if rest and isinstance(rest[0], list) else []
        return_type = list(filter(lambda x: isinstance(x, Type), rest))[0]
        body = rest[-2] if len(rest) > 2 else []
        return MethodDeclaration(
            meta=meta,
            name=name,
            parameters=parameters,
            return_type=return_type,
            body=list(self._filter_body_for_statements(body)),
            access_modifier=None,
            is_static=False,
            is_override=False,
        )

    def constructor_declaration(self, meta, _constructor, _lpar, *rest):

        parameters = rest[0] if rest and isinstance(rest[0], list) else []
        body = rest[-2] if len(rest) > 2 else []
        return ConstructorDeclaration(
            meta=meta,
            parameters=parameters,
            body=list(self._filter_body_for_statements(body)),
            access_modifier=None,
            is_static=False,
            is_override=False,
        )

    def interface_declaration(self, meta, _interface, name, body, _end):

        return InterfaceDeclaration(name=name, body=body, meta=meta)

    def interface_body(self, meta, *members):

        return list(members)

    def interface_member(self, meta, _func, name, _lpar, *rest):

        parameters = rest[0] if rest and isinstance(rest[0], list) else []
        return_type_list = list(filter(lambda x: isinstance(x, Type), rest))
        return_type = (
            return_type_list[0] if return_type_list else Type(name="void", meta=meta)
        )
        return InterfaceMethodDeclaration(
            meta=meta, name=name, parameters=parameters, return_type=return_type
        )

    def expression_statement(self, meta, expression):

        return ExpressionStatement(expression=expression, meta=meta)

    def array_literal(self, meta, _lbracket, elements, _rbracket):
        elements = list(self._filter_tokens_out(elements))

        return ArrayLiteral(elements=elements or [], meta=meta)

    def map_literal(self, meta, _lbrace, entries, _rbrace):

        return MapLiteral(entries=entries or [], meta=meta)

    def map_entries(self, meta, *entries):

        entries = list(self._filter_tokens_out(entries))
        return list(entries)

    def map_entry(self, meta, key, _arrow, value):

        return MapEntry(key=key, value=value, meta=meta)

    def object_literal(self, meta, _lbrace, entries, _rbrace):

        return ObjectLiteral(entries=entries or [], meta=meta)

    def dict_entries(self, meta, *entries):

        entries = list(self._filter_tokens_out(entries))
        return list(entries)

    def dict_entry(self, meta, key, _colon, value):

        return DictEntry(key=key, value=value, meta=meta)

    def empty_object_literal(self, meta, *args):

        return ObjectLiteral(entries=[], meta=meta)

    def empty_list_literal(self, meta, *args):
        return ArrayLiteral(elements=[], meta=meta)

    def empty_map_literal(self, meta, *args):
        return MapLiteral(entries=[], meta=meta)

    def empty_tuple_literal(self, meta, *args):
        return TupleLiteral(elements=[], meta=meta)

    def tuple_literal(self, meta, _lparen, *elements):

        elements = list(self._filter_tokens_out(elements))
        return TupleLiteral(elements=list(elements) or [], meta=meta)

    def lambda_expression(self, meta, _func, _lpar, *rest):
        parameters = list(filter(lambda x: isinstance(x, Parameter), rest[0]))
        body = rest[-1]

        return LambdaExpression(parameters=parameters or [], body=body, meta=meta)

    def anonymous_function(self, meta, _func, _lpar, *everythingelse):

        parameters = list(filter(lambda x: isinstance(x, Parameter), everythingelse[0]))
        return_type = list(filter(lambda x: isinstance(x, Type), everythingelse))[0]
        body = list(self._filter_body_for_statements(everythingelse[-2]))
        return AnonymousFunction(
            parameters=parameters, body=body, type=return_type, meta=meta
        )

    def method_call(self, meta, _colon1, method, _colon2, _lparen, *other):
        logging.debug(
            f"method_call: method={method}, other={other}, _lparen={_lparen}, _colon2={_colon2}, _colon_1= {_colon1}"
        )
        arguments = list(self._filter_tokens_out(other[0]))
        if isinstance(other[0], Token) and other[0].type == "RPAR":
            # No arguments
            arguments = []

        base = Identifier(
            name="THIS SHOULD NOT SHOW UP, WE FIX IT IN POSTFIX EXPRESSION", meta=meta
        )

        return MethodCall(
            base=base, function_name=method, arguments=arguments, meta=meta
        )

    def method_name(self, meta, what):

        return self.expression(meta, what)

    def array_type(self, meta, _lbracket, base_type, _rbracket):

        return ArrayType(name=f"[{base_type.name}]", base_type=base_type, meta=meta)

    def map_type(self, meta, _lbrace, key_type, _comma, value_type, _rbrace):

        return MapType(
            name=f"{{{key_type.name},{value_type.name}}}",
            key_type=key_type,
            value_type=value_type,
            meta=meta,
        )

    def tuple_type(self, meta, _lparen, *types):

        type_list = list(self._filter_tokens_out(types))
        return TupleType(
            name=f"({','.join([t.name for t in type_list])})",
            types=type_list,
            meta=meta,
        )

    def qualified_identifier(self, meta, *parts):

        return QualifiedIdentifier(
            parts=list(self._filter_tokens_out(parts)), meta=meta
        )

    def pattern(self, meta, *parts):

        if len(parts) == 1:
            if isinstance(parts[0], Literal):
                return LiteralPattern(literal=parts[0], meta=meta)
            elif isinstance(parts[0], Identifier):
                return IdentifierPattern(name=parts[0], meta=meta)
            elif isinstance(parts[0], ArrayPattern):
                return parts[0]
            elif isinstance(parts[0], ObjectPattern):
                return parts[0]
            elif isinstance(parts[0], MapPattern):
                return parts[0]
            elif isinstance(parts[0], TuplePattern):
                return parts[0]
            else:
                return parts[0]
        elif (
            len(parts) == 2
            and isinstance(parts[0], Type)
            and isinstance(parts[1], Identifier)
        ):
            return TypedIdentifierPattern(var_type=parts[0], name=parts[1], meta=meta)
        else:
            raise ValueError(f"Unsupported pattern structure: {parts}")

    def dotted_name(self, meta, *identifiers):

        filttered = list(filter(lambda x: isinstance(x, Identifier), identifiers))
        return ".".join([identifier.name for identifier in filttered])

    def _filter_if_body(self, body):
        else_clase = None
        elif_clauses = []
        main_body = []
        for piece in body:
            if isinstance(piece, Token):
                if piece.type == "END":

                    break
            elif isinstance(piece, ElifClause):

                elif_clauses.append(piece)
            elif isinstance(piece, ElseClause):
                if not else_clase:

                    else_clase = piece
                else:
                    raise ValueError(
                        "Multiple else clauses found in if statement body."
                    )
            else:
                main_body.append(piece)

        return main_body, elif_clauses, else_clase

    def tuple_pattern(self, meta, _lparen, patterns, _rparen):

        return TuplePattern(
            patterns=list(self._filter_tokens_out(patterns)) or [], meta=meta
        )

    def object_pattern(self, meta, _lbrace, entries, _rbrace):

        return ObjectPattern(entries=entries or [], meta=meta)

    def dict_pattern_entries(self, meta, *entries):

        return list(self._filter_tokens_out(entries))

    def dict_pattern_entry(self, meta, key, _colon, value):

        return DictEntryPattern(key=key, value=value, meta=meta)

    def map_pattern(self, meta, _lbrace, entries, _rbrace):

        return MapPattern(entries=entries or [], meta=meta)

    def map_pattern_entries(self, meta, *entries):

        return list(self._filter_tokens_out(entries))

    def map_pattern_entry(self, meta, key, _arrow, value):

        return MapEntryPattern(key=key, value=value, meta=meta)

    def empty_object_pattern(self, meta, *args):

        return ObjectPattern(entries=[], meta=meta)

    def empty_map_pattern(self, meta, *args):

        return MapPattern(entries=[], meta=meta)

    def array_pattern(self, meta, _lbracket, patterns, _rbracket):

        return ArrayPattern(patterns=patterns or [], meta=meta)

    def pattern_list(self, meta, *patterns):

        return list(self._filter_tokens_out(patterns))

    def assignable_target(self, meta, token, property_access=None):

        if not property_access:
            if isinstance(token, Identifier):
                return token
            else:
                return Identifier(name=token.value, meta=meta)
        return PropertyAccess(
            base=Identifier(name=token.value, meta=meta),
            property_name=Identifier(
                name=property_access.property_name.name, meta=meta
            ),
            meta=meta,
        )

    def target_expression(self, meta, token, property_access=None):

        base = (
            token
            if isinstance(token, Identifier)
            else Identifier(name=token.value, meta=meta)
        )
        if not property_access:
            return base
        return PropertyAccess(
            base=base,
            property_name=Identifier(
                name=property_access.property_name.name, meta=meta
            ),
            meta=meta,
        )

    def super_method_call(
        self, meta, _super, _colon, name, _colon2, _lparen, *arguments
    ):

        return MethodCall(
            meta=meta,
            base=SuperCall(meta=meta),
            function_name=name,
            arguments=list(self._filter_tokens_out(arguments)),
        )

    def super_constructor_call(self, meta, _super, _colon1, _lparen, *arguments):
        arguments = []
        if len(arguments) == 2:
            args = list(self._filter_tokens_out(arguments[0]))
            if all(map(lambda x: isinstance(x, Expression), args)):
                arguments = list(self._filter_tokens_out(args))

        return SuperCall(arguments=arguments if arguments else None, meta=meta)

    def _filter_body_for_statements(self, body):
        for piece in body:
            if isinstance(piece, Statement):
                yield piece
            elif isinstance(piece, Token):
                if piece.type == "END":
                    break

    def _filter_tokens_out(self, lst):
        for piece in lst:
            if isinstance(piece, Token) or isinstance(piece, tree.Meta):
                continue
            yield piece
