---
name: xmltodict-xml-to-dictionary-conversion
description: 'Guide for xmltodict: parse/unparse API, OrderedDict output, XML-to-JSON file patterns, conditional save, and common pitfalls (return value, hardcoded paths).'
---

# xmltodict — XML to Dictionary Conversion

## Core API

```python
import xmltodict

data = xmltodict.parse(xml_string)   # → OrderedDict
xml_str = xmltodict.unparse(data)    # → XML string
```

`xmltodict.parse` wraps the document in a dict keyed by the root element:

```python
xmltodict.parse("<root><name>Alice</name><age>30</age></root>")
# → {"root": {"name": "Alice", "age": "30"}}

xmltodict.parse("<items><item>A</item><item>B</item></items>")
# → {"items": {"item": ["A", "B"]}}   # list when multiple same-tag siblings

xmltodict.parse("<root attr='val'><child>X</child></root>")
# → {"root": {"@attr": "val", "child": "X"}}   # attributes prefixed with @
```

## XML → JSON file

Always write to the path argument received, not a hardcoded name. Return the dict object, not the file path:

```python
import xmltodict, json

def xml_to_json_file(xml_string, file_path):
    my_dict = xmltodict.parse(xml_string)
    with open(file_path, "w") as json_file:
        json.dump(my_dict, json_file, indent=4)
    return my_dict
```

## Conditional save

```python
import xmltodict, json

def xml_to_json_optional(xml_string, save_json, json_file_path):
    my_dict = xmltodict.parse(xml_string)
    if save_json:
        with open(json_file_path, "w") as f:
            json.dump(my_dict, f, indent=4)
    return my_dict
```

## Common pitfalls

- **Return value**: return the `OrderedDict` from `xmltodict.parse(...)`, not a string or the file path.
- **Hardcoded output path**: always write to the `file_path` argument, not a literal like `"output.json"`.
- **Invalid XML**: `xmltodict.parse("")` raises `xml.parsers.expat.ExpatError` — let it propagate unless the task says to handle it.
- **OrderedDict vs dict**: the return value compares equal to a plain dict with the same keys — no conversion is needed.
