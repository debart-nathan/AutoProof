"""Existential quantifier formula (∃x.A)."""

from typing import List, Optional, Tuple
from ...interfaces.formula import Formula
from .universal import fresh_constant   # reuse your fresh constant generator


class Existential(Formula):
    """Represents existential quantification (∃x.A)."""

    def __init__(self, var, formula):
        self.var = var
        self.formula = formula

    def __str__(self) -> str:
        return f"∃{self.var}.{self.formula}"

    def __eq__(self, other) -> bool:
        return isinstance(other, Existential) and self.var == other.var and self.formula == other.formula

    def __hash__(self) -> int:
        return hash((self.var, self.formula))

    def substitute(self, var, term):
        """Do not substitute under a binder for the same variable."""
        if var == self.var:
            return self
        return Existential(self.var, self.formula.substitute(var, term))

    def apply_right(self, sequent) -> Optional[Tuple[List, str]]:
        """
        ∃R (witness rule):
            from Γ ⇒ A[x := t] infer Γ ⇒ ∃x.A
        where t is ANY term. We use a fresh constant as witness.
        """
        antecedent, succedent = sequent
        if succedent != self:
            return None

        witness = fresh_constant()
        instantiated = self.formula.substitute(self.var, witness)

        return ([(list(antecedent), instantiated)], 'single')

    def apply_left(self, sequent) -> Optional[Tuple[List, str]]:
        """
        ∃L (elimination rule):
            from Γ, A[x := a] ⇒ C infer Γ, ∃x.A ⇒ C
        where a is a fresh constant (eigenvariable).
        """
        antecedent, succedent = sequent
        if self not in antecedent:
            return None

        idx = antecedent.index(self)
        base = list(antecedent[:idx]) + list(antecedent[idx+1:])

        a = fresh_constant()
        instantiated = self.formula.substitute(self.var, a)

        new_ant = base + [instantiated]
        return ([(new_ant, succedent)], 'single')
