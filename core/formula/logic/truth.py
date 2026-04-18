"""Truth constant (⊤ / True)."""

from typing import Optional, Tuple, List
from ...interfaces.formula import Formula


class Truth(Formula):
    """Represents the intuitionistic truth constant True (⊤)."""

    def __str__(self):
        return "True"

    def __eq__(self, other):
        return isinstance(other, Truth)

    def __hash__(self):
        return hash("True")

    def substitute(self, var, term):
        return self

    def apply_right(self, sequent) -> Optional[Tuple[List, str]]:
        """
        ⊤R: Γ ⇒ True is always provable.
        No premises.
        """
        antecedent, succedent = sequent
        if succedent == self:
            return ([], "single")
        return None

    def apply_left(self, sequent):
        """
        ⊤L: never useful; no rule needed.
        """
        return None
