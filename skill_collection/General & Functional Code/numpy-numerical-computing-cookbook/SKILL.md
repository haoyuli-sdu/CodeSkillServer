---
name: numpy-numerical-computing-cookbook
description: 'Practical reference for numpy: array operations, random generation, aggregation, histogram bins, seeding, dtype conventions, and common numerical recipes.'
---

# numpy — Numerical Computing Cookbook

## Array Ranges and Endpoints

`np.arange(start, stop)` excludes `stop`; `np.linspace(start, stop, n)` includes `stop`.

```python
np.arange(0, 5)        # [0, 1, 2, 3, 4]  — stop excluded
np.linspace(0, 1, 5)   # [0.0, 0.25, 0.5, 0.75, 1.0]  — endpoint included
```

## Random Generation: Boundary Conventions

`np.random.randint(low, high, size)` is **exclusive** of `high` — integers in `[low, high)`.
`random.randint(a, b)` from the stdlib is **inclusive** of both ends: integers in `[a, b]`.

```python
np.random.randint(1, 101, 10)   # 10 integers in [1, 100]
random.randint(1, 100)          # integer in [1, 100] inclusive
```

Other generators: `np.random.uniform(low, high, size)` returns floats in `[low, high)`;
`np.random.normal(loc, scale, size)` draws from a Gaussian.

## Seeding: stdlib and numpy are independent

`random.seed(s)` and `np.random.seed(s)` control **separate** internal states.
`np.random.seed(None)` is valid — it seeds from `/dev/urandom` (truly random).
Call the seed directly without a None-guard:

```python
import random, numpy as np
random.seed(42)      # seeds only the stdlib random state
np.random.seed(42)   # seeds only the numpy random state — independent of above
```

When a function only uses one module's random functions, seed only that module.
When a task mixes both (e.g., `random.choice` and `np.random.randint`), seed each at its call site.

## Axis-Based Aggregations

```python
a = np.array([[1, 2], [3, 4], [5, 6]])
np.mean(a, axis=0)   # [3.0, 4.0] — column means (collapse rows)
np.mean(a, axis=1)   # [1.5, 3.5, 5.5] — row means (collapse columns)
np.sum(a, axis=1)    # [3, 7, 11]
```

`np.sum`, `np.std`, `np.min`, `np.max`, `np.median` all accept `axis`.
NaN-safe variants: `np.nanmean`, `np.nanstd`, `np.nanmin`, `np.nanmax`.

## Standard Deviation: numpy vs pandas Default

`np.std(arr)` uses **ddof=0** (population std); `pd.Series.std()` uses **ddof=1** (sample std).

```python
data = np.array([2.0, 4.0, 4.0, 6.0])
np.std(data)           # 1.4142  (ddof=0, population)
pd.Series(data).std()  # 1.6330  (ddof=1, sample)
np.std(data, ddof=1)   # 1.6330  (explicitly match pandas default)
```

When returning both mean and std alongside a DataFrame, match whichever convention the rest of the pipeline uses.

## Integer-Aligned Histogram Bins

To align bin edges with integer values, offset `np.arange` by 0.5:

```python
_, ax = plt.subplots()
bins = np.arange(min(values), max(values) + 2) - 0.5   # centers bins on integers
ax.hist(values, bins=bins, edgecolor='black')
```

This places bin boundaries at 0.5, 1.5, 2.5 ... so each integer falls in its own bin.

## Moving Elements with np.concatenate

To move the first `n` elements to the end, use slicing with `np.concatenate`:

```python
arr = np.array(some_list)    # preserves element type — strings stay strings
rotated = np.concatenate((arr[3:], arr[:3]))  # first 3 moved to end
```

`np.roll(arr, -3)` achieves the same cyclic rotation result. Both produce identical output.
The key is that `np.array(list_of_strings)` retains the original string type — no need to
convert strings to ordinal integers unless the task explicitly requires numeric output.

## Reshaping for Scikit-learn Scalers

`MinMaxScaler.fit_transform(X)` requires a 2D input and returns a 2D array. When the input
has shape `(n, 1)`, the output also has shape `(n, 1)`. Match the task's expected output shape:

```python
array = np.random.randint(0, 10, ARRAY_LENGTH).reshape(-1, 1)
scaler = MinMaxScaler()
scaled = scaler.fit_transform(array)   # shape (ARRAY_LENGTH, 1)
# If the task expects shape (ARRAY_LENGTH, 1), return scaled directly
# If the task expects a 1D array, use scaled.flatten() or scaled.ravel()
```

## Array Stats + Histogram: Common Recipe

```python
def compute_stats_and_histogram(n=1000, seed=0):
    np.random.seed(seed)
    data = np.random.randint(10, 200, size=n)
    mean = np.mean(data)
    std  = np.std(data)
    fig, ax = plt.subplots()
    ax.hist(data, bins='auto')
    ax.set_title('Histogram of Sampled Values')
    ax.set_xlabel('Value')
    ax.set_ylabel('Count')
    return data, mean, std, ax
```

## Serialising Arrays to Text

`np.array2string(arr)` converts an array to its repr string (space-separated, bracketed).
This matches the format tests typically expect when round-tripping through base64:

```python
standardized_str = np.array2string(standardized_data)
encoded = base64.b64encode(standardized_str.encode('ascii')).decode('ascii')
# Decoding: np.array2string produces "[[ 1.2 -0.5]\n [ 0.3  1.1]]"
```

Using `str(arr)` produces the same output in most cases, but `np.array2string` is more
predictable. Using `json.dumps(arr.tolist())` produces comma-separated format, which differs.

## Parsing a Comma-Separated String to Array

`np.fromstring(s, sep=",")` converts a comma-delimited string of numbers into a 1-D array:

```python
values = np.fromstring("1.5, 2.3, -0.7", sep=",")   # array([1.5, 2.3, -0.7])
```

If the string is empty, `values.size == 0`; raise `ValueError` in that case if needed.

## Differences Between Adjacent Elements

`np.diff(a)` returns length `len(a) - 1` pairwise differences:

```python
word_ascii = np.array([ord(c) for c in "hello"])
diffs = np.diff(word_ascii)   # [-3, 7, 0, 3]
```

## Boolean Selection with np.where

`np.where(condition)` returns a **tuple of index arrays**. Use `[0]` to get the 1-D index:

```python
a = np.array([1.0, 5.0, 2.0, 8.0])
indices = np.where(a > 4)[0]   # array([1, 3])
selected = a[indices]           # array([5., 8.])
```

Three-argument form: `np.where(cond, x, y)` returns `x` where True, `y` elsewhere.

## Percentiles and IQR

```python
q25, q75 = np.percentile(data, [25, 75])
iqr = q75 - q25
lower = q25 - 1.5 * iqr
upper = q75 + 1.5 * iqr
```

Call `np.percentile` only on **non-empty** arrays — an empty input raises `IndexError`.

## Scipy Integration: cumulative_trapezoid

`scipy.integrate.cumtrapz` was removed in SciPy 1.11. Use the new name:

```python
from scipy import integrate
y_int = integrate.cumulative_trapezoid(y, x, initial=0)
# same length as y; initial=0 sets the first element to zero
```

## Concatenating Arrays Conditionally

`np.concatenate` works fine with empty numpy arrays (`np.array([])`), but if the input list
itself is empty (`np.concatenate([])`), it raises an error. Guard against this when one
component might be size 0:

```python
normal_data = np.random.normal(size=num_samples)   # may be size 0 if num_samples=0
outliers    = np.random.uniform(-10, 10, size=num_outliers)
data = np.concatenate([normal_data, outliers]) if num_samples > 0 else outliers
```

## Datetime Arithmetic with np.datetime64

Subtracting two `np.datetime64` values gives a `np.timedelta64`. Convert to an int:

```python
start = np.datetime64("2021-01-01")
end   = np.datetime64("2021-12-31")
n_days = int((end - start).astype("timedelta64[D]").astype(int)) + 1
# random.sample(range(n_days), rows * cols) — picks unique day offsets
```

## Type Checking

```python
np.issubdtype(arr.dtype, np.integer)   # True for int32, int64, etc.
np.issubdtype(arr.dtype, np.floating)  # True for float32, float64
np.issubdtype(arr.dtype, np.number)    # True for any numeric dtype
```

## Common Recipe: Random Walk

```python
def make_random_walk(length=1000, seed=0):
    if length < 0:
        raise ValueError("length must be non-negative")
    random.seed(seed)
    steps = [1 if random.random() > 0.5 else -1 for _ in range(length)]
    walk = np.cumsum([0] + steps)   # starts at 0, length = length + 1
    return walk
```

Note: `[0] + steps` prepends the starting position so the walk length is `length + 1`.

## Common Recipe: Forecasting with Linear Regression

```python
def forecast_sales(sales_df, periods):
    X = np.arange(len(sales_df)).reshape(-1, 1)
    y = sales_df['Sales'].values
    model = LinearRegression().fit(X, y)
    future_X = np.arange(len(sales_df), len(sales_df) + periods).reshape(-1, 1)
    return model.predict(future_X)
```

## Common Recipe: Shuffled Columns + PCA

```python
def shuffle_cols_and_pca(array, seed=None):
    np.random.seed(seed)    # valid even when seed is None
    shuffled = np.copy(array)
    np.random.shuffle(np.transpose(shuffled))  # shuffles columns in-place via view
    n_components = min(2, shuffled.shape[1])
    pca = PCA(n_components=n_components)
    components = pca.fit_transform(shuffled)
    columns = ["PC1", "PC2"][:n_components]
    return pd.DataFrame(components, columns=columns)
```

`np.random.shuffle(arr.T)` shuffles columns of `arr` in-place because `.T` is a view.
`np.random.permutation(arr.T).T` returns a new array without modifying the original.
