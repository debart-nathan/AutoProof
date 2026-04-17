"""Equivalence formula (A ↔ B)."""

from typing import List, Optional, Tuple
from ..interfaces.formula import Formula
from .implication import Implication


class Equivalence(Formula):
    """Represents equivalence of two formulas (A ↔ B)."""

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"({self.left} ↔ {self.right})"

    def __eq__(self, other) -> bool:
        return isinstance(other, Equivalence) and self.left == other.left and self.right == other.right

    def __hash__(self) -> int:
        return hash((self.left, self.right, 'equiv'))

    def substitute(self, var, term):
        """Substitute inside both sides of the equivalence."""
        return Equivalence(
            self.left.substitute(var, term),
            self.right.substitute(var, term)
        )

    def apply_right(self, sequent) -> Optional[Tuple[List, str]]:
        """
        ↔R: Γ ⇒ A ↔ B  from  Γ ⇒ A → B  AND  Γ ⇒ B → A.
        Both directions must be proven.
        """
        antecedent, succedent = sequent
        if self == succedent:
            premises = [
                (list(antecedent), Implication(self.left, self.right)),
                (list(antecedent), Implication(self.right, self.left)),
            ]
            return (premises, 'multiple')
        return None

    def apply_left(self, sequent) -> Optional[Tuple[List, str]]:
        """
        ↔L: Γ, A ↔ B ⇒ C  
        becomes  
        Γ, A → B, B → A ⇒ C.
        """
        antecedent, succedent = sequent
        if self in antecedent:
            idx = antecedent.index(self)
            base = list(antecedent[:idx]) + list(antecedent[idx+1:])

            new_ant = base + [
                Implication(self.left, self.right),
                Implication(self.right, self.left)
            ]

            return ([(new_ant, succedent)], 'single')
        return None
