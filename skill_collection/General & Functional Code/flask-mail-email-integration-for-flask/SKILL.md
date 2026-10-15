---
name: flask-mail-email-integration-for-flask
description: Flask-Mail configuration types, initialization patterns, Message composition, and returning mail+config tuples.
---

# Flask-Mail — Email Integration for Flask

## Configuration Keys and Types

All mail settings go into `app.config`. `MAIL_PORT` must be an **integer**. When reading from environment variables (which return strings), convert explicitly:

```python
import os

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'localhost')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 25))          # int(), not string
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', False) == 'True'   # boolean
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', None)
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', None)
```

When parameters are passed directly (not from environment variables), assign them as-is since they already have the correct types.

## Two Initialization Patterns

**Direct initialization** — pass the app to `Mail()` constructor:
```python
mail = Mail(app)
```

**Application factory pattern** — create `Mail()` first, bind later:
```python
mail = Mail()
mail.init_app(app)
```

Both patterns work. The factory pattern is useful when the app object is constructed inside a function.

## Return Value: Mail Instance and Config Dict

When the task asks to return a `(mail_instance, configs)` tuple, read values from `app.config` (not from `os.getenv()` calls). The config values are already typed after the conversion above:

```python
mail = Mail(app)

return mail, {
    'MAIL_SERVER': app.config['MAIL_SERVER'],
    'MAIL_PORT': app.config['MAIL_PORT'],        # already int
    'MAIL_USE_TLS': app.config['MAIL_USE_TLS'],  # already bool
    'MAIL_USERNAME': app.config['MAIL_USERNAME'],
    'MAIL_PASSWORD': app.config['MAIL_PASSWORD'],
}
```

## Sending a Message

`Message` takes `subject`, `sender`, and `recipients` (a list). Message body goes in `msg.body`. The route name must match what the task specifies:

```python
from flask import Flask
from flask_mail import Mail, Message

def setup_mail_app(smtp_server, smtp_port, smtp_user, smtp_password, template_folder):
    app = Flask(__name__, template_folder=template_folder)
    app.config['MAIL_SERVER'] = smtp_server
    app.config['MAIL_PORT'] = smtp_port
    app.config['MAIL_USERNAME'] = smtp_user
    app.config['MAIL_PASSWORD'] = smtp_password
    app.config['MAIL_USE_TLS'] = True

    mail = Mail()
    mail.init_app(app)

    @app.route('/send_mail')
    def send_mail():
        msg = Message('Hello', sender='from@example.com', recipients=['to@example.com'])
        msg.body = 'Hello Flask message sent from Flask-Mail'
        mail.send(msg)
        return 'Mail sent!'

    return app
```

## Full Setup with os.getenv

```python
from flask import Flask
from flask_mail import Mail, Message
import os

def setup_mail_app(app_name):
    app = Flask(app_name)
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'localhost')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 25))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', False) == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', None)
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', None)

    mail = Mail(app)

    return mail, {
        'MAIL_SERVER': app.config['MAIL_SERVER'],
        'MAIL_PORT': app.config['MAIL_PORT'],
        'MAIL_USE_TLS': app.config['MAIL_USE_TLS'],
        'MAIL_USERNAME': app.config['MAIL_USERNAME'],
        'MAIL_PASSWORD': app.config['MAIL_PASSWORD'],
    }
```
