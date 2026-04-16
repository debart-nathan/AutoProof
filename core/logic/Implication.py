from typing import List, Optional, Tuple
from .Conjunction import Conjunction
from .Disjunction import Disjunction

class Implication:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return f"({self.left} → {self.right})"

    def __eq__(self, other):
        return isinstance(other, Implication) and self.left == other.left and self.right == other.right

    def __hash__(self):
        return hash((self.left, self.right))

    def apply_right(self, sequent) -> Optional[Tuple[List, str]]:
        antecedent, succedent = sequent
        if self == succedent:
            new_antecedent = antecedent + (self.left,)
            new_succedent = self.right
            return ([(new_antecedent, new_succedent)], 'single')
        return None

    def apply_left(self, sequent) -> Optional[Tuple[List, str]]:
        antecedent, succedent = sequent
        if self not in antecedent:
            return None

        idx = antecedent.index(self)
        base = antecedent[:idx] + antecedent[idx+1:]

        # LJT1: (A ∧ B) → C  ⇒  A → (B → C)
        if isinstance(self.left, Conjunction):
            new_impl = Implication(
                self.left.left,
                Implication(self.left.right, self.right)
            )
            return ([(base + (new_impl,), succedent)], 'single')

        # LJT2: (A ∨ B) → C  ⇒  (A → C), (B → C)
        if isinstance(self.left, Disjunction):
            impl_left = Implication(self.left.left, self.right)
            impl_right = Implication(self.left.right, self.right)
            return ([(base + (impl_left, impl_right), succedent)], 'single')

        # LJT4: (A → B) → C  ⇒  (B → C)
        if isinstance(self.left, Implication):
            new_impl = Implication(self.left.right, self.right)
            return ([(base + (new_impl,), succedent)], 'single')

        # LJT3: atomic A → B  ⇒  standard →L
        premise1 = (base, self.left)
        premise2 = (base + (self.right,), succedent)
        return ([premise1, premise2], 'and')
