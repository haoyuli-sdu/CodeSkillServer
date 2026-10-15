---
name: turtle-turtle-graphics-drawing
description: 'turtle patterns: Screen+Turtle setup, window.mainloop() (not turtle.done()), square drawing with right(90), speed values, fill, and pen control.'
---

# turtle — Turtle Graphics Drawing

## Screen and Turtle Setup

The standard initialization pattern uses `turtle.Screen()` and `turtle.Turtle()`. Call `window.mainloop()` — not `turtle.done()` or `turtle.mainloop()` — to keep the window open:

```python
import turtle
import time
from random import choice

def draw_shapes(colors):
    window = turtle.Screen()
    window.bgcolor('white')

    t = turtle.Turtle()
    t.speed(1)

    for _ in range(5):
        t.color(choice(colors))
        for _ in range(4):
            t.forward(100)
            t.right(90)
        time.sleep(1)

    window.mainloop()
```

Key points:
- `window = turtle.Screen()` — use the Screen instance, not the module-level functions
- `window.mainloop()` on the `Screen` instance — not `turtle.mainloop()` or `turtle.done()`
- Drawing squares uses `t.right(90)` (or `t.left(90)`) without `begin_fill`/`end_fill` unless fill is specifically required

## Speed Values

| Value | Meaning |
|---|---|
| 0 | Instant (no animation) |
| 1 | Slowest |
| 6 | Normal |
| 10 | Fast |

## Colors and Fill

```python
t.color("red")            # pen and fill color
t.color("blue", "gold")   # pen color, fill color separately

t.begin_fill()
for _ in range(4):
    t.forward(100)
    t.right(90)
t.end_fill()
```

## Pen Control

```python
t.penup()      # lift pen — no drawing while moving
t.pendown()    # lower pen — draw while moving
t.goto(x, y)  # move to absolute position
t.hideturtle()
```
