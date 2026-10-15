---
name: scikit-image-skimage-image-transformatio
description: 'skimage patterns: resize returns float64 in [0,1], scaling by factor using PIL dimensions, float-to-uint8 conversion, color and filter utilities.'
---

# scikit-image (skimage) — Image Transformation and Processing

## Resizing with skimage.transform.resize

`resize()` always returns a **float64 array with values in `[0.0, 1.0]`**, regardless of input dtype:

```python
from skimage.transform import resize
import numpy as np

arr = np.array(img)  # uint8, shape (H, W, 3)
scaled = resize(arr, (new_h, new_w), mode='reflect', anti_aliasing=True)
# scaled.dtype == float64, values in [0.0, 1.0]
```

Matplotlib's `ax.imshow()` handles `float64` arrays in `[0, 1]` natively — pass the result directly:

```python
ax.imshow(scaled)   # no conversion needed
```

## Scaling by Factor

Compute target dimensions from PIL `Image` attributes:

```python
from PIL import Image
from skimage.transform import resize
import matplotlib.pyplot as plt
import numpy as np

def scale_images(img_path, scale_factors):
    im = Image.open(img_path)
    img_arr = np.array(im)
    results = []
    for sf in scale_factors:
        new_h = int(im.height * sf)
        new_w = int(im.width * sf)
        scaled = resize(img_arr, (new_h, new_w), mode='reflect', anti_aliasing=True)
        fig, ax = plt.subplots()
        ax.imshow(scaled)
        ax.set_title(f'Scale factor: {sf}')
        results.append((ax, scaled))
    return results
```

## Converting float64 → uint8

Only needed when passing to cv2 or PIL functions requiring uint8:

```python
scaled_uint8 = (scaled * 255).astype(np.uint8)
```

Direct `.astype(np.uint8)` without multiplying truncates float values to 0 or 1.

## Color and Filter Utilities

```python
from skimage.color import rgb2gray, gray2rgb
from skimage.filters import gaussian, sobel
from skimage.feature import canny

gray = rgb2gray(arr)          # float64 in [0, 1], shape (H, W)
blurred = gaussian(arr, sigma=1.0)
edges = canny(gray)           # bool array
```
