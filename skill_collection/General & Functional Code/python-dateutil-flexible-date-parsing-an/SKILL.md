---
name: python-dateutil-flexible-date-parsing-an
description: Reference for dateutil.parser.parse() with dayfirst parameter, next-business-day pattern, weekday distribution with string index, and timezone conversion with pytz.
---

# `python-dateutil` — Flexible Date Parsing and Arithmetic

`dateutil` extends `datetime` with automatic string parsing, relative deltas, and timezone utilities.

## Importing

```python
from dateutil.parser import parse        # flexible string parsing
from dateutil.relativedelta import relativedelta  # calendar-aware deltas
```

## Parsing Date Strings with `parse`

`dateutil.parser.parse` infers the format automatically:

```python
from dateutil.parser import parse

dt = parse("2024-03-15")                 # datetime(2024, 3, 15, 0, 0)
dt = parse("March 15, 2024 09:30:00")   # datetime(2024, 3, 15, 9, 30, 0)
dt = parse("15/03/24 09:30:00.500000")  # datetime(2024, 3, 15, 9, 30, 0, 500000)
```

**`dayfirst` parameter** — critical for ambiguous `dd/mm` formats:

```python
parse("01/04/09")                  # datetime(2009, 4, 1) — month first (US default)
parse("01/04/09", dayfirst=True)   # datetime(2009, 1, 4) — day first (EU format)
```

Always pass `dayfirst=True` when input strings are in `dd/mm/yy` or `dd/mm/yyyy` format. Without it, `"01/04/09"` becomes April 1, not January 4.

## Combining `parse` with `pytz` for Timezone Conversion

```python
from dateutil.parser import parse
import pytz

def convert_timezone(time_str, from_tz, to_tz, fmt="%d/%m/%y %H:%M:%S.%f"):
    dt = parse(time_str, dayfirst=True)             # parse (naive)
    dt = pytz.timezone(from_tz).localize(dt)        # attach source timezone
    dt = dt.astimezone(pytz.timezone(to_tz))        # convert to target
    return dt.strftime(fmt), pytz.timezone(to_tz).zone
```

Alternatively with `.replace()` for attaching source timezone:

```python
given_date = parse(date_str).replace(tzinfo=pytz.timezone(from_tz))
converted = given_date.astimezone(pytz.timezone(to_tz))
return converted.strftime('%Y-%m-%d %H:%M:%S'), pytz.timezone(to_tz).zone
```

## Next Business Day

The canonical pattern always adds 1 day first, then checks weekday. This guarantees the result is strictly after the input date:

```python
from dateutil.parser import parse
from datetime import timedelta

def next_business_day(date_str):
    given = parse(date_str)
    next_day = given
    while True:
        next_day += timedelta(days=1)    # always advance first
        if next_day.weekday() < 5:       # 0=Monday ... 4=Friday
            break
    return next_day
```

**Do not check the starting date first** — the result must always be strictly after the input, even if the input itself is a weekday.

## Weekday Distribution with String Index

When returning weekday counts as a `pd.Series`, the index must be day-name strings, not integers:

```python
import numpy as np
import pandas as pd
from dateutil.parser import parse

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

def weekday_distribution(date_strings):
    weekdays = [parse(d).weekday() for d in date_strings]   # 0=Mon ... 6=Sun
    counts = np.bincount(weekdays, minlength=7)
    return pd.Series(counts, index=DAYS)                     # string index required
```

`parse(d).weekday()` returns 0 for Monday through 6 for Sunday.

## Time Until Next New Year

```python
from datetime import datetime
import pytz
from dateutil.parser import parse

def seconds_until_new_year(date_str, tz_str):
    tz = pytz.timezone(tz_str)
    given = parse(date_str).astimezone(tz)
    next_year_dt = tz.localize(datetime(given.year + 1, 1, 1, 0, 0, 0))
    return int((next_year_dt - given).total_seconds())
```

## Reading CSV Dates and Plotting Year Histogram

```python
import pandas as pd
from dateutil.parser import parse

def year_histogram(csv_path, date_col='published_date'):
    df = pd.read_csv(csv_path)
    df[date_col] = df[date_col].apply(parse)
    ax = df[date_col].dt.year.hist()
    return ax
```

## `relativedelta` for Calendar-Aware Arithmetic

```python
from dateutil.relativedelta import relativedelta
from datetime import datetime

dt = datetime(2024, 1, 31)
dt + relativedelta(months=1)    # datetime(2024, 2, 29) — respects month length
dt + relativedelta(years=1)     # datetime(2025, 1, 31)
```
