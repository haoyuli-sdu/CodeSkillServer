---
name: scipy-scientific-computing-statistics-op
description: 'Practical reference for scipy API: stats.mode version handling, entropy as unnormalized weights, norm.fit usage, histogram bin counts, chi2_contingency defaults, curve_fit patterns, and cumulative_trapezoid.'
---

# scipy — Scientific Computing: Statistics, Optimization, Signal Processing

## scipy.stats.mode — Version-Dependent Return Type

`stats.mode()` behavior changed across versions:

- **scipy < 1.11**: `.mode` returns a 1-D array `array([x])`, so `result.mode[0]` or `result[0][0]` gives the scalar value.
- **scipy ≥ 1.11**: `.mode` returns a scalar when `keepdims=False` (the new default). Subscripting a scalar with `[0]` raises `IndexError`.

```python
from scipy.stats import mode
import numpy as np

arr = np.array([1, 2, 2, 3, 3, 3])

# Always-safe: use keepdims=True for array-style access
scalar_mode = mode(arr, keepdims=True).mode[0]   # works on all versions

# Modern scipy (≥ 1.11): scalar directly
scalar_mode = mode(arr).mode    # scalar, no [0] subscript needed
scalar_mode = mode(arr)[0]      # equivalent via namedtuple indexing

# Return the FULL ModeResult when the task requires .mode and .count attributes:
result = mode(arr)   # ModeResult(mode=3, count=3) — return this whole object

# Flatten inhomogeneous nested lists before calling mode:
nested = [[1, 2], [3], [1, 2, 3]]
flat = np.hstack(nested)   # use np.hstack, NOT np.array(nested) which raises ValueError
scalar_mode = mode(flat, keepdims=True).mode[0]
```

## scipy.stats.entropy — Raw Array as Unnormalized Weights

`entropy()` treats its input directly as **unnormalized frequency weights** — it divides each value by the sum and applies the log formula. The key consequence: passing raw difference arrays or count arrays produces correct results; pre-computing probabilities first gives a different (wrong) answer.

```python
from scipy.stats import entropy

# Five identical differences → entropy of a uniform distribution over 5 outcomes
diffs = np.array([1, 1, 1, 1, 1])
h = entropy(diffs)        # ln(5) ≈ 1.6094  — correct
# NOT: probs = diffs / diffs.sum(); entropy(probs) — same result here but wrong approach

# Entropy of a difference array (values treated as weights directly):
ascii_diffs = np.array([3, -1, 4, 1])   # can include negatives
h = entropy(ascii_diffs)  # may be -inf if weights don't form a valid distribution

# Two-distribution KL divergence:
h = entropy(pk, qk=qk, base=2)   # bits
```

Pass the raw array directly. If any element is zero or negative, `entropy` returns `0.0` or `-inf` — these are mathematically correct results, not errors.

## Histogram + Normal PDF Overlay — Canonical Pattern

```python
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

def plot_hist_with_fit(data, bins_spec='auto'):
    # Use np.histogram_bin_edges when the exact bin count matters:
    bin_edges = np.histogram_bin_edges(data, bins=bins_spec)
    n_bins = len(bin_edges) - 1

    fig, ax = plt.subplots()
    ax.hist(data, bins=n_bins, density=True, alpha=0.6, color='g')

    mu, std = norm.fit(data)   # norm.fit takes ONE positional arg: the raw sample data
    xmin, xmax = ax.get_xlim()
    x = np.linspace(xmin, xmax, 100)
    ax.plot(x, norm.pdf(x, mu, std), 'k', linewidth=2)
    return fig
```

`norm.fit(data)` takes **one positional argument** — the array of raw sample measurements. It returns `(mu, std)`. When `mu`/`std` are provided by the task, use them directly: `norm.pdf(x, mu, std)` — do not re-fit.

Guard for constant data before fitting:

```python
if df["value"].nunique() <= 1:
    mu, std = None, None
else:
    mu, std = norm.fit(df["value"])

fig, ax = plt.subplots()
ax.hist(df["value"], bins=bins, density=True, alpha=0.6, color="g")
if mu is not None:
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    ax.plot(x, norm.pdf(x, mu, std), "k", linewidth=2)
```

## scipy.stats.gaussian_kde — Callable Estimator

`gaussian_kde` returns a callable object, not an array.

```python
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt

sample = np.random.normal(0, 1, 300)
density = stats.gaussian_kde(sample)

x = np.linspace(sample.min(), sample.max(), 200)
fig, ax = plt.subplots()
ax.plot(x, density(x))    # evaluate the callable on x to get density values
```

KDE fails on constant data (singular covariance). Check `np.var(data) != 0` beforehand.

## scipy.integrate — Updated Function Names

`cumtrapz` and `trapz` were removed in SciPy 1.14. Use:

```python
from scipy.integrate import cumulative_trapezoid, trapezoid

y_int = cumulative_trapezoid(y, x, initial=0)   # cumulative, length = len(y)
area  = trapezoid(y, x)                          # scalar total area
```

## scipy.optimize.curve_fit — Function Signature Determines Parameters

```python
from scipy.optimize import curve_fit
import numpy as np

x = np.array([0., 1., 2., 3., 4.])
y = np.array([5.0, 2.5, 1.2, 0.6, 0.3])

def exp_decay(x, a, b, c):
    return a * np.exp(-b * x) + c

popt, _ = curve_fit(exp_decay, x, y, p0=[1, 0.1, 0])
# popt = [a, b, c]; use func(x, *popt) to evaluate

# Two-parameter sine fit:
def sine_wave(x, a, b):
    return a * np.sin(b * x)

popt, _ = curve_fit(sine_wave, x_data, y_data, p0=[1, 1])
```

Label format for fitted lines: `'fit: a=%5.3f, b=%5.3f' % tuple(popt)`.

## scipy.stats.chi2_contingency — Contingency Table Test

```python
from scipy.stats import chi2_contingency
import pandas as pd

contingency_table = pd.crosstab(df[col1], df[col2])
chi2, p, dof, expected = chi2_contingency(contingency_table)
return p
```

`chi2_contingency` applies Yates' correction automatically for 2×2 tables. Do not pass `correction=False` unless the task explicitly requires it — doing so changes the p-value.

## scipy.stats.linregress — Returns 5-Tuple

```python
from scipy.stats import linregress

slope, intercept, r_value, p_value, std_err = linregress(x, y)
# fitted line: intercept + slope * x_new
```

## scipy.spatial.distance — Numeric dtype Required

```python
from scipy.spatial.distance import pdist, squareform
import numpy as np

dist_matrix = squareform(pdist(matrix.astype(float)))   # convert to float first
```

## scipy.stats.zscore — DataFrame Column Normalization

```python
from scipy import stats
import pandas as pd

df = pd.DataFrame([[1, 2], [3, 4], [5, 6]])
df_normalized = df.apply(stats.zscore).fillna(0.0)  # constant columns → NaN → 0

# 2D array with axis parameter:
z = stats.zscore(matrix, axis=1)   # row-wise; returns ndarray
```

## Common scipy.stats Functions — Quick Reference

| Function | Returns | Notes |
|---|---|---|
| `stats.norm.fit(data)` | `(mu, std)` | fits parameters from raw sample data |
| `stats.norm.pdf(x, mu, std)` | array | density values at x |
| `stats.norm.rvs(loc, scale, size)` | ndarray | random samples |
| `stats.mode(arr)` | `ModeResult` | `.mode` = scalar (1.11+); use `keepdims=True` for array |
| `stats.entropy(arr)` | float | treats arr as unnormalized weights |
| `stats.zscore(arr)` | ndarray | column-wise; NaN for constant columns |
| `stats.skew(arr)` | float | Fisher's skewness |
| `stats.kurtosis(arr)` | float | Fisher's kurtosis (0 = normal) |
| `stats.normaltest(arr)` | `(stat, p_value)` | needs ≥ 20 samples |
| `stats.ttest_1samp(arr, popmean)` | `(stat, p_value)` | one-sample t-test |
| `stats.ttest_ind(a, b)` | `(stat, p_value)` | two-sample t-test |
| `stats.pearsonr(x, y)` | `(r, p_value)` | Pearson correlation |
| `stats.chi2_contingency(table)` | `(chi2, p, dof, expected)` | use `pd.crosstab()` to build table |
| `stats.probplot(data, plot=ax)` | `((osm, osr), (slope, intercept, r))` | Q-Q plot drawn on ax |
| `stats.boxcox(x)` | `(transformed, lambda)` | requires strictly positive values |
| `stats.iqr(arr)` | float | interquartile range |
| `stats.poisson(mu).rvs()` | int | single Poisson sample |
| `stats.gaussian_kde(data)` | callable | evaluate on x array: `kde(x)` |
| `np.histogram_bin_edges(data, bins='auto')` | array | use `len(edges)-1` for bin count |
