from .values import SugarInt, SugarFloat, SugarBool, SugarChar, SugarStr

class LiteralEvaluator:
    """Handles evaluation of literal values."""
    @staticmethod
    def evaluate_literal(node):
        if not hasattr(node, 'data') or node.data != 'literal':
            return SugarInt(0)
        if not node.children or not hasattr(node.children[0], 'type'):
            return SugarInt(0)
        ttype = node.children[0].type
        value = node.children[0].value
        literal_handlers = {
            'INTEGER': lambda v: SugarInt(int(v)),
            'FLOAT': lambda v: SugarFloat(float(v)),
            'BOOLEAN': lambda v: SugarBool(True if v == ':T:' else False),
            'CHAR': lambda v: SugarChar(v),
            'STRING': lambda v: SugarStr(v)
        }
        handler = literal_handlers.get(ttype)
        return handler(value) if handler else SugarInt(0) 