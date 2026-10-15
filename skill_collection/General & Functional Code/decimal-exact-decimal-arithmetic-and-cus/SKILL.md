---
name: decimal-exact-decimal-arithmetic-and-cus
description: 'Guide for Decimal type: construction, arithmetic, and JSONEncoder delegation pattern.'
---

# Python `decimal` Module — Exact Decimal Arithmetic and JSON Serialization

`Decimal` provides arbitrary-precision decimal arithmetic that avoids the rounding errors of binary floating-point. Its most common integration point is JSON serialization: `json.JSONEncoder` does not handle `Decimal`, `datetime`, or `numpy.ndarray` out of the box.

## Custom JSONEncoder Pattern

Subclass `json.JSONEncoder`, override `default()`, then pass `cls=MyEncoder` to `json.dumps`. The final line of `default()` must delegate to the base class — this is what causes `TypeError` to propagate for truly unsupported types:

```python
import json
from decimal import Decimal
from datetime import datetime
import numpy as np

class ExtendedEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()        # "2024-01-15T12:00:00"
        if isinstance(obj, Decimal):
            return str(obj)               # "3.14"  (preserves exact representation)
        if isinstance(obj, np.ndarray):
            return obj.tolist()           # [1.0, 2.0, 3.0]
        return super().default(obj)       # raises TypeError for unsupported types

def serialize(data):
    return json.dumps(data, cls=ExtendedEncoder)
```

Two details that affect correctness:
- `str(obj)` for `Decimal`, not `float(obj)` — `float(Decimal('99.99'))` can introduce binary rounding error.
- `super().default(obj)` at the end, not a manual `raise TypeError(...)`. The base implementation raises `TypeError` with the standard message; raising manually or catching `TypeError` from a different variable can produce wrong messages or swallow the exception.

## Decimal Basics

```python
from decimal import Decimal, getcontext

getcontext().prec = 10           # global precision for division

d = Decimal('3.14159')           # construct from string: exact
d2 = Decimal('1.5') + Decimal('2.5')    # Decimal('4.0')
d3 = Decimal('10') / Decimal('3')       # Decimal('3.333333333')
str(d)                            # '3.14159'  — round-trip safe
float(d)                          # 3.14159 as Python float
```

Always construct from strings, not floats: `Decimal(0.1)` captures the binary floating-point representation (`0.1000000000000000055511...`), not the decimal value `0.1`.

## Which Types to Handle

Match the encoder's type coverage to what the task specifies:

| Data type         | Canonical serialisation    |
|-------------------|---------------------------|
| `datetime`        | `obj.isoformat()`          |
| `Decimal`         | `str(obj)`                 |
| `numpy.ndarray`   | `obj.tolist()`             |
| anything else     | `super().default(obj)`     |

The `super().default(obj)` delegation handles the "unsupported type" contract — callers that pass an unknown object receive `TypeError` automatically, without any explicit `raise` in user code.
