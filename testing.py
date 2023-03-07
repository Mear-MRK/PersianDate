import persian_date as pdt
import datetime

def _greg_leap_year(year):
    return year % 4 == 0 and year % 100 != 0 or year % 400 == 0
    
def test_GregDate_id():
    max_id = 4000 * 365 + 4000//4
    inc = 0
    prn = 0
    for id1 in range(max_id):
        gdt = pdt._GregDate_from_day_id(id1)
        id2 = pdt._calc_Greg_day_id_from_GregDate(*gdt)
        try:                 
            dt = datetime.date(*gdt)
            ordn = dt.toordinal()-1
        except:
            if prn < 1000:
                print('Invalid date!', id1, id2, gdt,'N/A', _greg_leap_year(gdt[0]))
                prn += 1
            inc += 1
        else:
            if id1 != id2 or id1 != ordn or id2 != ordn:
                inc += 1
                if prn < 1000:
                    print('Id doesn\'t match!', id1, id2, ordn , gdt, _greg_leap_year(gdt[0]))
                    prn += 1
    return inc, inc * 100 / max_id

if __name__ == '__main__':

    per_0_id = pdt.persian_date(1, 1, 1)._day_id
    greg_0_id = pdt._calc_Greg_day_id_from_GregDate(1, 1, 1)
    print("Zero Persian day id:", per_0_id)
    print("Zero Greg day id:", greg_0_id)
    print(greg_0_id - per_0_id == pdt._GREG_ID_OFFSET)

    print('-' * 32)

    now = datetime.datetime.today()
    G_td = now.year, now.month, now.day
    print('Today Greg. datetime.date:', now.date())
    print('Today Per. date:', pdt.today())
    print('Now in Iran:', pdt.now())
    print('Today Per. to Greg. tuple:', pdt.today().gregorian_date)
    print('Today Per. to datetime.date:', pdt.today().datetime_date)
    print('Today from Greg. tuple:', pdt.from_gregorian_date(*G_td))
    print('Today from Greg. datetime.date:', pdt.from_datetime_date(now.date()))

    print('-' * 32)
    
    print(test_GregDate_id())
    
    #print(test_GregDate_from_id())

    # dt1 = persian_date(1400, 11, 14)
    # dt2 = persian_date(1360, 11, 14)
    # print(dt1, dt2)
    # print(dt1 > dt2, dt1 - dt2)
    # print(dt1 + 5, 5 + dt1)
    # print(dt1.Greg_date)

    # print('-' * 32)

    # for y in range(1370, 1402):
    #     print(y, _vernal_equinox(y, 1), _vernal_equinox(y, 2), sep='\t')

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
    #         dt = persian_date(y, m, d, abbr_year=False)
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