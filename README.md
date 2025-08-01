# Sugar Programming Language

Sugar is a modern, statically-typed, object-oriented scripting language designed for clarity and expressiveness. It combines familiar concepts from popular languages with a unique syntax to create a powerful and developer-friendly experience.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Language Syntax](#language-syntax)
  - [Variables and Types](#variables-and-types)
  - [Data Structures](#data-structures)
  - [Control Flow](#control-flow)
  - [Functions](#functions)
  - [Object-Oriented Programming (OOP)](#object-oriented-programming-oop)
  - [Pattern Matching](#pattern-matching)
  - [Error Handling](#error-handling)
  - [Concurrency](#concurrency)
  - [Imports](#imports)
  - [Standard Library](#standard-library)
- [Running Tests](#running-tests)
- [Contributing](#contributing)

## Features

- **Static Typing:** All variables and functions have explicit types, catching errors before runtime.
- **Object-Oriented:** Supports classes, inheritance, interfaces, and access modifiers.
- **Rich Data Structures:** Built-in support for arrays, maps, and tuples with a wealth of operations.
- **Powerful Control Flow:** Includes `if/elif/else`, `for` loops, `while` loops, and an advanced `MATCH` statement.
- **Concurrency:** Simple-to-use concurrency model with `SPAWN` and `JOIN`.
- **Error Handling:** Robust `TRY/CATCH/FINALLY` mechanism with custom error types.
- **Modular:** Support for importing code from other files.
- **Expressive Syntax:** A clean and readable syntax that aims to reduce boilerplate.

## Project Structure

The project is organized as follows:

```
/
├── src/                # Interpreter source code (Python)
│   ├── sugar.py        # Main entry point
│   ├── parser.py       # Language parser
│   ├── interpreter.py  # Language interpreter
│   ├── ast_nodes.py    # Abstract Syntax Tree definitions
│   └── ...
├── examples/           # Example .sugar files
│   └── interpreting_tests/ # Suite of syntax examples
├── tests/              # Test suite for the interpreter
│   ├── test_parser.py
│   └── test_interpreter.py
├── pyproject.toml      # Project dependencies
├── uv.lock             # Pinned dependency versions
└── README.md           # This file
```

## Installation

This project uses `uv` for environment and package management.

1.  **Install `uv`:** If you don't have it, follow the official installation instructions for `uv`.
2.  **Set up the environment:** Run the following command in the project root. This will create a virtual environment and install the dependencies from `pyproject.toml`.
    ```bash
    uv sync
    ```

## Usage

To run a Sugar program, use the main `sugar` command followed by the path to the file:

```bash
sugar examples/interpreting_tests/01_var_decl.sugar
```

For development, you can also run the interpreter directly with `uv`:

```bash
uv run python src/sugar.py examples/interpreting_tests/01_var_decl.sugar
```

## Language Syntax

### Variables and Types

Variables are declared with `DEF`, a name, a type, and an initial value. Re-assignment uses the `:=` operator.

**Primitive Types:** `#int`, `#float`, `#bool`, `#char`, `#str`

```sugar
DEF x #int = 10
DEF message #str = "Hello, Sugar!"
DEF is_active #bool = :T:

x := 20 // Re-assign value
```

### Data Structures

#### Arrays

Arrays are ordered collections.

```sugar
DEF numbers #[#int] = [1, 2, 3, 4, 5]
numbers :ADD: (6)
DEF first #int = numbers :GET: (0)
DEF length #int = numbers :LENGTH: ()
```

#### Maps

Maps are key-value stores.

```sugar
DEF scores #{#str, #int} = {"Alice" -> 100, "Bob" -> 95}
scores :SET: ("Charlie", 98)
DEF bobs_score #int = scores :GET: ("Bob")
```

#### Tuples

Tuples are fixed-size, ordered collections.

```sugar
DEF person #(#str, #int) = ("Alice", 30)
```

### Control Flow

Boolean conditions in control flow are wrapped in `$`.

```sugar
// If/Elif/Else
if $x > 10$ do
    IO:PRINT:("x is large")
elif $x > 5$ do
    IO:PRINT:("x is medium")
else do
    IO:PRINT:("x is small")
end

// For Loop
DEF sum #int = 0
for DEF n #int in [1, 2, 3] do
    sum := sum + n
end

// While Loop
DEF i #int = 0
while $i < 5$ do
    i := i + 1
end
```

### Functions

Functions are declared with `FUNC`. They require typed parameters and a return type (`#void` if nothing is returned).

```sugar
FUNC add(a #int, b #int) #int
    RETURN a + b
end

DEF result #int = add(5, 3) // result is 8
```

### Object-Oriented Programming (OOP)

Sugar is fully object-oriented.

```sugar
CLASS Adder
    value #int
    CONSTRUCTOR()
        DEF THIS.value #int = 0
    end
    FUNC add(x #int) #int
        THIS.value := THIS.value + x
        RETURN THIS.value
    end
end

DEF a #Adder = Adder()
a:add:(5)
a:add:(10) // a.value is now 15
```

It also supports `EXTENDS` for inheritance, `INTERFACE` and `IMPLEMENTS` for polymorphism, and `STATIC` methods.

### Pattern Matching

The `MATCH` statement is a powerful way to control flow based on the structure of data.

```sugar
DEF my_var #int = 2
DEF result #str = ""

MATCH my_var
    CASE 1 do
        result := "one"
    CASE n if $n % 2 == 0$ do // Case with a guard
        result := "an even number"
    DEFAULT do
        result := "something else"
end
```

### Error Handling

Handle runtime errors with a `TRY/CATCH/FINALLY` block.

```sugar
TYPE MyError EXTENDS Error
    message #str
end

FUNC risky() #void
    THROW MyError("fail!")
end

TRY
    risky()
CATCH e #MyError do
    IO:PRINT:("Caught error: " + e.message)
FINALLY do
    IO:PRINT:("Execution finished.")
end
```

### Concurrency

Run functions concurrently using `SPAWN`.

```sugar
FUNC compute() #int
    RETURN 42
end

DEF task #Task = SPAWN FUNC() #int RETURN compute() end
DEF result #int = task:JOIN:() // Waits for the task to finish and gets the result
```

### Imports

Organize your code into multiple files and import them.

```sugar
// In imported_module.sugar
DEF m #{#str, #int} = {"a"->5}

// In main.sugar
import imported_module.m
DEF r #int = m:GET:("a") // r is 5
```

### Standard Library

Sugar has a standard library for common tasks.

-   `IO`: `PRINT`, `INPUT`
-   `Math`: `SQRT`, `POW`, `SIN`, `PI`, etc.
-   `Time`: `NOW_STR`, `FORMAT_STR`
-   `Random`: `INT`, `FLOAT`, `SEED`

## Running Tests

The project has a suite of tests for the interpreter. To run all tests, use `pytest`:

```bash
uv run pytest
```

To run a specific test file:

```bash
uv run pytest tests/test_parser.py
```

## Contributing

Contributions are welcome! Please feel free to open an issue on the project's repository to report bugs or suggest features.
