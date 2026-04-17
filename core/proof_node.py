from dataclasses import dataclass
from typing import List, Optional
from .sequent import Sequent

@dataclass
class ProofNode:
    sequent: Sequent
    rule: str
    premises: List["ProofNode"]  # subproofs
