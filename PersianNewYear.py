"""Under development"""
from JulianDate import _JD_OFFSET
from PersianDate import _from_day_id
from math import modf as _modf


def vernal_equinox(per_year: int, tzone: float = 3.5, formula=1):
    """
    (Experimental) It calculates the Vernal Equinox moment.
    INPUT: Persian year, time zone (default IRST: UTC+3:30) 
    OUPUT: Spring Equinox in Persian Date and time (by default Iran standard time)
    """
    greg_year = per_year + 621
    jd_m = 0
    if formula == 1:
        t = greg_year / 1000
        jd_m = 1721139.2855 + (365242.1376 + (0.0679190 - 0.0027879 * t) * t) * t
    elif formula == 2:
        t = (greg_year - 2000) / 1000
        jd_m = 2451623.80984 + (365242.37404 + (0.05169 - (0.00411 - 0.00057 * t) * t) * t) * t
        jd_m = jd_m - (102 + (1020 + 2530 * t) * t) / (24 * 3600)

    f, i = _modf(jd_m + 0.5 + tzone / 24)
    per_date = _from_day_id(int(i) - _JD_OFFSET)
    f, h = _modf(f * 24)
    f, m = _modf(f * 60)
    f, s = _modf(f * 60)
    return per_date, int(h), int(m), s


if __name__ == '__main__':
    import PersianDate as PD

    next_year = PD.now().year + 1
    print('Persian next New Year moment:')
    print('Formula 1, {} {}:{}:{}'.format(*vernal_equinox(next_year)))
    print('Formula 2, {} {}:{}:{}'.format(*vernal_equinox(next_year, formula=2)))
