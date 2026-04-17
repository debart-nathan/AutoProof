"""Bottom (falsum) formula ⊥."""

from typing import Optional, Tuple, List
from ..interfaces.formula import Formula


class Bottom(Formula):
    """Represents the bottom formula (falsum/contradiction)."""

    def __str__(self) -> str:
        return "⊥"

    def __eq__(self, other) -> bool:
        return isinstance(other, Bottom)

    def __hash__(self) -> int:
        return hash("⊥")

    def substitute(self, var, term):
        """⊥ contains no variables; substitution is a no-op."""
        return self

    def apply_right(self, sequent) -> Optional[Tuple[List, str]]:
        """⊥ has no right introduction rule."""
        return None

    def apply_left(self, sequent) -> Optional[Tuple[List, str]]:
        """
        ⊥L: Γ, ⊥ ⇒ C
        If ⊥ is in the context, the sequent is immediately provable.
        """
        antecedent, succedent = sequent
        if self in antecedent:
            return ([], 'bottom-left')
        return None
