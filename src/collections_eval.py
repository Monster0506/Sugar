from .literal_eval import LiteralEvaluator
from .values import SugarArray, SugarMap, SugarStr

class CollectionEvaluator:
    """Handles evaluation of collection literals (arrays, maps)."""
    @staticmethod
    def evaluate_array_literal(node, env):
        if not hasattr(node, 'data') or node.data != 'array_literal':
            return []
        if not node.children or not hasattr(node.children[0], 'data') or node.children[0].data != 'argument_list':
            return []
        arg_list = node.children[0]
        elements = []
        for child in arg_list.children:
            if hasattr(child, 'data') and child.data == 'literal':
                element = LiteralEvaluator.evaluate_literal(child)
                elements.append(element)
        return elements
    @staticmethod
    def evaluate_dict_literal(node, env):
        if not hasattr(node, 'data') or node.data != 'dict_literal':
            return {}
        if not node.children or not hasattr(node.children[0], 'data') or node.children[0].data != 'dict_entries':
            return {}
        dict_entries = node.children[0]
        mapping = {}
        for child in dict_entries.children:
            if hasattr(child, 'data') and child.data == 'dict_entry' and len(child.children) >= 2:
                key_literal = child.children[0]
                value_literal = child.children[1]
                key = LiteralEvaluator.evaluate_literal(key_literal)
                value = LiteralEvaluator.evaluate_literal(value_literal)
                if isinstance(key, SugarStr):
                    mapping[key.value] = value
                else:
                    mapping[str(key)] = value
        return mapping 