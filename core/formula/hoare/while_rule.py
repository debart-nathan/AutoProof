"""Hoare while loop rule."""

from typing import Optional, Tuple, List
from ...interfaces.formula import Formula


class WhileRule(Formula):
    """Represents a Hoare while loop rule."""

    def __init__(self, invariant, condition, body):
        self.invariant = invariant
        self.condition = condition
        self.body = body

    def __str__(self) -> str:
        return f"while ({self.condition}) {{ {self.body} }} [inv: {self.invariant}]"

    def __eq__(self, other) -> bool:
        return (isinstance(other, WhileRule) and
                self.invariant == other.invariant and
                self.condition == other.condition and
                self.body == other.body)

    def __hash__(self) -> int:
        return hash((self.invariant, self.condition, self.body, 'while'))

    def substitute(self, var, term):
        return WhileRule(
            self.invariant.substitute(var, term),
            self.condition,  # conditions don't have substitution yet
            self.body
        )

    def apply_right(self, sequent) -> Optional[Tuple[List, str]]:
        return None

    def apply_left(self, sequent) -> Optional[Tuple[List, str]]:
        return None
