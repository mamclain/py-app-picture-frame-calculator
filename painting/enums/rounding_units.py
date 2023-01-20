"""
a enumerated class for rounding units
"""

from enum import (
    IntEnum
)


class RoundingUnits(IntEnum):
    """
    an enumerated class for rounding units
    """
    THIRTY_SECOND = 32
    SIXTEENTH = 16
    EIGHTH = 8
    QUARTER = 4
    HALF = 2
    INCH = 1
