import datetime as dt


def year(req):
    year_current = dt.date.today().year
    return {
        'year': year_current
    }
