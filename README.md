# PersianDate
A Python module that comprises classes and functions which define and convert a date in the Persian (Soalr Hijri) calendar.

Notably, the module contains:
 - class `PersianDate` which encapsulates a date in the Persian calendar;
 - property `gregorian_date` of `PersianDate` which gives the equivalent Gregorian date;
 - function `from_gregorian_date` is a builder function that gives the Persian date equivalent of a Greg. date;
 - function `from_datetime_date` is a builder function that gives the Persian date equivalent of a `datetime.date` object.
