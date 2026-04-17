"""Atomic formula (propositional variable)."""

from typing import Optional, Tuple, List
from ..interfaces.formula import Formula


class Atomic(Formula):
    """Represents an atomic proposition (variable)."""

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        return isinstance(other, Atomic) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def substitute(self, var, term):
        """
        Propositional atoms do not contain term variables.
        Substitution is a no-op.
        """
        return self

    def apply_right(self, sequent) -> Optional[Tuple[List, str]]:
        """Atomic formulas have no right introduction rule."""
        return None

    def apply_left(self, sequent) -> Optional[Tuple[List, str]]:
        """Atomic formulas have no left elimination rule."""
        return None
