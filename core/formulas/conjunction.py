"""Conjunction formula (A ∧ B)."""

from typing import List, Optional, Tuple
from ..interfaces.formula import Formula


class Conjunction(Formula):
    """Represents conjunction of two formulas (A ∧ B)."""

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"({self.left} ∧ {self.right})"

    def __eq__(self, other) -> bool:
        return isinstance(other, Conjunction) and self.left == other.left and self.right == other.right

    def __hash__(self) -> int:
        return hash((self.left, self.right))

    def substitute(self, var, term):
        """Substitute inside both conjuncts."""
        return Conjunction(
            self.left.substitute(var, term),
            self.right.substitute(var, term)
        )

    def apply_right(self, sequent) -> Optional[Tuple[List, str]]:
        """
        ∧R: Γ ⇒ A ∧ B from Γ ⇒ A and Γ ⇒ B.
        Both premises must be proven.
        """
        antecedent, succedent = sequent
        if self == succedent:
            premises = [
                (list(antecedent), self.left),
                (list(antecedent), self.right),
            ]
            return (premises, 'multiple')
        return None

    def apply_left(self, sequent) -> Optional[Tuple[List, str]]:
        """
        ∧L: Γ, A ∧ B ⇒ C from Γ, A, B ⇒ C.
        Replace conjunction in context with its components.
        """
        antecedent, succedent = sequent
        if self in antecedent:
            idx = antecedent.index(self)
            new_ant = (
                list(antecedent[:idx])
                + [self.left, self.right]
                + list(antecedent[idx+1:])
            )
            return ([(new_ant, succedent)], 'single')
        return None
