# sequent.py
from typing import Tuple, FrozenSet, Iterable, List, Any


class Sequent:
    def __init__(self, antecedent: Iterable, succedent, proof: List[Any] | None = None):
        ant_tuple = tuple(antecedent) if antecedent else ()
        self._antecedent_set: FrozenSet = frozenset(ant_tuple)
        self._antecedent_tuple: Tuple = ant_tuple
        self.succedent = succedent
        self.proof: List[Any] = proof or []

    @property
    def antecedent(self) -> Tuple:
        return self._antecedent_tuple

    @property
    def context_set(self) -> FrozenSet:
        return self._antecedent_set

    def _with(self, antecedent=None, succedent=None) -> "Sequent":
        return Sequent(
            antecedent if antecedent is not None else self.antecedent,
            succedent if succedent is not None else self.succedent,
            proof=self.proof.copy(),
        )

    def with_antecedent(self, new_antecedent) -> "Sequent":
        return self._with(antecedent=new_antecedent)

    def with_succedent(self, new_succedent) -> "Sequent":
        return self._with(succedent=new_succedent)

    def add_to_context(self, formula) -> "Sequent":
        if formula not in self._antecedent_set:
            return self._with(antecedent=self.antecedent + (formula,))
        return self

    def remove_from_context(self, formula) -> "Sequent":
        if formula in self._antecedent_set:
            new_ant = tuple(f for f in self.antecedent if f != formula)
            return self._with(antecedent=new_ant)
        return self

    def contains_in_context(self, formula) -> bool:
        return formula in self._antecedent_set

    def replace_right(self, new_succedent):
        return self.with_succedent(new_succedent)

    def replace_left(self, old_formula, new_formula):
        new_ant = tuple(f if f != old_formula else new_formula for f in self.antecedent)
        return self.with_antecedent(new_ant)

    # ---- proof tracing ----

    def add_step(self, rule_name: str, before_term, after_term):
        self.proof.append((rule_name, before_term, after_term))

    def __eq__(self, other):
        if not isinstance(other, Sequent):
            return False
        return self._antecedent_set == other._antecedent_set and self.succedent == other.succedent

    def __hash__(self):
        return hash((self._antecedent_set, self.succedent))

    def __str__(self):
        ant_str = ", ".join(str(f) for f in self.antecedent) if self.antecedent else ""
        return f"{ant_str} ⇒ {self.succedent}"

    def __repr__(self):
        return f"Sequent({self})"

    def __iter__(self):
        yield self.antecedent
        yield self.succedent
