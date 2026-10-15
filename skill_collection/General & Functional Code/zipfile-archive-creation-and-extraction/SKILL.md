---
name: zipfile-archive-creation-and-extraction
description: 'Practical guide to zipfile: arcname behavior, in-memory zipping, download+extract patterns, module-level constant handling.'
---

# zipfile — Archive Creation and Extraction

## Core context manager pattern

Always use `zipfile.ZipFile(path, mode)` as a context manager. The `mode` is `'r'` to read/extract, `'w'` to create a new archive, `'a'` to append:

```python
# Create
with zipfile.ZipFile('output.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write('report.pdf', arcname='report.pdf')

# Extract
with zipfile.ZipFile('archive.zip', 'r') as zf:
    zf.extractall('/tmp/out')   # creates /tmp/out if needed
    names = zf.namelist()
```

`extractall(dest)` creates `dest` automatically — no separate `os.makedirs` needed for the extraction target.

## arcname controls the stored path inside the archive

`zf.write(full_path)` stores the full path string (including all directory components). Pass `arcname` to override:

```python
# Stores 'reports/q1.csv' inside archive
zf.write('/data/reports/q1.csv', arcname='reports/q1.csv')

# Walking a directory — preserve relative structure
for root, dirs, files in os.walk(src_dir):
    for fname in files:
        full = os.path.join(root, fname)
        zf.write(full, arcname=os.path.relpath(full, src_dir))

# Walking a directory — include the top-level folder name
for root, dirs, files in os.walk(src_dir):
    for fname in files:
        full = os.path.join(root, fname)
        zf.write(full)   # stores e.g. "src_dir/subdir/fname"
```

When the task specifies that stored names should include the parent directory, omit `arcname` (or pass the joined path). When the task wants only bare filenames, pass `arcname=fname`.

## In-memory zip (writestr + BytesIO)

Use `writestr(arcname, data)` when content is already in memory — no real file required:

```python
buf = io.BytesIO()
with zipfile.ZipFile(buf, 'w') as zf:
    for name in file_names:
        zf.writestr(name, f'Content of {name}.')
buf.seek(0)
response = FileResponse(buf, as_attachment=True, filename='bundle.zip')
response['Content-Type'] = 'application/zip'
return response
```

`data` passed to `writestr` can be `str` or `bytes`.

## Download and extract (requests)

Save to a path inside the destination directory, then extract — do not call `os.makedirs` for the destination if the caller controls whether it exists:

```python
response = requests.get(url, headers=headers or {'accept': 'application/octet-stream'})
zip_path = os.path.join(destination_directory, os.path.basename(url))
with open(zip_path, 'wb') as f:
    f.write(response.content)
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(destination_directory)
return os.listdir(destination_directory)
```

## Download and extract (urllib + module-level constants)

When module-level constants like `TARGET_DIR` and `TARGET_ZIP_FILE` are defined, use them directly — do not join them with `os.getcwd()`:

```python
# Constants defined at module level:
# TARGET_DIR = "downloaded_files"
# TARGET_ZIP_FILE = "downloaded_files.zip"

os.makedirs(TARGET_DIR, exist_ok=True)
urllib.request.urlretrieve(url, TARGET_ZIP_FILE)   # bare constant, not os.path.join(cwd, ...)
with zipfile.ZipFile(TARGET_ZIP_FILE, 'r') as zf:
    zf.extractall(TARGET_DIR)
if os.path.exists(TARGET_ZIP_FILE):
    os.remove(TARGET_ZIP_FILE)
return TARGET_DIR
```

## Pattern-matching filenames then extracting

Use `re.match(pattern, filename)` and extract the capture group for the destination subdirectory. Call `os.makedirs` *after* `extractall` with `exist_ok=True` as a no-op guard:

```python
extracted_dirs = []
for filename in os.listdir(directory):
    match = re.match(pattern, filename)
    if match:
        base_name = match.group(1)
        extract_path = os.path.join(directory, base_name)
        with zipfile.ZipFile(os.path.join(directory, filename), 'r') as zf:
            zf.extractall(extract_path)
        if extract_path not in extracted_dirs:
            extracted_dirs.append(extract_path)
            os.makedirs(extract_path, exist_ok=True)
return extracted_dirs
```

## Filtering and archiving files (shutil.move workflow)

When processing files and moving them after archiving:

```python
archive_path = os.path.join(target_dir, archive_name)
with zipfile.ZipFile(archive_path, 'w') as zf:
    for fname in os.listdir(source_dir):
        if condition(fname):
            full = os.path.join(source_dir, fname)
            zf.write(full, arcname=fname)
            shutil.move(full, target_dir)
return archive_path
```

## Zip filename placement

A bare name like `'output.zip'` lands in the current working directory. Joining with a directory changes its location. When a constant like `ZIPFILE_NAME = 'encrypted.zip'` is defined, return and use that exact constant:

```python
zipfile_name = 'encrypted_files.zip'    # stays in cwd
with zipfile.ZipFile(zipfile_name, 'w') as zf:
    for fname in os.listdir(directory):
        fp = os.path.join(directory, fname)
        if os.path.isfile(fp):
            zf.writestr(fname, encrypt(open(fp, 'rb').read()))
return pub_key, zipfile_name
```

## Streaming download with error handling

```python
try:
    r = requests.get(url, stream=True, timeout=5)
    if r.status_code == 200:
        filepath = DOWNLOAD_DIR / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content():
                f.write(chunk)
        zip_dir = ZIP_DIR / filename[:-4]
        zip_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(filepath, 'r') as zf:
            zf.extractall(zip_dir)
        return 'Download and extraction successful', [p.name for p in zip_dir.iterdir()]
    return f'Download failed: HTTP status code {r.status_code}', []
except requests.exceptions.RequestException as e:
    return f'Error: {e}', []
except zipfile.BadZipFile as e:
    return f'Error: Invalid zip file: {e}', []
```
