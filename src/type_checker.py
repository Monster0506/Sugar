from src.ast_nodes import ArrayType, CustomType, MapType, TupleType, Type


class TypeChecker:
    def __init__(self, environment=None):
        self.environment = environment
    def assert_type(self, value, expected_type):

        if isinstance(expected_type, ArrayType):
            return self._assert_array(value, expected_type)
        elif isinstance(expected_type, MapType):
            return self._assert_map(value, expected_type)
        elif isinstance(expected_type, TupleType):
            return self._assert_tuple(value, expected_type)
        elif isinstance(expected_type, Type):
            return self._assert_simple(value, expected_type)
        else:
            raise TypeError(f"Unknown type annotation: {expected_type}")

    def _assert_simple(self, value, expected_type: Type):
        type_map = {
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "char": str,
        }
        if expected_type.name not in type_map:
            return self._assert_custom_type(value, expected_type)

        if not isinstance(value, type_map[expected_type.name]):

            raise TypeError(
                f"Type mismatch: expected {expected_type.name}, got {type(value).__name__}"
            )

        if expected_type.name == "char" and len(value) != 1:
            raise TypeError("Character must be a single character string.")

        return True

    def _assert_array(self, value, expected_type: ArrayType):
        if not (isinstance(value, list)):
            raise TypeError(f"Expected an array, but got {type(value).__name__}")

        if expected_type.base_type is None:
            return True

        for item in value:
            self.assert_type(item, expected_type.base_type)

        return True

    def _assert_map(self, value, expected_type: MapType):
        if not isinstance(value, dict):
            raise TypeError(f"Expected a map, but got {type(value).__name__}")

        for k, v in value.items():
            self.assert_type(k, expected_type.key_type)
            self.assert_type(v, expected_type.value_type)

        return True

    def _assert_tuple(self, value, expected_type: TupleType):
        if not isinstance(value, tuple):
            raise TypeError(f"Expected a tuple, but got {type(value).__name__}")

        if len(value) != len(expected_type.types):
            raise TypeError(
                f"Tuple length mismatch: expected {len(expected_type.types)}, got {len(value)}"
            )

        for i, item in enumerate(value):
            self.assert_type(item, expected_type.types[i])

        return True

    def _assert_custom_type(self, value, expected_type: Type):
        if not self.environment:
            raise TypeError("Environment not set for type checker.")

        type_def = self.environment.get(expected_type.name)
        if not isinstance(type_def, CustomType):
            raise TypeError(f"Unknown type: {expected_type.name}")

        if not isinstance(value, dict):
            raise TypeError(f"Expected an object of type {expected_type.name}, but got {type(value).__name__}")

        type_fields = type_def.declaration.type_body
        if len(value) != len(type_fields):
            raise TypeError(f"Incorrect number of fields for type {expected_type.name}. Expected {len(type_fields)}, got {len(value)}")

        for field_def in type_fields:
            field_name = field_def.name.name
            if field_name not in value:
                raise TypeError(f"Missing field '{field_name}' in object of type {expected_type.name}")
            self.assert_type(value[field_name], field_def.field_type)

        return True

    def is_assignable(self, value, target_type: Type):
        if isinstance(value, list):
            if isinstance(target_type, ArrayType):
                return self._assert_array(value, target_type)
            else:
                return False  # A list cannot be assigned to a non-array type like str
        try:
            self.assert_type(value, target_type)
            return True
        except TypeError:
            return False

    def __repr__(self) -> str:
        attrs: str = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"

    def get_runtime_type(self, value) -> Type:
        """
        Infers the AST Type object from a Python runtime value.
        """
        if isinstance(value, int):
            return Type("int")
        elif isinstance(value, float):
            return Type("float")
        elif isinstance(value, str):
            if len(value) == 1:
                return Type("char")
            return Type("str")
        elif isinstance(value, bool):
            return Type("bool")
        elif isinstance(value, list):
            # For lists, try to determine the base type if possible
            if not value:  # Empty list
                return ArrayType(name="[]", base_type=Type("dynamic"))  # Or Type("any")

            # Try to find a common base type for all elements
            first_element_type = self.get_runtime_type(value[0])
            all_same_type = True
            for item in value:
                if not self.is_assignable(item, first_element_type):
                    all_same_type = False
                    break

            if all_same_type:
                return ArrayType(
                    name=f"[{first_element_type.name}]", base_type=first_element_type
                )
            else:
                raise TypeError("All list values must be of same type")
        elif isinstance(value, dict):
            # For maps, infer key and value types
            if not value:
                return MapType(
                    name="{}", key_type=Type("dynamic"), value_type=Type("dynamic")
                )

            # Take the first key-value pair as a hint, or iterate for a common type
            first_key, first_value = next(iter(value.items()))
            key_type = self.get_runtime_type(first_key)
            value_type = self.get_runtime_type(first_value)

            # You might want to do a more robust common type inference here for complex scenarios
            return MapType(
                name=f"{{{key_type.name},{value_type.name}}}",
                key_type=key_type,
                value_type=value_type,
            )
        # elif isinstance(value, tuple):
        #     # For tuples, infer types for each element
        #     element_types = [self.get_runtime_type(item) for item in value]
        #     return TupleType(
        #         name=f"({', '.join(t.name for t in element_types)})",
        #         types=element_types,
        #     )
        elif value is None:
            return Type("null")  # Assuming you have a 'null' or 'None' type
        elif callable(value):  # For functions, lambdas, etc.
            return Type("function")
        else:

            raise TypeError("Could not infer runtime type")
