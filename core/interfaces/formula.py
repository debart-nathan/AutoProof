"""
Abstract base class defining the interface for logical formulas.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, List


class Formula(ABC):
    """
    Abstract base class for all logical formulas.

    All formula types must implement:
    - substitute(var, term)
    - apply_right(sequent): Right introduction rule
    - apply_left(sequent): Left elimination rule
    - __str__, __eq__, __hash__
    """

    @abstractmethod
    def apply_right(self, sequent) -> Optional[Tuple[List, str]]:
        """
        Apply the right introduction rule for this formula.

        Args:
            sequent: A tuple or Sequent object (antecedent, succedent)

        Returns:
            None if rule doesn't apply, or (premises, connection_type) where:

            - premises: list of new sequents to prove
            - connection_type:
                'single'       → exactly one premise must be proven
                'multiple'     → all premises must be proven
                'or'           → at least one premise must be proven
                'bottom-left'  → sequent is immediately proven
                'none'         → rule applies but yields no premises
        """
        pass

    @abstractmethod
    def apply_left(self, sequent) -> Optional[Tuple[List, str]]:
        """
        Apply the left elimination rule for this formula.

        Same return contract as apply_right().
        """
        pass

    @abstractmethod
    def substitute(self, var, term) -> "Formula":
        """Return a new formula with all free occurrences of var replaced by term."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Return string representation of the formula."""
        pass

    @abstractmethod
    def __eq__(self, other) -> bool:
        """Check equality with another formula."""
        pass

    @abstractmethod
    def __hash__(self) -> int:
        """Return hash for use in sets and dicts."""
        pass
