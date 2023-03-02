import datetime as _datetime
from bisect import bisect as _bisect


# Remainders of Persian leap years divided by 33
_LEAP_REM = {1, 5, 9, 13, 17, 22, 26, 30}

# Number of days before each year in a 33-Persian-year cycle (1-33),
# assuming that the year that (year % 33 == 22) is the irregular Persian leap year.
_CUM_ND_1Y_33Y = (0, 366, 731, 1096, 1461, 1827, 2192, 2557, 2922, 3288, 3653,
                  4018, 4383, 4749, 5114, 5479, 5844, 6210, 6575, 6940, 7305, 7670,
                  8036, 8401, 8766, 9131, 9497, 9862, 10227, 10592, 10958, 11323, 11688)

# Number of days in 33 consecutive Persian years
_ND_33Y = 12053

# Number of days before each month in a common Gregorian year
_CUM_ND_1M_1COM_GY = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)

# Number of days before each month in a leap Greg. year
_CUM_ND_1M_1LEAP_GY = (0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335)

# Number of days in 4 consecutive Greg. years, assuming last year is leap.
_ND_4GY = 4*365 + 1
# Number of days in 100 consecutive Greg. years, assuming last year is not leap.
_ND_100GY = 25*_ND_4GY - 1
# Number of days in 400 consecutive Greg. years
_ND_400GY = 4*_ND_100GY + 1  


# Offset to calculate Greg. day id from Per. day id
_GREG_ID_OFFSET = 226894

# 3-letter short form of weekday names of the Persian calendar
_WEEKDAY_ABBR = ('shn', '1sh', '2sh', '3sh', '4sh', '5sh', 'jom')

# 3-letter short form of month names of the Persian calendar
_MONTH_ABBR = ('Far', 'Ord', 'Kho', 'Tir', 'Mor', 'Sha', 'Meh', 'Aba', 'Aza', 'Dey', 'Bah', 'Esf')


class PersianDate:
    """A class that defines a Persian date in Persian/Solar Hijri calendar."""
    
    __slots__ = ('_year', '_month', '_day', '_weekday_id', '_day_of_week', '_day_of_year',
                 '_week_of_year', '_leap_year', '_Greg_date', '_day_of_year', '_day_id', '_hash')

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
    def Greg_date(self) -> tuple[int, int, int]:
        if self._Greg_date is None:
            self._Greg_date = _GregDate_from_g_day_id(self._day_id + _GREG_ID_OFFSET)
        return self._Greg_date
        
    @property
    def datetime_date(self) -> _datetime.date:
        return _datetime.date(*self.Greg_date)

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


def now(daylight_saving=False) -> PersianDate:
    """Gives current Persian date of Iran (IRST). By default, doesn't consider for daylight saving."""
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone(timedelta(hours=3+int(daylight_saving), minutes=30)))
    return from_GregDate(now.year, now.month, now.day)

    
def today() -> PersianDate:
    """Gives today Persian date."""
    td = _datetime.date.today()
    return from_GregDate(td.year, td.month, td.day)
    

# day_id for 01-01-01 is 0
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


# Greg. day_id for 01-01-01 is 0
def _calc_Greg_day_id_from_GregDate(year: int, month: int, day: int) -> int:
    y = year - 1
    m = month - 1
    d = day - 1
    d1 = 365 * y + y // 4 - y // 100 + y // 400
    leap = year % 4 == 0 and year % 100 != 0 or year % 400 == 0
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

    return PersianDate(year, month, day)


def _float_per_datetime(year: int, month: int, day: int, h: int, m: int, s: float) -> float:
    day = _calc_day_id(year, month, day)
    f = (h + (m + s / 60) / 60) / 24
    return day + f
    

def _GregDate_from_g_day_id(g_day_id: int):
    n400y, rd = divmod(g_day_id, _ND_400GY)
    n100y, rd = divmod(rd, _ND_100GY)
    if n100y == 4:
        n100y = 3
        rd += _ND_100GY
    n4y, rd   = divmod(rd, _ND_4GY)
    n1y, rd   = divmod(rd, 365)
    if n1y == 4:
        n1y = 3
        rd += 365
    
    leap_year = n1y == 3 and (n4y != 24 or n100y == 3)
    cum_nbr_days = _CUM_ND_1M_1LEAP_GY if leap_year else _CUM_ND_1M_1COM_GY

    year = n400y * 400 + n100y * 100 + n4y * 4 + n1y + 1
    month = _bisect(cum_nbr_days, rd)
    day = rd - cum_nbr_days[month - 1] + 1

    return year, month, day


def from_GregDate(year: int, month: int, day: int) -> PersianDate:
    g_id = _calc_Greg_day_id_from_GregDate(year, month, day)
    return _from_day_id(g_id - _GREG_ID_OFFSET)
    
    
def from_datetime_date(date: _datetime.date) -> PersianDate:
    return  from_GregDate(date.year, date.month, date.day)


if __name__ == '__main__':
    td = today()
    print("Today in Persian date:", td, ", Day number: ", td.day_of_year, ', Week number: ', td.week_of_year, sep='')
    print('Now in Iran (UTC+3:30):', now())

