"""
a class to hold frame part list
"""

from dataclasses import dataclass
from typing import List

from painting.dataclasses.frame_part import FramePart


@dataclass
class FramePartList:
    """
    a class to hold frame part list
    Attributes:
        parts: a list of frame parts
    """
    parts: List[FramePart]
