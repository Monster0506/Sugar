from src.ast_nodes import ArrayType, MapType, TupleType, Type


class TypeChecker:
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

            raise TypeError(f"Unknown simple type: {expected_type.name}")

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
