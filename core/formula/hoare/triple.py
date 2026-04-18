"""Hoare triple formula {P} c {Q}."""

from typing import Optional, Tuple, List
from ...interfaces.formula import Formula


class Triple(Formula):
    """Represents a Hoare triple {P} c {Q}."""

    def __init__(self, precondition, command, postcondition):
        self.precondition = precondition
        self.command = command
        self.postcondition = postcondition

    def __str__(self) -> str:
        return f"{{ {self.precondition} }} {self.command} {{ {self.postcondition} }}"

    def __eq__(self, other) -> bool:
        return (isinstance(other, Triple) and 
                self.precondition == other.precondition and
                self.command == other.command and
                self.postcondition == other.postcondition)

    def __hash__(self) -> int:
        return hash((self.precondition, self.command, self.postcondition, 'triple'))

    def substitute(self, var, term):
        return Triple(
            self.precondition.substitute(var, term),
            self.command,  # commands don't have substitution yet
            self.postcondition.substitute(var, term)
        )

    def apply_right(self, sequent) -> Optional[Tuple[List, str]]:
        return None

    def apply_left(self, sequent) -> Optional[Tuple[List, str]]:
        return None
