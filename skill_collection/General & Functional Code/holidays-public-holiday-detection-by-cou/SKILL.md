---
name: holidays-public-holiday-detection-by-cou
description: 'Guide for holidays library: CountryHoliday() takes only country string (no dates= kwarg), business day filtering with weekday() < 5, pd.date_range membership testing.'
---

# holidays — Public Holiday Detection by Country

The `holidays` library provides country-specific public holiday calendars queryable like a dictionary.

## Constructor Variants

```python
import holidays

# Country-specific class (pre-loads a year):
us = holidays.US(years=2024)
ca = holidays.CA(years=[2023, 2024])

# Generic constructor by ISO country code:
h = holidays.country_holidays('US', years=2024)

# Dynamic lookup (no year pre-loading, checks dates on-the-fly):
h = holidays.CountryHoliday('US')
```

`holidays.CountryHoliday(country)` takes only the ISO country code string — there is no `dates=` or `year=` keyword argument. Holiday lookup happens dynamically as dates are queried.

## Checking Dates

```python
from datetime import date
import holidays

h = holidays.US(years=2024)
date(2024, 12, 25) in h      # True
h.get(date(2024, 12, 25))    # "Christmas Day"
```

Works with `date`, `datetime`, and `pd.Timestamp` objects.

## Business Day Filtering

```python
import pandas as pd
from datetime import datetime
import holidays

def business_days(start_date, end_date, country='US'):
    if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
        raise ValueError("start_date and end_date must be datetime objects.")
    if start_date > end_date:
        raise ValueError("start_date must not be after end_date.")

    country_holidays = holidays.CountryHoliday(country)
    dates = pd.date_range(start_date, end_date)
    return [d for d in dates if d.weekday() < 5 and d not in country_holidays]
```

`weekday()` returns 0 (Monday) through 6 (Sunday); `< 5` keeps Mon–Fri only.

`pd.date_range()` returns `pd.Timestamp` objects that support `in` membership testing against a `holidays` calendar.

## Iterating Holidays

```python
for dt, name in sorted(h.items()):
    print(dt, name)
```

## Multi-Year Loading

```python
h = holidays.US(years=range(2020, 2025))   # loads 2020–2024
```
