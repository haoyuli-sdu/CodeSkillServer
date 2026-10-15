---
name: pandas-dataframe-construction-transforma
description: Practical reference covering dict/list input conversion, row-by-row construction with dynamic column names, internal constants pattern, pd.concat empty guard, plt.hist/bar return types, Counter-to-DataFrame, groupby-nunique-pivot, df.replace value mapping, scaler.fit_transform, and column shuffling.
---

# pandas — DataFrame Construction, Transformation, and Analysis

## Converting Dicts, Lists, and Arrays to DataFrames

Many functions receive a plain `dict`, a list of dicts, or a 2D array. Convert before using any DataFrame API:

```python
def analyze(data, column="value"):
    df = pd.DataFrame(data)          # required even if param is called 'df'
    numeric_cols = df.select_dtypes(include='number')
    return numeric_cols.describe()
```

Passing a plain dict to `.columns`, `.select_dtypes()`, `.drop()`, `.groupby()`, or `.empty` raises `AttributeError`.

For parallel arrays, build column-oriented:

```python
stats = {
    'Array1': [np.mean(a1), np.median(a1), np.std(a1)],
    'Array2': [np.mean(a2), np.median(a2), np.std(a2)]
}
df = pd.DataFrame(stats, index=['Mean', 'Median', 'Std'])
ax = df.plot(kind='bar')
return df, ax
```

For 2D numpy output (zscore, scaler, etc.), wrap directly:

```python
z = zscore(matrix, axis=1)
df = pd.DataFrame(z, columns=[f'F{i+1}' for i in range(z.shape[1])])
```

## Building DataFrames Row-by-Row

Accumulate rows as a list, then construct the DataFrame in a single call:

```python
rows = []
for student in students:
    grades = [random.randint(0, 100) for _ in subjects]
    avg = statistics.mean(grades)
    rows.append([student] + grades + [avg])

df = pd.DataFrame(rows, columns=['Student'] + subjects + ['Average Grade'])
return df
```

This pattern is especially important when column names come from a parameter (like `subjects`): construct `columns=['Student'] + subjects + ['Average Grade']` dynamically, not as hardcoded names.

## Constant Definitions and Internal State

When a task says "Internal Constants: COLUMNS = [...]", define those constants **inside the function body**, not outside or inline in the `pd.DataFrame()` call:

```python
def task_func(array):
    COLUMNS = ["A", "B", "C", "D", "E"]     # defined inside the function
    df = pd.DataFrame(array, columns=COLUMNS)
    sums = df.sum()
    fig, ax = plt.subplots()
    sums.plot(kind="bar", ax=ax)
    return df, ax
```

## pd.concat with a List of DataFrames

Always guard `pd.concat` against an empty list — an empty call raises `ValueError`:

```python
dfs = []
for filename in sorted(os.listdir(path)):
    if filename.endswith('.json'):
        with open(os.path.join(path, filename)) as f:
            temp = pd.DataFrame(json.load(f))
        temp['Source'] = filename
        dfs.append(temp)
        shutil.move(os.path.join(path, filename), output_dir)

result = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
return result
```

## plt.hist() and df.hist() Return Types

`plt.hist()` returns a **tuple** `(n, bins, patches)`, not an Axes:

```python
result = plt.hist(data, bins=20)       # (n, bins, patches) tuple
return df, result                      # if task expects the tuple
```

`df.hist()` and `df.plot(kind='hist')` return Axes or arrays of Axes. Use `pd.Series.plot.hist()` when `rwidth` or `grid` kwargs are needed:

```python
ax = pd.Series(data).plot.hist(bins=20, rwidth=0.8, grid=True)
```

`plt.hist()` and `ax.hist()` do **not** accept `rwidth` or `grid`.

## plt.bar() — Get Axes via plt.gca()

`plt.bar()` returns a `BarContainer`, not an Axes. Retrieve the current Axes after drawing:

```python
counts = df["Color"].value_counts()
plt.bar(counts.index, counts.values, width=0.4)
plt.xlabel("Color"); plt.ylabel("Frequency")
ax = plt.gca()
return df, ax
```

## Stacked Bar Chart — df.plot(kind='bar', stacked=True)

```python
fig, ax = plt.subplots()
data.plot(kind='bar', stacked=True, ax=ax)
return fig
```

For cross-tabulation (count rows by two categorical columns):

```python
cross = df.groupby(['Location', 'Item']).size().unstack().fillna(0)
ax = cross.plot(kind='bar', stacked=True)
```

## Axes Title — Set on the Returned Axes Object

When a function returns an `Axes`, set the title on that Axes:

```python
fig, ax = plt.subplots()
ax.pie(counts, labels=counts.index, autopct='%1.1f%%')
ax.set_title('Status Distribution')    # NOT plt.title()
return ax
```

Using `plt.title()` only sets the title on the current figure's axes, which may differ from the returned `ax` when tests inspect `ax.get_title()`.

## Counter → DataFrame

```python
from collections import Counter
counter = Counter(items)
df = pd.DataFrame.from_dict(counter, orient='index', columns=['Count'])
df.index.name = 'Item'
```

Use `pd.DataFrame(counter.items(), columns=['Item', 'Count'])` when Item is a regular column rather than the index.

When the input list may be empty, guard before constructing:

```python
flat = [x for sub in nested_list for x in sub]
if not flat:
    return None             # or pd.DataFrame(), per spec
counter = Counter(flat)
df = pd.DataFrame.from_dict(counter, orient='index', columns=['Count'])
```

## groupby with nunique() and pivot

Count distinct values per group, then pivot to a 2D grid:

```python
analyzed = df.groupby(['col1', 'col2'])['col3'].nunique().reset_index()
analyzed = analyzed.pivot(index='col1', columns='col2', values='col3')
```

Reassign to the **same variable** so the returned value is the pivoted DataFrame.

## df.replace() vs Column Key Checking

`df.replace(dct)` maps **values** to new values across all cells — the dictionary keys are data values, not column names:

```python
df = df.replace({'old_value': 'new_value', 0: np.nan})   # replaces cell values
```

Do not check whether `dct.keys()` are column names — they are not.

## scaler.fit_transform() Returns numpy Array

`StandardScaler.fit_transform()` and `MinMaxScaler.fit_transform()` return a numpy array:

```python
scaler = StandardScaler()
scaled = scaler.fit_transform(df[['age', 'income']])
df[['age', 'income']] = scaled          # assign back
return df

# Or build a new DataFrame:
df_scaled = pd.DataFrame(scaled, columns=['age', 'income'])
```

When the input is a 1D list or array, reshape first:

```python
arr = np.array(l).reshape(-1, 1)
scaled = MinMaxScaler().fit_transform(arr)
df = pd.DataFrame(scaled, columns=['Scaled Values'])
```

## select_dtypes for Numeric Columns

```python
numeric_df = df.select_dtypes(include='number')   # string form
```

## Column Shuffling — np.random.shuffle on Transposed Array

```python
if seed is not None:
    np.random.seed(seed)
shuffled = feature_array.copy()
np.random.shuffle(shuffled.T)          # shuffles columns in-place
df = pd.DataFrame(shuffled, columns=feature_names)
df[target_name] = target_array
```

`np.random.shuffle()` permutes in-place and consumes random state. Using `random.sample()` on a list also shuffles but consumes state differently — use whichever approach the task implies.

## Clustering — Fit on the DataFrame Directly

```python
df = pd.DataFrame(data, columns=cols)
dbscan = DBSCAN(eps=3, min_samples=2)
df['Cluster'] = dbscan.fit_predict(df)
return df
```

When the task specifies exact parameter values, use those values on the raw data — preprocessing changes scale and cluster boundaries.

## Time Series: resample()

```python
df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date')
daily = df.resample('D').sum()
ax = daily.plot(y='Sales')
```

## String Replacement in a Column

```python
df['col'] = df['col'].str.replace('\n', '<br>', regex=False)
```

Note: `pd.Series.str` methods do not work on Python lists. Convert to DataFrame first.

## pd.read_sql_query — SQLite Context Manager

```python
with sqlite3.connect(db_path) as conn:
    df = pd.read_sql_query("SELECT * FROM table_name", conn)
df[column_name] = df[column_name].str.replace('\n', '<br>')
return df
```

## Default None Parameters — Supply Defaults Inside

```python
def task_func(categories=None, months=None, seed=42):
    if categories is None:
        categories = ['Electronics', 'Clothing', 'Home & Kitchen']
    if months is None:
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
```

## Deprecated API

`DataFrame.iteritems()` was removed in pandas 2.0. Use `DataFrame.items()`.

## JSON and CSV Output

Use `json.dump(original_data, f)` to preserve the original list/dict structure. `df.to_json()` serializes the DataFrame structure (column-oriented by default):

```python
df = pd.DataFrame(result)
df.to_csv(csv_path, index=False)

with open(json_path, 'w') as f:
    json.dump(result, f, indent=4)     # preserves list-of-dicts format
```
