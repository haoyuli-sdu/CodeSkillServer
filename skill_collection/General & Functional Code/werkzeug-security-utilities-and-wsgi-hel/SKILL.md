---
name: werkzeug-security-utilities-and-wsgi-hel
description: Password hashing with generate/check_password_hash, secure_filename, HTTP exceptions, and Flask integration.
---

# Werkzeug — Security Utilities and WSGI Helpers

## Password Hashing

`generate_password_hash` returns a salted hash string. `check_password_hash` verifies a plain-text password against a stored hash. Both are in `werkzeug.security`.

```python
from werkzeug.security import generate_password_hash, check_password_hash

hashed = generate_password_hash('mypassword')
check_password_hash(hashed, 'mypassword')    # True
check_password_hash(hashed, 'wrong')         # False
```

Typical usage in a User model with Flask-Login:

```python
class User(UserMixin):
    def __init__(self, username, password):
        self.id = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

## URL and File Utilities

`werkzeug.utils.secure_filename` sanitizes user-supplied filenames for safe filesystem use:

```python
from werkzeug.utils import secure_filename

filename = secure_filename('../../../etc/passwd')  # returns 'etc_passwd'
filename = secure_filename('my file.txt')          # returns 'my_file.txt'
```

## HTTP Exceptions

Common Werkzeug HTTP exceptions (importable from `werkzeug.exceptions`):

| Class | Status |
|---|---|
| `BadRequest` | 400 |
| `Unauthorized` | 401 |
| `Forbidden` | 403 |
| `NotFound` | 404 |
| `MethodNotAllowed` | 405 |
| `InternalServerError` | 500 |

These can be raised directly inside Flask views — Flask catches them and returns the appropriate HTTP response:

```python
from werkzeug.exceptions import Unauthorized, NotFound

def get_item(item_id):
    item = db.get(item_id)
    if item is None:
        raise NotFound(f'Item {item_id} not found')
    return item
```

## Request and Response Internals

Werkzeug provides the underlying `Request` and `Response` classes that Flask wraps. In most Flask tasks, you interact with Flask's proxies (`flask.request`, `flask.Response`) rather than Werkzeug's classes directly. The `werkzeug.security` module is the most commonly needed part of Werkzeug in authentication tasks.
