"""Atomic formula (predicate or propositional variable)."""

from typing import Optional, Tuple, List
from ...interfaces.formula import Formula


class Atomic(Formula):
    """
    Represents an atomic predicate or propositional variable.

    Supports:
      - propositional atoms: A
      - predicate applications: P(x)
      - function-like atoms: f(x, y)
    """

    def __init__(self, name: str, args: Optional[List[Formula]] = None):
        self.name = name
        self.args = args or []   # list of Formula terms

    def __str__(self) -> str:
        if not self.args:
            return self.name
        args_str = ", ".join(str(a) for a in self.args)
        return f"{self.name}({args_str})"

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, Atomic)
            and self.name == other.name
            and self.args == other.args
        )

    def __hash__(self) -> int:
        return hash(("atomic", self.name, tuple(self.args)))

    def substitute(self, var, term):
        """Substitute inside arguments."""
        new_args = [a.substitute(var, term) for a in self.args]
        return Atomic(self.name, new_args)

    def apply_right(self, sequent) -> Optional[Tuple[List, str]]:
        return None  # no right rule for atomic formulas

    def apply_left(self, sequent) -> Optional[Tuple[List, str]]:
        return None  # no left rule for atomic formulas
