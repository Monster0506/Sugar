from src.ast_nodes import *
from src.ast_nodes import SugarClass, SugarInstance
from src.builtin_operations import array_operations, map_operations, str_operations
from src.stdlib import library
from src.type_checker import TypeChecker


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

        if name in self.values:
            return self.values[name]
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise NameError(f"Undefined variable '{name}'.")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(values={self.values!r}, enclosing={self.enclosing!r})"


class Interpreter:
    def __init__(self):
        self.environment = Environment()
        self.return_value = None

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
            # self.environment.define(node.name, value, var_type)

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
                    property_decl = base_instance.sugar_class.properties.get(
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
        else:
            for elif_clause in node.elif_clauses:
                if self.visit(elif_clause.condition):
                    for statement in elif_clause.body:
                        self.visit(statement)
                    return
            if node.else_clause:
                for statement in node.else_clause.body:
                    self.visit(statement)

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

        functions = self.environment.get(func_name.name)

        if isinstance(functions, SugarClass):
            instance = SugarInstance(
                sugar_class=functions, environment=Environment(self.environment)
            )
            if functions.constructor:
                self._execute_function(functions.constructor, [], instance)
            return instance
            raise TypeError(f"{func_name} is not a function.")

        # Evaluate arguments once
        evaluated_args = (
            [self.visit(arg) for arg in node.arguments] if node.arguments else []
        )

        func_to_call = self._get_correct_function(functions, evaluated_args)

        if not func_to_call:
            raise TypeError(
                f"No matching function found for {func_name} with provided arguments."
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

    def visit_NotExpression(self, node: NotExpression):
        return self.visit_UnaryOperation(node)

    def _get_correct_function(self, funcs: list[Function], evaluated_args: list):
        if isinstance(funcs, list):
            for func in funcs:
                if len(evaluated_args) == len(func.params):
                    types_match = True
                    for i, param in enumerate(func.params):
                        # Use the type checker to compare the evaluated argument with the parameter type
                        if not self.environment.type_checker.is_assignable(
                            evaluated_args[i], param.param_type
                        ):
                            types_match = False
                            break
                    if types_match:
                        return func
            return None
        elif isinstance(funcs, SugarClass):
            return funcs
        else:
            raise TypeError(
                f"Expected a function or a class, but got {type(funcs).__name__}"
            )

    def _execute_function(self, func: Function, args: list, instance=None):
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

        return result

    def visit_MethodCall(self, node: MethodCall):
        base = self.visit(node.base)
        method_name = node.function_name.name

        evaluated_args = (
            [self.visit(arg) for arg in node.arguments] if node.arguments else []
        )
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

        can_use_array = isinstance(
            assumed_type, ArrayType
        ) or self.environment.type_checker.is_assignable(
            base, ArrayType(name="[dynamic]", base_type=None)
        )

        can_use_str = (
            isinstance(assumed_type, Type) and assumed_type.name == "str"
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
            return base.environment.get(node.property_name.name).value
        elif isinstance(base, dict) and isinstance(
            base.get(node.property_name.name, 0), StdLibCall
        ):
            return self._stdlib_call(base, node.property_name.name, [])
        else:
            raise TypeError(
                f"Cannot access property on non-instance type: {type(base).__name__}"
            )

    def visit_ThisAssignment(self, node: ThisAssignment):
        this_instance = self.environment.get("THIS")
        if not isinstance(this_instance, SugarInstance):
            raise TypeError(
                "'THIS' is not defined in the current scope or is not an instance."
            )

        value = self.visit(node.value)
        this_instance.environment.assign(node.property_name.name, value)

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

    def visit_MatchStatement(self, node: MatchStatement):
        expression = self.visit(node.expression)
        matched = None
        original_environment = self.environment
        for case_clause in node.case_clauses:
            self.environment = Environment(original_environment)
            if isinstance(case_clause.pattern, IdentifierPattern):
                self.environment.define(
                    case_clause.pattern.name.name,
                    expression,
                    self.environment.type_checker.get_runtime_type(expression),
                )
                pattern = self.visit(case_clause.pattern)
            else:
                pattern = self.visit(case_clause.pattern)
            guard = self.visit(case_clause.guard) if case_clause.guard else True
            if expression == pattern and guard:
                matched = case_clause
                break
        if not matched:
            if node.default_clause:
                for statement in node.default_clause.body:
                    self.visit(statement)
        else:
            for statement in matched.body:
                self.visit(statement)
        self.environment = original_environment

    def visit_LiteralPattern(self, node: LiteralPattern):
        return self.visit(node.literal)

    def visit_IdentifierPattern(self, node: IdentifierPattern):
        return self.visit(node.name)

    def visit_TuplePattern(self, node: TuplePattern):
        values = []
        for pattern in node.patterns:
            values.append(self.visit(pattern))
        return tuple(values)

    def visit_ArrayPattern(self, node: ArrayPattern):
        values = []
        for pattern in node.patterns if node.patterns else []:
            values.append(self.visit(pattern))
        return values

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

        sugar_class = SugarClass(node.name.name, methods, properties, constructor)

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

    def _stdlib_call(self, base, method_name, args):
        return base[method_name](*args)
