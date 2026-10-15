---
name: pillow-pil-image-opening-transformation
description: 'PIL patterns: opening images without unnecessary mode conversion, URL fetching, filters, numpy interop, and grayscale histograms.'
---

# Pillow (PIL) — Image Opening, Transformation, and Processing

## Opening Images

`Image.open()` opens an image lazily and preserves the original mode (RGB, RGBA, L, etc.). Call `.convert()` only when a specific mode is explicitly required — adding an unnecessary `.convert("RGB")` will discard the alpha channel of RGBA images:

```python
from PIL import Image
img = Image.open("photo.png")      # preserves original mode (could be RGBA, L, etc.)
img_rgb = img.convert("RGB")      # only if RGB is specifically needed
```

Common modes: `"RGB"` (3-channel), `"L"` (grayscale), `"RGBA"` (4-channel with alpha).

## Image Dimensions

`img.width` and `img.height` give dimensions in pixels. `resize()` takes `(width, height)` — note width first, opposite of numpy `(H, W)` convention:

```python
new_w = int(img.width * 0.5)
new_h = int(img.height * 0.5)
small = img.resize((new_w, new_h))
```

## Fetching Images from URLs

For non-streaming requests, open from `io.BytesIO(response.content)`. Let `raise_for_status()` handle HTTP errors — do not compare `response.status_code` directly:

```python
import requests
from PIL import Image
import io

def fetch_image(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content))
        return image
    except Exception as e:
        raise ValueError(f"Failed to retrieve image from {url}: {e}") from e
```

For streamed downloads, use `response.raw` with `stream=True`. Keep `IOError` and `requests.RequestException` in separate `except` blocks so each raises the right exception type:

```python
def fetch_and_convert(url):
    response = None
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        img = Image.open(response.raw).convert("L")
    except requests.RequestException as e:
        raise ValueError(f"Error downloading the image: {e}") from e
    except IOError as e:
        raise IOError(f"Error processing the image: {e}") from e
    finally:
        if response:
            response.close()
    return img
```

## Applying Filters

```python
from PIL import ImageFilter

blurred = img.filter(ImageFilter.GaussianBlur(radius=2))
sharpened = img.filter(ImageFilter.SHARPEN)
```

## Rotation

`img.rotate(angle)` rotates counter-clockwise. Use `expand=True` to avoid cropping corners:

```python
rotated = img.rotate(45, expand=True)
```

## Converting PIL Image to/from numpy

```python
arr = np.array(img)                   # dtype uint8, shape (H, W, 3) or (H, W)
img = Image.fromarray(arr.astype(np.uint8))
```

After `skimage.transform.resize()`, the result is `float64` in `[0, 1]`. Matplotlib's `ax.imshow()` handles float arrays in `[0, 1]` natively — pass the result directly without conversion:

```python
from skimage.transform import resize

scaled = resize(np.array(img), (new_h, new_w), mode='reflect', anti_aliasing=True)
ax.imshow(scaled)   # float64 in [0, 1] is fine for imshow
```

## Grayscale Histogram

```python
img = Image.open(path).convert("L")
arr = np.array(img)
_, ax = plt.subplots()
ax.hist(arr.ravel(), bins=256, color="gray", alpha=0.7)
return ax
```

## OCR with pytesseract

```python
from PIL import Image
import pytesseract

with Image.open(filename) as image:
    text = pytesseract.image_to_string(image)
```
