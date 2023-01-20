"""
a part of the frame to be built
"""

from dataclasses import dataclass


@dataclass
class FramePart:
    """
    a part of the frame to be built
    Attributes:
        inner_length_cm: the length of the part inside the frame in cm
        outer_length_cm: the length of the part outside the frame in cm
        inlay_width_cm: the width of the inlay in cm
    """
    inner_length_cm: float
    outer_length_cm: float
    inlay_width_cm: float
