# Sugar Programming Language

A statically typed programming language with emphasis on readability and expressive syntax. Sugar combines strong typing with syntactic sugar to make code both robust and pleasant to write.

## Features

- **Strong Static Typing:** All variables must be explicitly typed at declaration time
- **Syntactic Sugar:** Rich set of operators and shorthand notations
- **Readability:** Clear syntax with minimal boilerplate
- **Type Safety:** Comprehensive type checking at compile time
- **Object-Oriented Programming:** Classes, inheritance, and interfaces
- **Functional Programming:** Higher-order functions, pipelines, and pattern matching
- **Concurrency:** First-class support for concurrent programming

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd Sugar

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running Sugar Programs

```bash
# Run a Sugar program
python sugar.py run program.sugar

# Compile to bytecode
python sugar.py compile program.sugar

# Type check only
python sugar.py typecheck program.sugar
```

### Example Programs

See the `examples/` directory for sample programs demonstrating various language features.

## Language Features

### Basic Syntax

```sugar
DEF variable_name #type = value

FUNC function_name(param1 #type1, param2 #type2) #return_type
    // function body
    RETURN value
END FUNC
```

### Type System

- **Primitive Types:** `#int`, `#float`, `#bool`, `#char`, `#str`
- **Composite Types:** `#[#type]`, `#{#key_type, #value_type}`, `#(#type1, #type2, ...)`
- **Custom Types:** User-defined types with the `TYPE` keyword

### Syntactic Sugar

- Collection operations: `:ADD:`, `:REMOVE:`, `:GET:`, `:REVERSE:`, `:LENGTH:`
- String operations: `:UPPER:`, `:LOWER:`, `:SPLIT:`
- Comparison operators: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Pipeline operator: `:>` for functional composition

## Project Structure

```
Sugar/
├── src/
│   ├── lexer.py          # Tokenizer for Sugar syntax
│   ├── parser.py         # Abstract Syntax Tree construction
│   ├── type_checker.py   # Static type checking
│   ├── interpreter.py    # Runtime execution
│   ├── compiler.py       # Bytecode compilation
│   └── stdlib.py         # Standard library functions
├── examples/             # Sample programs
├── tests/               # Test suite
├── sugar.py             # Main entry point
└── requirements.txt     # Python dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
