from typing import List, Optional, Tuple
from .Bottom import Bottom

class Negation:
    def __init__(self, formula):
        self.formula = formula

    def __str__(self):
        return f"¬{self.formula}"

    def __eq__(self, other):
        return isinstance(other, Negation) and self.formula == other.formula

    def __hash__(self):
        return hash((self.formula,))

    def apply_right(self, sequent) -> Optional[Tuple[List, str]]:
        # ¬R: Γ ⇒ ¬A from Γ, A ⇒ ⊥
        antecedent, succedent = sequent
        if succedent is self:
            bottom = Bottom()
            new_antecedent = antecedent + (self.formula,)
            return ([(new_antecedent, bottom)], 'single')
        return None

    def apply_left(self, sequent) -> Optional[Tuple[List, str]]:
        # ¬L: Γ, ¬A ⇒ C from Γ ⇒ A
        antecedent, succedent = sequent
        if self not in antecedent:
            return None

        idx = antecedent.index(self)
        new_ant = antecedent[:idx] + antecedent[idx+1:]

        return ([(new_ant, self.formula)], 'single')
