from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from lark import LarkError
from lark.tree import Meta

from src.static_analysis import StaticError


if TYPE_CHECKING:
    from src.ast_nodes import Node


class ErrorReporter:
    def __init__(self, source_code: str, file_path: str):
        self.source_code = source_code
        self.file_path = file_path
        self.lines = source_code.splitlines()

    def _print_error(self, message: str, line: int | None, column: int | None):
        formatted = self._format_error(
            message, line if line else 0, column if column else 0
        )
        print(formatted, file=sys.stderr)

    def _format_error(self, message: str, line: int, column: int) -> str:
        """Return a detailed error message with code context."""
        header = f"Error in {self.file_path} at line {line}, column {column}:"
        error_line = self.lines[line - 1] if 0 < line <= len(self.lines) else ""
        pointer = " " * (column - 1) + "^" if column > 0 else ""
        return f"\n{header}\n{message}\n\n  {error_line}\n  {pointer}\n"

    def _extract_meta_position(self, error: Exception) -> tuple[int, int]:
        """Try to extract (line, column) from an error's args if Meta is present."""
        if len(error.args) > 1 and isinstance(error.args[1], Meta):
            return error.args[1].line, error.args[1].column
        return 0, 0

    def report_syntactic(self, error: LarkError):
        """Report a syntax error raised by Lark."""
        line, column = self._extract_meta_position(error)
        self._print_error(str(error), line, column)

    def report_static(self, error: StaticError):
        """Report a static analysis error."""
        line, column = self._extract_meta_position(error)
        self._print_error(str(error), line, column)

    def report_semantic(self, message: str, node: Node):
        """Report a semantic error (detected during analysis)."""
        if not getattr(node, "meta", None):
            print(
                f"Semantic Error in {self.file_path}: {message} (no location info)",
                file=sys.stderr,
            )
            return
        self._print_error(
            message,
            node.meta.line if node.meta else None,
            node.meta.column if node.meta else None,
        )

    def report_runtime(self, message: str, node: Node | None):
        """Report a runtime error (detected during execution)."""
        if not node or not getattr(node, "meta", None):
            print(
                f"Runtime Error in {self.file_path}: {message} (no location info)",
                file=sys.stderr,
            )
            return
        self._print_error(
            message,
            node.meta.line if node.meta else None,
            node.meta.column if node.meta else None,
        )
