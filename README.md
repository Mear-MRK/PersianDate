# Persian Calendar
This repository contains Python modules related to the Persian (Solar Hijri/Jalali) calendar (https://en.wikipedia.org/wiki/Solar_Hijri_calendar).

## Persian date
Module `persian_date` represents Persian dates and can be used to convert from/to Gregorian dates. We are using a very simple rule to find Persian leap years which is in accordance with officially announced list of leap years for 1206 <= year <= 1498 by the Institute of Geophysics at the University of Tehran.

The module includes:
  - The `PersianDate` class, which represents a date in the Persian calendar.
  - The `gregorian_date` property of the `PersianDate` class, which provides the equivalent date in the Gregorian calendar.
  - The `from_gregorian_date` function, which returns the Persian date equivalent of a given Gregorian date.
  - The `from_datetime_date` function, which returns the Persian date equivalent of a `datetime.date` object.
  
It is possible to subtract two Persian dates which gives the difference in days. Also, one can add an int to a date to get a new date that amount of days ahead.

## Persian new year
Module `persian_newyear` gives an estimate of the moment of the Persian new year (Nowruz) by computing the spring equinox using two different formulae. It must be noted that the result is not the exact official moment of Nowruz and usually has a 15 min difference. 
