"""
Abstract base class defining the interface for proof systems.
"""

from abc import ABC, abstractmethod
from typing import Literal


class ProverInterface(ABC):
    """
    Abstract base class for proof systems.
    
    Any prover system must implement this interface to prove sequents.
    """

    @abstractmethod
    def prove(self, sequent) -> Literal['proven', 'disproven', 'unknown']:
        """
        Attempt to prove a sequent.
        
        Args:
            sequent: A Sequent object (antecedent, succedent) or tuple
            
        Returns:
            - 'proven': The sequent is proven/valid
            - 'disproven': The sequent is disproven (negation is proven)
            - 'unknown': Cannot determine with current proof strategy
        """
        pass

    @abstractmethod
    def reset_memo(self) -> None:
        """
        Clear any memoization/caching from previous proofs.
        Useful when running independent proofs or testing.
        """
        pass
