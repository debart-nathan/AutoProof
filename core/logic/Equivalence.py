from typing import List, Optional, Tuple
from .Implication import Implication

class Equivalence:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return f"({self.left} ↔ {self.right})"

    def __eq__(self, other):
        return isinstance(other, Equivalence) and self.left == other.left and self.right == other.right

    def __hash__(self):
        return hash((self.left, self.right, 'equiv'))

    def apply_right(self, sequent) -> Optional[Tuple[List, str]]:
        # ↔R: Γ ⇒ A ↔ B from Γ ⇒ A → B and Γ ⇒ B → A
        antecedent, succedent = sequent
        if self == succedent:
            return ([
                (antecedent, Implication(self.left, self.right)),
                (antecedent, Implication(self.right, self.left))
            ], 'and')
        return None

    def apply_left(self, sequent) -> Optional[Tuple[List, str]]:
        # ↔L: Γ, A ↔ B ⇒ C from Γ, A → B, B → A ⇒ C
        antecedent, succedent = sequent
        if self in antecedent:
            idx = antecedent.index(self)
            new_ant = (
                antecedent[:idx]
                + (Implication(self.left, self.right), Implication(self.right, self.left))
                + antecedent[idx+1:]
            )
            return ([(new_ant, succedent)], 'single')
        return None
