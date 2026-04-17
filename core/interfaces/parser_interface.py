"""
Abstract base class defining the interface for formula parsers.
"""

from abc import ABC, abstractmethod
from typing import Union
from .formula import Formula


class ParserInterface(ABC):
    """
    Abstract base class for formula parsers.
    
    Any parser converting text/code to logical formulas must implement this interface.
    """

    @abstractmethod
    def parse(self, text: str) -> Formula:
        """
        Parse input text and return a logical formula.
        
        Args:
            text: Input string to parse (format depends on parser implementation)
            
        Returns:
            A Formula object representing the parsed formula
            
        Raises:
            ValueError: If the input cannot be parsed
        """
        pass
