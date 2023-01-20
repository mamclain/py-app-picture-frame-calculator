"""
a class to hold the layout of a panting frame
"""
from dataclasses import dataclass

from .coordinate_list import CoordinateList


@dataclass
class FrameLayout:
    """ a class to hold the layout of a panting frame
        Attributes:
        painting_max_boundary: the maximum boundary of the painting
        painting_min_boundary: the minimum boundary of the painting
        painting_overlay_edge: the overlap between from the maximum boundary to some offset within the painting
        frame_exterior_boundary: the edge of the frame, or the overlay edge plus the frame width
    """
    painting_max_boundary: CoordinateList
    painting_min_boundary: CoordinateList
    painting_overlap_boundary: CoordinateList
    frame_exterior_boundary: CoordinateList
