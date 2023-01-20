"""
a part of the frame to be built
"""

from dataclasses import dataclass

from painting.dataclasses.unit_cm_value import UnitCm


@dataclass
class FramePart:
    """
    a part of the frame to be built
    Attributes:
        inner_length: the length of the part inside the frame in cm
        outer_length: the length of the part outside the frame in cm
        inlay_width: the width of the inlay in cm
        coverage_width: the width of the coverage from painting min to inlay width in cm
    """
    inner_length: UnitCm
    outer_length: UnitCm
    inlay_width: UnitCm
    coverage_width: UnitCm
