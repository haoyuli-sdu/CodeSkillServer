---
name: flask-restful-resource-classes-and-api-r
description: Api(app) setup, Resource subclasses, add_resource URL registration, HTTP method handlers, and external API proxying.
---

# Flask-RESTful — Resource Classes and API Registration

## Core Pattern

Create an `Api(app)` object, define `Resource` subclasses with HTTP method handlers, and register each resource at its URL with `api.add_resource`. The URL is set by `add_resource`, not by the class name.

```python
from flask import Flask
from flask_restful import Resource, Api
import requests

def create_api_app(api_url, template_folder):
    app = Flask(__name__, template_folder=template_folder)
    api = Api(app)

    class DataResource(Resource):
        def get(self):
            response = requests.get(api_url)
            return response.json()    # dict; flask-restful serializes to JSON automatically

    api.add_resource(DataResource, '/data')   # endpoint at /data

    return app
```

## URL Path Registration

The path in `api.add_resource(Resource, '/path')` is the actual URL endpoint. Do not add extra prefixes unless the task explicitly specifies them:

```python
api.add_resource(ItemList, '/items')           # GET /items
api.add_resource(Item, '/items/<int:item_id>') # GET /items/1
```

## Resource Methods

Define HTTP verb handlers as lowercase method names: `get`, `post`, `put`, `delete`, `patch`. Returning a plain dict automatically serializes to JSON with status 200:

```python
class UserResource(Resource):
    def get(self):
        return {'name': 'Alice', 'role': 'admin'}   # 200 JSON

    def post(self):
        return {'created': True}, 201               # explicit status code
```

## Fetching External Data in a Resource

When a resource proxies an external API, use `requests.get()` and return `response.json()`:

```python
class ProxyResource(Resource):
    def get(self):
        resp = requests.get('https://api.example.com/data')
        return resp.json()    # returned dict becomes the JSON response body
```

## Integration with Flask App Factory

`Api(app)` wraps an existing Flask app. All normal Flask behavior (templates, config, extensions) is preserved. Return the Flask app object, not the `Api` object:

```python
app = Flask(__name__, template_folder=template_folder)
api = Api(app)
# define resources...
api.add_resource(MyResource, '/endpoint')
return app   # return app, not api
```
