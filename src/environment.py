class SugarEnvironment:
    """Represents a runtime environment (scope) for variables and functions."""
    def __init__(self, parent=None):
        self.parent = parent
        self.variables = {}

    def get(self, name):
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise NameError(f"Variable '{name}' not found")

    def set(self, name, value):
        self.variables[name] = value

    def __repr__(self):
        return f"SugarEnvironment({self.variables})"

class SugarCallFrame:
    """Represents a call stack frame for function/method calls."""
    def __init__(self, env, function_name=None):
        self.env = env
        self.function_name = function_name 