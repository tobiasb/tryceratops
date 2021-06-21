import ast

from tryceratops.violations import Violation, codes

from .base import BaseAnalyzer, visit_error_handler


class ExceptReraiseWithoutCauseAnalyzer(BaseAnalyzer, ast.NodeVisitor):
    @visit_error_handler
    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        def is_raise_without_cause(node: ast.stmt):
            if isinstance(node, ast.Raise):
                return isinstance(node.exc, ast.Call) and node.cause is None
            return False

        reraises_no_cause = [stm for stm in node.body if is_raise_without_cause(stm)]
        violations = [
            Violation.build(self.filename, codes.RERAISE_NO_CAUSE, block)
            for block in reraises_no_cause
        ]
        self.violations += violations

        self.generic_visit(node)


class ExceptVerboseReraiseAnalyzer(BaseAnalyzer, ast.NodeVisitor):
    @visit_error_handler
    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        def is_raise_with_name(stm: ast.stmt, name: str):
            if isinstance(stm, ast.Raise) and isinstance(stm.exc, ast.Name):
                return stm.exc.id == name
            return False

        # If no name is set, then it's impossible to be verbose
        # since you don't have the object
        if node.name:
            for child in ast.walk(node):
                if is_raise_with_name(child, node.name):
                    violation = Violation.build(
                        self.filename, codes.VERBOSE_RERAISE, child
                    )
                    self.violations.append(violation)

        self.generic_visit(node)
