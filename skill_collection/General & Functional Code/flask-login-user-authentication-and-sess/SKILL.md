---
name: flask-login-user-authentication-and-sess
description: LoginManager setup, UserMixin requirements, login/logout routes, and protected routes returning plain strings.
---

# Flask-Login — User Authentication and Session Management

## Core Setup

Create a `LoginManager` at module level, call `login_manager.init_app(app)` inside the factory, and register a `@login_manager.user_loader` callback. The `user_loader` receives a user ID string and returns a user object.

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
            self.id = username                              # id must be set
            self.password_hash = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.password_hash, password)

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id, 'password')    # minimal stub

    return app
```

## Login and Logout Routes

`login_user(user)` logs the user in. `logout_user()` logs the current user out. `@login_required` protects a route.

```python
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
```

## Protected Routes — Return Strings, Not Templates

A `@login_required` route can return a plain string. When there is no HTML template file available, returning a string avoids `TemplateNotFound` errors:

```python
@app.route('/protected')
@login_required
def protected():
    return 'Logged in as: ' + current_user.id   # no template file needed
```

`current_user.id` is the value stored in `self.id` on the user object. If `self.id = username`, then `current_user.id` is the username string.

## UserMixin Requirements

`UserMixin` provides default implementations of `is_authenticated`, `is_active`, `is_anonymous`, and `get_id()`. The only attribute you must set manually is `self.id` — Flask-Login's `get_id()` returns `str(self.id)` automatically.

```python
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id   # this is all that's required for get_id() to work
```
