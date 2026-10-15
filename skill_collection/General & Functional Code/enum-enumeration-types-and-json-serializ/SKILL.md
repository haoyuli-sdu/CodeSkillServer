---
name: enum-enumeration-types-and-json-serializ
description: 'Reference for Python enum module: Enum vs IntEnum, member access, JSON serialization with custom encoder.'
---

# Python `enum` Module — Enumeration Types

## Defining Enumerations

```python
from enum import Enum, IntEnum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

class Priority(IntEnum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
```

- `Enum` — symbolic names bound to unique values
- `IntEnum` — members are also ints and compare equal to integer values

## Accessing Enum Members

```python
Color.RED           # <Color.RED: 1>
Color.RED.name      # 'RED'
Color.RED.value     # 1
Color['RED']        # access by name string
Color(1)            # access by value
```

## JSON Serialization with Enum

`json.dumps` raises `TypeError` for Enum members. Use a custom encoder:

```python
import json
from enum import Enum

class StatusEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value   # serialize as the underlying value
        return super().default(obj)

data = {'status': Color.RED, 'label': 'active'}
json.dumps(data, cls=StatusEncoder)   # '{"status": 1, "label": "active"}'
```

Inline serialization:

```python
json.dumps({'color': Color.RED.value})   # using numeric value
json.dumps({'color': Color.RED.name})    # using string name
```

## Iterating Enum Members

```python
for member in Color:
    print(member.name, member.value)

list(Color)           # [<Color.RED: 1>, <Color.GREEN: 2>, <Color.BLUE: 3>]
Color.__members__     # OrderedDict mapping name → member
```

## `Enum` vs `IntEnum` Comparison

```python
class Size(Enum):
    S = 1

class ISize(IntEnum):
    S = 1

Size.S == 1    # False — Enum does not compare with plain ints
ISize.S == 1   # True — IntEnum does
```
