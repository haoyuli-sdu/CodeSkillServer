---
name: calendar-calendar-utilities-and-weekday
description: Reference for calendar.day_name indexing, weekday calculations, and UTC-aware date arithmetic.
---

# Python calendar Module — Practical Reference

The `calendar` module provides utilities for working with calendars, weekdays, and month/year layouts.

## Weekday Name Lookup

`calendar.day_name` is a sequence of full weekday names indexed 0 (Monday) through 6 (Sunday). Use it with `datetime.weekday()`:

```python
import calendar

# calendar.day_name[0] == "Monday"
# calendar.day_name[4] == "Friday"
# calendar.day_name[6] == "Sunday"

day_name = calendar.day_name[some_date.weekday()]  # e.g., "Friday"
```

`calendar.day_abbr` provides three-letter abbreviations: `["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]`.

There is no `calendar.weekname()` function. The correct API is `calendar.day_name[n]` where `n` is an integer 0–6.

## Key Functions

```python
import calendar

# Day of week (0=Monday, 6=Sunday) for a given date
dow = calendar.weekday(year, month, day)

# Number of days in a month; monthrange returns (weekday_of_first_day, days_in_month)
days = calendar.monthrange(year, month)[1]

# Check if year is a leap year
is_leap = calendar.isleap(year)
```

## "N Days Ago" Weekday Pattern

Compute the weekday name for a date that is `n` days before today using UTC time:

```python
from datetime import datetime, timedelta
import pytz
import calendar

def weekday_n_days_ago(n):
    if n < 0:
        raise ValueError("n cannot be negative")
    target = datetime.now(pytz.UTC) - timedelta(days=n)
    return calendar.day_name[target.weekday()]
```

`datetime.now(pytz.UTC)` returns a timezone-aware datetime in UTC. `target.weekday()` returns an integer 0–6; index into `calendar.day_name` to get the full English name.

## Weekday Constants

`calendar.MONDAY` through `calendar.SUNDAY` are integer constants (0–6), useful for comparisons:

```python
if some_date.weekday() == calendar.FRIDAY:
    print("It's Friday")
```
