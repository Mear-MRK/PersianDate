"""Under development"""

from math import floor as _floor, modf as _modf

# Corresponding Julian Day to the Persian date 01-01-01
_JD_OFFSET = 1948320

def JulianDay_from_JulianDate(jdt: tuple[int, int, int]) -> int:
    raise NotImplementedError


def JulianDay_from_GregDate(year: int, month: int, day: int) -> int:
    """Gives Julian Day at noon from Greg. date."""
    if month > 2:
        y = year
        m = month
    else:
        y = year - 1
        m = month + 12
    a = y // 100
    b = 2 - a + a // 4
    return _floor(365.25 * (y + 4716)) + _floor(30.6001 * (m + 1)) + day + b - 1524  # At noon, otherwise 1524.5
    


def GregDate_from_JulianDay(JD: int) -> tuple[int, int, int]:
    """
    Output: Proleptic Gregorian date
    Input:  Positive Julian Day at noon
    """
    #  JD 2299161 : Gregorian (1582, 10, 15)
    z = JD
    alpha = _floor((z - 1867216.25) / 36524.25)
    a = z + 1 + alpha - alpha // 4
    b = a + 1524
    c = _floor((b - 122.1) / 365.25)
    d = _floor(365.25 * c)
    e = _floor((b - d) / 30.6001)
    day = b - d - _floor(30.6001 * e)
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715

    return year, month, day
    


def JulianDate_from_JulianDay(JD: int) -> tuple[int, int, int]:
    """
    Output: Julian date
    Input:  Positive Julian Day at noon
    """
    #  JD 2299161 : Julian (1582, 10, 5)
    z = JD
    b = z + 1524
    c = _floor((b - 122.1) / 365.25)
    d = _floor(365.25 * c)
    e = _floor((b - d) / 30.6001)
    day = b - d - _floor(30.6001 * e)
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715

    return year, month, day
    
def GregDate_from_JulianDate(jdt: tuple[int, int, int]) -> tuple[int, int, int]:
    raise NotImplementedError
