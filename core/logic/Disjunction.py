from typing import List, Optional, Tuple

class Disjunction:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return f"({self.left} ∨ {self.right})"

    def __eq__(self, other):
        return isinstance(other, Disjunction) and self.left == other.left and self.right == other.right

    def __hash__(self):
        return hash((self.left, self.right))

    def apply_right(self, sequent) -> Optional[Tuple[List, str]]:
        # ∨R: Γ ⇒ A ∨ B from Γ ⇒ A or Γ ⇒ B
        antecedent, succedent = sequent
        if self == succedent:
            return ([(antecedent, self.left), (antecedent, self.right)], 'or')
        return None

    def apply_left(self, sequent) -> Optional[Tuple[List, str]]:
        # ∨L: Γ, A ∨ B ⇒ C from Γ, A ⇒ C and Γ, B ⇒ C
        antecedent, succedent = sequent
        if self in antecedent:
            idx = antecedent.index(self)
            base = antecedent[:idx] + antecedent[idx+1:]
            return ([
                (base + (self.left,), succedent),
                (base + (self.right,), succedent)
            ], 'and')
        return None
