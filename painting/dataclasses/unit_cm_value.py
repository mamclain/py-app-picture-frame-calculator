"""
a class to hold a unit cm value
"""

from dataclasses import dataclass

from painting.mathematics.units import (
    cm_to_in,
    in_to_tape_measure
)


@dataclass
class UnitCm:
    """
    A class to hold a unit Cm value
    Attributes:
        value_cm: the value

    """
    value_cm: float

    @property
    def value_cm_round(self) -> float:
        """
        Get the value rounded to the nearest .01mm
        :return: the rounded value
        """
        return round(self.value_cm, 2)

    @property
    def value_in(self) -> float:
        """
        Return the value in inches
        :return: the value in inches
        """
        return cm_to_in(self.value_cm)

    @property
    def value_tape(self) -> str:
        """
        Return the value in inches as a string
        :return: the value in inches as a string
        """
        return in_to_tape_measure(self.value_in)
