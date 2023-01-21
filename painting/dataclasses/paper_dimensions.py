"""
a data class to hold paper dimensions
"""

from dataclasses import dataclass


@dataclass
class PaperDimensions:
    """
    A data class to hold paper dimensions
    Attributes:
        width: the width of the paper
        height: the height of the paper
    """
    width: float
    height: float
