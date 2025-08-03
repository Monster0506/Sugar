from src.ast_nodes import (
    ArrayType,
    CancellationToken,
    CustomType,
    MapType,
    SugarClass,
    SugarInstance,
    SugarTask,
    TupleType,
    Type,
)


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
            # Check if it's a SugarClass type
            if (
                self.environment
                and expected_type.name in self.environment.values
                and isinstance(self.environment.values[expected_type.name], SugarClass)
            ):
                return self._assert_sugar_class(
                    value, self.environment.values[expected_type.name]
                )
            return self._assert_simple(value, expected_type)
        else:
            raise TypeError(f"Unknown type annotation: {expected_type}")

    def _assert_simple(self, value, expected_type: Type):
        if expected_type.name == "Task":
            if not isinstance(value, SugarTask):
                raise TypeError(f"Expected Task, got {type(value).__name__}")
            return True
        if expected_type.name == "Token":
            if not isinstance(value, CancellationToken):
                raise TypeError(f"Expected Token, got {type(value).__name__}")
            return True

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

    def _assert_sugar_class(self, value, expected_class: SugarClass):
        if not isinstance(value, SugarInstance):
            raise TypeError(
                f"Expected an instance of {expected_class.name}, but got {type(value).__name__}"
            )

        if value.sugar_class.name != expected_class.name:
            raise TypeError(
                f"Expected an instance of {expected_class.name}, but got {value.sugar_class.name}"
            )

        # Check properties
        for prop_name, prop_decl in expected_class.properties.items():
            try:
                prop_value = value.environment.get(prop_name).value
                self.assert_type(prop_value, prop_decl.property_type)
            except NameError:
                raise TypeError(
                    f"Missing property '{prop_name}' in instance of {expected_class.name}"
                )

        return True

    def _assert_custom_type(self, value, expected_type: Type):
        if not self.environment:
            raise TypeError("Environment not set for type checker.")

        type_def = self.environment.get(expected_type.name)
        if not isinstance(type_def, CustomType):
            raise TypeError(f"Unknown type: {expected_type.name}")

        if isinstance(value, SugarInstance):
            # If the value is a SugarInstance, check its class name
            if value.sugar_class.declaration.name.name != expected_type.name:
                raise TypeError(
                    f"Expected an object of type {expected_type.name}, but got {value.sugar_class.name}"
                )
            # And then use its environment for the field checks
            value_dict = {
                k: v.value for k, v in value.environment.values.items() if k != "THIS"
            }
        elif isinstance(value, dict):
            value_dict = value
        else:
            raise TypeError(
                f"Expected an object of type {expected_type.name}, but got {type(value).__name__}"
            )

        type_fields = type_def.declaration.type_body
        if len(value_dict) != len(type_fields):
            raise TypeError(
                f"Incorrect number of fields for type {expected_type.name}. Expected {len(type_fields)}, got {len(value_dict)}"
            )

        for field_def in type_fields:
            field_name = field_def.name.name
            if field_name not in value_dict:
                raise TypeError(
                    f"Missing field '{field_name}' in object of type {expected_type.name}"
                )
            self.assert_type(value_dict[field_name], field_def.field_type)

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
        return f"{self.__class__.__name__}()"

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
            if not value:
                return MapType(
                    name="{}", key_type=Type("dynamic"), value_type=Type("dynamic")
                )

            first_key, first_value = next(iter(value.items()))
            key_type = self.get_runtime_type(first_key)
            value_type = self.get_runtime_type(first_value)

            return MapType(
                name=f"{{{key_type.name},{value_type.name}}}",
                key_type=key_type,
                value_type=value_type,
            )
        elif isinstance(value, tuple):
            element_types = [self.get_runtime_type(item) for item in value]
            return TupleType(
                name=f"({', '.join(t.name for t in element_types)})",
                types=element_types,
            )
        elif value is None:
            return Type("null")
        elif callable(value):
            return Type("function")
        elif isinstance(value, SugarInstance):
            return Type(value.sugar_class.name)
        elif isinstance(value, SugarClass):
            return Type(value.name)
        else:

            raise TypeError(f"Could not infer runtime type for {value}")
