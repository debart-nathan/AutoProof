"""Core sequent data structure."""

from typing import Tuple, FrozenSet, Iterable


class Sequent:
    """
    Represents a sequent Γ ⇒ A with separated context and goal.

    Stores context as a frozenset for efficient hashing and comparison,
    but maintains tuple conversion for rule application.
    """

    def __init__(self, antecedent: Iterable, succedent):
        """
        Args:
            antecedent: iterable of formulas (context/premises)
            succedent: single formula (goal)
        """
        ant_tuple = tuple(antecedent) if antecedent else ()
        self._antecedent_set: FrozenSet = frozenset(ant_tuple)
        self._antecedent_tuple: Tuple = ant_tuple
        self.succedent = succedent

    @property
    def antecedent(self) -> Tuple:
        """Returns antecedent as ordered tuple for rule application."""
        return self._antecedent_tuple

    @property
    def context_set(self) -> FrozenSet:
        """Returns antecedent as frozenset for efficient membership testing."""
        return self._antecedent_set

    def with_antecedent(self, new_antecedent) -> 'Sequent':
        """Create new sequent with modified antecedent."""
        return Sequent(new_antecedent, self.succedent)

    def with_succedent(self, new_succedent) -> 'Sequent':
        """Create new sequent with modified succedent."""
        return Sequent(self.antecedent, new_succedent)

    def add_to_context(self, formula) -> 'Sequent':
        """Add formula to context, avoiding duplicates."""
        if formula not in self._antecedent_set:
            return Sequent(self.antecedent + (formula,), self.succedent)
        return self

    def remove_from_context(self, formula) -> 'Sequent':
        """Remove formula from context."""
        if formula in self._antecedent_set:
            new_ant = tuple(f for f in self.antecedent if f != formula)
            return Sequent(new_ant, self.succedent)
        return self

    def contains_in_context(self, formula) -> bool:
        """Efficient membership test using frozenset."""
        return formula in self._antecedent_set

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

    # Backward compatibility: allow tuple unpacking
    def __iter__(self):
        """Allow unpacking: antecedent, succedent = sequent"""
        yield self.antecedent
        yield self.succedent
