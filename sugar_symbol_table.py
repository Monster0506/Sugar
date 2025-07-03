#!/usr/bin/env python3
"""
Sugar Symbol Table Generator
Walks the AST and builds a comprehensive symbol table for type checking.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Change to INFO to reduce noise
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger("SymbolTable")

class SymbolKind(Enum):

    """Types of symbols that can be stored in the symbol table."""
    VARIABLE = "variable"
    FUNCTION = "function"
    CLASS = "class"
    TYPE = "type"
    INTERFACE = "interface"
    PARAMETER = "parameter"
    PROPERTY = "property"
    METHOD = "method"
    CONSTRUCTOR = "constructor"
    MODULE = "module"
    CONSTANT = "constant"
    ENUM = "enum"
    ENUM_VALUE = "enum_value"
    NAMESPACE = "namespace"
    ALIAS = "alias"
    GENERIC = "generic"
    TRAIT = "trait"
    IMPLEMENTATION = "implementation"
    MACRO = "macro"
    ANNOTATION = "annotation"
    ERROR_TYPE = "error_type"
    UNION_TYPE = "union_type"
    OPTIONAL_TYPE = "optional_type"
    ARRAY_TYPE = "array_type"
    MAP_TYPE = "map_type"
    TUPLE_TYPE = "tuple_type"


@dataclass
class SymbolInfo:
    """Information about a symbol in the symbol table."""
    name: str
    kind: SymbolKind
    type: str
    line: int
    column: int
    scope_level: int
    is_qualified: bool = False  # For methods like Student:calculate_average
    access_modifier: Optional[str] = None  # PUBLIC, PRIVATE, PROTECTED
    is_static: bool = False
    is_override: bool = False
    is_abstract: bool = False
    is_final: bool = False
    is_deprecated: bool = False
    documentation: Optional[str] = None
    generic_parameters: Optional[List[str]] = None
    default_value: Optional[str] = None
    is_mut: bool = False  # For mutable variables
    is_const: bool = False  # For constants
    visibility: str = "public"  # public, private, protected, internal
    source_file: Optional[str] = None
    param_types: Optional[List[str]] = None  # For function/method overloading

class Scope:
    """A scope in the symbol table, with parent/children and symbols."""
    def __init__(self, name: str, level: int, parent=None):
        self.name = name
        self.level = level
        self.parent = parent  # Parent Scope
        self.children = []   # List of child Scopes
        self.symbols: Dict[str, Any] = {}  # str -> SymbolInfo or List[SymbolInfo] for functions
        self.logger = logging.getLogger("Scope")
        self.logger.debug(f"Created scope '{self.name}' at level {self.level}")
    def add_child(self, child_scope):
        self.children.append(child_scope)
        self.logger.debug(f"Added child scope '{child_scope.name}' to '{self.name}'")

class SymbolTable:
    """Manages hierarchical scopes and symbols for the Sugar language."""
    def __init__(self):
        self.root_scope = Scope("global", 0, parent=None)
        self.current_scope = self.root_scope
        self.errors: List[str] = []
        self.logger = logging.getLogger("SymbolTable")
        self.global_symbols: Dict[str, SymbolInfo] = {}  # For fast lookup
    
    def enter_scope(self, scope_name: str = "block") -> None:
        """Enter a new scope (function, class, block, etc.)."""
        new_scope = Scope(scope_name, self.current_scope.level + 1, parent=self.current_scope)
        self.current_scope.add_child(new_scope)
        self.current_scope = new_scope
        self.logger.info(f"Entered scope '{scope_name}' at level {self.current_scope.level}")

    def exit_scope(self) -> None:
        """Exit the current scope."""
        if self.current_scope.parent is not None:
            self.logger.info(f"Exiting scope '{self.current_scope.name}' at level {self.current_scope.level}")
            self.current_scope = self.current_scope.parent
        else:
            self.logger.warning("Attempted to exit global scope")

    def declare(self, name: str, kind: SymbolKind, type_info: str, 
                line: int, column: int, **kwargs) -> bool:
        """Declare a new symbol in the current scope."""
        # Validate symbol name
        if not self._is_valid_symbol_name(name):
            error_msg = f"Invalid symbol name '{name}' at line {line}, column {column}"
            self.errors.append(error_msg)
            self.logger.error(error_msg)
            return False
        symbol_info = SymbolInfo(
            name=name,
            kind=kind,
            type=type_info,
            line=line,
            column=column,
            scope_level=self.current_scope.level,
            **kwargs
        )
        # Function overloading support
        if kind == SymbolKind.FUNCTION:
            overloads = self.current_scope.symbols.get(name, [])
            # Check for signature clash
            for overload in overloads:
                if getattr(overload, 'param_types', None) == symbol_info.param_types:
                    error_msg = (
                        f"Redeclaration of overloaded function '{name}' with same parameter types at line {line}, column {column}. "
                        f"Previously declared at line {overload.line}, column {overload.column}"
                    )
                    self.errors.append(error_msg)
                    self.logger.error(error_msg)
                    return False
            overloads.append(symbol_info)
            self.current_scope.symbols[name] = overloads
            self.logger.info(f"Declared overloaded function '{name}' with param_types={symbol_info.param_types} in scope '{self.current_scope.name}' (level {self.current_scope.level})")
            return True
        # Non-function: check for redeclaration
        if name in self.current_scope.symbols:
            existing = self.current_scope.symbols[name]
            error_msg = f"Redeclaration of '{name}' at line {line}, column {column}. " \
                       f"Previously declared at line {existing.line}, column {existing.column}"
            self.errors.append(error_msg)
            self.logger.error(error_msg)
            return False
        self.current_scope.symbols[name] = symbol_info
        if self.current_scope.level == 0:
            self.global_symbols[name] = symbol_info
        self.logger.info(f"Declared {kind.value} '{name}' in scope '{self.current_scope.name}' (level {self.current_scope.level})")
        return True

    def lookup(self, name: str, param_types: Optional[List[str]] = None, current_scope_only: bool = False) -> Optional[SymbolInfo]:
        """Look up a symbol by name (and param_types for functions), searching up the scope tree."""
        scope = self.current_scope
        while scope is not None:
            if name in scope.symbols:
                symbol = scope.symbols[name]
                if isinstance(symbol, list):  # function overloads
                    if param_types is not None:
                        for overload in symbol:
                            if overload.param_types == param_types:
                                self.logger.debug(f"Found overloaded function '{name}' with param_types={param_types} in scope '{scope.name}' (level {scope.level})")
                                return overload
                        self.logger.debug(f"No matching overload for function '{name}' with param_types={param_types} in scope '{scope.name}' (level {scope.level})")
                        return None
                    else:
                        self.logger.debug(f"Returning first overload for function '{name}' in scope '{scope.name}' (level {scope.level})")
                        return symbol[0] if symbol else None
                else:
                    self.logger.debug(f"Found '{name}' in scope '{scope.name}' (level {scope.level})")
                    return symbol
            if current_scope_only:
                break
            scope = scope.parent
        self.logger.debug(f"Symbol '{name}' not found in any scope")
        return None

    def _is_valid_symbol_name(self, name: str) -> bool:
        if not name or not name.strip():
            return False
        reserved_keywords = {
            'DEF', 'FUN', 'CLASS', 'TYPE', 'INTERFACE', 'IF', 'ELSE', 'FOR', 
            'WHILE', 'TRY', 'CATCH', 'FINALLY', 'MATCH', 'CASE', 'DEFAULT',
            'RETURN', 'BREAK', 'CONTINUE', 'THIS', 'SUPER', 'NEW', 'PUBLIC',
            'PRIVATE', 'PROTECTED', 'STATIC', 'ABSTRACT', 'FINAL', 'OVERRIDE',
            'CONST', 'MUT', 'VAR', 'LET', 'TRUE', 'FALSE', 'NULL', 'NONE'
        }
        if name.upper() in reserved_keywords:
            return False
        if not name[0].isalpha() and name[0] != '_':
            return False
        return True

    def update(self, name: str, **kwargs) -> bool:
        symbol = self.lookup(name)
        if symbol is None:
            return False
        for key, value in kwargs.items():
            if hasattr(symbol, key):
                setattr(symbol, key, value)
        return True

    def get_current_scope_symbols(self) -> Dict[str, SymbolInfo]:
        """Return a copy of the current scope's symbols."""
        return self.current_scope.symbols.copy()
    def get_all_symbols(self) -> Dict[str, SymbolInfo]:
        """Return a flat dictionary of all symbols in all scopes, using qualified names for uniqueness."""
        all_symbols = {}

        def collect_symbols(scope, prefix=""):
            for name, symbol in scope.symbols.items():
                if isinstance(symbol, list):  # function overloads
                    for idx, overload in enumerate(symbol):
                        qualified_name = f"{prefix}{name}__overload{idx}" if prefix else f"{name}__overload{idx}"
                        all_symbols[qualified_name] = overload
                else:
                    qualified_name = f"{prefix}{symbol.name}" if not prefix else f"{prefix}.{symbol.name}"
                    all_symbols[qualified_name] = symbol
            for child in scope.children:
                child_prefix = f"{prefix}{child.name}." if prefix else f"{child.name}."
                collect_symbols(child, child_prefix)

        collect_symbols(self.root_scope)
        return all_symbols
    def print_symbol_table(self) -> None:
        """Print the symbol table in a hierarchical format showing nested scopes."""
        print("\n" + "="*60)
        print("SYMBOL TABLE - HIERARCHICAL SCOPE STRUCTURE")
        print("="*60)
        
        def print_scope_recursive(scope: Scope, indent: int = 0):
            indent_str = "  " * indent
            print(f"{indent_str} Scope: {scope.name} (Level {scope.level})")
            
            if scope.symbols:
                # Group symbols by kind
                symbols_by_kind = {}
                for name, symbol in scope.symbols.items():
                    if isinstance(symbol, list):
                        for overload in symbol:
                            kind = overload.kind.value
                            symbols_by_kind.setdefault(kind, []).append(overload)
                    else:
                        kind = symbol.kind.value
                        symbols_by_kind.setdefault(kind, []).append(symbol)
                # Print symbols grouped by kind
                for kind, symbols in sorted(symbols_by_kind.items()):
                    print(f"{indent_str}   {kind.upper()} VALUES:")
                    for symbol in sorted(symbols, key=lambda s: s.name):
                        type_display = f" : {symbol.type}" if symbol.type else ""
                        if symbol.kind == SymbolKind.FUNCTION and symbol.param_types is not None:
                            print(f"{indent_str}     {symbol.name}({', '.join(symbol.param_types)}){type_display} (line {symbol.line})")
                        else:
                            print(f"{indent_str}     {symbol.name}{type_display} (line {symbol.line})")
            else:
                print(f"{indent_str}  (no symbols)")
            # Print child scopes
            for child in scope.children:
                print_scope_recursive(child, indent + 1)
        # Start from root scope
        print_scope_recursive(self.root_scope)
        print("="*60)
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    def get_errors(self) -> List[str]:
        return self.errors.copy()
    def add_error(self, error_msg: str) -> None:
        self.errors.append(error_msg)
        self.logger.error(error_msg)
    def add_warning(self, warning_msg: str) -> None:
        self.logger.warning(warning_msg)
    def get_symbols_by_kind(self, kind: SymbolKind) -> List[SymbolInfo]:
        """Return a list of SymbolInfo for all symbols of the given SymbolKind in the entire table."""
        result = []
        def collect(scope):
            for symbol in scope.symbols.values():
                if symbol.kind == kind:
                    result.append(symbol)
            for child in scope.children:
                collect(child)
        collect(self.root_scope)
        return result
    def get_symbols_by_type(self, type_name: str) -> List[SymbolInfo]:
        """Return a list of SymbolInfo for all symbols with the given type name in the entire table."""
        result = []
        def collect(scope):
            for symbol in scope.symbols.values():
                if symbol.type == type_name:
                    result.append(symbol)
            for child in scope.children:
                collect(child)
        collect(self.root_scope)
        return result
    def get_scope_depth(self) -> int:
        """Return the current scope's depth (level)."""
        return self.current_scope.level
    def get_scope_name(self, level: Optional[int] = None) -> str:
        """Return the name of the current scope or the scope at the specified level."""
        if level is None:
            return self.current_scope.name
        # Traverse up to the requested level
        scope = self.current_scope
        while scope is not None and scope.level != level:
            scope = scope.parent
        return scope.name if scope is not None else ""
    def is_in_global_scope(self) -> bool:
        return self.current_scope == self.root_scope
    def get_qualified_name(self, symbol: SymbolInfo) -> str:
        """Return the qualified name for a symbol, based on its scope hierarchy."""
        # Walk up from the symbol's scope to root, collecting names
        def find_scope_with_symbol(scope, name):
            if name in scope.symbols:
                return scope
            for child in scope.children:
                found = find_scope_with_symbol(child, name)
                if found:
                    return found
            return None
        # Find the scope where this symbol is declared
        scope = self.root_scope
        path = []
        def find_path(scope, name):
            if name in scope.symbols:
                path.append(scope.name)
                return True
            for child in scope.children:
                if find_path(child, name):
                    path.append(scope.name)
                    return True
            return False
        find_path(self.root_scope, symbol.name)
        path = list(reversed(path))
        if path and path[0] == "global":
            path = path[1:]
        qualified = ".".join(path + [symbol.name]) if path else symbol.name
        return qualified
    def find_conflicts(self) -> List[Tuple[str, List[SymbolInfo]]]:
        raise NotImplementedError
    def get_symbol_statistics(self) -> Dict[str, int]:
        """Return a dictionary mapping SymbolKind names to counts of symbols of each kind in the entire table."""
        stats = {kind.value: 0 for kind in SymbolKind}
        def count_symbols(scope):
            for symbol in scope.symbols.values():
                stats[symbol.kind.value] += 1
            for child in scope.children:
                count_symbols(child)
        count_symbols(self.root_scope)
        return stats
    def get_scope_statistics(self) -> Dict[str, int]:
        """Return a dictionary mapping scope names to the number of symbols declared in each scope (recursively, including children)."""
        stats = {}
        def count_scope(scope):
            stats[scope.name] = len(scope.symbols)
            for child in scope.children:
                count_scope(child)
        count_scope(self.root_scope)
        return stats
    def export_symbols(self, format: str = "dict") -> Union[Dict, str]:
        """Export all symbols in the table in the requested format.
        - 'dict': nested dict by scope
        - 'flat': flat dict of qualified names to symbol info
        - 'str': string representation
        """
        if format == "dict":
            def scope_to_dict(scope):
                return {
                    'scope_name': scope.name,
                    'level': scope.level,
                    'symbols': {name: symbol.__dict__ for name, symbol in scope.symbols.items()},
                    'children': [scope_to_dict(child) for child in scope.children]
                }
            return scope_to_dict(self.root_scope)
        elif format == "flat":
            return {qname: symbol.__dict__ for qname, symbol in self.get_all_symbols().items()}
        elif format == "str":
            import pprint
            return pprint.pformat(self.get_all_symbols())
        else:
            raise ValueError(f"Unknown export format: {format}")



class SymbolTableGenerator:
    """Walks the AST and builds a symbol table."""
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.logger = logging.getLogger("SymbolTableGenerator")
        self.current_line = 0
        self.current_column = 0
        self.match_type_stack = []  # For tracking match expression types
    
    def generate(self, ast) -> SymbolTable:
        """Generate symbol table from AST."""
        self.logger.info("Starting symbol table generation...")
        
        try:
            self.visit(ast)
            
            # Perform post-processing validations
            self._validate_symbol_table()
            
            self.logger.info("Symbol table generation complete")
            self.symbol_table.print_symbol_table()
            
            if self.symbol_table.has_errors():
                self.logger.warning(f"Symbol table generation completed with {len(self.symbol_table.get_errors())} errors")
            else:
                self.logger.info("Symbol table generation completed successfully")
                
        except Exception as e:
            error_msg = f"Error during symbol table generation: {str(e)}"
            self.symbol_table.add_error(error_msg)
            self.logger.error(error_msg, exc_info=True)
        
        return self.symbol_table
    
    def _validate_symbol_table(self) -> None:
        """Perform validation checks on the generated symbol table."""
        # Implementation needs to be updated to use Scope objects
        pass
    
    def visit(self, node) -> None:
        """Visit a node and process it for symbol table construction."""
        if node is None:
            return
        
        # Extract line/column info if available
        if hasattr(node, 'meta') and hasattr(node.meta, 'line'):
            self.current_line = node.meta.line
        if hasattr(node, 'meta') and hasattr(node.meta, 'column'):
            self.current_column = node.meta.column
        
        # Determine node type and call appropriate visitor
        if hasattr(node, 'data'):
            node_type = node.data
            self.logger.debug(f"Visiting {node_type} node with {len(node.children)} children")
            
            # Map node types to visitor methods
            visitor_map = {
                'program': self.visit_program,
                'variable_declaration': self.visit_variable_declaration,
                'variable_assignment': self.visit_variable_assignment,
                'this_assignment': self.visit_this_assignment,
                'function_declaration': self.visit_function_declaration,
                'class_declaration': self.visit_class_declaration,
                'type_declaration': self.visit_type_declaration,
                'interface_declaration': self.visit_interface_declaration,
                'method_declaration': self.visit_method_declaration,
                'constructor_declaration': self.visit_constructor_declaration,
                'property_declaration': self.visit_property_declaration,
                'enum_declaration': self.visit_enum_declaration,
                'enum_value': self.visit_enum_value,
                'constant_declaration': self.visit_constant_declaration,
                'module_declaration': self.visit_module_declaration,
                'namespace_declaration': self.visit_namespace_declaration,
                'trait_declaration': self.visit_trait_declaration,
                'implementation_declaration': self.visit_implementation_declaration,
                'alias_declaration': self.visit_alias_declaration,
                'generic_declaration': self.visit_generic_declaration,
                'macro_declaration': self.visit_macro_declaration,
                'annotation_declaration': self.visit_annotation_declaration,
                'if_statement': self.visit_if_statement,
                'elif_clause': self.visit_elif_clause,
                'else_clause': self.visit_else_clause,
                'for_statement': self.visit_for_statement,
                'while_statement': self.visit_while_statement,
                'try_statement': self.visit_try_statement,
                'match_statement': self.visit_match_statement,
                'parameter_list': self.visit_parameter_list,
                'parameter': self.visit_parameter,
                'function_body': self.visit_function_body,
                'class_body': self.visit_class_body,
                'type_body': self.visit_type_body,
                'interface_body': self.visit_interface_body,
                'enum_body': self.visit_enum_body,
                'trait_body': self.visit_trait_body,
                'implementation_body': self.visit_implementation_body,
                'case_clause': self.visit_case_clause,
                'catch_clause': self.visit_catch_clause,
                'finally_clause': self.visit_finally_clause,
            }
            
            if node_type in visitor_map:
                self.logger.debug(f"Calling visitor for {node_type}")
                visitor_map[node_type](node)
            else:
                # For other nodes, just visit children
                self.logger.debug(f"No visitor for {node_type}, visiting children")
                for child in node.children:
                    self.visit(child)
        else:
            # Leaf node (token)
            self.logger.debug(f"Visiting leaf node: {node}")
    
    def visit_program(self, node) -> None:
        """Visit program node - entry point."""
        self.logger.info("Processing program node")
        for child in node.children:
            self.visit(child)
    
    def visit_variable_declaration(self, node) -> None:
        """Visit variable declaration node."""
        if len(node.children) >= 3:
            # Structure: [IDENTIFIER, type_tree, expression]
            name_token = node.children[0]
            type_tree = node.children[1]
            
            # Extract name from IDENTIFIER token
            if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
                name = str(name_token.value)
            else:
                name = str(name_token)
            
            # Extract type from type tree
            type_info = self.extract_type_from_tree(type_tree)
            
            if name and type_info:
                self.logger.info(f"Processing variable declaration: {name} : {type_info}")
                
                self.symbol_table.declare(
                    name=name,
                    kind=SymbolKind.VARIABLE,
                    type_info=type_info,
                    line=self.current_line,
                    column=self.current_column
                )
            else:
                self.logger.warning(f"Could not extract name or type from variable declaration: {node.children}")
    
    def extract_type_from_tree(self, type_tree) -> str:
        """Extract type string from a type tree."""
        if not type_tree:
            return "unknown"
        
        # Handle Tree objects
        if hasattr(type_tree, 'data'):
            if type_tree.data == 'type':
                if type_tree.children and hasattr(type_tree.children[0], 'data'):
                    child = type_tree.children[0]
                    if child.data == 'primitive_type' and child.children:
                        type_token = child.children[0]
                        if hasattr(type_token, 'type'):
                            return str(type_token.value)
                        elif hasattr(type_token, 'value'):
                            return str(type_token.value)
                    elif child.data == 'array_type':
                        element_type = self.extract_type_from_tree(child.children[0])
                        return f"[{element_type}]"
                    elif child.data == 'map_type':
                        key_type = self.extract_type_from_tree(child.children[0])
                        value_type = self.extract_type_from_tree(child.children[1])
                        return f"{{key: {key_type}, value: {value_type}}}"
                    elif child.data == 'tuple_type':
                        element_types = []
                        for element in child.children:
                            element_types.append(self.extract_type_from_tree(element))
                        return f"({', '.join(element_types)})"
                    elif child.data == 'custom_type' and child.children:
                        type_token = child.children[0]
                        if hasattr(type_token, 'type'):
                            return str(type_token.value)
                        elif hasattr(type_token, 'value'):
                            return str(type_token.value)
            elif type_tree.data == 'primitive_type':
                if type_tree.children:
                    type_token = type_tree.children[0]
                    if hasattr(type_token, 'type'):
                        return str(type_token.value)
                    elif hasattr(type_token, 'value'):
                        return str(type_token.value)
        
        # Handle Token objects directly
        elif hasattr(type_tree, 'type'):
            return str(type_tree.value)
        
        # Handle string literals
        elif isinstance(type_tree, str):
            return type_tree
        
        # Try to convert to string
        try:
            return str(type_tree)
        except:
            return "unknown"
    
    def visit_function_declaration(self, node) -> None:
        """Visit function declaration node."""
        # Children: [name, (optional parameter_list), type, function_body]
        children = node.children
        name_token = children[0]
        idx = 1
        # Check if parameter_list is present
        if hasattr(children[idx], 'data') and children[idx].data == 'parameter_list':
            param_list = children[idx]
            idx += 1
        else:
            param_list = None
        return_type_tree = children[idx]
        function_body = children[idx + 1]
        # Extract function name
        if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
            name = str(name_token.value)
        else:
            name = str(name_token)
        # Extract return type
        return_type = self.extract_type_from_tree(return_type_tree)
        # Extract parameter types
        param_types = []
        if param_list is not None and hasattr(param_list, 'children') and param_list.children:
            for param in param_list.children:
                if hasattr(param, 'data') and param.data == 'parameter' and len(param.children) >= 2:
                    type_info = self.extract_type_from_tree(param.children[1])
                    param_types.append(type_info)
        self.logger.info(f"Processing function declaration: {name}({', '.join(param_types)}) -> {return_type}")
        self.symbol_table.declare(
            name=name,
            kind=SymbolKind.FUNCTION,
            type_info=return_type,
            line=self.current_line,
            column=self.current_column,
            is_qualified=False,  # Will handle qualified names later
            param_types=param_types
        )
        # Enter function scope and process parameters
        self.symbol_table.enter_scope(f"function_{name}_{self.current_line}_{self.current_column}")
        # Process parameters
        if param_list is not None and hasattr(param_list, 'children') and param_list.children:
            self.visit_parameter_list(param_list)
        # Process function body
        self.visit(function_body)
        self.symbol_table.exit_scope()
    
    def visit_parameter_list(self, node) -> None:
        """Visit parameter list node."""
        self.logger.debug("Processing parameter list")
        for child in node.children:
            if hasattr(child, 'data') and child.data == 'parameter':
                self.visit_parameter(child)
    
    def visit_parameter(self, node) -> None:
        """Visit parameter node."""
        if len(node.children) >= 2:
            name = str(node.children[0])
            type_info = self.extract_type_from_tree(node.children[1])
            self.logger.debug(f"Processing parameter: {name} : {type_info}")
            
            self.symbol_table.declare(
                name=name,
                kind=SymbolKind.PARAMETER,
                type_info=type_info,
                line=self.current_line,
                column=self.current_column
            )
    
    def visit_class_declaration(self, node) -> None:
        """Visit class declaration node."""
        if len(node.children) >= 2:
            name_token = node.children[0]
            if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
                name = str(name_token.value)
            else:
                name = str(name_token)
            self.logger.debug(f"Processing class declaration: {name}")
            self.symbol_table.declare(
                name=name,
                kind=SymbolKind.CLASS,
                type_info="class",
                line=self.current_line,
                column=self.current_column
            )
            self.symbol_table.enter_scope(f"class_{name}_{self.current_line}_{self.current_column}")
            # Debug print for MathUtility
            if name == "MathUtility":
                print(f"DEBUG visit_class_declaration: MathUtility class body children: {node.children[1].children}")
            self.visit(node.children[1])
            self.symbol_table.exit_scope()
    
    def visit_type_declaration(self, node) -> None:
        """Visit type declaration node."""
        if len(node.children) >= 2:
            # Extract the type name from the first child (should be the type body)
            type_body = node.children[0]
            name = self._extract_type_name_from_body(type_body)
            
            self.logger.debug(f"Processing type declaration: {name}")
            
            self.symbol_table.declare(
                name=name,
                kind=SymbolKind.TYPE,
                type_info="type",
                line=self.current_line,
                column=self.current_column
            )
    
    def _extract_type_name_from_body(self, type_body) -> str:
        if isinstance(type_body, str):
            return type_body
        """Extract type name from type body or return a default name."""
        # For now, return a simple name based on the structure
        # In a real implementation, you'd extract the actual type name
        if hasattr(type_body, 'data') and type_body.data == 'type_body':
            return "CustomType"  # Default name for now
        return "UnknownType"
    
    def visit_interface_declaration(self, node) -> None:
        """Visit interface declaration node."""
        if len(node.children) >= 2:
            # Extract the interface name from the first child (should be the interface body)
            interface_body = node.children[0]
            name = self._extract_interface_name_from_body(interface_body)
            
            self.logger.debug(f"Processing interface declaration: {name}")
            
            self.symbol_table.declare(
                name=name,
                kind=SymbolKind.INTERFACE,
                type_info="interface",
                line=self.current_line,
                column=self.current_column
            )
    
    def _extract_interface_name_from_body(self, interface_body) -> str:
        if isinstance(interface_body, str):
            return interface_body               
        """Extract interface name from interface body or return a default name."""
        # For now, return a simple name based on the structure
        # In a real implementation, you'd extract the actual interface name
        if hasattr(interface_body, 'data') and interface_body.data == 'interface_body':
            return "CustomInterface"  # Default name for now
        return "UnknownInterface"
    
    def visit_variable_assignment(self, node) -> None:
        """Visit variable assignment node."""
        if len(node.children) >= 2:
            name_token = node.children[0]
            if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
                name = str(name_token.value)
                self.logger.debug(f"Processing variable assignment: {name}")
    
    def visit_this_assignment(self, node) -> None:
        """Visit this assignment node."""
        if len(node.children) >= 3:
            name_token = node.children[1]  # After "THIS" and ":"
            if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
                name = str(name_token.value)
                self.logger.debug(f"Processing this assignment: THIS:{name}")
    
    def visit_method_declaration(self, node) -> None:
        """Visit method declaration node."""
        if len(node.children) >= 4:
            name_token = node.children[0]
            param_list = node.children[1]
            return_type_tree = node.children[2]
            method_body = node.children[3]
            
            if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
                name = str(name_token.value)
            else:
                name = str(name_token)
            
            return_type = self.extract_type_from_tree(return_type_tree)
            
            self.logger.info(f"Processing method declaration: {name} -> {return_type}")
            
            self.symbol_table.declare(
                name=name,
                kind=SymbolKind.METHOD,
                type_info=return_type,
                line=self.current_line,
                column=self.current_column
            )
            
            # Enter method scope
            self.symbol_table.enter_scope(f"method_{name}_{self.current_line}_{self.current_column}")
            
            # Process parameters
            if hasattr(param_list, 'children') and param_list.children:
                self.visit_parameter_list(param_list)
            
            # Process method body
            self.visit(method_body)
            
            self.symbol_table.exit_scope()
    
    def visit_constructor_declaration(self, node) -> None:
        """Visit constructor declaration node."""
        if len(node.children) >= 2:
            param_list = node.children[0]
            constructor_body = node.children[1]
            
            self.logger.info("Processing constructor declaration")
            
            self.symbol_table.declare(
                name="constructor",
                kind=SymbolKind.CONSTRUCTOR,
                type_info="constructor",
                line=self.current_line,
                column=self.current_column
            )
            
            # Enter constructor scope
            self.symbol_table.enter_scope(f"constructor_{self.current_line}_{self.current_column}")
            
            # Process parameters
            if hasattr(param_list, 'children') and param_list.children:
                self.visit_parameter_list(param_list)
            
            # Process constructor body
            self.visit(constructor_body)
            
            self.symbol_table.exit_scope()
    
    def visit_property_declaration(self, node) -> None:
        """Visit property declaration node."""
        if len(node.children) >= 2:
            name_token = node.children[0]
            type_tree = node.children[1]
            
            if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
                name = str(name_token.value)
            else:
                name = str(name_token)
            
            type_info = self.extract_type_from_tree(type_tree)
            
            self.logger.info(f"Processing property declaration: {name} : {type_info}")
            
            self.symbol_table.declare(
                name=name,
                kind=SymbolKind.PROPERTY,
                type_info=type_info,
                line=self.current_line,
                column=self.current_column
            )
    
    def visit_if_statement(self, node) -> None:
        """Visit if statement node."""
        self.logger.debug("Processing if statement")
        
        # Process condition (first child)
        if node.children:
            self.visit(node.children[0])
        
        # Process if body (second child) in its own scope
        if len(node.children) > 1:
            self.symbol_table.enter_scope(f"if_block_{self.current_line}_{self.current_column}")
            self.visit(node.children[1])
            self.symbol_table.exit_scope()
        
        # Process elif clauses (third child onwards, except the last one if it's an else_clause)
        elif_start = 2
        elif_end = len(node.children) - 1 if node.children and hasattr(node.children[-1], 'data') and node.children[-1].data == 'else_clause' else len(node.children)
        
        for i in range(elif_start, elif_end):
            self.visit(node.children[i])
        
        # Process else clause (last child) in its own scope if present
        if node.children and hasattr(node.children[-1], 'data') and node.children[-1].data == 'else_clause':
            self.visit(node.children[-1])
    
    def visit_elif_clause(self, node) -> None:
        """Visit elif clause node."""
        self.logger.debug("Processing elif clause")
        
        # Process condition (first child)
        if node.children:
            self.visit(node.children[0])
        
        # Process elif body (second child) in its own scope
        if len(node.children) > 1:
            self.symbol_table.enter_scope(f"elif_block_{self.current_line}_{self.current_column}")
            self.visit(node.children[1])
            self.symbol_table.exit_scope()
    
    def visit_else_clause(self, node) -> None:
        """Visit else clause node."""
        self.logger.debug("Processing else clause")
        # Enter else block scope
        self.symbol_table.enter_scope(f"else_block_{self.current_line}_{self.current_column}")
        
        # Process else body
        for child in node.children:
            self.visit(child)
        
        self.symbol_table.exit_scope()
    
    def visit_for_statement(self, node) -> None:
        """Visit for statement node."""
        self.logger.debug("Processing for statement")
        self.symbol_table.enter_scope(f"for_loop_{self.current_line}_{self.current_column}")

        # Check for iterator variable pattern: IDENTIFIER, type
        if (len(node.children) >= 2 and
            hasattr(node.children[0], 'type') and node.children[0].type == 'IDENTIFIER' and
            hasattr(node.children[1], 'data') and node.children[1].data == 'type'):
            name_token = node.children[0]
            type_tree = node.children[1]
            name = str(name_token.value)
            type_info = self.extract_type_from_tree(type_tree)
            self.symbol_table.declare(
                name=name,
                kind=SymbolKind.VARIABLE,
                type_info=type_info,
                line=self.current_line,
                column=self.current_column
            )
            # Visit the rest (collection, body, etc.)
            for child in node.children[2:]:
                self.visit(child)
        else:
            # Fallback: visit all children
            for child in node.children:
                self.visit(child)

        self.symbol_table.exit_scope()
    
    def visit_while_statement(self, node) -> None:
        """Visit while statement node."""
        self.logger.debug("Processing while statement")
        # Enter while loop scope
        self.symbol_table.enter_scope(f"while_loop_{self.current_line}_{self.current_column}")
        
        # Process all children (condition and body)
        for child in node.children:
            self.visit(child)
        
        self.symbol_table.exit_scope()
    
    def visit_try_statement(self, node) -> None:
        """Visit try statement node."""
        self.logger.debug("Processing try statement")
        # Enter try block scope
        self.symbol_table.enter_scope(f"try_block_{self.current_line}_{self.current_column}")
        
        # Process all children (try body, catch clauses, finally clause)
        for child in node.children:
            self.visit(child)
        
        self.symbol_table.exit_scope()
    
    def visit_match_statement(self, node) -> None:
        """Visit match statement node."""
        self.logger.debug("Processing match statement")
        # Enter match block scope
        self.symbol_table.enter_scope(f"match_block_{self.current_line}_{self.current_column}")
        # The first child is the expression being matched
        if node.children:
            match_expr = node.children[0]
            # Try to extract type from the match expression
            match_type = self._infer_type_of_expression(match_expr)
            self.logger.info(f"Pushing match type '{match_type}' onto stack for match statement at line {self.current_line}")
            self.match_type_stack.append(match_type)
        # Process all children (expression, case clauses, default clause)
        for child in node.children:
            self.visit(child)
        if node.children:
            self.match_type_stack.pop()
            self.logger.info(f"Popped match type for match statement at line {self.current_line}")
        self.symbol_table.exit_scope()
    
    def _infer_type_of_expression(self, expr_node) -> str:
        # Try to infer the type of an expression node (very basic for now)
        # If it's a variable, look it up in the symbol table
        if hasattr(expr_node, 'type') and expr_node.type == 'IDENTIFIER':
            name = str(expr_node.value)
            symbol = self.symbol_table.lookup(name)
            if symbol:
                return symbol.type
        # If it's a literal, return its type
        if hasattr(expr_node, 'type') and expr_node.type in ('NUMBER', 'STRING', 'BOOL'):
            if expr_node.type == 'NUMBER':
                return '#int'  # or '#float' if you distinguish
            if expr_node.type == 'STRING':
                return '#str'
            if expr_node.type == 'BOOL':
                return '#bool'
        # If it's a tree node with a type annotation
        if hasattr(expr_node, 'data') and expr_node.data == 'type':
            return self.extract_type_from_tree(expr_node)
        return 'unknown'
    
    def visit_function_body(self, node) -> None:
        """Visit function body node."""
        self.logger.debug("Processing function body")
        for child in node.children:
            self.visit(child)
    
    def visit_class_body(self, node) -> None:
        """Visit class body node."""
        self.logger.debug("Processing class body")
        # Print detailed children if this is MathUtility
        parent_scope = self.symbol_table.current_scope.name if self.symbol_table.current_scope else None
        if parent_scope and "MathUtility" in parent_scope:
            print(f"DEBUG MathUtility class_body children:")
            for idx, child in enumerate(node.children):
                print(f"  [{idx}] {child}")
        for child in node.children:
            is_static = getattr(child.meta, "is_static", False)
            is_override = getattr(child.meta, "is_override", False)
            access_modifier = getattr(child.meta, "access_modifier", None)
            print(f"DEBUG visit_class_body: is_static={is_static}, is_override={is_override}, access_modifier={access_modifier}, child={child}")
            # The actual member (property/method/constructor)
            member_node = child.children[0] if hasattr(child, "children") and child.children else child
            if hasattr(member_node, 'data'):
                print(f"DEBUG visit_class_body: member_node.data={member_node.data}")
                if member_node.data == "property_declaration":
                    self.visit_property_declaration_with_flags(member_node, is_static, access_modifier)
                elif member_node.data == "method_declaration":
                    self.visit_method_declaration_with_flags(member_node, is_static, is_override, access_modifier)
                elif member_node.data == "constructor_declaration":
                    self.visit_constructor_declaration(member_node)
                else:
                    self.visit(member_node)
            else:
                self.visit(member_node)
    
    def visit_type_body(self, node) -> None:
        """Visit type body node."""
        self.logger.debug("Processing type body")
        for child in node.children:
            self.visit(child)
    
    def visit_interface_body(self, node) -> None:
        """Visit interface body node."""
        self.logger.debug("Processing interface body")
        for child in node.children:
            self.visit(child)
    
    def visit_case_clause(self, node) -> None:
        """Visit case clause node."""
        self.logger.debug("Processing case clause")
        self.symbol_table.enter_scope(f"case_block_{self.current_line}_{self.current_column}")

        idx = 0
        # Handle pattern variable
        if len(node.children) > idx and hasattr(node.children[idx], 'data') and node.children[idx].data == 'pattern':
            pattern_node = node.children[idx]
            # TODO: Destructuring patterns (arrays, tuples, type-annotated, etc.)
            # Implementation Plan:
            # 1. If pattern_node is a simple identifier, handle as now.
            # 2. If pattern_node represents an array/tuple destructure, recursively process its children:
            #    - For arrays: assign element type from match_type (e.g., #[#int] => #int for each element)
            #    - For tuples: assign each element the corresponding tuple type
            # 3. If pattern_node is type-annotated, use the annotated type for the variable
            # 4. For nested patterns, recursively call this logic
            # 5. For each identifier found, declare it in the symbol table with the inferred type
            # 6. Add logging for each variable declared via destructuring
            # Example pseudocode:
            #   def handle_pattern(pattern_node, match_type):
            #       if is_identifier(pattern_node):
            #           declare variable with match_type
            #       elif is_array_pattern(pattern_node):
            #           for child in pattern_node.children:
            #               handle_pattern(child, element_type_of(match_type))
            #       elif is_tuple_pattern(pattern_node):
            #           for i, child in enumerate(pattern_node.children):
            #               handle_pattern(child, tuple_type_at(match_type, i))
            #       elif is_type_annotated_pattern(pattern_node):
            #           use annotated type
            #       # ...etc.
            #   handle_pattern(pattern_node, match_type)
            if (pattern_node.children and
                hasattr(pattern_node.children[0], 'type') and pattern_node.children[0].type == 'IDENTIFIER'):
                name_token = pattern_node.children[0]
                name = str(name_token.value)
                # Infer the type from the parent match expression
                match_type = self.match_type_stack[-1] if self.match_type_stack else 'unknown'
                self.logger.info(f"Assigning match case variable '{name}' type '{match_type}' at line {self.current_line}")
                self.symbol_table.declare(
                    name=name,
                    kind=SymbolKind.VARIABLE,
                    type_info=match_type,
                    line=self.current_line,
                    column=self.current_column
                )
            idx += 1

        # Handle guard (optional)
        if len(node.children) > idx and hasattr(node.children[idx], 'data') and node.children[idx].data == 'guard':
            self.visit(node.children[idx])
            idx += 1

        # Handle body (rest)
        for child in node.children[idx:]:
            self.visit(child)

        self.symbol_table.exit_scope()
    
    def visit_catch_clause(self, node) -> None:
        """Visit catch clause node."""
        if len(node.children) >= 3:
            error_name_token = node.children[0]
            error_type_tree = node.children[1]
            catch_body = node.children[2]
            
            if hasattr(error_name_token, 'type') and error_name_token.type == 'IDENTIFIER':
                error_name = str(error_name_token.value)
            else:
                error_name = str(error_name_token)
            
            error_type = self.extract_type_from_tree(error_type_tree)
            
            self.logger.debug(f"Processing catch clause: {error_name} : {error_type}")
            
            # Enter catch block scope
            self.symbol_table.enter_scope(f"catch_block_{self.current_line}_{self.current_column}")
            
            # Declare the error variable
            self.symbol_table.declare(
                name=error_name,
                kind=SymbolKind.VARIABLE,
                type_info=error_type,
                line=self.current_line,
                column=self.current_column
            )
            
            # Process catch body
            self.visit(catch_body)
            
            self.symbol_table.exit_scope()
    
    def visit_finally_clause(self, node) -> None:
        """Visit finally clause node."""
        self.logger.debug("Processing finally clause")
        # Enter finally block scope
        self.symbol_table.enter_scope(f"finally_block_{self.current_line}_{self.current_column}")
        
        for child in node.children:
            self.visit(child)
        
        self.symbol_table.exit_scope()
    
    def visit_enum_declaration(self, node) -> None:
        """Visit enum declaration node."""
        if len(node.children) >= 2:
            name_token = node.children[0]
            enum_body = node.children[1]
            
            if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
                name = str(name_token.value)
            else:
                name = str(name_token)
            
            self.logger.info(f"Processing enum declaration: {name}")
            
            self.symbol_table.declare(
                name=name,
                kind=SymbolKind.ENUM,
                type_info="enum",
                line=self.current_line,
                column=self.current_column
            )
            
            # Enter enum scope
            self.symbol_table.enter_scope(f"enum_{name}_{self.current_line}_{self.current_column}")
            
            # Process enum body
            self.visit(enum_body)
            
            self.symbol_table.exit_scope()
    
    def visit_enum_value(self, node) -> None:
        """Visit enum value node."""
        if len(node.children) >= 1:
            name_token = node.children[0]
            
            if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
                name = str(name_token.value)
            else:
                name = str(name_token)
            
            self.logger.debug(f"Processing enum value: {name}")
            
            self.symbol_table.declare(
                name=name,
                kind=SymbolKind.ENUM_VALUE,
                type_info="enum_value",
                line=self.current_line,
                column=self.current_column,
                is_const=True
            )
    
    def visit_constant_declaration(self, node) -> None:
        """Visit constant declaration node."""
        if len(node.children) >= 3:
            name_token = node.children[0]
            type_tree = node.children[1]
            value_expression = node.children[2]
            
            if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
                name = str(name_token.value)
            else:
                name = str(name_token)
            
            type_info = self.extract_type_from_tree(type_tree)
            
            self.logger.info(f"Processing constant declaration: {name} : {type_info}")
            
            self.symbol_table.declare(
                name=name,
                kind=SymbolKind.CONSTANT,
                type_info=type_info,
                line=self.current_line,
                column=self.current_column,
                is_const=True
            )
    
    def visit_module_declaration(self, node) -> None:
        """Visit module declaration node."""
        if len(node.children) >= 2:
            name_token = node.children[0]
            module_body = node.children[1]
            
            if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
                name = str(name_token.value)
            else:
                name = str(name_token)
            
            self.logger.info(f"Processing module declaration: {name}")
            
            self.symbol_table.declare(
                name=name,
                kind=SymbolKind.MODULE,
                type_info="module",
                line=self.current_line,
                column=self.current_column
            )
            
            # Enter module scope
            self.symbol_table.enter_scope(f"module_{name}_{self.current_line}_{self.current_column}")
            
            # Process module body
            self.visit(module_body)
            
            self.symbol_table.exit_scope()
    
    def visit_namespace_declaration(self, node) -> None:
        """Visit namespace declaration node."""
        if len(node.children) >= 2:
            name_token = node.children[0]
            namespace_body = node.children[1]
            
            if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
                name = str(name_token.value)
            else:
                name = str(name_token)
            
            self.logger.info(f"Processing namespace declaration: {name}")
            
            self.symbol_table.declare(
                name=name,
                kind=SymbolKind.NAMESPACE,
                type_info="namespace",
                line=self.current_line,
                column=self.current_column
            )
            
            # Enter namespace scope
            self.symbol_table.enter_scope(f"namespace_{name}_{self.current_line}_{self.current_column}")
            
            # Process namespace body
            self.visit(namespace_body)
            
            self.symbol_table.exit_scope()
    
    def visit_trait_declaration(self, node) -> None:
        """Visit trait declaration node."""
        if len(node.children) >= 2:
            name_token = node.children[0]
            trait_body = node.children[1]
            
            if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
                name = str(name_token.value)
            else:
                name = str(name_token)
            
            self.logger.info(f"Processing trait declaration: {name}")
            
            self.symbol_table.declare(
                name=name,
                kind=SymbolKind.TRAIT,
                type_info="trait",
                line=self.current_line,
                column=self.current_column
            )
            
            # Enter trait scope
            self.symbol_table.enter_scope(f"trait_{name}_{self.current_line}_{self.current_column}")
            
            # Process trait body
            self.visit(trait_body)
            
            self.symbol_table.exit_scope()
    
    def visit_implementation_declaration(self, node) -> None:
        """Visit implementation declaration node."""
        if len(node.children) >= 3:
            trait_name = str(node.children[0])
            type_name = str(node.children[1])
            impl_body = node.children[2]
            
            self.logger.info(f"Processing implementation: {trait_name} for {type_name}")
            
            self.symbol_table.declare(
                name=f"{trait_name}_for_{type_name}",
                kind=SymbolKind.IMPLEMENTATION,
                type_info=f"implementation of {trait_name} for {type_name}",
                line=self.current_line,
                column=self.current_column
            )
            
            # Enter implementation scope
            self.symbol_table.enter_scope(f"impl_{trait_name}_{type_name}_{self.current_line}_{self.current_column}")
            
            # Process implementation body
            self.visit(impl_body)
            
            self.symbol_table.exit_scope()
    
    def visit_alias_declaration(self, node) -> None:
        """Visit alias declaration node."""
        if len(node.children) >= 2:
            alias_name = str(node.children[0])
            original_name = str(node.children[1])
            
            self.logger.info(f"Processing alias: {alias_name} -> {original_name}")
            
            self.symbol_table.declare(
                name=alias_name,
                kind=SymbolKind.ALIAS,
                type_info=f"alias for {original_name}",
                line=self.current_line,
                column=self.current_column
            )
    
    def visit_generic_declaration(self, node) -> None:
        """Visit generic declaration node."""
        if len(node.children) >= 2:
            name_token = node.children[0]
            generic_params = node.children[1]
            
            if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
                name = str(name_token.value)
            else:
                name = str(name_token)
            
            self.logger.info(f"Processing generic declaration: {name}")
            
            # Extract generic parameters
            param_names = []
            if hasattr(generic_params, 'children'):
                for param in generic_params.children:
                    if hasattr(param, 'type') and param.type == 'IDENTIFIER':
                        param_names.append(str(param.value))
            
            self.symbol_table.declare(
                name=name,
                kind=SymbolKind.GENERIC,
                type_info="generic",
                line=self.current_line,
                column=self.current_column,
                generic_parameters=param_names
            )
    
    def visit_macro_declaration(self, node) -> None:
        """Visit macro declaration node."""
        if len(node.children) >= 2:
            name_token = node.children[0]
            macro_body = node.children[1]
            
            if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
                name = str(name_token.value)
            else:
                name = str(name_token)
            
            self.logger.info(f"Processing macro declaration: {name}")
            
            self.symbol_table.declare(
                name=name,
                kind=SymbolKind.MACRO,
                type_info="macro",
                line=self.current_line,
                column=self.current_column
            )
    
    def visit_annotation_declaration(self, node) -> None:
        """Visit annotation declaration node."""
        if len(node.children) >= 2:
            name_token = node.children[0]
            annotation_body = node.children[1]
            
            if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
                name = str(name_token.value)
            else:
                name = str(name_token)
            
            self.logger.info(f"Processing annotation declaration: {name}")
            
            self.symbol_table.declare(
                name=name,
                kind=SymbolKind.ANNOTATION,
                type_info="annotation",
                line=self.current_line,
                column=self.current_column
            )
    
    def visit_enum_body(self, node) -> None:
        """Visit enum body node."""
        self.logger.debug("Processing enum body")
        for child in node.children:
            self.visit(child)
    
    def visit_trait_body(self, node) -> None:
        """Visit trait body node."""
        self.logger.debug("Processing trait body")
        for child in node.children:
            self.visit(child)
    
    def visit_implementation_body(self, node) -> None:
        """Visit implementation body node."""
        self.logger.debug("Processing implementation body")
        for child in node.children:
            self.visit(child)

    def visit_property_declaration_with_flags(self, node, is_static, access_modifier):
        if len(node.children) >= 2:
            name_token = node.children[0]
            type_tree = node.children[1]
            if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
                name = str(name_token.value)
            else:
                name = str(name_token)
            type_info = self.extract_type_from_tree(type_tree)
            print(f"DEBUG DECLARE PROPERTY: {name}, static={is_static}, access={access_modifier}")
            self.logger.info(f"Processing property declaration: {name} : {type_info}")
            self.symbol_table.declare(
                name=name,
                kind=SymbolKind.PROPERTY,
                type_info=type_info,
                line=self.current_line,
                column=self.current_column,
                is_static=is_static,
                access_modifier=access_modifier
            )

    def visit_method_declaration_with_flags(self, node, is_static, is_override, access_modifier):
        if len(node.children) >= 4:
            name_token = node.children[0]
            param_list = node.children[1]
            return_type_tree = node.children[2]
            method_body = node.children[3]
            if hasattr(name_token, 'type') and name_token.type == 'IDENTIFIER':
                name = str(name_token.value)
            else:
                name = str(name_token)
            return_type = self.extract_type_from_tree(return_type_tree)
            print(f"DEBUG DECLARE METHOD: {name}, static={is_static}, override={is_override}, access={access_modifier}")
            self.logger.info(f"Processing method declaration: {name} -> {return_type}")
            self.symbol_table.declare(
                name=name,
                kind=SymbolKind.METHOD,
                type_info=return_type,
                line=self.current_line,
                column=self.current_column,
                is_static=is_static,
                is_override=is_override,
                access_modifier=access_modifier
            )
            self.symbol_table.enter_scope(f"method_{name}_{self.current_line}_{self.current_column}")
            if hasattr(param_list, 'children') and param_list.children:
                self.visit_parameter_list(param_list)
            self.visit(method_body)
            self.symbol_table.exit_scope()


def generate_symbol_table_from_file(file_path: str) -> SymbolTable:
    """Generate symbol table from a Sugar file."""
    from sugar_parser import SugarParser
    
    parser = SugarParser()
    ast = parser.parse_file(file_path)
    
    generator = SymbolTableGenerator()
    symbol_table = generator.generate(ast)
    
    return symbol_table


def main():
    """Main entry point for testing symbol table generation."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: uv run symbol_table.py <sugar_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        symbol_table = generate_symbol_table_from_file(file_path)
        
        if symbol_table.has_errors():
            print("Symbol table generation completed with errors:")
            for error in symbol_table.get_errors():
                print(f"  ERROR: {error}")
        else:
            print("Symbol table generation completed successfully!")
        
        print(f"\nTotal symbols found: {len(symbol_table.get_all_symbols())}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 