"""Arithmetic not equal formula."""

from typing import Optional, Tuple, List
from ...interfaces.formula import Formula

class NotEq(Formula):
    """Represents arithmetic not-equal."""

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"({self.left} != {self.right})"

    def __eq__(self, other) -> bool:
        return isinstance(other, NotEq) and self.left == other.left and self.right == other.right

    def __hash__(self) -> int:
        return hash((self.left, self.right, 'not_eq'))

    def substitute(self, var, term):
        return NotEq(
            self.left.substitute(var, term),
            self.right.substitute(var, term)
        )

    def apply_right(self, sequent) -> Optional[Tuple[List, str]]:
        return None

    def apply_left(self, sequent) -> Optional[Tuple[List, str]]:
        return None