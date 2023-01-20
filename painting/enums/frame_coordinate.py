"""
an enumeration to hold the frame coordinate maps
"""
from enum import IntEnum


class FrameCoordinate(IntEnum):
    """
    an enumeration to hold the frame coordinate maps
    """
    BOTTOM_LEFT = 0
    BOTTOM_RIGHT = 1
    TOP_RIGHT = 2
    TOP_LEFT = 3
    BOTTOM_LEFT_OVERLAY = 4
