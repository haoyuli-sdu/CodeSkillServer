---
name: mpl-toolkits-3d-plotting-with-matplotlib
description: Axes3D creation, 3D color histogram using cv2.calcHist (not np.histogram3d), common 3D plot types, and event connection.
---

# mpl_toolkits — 3D Plotting with Matplotlib

## Creating a 3D Axes Object

```python
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = Axes3D(fig)          # returns a 3D Axes attached to fig
# equivalently: ax = fig.add_subplot(111, projection='3d')
```

`Axes3D` is a subclass of `matplotlib.axes.Axes`, so it passes `isinstance(ax, Axes)` checks.

## 3D Color Histogram of an Image

Plot per-channel histograms using `cv2.calcHist` — **`np.histogram3d` does not exist**. Plot each channel as a line in 3D space:

```python
import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def plot_color_hist_3d(file_path, on_pick):
    import os
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No file found at {file_path}")

    img = cv2.imread(file_path)
    fig = plt.figure()
    ax = Axes3D(fig)

    for i, col in enumerate(('b', 'g', 'r')):
        hist = cv2.calcHist([img], [i], None, [256], [0, 256])  # shape (256, 1)
        ax.plot(np.arange(256), hist, color=col)

    fig.canvas.mpl_connect('pick_event', on_pick)
    return ax
```

`cv2.calcHist([img], [channel_idx], mask, [bins], [range])` — all arguments except mask are lists.

## Common 3D Plot Types

```python
ax.scatter(xs, ys, zs)                 # 3D scatter
ax.plot(xs, ys, zs)                    # 3D line
ax.plot_surface(X, Y, Z)               # surface (needs meshgrid)
ax.bar3d(x, y, z, dx, dy, dz)         # 3D bar chart

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
```

## Event Connection

```python
fig.canvas.mpl_connect('pick_event', callback_func)
fig.canvas.mpl_connect('button_press_event', on_click)
```
