---
name: types-lambdatype-and-function-type-check
description: Guide for types.LambdaType alias, lambda detection for flag vs validation contexts, inspect.getfullargspec integration, and annotation string conversion.
---

# Python `types` Module — Function and Lambda Type Checking

## `types.LambdaType` and `types.FunctionType`

`types.LambdaType` is an alias for `types.FunctionType`. Both evaluate to `True` for any
Python function — named or lambda:

```python
import types

regular_func = lambda x: x
def named_func(x): return x

isinstance(regular_func, types.LambdaType)  # True
isinstance(named_func, types.LambdaType)    # True — LambdaType is FunctionType!
```

When used for an `is_lambda` flag in a specification dict (per canonical pattern below),
`isinstance(f, types.LambdaType)` is the expected form even though it returns `True` for
all functions. When the task is to *detect* whether the function is truly a lambda (e.g.,
to raise ValueError), use the name check instead: `f.__name__ == '<lambda>'`.

## Recipe: Inspect + types for Function Specs

```python
import inspect
import types

def get_func_spec(f):
    spec = inspect.getfullargspec(f)
    return {
        'function_name': f.__name__,
        'is_lambda': isinstance(f, types.LambdaType),
        'args': spec.args,
        'defaults': spec.defaults,   # None if no defaults (not [])
        'annotations': spec.annotations,
    }
```

This mirrors the canonical pattern. The `'function_name'` key (not `'name'`) and flat
structure from `getfullargspec` (not `signature`) are essential.

## Counting Lambda Defaults

```python
import inspect
import types

spec = inspect.getfullargspec(f)
if spec.defaults:
    lambda_count = sum(1 for d in spec.defaults if isinstance(d, types.LambdaType))
else:
    lambda_count = 0
```

`spec.defaults` is `None` (not an empty tuple) when there are no defaults. Guard with
`if spec.defaults:` before iterating.

## Annotations with String Names

When serializing annotations to JSON:
```python
annotations = {
    k: v.__name__ if isinstance(v, type) else str(v)
    for k, v in spec.annotations.items()
}
# {'x': 'int', 'y': 'str', 'return': 'None'}  — not "<class 'int'>"
```

## Other Useful `types` Objects

```python
types.FunctionType         # any Python function (same as LambdaType)
types.BuiltinFunctionType  # built-in functions like len, print
types.ModuleType           # module objects
types.NoneType             # the type of None (type(None))
types.SimpleNamespace      # a simple attribute namespace
```
