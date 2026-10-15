---
name: datetime-date-and-time-operations-in-pyt
description: 'Guide for correct datetime API usage: parsing, formatting, arithmetic, epoch conversion, date sequences, timezone handling, and common type pitfalls.'
---

# Python `datetime` Module — Practical Reference

## Core Classes

- `datetime.datetime` — full date + time
- `datetime.date` — date only (year, month, day)
- `datetime.time` — time only (hour, minute, second, microsecond)
- `datetime.timedelta` — duration between two points

`from datetime import datetime, date, time, timedelta` imports the classes directly.

## Constructing and Getting the Current Time

```python
from datetime import datetime, timedelta

now = datetime.now()            # local naive datetime
today = datetime.now().date()   # date object, no time component
utc_now = datetime.utcnow()    # UTC naive datetime

# From a Unix timestamp (in SECONDS)
dt = datetime.fromtimestamp(1_700_000_000)       # local time
dt_utc = datetime.utcfromtimestamp(1_700_000_000)  # UTC
```

When epoch is given in **milliseconds** (parameter named `epoch_milliseconds`), divide by 1000:
```python
dt = datetime.fromtimestamp(epoch_ms / 1000.0)   # local time, returns datetime object
```

Keep the result as a `datetime` object — do not convert to string unless the spec explicitly requires a specific format. Storing `datetime` objects in a DataFrame column enables arithmetic and `.dt` accessor operations.

## Parsing and Formatting

`strptime` parses a **string** into a `datetime`; `strftime` formats a `datetime` into a string.

```python
from datetime import datetime

dt = datetime.strptime("2024-03-15 09:30:00", "%Y-%m-%d %H:%M:%S")
dt2 = datetime.strptime("15/03/24 09:30:00.500", "%d/%m/%y %H:%M:%S.%f")

s = dt.strftime("%Y-%m-%d %H:%M:%S")   # "2024-03-15 09:30:00"
```

If a parameter is already a `datetime` object, do not call `strptime` on it.

Common format codes:
- `%Y` four-digit year, `%y` two-digit year, `%m` month, `%d` day
- `%H` hour (24h), `%M` minute, `%S` second, `%f` microseconds (6 digits)
- `%A` full weekday name, `%B` full month name, `%Z` timezone abbreviation
- `%Y%m%d%H%M%S%f` — compact timestamp including microseconds (6-digit `%f`)

`str(dt)` produces `"2024-03-15 09:30:00.123456"` — useful for storing current time as a plain string.

## Arithmetic with timedelta

```python
from datetime import datetime, timedelta

dt = datetime(2024, 3, 15)
tomorrow = dt + timedelta(days=1)
diff = datetime(2024, 4, 1) - datetime(2024, 3, 15)

diff.days             # 17 (integer days only)
diff.total_seconds()  # 1468800.0 — total elapsed time
```

`diff.seconds` is only the seconds component of the day remainder, not the total — use `.total_seconds()` for full duration.

## Building Date Sequences

```python
import pandas as pd
from datetime import datetime, timedelta

# N days ending today (inclusive) — exactly N dates
dates = pd.date_range(end=datetime.now().date(), periods=7)

# Between start and end (inclusive on both ends)
date_range = pd.date_range(start="2024-01-01", end="2024-01-31")

# Using parsed datetime objects
start_dt = datetime.strptime(start_str, "%Y-%m-%d")
end_dt   = datetime.strptime(end_str,   "%Y-%m-%d")
date_range = pd.date_range(start_dt, end_dt)   # same as above
```

`start=X - timedelta(days=N), end=X` creates N+1 dates. Use `periods=N` to get exactly N.

## Generating Time Series DataFrames

Build the column data as a dict, then pass to `pd.DataFrame`. This avoids shape-mismatch errors when multiple series have the same number of entries:

```python
import pandas as pd
from datetime import datetime
import random

def make_time_series(start_str, end_str, series_names, seed=None):
    if seed is not None:
        random.seed(seed)
    date_range = pd.date_range(start=start_str, end=end_str)
    data = {name: [random.randint(0, 100) for _ in date_range]
            for name in series_names}
    df = pd.DataFrame(data, index=date_range)
    return df
```

## Iterating with Growing Timestamps (Logs / Event Streams)

The canonical pattern for generating log-style records up to "now":

```python
from datetime import datetime, timedelta
import random
import pandas as pd

def generate_event_log(start_ms, seed=0):
    random.seed(seed)
    current = datetime.fromtimestamp(start_ms / 1000.0)  # local datetime object
    end = datetime.now()
    if current >= end:
        raise ValueError("Start time must be before current system time")

    records = []
    while current <= end:
        records.append({"User": random.choice(USERS),
                        "Action": random.choice(ACTIONS),
                        "Time": current})          # store datetime object, not string
        current += timedelta(seconds=random.randint(1, 10))

    return pd.DataFrame(records)
```

## Day-of-Week Patterns

```python
from datetime import datetime
from collections import defaultdict

activity_counts = defaultdict(int)
for dt in timestamps:
    activity_counts[dt.strftime('%A')] += 1

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
counts = [activity_counts[day] for day in days]   # zero-safe ordering
```

`weekday()` returns 0=Monday … 6=Sunday. `isoweekday()` returns 1=Monday … 7=Sunday.

## `datetime.time` Object

`datetime.time` is a standalone time-of-day class, separate from the `time` module.

```python
from datetime import time

t = time(9, 30, 0)   # 09:30:00
t.hour    # 9
t.minute  # 30

# Average time from accumulated minutes
avg_min = total_minutes // n
avg_time = time(avg_min // 60, avg_min % 60)

# Return as a plain tuple, not a dict
return error_times, avg_time
```

## Working with numpy datetime64

```python
import numpy as np
from datetime import datetime

start_np = np.datetime64(start_str)      # e.g. "2021-01-01"
end_np   = np.datetime64(end_str)

# Convert timedelta64 to int days
n_days = int((end_np - start_np).astype('timedelta64[D]').astype(int)) + 1
```

`int(end - start)` on two `datetime.datetime` objects returns a `timedelta`, not an int.

## Timezone Conversion with pytz

```python
from datetime import datetime
import pytz

tz = pytz.timezone("America/New_York")

# Convert a UTC-aware datetime to local
utc_aware = utc_dt.replace(tzinfo=pytz.utc)   # or .astimezone() if already aware
local_dt  = utc_aware.astimezone(tz)
formatted = local_dt.strftime('%Y-%m-%d %H:%M:%S %Z')  # includes tz abbreviation

# Localize a naive datetime (treats it as being in `tz`)
local_aware = tz.localize(naive_dt)
```

When iterating over a city→timezone mapping, raise a descriptive error for missing keys:
```python
for city in cities:
    if city not in timezones:
        raise ValueError(f"Timezone for {city} not provided")
    city_tz = pytz.timezone(timezones[city])
```

## Key Dict Schema for Script Execution Results

When running a subprocess and returning timing metadata, use the exact key names from the spec:

```python
import subprocess, shlex
from datetime import datetime

start = datetime.now()
proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = proc.communicate()
end = datetime.now()

return {
    'Start Time': str(start),
    'End Time':   str(end),
    'Stdout':     stdout.decode('utf-8'),
    'Stderr':     stderr.decode('utf-8'),
}
```

## matplotlib.dates.DateFormatter

`DateFormatter` lives in `matplotlib.dates`, not `matplotlib.pyplot`:

```python
import matplotlib.dates as mdates

ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
```
