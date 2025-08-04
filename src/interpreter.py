from pathlib import Path

from src.ast_nodes import *
from src.ast_nodes import SugarClass, SugarError, SugarInstance
from src.builtins import (
    all_operations,
    array_operations,
    base_errors,
    map_operations,
    standard_functions,
    str_operations,
    task_operations,
    token_operations,
)
from src.parser import parse_to_ast
from src.stdlib import library
from src.type_checker import TypeChecker
from src.utils import debug_class_wrapper


@debug_class_wrapper
class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing
        self.type_checker = TypeChecker(self)

    def define(self, name, value, var_type: Type):
        if name in library:
            raise TypeError(f"Cannot define the built-in module {name}")
        if isinstance(value, Function):

            if name in self.values.keys() and self.values[name]:
                # Check for duplicate function signatures
                if isinstance(self.values[name], list):
                    for existing_func in self.values[name]:
                        if isinstance(existing_func, Function):
                            if len(existing_func.params) == len(value.params):
                                is_duplicate = True
                                for i, new_param in enumerate(value.params):
                                    if (
                                        existing_func.params[i].param_type.name
                                        != new_param.param_type.name
                                    ):
                                        is_duplicate = False
                                        break
                                if is_duplicate:
                                    raise TypeError(
                                        f"Duplicate function overload for '{name}' with "
                                        f"parameters ({', '.join([p.param_type.name for p in value.params])})"
                                    )
                self.values[name].append(value)
            else:
                self.values[name] = [value]
        elif isinstance(value, CustomType):
            self.values[name] = value
        elif isinstance(value, SugarClass):
            self.values[name] = value
        elif isinstance(value, InterfaceDeclaration):
            self.values[name] = value
        else:
            if var_type is not None:
                self.type_checker.assert_type(value, var_type)
            self.values[name] = Variable(value, var_type)

    def assign(self, name, value):
        if name in library:
            raise TypeError(f"Cannot reassign the built-in module {name}")

        if name in self.values:
            if isinstance(self.values[name], Variable):
                self.type_checker.assert_type(value, self.values[name].var_type)
                self.values[name] = Variable(value, self.values[name].var_type)
            else:
                raise TypeError(f"Cannot assign to function '{name}'.")
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        raise NameError(f"Undefined variable '{name}'.")

    def get(self, name):
        if name in library:
            return library.get(name)
        if name in base_errors:
            return base_errors.get(name)

        if name in self.values:
            return self.values[name]
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise NameError(f"Undefined variable '{name}'.")

    def merge(self, other, import_name=None):
        for name, value in other.values.items():
            if import_name is None or name == import_name:
                if isinstance(value, Variable):
                    if name not in self.values:
                        self.define(name, value.value, value.var_type)
                        break
                elif isinstance(value, SugarClass):
                    if name not in self.values:
                        self.values[name] = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(values={self.values!r}, enclosing={self.enclosing!r})"


@debug_class_wrapper
class Interpreter:
    def __init__(self, run_path=None):
        self.environment = Environment()
        for error in base_errors:
            self.environment.define(error, CustomType(declaration=None), SugarError)
        self.environment.define("Task", CustomType(None), None)
        self.environment.define("Token", CustomType(None), None)
        self.return_value = None
        self.current_class = None
        self.run_path = run_path

    def interpret(self, program: Program):
        for statement in program.statements:
            self.visit(statement)

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"

        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, method_name):
        raise NotImplementedError(f"generic_visit called to {method_name}")

    def visit_Identifier(self, node: Identifier):
        name = node.name
        value = self.environment.get(name)
        if isinstance(value, Variable):
            return value.value
        return value

    def visit_VariableDeclaration(self, node: VariableDeclaration):
        value = self.visit(node.value)
        var_type = node.var_type
        if isinstance(node.name, Identifier):
            self.environment.define(node.name.name, value, var_type)
        elif isinstance(node.name, PropertyAccess):
            base = self.visit(node.name.base)
            if isinstance(base, SugarInstance):
                prop_name = node.name.property_name.name
                base.environment.define(prop_name, value, var_type)
            else:
                raise TypeError("Cannot declare a property on a non-instance.")
        elif isinstance(node.name, PropertyDeclaration):
            self.visit(node.name)

    def visit_ArrayLiteral(self, node: ArrayLiteral):
        values = (
            [self.visit(element) for element in node.elements] if node.elements else []
        )
        return values

    def visit_TupleLiteral(self, node: ArrayLiteral):
        values = (
            [self.visit(element) for element in node.elements] if node.elements else []
        )
        return tuple(values)

    def visit_MapLiteral(self, node: MapLiteral):
        values = {}
        if node.entries:
            for entry in node.entries:
                value = self.visit(entry)
                values.update(value)
        return values

    def visit_MapEntry(self, node: MapEntry) -> dict:
        return {self.visit(node.key): self.visit(node.value)}

    def visit_VariableAssignment(self, node: VariableAssignment):
        value = self.visit(node.value)
        if isinstance(node.name, PropertyAccess):
            base_instance = self.visit(node.name.base)
            if isinstance(base_instance, SugarInstance):
                property_name = node.name.property_name.name
                # Check if the property already exists in the instance's environment
                try:
                    base_instance.environment.get(property_name)
                    base_instance.environment.assign(property_name, value)
                except NameError:
                    property_decl = base_instance.sugar_class.find_property(
                        property_name
                    )
                    if property_decl:
                        base_instance.environment.define(
                            property_name, value, property_decl.property_type
                        )
                    else:
                        raise NameError(
                            f"Undefined property '{property_name}' on instance of '{base_instance.sugar_class.name}'."
                        )
            else:
                raise TypeError(
                    f"Cannot assign to property of non-instance type: {type(base_instance).__name__}"
                )
        else:
            self.environment.assign(node.name.name, value)

    def visit_ExpressionStatement(self, node: ExpressionStatement):
        return self.visit(node.expression)

    def visit_Literal(self, node: Literal):
        return node.value

    def visit_BinaryOperation(self, node: BinaryOperation):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(left, Exception):
            left = left.args[0]
        if isinstance(right, Exception):
            right = right.args[0]

        if node.operator == "+":
            return left + right
        elif node.operator == "-":
            return left - right
        elif node.operator == "*":
            return left * right
        elif node.operator == "/":
            return left / right
        elif node.operator == "%":
            return left % right
        elif node.operator == "==":
            return left == right
        elif node.operator == "!=":
            return left != right
        elif node.operator == ">":
            return left > right
        elif node.operator == "<":
            return left < right
        elif node.operator == ">=":
            return left >= right
        elif node.operator == "<=":
            return left <= right
        elif node.operator == "&&":
            return left and right
        elif node.operator == "||":
            return left or right

    def visit_MultiplicativeExpression(self, node: MultiplicativeExpression):
        return self.visit_BinaryOperation(node)

    def visit_AndExpression(self, node: AndExpression):
        return self.visit_BinaryOperation(node)

    def visit_OrExpression(self, node: OrExpression):
        return self.visit_BinaryOperation(node)

    def visit_RelationalExpression(self, node: RelationalExpression):
        return self.visit_BinaryOperation(node)

    def visit_IfStatement(self, node: IfStatement):
        if self.visit(node.condition):
            for statement in node.body:
                self.visit(statement)
                if self.return_value is not None:
                    return
        else:
            for elif_clause in node.elif_clauses:
                if self.visit(elif_clause.condition):
                    for statement in elif_clause.body:
                        self.visit(statement)
                        if self.return_value is not None:
                            break
                    return
            if node.else_clause:
                for statement in node.else_clause.body:
                    self.visit(statement)
                    if self.return_value is not None:
                        break

    def visit_ForStatement(self, node: ForStatement):
        collection = self.visit(node.collection)
        original_environment = self.environment
        for element in collection:
            self.environment = Environment(original_environment)
            self.environment.define(
                node.iterator_name.name, element, node.iterator_type
            )
            for statement in node.body:
                self.visit(statement)
                if self.return_value is not None:
                    break
            if self.return_value is not None:
                break
        self.environment = original_environment

    def visit_WhileStatement(self, node: WhileStatement):
        original_environment = self.environment
        while self.visit(node.condition):
            self.environment = Environment(original_environment)
            for statement in node.body:
                self.visit(statement)
        self.environment = original_environment

    def visit_FunctionDeclaration(self, node: FunctionDeclaration):
        func = Function(node.parameters, node.body, node.return_type)
        self.environment.define(node.name.name, func, node.return_type)

    def visit_FunctionCall(self, node: FunctionCall):
        if not node.base:
            func_name = node.function_name

        evaluated_args = (
            [self.visit(arg) for arg in node.arguments] if node.arguments else []
        )
        if func_name.name in standard_functions:
            result = standard_functions.get(func_name.name)(*evaluated_args)
            return result

        functions = self.environment.get(func_name.name)

        if isinstance(functions, SugarClass):
            instance = SugarInstance(
                sugar_class=functions, environment=Environment(self.environment)
            )
            if functions.constructor:
                self._execute_function(functions.constructor, evaluated_args, instance)
            return instance
        elif isinstance(functions, CustomType):
            instance = SugarInstance(
                sugar_class=functions, environment=Environment(self.environment)
            )
            for field, arg in zip(functions.declaration.type_body, evaluated_args):
                instance.environment.define(field.name.name, arg, field.field_type)
            return instance
        if isinstance(functions, SugarError):
            return functions

        func_to_call = self._get_correct_function(functions, evaluated_args)

        if not func_to_call:
            raise TypeError(
                f"No matching function found for {func_name.name} with provided arguments."
            )

        return self._execute_function(func_to_call, evaluated_args)

    def visit_ReturnStatement(self, node: ReturnStatement):
        self.return_value = self.visit(node.value)

    def visit_AdditiveExpression(self, node: AdditiveExpression):
        return self.visit_BinaryOperation(node)

    def visit_EqualityExpression(self, node: EqualityExpression):
        return self.visit_BinaryOperation(node)

    def visit_UnaryOperation(self, node: UnaryOperation):
        value = self.visit(node.expression)
        if node.operator == "!":
            return not value
        if node.operator == "-":
            return -value
        if node.operator == "+":
            return +value

    def visit_UnaryMinusExpression(self, node: UnaryMinusExpression):
        return self.visit_UnaryOperation(node)

    def visit_UnaryPlusExpression(self, node: UnaryPlusExpression):
        return self.visit_UnaryOperation(node)

    def visit_NotExpression(self, node: NotExpression):
        return self.visit_UnaryOperation(node)

    def _get_correct_function(self, funcs: list[Function], evaluated_args: list):
        if isinstance(funcs, list):
            for func in funcs:
                if len(evaluated_args) == len(func.params):
                    types_match = True
                    for i, param in enumerate(func.params):
                        if not self.environment.type_checker.is_assignable(
                            evaluated_args[i], param.param_type
                        ):
                            types_match = False
                            break
                    if types_match:
                        return func
            return None
        elif isinstance(funcs, SugarClass) or isinstance(funcs, CustomType):
            return funcs
        else:
            raise TypeError(
                f"Expected a function or a class, but got {type(funcs).__name__}"
            )

    def _execute_function(self, func: Function, args: list, instance=None):
        previous_class = self.current_class
        if instance:
            self.current_class = instance.sugar_class

        calling_environment = self.environment
        self.environment = Environment(calling_environment)
        if instance:
            self.environment.define("THIS", instance, None)

        for param, arg_value in zip(func.params, args):
            self.environment.define(param.name.name, arg_value, param.param_type)

        for statement in func.body:
            self.visit(statement)
            if self.return_value is not None:
                break

        result = self.return_value
        self.return_value = None
        self.environment = calling_environment
        self.current_class = previous_class

        return result

    def visit_MethodCall(self, node: MethodCall):
        base = self.visit(node.base)
        method_name = node.function_name.name

        evaluated_args = (
            [self.visit(arg) for arg in node.arguments] if node.arguments else []
        )

        if isinstance(base, tuple) and base[0] == "SUPER_CALL":
            this_instance = base[1]
            superclass = this_instance.sugar_class.superclass
            if superclass and method_name in superclass.methods:
                method = superclass.methods[method_name]
                return self._execute_function(method, evaluated_args, this_instance)
            else:
                raise AttributeError(
                    f"Method '{method_name}' not found on superclass of {this_instance.sugar_class.name}"
                )

        if isinstance(base, SugarTask):
            if method_name in task_operations:
                return task_operations.get(method_name)(base, *evaluated_args)
            else:
                raise AttributeError(f"Task object has no attribute '{method_name}'")
        if isinstance(
            base, CancellationToken
        ):  # Assuming CancellationToken is your Python class
            if method_name in token_operations:  # Use your new token_operations dict
                return token_operations.get(method_name)(base, *evaluated_args)
            else:
                raise AttributeError(f"Token object has no attribute '{method_name}'")
        if isinstance(base, SugarInstance):
            if method_name in base.sugar_class.methods:
                method = base.sugar_class.methods[method_name]
                return self._execute_function(method, evaluated_args, base)
            else:
                raise AttributeError(
                    f"Method '{method_name}' not found on instance of {base.sugar_class.name}"
                )

        if isinstance(base, dict):
            if len(base.keys()) > 0 and isinstance(
                base[list(base.keys())[0]], StdLibCall
            ):
                return self._stdlib_call(base, method_name, evaluated_args)

        assumed_type = self.environment.type_checker.get_runtime_type(base)

        if method_name in all_operations:
            operation = all_operations[method_name]

            new_value = operation(base, *evaluated_args)
            return new_value

        can_use_array = isinstance(
            assumed_type, ArrayType
        ) or self.environment.type_checker.is_assignable(
            base, ArrayType(name="[dynamic]", base_type=None)
        )

        can_use_str = (
            (isinstance(assumed_type, Type) and assumed_type.name == "char")
            or (isinstance(assumed_type, Type) and assumed_type.name == "str")
        ) or self.environment.type_checker.is_assignable(base, Type("str"))

        can_use_map = isinstance(
            assumed_type, MapType
        ) or self.environment.type_checker.is_assignable(
            base,
            MapType(
                name="{dynamic, dynamic}",
                key_type=Type("dynamic"),
                value_type=Type("dynamic"),
            ),
        )

        if can_use_str and method_name in str_operations.keys():
            operation = str_operations[method_name]

            new_value = operation(base, *evaluated_args)
            return new_value

        elif can_use_array and method_name in array_operations.keys():
            operation = array_operations[method_name]

            if method_name in ["ADD", "INSERT", "REMOVE", "REVERSE"]:
                operation(base, *evaluated_args)
                return None
            else:
                result = operation(base, *evaluated_args)
                return result
        elif can_use_map and method_name in map_operations.keys():
            operation = map_operations[method_name]

            new_value = operation(base, *evaluated_args)
            return new_value
        elif isinstance(base, SugarClass):
            if method_name in base.methods:
                return self._execute_function(base.methods[method_name], evaluated_args)
        else:
            raise NotImplementedError(
                f"Method '{method_name}' is not implemented for this type {assumed_type}"
            )

    def visit_PropertyAccess(self, node: PropertyAccess):
        base = self.visit(node.base)
        if isinstance(base, SugarInstance):
            prop_name = node.property_name.name
            if isinstance(base.sugar_class, SugarClass):
                prop_decl = base.sugar_class.find_property(prop_name)

                if (
                    prop_decl
                    and prop_decl.access_modifier
                    and prop_decl.access_modifier.modifier == "PRIVATE"
                ):
                    if (
                        self.current_class is None
                        or self.current_class.name != base.sugar_class.name
                    ):
                        raise TypeError(
                            f"Cannot access private property '{prop_name}' from outside its class."
                        )

            return base.environment.get(prop_name).value
        elif isinstance(base, dict) and isinstance(
            base.get(node.property_name.name, 0), StdLibCall
        ):
            return self._stdlib_call(base, node.property_name.name, [])
        elif isinstance(base, Exception):
            property_name = node.property_name.name
            if hasattr(base, property_name):
                # Access the attribute directly
                if property_name == "args" and isinstance(
                    getattr(base, property_name), tuple
                ):
                    if getattr(base, property_name):  # Check if the tuple is not empty
                        result = getattr(base, property_name)[0]
                    else:
                        result = None  # Or handle empty args as appropriate
                else:
                    result = getattr(base, property_name)
                return result
            else:
                raise ValueError(
                    f"Error: Exception object does not have a '{property_name}' attribute."
                )
        else:
            raise TypeError(
                f"Cannot access property on non-instance type: {type(base).__name__}"
            )

    def visit_ThisAssignment(self, node: ThisAssignment):
        this_variable = self.environment.get("THIS")
        this_instance = (
            this_variable.value
            if isinstance(this_variable, Variable)
            else this_variable
        )
        if not isinstance(this_instance, SugarInstance):
            raise TypeError(
                "'THIS' is not defined in the current scope or is not an instance."
            )

        value = self.visit(node.value)
        this_instance.environment.assign(node.property_name.name, value)

    def visit_ThisExpression(self, node):
        this_variable = self.environment.get("THIS")
        this_instance = (
            this_variable.value
            if isinstance(this_variable, Variable)
            else this_variable
        )
        if not isinstance(this_instance, SugarInstance):
            raise TypeError(
                "'THIS' is not defined in the current scope or is not an instance."
            )
        return this_instance

    def visit_LambdaExpression(self, node: LambdaExpression):

        def lambda_func(*args):
            calling_environment = self.environment
            self.environment = Environment(calling_environment)

            for param, arg_value in zip(
                node.parameters if node.parameters else [], args
            ):
                self.environment.define(param.name.name, arg_value, param.param_type)

            result = self.visit(node.body)

            self.environment = calling_environment
            return result

        return lambda_func

    def visit_AnonymousFunction(self, node: AnonymousFunction):
        def anon_func(*args):
            calling_environment = self.environment
            self.environment = Environment(calling_environment)

            for param, arg_value in zip(
                node.parameters if node.parameters else [], args
            ):
                self.environment.define(param.name.name, arg_value, param.param_type)

            for statement in node.body:
                self.visit(statement)
                if self.return_value is not None:
                    break

            result = self.return_value
            self.return_value = None

            self.environment = calling_environment
            return result

        return anon_func

    def _match(self, value, pattern, env: Environment):
        if isinstance(pattern, LiteralPattern):
            return self._match_literal_pattern(value, pattern)
        elif isinstance(pattern, TypedIdentifierPattern):
            return self._match_typed_identifier_pattern(value, pattern, env)
        elif isinstance(pattern, TuplePattern):
            return self._match_tuple_pattern(value, pattern, env)
        elif isinstance(pattern, ArrayPattern):
            return self._match_array_pattern(value, pattern, env)
        elif isinstance(pattern, MapPattern):
            return self._match_map_pattern(value, pattern, env)
        elif isinstance(pattern, IdentifierPattern):
            return self._match_identifier_pattern(value, pattern, env)
        else:
            return value == self.visit(pattern)

    def _match_literal_pattern(self, value, pattern: LiteralPattern):
        return value == self.visit(pattern.literal)

    def visit_LiteralPattern(self, node: LiteralPattern):
        return self.visit(node.literal)

    def _match_typed_identifier_pattern(
        self, value, pattern: TypedIdentifierPattern, env: Environment
    ):
        if self.environment.type_checker.is_assignable(value, pattern.var_type):
            env.define(pattern.name.name, value, pattern.var_type)
            return True
        return False

    def _match_tuple_pattern(self, value, pattern: TuplePattern, env: Environment):
        if not isinstance(value, tuple) or len(value) != len(pattern.patterns):
            return False
        for val, p in zip(value, pattern.patterns):
            if not self._match(val, p, env):
                return False
        return True

    def _match_array_pattern(self, value, pattern: ArrayPattern, env: Environment):
        if not isinstance(value, list) or len(value) != len(pattern.patterns):
            return False
        for val, p in zip(value, pattern.patterns):
            if not self._match(val, p, env):
                return False
        return True

    def _match_map_pattern(self, value, pattern: MapPattern, env: Environment):
        if not isinstance(value, dict) or len(value) != len(pattern.entries):
            return False
        for entry in pattern.entries:
            k = self.visit(entry.key)
            if k not in value:
                return False
            if not self._match(value[k], entry.value, env):
                return False
        return True

    def _match_identifier_pattern(
        self, value, pattern: IdentifierPattern, env: Environment
    ):
        env.define(
            pattern.name.name,
            value,
            self.environment.type_checker.get_runtime_type(value),
        )
        return True

    def visit_MatchStatement(self, node: MatchStatement):
        expression = self.visit(node.expression)
        matched = False
        original_environment = self.environment

        for case_clause in node.case_clauses:
            case_environment = Environment(original_environment)
            if self._match(expression, case_clause.pattern, case_environment):
                guard = True
                if case_clause.guard:
                    self.environment = case_environment
                    guard = self.visit(case_clause.guard)
                    self.environment = original_environment

                if guard:
                    self.environment = case_environment
                    for statement in case_clause.body:
                        self.visit(statement)
                    self.environment = original_environment
                    matched = True
                    break

        if not matched and node.default_clause:
            for statement in node.default_clause.body:
                self.visit(statement)

    def visit_ObjectLiteral(self, node: ObjectLiteral):
        obj = {}
        for entry in node.entries:
            key = entry.key.name
            value = self.visit(entry.value)
            obj[key] = value
        return obj

    def visit_TypeDeclaration(self, node: TypeDeclaration):
        custom_type = CustomType(declaration=node)
        self.environment.define(node.name.name, custom_type, None)

    def visit_ClassDeclaration(self, node: ClassDeclaration):
        methods = {}
        properties = {}
        constructor = None
        superclass = None

        if node.extends_clause:
            superclass_name = node.extends_clause[0].name
            superclass = self.environment.get(superclass_name)
            if not isinstance(superclass, SugarClass):
                raise TypeError(f"{superclass_name} is not a class.")

        for member in node.body:
            if isinstance(member, MethodDeclaration):
                func = Function(
                    member.parameters,
                    member.body,
                    member.return_type,
                    member.is_static,
                    member.is_override,
                )
                methods[member.name.name] = func
            elif isinstance(member, ConstructorDeclaration):
                constructor = Function(member.parameters, member.body, None)
            elif isinstance(member, PropertyDeclaration):
                properties[member.name.name] = member

        sugar_class = SugarClass(
            node.name.name, methods, properties, constructor, superclass
        )

        if node.implements_clause:
            for interface_name in node.implements_clause:
                interface = self.environment.get(interface_name.name)
                if not isinstance(interface, InterfaceDeclaration):
                    raise TypeError(f"{interface_name.name} is not an interface.")
                for method in interface.body:
                    if method.name.name not in sugar_class.methods:
                        raise TypeError(
                            f"Class {sugar_class.name} does not implement method {method.name.name} from interface {interface.name.name}"
                        )

        self.environment.define(node.name.name, sugar_class, None)

    def visit_InterfaceDeclaration(self, node: InterfaceDeclaration):
        self.environment.define(node.name.name, node, None)

    def visit_SuperCall(self, node: SuperCall):
        this_variable = self.environment.get("THIS")
        this_instance = (
            this_variable.value
            if isinstance(this_variable, Variable)
            else this_variable
        )

        if not isinstance(this_instance, SugarInstance):
            raise TypeError(
                "'THIS' is not defined in the current scope or is not an instance."
            )

        superclass = this_instance.sugar_class.superclass
        if not superclass:
            raise TypeError("Class does not have a superclass.")

        if node.arguments is not None:
            evaluated_args = (
                [self.visit(arg) for arg in node.arguments] if node.arguments else []
            )
            if superclass.constructor:
                return self._execute_function(
                    superclass.constructor, evaluated_args, this_instance
                )
            return None

        return ("SUPER_CALL", this_instance)

    def _stdlib_call(self, base, method_name, args):
        return base[method_name](*args)

    def visit_Type(self, node: Type):
        return node.name

    def visit_ThrowStatement(self, node: ThrowStatement):

        exception = self.visit(node.exception)

        if isinstance(exception, SugarError):
            arguments = node.exception.arguments
            final_sugar_error = self._construct_sugarError(exception, arguments)
            final_sugar_error.trigger()
        elif isinstance(exception, SugarInstance):
            if not isinstance(exception.sugar_class, CustomType):
                raise TypeError("Should be sending a custom error type")
            custom_error_definition = exception.sugar_class.declaration
            error_instance_values = exception.environment.values
            if (
                not isinstance(custom_error_definition.extends_clause, list)
                or len(custom_error_definition.extends_clause) != 1
                or not isinstance(custom_error_definition.extends_clause[0], Identifier)
            ):
                raise TypeError(
                    "Custom errors require at most one inherit from a base exception type"
                )

            base_exception_name = custom_error_definition.extends_clause[0].name
            python_base_exception_class = base_errors.get(
                base_exception_name,
                SugarError(Exception),
            )

            constructor_args = [
                Literal(var.value) for var in error_instance_values.values()
            ]
            final_sugar_error = self._construct_sugarError(
                python_base_exception_class, constructor_args
            )
            final_sugar_error.trigger()

        elif isinstance(exception, Exception):
            raise exception
        else:
            # Fallback if `self.visit` returns something unexpected
            raise TypeError(
                f"Unhandled exception type for throw statement: {type(exception)}"
            )
        raise Exception(exception)

    def _resolve_exception_base_name(self, exception_type: Type) -> str | None:
        """
        Resolves the true base exception name for a given declared exception type.
        This handles both direct base errors and custom types that extend base errors.
        """
        if not isinstance(exception_type, Type):
            return None

        clause_type_name = exception_type.name

        # Check if it's a known base error or a SugarError instance
        sugar_error_or_name = base_errors.get(clause_type_name)
        if sugar_error_or_name:
            if isinstance(sugar_error_or_name, SugarError):
                return sugar_error_or_name.base_class_name
            else:  # Assume it's already the name string
                return sugar_error_or_name

        # If not a direct base error, check if it's a custom type that extends a base error
        thingy = self.environment.get(clause_type_name)
        if isinstance(thingy, CustomType):
            if (
                thingy.declaration
                and thingy.declaration.extends_clause
                and thingy.declaration.extends_clause[0]
            ):
                extends_name = thingy.declaration.extends_clause[0].name
                sugar_error_or_name = base_errors.get(extends_name)
                if sugar_error_or_name:
                    if isinstance(sugar_error_or_name, SugarError):
                        return sugar_error_or_name.base_class_name
                    else:
                        return sugar_error_or_name
        return None

    def visit_TryStatement(self, node: TryStatement):
        original_environment = self.environment

        try:
            for statement in node.body:
                self.visit(statement)
        except Exception as caught:
            caught_exception_name = type(caught).__name__

            match_found_and_handled = False
            for catch_clause in node.catch_clauses:
                resolved_base_error_name = self._resolve_exception_base_name(
                    catch_clause.exception_type
                )

                is_direct_match = (
                    caught_exception_name == catch_clause.exception_type.name
                )
                is_resolved_base_match = (
                    resolved_base_error_name
                    and caught_exception_name == resolved_base_error_name
                )

                if is_direct_match or is_resolved_base_match:
                    if catch_clause.exception_name:
                        self.environment = Environment(original_environment)

                        custom_error_type = self.environment.get(
                            catch_clause.exception_type.name
                        )

                        if isinstance(custom_error_type, CustomType):
                            error_instance = SugarInstance(
                                sugar_class=custom_error_type,
                                environment=Environment(self.environment),
                            )
                            message = caught.args[0] if caught.args else ""

                            message_field_name = next(
                                (
                                    field.name.name
                                    for field in custom_error_type.declaration.type_body
                                    if field.field_type.name == "str"
                                ),
                                None,
                            )
                            if message_field_name:
                                error_instance.environment.define(
                                    message_field_name, message, Type(name="str")
                                )

                            self.environment.define(
                                catch_clause.exception_name.name,
                                error_instance,
                                catch_clause.exception_type,
                            )
                        else:
                            self.environment.define(
                                catch_clause.exception_name.name,
                                caught,
                                catch_clause.exception_type,
                            )

                    for statement in catch_clause.body:
                        self.visit(statement)

                    self.environment = original_environment
                    match_found_and_handled = True
                    break

            if not match_found_and_handled:
                raise caught

        finally:
            if node.finally_clause:
                for statement in node.finally_clause.body:
                    self.visit(statement)

    def _construct_sugarError(self, exception, arguments):
        evaluated_args = [self.visit(arg) for arg in arguments] if arguments else []
        final_sugar_error = SugarError(exception.base_class, evaluated_args)
        return final_sugar_error

    def visit_SpawnStatement(self, node: SpawnStatement):
        func_node = node.expression
        task = SugarTask(func_node, self.environment, self.run_path)
        task.start()
        return task

    def visit_ImportStatement(self, node: ImportStatement):
        paths = node.dotted_name
        saved_env = self.environment
        content = ""
        module_path = f"{paths[0]}.sugar"
        if isinstance(self.run_path, Path):
            parent = self.run_path.parent
            module_path = f"{parent}/{module_path}"

        with open(module_path, "r") as f:
            content = f.read()
        parsed = parse_to_ast(content)
        self.environment = Environment()
        self.interpret(parsed)
        parser_environment = self.environment
        self.environment = saved_env
        if len(paths) == 1:
            self.environment.merge(parser_environment)
        else:
            self.environment.merge(parser_environment, paths[1])
