"""
an enumeration class of the display text modes
"""

from enum import (
    IntEnum,
    auto
)


class TextUnitMode(IntEnum):
    """
    an enumeration class of the display text modes
    """
    CM = auto()
    INCH = auto()
    TAPE = auto()
