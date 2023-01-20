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
        inner_length_cm: the length of the part inside the frame in cm
        outer_length_cm: the length of the part outside the frame in cm
        inlay_width_cm: the width of the inlay in cm
        coverage_width_cm: the width of the coverage from painting min to inlay width in cm
    """
    inner_length_cm: UnitCm
    outer_length_cm: UnitCm
    inlay_width_cm: UnitCm
    coverage_width_cm: UnitCm
