"""Implication formula (A → B)."""

from typing import List, Optional, Tuple
from ...interfaces.formula import Formula


class Implication(Formula):
    """Represents implication of two formulas (A → B)."""

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"({self.left} → {self.right})"

    def __eq__(self, other) -> bool:
        return isinstance(other, Implication) and self.left == other.left and self.right == other.right

    def __hash__(self) -> int:
        return hash((self.left, self.right))

    def substitute(self, var, term):
        """Substitute inside both sides of the implication."""
        return Implication(
            self.left.substitute(var, term),
            self.right.substitute(var, term)
        )

    def apply_right(self, sequent) -> Optional[Tuple[List, str]]:
        """
        →R: Γ ⇒ A → B  from  Γ, A ⇒ B.
        """
        antecedent, succedent = sequent
        if self == succedent:
            new_ant = list(antecedent) + [self.left]
            return ([(new_ant, self.right)], 'single')
        return None

    def apply_left(self, sequent) -> Optional[Tuple[List, str]]:
        """
        LJT transformations for →L.
        """
        from .conjunction import Conjunction
        from .disjunction import Disjunction

        antecedent, succedent = sequent
        if self not in antecedent:
            return None

        idx = antecedent.index(self)
        base = list(antecedent[:idx]) + list(antecedent[idx+1:])

        # LJT1: (A ∧ B) → C  ⇒  A → (B → C)
        if isinstance(self.left, Conjunction):
            new_impl = Implication(
                self.left.left,
                Implication(self.left.right, self.right)
            )
            return ([(base + [new_impl], succedent)], 'single')

        # LJT2: (A ∨ B) → C  ⇒  (A → C), (B → C)
        if isinstance(self.left, Disjunction):
            impl_left = Implication(self.left.left, self.right)
            impl_right = Implication(self.left.right, self.right)
            return ([(base + [impl_left], succedent),
                     (base + [impl_right], succedent)], 'multiple')

        # LJT4: (A → B) → C  ⇒  (B → C)
        if isinstance(self.left, Implication):
            new_impl = Implication(self.left.right, self.right)
            return ([(base + [new_impl], succedent)], 'single')

        # LJT3: atomic A → B  ⇒  standard →L
        premise1 = (base, self.left)
        premise2 = (base + [self.right], succedent)
        return ([premise1, premise2], 'multiple')
