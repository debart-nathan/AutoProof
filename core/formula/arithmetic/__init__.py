"""
Arithmetic formulas for the AutoProof system.
"""

from .add import Add
from .sub import Sub
from .mul import Mul
from .eq import Eq
from .gt import Gt
from .ge import Ge
from .div import Div
from .lt import Lt
from .le import Le
from .not_eq import NotEq
from .succ import Succ
from .zero import Zero

__all__ = [
    "Add",
    "Sub",
    "Mul",
    "Eq",
    "Gt",
    "Ge",
    "Div"
    "Lt",
    "Le",
    "NotEq",
    "Succ"
    "Zero"
]
