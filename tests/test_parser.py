import pytest

from src.ast_nodes import (
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
    DefaultClause,
    ElifClause,
    ElseClause,
    Expression,
    ExpressionStatement,
    FinallyClause,
    ForStatement,
    FunctionCall,
    FunctionDeclaration,
    Identifier,
    IfStatement,
    ImportStatement,
    InterfaceDeclaration,
    LambdaExpression,
    Literal,
    LiteralPattern,
    MapEntry,
    MapLiteral,
    MapPattern,
    MapType,
    MatchStatement,
    MethodCall,
    MultiplicativeExpression,
    NotExpression,
    ObjectLiteral,
    ObjectPattern,
    OrExpression,
    Program,
    PropertyAccess,
    RelationalExpression,
    ReturnStatement,
    SpawnStatement,
    SuperCall,
    ThrowStatement,
    TryStatement,
    TupleLiteral,
    TuplePattern,
    TupleType,
    Type,
    TypeDeclaration,
    TypedIdentifierPattern,
    UnaryMinusExpression,
    UnaryPlusExpression,
    VariableAssignment,
    VariableDeclaration,
    WhileStatement,
)
from src.parser import parse_to_ast


def test_variable_declaration():
    """Tests parsing of a simple variable declaration."""
    code = "DEF my_var #int = 10"
    ast = parse_to_ast(code)

    assert isinstance(ast, Program)
    assert len(ast.statements) == 1

    statement = ast.statements[0]
    assert isinstance(statement, VariableDeclaration)
    assert statement.name.name == "my_var"
    assert statement.var_type.name == "int"
    assert isinstance(statement.value, Literal)
    assert statement.value.value == 10


def test_variable_assignment():
    """Tests parsing of a simple variable assignment."""
    code = "my_var := 20"
    ast = parse_to_ast(code)

    assert isinstance(ast, Program)
    assert len(ast.statements) == 1

    statement = ast.statements[0]
    assert isinstance(statement, VariableAssignment)
    assert statement.name.name == "my_var"
    assert isinstance(statement.value, Literal)
    assert statement.value.value == 20


def test_this_assignment():
    """Tests parsing of a 'this' assignment."""
    code = "DEF THIS.my_prop #int = 30"
    ast = parse_to_ast(code)

    assert isinstance(ast, Program)
    assert len(ast.statements) == 1

    statement = ast.statements[0]
    assert isinstance(statement, VariableDeclaration)
    assert isinstance(statement.name, PropertyAccess)
    assert statement.name.property_name.name == "my_prop"
    assert isinstance(statement.value, Literal)
    assert statement.value.value == 30


def test_function_declaration():
    """Tests parsing of a simple function declaration."""
    code = """FUNC my_func(param1 #int, param2 #str) #bool
    DEF y #int = 3
    y := 5
  RETURN :T:
end"""
    ast = parse_to_ast(code)

    assert isinstance(ast, Program)
    assert len(ast.statements) == 1

    statement = ast.statements[0]
    assert isinstance(statement, FunctionDeclaration)
    assert statement.name.name == "my_func"
    assert len(statement.parameters) == 2
    assert statement.parameters[0].name.name == "param1"
    assert statement.parameters[0].param_type.name == "int"
    assert statement.parameters[1].name.name == "param2"
    assert statement.parameters[1].param_type.name == "str"
    assert isinstance(statement.return_type, Type)
    assert statement.return_type.name == "bool"
    assert isinstance(statement.body, list)
    assert len(statement.body) == 3
    assert isinstance(statement.body[-1], ReturnStatement)
    assert isinstance(statement.body[-1].value, Literal)
    assert statement.body[-1].value.value is True


def test_if_statement():
    """Tests parsing of a simple if statement."""
    code = """if $x > 10$ do
      DEF y #int = 5
      DEF z #bool = :T:
end"""
    ast = parse_to_ast(code)

    assert isinstance(ast, Program)
    assert len(ast.statements) == 1

    if_stmt = ast.statements[0]
    assert isinstance(if_stmt, IfStatement)
    assert isinstance(if_stmt.condition, RelationalExpression)
    assert len(if_stmt.body) == 2
    assert isinstance(if_stmt.body[0], VariableDeclaration)
    assert len(if_stmt.elif_clauses) == 0
    assert if_stmt.else_clause is None


def test_if_else_statement():
    """Tests parsing of an if-else statement."""
    code = """if $x > 10$ do
      DEF y #int = 5
    else do
      DEF z #int = 10
    end"""
    ast = parse_to_ast(code)

    assert isinstance(ast, Program)
    assert len(ast.statements) == 1

    if_stmt = ast.statements[0]
    assert isinstance(if_stmt, IfStatement)
    assert isinstance(if_stmt.condition, Expression)
    assert len(if_stmt.body) == 1
    assert isinstance(if_stmt.body[0], VariableDeclaration)
    assert len(if_stmt.elif_clauses) == 0
    assert isinstance(if_stmt.else_clause, ElseClause)
    assert len(if_stmt.else_clause.body) == 1
    assert isinstance(if_stmt.else_clause.body[0], VariableDeclaration)


def test_if_elif_else_statement():
    """Tests parsing of an if-elif-else statement."""
    code = """if $x > 10$ do
      DEF y #int = 5
    elif $x == 10$ do
      DEF a #int = 1
    elif $x == 0$ do
      DEF a #int = 14
    else do
      DEF z #int = 10
    end"""
    ast = parse_to_ast(code)

    assert isinstance(ast, Program)
    assert len(ast.statements) == 1

    if_stmt = ast.statements[0]
    assert isinstance(if_stmt, IfStatement)
    assert isinstance(if_stmt.condition, Expression)
    assert len(if_stmt.body) == 1
    assert isinstance(if_stmt.body[0], VariableDeclaration)
    assert len(if_stmt.elif_clauses) == 2
    assert isinstance(if_stmt.elif_clauses[0], ElifClause)
    assert isinstance(if_stmt.elif_clauses[0].condition, Expression)
    assert len(if_stmt.elif_clauses[0].body) == 1
    assert isinstance(if_stmt.elif_clauses[0].body[0], VariableDeclaration)
    assert isinstance(if_stmt.else_clause, ElseClause)
    assert len(if_stmt.else_clause.body) == 1
    assert isinstance(if_stmt.else_clause.body[0], VariableDeclaration)


def test_empty_function_body():
    """Tests parsing of a function with an empty body."""
    code = """FUNC empty_func() #void
end"""
    ast = parse_to_ast(code)

    assert isinstance(ast, Program)
    assert len(ast.statements) == 1

    func_decl = ast.statements[0]
    assert isinstance(func_decl, FunctionDeclaration)
    assert func_decl.name.name == "empty_func"
    assert len(func_decl.parameters) == 0
    assert isinstance(func_decl.return_type, Type)
    assert func_decl.return_type.name == "void"
    assert len(func_decl.body) == 0


def test_function_no_params_no_return():
    """Tests parsing of a function with no parameters and no return type."""
    code = """FUNC simple_func() #void
  DEF x #int = 1
end"""
    ast = parse_to_ast(code)

    assert isinstance(ast, Program)
    assert len(ast.statements) == 1

    func_decl = ast.statements[0]
    assert isinstance(func_decl, FunctionDeclaration)
    assert func_decl.name.name == "simple_func"
    assert len(func_decl.parameters) == 0
    assert isinstance(func_decl.return_type, Type)
    assert func_decl.return_type.name == "void"
    assert len(func_decl.body) == 1
    assert isinstance(func_decl.body[0], VariableDeclaration)


def test_nested_if_statements():
    """Tests parsing of nested if statements."""
    code = """if $a > 10$ do
      if $b < 5$ do
        DEF result #int = 1
      end
    end"""
    ast = parse_to_ast(code)

    assert isinstance(ast, Program)
    assert len(ast.statements) == 1

    outer_if = ast.statements[0]
    assert isinstance(outer_if, IfStatement)
    assert len(outer_if.body) == 1

    inner_if = outer_if.body[0]
    assert isinstance(inner_if, IfStatement)
    assert len(inner_if.body) == 1
    assert isinstance(inner_if.body[0], VariableDeclaration)
    assert inner_if.body[0].name.name == "result"


def test_for_loop():
    """Tests parsing of a for loop."""
    code = """for DEF i #int in my_list do
        x := i
    end"""
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    for_stmt = ast.statements[0]
    assert isinstance(for_stmt, ForStatement)
    assert for_stmt.iterator_name.name == "i"
    assert for_stmt.iterator_type.name == "int"
    assert isinstance(for_stmt.collection, Identifier)
    assert for_stmt.collection.name == "my_list"
    assert len(for_stmt.body) == 1
    assert isinstance(for_stmt.body[0], VariableAssignment)


def test_while_loop():
    """Tests parsing of a while loop."""
    code = """while $x < 10$ do
        x := x + 1
    end"""
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    while_stmt = ast.statements[0]
    assert isinstance(while_stmt, WhileStatement)
    assert isinstance(while_stmt.condition, RelationalExpression)
    assert len(while_stmt.body) == 1
    assert isinstance(while_stmt.body[0], VariableAssignment)


def test_try_catch_finally():
    """Tests parsing of a try-catch-finally statement."""
    code = """TRY
        THROW "An error"
    CATCH e #Error do
        x := 1
    FINALLY do
        y := 2
    end"""
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    try_stmt = ast.statements[0]
    assert isinstance(try_stmt, TryStatement)
    assert len(try_stmt.body) == 1
    assert isinstance(try_stmt.body[0], ThrowStatement)
    assert len(try_stmt.catch_clauses) == 1
    catch_clause = try_stmt.catch_clauses[0]
    assert isinstance(catch_clause, CatchClause)
    assert catch_clause.exception_name.name == "e"
    assert catch_clause.exception_type.name == "Error"
    assert len(catch_clause.body) == 1
    assert isinstance(catch_clause.body[0], VariableAssignment)
    assert isinstance(try_stmt.finally_clause, FinallyClause)
    assert len(try_stmt.finally_clause.body) == 1
    assert isinstance(try_stmt.finally_clause.body[0], VariableAssignment)


def test_match_statement():
    """Tests parsing of a match statement."""
    code = """MATCH my_var
        CASE 1 do
            x := 1
        CASE n if $n % 2 <= 0$ do
            x := 2
        DEFAULT do
            x := 3
    end"""
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    match_stmt = ast.statements[0]
    assert isinstance(match_stmt, MatchStatement)
    assert isinstance(match_stmt.expression, Identifier)
    assert match_stmt.expression.name == "my_var"
    assert len(match_stmt.case_clauses) == 2
    case_clause = match_stmt.case_clauses[0]
    assert isinstance(case_clause, CaseClause)
    assert isinstance(case_clause.pattern, LiteralPattern)
    assert case_clause.pattern.literal.value == 1
    assert len(case_clause.body) == 1
    assert isinstance(case_clause.body[0], VariableAssignment)
    assert isinstance(match_stmt.default_clause, DefaultClause)
    assert len(match_stmt.default_clause.body) == 1
    assert isinstance(match_stmt.default_clause.body[0], VariableAssignment)


def test_spawn_statement():
    """Tests parsing of a spawn statement."""
    code = """SPAWN my_func()"""
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    expr_statement = ast.statements[0]
    assert isinstance(expr_statement, ExpressionStatement)
    spawn_stmt = expr_statement.expression
    assert isinstance(spawn_stmt, SpawnStatement)
    assert isinstance(spawn_stmt.expression, FunctionCall)
    assert spawn_stmt.expression.function_name.name == "my_func"


def test_function_call():
    """Tests parsing of a function call."""
    code = """my_func(param1, param2)"""
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    ast_stmt = ast.statements[0]
    assert isinstance(ast_stmt, ExpressionStatement)
    assert isinstance(ast_stmt.expression, FunctionCall)
    assert ast_stmt.expression.function_name.name == "my_func"
    assert isinstance(ast_stmt.expression.arguments, list)
    assert len(ast_stmt.expression.arguments) == 2
    assert isinstance(ast_stmt.expression.arguments[0], Identifier)
    assert ast_stmt.expression.arguments[0].name == "param1"
    assert isinstance(ast_stmt.expression.arguments[1], Identifier)
    assert ast_stmt.expression.arguments[1].name == "param2"


def test_import_statement():
    """Tests parsing of an import statement."""
    code = """import my_module.utils"""
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    import_stmt = ast.statements[0]
    assert isinstance(import_stmt, ImportStatement)
    assert import_stmt.dotted_name == "my_module.utils".split(".")


def test_type_declaration():
    """Tests parsing of a type declaration."""
    code = """TYPE MyType EXTENDS BaseType
        prop1 #int
        prop2 #str
    end"""
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    type_decl = ast.statements[0]
    assert isinstance(type_decl, TypeDeclaration)
    assert type_decl.name.name == "MyType"
    assert len(type_decl.type_body) == 2
    assert type_decl.type_body[0].name.name == "prop1"
    assert type_decl.type_body[0].field_type.name == "int"
    assert isinstance(type_decl.extends_clause, list)
    assert len(type_decl.extends_clause) == 1
    assert type_decl.extends_clause[0].name == "BaseType"


def test_class_declaration():
    """Tests parsing of a class declaration."""
    code = """CLASS MyClass EXTENDS OtherClass IMPLEMENTS MyInterface
        PUBLIC STATIC my_prop #int = 10
        PRIVATE CONSTRUCTOR(p1 #int)
        end
        PUBLIC OVERRIDE FUNC my_method() #void
        end
    end"""
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    class_decl = ast.statements[0]
    assert isinstance(class_decl, ClassDeclaration)
    assert class_decl.name.name == "MyClass"
    assert isinstance(class_decl.extends_clause, list)
    assert len(class_decl.extends_clause) == 1
    assert class_decl.extends_clause[0].name == "OtherClass"
    assert isinstance(class_decl.implements_clause, list)
    assert len(class_decl.implements_clause) == 1
    assert class_decl.implements_clause[0].name == "MyInterface"
    assert len(class_decl.body) == 3


def test_interface_declaration():
    """Tests parsing of an interface declaration."""
    code = """INTERFACE MyInterface
        FUNC my_method() #void
        FUNC other_method(p1 #int) #str
    end"""
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    interface_decl = ast.statements[0]
    assert isinstance(interface_decl, InterfaceDeclaration)
    assert interface_decl.name.name == "MyInterface"
    assert len(interface_decl.body) == 2
    assert interface_decl.body[0].name.name == "my_method"
    assert interface_decl.body[1].name.name == "other_method"


def test_array_literal():
    """Tests parsing of an array literal."""
    code = '[1, "hello", :T:]'
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    expr_stmt = ast.statements[0]
    assert isinstance(expr_stmt, ExpressionStatement)
    assert isinstance(expr_stmt.expression, ArrayLiteral)
    assert isinstance(expr_stmt.expression.elements, list)
    assert len(expr_stmt.expression.elements) == 3
    assert isinstance(expr_stmt.expression.elements[0], Literal)
    assert expr_stmt.expression.elements[0].value == 1
    assert isinstance(expr_stmt.expression.elements[2], Literal)
    assert expr_stmt.expression.elements[2].value is True


def test_map_literal():
    """Tests parsing of a map literal."""
    code = '{"a" -> 1, "b" -> 2}'
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    expr_stmt = ast.statements[0]
    assert isinstance(expr_stmt, ExpressionStatement)
    assert isinstance(expr_stmt.expression, MapLiteral)
    assert len(expr_stmt.expression.entries) == 2
    assert isinstance(expr_stmt.expression.entries[0], MapEntry)
    assert isinstance(expr_stmt.expression.entries[0].key, Literal)
    assert expr_stmt.expression.entries[0].key.value == "a"
    assert isinstance(expr_stmt.expression.entries[0].value, Literal)
    assert expr_stmt.expression.entries[0].value.value == 1


def test_object_literal():
    """Tests parsing of an object literal."""
    code = '{a: 1, b: "two"}'
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    expr_stmt = ast.statements[0]
    assert isinstance(expr_stmt, ExpressionStatement)
    assert isinstance(expr_stmt.expression, ObjectLiteral)
    assert len(expr_stmt.expression.entries) == 2
    assert expr_stmt.expression.entries[0].key.name == "a"


def test_empty_object_literal():
    """Tests parsing of an empty object literal."""
    code = "{_}"
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    expr_stmt = ast.statements[0]
    assert isinstance(expr_stmt, ExpressionStatement)
    assert isinstance(expr_stmt.expression, ObjectLiteral)
    assert len(expr_stmt.expression.entries) == 0


def test_tuple_literal():
    """Tests parsing of a tuple literal."""
    code = '(1, "two")'
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    expr_stmt = ast.statements[0]
    assert isinstance(expr_stmt, ExpressionStatement)
    assert isinstance(expr_stmt.expression, TupleLiteral)
    assert len(expr_stmt.expression.elements) == 2

    assert isinstance(expr_stmt.expression.elements[0], Literal)
    assert expr_stmt.expression.elements[0].value == 1


def test_lambda_expression():
    """Tests parsing of a lambda expression."""
    code = "FUNC (x #int) -> x * 2"
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    expr_stmt = ast.statements[0]
    assert isinstance(expr_stmt, ExpressionStatement)
    assert isinstance(expr_stmt.expression, LambdaExpression)
    assert isinstance(expr_stmt.expression.parameters, list)
    assert len(expr_stmt.expression.parameters) == 1
    assert isinstance(expr_stmt.expression.body, Expression)


def test_anonymous_function():
    """Tests parsing of an anonymous function."""
    code = "FUNC () #void\nDEF x #int = 10\nRETURN x\nend"
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    expr_stmt = ast.statements[0]
    assert isinstance(expr_stmt, ExpressionStatement)
    assert isinstance(expr_stmt.expression, AnonymousFunction)
    assert isinstance(expr_stmt.expression.parameters, list)
    assert len(expr_stmt.expression.parameters) == 0
    assert isinstance(expr_stmt.expression.body, list)


def test_method_call():
    """Tests parsing of a method call."""
    code = "my_obj:my_method:(a, c)"
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    expr_stmt = ast.statements[0]
    assert isinstance(expr_stmt, ExpressionStatement)
    assert isinstance(expr_stmt.expression, MethodCall)
    assert isinstance(expr_stmt.expression.base, Identifier)
    assert expr_stmt.expression.base.name == "my_obj"
    assert expr_stmt.expression.function_name.name == "my_method"
    assert isinstance(expr_stmt.expression.arguments, list)
    assert len(expr_stmt.expression.arguments) == 2


def test_property_access():
    """Tests parsing of a property access."""
    code = "my_obj.my_prop"
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    expr_stmt = ast.statements[0]
    assert isinstance(expr_stmt, ExpressionStatement)
    assert isinstance(expr_stmt.expression, PropertyAccess)
    assert isinstance(expr_stmt.expression.base, Identifier)
    assert expr_stmt.expression.base.name == "my_obj"
    assert expr_stmt.expression.property_name.name == "my_prop"


def test_array_access():
    """Tests parsing of an array access."""
    code = "my_array[0]"
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    expr_stmt = ast.statements[0]
    assert isinstance(expr_stmt, ExpressionStatement)
    assert isinstance(expr_stmt.expression, ArrayAccess)
    assert isinstance(expr_stmt.expression.base, Identifier)

    assert expr_stmt.expression.base.name == "my_array"
    assert isinstance(expr_stmt.expression.index, Literal)
    assert expr_stmt.expression.index.value == 0


def test_expression_statement():
    """Tests parsing of an expression statement."""
    code = "my_func()"
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    expr_stmt = ast.statements[0]
    assert isinstance(expr_stmt, ExpressionStatement)
    assert isinstance(expr_stmt.expression, FunctionCall)


def test_array_type():
    """Tests parsing of an array type."""
    code = "DEF my_array #[#int] = [1, 2, 3]"
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    var_decl = ast.statements[0]
    assert isinstance(var_decl, VariableDeclaration)
    assert isinstance(var_decl.var_type, ArrayType)
    assert var_decl.var_type.base_type.name == "int"


def test_map_type():
    """Tests parsing of a map type."""
    code = 'DEF my_map #{#str, #int} = {"a" -> 1}'
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    var_decl = ast.statements[0]
    assert isinstance(var_decl, VariableDeclaration)
    assert isinstance(var_decl.var_type, MapType)
    assert var_decl.var_type.key_type.name == "str"
    assert var_decl.var_type.value_type.name == "int"


def test_tuple_type():
    """Tests parsing of a tuple type."""
    code = 'DEF my_tuple #(#int, #str) = (1, "a")'
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    var_decl = ast.statements[0]
    assert isinstance(var_decl, VariableDeclaration)
    assert isinstance(var_decl.var_type, TupleType)
    assert len(var_decl.var_type.types) == 2
    assert var_decl.var_type.types[0].name == "int"


def test_pattern_matching_all_forms():
    """Tests parsing of all forms of pattern matching."""
    code = """MATCH my_var
        CASE 1 do x := 1
        CASE #int n if $n % 2 == 0$ do x := 2
        CASE [1, 2] do x := 3
        CASE {a: 1} do x := 4
        CASE {"a" -> 1} do x := 5
        CASE (1, 2) do x := 6
        DEFAULT do x := 7
    end"""
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    match_stmt = ast.statements[0]
    assert isinstance(match_stmt, MatchStatement)
    assert len(match_stmt.case_clauses) == 6
    assert isinstance(match_stmt.case_clauses[0].pattern, LiteralPattern)
    assert isinstance(match_stmt.case_clauses[1].pattern, TypedIdentifierPattern)
    assert isinstance(match_stmt.case_clauses[2].pattern, ArrayPattern)
    assert isinstance(match_stmt.case_clauses[3].pattern, ObjectPattern)
    assert isinstance(match_stmt.case_clauses[4].pattern, MapPattern)
    assert isinstance(match_stmt.case_clauses[5].pattern, TuplePattern)


def test_super_call():
    """Tests parsing of a SUPER() call."""
    code = "SUPER:(1,2)"
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    expr_stmt = ast.statements[0]
    assert isinstance(expr_stmt, ExpressionStatement)
    assert isinstance(expr_stmt.expression, SuperCall)
    assert isinstance(expr_stmt.expression.arguments, list)
    assert len(expr_stmt.expression.arguments) == 2
    assert isinstance(expr_stmt.expression.arguments[0], Literal)
    assert expr_stmt.expression.arguments[0].value == 1
    assert isinstance(expr_stmt.expression.arguments[1], Literal)
    assert expr_stmt.expression.arguments[1].value == 2


def test_float_literal():
    """Tests parsing of a float literal."""
    code = "DEF my_float #float = 3.14"
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    var_decl = ast.statements[0]
    assert isinstance(var_decl, VariableDeclaration)
    assert isinstance(var_decl.value, Literal)
    assert var_decl.value.value == 3.14


def test_or_expression():
    """Tests parsing of an OR expression."""
    code = "DEF result #bool = :T: || :F:"
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    var_decl = ast.statements[0]
    assert isinstance(var_decl, VariableDeclaration)
    assert isinstance(var_decl.value, OrExpression)
    assert isinstance(var_decl.value.left, Literal)
    assert var_decl.value.left.value is True
    assert isinstance(var_decl.value.right, Literal)
    assert var_decl.value.right.value is False
    assert var_decl.value.operator == "||"


def test_and_expression():
    """Tests parsing of an AND expression."""
    code = "DEF result #bool = :T: && :F:"
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    var_decl = ast.statements[0]
    assert isinstance(var_decl, VariableDeclaration)
    assert isinstance(var_decl.value, AndExpression)
    assert isinstance(var_decl.value.left, Literal)
    assert var_decl.value.left.value is True
    assert isinstance(var_decl.value.right, Literal)
    assert var_decl.value.right.value is False
    assert var_decl.value.operator == "&&"


def test_additive_expression():
    """Tests parsing of additive expressions."""
    code = """ DEF result #int = 1 + 2 - 3
    DEF thingy #str = "a" +   result + "b"
    """
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 2
    var_decl = ast.statements[0]
    assert isinstance(var_decl, VariableDeclaration)
    assert isinstance(var_decl.value, AdditiveExpression)
    assert isinstance(var_decl.value.left, AdditiveExpression)
    assert var_decl.value.operator == "-"
    assert isinstance(var_decl.value.right, Literal)
    assert var_decl.value.right.value == 3

    var_decl2 = ast.statements[1]
    assert isinstance(var_decl2, VariableDeclaration)


def test_multiplicative_expression():
    """Tests parsing of multiplicative expressions."""
    code = "DEF result #int = 1 * 2 / 3 % 4"
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    var_decl = ast.statements[0]
    assert isinstance(var_decl, VariableDeclaration)
    assert isinstance(var_decl.value, MultiplicativeExpression)
    assert isinstance(var_decl.value.left, MultiplicativeExpression)
    assert var_decl.value.operator == "%"
    assert isinstance(var_decl.value.right, Literal)
    assert var_decl.value.right.value == 4


def test_unary_expressions():
    """Tests parsing of unary expressions."""
    code = """DEF result #bool = !:T:
DEF num #int = -10
DEF pos_num #int = +5
"""
    ast = parse_to_ast(code)
    assert isinstance(ast, Program)
    assert len(ast.statements) == 3

    assert isinstance(ast.statements[0], VariableDeclaration)
    not_expr = ast.statements[0].value
    assert isinstance(not_expr, NotExpression)
    assert not_expr.operator == "!"
    assert isinstance(not_expr.expression, Literal)
    assert not_expr.expression.value is True
    assert isinstance(ast.statements[1], VariableDeclaration)

    minus_expr = ast.statements[1].value
    assert isinstance(minus_expr, UnaryMinusExpression)
    assert minus_expr.operator == "-"
    assert isinstance(minus_expr.expression, Literal)
    assert minus_expr.expression.value == 10
    assert isinstance(ast.statements[2], VariableDeclaration)

    plus_expr = ast.statements[2].value
    assert isinstance(plus_expr, UnaryPlusExpression)
    assert plus_expr.operator == "+"
    assert isinstance(plus_expr.expression, Literal)
    assert plus_expr.expression.value == 5


if __name__ == "__main__":
    pytest.main()
