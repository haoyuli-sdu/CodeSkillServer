---
name: faker-generating-reproducible-fake-data
description: 'Guide for reproducible fake data generation: class-level vs instance-level seeding, calling order effects, datetime native types.'
---

# Faker — Generating Reproducible Fake Data

## Seeding for Reproducibility

`Faker.seed(n)` is a class-level call that seeds the shared RNG for all instances. Call it before creating the `Faker()` instance:

```python
from faker import Faker

Faker.seed(42)
fake = Faker()
name = fake.name()          # same value every run with seed 42
first = fake.unique.first_name()
```

`fake.seed_instance(n)` is an instance-level alternative that seeds only one instance without affecting others. Both forms accept `None` — passing `None` simply resets or disables seeding:

```python
fake = Faker()
fake.seed_instance(seed_value)   # works with any value, including None
```

When a function also uses `random.randint()` for numeric fields, seed the stdlib module independently with the same value:

```python
import random
Faker.seed(seed)
random.seed(seed)
fake = Faker()
```

## Calling Order Affects Reproducibility

Faker methods consume RNG state in the order they are called. When building rows with multiple fields, always generate them in a **fixed, consistent order**. Interleaving calls differently between runs (e.g., computing address before name, or skipping a call) shifts all subsequent values:

```python
import csv
import random
from faker import Faker

def write_records(file_path, n, seed=None):
    Faker.seed(seed)
    random.seed(seed)
    fake = Faker()

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Age", "Address", "Email"])
        for _ in range(n):
            name    = fake.name()
            age     = random.randint(20, 60)
            address = fake.address().replace("\n", ", ")
            email   = fake.email()
            writer.writerow([name, age, address, email])
    return file_path
```

`fake.address()` commonly contains embedded newlines — replace `\n` with `", "` before writing to single-line formats like CSV.

## Datetime from Epoch

`datetime.fromtimestamp(epoch_sec)` returns a local-timezone `datetime` — no pytz needed for local time. Access `.date()` and `.time()` as native objects, not strings:

```python
from datetime import datetime

dt = datetime.fromtimestamp(epoch_ms / 1000.0)
d = dt.date()   # datetime.date(2024, 3, 15) — not '2024-03-15'
t = dt.time()   # datetime.time(14, 30, 0)   — not '14:30:00'
```

Keep these as `datetime.date` / `datetime.time` objects in dicts and return values.

## Commonly Used Generators

| Method | Returns |
|---|---|
| `fake.name()` | Full name string |
| `fake.unique.first_name()` | First name, non-repeating within this instance |
| `fake.address()` | Multi-line address string (may contain `\n`) |
| `fake.email()` | Email address string |
| `fake.random_element(elements=seq)` | Random item from sequence (respects Faker's RNG) |
