---
name: inspect-function-introspection-recipes
description: 'Practical guide for inspect.getfullargspec: return types, lambda detection patterns (report vs reject), DataFrame export, and plt.show() pairing.'
---

# Python `inspect` Module — Function Introspection Recipes

## Core API: `inspect.getfullargspec`

The standard introspection tool is `inspect.getfullargspec(f)`, returning a `FullArgSpec`
namedtuple. Prefer it over `inspect.signature()` — the field names differ and tests
typically expect the `getfullargspec` structure.

```
FullArgSpec fields:
  .args           list of positional param names (['x', 'y'])
  .defaults       tuple of trailing defaults, or None (not [])
  .annotations    dict of name → type object, may include 'return' key
  .varargs        name of *args param, or None
  .varkw          name of **kwargs param, or None
  .kwonlyargs     list of keyword-only param names
  .kwonlydefaults dict of keyword-only defaults, or None
```

`.defaults` is `None` — not an empty tuple — when no defaults exist.
Guard before iterating: `if spec.defaults:`.

## Recipe: Return a Function Specification Dict

```python
import inspect
import types

def describe_function(f):
    spec = inspect.getfullargspec(f)
    return {
        'function_name': f.__name__,
        'is_lambda': isinstance(f, types.LambdaType),
        'args': spec.args,
        'defaults': spec.defaults,       # None or tuple — never []
        'annotations': spec.annotations, # raw dict with type objects as values
    }
```

`spec.annotations` maps parameter names to type objects: `{'x': int, 'return': str}`.
Return it directly when the task asks for an annotations dict. Serialize to strings only
when the task explicitly requires it (e.g., for JSON output).

## Annotations: String Conversion for Serialization

When the output must be a string-formatted annotation dict (for JSON serialization):

```python
annotations = {
    k: v.__name__ if isinstance(v, type) else str(v)
    for k, v in spec.annotations.items()
}
# {'x': 'int', 'return': 'str'}  — clean names, not "<class 'int'>"
```

## Lambda Detection: Two Distinct Contexts

**Context A — Report whether a function is a lambda** (set an `is_lambda` field, process all functions including lambdas):

```python
# Both lambdas and named functions pass through; set the flag
spec = inspect.getfullargspec(f)
row = {
    'function_name': f.__name__,
    'is_lambda': isinstance(f, types.LambdaType),
    'args': spec.args,
}
```

**Context B — Raise ValueError when a lambda is passed** (filter out lambdas at validation):

```python
for f in func_list:
    if f.__name__ == '<lambda>':
        raise ValueError("Lambda functions are not allowed.")
```

Use `f.__name__ == '<lambda>'` for reliable detection in both cases. `isinstance(f, types.LambdaType)` also works for the flag (returns `True` for lambdas), but note that `types.LambdaType` is an alias for `types.FunctionType` — it returns `True` for all Python functions, not just lambdas.

## Recipe: Analyze a List of Functions into a DataFrame + Plot

```python
import inspect
import pandas as pd
import matplotlib.pyplot as plt

def analyze_functions(func_list):
    rows = []
    for f in func_list:
        if f.__name__ == '<lambda>':
            raise ValueError("Lambda functions are not allowed.")
        spec = inspect.getfullargspec(f)
        rows.append([f.__name__, len(spec.args)])

    df = pd.DataFrame(rows, columns=['Function Name', 'Number of Arguments'])
    df.set_index('Function Name', inplace=True)
    df.plot(kind='bar')
    plt.show()
    return df
```

When a task says "draw a bar chart" using `df.plot(kind='bar')`, always follow it with
`plt.show()` — both calls are expected by the caller.

## Recipe: Export Function Specs to CSV

```python
import inspect
import pandas as pd

def export_func_specs(func_list, file_path):
    if not all(callable(f) for f in func_list):
        raise ValueError("All elements must be callable functions.")
    if not func_list:
        raise ValueError("func_list must not be empty.")
    if not isinstance(file_path, str):
        raise ValueError("file_path must be a string.")

    rows = []
    for f in func_list:
        spec = inspect.getfullargspec(f)
        rows.append([
            f.__name__,
            len(spec.args),
            spec.defaults,
            spec.annotations,
            f.__name__ == '<lambda>',    # Is Lambda: True for lambdas, False otherwise
        ])

    df = pd.DataFrame(rows, columns=[
        'Function Name', 'Number of Arguments', 'Defaults', 'Annotations', 'Is Lambda'
    ])
    try:
        df.to_csv(file_path, index=False)
    except IOError as e:
        raise IOError(f"Error writing to file: {e}")
```

Lambda functions should be **included** in the CSV (with `Is Lambda=True`) unless the
task explicitly says to raise an error when a lambda is encountered.

## Counting Lambdas in Default Values

```python
import inspect
import types

spec = inspect.getfullargspec(f)
if spec.defaults:
    lambda_count = sum(1 for d in spec.defaults if isinstance(d, types.LambdaType))
else:
    lambda_count = 0
```

Always guard with `if spec.defaults:` — `spec.defaults` is `None` when no defaults exist.
