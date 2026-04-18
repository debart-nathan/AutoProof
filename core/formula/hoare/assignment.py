"""Hoare assignment rule."""

from typing import Optional, Tuple, List
from ...interfaces.formula import Formula


class Assignment(Formula):
    """Represents a Hoare assignment command."""

    def __init__(self, variable, expression):
        self.variable = variable
        self.expression = expression

    def __str__(self) -> str:
        return f"{self.variable} := {self.expression}"

    def __eq__(self, other) -> bool:
        return (isinstance(other, Assignment) and
                self.variable == other.variable and
                self.expression == other.expression)

    def __hash__(self) -> int:
        return hash((self.variable, self.expression, 'assign'))

    def substitute(self, var, term):
        return Assignment(self.variable, self.expression)

    def apply_right(self, sequent) -> Optional[Tuple[List, str]]:
        return None

    def apply_left(self, sequent) -> Optional[Tuple[List, str]]:
        return None
