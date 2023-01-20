"""
an enumeration to hold rounding modes
"""

from enum import (
    IntEnum,
    auto
)


class RoundingMode(IntEnum):
    """
    an enumeration to hold rounding modes
    """
    NEAREST = auto()
    FLOOR = auto()
    CEILING = auto()
