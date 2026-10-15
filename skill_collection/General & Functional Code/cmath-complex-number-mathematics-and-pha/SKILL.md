---
name: cmath-complex-number-mathematics-and-pha
description: 'Guide for cmath API usage: phase computation, 2D grid patterns, imshow visualisation.'
---

# Python `cmath` Module — Complex-Number Mathematics

`cmath` provides mathematical functions that operate on Python complex numbers. Unlike `math`, every `cmath` function accepts complex input and returns complex output, so it handles negative-real arguments and imaginary-axis crossings naturally.

## Core Functions

```python
import cmath

z = complex(3, 4)          # 3 + 4j; alias for 3 + 4j literal
cmath.phase(z)             # arg(z) = atan2(im, re) ≈ 0.9273 rad, range (-π, π]
cmath.polar(z)             # (r, φ): r=5.0, φ=0.9273
cmath.rect(r, phi)         # r * exp(jφ) → complex
cmath.sqrt(z)              # principal complex square root (never raises)
cmath.log(z)               # complex natural logarithm
cmath.exp(z)               # complex exponential e^z
abs(z)                     # |z| = 5.0  (built-in, same as cmath.polar(z)[0])
```

## Phase Computation Over a 2D Grid

The standard recipe: for each lattice point `(x[j], y[i])`, form `z = complex(x[j], y[i])`, evaluate a function of z, then store `cmath.phase(f(z))` into a 2D array with shape `(len(y), len(x))`.

```python
import numpy as np
import cmath

def compute_phase_grid(xs, ys):
    if not isinstance(xs, np.ndarray) or not isinstance(ys, np.ndarray):
        raise TypeError("xs and ys must be numpy.ndarray")
    if len(xs) != len(ys):
        raise ValueError("xs and ys must have the same length")

    # Guard against empty input before np.amin/amax (raises on size-0 arrays)
    if xs.size == 0 or ys.size == 0:
        return None, np.array([])

    # Build the phase matrix row-by-row (row = y index, col = x index)
    Z = np.zeros((len(ys), len(xs)), dtype=float)
    for i in range(len(ys)):
        for j in range(len(xs)):
            z = complex(xs[j], ys[i])
            Z[i, j] = cmath.phase(z**3 + z)   # substitute the specific f(z) here

    return Z
```

Key structural points:
- Shape is `(len(y), len(x))` — rows are y, columns are x.
- The nested loop form is idiomatic; vectorising with `np.meshgrid` + `np.angle` on a 1D pair gives shape errors (`imshow` expects 2D, not 1D).
- `complex(x[j], y[i])` — real part from x, imaginary part from y.
- The task description specifies which function `f(z)` to compute the phase of; read it carefully.

## Visualising Phase Data with imshow

`ax.imshow` renders a 2D array as a color image. Pair it with the coordinate `extent` so axis ticks reflect actual values:

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
c = ax.imshow(Z,
              extent=(np.amin(xs), np.amax(xs), np.amin(ys), np.amax(ys)),
              origin='lower', cmap='hsv')
fig.colorbar(c, ax=ax, label="Phase (radians)")
ax.grid()
return ax, Z
```

`origin='lower'` places (x_min, y_min) at the bottom-left — consistent with the Cartesian convention. `cmap='hsv'` wraps smoothly at ±π, which suits phase data.

## Phase Value Reference

```
cmath.phase(1+0j)   →  0.0
cmath.phase(-1+0j)  →  π ≈ 3.14159
cmath.phase(0+1j)   →  π/2 ≈ 1.5708
cmath.phase(0-1j)   → -π/2
cmath.phase(0+0j)   →  0.0
```
