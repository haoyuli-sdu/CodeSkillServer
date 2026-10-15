---
name: wtforms-form-fields-and-validators
description: Common field types, validators, standalone validation, field data access, and Flask-WTF integration.
---

# WTForms — Form Fields and Validators

## Common Field Types

| Field class | Purpose |
|---|---|
| `StringField` | Single-line text input |
| `PasswordField` | Password input (masked) |
| `TextAreaField` | Multi-line text |
| `IntegerField` | Integer number |
| `BooleanField` | Checkbox |
| `SelectField` | Dropdown; use `choices=[(val, label), ...]` |
| `SubmitField` | Submit button |

All field constructors take `(label, validators=[...])` as the first two positional arguments.

## Common Validators

```python
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, Optional

StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
StringField('Email', validators=[DataRequired(), Email()])
PasswordField('Confirm', validators=[EqualTo('password')])
IntegerField('Age', validators=[NumberRange(min=0, max=120)])
```

- `DataRequired()` — field must not be empty.
- `Length(min=N, max=M)` — string length bounds.
- `Email()` — validates email format (requires `email-validator` package).
- `EqualTo('other_field')` — value must match another field's value.
- `Optional()` — makes a field optional; short-circuits other validators if empty.

## Standalone Validation (without Flask)

When using WTForms outside Flask, subclass `Form` from `wtforms` (not `FlaskForm` from `flask_wtf`). Use `form.validate()` instead of `validate_on_submit()`.

```python
from wtforms import Form, StringField, IntegerField
from wtforms.validators import DataRequired, NumberRange

class ProfileForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[NumberRange(min=0, max=120)])

form = ProfileForm(data={'name': 'Alice', 'age': 30})
if form.validate():
    print(form.name.data, form.age.data)
```

## Field Data Access and Errors

After validation, access field values with `form.field_name.data`. Errors appear in `form.errors` as a dict mapping field names to lists of error messages:

```python
if not form.validate():
    print(form.username.errors)   # e.g. ['This field is required.']
    print(form.errors)            # {'username': ['This field is required.']}
```

## Integration with Flask-WTF

In Flask applications, import `FlaskForm` from `flask_wtf` instead of `Form` from `wtforms`. All field and validator imports still come from `wtforms` and `wtforms.validators`:

```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=80)])
    submit = SubmitField('Log In')
```
