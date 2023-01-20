"""
a class to hold unit conversion functions
"""
import math
from fractions import Fraction

from ..enums.rounding_mode import RoundingMode
from ..enums.rounding_units import RoundingUnits


def in_to_cm(inches: float) -> float:
    """ convert inches to centimeters
    :param inches: the inches to convert
    :return: the converted inches in centimeters
    """
    return inches * 2.54


def cm_to_in(cm: float) -> float:
    """ convert centimeters to inches
    :param cm: the centimeters to convert
    :return: the converted centimeters in inches
    """
    return cm / 2.54


def in_to_tape_measure(
        value_in: float,
        round_unit: RoundingUnits = RoundingUnits.THIRTY_SECOND,
        round_mode: RoundingMode = RoundingMode.CEILING
) -> str:
    """ convert inches to the values found on a tape measure

    :param value_in: the input value in inches
    :param round_unit: the units to round at
    :param round_mode: the rounding mode
    :return: the tape measure value as a string
    """

    round_unit_float = float(round_unit)

    if round_mode == RoundingMode.CEILING:
        round_value_in = math.ceil(value_in * round_unit_float) / round_unit
    elif round_mode == RoundingMode.FLOOR:
        round_value_in = math.floor(value_in * round_unit_float) / round_unit
    else:
        round_value_in = round(value_in * round_unit_float) / round_unit

    frac_part, int_part = math.modf(round_value_in)
    limited_frac_part = Fraction(frac_part).limit_denominator(round_unit)
    if limited_frac_part == 0:
        return "{}".format(int(int_part))
    else:
        return "{} {}".format(int(int_part), limited_frac_part)
