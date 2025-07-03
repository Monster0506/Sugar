import logging
from .environment import SugarEnvironment, SugarCallFrame
from .statement_handler import StatementHandler

class SugarInterpreter:
    def __init__(self, ast, symbol_table):
        self.ast = ast
        self.symbol_table = symbol_table
        self.global_env = SugarEnvironment()
        self.call_stack = []
        self.logger = logging.getLogger("SugarInterpreter")
        self.statement_handler = StatementHandler(self.logger)
    def run(self):
        self.logger.info("Interpreter started.")
        if hasattr(self.ast, 'data') and self.ast.data == 'program':
            for stmt in self.ast.children:
                self.statement_handler.handle_statement(stmt, self.global_env)
        self.logger.info(f"Global environment after execution: {self.global_env}") 