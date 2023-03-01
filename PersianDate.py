import datetime as _datetime
from bisect import bisect as _bisect
from math import floor as _floor
from math import modf as _modf


# Remainders of Persian leap years divided by 33
_LEAP_REM = {1, 5, 9, 13, 17, 22, 26, 30}

# Number of days before the beginning of each year in a 33-Persian-year cycle (1-33),
# assuming that the year that (year % 33 == 22) is the irregular leap year.
_CUM_ND_1Y_33Y = (0, 366, 731, 1096, 1461, 1827, 2192, 2557, 2922, 3288, 3653,
                  4018, 4383, 4749, 5114, 5479, 5844, 6210, 6575, 6940, 7305, 7670,
                  8036, 8401, 8766, 9131, 9497, 9862, 10227, 10592, 10958, 11323, 11688)

# Number of days in 33 consecutive Persian years
_ND_33Y = 12053

# Corresponding Julian Day to the Persian date 01-01-01
_JD_OFFSET = 1948320

# Number of days before the beginning of each month in a common Greg. year
_CUM_ND_1M_1COM_GY = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)

# Number of days before the beginning of each month in a leap Greg. year
_CUM_ND_1M_1LEAP_GY = (0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335)

# Number of days in 400 consecutive Greg. years
_ND_400GY = 146097  # 400 * 365 + 3 * 24 + 25

# Number of days before the beginning of each Greg. century in a 400-Greg-year cycle (1-400),
# assuming that none of the years dividable by 100 is a leap year except for the last one (400).
_CUM_ND_100GY_400GY = (0, 36524, 73048, 109572)

# Number of days before the beginning of each 4-Greg-year cycle (1-4) in a Greg. century (1-100),
# assuming that the years dividable by 4 are leap years except the last year (100) may or may not be a leap year.
_CUM_ND_4GY_100GY = (0, 1461, 2922, 4383, 5844, 7305, 8766, 10227, 11688, 13149, 14610, 16071, 17532,
                     18993, 20454, 21915, 23376, 24837, 26298, 27759, 29220, 30681, 32142, 33603)

# Number of days before the beginning of each year in a 4-Greg-year cycle (1-4),
# assuming that only the last year (4) can be a leap year.
_CUM_ND_1GY_4GY = (0, 365, 730, 1095)

# Offset to calculate Greg. day id from Per. day id
_GREG_ID_OFFSET = 226894

# 3-letter short form of weekday names of the Persian calendar
_WEEKDAY_ABBR = ('shn', '1sh', '2sh', '3sh', '4sh', '5sh', 'jom')

# 3-letter short form of month names of the Persian calendar
_MONTH_ABBR = ('Far', 'Ord', 'Kho', 'Tir', 'Mor', 'Sha', 'Meh', 'Aba', 'Aza', 'Dey', 'Bah', 'Esf')


class PersianDate:
    __slots__ = ('_year', '_month', '_day', '_weekday_id', '_day_of_week', '_day_of_year',
                 '_week_of_year', '_leap_year', '_Greg_date', '_day_of_year', '_day_id', '_JD', '_hash')

    @property
    def year(self) -> int:
        return self._year

    @property
    def month(self) -> int:
        return self._month

    @property
    def day(self) -> int:
        return self._day

    @property
    def weekday_id(self) -> int:
        return self._weekday_id

    @property
    def day_of_week(self) -> str:
        return self._day_of_week

    @property
    def leap_year(self) -> bool:
        return self._leap_year

    @property
    def Greg_date(self):
        if self._Greg_date is None:
            self._Greg_date = GregDate_from_JD(self._JD)
        return self._Greg_date

    @property
    def day_of_year(self):
        if self._day_of_year is None:
            m = self._month - 1
            self._day_of_year = (m * 31 if m < 7 else 186 + (m - 6) * 30) + self._day
        return self._day_of_year

    @property
    def week_of_year(self):
        if self._week_of_year is None:
            dis = self._day_of_year - 1 - self._weekday_id
            fdw = (- dis) % 7
            self._week_of_year = (dis + fdw) // 7 + 1
        return self._week_of_year

    @property
    def tuple(self):
        return self._year, self._month, self._day

    def __init__(self, year=1, month=1, day=1, year_abbr=False):
        # If year_abbr is true, then the year must be in 0-99.
        if year_abbr:
            if year > 99 or year < 0:
                raise ValueError('Since year_abbr=True, year should be in 0-99.')
            self._year = 1400 + year if year < 50 else 1300 + year
        else:
            self._year = year
        if month < 1 or month > 12:
            raise ValueError("Not a valid month.")
        self._month = month
        self._leap_year = is_leap_year(self._year)
        if day > 31 or day < 0:
            raise ValueError("Not a valid day.")
        elif month > 6 and day > 30:
            raise ValueError("Not a valid day.")
        elif month == 12 and not self._leap_year and day == 30:
            raise ValueError("Not a valid day; year {} is not a leap year.".format(year))
        self._day = day

        self._day_id = _calc_day_id(self._year, self._month, self._day)
        self._JD = _JD_OFFSET + self._day_id
        self._Greg_date = None
        self._weekday_id = (self._day_id + 5) % 7
        self._day_of_week = _WEEKDAY_ABBR[self._weekday_id]
        self._day_of_year = None
        self._week_of_year = None
        self._hash = hash(self._day_id)

    def __sub__(self, oth) -> int:
        if isinstance(oth, PersianDate):
            return self._day_id - oth._day_id
        raise NotImplemented

    def __add__(self, days: int):
        if isinstance(days, int):
            return _from_day_id(self._day_id + days)
        raise NotImplemented

    __radd__ = __add__

    def __str__(self) -> str:
        return f'{self._year}-{self._month:02}-{self._day:02} {self._day_of_week}'

    def __repr__(self) -> str:
        return f'PersianDate({self._year},{self._month},{self._day})'

    def __eq__(self, oth) -> bool:
        if isinstance(oth, PersianDate):
            return self._day_id == oth._day_id
        raise NotImplemented

    def __le__(self, oth) -> bool:
        if isinstance(oth, PersianDate):
            return self._day_id <= oth._day_id
        raise NotImplemented

    def __lt__(self, oth) -> bool:
        if isinstance(oth, PersianDate):
            return self._day_id < oth._day_id
        raise NotImplemented

    def __ge__(self, oth) -> bool:
        if isinstance(oth, PersianDate):
            return self._day_id >= oth._day_id
        raise NotImplemented

    def __gt__(self, oth) -> bool:
        if isinstance(oth, PersianDate):
            return self._day_id > oth._day_id
        raise NotImplemented

    def __hash__(self):
        return self._hash


def is_leap_year(year: int) -> bool:
    """This guaranteed to work for 1206 <= year <= 1498 """
    return year % 33 in _LEAP_REM


def today(time_zone: _datetime.timezone = None) -> PersianDate:
    """Gives today Persian date. If 'time_zone' is not specified,
    it gives Iran standard date right now (without considering daylight saving)."""
    from datetime import datetime, timezone, timedelta
    now = datetime.now(time_zone) if time_zone is not None \
        else datetime.now(timezone(timedelta(hours=3, minutes=30)))
    return from_GregDate(now.year, now.month, now.day)


def _calc_day_id(year: int, month: int, day: int) -> int:
    y = year - 1
    m = month - 1
    d = day - 1
    n, r = divmod(y, 33)
    d1 = n * _ND_33Y
    nl = sum(map(lambda x: x <= r, _LEAP_REM))
    d2 = nl * 366 + (r - nl) * 365
    d3 = (m * 31 if m < 7 else 186 + (m - 6) * 30) + d
    return d1 + d2 + d3


def _calc_Greg_day_id_from_GregDate(year: int, month: int, day: int) -> int:
    y = year - 1
    m = month - 1
    d = day - 1
    d1 = 365 * y + y // 4 - y // 100 + y // 400
    leap = (year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))
    d2 = _CUM_ND_1M_1LEAP_GY[m] if leap else _CUM_ND_1M_1COM_GY[m]
    return d1 + d2 + d


def _from_day_id(day_id: int) -> PersianDate:
    n33y, rd = divmod(day_id, _ND_33Y)
    i = _bisect(_CUM_ND_1Y_33Y, rd)
    r = i - 1
    year = n33y * 33 + i
    rd -= _CUM_ND_1Y_33Y[r]
    if rd < 186:
        m, d = divmod(rd, 31)
        month = m + 1
        day = d + 1
    else:
        rd -= 186
        m, d = divmod(rd, 30)
        month = m + 7
        day = d + 1

    return PersianDate(year, month, day, year_abbr=False)


def _Vernal_Equinox(year: int, tzone: float = 3.5, formula=1):
    """
    (Experimental) It calculates the Vernal Equinox moment in Julian date
    """
    G_year = year + 621
    JD_M = 0
    if formula == 1:
        t = G_year / 1000
        JD_M = 1721139.2855 + (365242.1376 + (0.0679190 - 0.0027879 * t) * t) * t
    elif formula == 2:
        t = (G_year - 2000) / 1000
        JD_M = 2451623.80984 + (365242.37404 + (0.05169 - (0.00411 - 0.00057 * t) * t) * t) * t
        JD_M = JD_M - (102 + (1020 + 2530 * t) * t) / (24 * 3600)

    f, i = _modf(JD_M + 0.5 + tzone / 24)
    J_dat = _from_day_id(int(i) - _JD_OFFSET)
    f, h = _modf(f * 24)
    f, m = _modf(f * 60)
    f, s = _modf(f * 60)
    return J_dat.year, J_dat.month, J_dat.day, int(h), int(m), s


def _float_per_datetime(year: int, month: int, day: int, h: int, m: int, s: float) -> float:
    day = _calc_day_id(year, month, day)
    f = (h + (m + s / 60) / 60) / 24
    return day + f


def JulianDate_from_JD(JD: int) -> tuple[int, int, int]:
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


def GregDate_from_JD(JD: int) -> tuple[int, int, int]:
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


def _Greg_from_day_id(day_id: int):
    g_day_id = day_id + _GREG_ID_OFFSET
    n400y, rd = divmod(g_day_id, _ND_400GY)
    n100y = _bisect(_CUM_ND_100GY_400GY, rd) - 1
    rd -= _CUM_ND_100GY_400GY[n100y]
    n4y = _bisect(_CUM_ND_4GY_100GY, rd) - 1
    rd -= _CUM_ND_4GY_100GY[n4y]
    n1y = _bisect(_CUM_ND_1GY_4GY, rd) - 1
    rd -= _CUM_ND_1GY_4GY[n1y]

    leap_year = n1y == 3 and (n4y != 24 or n100y == 3)
    cum_nbr_days = _CUM_ND_1M_1LEAP_GY if leap_year else _CUM_ND_1M_1COM_GY

    year = n400y * 400 + n100y * 100 + n4y * 4 + n1y + 1
    month = _bisect(cum_nbr_days, rd)
    day = rd - cum_nbr_days[month - 1] + 1

    return year, month, day


def from_GregDate(year: int, month: int, day: int):
    g_id = _calc_Greg_day_id_from_GregDate(year, month, day)
    return _from_day_id(g_id - _GREG_ID_OFFSET)


def from_GregDate_JD(year: int, month: int, day: int):
    """Gives Persian date from Greg. date."""
    JD = JulianDay_from_GregDate(year, month, day)
    return _from_day_id(JD - _JD_OFFSET)


# Test
def test():

    print("Zero day id:", PersianDate(1, 1, 1)._day_id)
    print("Greg Zero day id:", from_GregDate(1, 1, 1)._day_id)
    did = _JD_OFFSET - _GREG_ID_OFFSET
    print("JD", did)
    print("GfJ", GregDate_from_JD(did))
    print("JfG", JulianDay_from_GregDate(1, 1, 1))

    print('-' * 32)

    print("Gregorian date of jd=2299161", GregDate_from_JD(2299161))
    print("Julian date of jd=2299161", JulianDate_from_JD(2299161))

    print('*' * 32)

    now = _datetime.datetime.today()
    td = today(now.astimezone().tzinfo)
    G_td = now.year, now.month, now.day
    print('Today:', td, now.date())
    G_id = _calc_Greg_day_id_from_GregDate(*G_td)
    print('today day_id:', td._day_id, 'G day_id:', G_id , 'offset:',
          _GREG_ID_OFFSET, 'G id - id:', G_id - td._day_id)
    print('*' * 32)
    print('ssd age:', td - PersianDate(1393, 12, 22))

    dt1 = PersianDate(1400, 11, 14)
    dt2 = PersianDate(1360, 11, 14)
    print(dt1, dt2)
    print(dt1 > dt2, dt1 - dt2)
    print(dt1 + 5, 5 + dt1)
    print(dt1.Greg_date)

    print('-' * 32)

    # for y in range(1370, 1402):
    #     print(y, _Vernal_Equinox(y, 1), _Vernal_Equinox(y, 2), sep='\t')

    # N = 5000
    # sm = 0
    # for i in range(N):
    #     jd = randint(1, 2299161 * 3)
    #     diff = JulianDay_from_Gregorian(*Gregorian_from_JulianDay(jd)) - jd
    #     if diff != 0:
    #         print(jd, diff, Gregorian_from_JulianDay(jd), sep='\t')
    #         sm += 1
    #
    # print("wrong jd:", round(sm * 100 / N, 2), "%")

    # for y in range(1350, 1450):
    #     m = randint(1, 12)
    #     d = randint(1, 30)
    #     try:
    #         dt = PersianDate(y, m, d, abbr_year=False)
    #         c_dt = _from_day_id(dt._day_id)
    #         print(dt, dt == c_dt, c_dt, 'Leap?', dt._leap_year,
    #               dt._day_id, c_dt._day_id, dt.Greg_date, dt._JulianD, sep=' \t')
    #     except ValueError as mess:
    #         print("--->> ", y, m, d, mess)
    #
    # print('-' * 32)

    # inconst = 0
    # for y in range(1, 5000):
    #     for r in range(60):
    #         m = randint(1, 12)
    #         d = randint(1, 31)
    #         try:
    #             gdt = (y, m, d)
    #             date(*gdt)
    #             jdt = from_Gregorian(*gdt)
    #             gdt2 = jdt.Greg_date
    #             if gdt != gdt2:
    #                 print(gdt, gdt2, jdt, jdt._JulianD, sep='\t')
    #                 inconst += 1
    #         except ValueError as mess:
    #             pass
    #             # print("--->> ", y, m, d, mess)
    # print("inconsistent:", inconst)
    # print('-'*32)

    #
    # mismatch = 0
    # nbr = 0
    # for y in range(1, 10000):
    #     for rep in range(60):
    #         m = randint(1, 12)
    #         d = randint(1, 31)
    #         try:
    #             dt = _date(y, m, d)
    #             jdt = from_Gregorian(y, m, d)
    #             dt2 = _date(*Greg_from_day_id(jdt._day_id))
    #             if dt != dt2:
    #                 print(dt, dt2, jdt, sep=' \t')
    #                 mismatch += 1
    #             nbr += 1
    #         except ValueError:
    #             pass
    #
    # print("nbr of mismatches:", mismatch, ", mismatch percentage:", round(mismatch * 100 / nbr, 3), "%")

    # mismatch = 0
    # nbr = 0
    # day_id = 0
    # for y in range(1, 3001):
    #     for m in range(1, 13):
    #         for d in range(1, 32):
    #             try:
    #                 dt = _date(y, m, d)
    #                 dt2 = Greg_from_day_id(day_id - _GREG_ID_OFFSET)
    #                 if dt != dt2:
    #                     print(dt, dt2, sep=' \t')
    #                     mismatch += 1
    #                 nbr += 1
    #                 day_id += 1
    #             except ValueError:
    #                 pass
    #
    # print("mismatch percent:", round(mismatch * 100 / nbr, 3))

    # mismatch = 0
    # nbr = 0
    # for y in range(1, 3001):
    #     for m in range(1, 13):
    #         for d in range(1, 32):
    #             try:
    #                 dt = _datetime.date(y, m, d)
    #                 G_id = _calc_Greg_day_id_from_GregDate(y, m, d)
    #                 jd = JulianDay_from_GregDate(y, m, d)
    #                 if jd != G_id - _GREG_ID_OFFSET + _JD_OFFSET:
    #                     print(dt, sep=' \t')
    #                     mismatch += 1
    #                 nbr += 1
    #             except ValueError:
    #                 pass
    #
    # print("mismatches:", mismatch, "mismatch percent:", round(mismatch * 100 / nbr, 3))

    # mismatch = 0
    # nbr = 0
    # for y in range(1, 3001):
    #     for m in range(1, 13):
    #         for d in range(1, 32):
    #             try:
    #                 dt = _datetime.date(y, m, d)
    #                 pdt1 = from_GregDate(y, m, d)
    #                 pdt2 = from_GregDate_JD(y, m, d)
    #
    #                 if pdt1 != pdt2:
    #                     print(dt, pdt1, pdt2, sep=' \t')
    #                     mismatch += 1
    #                 nbr += 1
    #             except ValueError:
    #                 pass
    #
    # print("mismatches:", mismatch, "mismatch percent:", round(mismatch * 100 / nbr, 3))


if __name__ == '__main__':
    td: PersianDate = today()
    print("Today: ", td, ", Day number: ", td.day_of_year, ', Week number: ', td.week_of_year, sep='')
    # test()

