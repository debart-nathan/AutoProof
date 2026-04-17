"""Parser for Python boolean expressions to logical formulas."""

import ast
from typing import List, Optional
from .formulas import (
    Atomic, Equivalence, Implication, Conjunction,
    Disjunction, Bottom, Negation, Universal, Existential
)
from .interfaces.parser_interface import ParserInterface
from .interfaces.formula import Formula


class PythonParser(ParserInterface):
    """
    Improved parser for Python boolean expressions and code.
    Produces cleaner logical formulas with structured arithmetic and comparisons.
    """

    # -----------------------------
    # Public API
    # -----------------------------
    def parse(self, code: str) -> Formula:
        return self.parse_expression(code)

    def parse_expression(self, code: str) -> Formula:
        tree = ast.parse(code, mode='eval')
        return self._visit(tree.body)

    # -----------------------------
    # Core visitor
    # -----------------------------
    def _visit(self, node: ast.AST) -> Formula:

        # Boolean operators
        if isinstance(node, ast.BoolOp):
            return self._visit_boolop(node)

        # Negation
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return Negation(self._visit(node.operand))

        # Ternary: a if cond else b
        if isinstance(node, ast.IfExp):
            return self._visit_ifexp(node)

        # Variables
        if isinstance(node, ast.Name):
            return Atomic(node.id)

        # Constants
        if isinstance(node, ast.Constant):
            return self._visit_constant(node)

        # Comparisons: ==, !=, <, >, <=, >=
        if isinstance(node, ast.Compare):
            return self._visit_compare(node)

        # Arithmetic: +, -, *, /
        if isinstance(node, ast.BinOp):
            return self._visit_binop(node)

        # Function calls
        if isinstance(node, ast.Call):
            return self._visit_call(node)

        # Assignments inside function bodies
        if isinstance(node, ast.Assign):
            return self._visit_assign(node)

        # If statements
        if isinstance(node, ast.If):
            return self._visit_if(node)

        # For loops → ∀
        if isinstance(node, ast.For):
            return self._visit_for(node)

        # While loops → implication
        if isinstance(node, ast.While):
            return self._visit_while(node)

        # Return
        if isinstance(node, ast.Return):
            return self._visit(node.value) if node.value else Atomic("return")

        # Expression wrapper
        if isinstance(node, ast.Expr):
            return self._visit(node.value)

        # Pass
        if isinstance(node, ast.Pass):
            return Atomic("pass")

        raise ValueError(f"Unsupported AST node: {type(node)}")

    # -----------------------------
    # Helpers
    # -----------------------------
    def _visit_boolop(self, node: ast.BoolOp) -> Formula:
        left = self._visit(node.values[0])
        for val in node.values[1:]:
            right = self._visit(val)
            if isinstance(node.op, ast.And):
                left = Conjunction(left, right)
            else:
                left = Disjunction(left, right)
        return left

    def _visit_ifexp(self, node: ast.IfExp) -> Formula:
        cond = self._visit(node.test)
        t = self._visit(node.body)
        f = self._visit(node.orelse)
        return Conjunction(
            Implication(cond, t),
            Implication(Negation(cond), f),
        )

    def _visit_constant(self, node: ast.Constant) -> Formula:
        if node.value is True:
            return Atomic("True")
        if node.value is False:
            return Bottom()
        return Atomic(str(node.value))

    def _visit_compare(self, node: ast.Compare) -> Formula:
        left = self._visit(node.left)
        right = self._visit(node.comparators[0])
        op = node.ops[0]

        op_map = {
            ast.Eq: "Eq",
            ast.NotEq: "NotEq",
            ast.Lt: "Lt",
            ast.Gt: "Gt",
            ast.LtE: "Le",
            ast.GtE: "Ge",
        }

        op_name = op_map.get(type(op), type(op).__name__)
        return Atomic(f"{op_name}({left}, {right})")

    def _visit_binop(self, node: ast.BinOp) -> Formula:
        left = self._visit(node.left)
        right = self._visit(node.right)

        op_map = {
            ast.Add: "Add",
            ast.Sub: "Sub",
            ast.Mult: "Mul",
            ast.Div: "Div",
        }

        op_name = op_map.get(type(node.op), type(node.op).__name__)
        return Atomic(f"{op_name}({left}, {right})")

    def _visit_call(self, node: ast.Call) -> Formula:
        func = self._visit(node.func)
        args = [self._visit(a) for a in node.args]
        args_str = ", ".join(str(a) for a in args)
        return Atomic(f"{func}({args_str})")

    def _visit_assign(self, node: ast.Assign) -> Formula:
        target = node.targets[0]
        if isinstance(target, ast.Name):
            value = self._visit(node.value)
            return Atomic(f"Eq({target.id}, {value})")
        raise ValueError("Unsupported assignment target")

    def _visit_if(self, node: ast.If) -> Formula:
        cond = self._visit(node.test)
        body = self._visit_stmts(node.body)
        orelse = self._visit_stmts(node.orelse) if node.orelse else Atomic("True")
        return Conjunction(
            Implication(cond, body),
            Implication(Negation(cond), orelse),
        )

    def _visit_for(self, node: ast.For) -> Formula:
        if isinstance(node.target, ast.Name):
            var = node.target.id
            body = self._visit_stmts(node.body)
            return Universal(var, body)
        raise ValueError("Unsupported for-loop target")

    def _visit_while(self, node: ast.While) -> Formula:
        cond = self._visit(node.test)
        body = self._visit_stmts(node.body)
        return Implication(cond, body)

    def _visit_stmts(self, stmts: List[ast.stmt]) -> Formula:
        if not stmts:
            return Atomic("True")
        f = None
        for stmt in stmts:
            part = self._visit(stmt)
            f = part if f is None else Conjunction(f, part)
        return f

    def parse_function(self, code: str) -> Formula:
        tree = ast.parse(code)
        func = tree.body[0]
        return self._visit_stmts(func.body)
