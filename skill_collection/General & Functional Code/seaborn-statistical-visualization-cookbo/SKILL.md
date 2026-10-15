---
name: seaborn-statistical-visualization-cookbo
description: 'Practical guide for seaborn: return types (displot/FacetGrid, jointplot/JointGrid, pairplot/PairGrid), kdeplot colorbar, fillna+StandardScaler in-place, groupby-nunique-pivot, and plt.figure+gca patterns.'
---

# Seaborn — Statistical Visualization Cookbook

Seaborn wraps matplotlib; most functions return the `Axes` they drew into. Understanding return types and a few key patterns prevents the majority of errors.

## Return Type Quick Reference

```
sns.heatmap(...)       → Axes
sns.histplot(...)      → Axes
sns.boxplot(...)       → Axes
sns.barplot(...)       → Axes
sns.scatterplot(...)   → Axes
sns.regplot(...)       → Axes
sns.kdeplot(...)       → Axes
sns.swarmplot(...)     → Axes
sns.countplot(...)     → Axes
sns.displot(...)       → FacetGrid (access Axes via .ax)
sns.jointplot(...)     → JointGrid (NOT Axes)
sns.pairplot(...)      → PairGrid (NOT Axes)
```

`sns.displot(data, bins=10)` returns a `FacetGrid`. To collect `Axes` objects in a loop, append `plot.ax`:

```python
plots = []
for col in df.select_dtypes(include=[np.number]).columns:
    plot = sns.displot(df[col], bins=10)
    plots.append(plot.ax)
return description, plots
```

Access the underlying figure from a grid: `grid.fig`. The axes ndarray is at `grid.axes`, but callers typically want the grid object, not individual axes.

## plt.figure + sns + plt.gca() Pattern

Many canonical solutions follow this sequence — call `plt.figure()`, then a seaborn function without saving its return value, then `plt.gca()` at the end:

```python
plt.figure(figsize=(10, 5))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm")
return plt.gca()

# Same pattern with barplot:
plt.figure(figsize=(10, 5))
sns.barplot(x=list(freq.keys()), y=list(freq.values()))
return plt.gca()
```

When a task explicitly returns the Axes but the seaborn call is not assigned, use `plt.gca()` rather than the function's return value.

## fillna + StandardScaler In-Place Pattern

Replace NaN values with the column mean, then standardize — operating in-place on the whole DataFrame at once:

```python
df = df.fillna(df.mean(axis=0))          # fill all numeric NaN with column mean
scaler = StandardScaler()
df[df.columns] = scaler.fit_transform(df[df.columns])   # overwrite same DataFrame
plt.figure(figsize=(10, 5))
heatmap = sns.heatmap(df.corr(), annot=True, cmap="coolwarm")
return df, heatmap
```

Avoid separately extracting numeric columns and building a new DataFrame — replace values in the original `df` directly so that the returned object matches the input variable.

## kdeplot with Colorbar

When a KDE plot needs to include a colorbar, use `fill=True` and pass the first collection to `plt.colorbar`:

```python
np.random.seed(seed)
samples = np.random.normal(mu, sigma, 1000)
ax = sns.kdeplot(samples, fill=True)
plt.colorbar(mappable=ax.collections[0])
return ax
```

`ax.collections[0]` is the filled polygon that acts as the colormap-aware artist. Do not use `histplot` for this — it does not produce collections that `plt.colorbar` can consume.

## Dict / Array Input → Convert to DataFrame

When the input is a `dict`, `list-of-lists`, or 2D array and the function needs `.corr()`, `.drop()`, or similar DataFrame methods, construct the DataFrame first:

```python
def make_heatmap(data, drop_col="label"):
    df = pd.DataFrame(data)           # dict, list-of-lists, or 2D array
    df = df.drop(columns=[drop_col], errors="ignore")
    ax = sns.heatmap(df.corr(), annot=True, cmap="coolwarm")
    return ax
```

Import `pandas` explicitly when it is used — if the `code_prompt` does not include `import pandas as pd`, add it in the generated code before calling `pd.*`.

## groupby → nunique → pivot for Heatmaps

Count unique values of one column for each combination of two other columns, then pivot into a 2D table:

```python
COLUMNS = ["col1", "col2", "col3"]

def visualize_unique_counts(data):
    df = pd.DataFrame(data, columns=COLUMNS)
    analyzed = df.groupby(COLUMNS[:-1])[COLUMNS[-1]].nunique().reset_index()
    analyzed = analyzed.pivot(index=COLUMNS[0], columns=COLUMNS[1], values=COLUMNS[2])
    ax = sns.heatmap(analyzed, annot=True)
    plt.show()
    return analyzed, ax
```

Use `.nunique()` (count of distinct values), not `.mean()` or `.count()`. **Reassign the same variable** after pivot: `analyzed = analyzed.pivot(...)`.

## Multiple Subplots with plt.subplot

When the canonical pattern builds subplots via `plt.figure` + `plt.subplot`:

```python
fig = plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
sns.histplot(df["Score"], bins=10)
plt.title("Histogram of Scores")

plt.subplot(1, 2, 2)
sns.boxplot(x="Country", y="Score", data=df)
plt.title("Boxplot of Scores by Country")

plt.tight_layout()
return fig
```

Return `fig` (not individual axes) when the task says to return the figure. Each `plt.subplot(...)` call is positioned before its seaborn call — no `ax=` parameter needed.

## jointplot with Random Column Pairs

```python
from random import sample
COLUMNS = ["A", "B", "C", "D", "E"]

plots = []
for _ in range(n_plots):
    selected = sample(COLUMNS, 2)
    plot = sns.jointplot(data=df, x=selected[0], y=selected[1])
    plots.append(plot)
return df, plots
```

`sns.jointplot` returns a `JointGrid`. Store grids directly in the list — do not extract `.axes`.

## Heatmap: vmin/vmax for Explicit Color Range

```python
ax = sns.heatmap(
    arr,
    annot=True,
    vmin=arr.min(),
    vmax=arr.max(),
)
return ax
```

## Swarm Plot: Intersection Highlighting

```python
def compare_series(s1, s2):
    intersection = set(s1).intersection(set(s2))
    df = pd.concat([
        pd.DataFrame({s1.name: s1, "Type": "Series1"}),
        pd.DataFrame({s2.name: s2, "Type": "Series2"}),
    ], ignore_index=True)
    _, ax = plt.subplots()
    sns.swarmplot(x=df.columns[0], y="Type", data=df, ax=ax)
    for point in intersection:
        ax.axvline(x=point, color="red", linestyle="--")
    return ax, len(intersection)
```

Shared-value column → `x` axis (numeric); series-label column → `y` axis (categorical).

## Building Heatmap from Paired Arrays

```python
def heatmap_from_pairs(x_arrays, y_arrays, labels):
    rows = [np.concatenate((x, y)) for x, y in zip(x_arrays, y_arrays)]
    df = pd.DataFrame(rows, index=labels)
    ax = sns.heatmap(df, cmap="coolwarm")
    return ax, df
```
