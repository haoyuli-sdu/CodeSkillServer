---
name: pytz-timezone-aware-datetime-conversion
description: Reference for pytz.timezone(), localize() vs astimezone(), Unix timestamp conversion, pd.to_datetime().astimezone(), and timezone validation patterns.
---

# `pytz` — Timezone-Aware Datetime Handling

`pytz` attaches IANA timezone information to `datetime` objects for timezone conversion.

## Getting a Timezone Object

```python
import pytz
from datetime import datetime

tz = pytz.timezone("America/New_York")   # IANA name → timezone object
utc = pytz.utc                           # canonical UTC constant
```

## `localize()` vs `astimezone()` — Critical Distinction

- **`tz.localize(naive_dt)`** — attaches timezone to a naive datetime (no tzinfo). Raises `ValueError: Not naive datetime` if tzinfo is already set.
- **`aware_dt.astimezone(tz)`** — converts an already-aware datetime to a different timezone.

```python
naive = datetime(2024, 6, 15, 9, 0, 0)          # no tzinfo

# Attach a source timezone (naive → aware)
from_tz = pytz.timezone("US/Eastern")
aware = from_tz.localize(naive)                   # correct
# aware = naive.replace(tzinfo=from_tz)           # also works for simple cases

# Convert to target timezone (aware → aware)
to_tz = pytz.timezone("Europe/Paris")
converted = aware.astimezone(to_tz)
result = converted.strftime("%Y-%m-%d %H:%M:%S")
```

**Do not call `localize()` on an already-aware datetime** — use `astimezone()` instead.

## Unix Timestamp → Timezone-Aware Datetime

`datetime.fromtimestamp(ts, tz)` expects **seconds** (standard Unix time). Millisecond timestamps need division first:

```python
from datetime import datetime
import pytz

ts_seconds = 1_700_000_000
tz = pytz.timezone("Asia/Tokyo")
dt = datetime.fromtimestamp(ts_seconds, tz)       # tz-aware datetime
formatted = dt.strftime("%Y-%m-%d %H:%M:%S")

# From milliseconds:
ts_ms = 1_234_567_890_000
dt = datetime.fromtimestamp(ts_ms / 1000.0)       # naive, system timezone
```

Alternatively via UTC:
```python
dt = datetime.utcfromtimestamp(ts_seconds).replace(tzinfo=pytz.utc).astimezone(tz)
```

## Applying Timezone to String Timestamps

Use `pd.to_datetime(val).astimezone(tz)` when the input format is uncertain:

```python
import pandas as pd
import pytz

tz = pytz.timezone("US/Eastern")
for record in records:
    record['timestamp'] = pd.to_datetime(record['timestamp']).astimezone(tz)
```

For a known format, use `datetime.strptime` then `localize`:

```python
from datetime import datetime
import pytz

fmt = "%d/%m/%y %H:%M:%S.%f"
naive = datetime.strptime("01/04/21 12:00:00.000", fmt)
aware = pytz.timezone("US/Eastern").localize(naive)
```

## Timezone Validation

```python
import pytz, re

utc_offset_regex = r"^UTC([+-])(0[0-9]|1[0-4]):([0-5][0-9])$"

def is_valid_timezone(tz_str):
    return (tz_str == "UTC"
            or re.match(utc_offset_regex, tz_str)
            or tz_str in pytz.all_timezones)
```

## Full Conversion Recipe

```python
from datetime import datetime
import pytz

def convert_tz(dt_str, from_tz_name, to_tz_name, fmt="%Y-%m-%d %H:%M:%S"):
    from_tz = pytz.timezone(from_tz_name)
    to_tz = pytz.timezone(to_tz_name)
    naive = datetime.strptime(dt_str, fmt)
    aware = from_tz.localize(naive)
    converted = aware.astimezone(to_tz)
    return converted.strftime(fmt), to_tz.zone   # returns (str, zone_name)
```

## Result Types from `datetime` Methods

- `dt.date()` → `datetime.date` object (not a string)
- `dt.time()` → `datetime.time` object (not a string)
- `dt.strftime(fmt)` → `str`
- `dt.astimezone(tz)` → `datetime` object (tz-aware)
- `pytz.timezone(name).zone` → the IANA zone name string (e.g. `"America/New_York"`)

## Iterating Cities with Timezone Lookup

When cities map to timezone strings in a dict, raise `ValueError` for missing cities (not `KeyError`):

```python
import pytz
from datetime import datetime

def get_local_times(utc_dt, cities, timezones):
    if not isinstance(utc_dt, datetime):
        raise ValueError("utc_dt must be a datetime object")
    rows = []
    for city in cities:
        if city not in timezones:
            raise ValueError(f"No timezone for {city}")
        tz = pytz.timezone(timezones[city])
        local = utc_dt.astimezone(tz)
        rows.append((city, local.strftime("%Y-%m-%d %H:%M:%S %Z")))
    return rows
```

## `strftime` Format Specifiers

- `%Z` — timezone abbreviation (e.g. `EST`, `UTC`)
- `%z` — UTC offset as `+HHMM` (e.g. `+0530`)
- `%f` — microseconds (6 digits)
