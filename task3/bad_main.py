def calc(p, q, s, t, r, cp):
    # p - цена, q - кол-во, s - id продавца, t - тип клиента, r - регион, cp - купон
    a = p * q
    b = 0
    if t == 1:
        b = 0.15
    elif t == 2:
        b = 0.10
    else:
        b = 0.05

    a = a - (a * b)
    if cp > 0:
        a = a - cp

    c = 0
    if r == 1:
        c = 0.20
    elif r == 2:
        c = 0.18
    elif r == 3:
        c = 0.13
    else:
        c = 0.15

    a = a + (a * c)

    d = 0
    if s in [101, 102, 103, 104]:
        d = 0.05
    elif s in [201, 202, 203]:
        d = 0.08
    else:
        d = 0.12

    e = a * d
    f = a - e

    if f < 0:
        f = 0
    if f == 0:
        return "Ошибка"

    return round(f, 2)