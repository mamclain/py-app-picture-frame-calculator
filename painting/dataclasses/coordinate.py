"""
 a class to hold coordinate information
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Coordinate:
    """
    A class to hold coordinate information
    Attributes:
        x: the x coordinate
        y: the y coordinate
    """

    x: float
    y: float

    def __sub__(self, other: Coordinate):
        """
        Subtract a coordinate from this coordinate
        :param other: the coordinate to subtract
        :return:
        """
        return Coordinate(self.x - other.x, self.y - other.y)

    def __add__(self, other: Coordinate):
        """
        Add a coordinate to this coordinate
        :param other: the coordinate to add
        :return:
        """
        return Coordinate(self.x + other.x, self.y + other.y)
