class SugarValue:
    """Base class for all Sugar runtime values."""
    pass

class SugarInt(SugarValue):
    def __init__(self, value: int):
        self.value = value
    def __repr__(self):
        return f"SugarInt({self.value=})"

class SugarFloat(SugarValue):
    def __init__(self, value: float):
        self.value = value
    def __repr__(self):
        return f"SugarFloat({self.value=})"

class SugarBool(SugarValue):
    def __init__(self, value: bool):
        self.value = value
    def __repr__(self):
        return f"SugarBool({self.value=})"

class SugarChar(SugarValue):
    def __init__(self, value: str):
        self.value = value
    def __repr__(self):
        return f"SugarChar({self.value=})"

class SugarStr(SugarValue):
    def __init__(self, value: str):
        self.value = value
    def __repr__(self):
        return f"SugarStr({self.value=})"

class SugarArray(SugarValue):
    def __init__(self, elements):
        self.elements = elements
    def __repr__(self):
        return f"SugarArray({self.elements=})"

class SugarMap(SugarValue):
    def __init__(self, mapping):
        self.mapping = mapping
    def __repr__(self):
        return f"SugarMap({self.mapping=})"

class SugarTuple(SugarValue):
    def __init__(self, elements):
        self.elements = elements
    def __repr__(self):
        return f"SugarTuple({self.elements=})"

class SugarObject(SugarValue):
    def __init__(self, class_name, fields):
        self.class_name = class_name
        self.fields = fields
    def __repr__(self):
        return f"SugarObject({self.class_name=}, {self.fields=})" 