"""Disjunction formula (A ∨ B)."""

from typing import List, Optional, Tuple
from ..interfaces.formula import Formula


class Disjunction(Formula):
    """Represents disjunction of two formulas (A ∨ B)."""

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"({self.left} ∨ {self.right})"

    def __eq__(self, other) -> bool:
        return isinstance(other, Disjunction) and self.left == other.left and self.right == other.right

    def __hash__(self) -> int:
        return hash((self.left, self.right))

    def substitute(self, var, term):
        """Substitute inside both disjuncts."""
        return Disjunction(
            self.left.substitute(var, term),
            self.right.substitute(var, term)
        )

    def apply_right(self, sequent) -> Optional[Tuple[List, str]]:
        """
        ∨R: Γ ⇒ A ∨ B from Γ ⇒ A  OR  Γ ⇒ B.
        At least one premise must succeed.
        """
        antecedent, succedent = sequent
        if self == succedent:
            premises = [
                (list(antecedent), self.left),
                (list(antecedent), self.right),
            ]
            return (premises, 'or')
        return None

    def apply_left(self, sequent) -> Optional[Tuple[List, str]]:
        """
        ∨L: Γ, A ∨ B ⇒ C from Γ, A ⇒ C  AND  Γ, B ⇒ C.
        Both branches must succeed.
        """
        antecedent, succedent = sequent
        if self in antecedent:
            idx = antecedent.index(self)
            base = list(antecedent[:idx]) + list(antecedent[idx+1:])

            left_ant = base + [self.left]
            right_ant = base + [self.right]

            return ([(left_ant, succedent), (right_ant, succedent)], 'multiple')
        return None
