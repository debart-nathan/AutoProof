"""Negation formula (¬A)."""

from typing import List, Optional, Tuple
from ..interfaces.formula import Formula
from .bottom import Bottom


class Negation(Formula):
    """Represents negation of a formula (¬A)."""

    def __init__(self, formula):
        self.formula = formula

    def __str__(self) -> str:
        return f"¬{self.formula}"

    def __eq__(self, other) -> bool:
        return isinstance(other, Negation) and self.formula == other.formula

    def __hash__(self) -> int:
        return hash(("neg", self.formula))

    def substitute(self, var, term):
        """Substitute inside the negated formula."""
        return Negation(self.formula.substitute(var, term))

    def apply_right(self, sequent) -> Optional[Tuple[List, str]]:
        """
        ¬R: Γ ⇒ ¬A  from  Γ, A ⇒ ⊥.
        """
        antecedent, succedent = sequent
        if succedent is self:
            bottom = Bottom()
            new_ant = list(antecedent) + [self.formula]
            return ([(new_ant, bottom)], 'single')
        return None

    def apply_left(self, sequent) -> Optional[Tuple[List, str]]:
        """
        ¬L: Γ, ¬A ⇒ C  from  Γ ⇒ A.
        """
        antecedent, succedent = sequent
        if self not in antecedent:
            return None

        idx = antecedent.index(self)
        new_ant = list(antecedent[:idx]) + list(antecedent[idx+1:])

        return ([(new_ant, self.formula)], 'single')
