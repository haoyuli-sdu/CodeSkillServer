---
name: random-core-api-and-common-patterns
description: Reference for random.choice/choices/sample/shuffle, seeding, integer generation, and common generation patterns.
---

# Python `random` Module — Practical Reference

## Core Selection Functions

### `random.choice(seq)` — Single element from a sequence

Returns one item per call. Each call advances the RNG state independently.

```python
import random
color = random.choice(['red', 'green', 'blue'])
```

### `random.choices(population, k=n)` — Batch draw with replacement

Returns a **list** of `k` elements in a single call. Produces a different RNG state trajectory than calling `random.choice` `k` times in a loop — given the same seed, the two approaches yield different outputs. Use `choices` when the task generates a sequence of characters, tokens, or items in one shot:

```python
# Generating a random string of fixed length
label = ''.join(random.choices(string.ascii_letters, k=8))

# Generating a list of n random items
sample = random.choices(CATEGORIES, k=n)
```

### `random.sample(population, k)` — Draw without replacement

```python
hand = random.sample(deck, 5)   # 5 unique cards, no repeats
```

Use `sample` when uniqueness is required; `choices` when repeats are allowed.

## Integer and Float Generation

- `random.randint(a, b)` — integer N where `a <= N <= b` (both endpoints **inclusive**)
- `random.randrange(a, b)` — integer N where `a <= N < b` (upper end **exclusive**)
- `random.uniform(a, b)` — float in `[a, b]`
- `random.random()` — float in `[0.0, 1.0)`
- `random.gauss(mu, sigma)` — Gaussian float

```python
x = random.randint(0, 10)    # can return 10
y = random.randrange(0, 10)  # never returns 10
```

To select uniformly from a sequence by index, prefer `random.choice(seq)` over
`seq[random.randint(0, len(seq) - 1)]` — both are equivalent, but `choice` is cleaner.

## `random.shuffle(seq)`

Shuffles **in place**, returns `None`:

```python
items = [1, 2, 3, 4, 5]
random.shuffle(items)   # items is now shuffled; return value is None
```

## Seeding

`random.seed(n)` controls only Python's `random` module. When a function also uses NumPy's RNG, seed both:

```python
random.seed(seed)
np.random.seed(seed)   # independent — must be seeded separately
```

Conditional seeding with an optional parameter:

```python
if seed is not None:
    random.seed(seed)
```

When the function signature does not include a seed parameter, do not add a hardcoded `random.seed(42)` — that alters the RNG sequence and breaks any downstream seeded behavior.

## Float Formatting

To format a float with two decimal places and a comma as the thousands separator, use an f-string with the `,` format specifier:

```python
value = 9876.543
formatted = f"{value:,.2f}"   # '9,876.54'
```

This is the standard Python idiom for locale-style number formatting in string output.

## Dict with Integer Counts — Iteration Pattern

When a dict maps keys to integer counts and each count represents how many items to generate, wrap the count in `range()`:

```python
results = []
for dept_code, num_employees in dept_counts.items():
    for _ in range(num_employees):          # num_employees is an int, not iterable
        tag = ''.join(random.choices(string.ascii_uppercase, k=5))
        results.append(f'{dept_code}{tag}')
```

`for _ in num_employees` raises `TypeError: 'int' object is not iterable`. Always wrap with `range()`.

## File Cursor Reset

To seek a file's cursor back to the start, call `file.seek(0)` **inside** the `with` block while the file object is still open:

```python
with open(path, 'w') as f:
    f.write(content)
    f.seek(0)    # rewind while file is open
# File is closed here — seek after this point raises ValueError
```

## Common Patterns

### Per-row data generation

```python
rows = []
for item in item_list:
    category = random.choice(CATEGORIES)
    value = random.randint(min_val, max_val)
    rows.append([item, category, value])
df = pd.DataFrame(rows, columns=['Item', 'Category', 'Value'])
```

### Generating strings and formatted values in a DataFrame

```python
data = {
    'Label': [''.join(random.choices(string.ascii_letters, k=10))
               for _ in range(N)],
    'Amount': [f"{x:,.2f}" for x in np.random.uniform(0, 10000, N)],
}
df = pd.DataFrame(data)
```

### Conditional sampling from a matched subset

```python
matches = df[df[col].str.contains(pattern, na=False)]
if sample_size is not None:
    random.seed(seed)
    sample_size = min(sample_size, len(matches))
    indices = random.sample(range(len(matches)), sample_size)
    matches = matches.iloc[indices]
return matches
```
