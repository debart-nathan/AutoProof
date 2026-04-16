from typing import Optional, Tuple, List

class Bottom:
    def __str__(self):
        return "⊥"

    def __eq__(self, other):
        return isinstance(other, Bottom)

    def __hash__(self):
        return hash("⊥")

    def apply_right(self, sequent):
        return None

    def apply_left(self, sequent) -> Optional[Tuple[List, str]]:
        antecedent, succedent = sequent
        if self in antecedent:
            return ([], 'bottom-left')
        return None
