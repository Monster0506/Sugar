import sys
import os
import types
from symbol_table import SymbolTable, SymbolKind, SymbolInfo

# Helper to create a minimal symbol table with some scopes and symbols
def make_sample_table():
    st = SymbolTable()
    st.declare('x', SymbolKind.VARIABLE, 'int', 1, 1)
    st.declare('y', SymbolKind.VARIABLE, 'float', 2, 1)
    st.enter_scope('func')
    st.declare('f', SymbolKind.FUNCTION, 'int->int', 3, 1)
    st.declare('z', SymbolKind.VARIABLE, 'int', 4, 1)
    st.exit_scope()
    st.enter_scope('class')
    st.declare('C', SymbolKind.CLASS, 'class', 5, 1)
    st.exit_scope()
    return st

def test_get_current_scope_symbols():
    st = make_sample_table()
    # Should be global scope after all exits
    syms = st.get_current_scope_symbols()
    assert 'x' in syms and 'y' in syms
    assert 'f' not in syms

def test_get_scope_name_and_depth():
    st = make_sample_table()
    assert st.get_scope_name() == 'global'
    assert st.get_scope_depth() == 0
    st.enter_scope('inner')
    assert st.get_scope_name() == 'inner'
    assert st.get_scope_depth() == 1
    st.exit_scope()
    assert st.get_scope_name() == 'global'
    assert st.get_scope_depth() == 0

def test_get_qualified_name():
    st = make_sample_table()
    all_syms = st.get_all_symbols()
    for qname, sym in all_syms.items():
        qualified = st.get_qualified_name(sym)
        assert qualified.endswith(sym.name)
        assert sym.name in qualified

def test_get_symbol_statistics():
    st = make_sample_table()
    stats = st.get_symbol_statistics()
    assert stats['variable'] >= 3
    assert stats['function'] >= 1
    assert stats['class'] >= 1

def test_get_scope_statistics():
    st = make_sample_table()
    stats = st.get_scope_statistics()
    assert 'global' in stats
    assert 'func' in stats
    assert 'class' in stats
    assert stats['global'] >= 2

def test_get_symbols_by_kind_and_type():
    st = make_sample_table()
    vars = st.get_symbols_by_kind(SymbolKind.VARIABLE)
    assert any(s.name == 'x' for s in vars)
    ints = st.get_symbols_by_type('int')
    assert any(s.name == 'x' for s in ints)

def test_export_symbols():
    st = make_sample_table()
    d = st.export_symbols('dict')
    assert isinstance(d, dict)
    flat = st.export_symbols('flat')
    assert isinstance(flat, dict)
    s = st.export_symbols('str')
    assert isinstance(s, str)
    try:
        st.export_symbols('unknown')
        assert False, 'Expected ValueError for unknown format'
    except ValueError:
        pass

def test_real_files_in_examples():
    from sugar_parser import SugarParser
    from symbol_table import SymbolTableGenerator
    example_dir = os.path.join(os.path.dirname(__file__), 'examples')
    files = [f for f in os.listdir(example_dir) if f.endswith('.sugar')]
    assert files, 'No .sugar files found in examples/'
    parser = SugarParser()
    for fname in files:
        path = os.path.join(example_dir, fname)
        print(f'Parsing and generating symbol table for: {fname}')
        ast = parser.parse_file(path)
        generator = SymbolTableGenerator()
        st = generator.generate(ast)
        # Run API checks
        stats = st.get_symbol_statistics()
        scope_stats = st.get_scope_statistics()
        all_syms = st.get_all_symbols()
        print(f'  Symbol kinds: {stats}')
        print(f'  Scopes: {scope_stats}')
        print(f'  Total symbols: {len(all_syms)}')
        # Check that API methods do not raise
        st.get_current_scope_symbols()
        st.get_scope_name()
        st.get_scope_depth()
        st.export_symbols('dict')
        st.export_symbols('flat')
        st.export_symbols('str')
        # Try kind/type queries for a few kinds
        for kind in [SymbolKind.VARIABLE, SymbolKind.FUNCTION, SymbolKind.CLASS]:
            st.get_symbols_by_kind(kind)
        st.get_symbols_by_type('int')
        # Qualified name check for all
        for sym in all_syms.values():
            st.get_qualified_name(sym)
        print(f'  {fname} symbol table API checks passed.')

if __name__ == '__main__':
    # Run all tests manually
    test_get_current_scope_symbols()
    test_get_scope_name_and_depth()
    test_get_qualified_name()
    test_get_symbol_statistics()
    test_get_scope_statistics()
    test_get_symbols_by_kind_and_type()
    test_export_symbols()
    test_real_files_in_examples()
    print('All SymbolTable API tests passed.') 