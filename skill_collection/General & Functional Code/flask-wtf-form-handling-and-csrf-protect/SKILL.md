---
name: flask-wtf-form-handling-and-csrf-protect
description: FlaskForm subclassing, validate_on_submit pattern, SECRET_KEY requirement, and module-level form definitions.
---

# Flask-WTF — Form Handling and CSRF Protection

## FlaskForm Basics

Subclass `FlaskForm` from `flask_wtf`. Define fields as class attributes. `form.validate_on_submit()` returns `True` only when the request method is POST and all validators pass.

```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=80)])
    submit = SubmitField('Log In')
```

## Using a Form in a Route

Access field values with `form.field_name.data` after `validate_on_submit()` succeeds:

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        login_user(User(username, password))
        return redirect(url_for('protected'))
    return render_template('login.html', form=form)
```

## SECRET_KEY Requirement

Flask-WTF requires `app.config['SECRET_KEY']` for CSRF token generation. Set it before any form is used:

```python
app.config['SECRET_KEY'] = secret_key
```

## Forms Defined Outside the Factory Function

A `FlaskForm` subclass defined at module level (outside the factory) is fully usable inside route handlers. The class definition does not need to be inside the factory:

```python
class LoginForm(FlaskForm):    # module-level definition is fine
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

login_manager = LoginManager()   # also module-level

def create_app(secret_key, template_folder):
    app = Flask(__name__, template_folder=template_folder)
    app.config['SECRET_KEY'] = secret_key
    login_manager.init_app(app)
    # use LoginForm inside routes defined here
    return app
```

## CSRF in Non-Production Environments

Application code only needs to set `SECRET_KEY`. Disabling CSRF for non-production use is a configuration concern, not an application code concern.
