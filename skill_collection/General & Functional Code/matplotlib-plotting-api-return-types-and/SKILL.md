---
name: matplotlib-plotting-api-return-types-and
description: 'Guide for correct matplotlib API usage: return type contracts, OOP vs state-machine style, histogram rwidth, bar chart positioning, imshow interpolation, KDE colorbar, and common pitfalls.'
---

# matplotlib — Plotting API, Return Types, and Composition Recipes

## Return Type Quick Reference

The most common failure is returning more (or fewer) values than the task requires:

| Expression | Actual return type |
|---|---|
| `fig, ax = plt.subplots()` → `return ax` | `Axes` |
| `plt.figure()` → `return plt.gca()` | `Axes` |
| `plt.bar(labels, vals)` → `plt.gca()` | `Axes` (BarContainer is NOT Axes) |
| `plt.hist(data)` | `(n, bins, patches)` tuple — NOT Axes |
| `ax.hist(data)` | `(n, bins, patches)` tuple — NOT Axes |
| `df.hist()` | 2-D ndarray of Axes |
| `df.plot()` / `series.plot()` | `Axes` |
| `df.boxplot()` | NOT Axes — use `plt.gca()` after |
| `sns.kdeplot(data, fill=True)` | `Axes` (accessible as `mappable` for colorbar) |
| `sns.histplot(data)` | `Axes` |
| `ax.pie(...)` | `(wedges, texts)` or `(wedges, texts, autotexts)` — NOT Axes |

When the task says "return a DataFrame", `return df` — not `(df, ax)`.
When the task says "return (DataFrame, Axes)", `return df, ax`.

## Core Idioms

**OOP style** — use when returning an Axes or embedding into subplots:
```python
fig, ax = plt.subplots()
ax.plot(x, y, label="series")
ax.set_title("Monthly Readings")
ax.set_xlabel("Month")
ax.set_ylabel("Value")
ax.legend()
return ax
```

**State-machine style** — use when the function naturally calls `plt.plot()` and shows/saves the result:
```python
plt.figure()
plt.plot(x, y)
plt.title("Monthly Readings")
plt.xlabel("Month")
plt.ylabel("Value")
plt.show()
```

`plt.subplots()` and `plt.figure()` are not interchangeable — follow the style implied by the task's code prompt.

## Histograms and the rwidth Parameter

`ax.hist()` accepts `rwidth` (relative bar width, 0.0–1.0) directly:

```python
fig, ax = plt.subplots()
# bins aligned to integers: np.arange(max_val + 2) - 0.5 centers each bin on an integer
bins = np.arange(max(data) + 2) - 0.5 if data else []
ax.hist(data, bins=bins, rwidth=0.8)
ax.set_title("Distribution")
ax.set_xlabel("Value")
ax.set_ylabel("Frequency")
return ax
```

`rwidth` is an `ax.hist()` parameter — do not substitute `ax.bar()` to apply it.

## Bar Charts with Numeric Positions

When using integer positions for string-labeled bars:
```python
indexes = np.arange(len(labels))
ax.bar(indexes, values, color=color)
ax.set_xticks(indexes)          # must set positions first
ax.set_xticklabels(labels)      # then attach label strings
ax.set_xlabel("Category")
ax.set_ylabel("Count")
```

Omitting `set_xticks` before `set_xticklabels` raises a `ValueError` in recent matplotlib.

## Color Format Strings

Short color strings are the most portable when color identity matters:
```python
ax.plot(y, "b")          # get_color() → 'b'
ax.plot(y, "r--")        # get_color() → 'r'
ax.plot(y, color="blue") # get_color() → RGBA tuple, not 'b'
```

Cycling through a color list using the color as the second positional argument:
```python
from itertools import cycle
for col, c in zip(df.columns, cycle(COLORS)):
    ax.plot(df[col], c)
```

## imshow for Matrix Visualization

```python
fig, ax = plt.subplots()
ax.imshow(matrix, cmap="hot", interpolation="nearest")
return ax
```

Valid `interpolation=` values: `'nearest'`, `'bilinear'`, `'bicubic'`, `'antialiased'`, `'lanczos'`, `'gaussian'`, `'none'`. Use `'nearest'` for crisp discrete grids.

## Multiple Subplots

```python
fig, axes = plt.subplots(1, 2, figsize=(12, 6))
sns.histplot(df["score"], ax=axes[0])
axes[0].set_title("Histogram")
sns.boxplot(x="group", y="score", data=df, ax=axes[1])
axes[1].set_title("Box Plot")
plt.tight_layout()
return axes[0], axes[1]
```

`plt.subplots(1, n)` with n > 1 returns a 1-D ndarray of Axes — index into it before calling `.set_title()`.

Per-column histograms returned as a list:
```python
axes_list = []
for col in numeric_cols:
    fig, ax = plt.subplots()
    ax.hist(df[col])
    ax.set_title(col)
    ax.set_xlabel("Value")
    ax.set_ylabel("Frequency")
    axes_list.append(ax)
return axes_list
```

## Histogram with Fitted Normal Curve

```python
from scipy import stats
fig, ax = plt.subplots()
ax.hist(data, bins="auto", density=True, alpha=0.6)
mu, std = stats.norm.fit(data)
xmin, xmax = ax.get_xlim()
x = np.linspace(xmin, xmax, 200)
ax.plot(x, stats.norm.pdf(x, mu, std), linewidth=2)
ax.set_title(f"μ={mu:.2f}, σ={std:.2f}")
return ax
```

`stats.norm.fit(data)` takes a single array — do not pass separate mu/sigma as positional arguments.

## KDE Plot and Colorbar

`sns.kdeplot()` returns the Axes object. When adding a colorbar referencing the KDE fill:
```python
ax = sns.kdeplot(samples, fill=True)
plt.colorbar(mappable=ax.collections[0])
return ax
```

## FFT Visualization

`scipy.fftpack.fft()` returns complex numbers — plot magnitudes:
```python
fft_vals = fftpack.fft(signal)
ax.plot(np.abs(fft_vals))
ax.set_title("FFT Magnitude Spectrum")
```

## plt.show() and plt.savefig()

Save before displaying:
```python
if save_path:
    plt.savefig(save_path)
plt.show()
```

## Pie Charts

`ax.pie()` returns a tuple, not an Axes. Build via `fig, ax = plt.subplots()` and return `ax`:
```python
fig, ax = plt.subplots()
counts = df["category"].value_counts()
ax.pie(counts, labels=counts.index, autopct="%1.1f%%")
ax.set_title("Category Distribution")
return ax
```

## DataFrame Plot Helpers

```python
# df.plot() returns Axes
ax = df.set_index("Date").plot(kind="line")

# df.boxplot() does NOT return Axes — retrieve via plt.gca()
df.boxplot(column="score", by="group")
ax = plt.gca()
return ax
```

## fill_between for Confidence Bands

```python
fig, ax = plt.subplots()
for col in df.columns:
    std = df[col].std()
    ax.plot(x, df[col], label=col)
    ax.fill_between(x, df[col] - std, df[col] + std, alpha=0.2)
ax.legend()
return ax
```
