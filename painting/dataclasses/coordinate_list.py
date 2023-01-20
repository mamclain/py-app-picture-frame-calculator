"""
a class to hold a list of coordinates
"""

from dataclasses import dataclass
from typing import List

from .coordinate import Coordinate


@dataclass
class CoordinateList:
    """
    A class to hold a list of coordinates
    Attributes:
        coordinates: the list of coordinates
    """
    coordinates: List[Coordinate]

    def __add__(self, other: Coordinate):
        """
        Add a coordinate to each coordinate in the list
        :param other: a coordinate to add
        :return:
        """
        return CoordinateList([c + other for c in self.coordinates])

    def __sub__(self, other: Coordinate):
        """
        Subtract a coordinate from each coordinate in the list
        :param other: a coordinate to subtract
        :return:
        """
        return CoordinateList([c - other for c in self.coordinates])

    def __getitem__(self, item):
        """ Get a coordinate from the list
        :param item: the index of the coordinate to get
        :return: the coordinate
        """
        return self.coordinates[item]

    @property
    def xs(self) -> List[float]:
        """ Get the x coordinates as a list.
        :return: A list of x coordinates
        """
        return [c.x for c in self.coordinates]

    @property
    def ys(self) -> List[float]:
        """ Get the y coordinates as a list.
        :return: a list of y coordinates
        """
        return [c.y for c in self.coordinates]

    @property
    def x_min(self) -> float:
        """ get the minimum x value
        :return: the minimum x value
        """
        return min(self.xs)

    @property
    def x_max(self) -> float:
        """ get the maximum x value
        :return: the maximum x value
        """
        return max(self.xs)

    @property
    def y_min(self) -> float:
        """ get the minimum y value
        :return: the minimum y value
        """
        return min(self.ys)

    @property
    def y_max(self) -> float:
        """ get the maximum y value
        :return: the maximum y value
        """
        return max(self.ys)
