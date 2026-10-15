---
name: pytesseract-ocr-text-extraction-from-ima
description: 'Guide for pytesseract OCR: image_to_string returns string, encoding conversion with LookupError/UnicodeDecodeError, image metadata fallback pattern.'
---

# pytesseract — OCR Text Extraction from Images

## Basic Usage

`pytesseract.image_to_string()` accepts a PIL Image and returns extracted text as a string. An image with no detectable text returns `""`, never `None`.

```python
import pytesseract
from PIL import Image

with Image.open("document.png") as img:
    text = pytesseract.image_to_string(img)
```

## Encoding Conversion

After extracting text, re-encode from source to target encoding:

```python
converted = text.encode(from_encoding).decode(to_encoding)
```

An invalid codec name raises `LookupError`; incompatible byte sequences raise `UnicodeDecodeError`. Catch both and re-raise as `ValueError`:

```python
try:
    return text.encode(from_encoding).decode(to_encoding)
except (UnicodeDecodeError, LookupError) as exc:
    raise ValueError("Incorrect encoding provided.") from exc
```

## OCR with Image Metadata Fallback

When OCR may fail or produce empty output, fall back to metadata stored in the image's `info` dict:

```python
from PIL import Image
import codecs
import pytesseract

def extract_text(filename, from_encoding="cp1251", to_encoding="utf-8"):
    with Image.open(filename) as image:
        # Try OCR first
        try:
            text = pytesseract.image_to_string(image)
            if text:
                try:
                    return text.encode(from_encoding).decode(to_encoding)
                except (UnicodeDecodeError, LookupError) as exc:
                    raise ValueError("Incorrect encoding provided.") from exc
        except Exception:
            pass   # OCR unavailable or failed; fall through to metadata

        # Fall back to embedded comment metadata
        comment = image.info.get("comment", "")
        if isinstance(comment, bytes):
            try:
                return (
                    codecs.decode(comment, from_encoding)
                    .encode(to_encoding)
                    .decode(to_encoding)
                )
            except (UnicodeDecodeError, LookupError) as exc:
                raise ValueError("Incorrect encoding provided.") from exc

        return comment
```

The `image.info` dict may contain a `"comment"` key with bytes or a string depending on image format. Check `isinstance(comment, bytes)` before attempting codec decoding.

## Configuration Options

```python
# Specify Tesseract language
text = pytesseract.image_to_string(img, lang='eng')

# Get bounding boxes instead of raw text
data = pytesseract.image_to_data(img)

# Restrict to specific character set
custom_config = r'--psm 6 -c tessedit_char_whitelist=0123456789'
text = pytesseract.image_to_string(img, config=custom_config)
```
