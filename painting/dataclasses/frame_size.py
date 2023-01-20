"""
a dataclass to hold the size of a painting frame wood
"""

from dataclasses import dataclass

from painting.mathematics.units import in_to_cm


@dataclass
class FrameSize:
    """ a dataclass to hold the size of a painting frame wood
        Attributes:
        width_in: the width of the frame in inches
        height_in: the height of the frame in inches
    """
    width_in: float
    height_in: float

    @property
    def width_cm(self) -> float:
        """ get the width of the frame in centimeters
        :return: the width of the frame in centimeters
        """
        return in_to_cm(self.width_in)

    @property
    def height_cm(self) -> float:
        """ get the height of the frame in centimeters
        :return: the height of the frame in centimeters
        """
        return in_to_cm(self.height_in)
