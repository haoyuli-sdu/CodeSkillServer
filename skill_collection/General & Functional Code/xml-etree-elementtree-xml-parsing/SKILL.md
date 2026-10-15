---
name: xml-etree-elementtree-xml-parsing
description: 'Guide for xml.etree.ElementTree: fromstring, root.iter() for flat extraction, XML-to-CSV pattern, error handling, and element attribute access.'
---

# xml.etree.ElementTree — XML Parsing

## Basic Usage

```python
import xml.etree.ElementTree as ET

# Parse from string
root = ET.fromstring(xml_string)   # returns root Element

# Parse from file
tree = ET.parse("file.xml")
root = tree.getroot()
```

## Iterating All Elements

`root.iter()` yields the root element itself plus every descendant in document order:

```python
# Flatten entire XML into [tag, text] pairs — includes the root element
data = [[elem.tag, elem.text] for elem in root.iter()]
```

This is the idiomatic pattern for converting any XML to a flat two-column format (tag, text). The first row will be the root element itself. Do **not** skip the root by iterating from children — include it unless the task explicitly says to exclude it.

Targeted iteration alternatives:
- Direct children only: `list(root)` or `for child in root:`
- Specific tag anywhere in tree: `root.iter("record")` or `root.findall(".//record")`

## XML → CSV

```python
import xml.etree.ElementTree as ET
import csv

def xml_to_csv(xml_content, output_csv_path):
    try:
        root = ET.fromstring(xml_content)
        data = [[elem.tag, elem.text] for elem in root.iter()]
        with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(data)
    except ET.ParseError as e:
        raise ET.ParseError(f"Error parsing XML: {e}") from e
    except IOError as e:
        raise IOError(f"Error writing CSV file: {e}") from e
```

`newline=""` prevents double line endings on Windows. Re-raise `ET.ParseError` and `IOError` rather than swallowing them.

Do **not** add pre-flight path checks like `os.path.isdir(os.path.dirname(output_csv_path))` — this fails when the output path is a plain filename like `"output.csv"` (whose `dirname` is `""`).

## Error Handling

`ET.ParseError` is raised for malformed XML. It is a subclass of `SyntaxError`. Re-raise it wrapped in a descriptive message:

```python
try:
    root = ET.fromstring(xml_content)
except ET.ParseError as e:
    raise ET.ParseError(f"Error parsing XML: {e}") from e
```

## Element attributes and text

```python
# Access tag, text, and attributes
elem.tag        # tag name as string
elem.text       # text content (may be None for elements with only child elements)
elem.attrib     # dict of attributes
elem.get("id")  # single attribute with optional default
```
