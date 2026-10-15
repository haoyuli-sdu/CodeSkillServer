---
name: sympy-symbolic-mathematics-and-numeric-c
description: 'Guide for sympy API: equation solving, symbolic-to-Python conversion, isprime, and random coefficients.'
---

# Python `sympy` Module — Symbolic Mathematics

sympy performs symbolic algebra: exact arithmetic, symbolic differentiation, equation solving, and number-theory functions. Results are sympy expression objects, not Python floats — conversion is a separate step.

## Solving Polynomial Equations

```python
from sympy import symbols, solve

x = symbols('x')

roots = solve(x**2 - 5*x + 6, x)     # [2, 3]  — list of sympy expressions
roots = solve(x**2 + 1, x)            # [-I, I]  — complex; I is sympy's imaginary unit
roots = solve(x**2 + x + 1, x)        # complex solutions when discriminant < 0
```

`solve()` returns a **list** of sympy expressions. For a degree-n polynomial, the list has n entries (counting multiplicity). Solutions may be real or complex sympy objects.

## Converting Symbolic Solutions to Python Complex

Python's built-in `round()` does not work on sympy or complex objects — it raises `TypeError`. The correct pattern is: cast to Python `complex`, then round the real and imaginary parts separately as floats:

```python
from sympy import symbols, solve
import numpy as np

def quadratic_roots(a, b, c, precision=2):
    x = symbols('x')
    solutions = solve(a*x**2 + b*x + c, x)
    result = [
        complex(
            round(complex(sol).real, precision),
            round(complex(sol).imag, precision)
        )
        for sol in solutions
    ]
    return tuple(result)
```

This works for both real roots (imaginary part rounds to 0.0) and complex-conjugate root pairs.

## Generating Random Coefficients

When computing with symbolic equations that have randomly sampled coefficients:
- `np.random.uniform(-10, 10)` — continuous float draw
- `np.random.randint(-10, 11)` — integer draw (NOTE: uniform and randint consume the same RNG sequence differently, so the seed produces different coefficient sets)

If the task says "random numbers between -10 and 10" without specifying integers, use `np.random.uniform` — this matches the canonical implementation pattern and the expected numerical output.

## Number Theory Functions

```python
from sympy import isprime, nextprime, factorint

isprime(17)          # True
isprime(4)           # False
nextprime(10)        # 11
factorint(12)        # {2: 2, 3: 1}

# Filtering primes from a list
primes = [n for n in numbers if isprime(n)]
```

## Symbolic Conversion Quick Reference

```
complex(sol)                         → Python complex  (works for real and complex)
float(sol)                           → Python float    (raises if imaginary part nonzero)
complex(sol).real                    → real part as float
complex(sol).imag                    → imaginary part as float
round(complex(sol).real, n)          → correctly rounded float
```

## Expression Manipulation

```python
from sympy import factor, expand, simplify, sqrt, pi

expr = x**2 + 2*x + 1
factor(expr)              # (x + 1)**2
expand((x + 1)**2)        # x**2 + 2*x + 1
simplify(expr)            # simplified canonical form

sqrt(2)                   # sympy expression sqrt(2)
float(sqrt(2))            # 1.4142135623730951
```
