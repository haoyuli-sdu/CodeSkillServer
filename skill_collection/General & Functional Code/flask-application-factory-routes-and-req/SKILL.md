---
name: flask-application-factory-routes-and-req
description: Guide for Flask app factories, route definitions, logging patterns, Flask-Login auth, Flask-Mail setup, and Flask-RESTful integration.
---

# Flask — Application Factory, Routes, and Request Handling

## Application Factory Pattern

Pass `template_folder` to `Flask(__name__, template_folder=...)` when a custom templates directory is required. Set `app.config['SECRET_KEY']` for sessions and CSRF support.

```python
from flask import Flask

def create_app(template_folder, secret_key):
    app = Flask(__name__, template_folder=template_folder)
    app.config['SECRET_KEY'] = secret_key
    return app
```

## Route Definition

Specify `methods` explicitly for non-GET routes. Route names and paths must match what callers expect.

```python
@app.route('/submit', methods=['POST'])
def handle_post():
    data = request.get_json()
    return render_template('result.html', data=data)

@app.route('/data')          # GET by default
def get_data():
    return jsonify({'status': 'ok'})
```

## Logging JSON Payload — Single-Argument Form

When logging a JSON request payload, serialize it with `json.dumps()` and pass that single string to `logging.info()`. Any prefix or format string in the call adds positional arguments that change the call signature:

```python
import json
import logging

@app.route('/', methods=['POST'])
def handle():
    data = request.get_json()
    logging.info(json.dumps(data))           # one argument: the JSON string
    return render_template('index.html', data=data)
```

`logging.info(json.dumps(data))` differs from `logging.info("Got: %s", json.dumps(data))` — the second form passes two arguments. When the exact call signature matters, use the single-argument form.

## Protected Routes — Return Strings, Not Templates

A `@login_required` route can return a plain string. When there is no HTML template file on disk, returning a string avoids `TemplateNotFound` errors:

```python
@app.route('/protected')
@login_required
def protected():
    return 'Logged in as: ' + current_user.id   # no template file needed
```

## Flask-Mail Integration

Configure mail via `app.config`, bind with `mail.init_app(app)`, and define the route the task specifies (route name matters):

```python
from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = smtp_server
app.config['MAIL_PORT'] = smtp_port
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = smtp_user
app.config['MAIL_PASSWORD'] = smtp_password

mail = Mail()
mail.init_app(app)

@app.route('/send_mail')
def send_mail():
    msg = Message('Hello', sender='from@example.com', recipients=['to@example.com'])
    msg.body = 'Hello Flask message sent from Flask-Mail'
    mail.send(msg)
    return 'Mail sent!'
```

## Flask-RESTful Integration

Wrap an existing Flask app with `Api(app)`, define `Resource` subclasses, and register them with `api.add_resource`. The path in `add_resource` is the actual URL:

```python
from flask_restful import Resource, Api
import requests

api = Api(app)

class DataResource(Resource):
    def get(self):
        response = requests.get(external_url)
        return response.json()   # dict; flask-restful serializes to JSON automatically

api.add_resource(DataResource, '/data')   # accessible at /data
```

## Flask-Login — User Authentication Setup

Create `LoginManager` at module level. Call `login_manager.init_app(app)` inside the factory. Register a `user_loader` callback. The `User` class must set `self.id`:

```python
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

login_manager = LoginManager()

def create_app(secret_key, template_folder):
    app = Flask(__name__, template_folder=template_folder)
    app.config['SECRET_KEY'] = secret_key
    login_manager.init_app(app)

    class User(UserMixin):
        def __init__(self, username, password):
            self.id = username
            self.password_hash = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.password_hash, password)

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id, 'password')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User(form.username.data, form.password.data)
            login_user(user)
            return redirect(url_for('protected'))
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/protected')
    @login_required
    def protected():
        return 'Logged in as: ' + current_user.id   # plain string, no template

    return app
```
