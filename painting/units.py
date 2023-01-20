"""
a class to hold unit conversion functions
"""


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
