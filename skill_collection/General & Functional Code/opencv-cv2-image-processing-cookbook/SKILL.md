---
name: opencv-cv2-image-processing-cookbook
description: 'Core patterns for cv2: reading/converting images, blur, contours, histograms, KMeans segmentation, and seeded pixel generation.'
---

# OpenCV (cv2) — Image Processing Cookbook

## Reading Images

`cv2.imread()` always returns a BGR array. It returns `None` (not an exception) when the file is missing. Raise `FileNotFoundError` with `os.path.exists()` before reading, then check for `None` afterward:

```python
import os, cv2

if not os.path.exists(image_path):
    raise FileNotFoundError(f"No file found at {image_path}")
img = cv2.imread(image_path)                          # BGR, shape (H, W, 3)
img_gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # shape (H, W)
```

## Color Conversion

```python
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)   # BGR → grayscale
rgb  = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)    # BGR → RGB (for matplotlib)
gray = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2GRAY)  # PIL/RGB → grayscale
```

## Blur Filters

`cv2.blur()` applies a simple box filter. The second argument is a `(width, height)` tuple — not a single integer:

```python
blurred = cv2.blur(img, (kernel_size, kernel_size))
```

`cv2.GaussianBlur` and `cv2.blur` are different functions — prefer the one matching the task description exactly.

## Finding Contours

```python
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
contours, _ = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
```

`findContours` returns a 2-tuple `(contours, hierarchy)` — always unpack both.

## Pixel Histograms

`cv2.calcHist` wraps its arguments in lists and returns a 2D array of shape `(bins, 1)`:

```python
hist = cv2.calcHist([img], [0], None, [256], [0, 256])   # shape (256, 1)
```

For a plain 1D histogram array, use numpy:
```python
histogram, _ = np.histogram(img.ravel(), bins=256, range=[0, 256])
```

To get an Axes object from `plt.plot(hist)`, access `.axes` on the returned Line2D:
```python
axes = plt.plot(hist)[0].axes
```

## K-Means Segmentation — Keep Arrays as uint8

All arrays passed to `cv2.imwrite` must be `uint8`. After KMeans assigns cluster centers, cast back:

```python
pixels = img.reshape(-1, 3)                              # float is OK for KMeans input
kmeans = KMeans(n_clusters=n, random_state=seed)
kmeans.fit(pixels)
segmented = kmeans.cluster_centers_[kmeans.labels_]
segmented = segmented.reshape(img.shape).astype('uint8') # must cast before imwrite
```

Passing float64 arrays to cv2 functions raises `CV_64F` depth errors.

## Seeded Pixel Generation with `random.randint`

When pixel values must be filled with `random.randint` (the stdlib function, inclusive on both ends), the canonical approach uses a nested loop — **not** `np.random.randint` — because the two functions consume the RNG differently:

```python
import random
import numpy as np

random.seed(seed)
np.random.seed(seed)
image = np.zeros(image_size, dtype=np.uint8)
for i in range(image_size[0]):
    for j in range(image_size[1]):
        for k in range(image_size[2]):
            image[i, j, k] = random.randint(range_low, range_high)
```

Using `np.random.randint(lo, hi, size=...)` in place of this loop produces a different pixel array.

## Displaying Images with Matplotlib

Convert BGR to RGB before passing to `ax.imshow()`:

```python
fig, ax = plt.subplots()
ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
ax.set_title('Original')
```

For side-by-side comparison:
```python
fig, (ax1, ax2) = plt.subplots(1, 2)
ax1.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
ax1.set_title('Original')
ax2.imshow(cv2.cvtColor(blurred, cv2.COLOR_BGR2RGB))
ax2.set_title('Blurred')
```
