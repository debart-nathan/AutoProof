"""Universal quantifier formula (∀x.A)."""

from typing import List, Optional, Tuple
from ..interfaces.formula import Formula
from ..sequent import Sequent


# --- helpers (you can move them elsewhere later) ---

_fresh_counter = 0


def fresh_constant_name() -> str:
    global _fresh_counter
    _fresh_counter += 1
    return f"c{_fresh_counter}"


class Const(Formula):
    """
    Very simple constant term/formula placeholder.
    Adapt or replace with your own atomic/term type if you already have one.
    """

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        return isinstance(other, Const) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def substitute(self, var, term):
        return self

    def apply_right(self, sequent):
        return None

    def apply_left(self, sequent):
        return None


def fresh_constant() -> Const:
    return Const(fresh_constant_name())


def extract_terms_from_context(antecedent) -> List[Formula]:
    """
    Very naive term extractor: returns [] so we always fall back to a fresh constant.
    You can refine this later.
    """
    return []


class Universal(Formula):
    """Represents universal quantification (∀x.A)."""

    def __init__(self, var, formula: Formula):
        self.var = var
        self.formula = formula

    def __str__(self) -> str:
        return f"∀{self.var}.{self.formula}"

    def __eq__(self, other) -> bool:
        return isinstance(other, Universal) and self.var == other.var and self.formula == other.formula

    def __hash__(self) -> int:
        return hash((self.var, self.formula))

    def substitute(self, var, term):
        if var == self.var:
            return self
        return Universal(self.var, self.formula.substitute(var, term))

    def apply_right(self, sequent) -> Optional[Tuple[List, str]]:
        """
        ∀R (eigenvariable rule):
            from Γ ⇒ A[x := a] infer Γ ⇒ ∀x.A
        where a is a fresh constant.
        """
        antecedent, succedent = sequent

        if succedent != self:
            return None

        a = fresh_constant()
        instantiated = self.formula.substitute(self.var, a)

        new_sequent = (list(antecedent), instantiated)
        premises = [new_sequent]
        return (premises, 'single')

    def apply_left(self, sequent) -> Optional[Tuple[List, str]]:
        """
        ∀L (instantiation rule):
            from Γ, A[x := t] ⇒ C infer Γ, ∀x.A ⇒ C
        for any term t.
        """
        antecedent, succedent = sequent

        if self not in antecedent:
            return None

        base = [f for f in antecedent if f != self]

        terms = extract_terms_from_context(antecedent)
        terms.append(fresh_constant())

        premises: List[Tuple[List[Formula], Formula]] = []
        for t in terms:
            instantiated = self.formula.substitute(self.var, t)
            new_ant = base + [instantiated]
            premises.append((new_ant, succedent))

        return (premises, 'multiple')
