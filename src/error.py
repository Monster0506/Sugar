from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from lark import LarkError

if TYPE_CHECKING:
    from src.ast_nodes import Node


class ErrorReporter:
    def __init__(self, source_code: str, file_path: str):
        self.source_code = source_code
        self.file_path = file_path
        self.lines = source_code.splitlines()

    def _format_error(self, message: str, line: int, column: int) -> str:
        """Formats a detailed error message with code context."""
        header = f"Error in {self.file_path} at line {line}, column {column}:"
        error_line = self.lines[line - 1]
        pointer = " " * (column - 1) + "^"

        return f"\n{header}\n{message}\n\n  {error_line}\n  {pointer}\n"

    def report_syntactic(self, error: LarkError):
        """Reports a syntax error from Lark."""
        message = str(error)
        line = getattr(error, "line", 1)
        column = getattr(error, "column", 1)
        formatted_error = self._format_error(message, line, column)
        print(formatted_error, file=sys.stderr)

    def report_semantic(self, message: str, node: Node):
        """Reports a semantic error from the StaticAnalyzer."""
        if not node.meta:
            print(
                f"Semantic Error in {self.file_path}: {message} (no location info)",
                file=sys.stderr,
            )
            return

        line = node.meta.line
        column = node.meta.column
        formatted_error = self._format_error(message, line, column)
        print(formatted_error, file=sys.stderr)

    def report_runtime(self, message: str, node: Node | None):
        """Reports a runtime error from the Interpreter."""
        if not node or not node.meta:
            print(
                f"Runtime Error in {self.file_path}: {message} (no location info)",
                file=sys.stderr,
            )
            return

        line = node.meta.line
        column = node.meta.column
        formatted_error = self._format_error(message, line, column)
        print(formatted_error, file=sys.stderr)
