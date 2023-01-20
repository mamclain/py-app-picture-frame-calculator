"""
A Class to hold Painting Information
"""
from dataclasses import dataclass


@dataclass
class PaintingInformation:
    """
    A Class to hold Painting Information
    Attributes:
        width_min_cm: the minimum width of the painting in cm
        width_max_cm: the maximum width of the painting in cm
        height_min_cm: the minimum height of the painting in cm
        height_max_cm: the maximum height of the painting in cm
        hide_left_offset_cm: the amount of the left side of the painting to hide inside the frame in cm
        hide_bottom_offset_cm: the amount of the bottom of the painting to hide inside the frame in cm
        hide_right_offset_cm: the amount of the right side of the painting to hide inside the frame in cm
        hide_top_offset_cm: the amount of the top of the painting to hide inside the frame in cm
    """
    width_min_cm: float
    width_max_cm: float
    height_min_cm: float
    height_max_cm: float
    hide_left_offset_cm: float
    hide_top_offset_cm: float
    hide_right_offset_cm: float
    hide_bottom_offset_cm: float
