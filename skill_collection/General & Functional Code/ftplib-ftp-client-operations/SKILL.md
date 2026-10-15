---
name: ftplib-ftp-client-operations
description: FTP connection/login/navigation, nlst for file listing, structured error handling, and subprocess wget downloads.
---

# ftplib — FTP Client Operations

## Connection, Login, and Navigation

```python
import ftplib

ftp = ftplib.FTP('ftp.example.com')   # connect; no authentication yet
ftp.login('username', 'password')     # authenticate
ftp.cwd('/remote/dir')                # change working directory
```

## Listing Directory Contents

`nlst()` returns a plain list of filenames — use it when you need names only:

```python
files = ftp.nlst()      # ['data.csv', 'report.zip', ...]
```

`dir()` calls a callback with full `ls -l`-style lines — use it only when metadata is needed.

## Structured Error Handling

Wrap each step separately so exception messages include the right context:

```python
try:
    ftp = ftplib.FTP(server)
except Exception as e:
    raise Exception(f'Failed to connect to FTP server {server}: {e}')

try:
    ftp.login(user, password)
except Exception as e:
    raise Exception(f'Failed to log into FTP server {server} with user {user}: {e}')

try:
    ftp.cwd(directory)
except Exception as e:
    raise Exception(f'Failed to change to directory {directory} on server {server}: {e}')
```

## Downloading Files with wget via subprocess

When a task combines FTP listing with `subprocess` wget downloads:

```python
import os, subprocess

download_dir = "downloaded_files"
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

downloaded_files = []
for filename in ftp.nlst():
    command = f'wget ftp://{user}:{password}@{server}{ftp_dir}/{filename} -P {download_dir}'
    subprocess.call(command, shell=True)
    downloaded_files.append(filename)

ftp.quit()
return downloaded_files
```

Use `subprocess.call()` (not `subprocess.run()`). Call `ftp.quit()` **after** the download loop completes — not inside a `finally` block that runs before the loop.

## Downloading Files Directly with retrbinary

```python
with open('local_copy.bin', 'wb') as f:
    ftp.retrbinary('RETR remote_file.bin', f.write)
```

## Closing the Connection

```python
ftp.quit()    # graceful close with QUIT command
ftp.close()   # immediate close without QUIT
```
