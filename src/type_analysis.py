class TypeAnalyzer:
    """Handles type analysis and extraction from AST nodes."""
    @staticmethod
    def extract_type_info(type_tree):
        if not hasattr(type_tree, 'data') or type_tree.data != 'type':
            return None, False, False
        if not type_tree.children:
            return None, False, False
        child = type_tree.children[0]
        if hasattr(child, 'data') and child.data == 'primitive_type':
            return TypeAnalyzer._extract_primitive_type(child), False, False
        elif hasattr(child, 'data') and child.data == 'array_type':
            element_type = TypeAnalyzer._extract_array_element_type(child)
            return element_type, True, False
        elif hasattr(child, 'data') and child.data == 'map_type':
            return 'map', False, True
        return None, False, False
    @staticmethod
    def _extract_primitive_type(prim_type_node):
        if not prim_type_node.children or not hasattr(prim_type_node.children[0], 'type'):
            return None
        ttype = prim_type_node.children[0].type
        type_map = {
            'INT_TYPE': 'int',
            'FLOAT_TYPE': 'float',
            'BOOL_TYPE': 'bool',
            'CHAR_TYPE': 'char',
            'STR_TYPE': 'str'
        }
        return type_map.get(ttype)
    @staticmethod
    def _extract_array_element_type(array_type_node):
        if (array_type_node.children and 
            hasattr(array_type_node.children[0], 'data') and 
            array_type_node.children[0].data == 'type'):
            element_type_node = array_type_node.children[0]
            if (element_type_node.children and 
                hasattr(element_type_node.children[0], 'data') and 
                element_type_node.children[0].data == 'primitive_type'):
                return TypeAnalyzer._extract_primitive_type(element_type_node.children[0])
        return None 