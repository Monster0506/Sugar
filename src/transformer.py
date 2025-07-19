"""
Transforms the Lark parse tree into a structured AST.
"""

import logging

from lark import Token, Transformer, Tree, v_args

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


@v_args(inline=True)
# @debug_class_wrapper
class SugarTransformer(Transformer):
    def program(self, *statements):
        logging.debug(f"program: statements={statements}")
        return Program(statements=list(statements))

    def primary_expression(self, *children):
        logging.debug(f"primary_expression: children={children}")

        if len(children) == 1:
            return children[0]

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
                function_name=func_name_node, arguments=arguments, base=None
            )

        # Case 3: THIS (if not handled by postfix_expression for method calls)
        # If 'THIS' directly means a 'This' AST node.
        if (
            len(children) == 1
            and isinstance(children[0], Token)
            and children[0].type == "THIS"
        ):
            return ThisExpression()

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
            return SuperCall(arguments=arguments)

        logging.warning(f"Unhandled primary_expression children: {children}")
        return Tree("primary_expression", list(children))

    def variable_declaration(self, _def, name, var_type, _equals, value):
        logging.debug(
            f"variable_declaration: name={name}, var_type={var_type}, value={value}"
        )
        return VariableDeclaration(name=name, var_type=var_type, value=value)

    def variable_assignment(self, name, _equals, value):
        logging.debug(f"variable_assignment: name={name}, value={value}")
        return VariableAssignment(name=name, value=value)

    def this_assignment(self, _this, _colon, property_name, assign, value):
        logging.debug(f"this_assignment: property_name={property_name}, value={value}")
        return ThisAssignment(property_name=property_name, value=value)

    def function_declaration(self, _func, name, _lparen, *everythingelse):
        logging.debug(
            f"function_declaration: name={name}, everythingelse={everythingelse}"
        )

        parameters = list(filter(lambda x: isinstance(x, Parameter), everythingelse[0]))
        return_type_list = list(filter(lambda x: isinstance(x, Type), everythingelse))
        return_type = return_type_list[0] if return_type_list else Type(name="void")
        body = list(self._filter_body_for_statements(everythingelse[-2]))

        logging.debug(
            f"  Parsed: parameters={parameters}, return_type={return_type}, body={body}"
        )
        return FunctionDeclaration(
            name=name, parameters=parameters, return_type=return_type, body=body
        )

    def parameter_list(self, *parameters):
        logging.debug(f"parameter_list: parameters={parameters}")
        return list(parameters)

    def parameter(self, name, param_type):
        logging.debug(f"parameter: name={name}, param_type={param_type}")
        return Parameter(name=name, param_type=param_type)

    def function_body(self, *statements):
        logging.debug(f"function_body: statements={statements}")
        return list(statements)

    def return_statement(self, _return, value=None):
        logging.debug(f"return_statement: value={value}")
        return ReturnStatement(value=value)

    def if_statement(
        self,
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
            condition=condition,
            body=body,
            elif_clauses=elif_clauses,
            else_clause=else_clause,
        )

    def elif_clause(self, _elif, _dollar1, condition, _dollar2, _do, *body):

        logging.debug(f"elif_clause: condition={condition}, body={body}")
        body = self._filter_if_body(body)[0]  # Filter body to get only statements
        return ElifClause(condition=condition, body=body)

    def else_clause(self, _else, _do, *body):
        body = self._filter_if_body(body)[0]  # Filter body to get only statements
        logging.debug(f"else_clause: body={body}")
        return ElseClause(body=body)

    def for_statement(
        self, _for, _def, variable, var_type, _in, iterable, _do, *body, _end=None
    ):
        logging.debug(
            f"for_statement: body={body}, variable={variable}, iterable={iterable}"
        )
        return ForStatement(
            iterator_name=variable,
            iterator_type=var_type,
            collection=iterable,
            body=list(self._filter_body_for_statements(body)),
        )

    def while_statement(self, _while, _dollar1, condition, _dollar2, _do_kw, *body):
        logging.debug(f"while_statement: condition={condition}, body={body}")
        body = list(self._filter_body_for_statements(body))
        return WhileStatement(condition=condition, body=body)

    def try_statement(self, _try, *body, catch_clauses=None, finally_clause=None):
        logging.debug(
            f"try_statement: body={body}, catch_clauses={catch_clauses}, finally_clause={finally_clause}"
        )

        catch_clauses = list(filter(lambda x: isinstance(x, CatchClause), body))
        finally_clause = (
            list(filter(lambda x: isinstance(x, FinallyClause), body))[0] or None
        )
        body = list(self._filter_body_for_statements(body))
        return TryStatement(
            body=body,
            catch_clauses=catch_clauses or [],
            finally_clause=finally_clause,
        )

    def throw_statement(self, _throw, exception):
        return ThrowStatement(exception=exception)

    def catch_clause(self, _catch, exception_name, exception_type, _do, *body):
        return CatchClause(
            exception_name=exception_name,
            exception_type=exception_type,
            body=list(self._filter_body_for_statements(body)),
        )

    def finally_clause(self, _finally, _do, *body):
        return FinallyClause(list(self._filter_body_for_statements(body)))

    def type(self, hash_token, type_specifier):
        logging.debug(f"type: hash_token={hash_token}, type_specifier={type_specifier}")
        return type_specifier

    def type_specifier(self, specifier):
        logging.debug(f"type_specifier: specifier={specifier}")
        return specifier

    def custom_type(self, identifier):
        logging.debug(f"custom_type: identifier={identifier}")
        return Type(name=identifier.name)

    def PRIMITIVE_TYPE(self, token):
        logging.debug(f"PRIMITIVE_TYPE: token={token}")
        return Type(name=token.value)

    def expression(self, value):
        logging.debug(f"expression: value={value}")
        return value

    def literal(self, value):
        logging.debug(f"literal: value={value}")
        return value  # Literals are handled by their respective token types

    def BOOLEAN(self, token):
        logging.debug(f"BOOLEAN: token={token}")
        return Literal(value=True if token.value == ":T:" else False)

    def IDENTIFIER(self, token):
        logging.debug(f"IDENTIFIER: token={token}")
        if token.value == "END":
            return End
        return Identifier(name=token.value)

    def INTEGER(self, token):
        logging.debug(f"INTEGER: token={token}")
        return Literal(value=int(token.value))

    def FLOAT(self, token):
        logging.debug(f"FLOAT: token={token}")
        return Literal(value=float(token.value))

    def STRING(self, token):
        logging.debug(f"STRING: token={token}")
        return Literal(value=token.value[1:-1])  # Remove quotes

    def CHAR(self, token):
        logging.debug(f"CHAR: token={token}")
        return Literal(value=token.value[1:-1])  # Remove quotes

    def argument_list(self, *expressions):
        return list(expressions)

    def or_expression(self, left, op_token, right):
        return OrExpression(left, op_token.value, right)

    def and_expression(self, left, op_token, right):
        return AndExpression(left, op_token.value, right)

    def equality_expression(self, left, op_token, right):
        return EqualityExpression(left, op_token.value, right)

    def equality_op(self, op_token):
        return Token(type=op_token.type, value=op_token.value)

    def relational_expression(self, left, op_token, right):
        return RelationalExpression(left, op_token.value, right)

    def relational_op(self, op_token):
        return Token(type=op_token.type, value=op_token.value)

    def additive_expression(self, left, op_token, right):
        return AdditiveExpression(left, op_token.value, right)

    def multiplicative_expression(self, left, op_token, right):
        return MultiplicativeExpression(left, op_token.value, right)

    # Unary Expressions (need to distinguish operator based on token)
    def unary_expression(self, first_child, second_child=None):
        if isinstance(first_child, Token):  # It's an operator
            op_str = first_child.value
            if op_str == "!":
                return NotExpression(op_str, second_child)
            elif op_str == "-":
                return UnaryMinusExpression(op_str, second_child)
            elif op_str == "+":
                return UnaryPlusExpression(op_str, second_child)
            else:
                raise ValueError(f"Unknown unary operator: {op_str}")
        else:  # It's a postfix_expression (the base case for recursion in the grammar)
            return first_child

    # Postfix Expressions
    def postfix_expression(
        self,
        base_expr: Expression,
        *modifiers: MethodCall | PropertyAccess | ArrayAccess,
    ):
        # The first child is the primary_expression, subsequent children are modifiers
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

    def property_access(self, _dot, property_name):
        logging.debug(f"property_access: property_name={property_name}")
        base = Identifier("THIS SHOULD NOT SHOW UP, WE FIX IT IN POSTFIX EXPRESSION")
        return PropertyAccess(base=base, property_name=property_name)

    def array_access(self, _lbracket, expression, _rbracket):
        logging.debug(f"array_access: expr={expression}")
        base = Identifier("THIS SHOULD NOT SHOW UP, WE FIX IT IN POSTFIX EXPRESSION")
        return ArrayAccess(base=base, index=expression)

    def match_statement(
        self,
        _match,
        expr,
        *body,
    ):

        default_clause = list(filter(lambda x: isinstance(x, DefaultClause), body))[0]
        case_clauses = list(filter(lambda x: isinstance(x, CaseClause), body))
        return MatchStatement(
            expression=expr, default_clause=default_clause, case_clauses=case_clauses
        )

    def default_clause(self, _default, _do, *body):
        logging.debug(f"default_clause: body={body}")
        body = list(self._filter_body_for_statements(body))
        return DefaultClause(body=body)

    def case_clause(self, _case, pattern, *body):
        logging.debug(f"case_clause: pattern={pattern}, body={body}")

        guard_p = list(filter(lambda x: isinstance(x, Expression), body))
        guard = guard_p[0] if guard_p else None
        return CaseClause(
            pattern=pattern,
            body=list(
                self._filter_body_for_statements(body),
            ),
            guard=guard,
        )

    def guard(self, _if, _dollar1, condition, _dollar2):
        logging.debug(f"guard: condition={condition}")
        return self.expression(condition)

    def spawn_statement(self, _spawn, expression):
        logging.debug(f"spawn_statement: expression={expression}")
        return SpawnStatement(
            expression=expression
        )  # Assuming expression is a valid statement

    def import_statement(self, _import, dotted_name):
        logging.debug(f"import_statement: dotted_name={dotted_name}")
        return ImportStatement(dotted_name=dotted_name.split("."))

    def type_declaration(self, *args):
        logging.debug(f"type_declaration: args={args}")
        _type, name, *rest = args

        extends_clause = None
        type_body = []

        # The last element is always END
        if len(rest) > 1:
            # Check if the first element in rest is the extends_clause
            if isinstance(rest[0], list) and all(
                isinstance(i, Identifier) for i in rest[0]
            ):
                extends_clause = rest[0]
                type_body = rest[1]
            else:
                type_body = rest[0]

        return TypeDeclaration(
            name=name, type_body=type_body, extends_clause=extends_clause
        )

    def type_body(self, *fields):
        logging.debug(f"type_body: fields={fields}")
        return list(fields)

    def type_field(self, name, field_type):
        logging.debug(f"type_field: name={name}, field_type={field_type}")
        return TypeField(name=name, field_type=field_type)

    def extends_clause(self, _extends, *identifiers):
        logging.debug(f"extends_clause: identifiers={identifiers}")
        return list(identifiers)

    def implements_clause(self, _implements, *identifiers):
        logging.debug(f"implements_clause: identifiers={identifiers}")
        return list(identifiers)

    def class_declaration(self, *args):
        logging.debug(f"class_declaration: args={args}")
        _class, name, *rest = args
        extends_clause = None
        implements_clause = None
        class_body = []

        for item in rest:
            if isinstance(item, list) and all(isinstance(i, Identifier) for i in item):
                if extends_clause is None:
                    extends_clause = item
                else:
                    implements_clause = item
            elif isinstance(item, list):
                class_body = item

        return ClassDeclaration(
            name=name,
            extends_clause=extends_clause,
            implements_clause=implements_clause,
            body=class_body,
        )

    def class_body(self, *members):
        logging.debug(f"class_body: members={members}")
        return list(members)

    def class_member(self, *parts):
        logging.debug(f"class_member: parts={parts}")
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

    def access_modifier(self, modifier):
        logging.debug(f"access_modifier: modifier={modifier}")
        return AccessModifier(modifier=modifier.value)

    def property_declaration(self, name, prop_type, *rest):
        logging.debug(
            f"property_declaration: name={name}, prop_type={prop_type}, rest={rest}"
        )
        value = rest[1] if len(rest) > 1 else None
        return PropertyDeclaration(
            name=name,
            property_type=prop_type,
            value=value,
            access_modifier=None,
            is_static=False,
            is_override=False,
        )

    def method_declaration(self, _func, name, _lpar, *rest):
        logging.debug(f"method_declaration: name={name}, rest={rest}")
        parameters = rest[0] if rest and isinstance(rest[0], list) else []
        return_type = rest[1] if len(rest) > 1 and isinstance(rest[1], Type) else None
        body = rest[-2] if len(rest) > 2 else []
        return MethodDeclaration(
            name=name,
            parameters=parameters,
            return_type=return_type,
            body=list(self._filter_body_for_statements(body)),
            access_modifier=None,
            is_static=False,
            is_override=False,
        )

    def constructor_declaration(self, _constructor, _lpar, *rest):
        logging.debug(f"constructor_declaration: rest={rest}")
        parameters = rest[0] if rest and isinstance(rest[0], list) else []
        body = rest[-2] if len(rest) > 2 else []
        return ConstructorDeclaration(
            parameters=parameters,
            body=list(self._filter_body_for_statements(body)),
            access_modifier=None,
            is_static=False,
            is_override=False,
        )

    def interface_declaration(self, _interface, name, body, _end):
        logging.debug(f"interface_declaration: name={name}, body={body}")
        return InterfaceDeclaration(name=name, body=body)

    def interface_body(self, *members):
        logging.debug(f"interface_body: members={members}")
        return list(members)

    def interface_member(self, _func, name, _lpar, *rest):
        logging.debug(f"interface_member: name={name}, rest={rest}")
        parameters = rest[0] if rest and isinstance(rest[0], list) else []
        return_type_list = list(filter(lambda x: isinstance(x, Type), rest))
        return_type = return_type_list[0] if return_type_list else Type(name="void")
        return InterfaceMethodDeclaration(
            name=name, parameters=parameters, return_type=return_type
        )

    def expression_statement(self, expression):
        logging.debug(f"expression_statement: expression={expression}")
        return ExpressionStatement(expression=expression)

    def array_literal(self, _lbracket, elements, _rbracket):
        elements = list(self._filter_tokens_out(elements))
        logging.debug(f"array_literal: elements={elements}")
        return ArrayLiteral(elements=elements or [])

    def map_literal(self, _lbrace, entries, _rbrace):
        logging.debug(f"map_literal: entries={entries}")
        return MapLiteral(entries=entries or [])

    def map_entries(self, *entries):
        logging.debug(f"map_entries: entries={entries}")
        entries = list(self._filter_tokens_out(entries))
        return list(entries)

    def map_entry(self, key, _arrow, value):
        logging.debug(f"map_entry: key={key}, value={value}")
        return MapEntry(key=key, value=value)

    def object_literal(self, _lbrace, entries, _rbrace):
        logging.debug(f"object_literal: entries={entries}")
        return ObjectLiteral(entries=entries or [])

    def dict_entries(self, *entries):
        logging.debug(f"dict_entries: entries={entries}")
        entries = list(self._filter_tokens_out(entries))
        return list(entries)

    def dict_entry(self, key, _colon, value):
        logging.debug(f"dict_entry: key={key}, value={value}")
        return DictEntry(key=key, value=value)

    def empty_object_literal(self, *args):
        logging.debug("empty_object_literal")
        return ObjectLiteral(entries=[])

    def empty_list_literal(self, *args):
        return ArrayLiteral(elements=[])

    def empty_map_literal(self, *args):
        return MapLiteral(entries=[])

    def empty_tuple_literal(self, *args):
        return TupleLiteral(elements=[])

    def tuple_literal(self, _lparen, *elements):
        logging.debug(f"tuple_literal: elements={elements}")
        elements = list(self._filter_tokens_out(elements))
        return TupleLiteral(elements=list(elements) or [])

    def lambda_expression(self, _func, _lpar, params, _rpar, _arrow, body):
        logging.debug(f"lambda_expression: params={params}, body={body}")
        params = list(filter(lambda x: isinstance(x, Parameter), params))
        return LambdaExpression(parameters=params or [], body=body)

    def anonymous_function(self, _func, _lpar, *everythingelse):
        logging.debug(f"anonymous_function: everythingelse={everythingelse}")
        parameters = list(filter(lambda x: isinstance(x, Parameter), everythingelse[0]))
        return_type = list(filter(lambda x: isinstance(x, Type), everythingelse))[0]
        body = list(self._filter_body_for_statements(everythingelse[-2]))
        return AnonymousFunction(parameters=parameters, body=body, type=return_type)

    def method_call(self, _colon1, method, _colon2, _lparen, *other):
        print(
            f"method_call: method={method}, other={other}, _lparen={_lparen}, _colon2={_colon2}, _colon_1= {_colon1}"
        )
        print("looking here: ", other)
        arguments = list(self._filter_tokens_out(other[0]))
        if isinstance(other[0], Token) and other[0].type == "RPAR":
            # No arguments
            arguments = []

        base = Identifier("THIS SHOULD NOT SHOW UP, WE FIX IT IN POSTFIX EXPRESSION")

        return MethodCall(base=base, function_name=method, arguments=arguments)

    def method_name(self, what):
        logging.debug(f"method_name: what={what}")
        return self.expression(what)

    def array_type(self, _lbracket, base_type, _rbracket):
        logging.debug(f"array_type: base_type={base_type}")
        return ArrayType(name=f"[{base_type.name}]", base_type=base_type)

    def map_type(self, _lbrace, key_type, _comma, value_type, _rbrace):
        logging.debug(f"map_type: key_type={key_type}, value_type={value_type}")
        return MapType(
            name=f"{{{key_type.name},{value_type.name}}}",
            key_type=key_type,
            value_type=value_type,
        )

    def tuple_type(self, _lparen, *types):
        logging.debug(f"tuple_type: types={types}")
        type_list = list(self._filter_tokens_out(types))
        return TupleType(
            name=f"({','.join([t.name for t in type_list])})", types=type_list
        )

    def qualified_identifier(self, *parts):
        logging.debug(f"qualified_identifier: parts={parts}")
        return QualifiedIdentifier(parts=list(self._filter_tokens_out(parts)))

    def pattern(self, *parts):
        logging.debug(f"pattern: parts={parts}")
        if len(parts) == 1:
            if isinstance(parts[0], Literal):
                return LiteralPattern(literal=parts[0])
            elif isinstance(parts[0], Identifier):
                return IdentifierPattern(name=parts[0])
            elif isinstance(parts[0], ArrayLiteral):
                return ArrayPattern(
                    patterns=(
                        [self.pattern(e) for e in parts[0].elements]
                        if parts[0].elements
                        else []
                    )
                )
            elif isinstance(parts[0], ObjectLiteral):
                return ObjectPattern(
                    entries=(
                        [
                            self._transform_dict_entry_to_pattern(e)
                            for e in parts[0].entries
                        ]
                        if parts[0].entries
                        else []
                    )
                )
            elif isinstance(parts[0], MapLiteral):
                return MapPattern(
                    entries=(
                        [
                            self._transform_map_entry_to_pattern(e)
                            for e in parts[0].entries
                        ]
                        if parts[0].entries
                        else []
                    )
                )
            elif isinstance(parts[0], TupleLiteral):
                return TuplePattern(
                    patterns=(
                        [self.pattern(e) for e in parts[0].elements]
                        if parts[0].elements
                        else []
                    )
                )
            else:
                return parts[0]
        elif (
            len(parts) > 1
            and isinstance(parts[0], Token)
            and parts[0].type == "LBRACKET"
        ):
            return ArrayPattern(patterns=list(self._filter_tokens_out(parts[1:-1])))
        elif (
            len(parts) == 2
            and isinstance(parts[0], Type)
            and isinstance(parts[1], Identifier)
        ):
            return TypedIdentifierPattern(var_type=parts[0], name=parts[1])
        else:
            raise ValueError(f"Unsupported pattern structure: {parts}")

    def dotted_name(self, *identifiers):
        logging.debug(f"dotted_name: identifiers={identifiers}")
        filttered = list(filter(lambda x: isinstance(x, Identifier), identifiers))
        return ".".join([identifier.name for identifier in filttered])

    def _filter_if_body(self, body):
        else_clase = None
        elif_clauses = []
        main_body = []
        for piece in body:
            if isinstance(piece, Token):
                if piece.type == "END":
                    logging.debug("ENDING")
                    break
            elif isinstance(piece, ElifClause):
                logging.debug(f"ELIF_CLAUSE found: {piece}")
                elif_clauses.append(piece)
            elif isinstance(piece, ElseClause):
                if not else_clase:
                    logging.debug(f"ELSE_CLAUSE found: {piece}")
                    else_clase = piece
                else:
                    raise ValueError(
                        "Multiple else clauses found in if statement body."
                    )
            else:
                main_body.append(piece)

        return main_body, elif_clauses, else_clase

    def _filter_body_for_statements(self, body):
        for piece in body:
            if isinstance(piece, Statement):
                yield piece
            elif isinstance(piece, Token):
                if piece.type == "END":
                    break

    def _filter_tokens_out(self, lst):
        for piece in lst:
            if isinstance(piece, Token):
                continue
            yield piece

    def _transform_dict_entry_to_pattern(self, entry: DictEntry) -> DictEntryPattern:
        return DictEntryPattern(key=entry.key, value=self.pattern(entry.value))

    def _transform_map_entry_to_pattern(self, entry: MapEntry) -> MapEntryPattern:
        return MapEntryPattern(
            key=self.pattern(entry.key), value=self.pattern(entry.value)
        )
