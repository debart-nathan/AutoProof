"""Parser for Python boolean expressions to logical formulas."""

import ast
from .formulas import (
    Atomic, Equivalence, Implication, Conjunction,
    Disjunction, Bottom, Negation, Universal, Existential
)
from .interfaces.parser_interface import ParserInterface


class PythonParser(ParserInterface):
    """
    Parses Python boolean expressions and code into logical formulas.
    
    Examples:
        a and (not b)  →  Conjunction(Atomic('a'), Negation(Atomic('b')))
        x == y         →  Equivalence(Atomic('x'), Atomic('y'))
    """
    
    def parse(self, code: str):
        """Interface method: parse Python code as expression."""
        return self.parse_expression(code)
    
    def parse_expression(self, code: str):
        """Parse a Python boolean expression into a logical formula."""
        tree = ast.parse(code, mode='eval')
        return self._visit(tree.body)

    def _visit(self, node):
        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                left = self._visit(node.values[0])
                for val in node.values[1:]:
                    right = self._visit(val)
                    left = Conjunction(left, right)
                return left
            elif isinstance(node.op, ast.Or):
                left = self._visit(node.values[0])
                for val in node.values[1:]:
                    right = self._visit(val)
                    left = Disjunction(left, right)
                return left
        elif isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.Not):
                return Negation(self._visit(node.operand))
        elif isinstance(node, ast.IfExp):
            cond = self._visit(node.test)
            true_val = self._visit(node.body)
            false_val = self._visit(node.orelse)
            return Conjunction(Implication(cond, true_val), Implication(Negation(cond), false_val))
        elif isinstance(node, ast.Name):
            return Atomic(node.id)
        elif isinstance(node, ast.Constant):
            if node.value is False:
                return Bottom()
            elif node.value is True:
                # Treat True as a proposition
                return Atomic("True")
            else:
                return Atomic(str(node.value))
        elif isinstance(node, ast.Compare):
            left = self._visit(node.left)
            if len(node.ops) == 1 and len(node.comparators) == 1:
                right = self._visit(node.comparators[0])
                op = node.ops[0]
                if isinstance(op, ast.Eq):
                    return Equivalence(left, right)
                elif isinstance(op, ast.NotEq):
                    return Negation(Equivalence(left, right))
            # Treat other comparisons as atomic propositions
            comparators = [self._visit(c) for c in node.comparators]
            ops = [type(op).__name__ for op in node.ops]
            comp_str = f"{left}"
            for op_name, comp in zip(ops, comparators):
                comp_str += f" {op_name} {comp}"
            return Atomic(comp_str)
        elif isinstance(node, ast.BinOp):
            left = self._visit(node.left)
            right = self._visit(node.right)
            op = type(node.op).__name__
            return Atomic(f"{left} {op} {right}")
        elif isinstance(node, ast.Call):
            func = self._visit(node.func)
            args = [self._visit(arg) for arg in node.args]
            args_str = ", ".join(str(a) for a in args)
            return Atomic(f"{func}({args_str})")
        elif isinstance(node, ast.Assign):
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                target = node.targets[0].id
                value = self._visit(node.value)
                return Atomic(f"{target} = {value}")
            else:
                raise ValueError("Unsupported assignment")
        elif isinstance(node, ast.If):
            cond = self._visit(node.test)
            body_f = self._visit_stmts(node.body)
            orelse_f = self._visit_stmts(node.orelse) if node.orelse else Atomic("True")
            return Conjunction(Implication(cond, body_f), Implication(Negation(cond), orelse_f))
        elif isinstance(node, ast.For):
            if isinstance(node.target, ast.Name):
                var = node.target.id
                body_f = self._visit_stmts(node.body)
                return Universal(var, body_f)
            else:
                raise ValueError("Unsupported for loop target")
        elif isinstance(node, ast.While):
            cond = self._visit(node.test)
            body_f = self._visit_stmts(node.body)
            return Implication(cond, body_f)
        elif isinstance(node, ast.Return):
            if node.value:
                return self._visit(node.value)
            else:
                return Atomic("return")
        elif isinstance(node, ast.Expr):
            return self._visit(node.value)
        elif isinstance(node, ast.Pass):
            return Atomic("pass")
        else:
            raise ValueError(f"Unsupported AST node: {type(node)}")

    def _visit_stmts(self, stmts):
        """Visit a list of statements and combine them with conjunction."""
        if not stmts:
            return Atomic("True")
        formula = None
        for stmt in stmts:
            f = self._visit(stmt)
            if formula is None:
                formula = f
            else:
                formula = Conjunction(formula, f)
        return formula

    def parse_function(self, code: str):
        """Parse a Python function definition and extract the logical formula from the body statements."""
        tree = ast.parse(code)
        if not tree.body or not isinstance(tree.body[0], ast.FunctionDef):
            raise ValueError("No function definition found")
        func_def = tree.body[0]
        return self._visit_stmts(func_def.body)
        return self._visit_stmts(func_def.body)