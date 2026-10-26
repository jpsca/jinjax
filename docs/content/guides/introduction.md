---
title: Introduction
description: JinjaX is a Python library for creating reusable "components" - encapsulated template snippets that can take arguments and render to HTML. They are similar to React or Vue components, but they render on the server side, not in the browser.
---


Unlike Jinja's `{% include "..." %}` or macros, JinjaX components integrate naturally with the rest of your template code.

```html+jinja
<div>
  <Card class="bg-gray">
    <h1>Products</h1>
    {% for product in products %}
      <Product product={{ product }} />
    {% endfor %}
  </Card>
</div>
```

## Features

### Simple

JinjaX components are simple Jinja templates. You use them as if they were HTML tags without needing to import them: they're easy to use and easy to read.

### Encapsulated

They are independent of each other and can link to their own CSS and JS, so you can freely copy and paste components between applications.

### Testable

All components can be unit tested independently of the pages where they are used.

### Composable

A JinjaX component can wrap HTML code or other components with a natural syntax, treating them as if they were native HTML tags.

### Modern

They are a great complement to technologies like [TailwindCSS](https://tailwindcss.com/), [htmx](https://htmx.org/), or [Hotwire](https://hotwired.dev/).

## Usage

#### Install

Install the library using `pip`.

```bash
pip install jinjax
```

#### Components folder

Then, create a folder that will contain your components, for example:

```
└ myapp/
    ├── app.py
    ├── components/             🆕
    │   └── Card.jinja          🆕
    ├── static/
    ├── templates/
    └── views/
└─ requirements.txt
```

#### Catalog

Finally, you must create a "catalog" of components in your app. This object manages the components and their global settings. You then add the path to your components folder to this catalog:

```python
from jinjax import Catalog

catalog = Catalog()
catalog.add_folder("myapp/components")
```

#### Render

You'll use the catalog to render components from your views.

```python
def myview():
  ...
  return catalog.render(
    "Page",
    title="Lorem ipsum",
    message="Hello",
  )
```

### Per-request globals

Besides the regular arguments, `catalog.render()` accepts a special `_globals` argument: a dictionary of values that are made available as template globals to the component being rendered **and every component nested inside it**, no matter how deep. This is the way to make the current request, the current user, a CSRF token, or any other per-request data available to all your components without passing it down by hand through every level.

```python
def myview(request):
  ...
  return catalog.render(
    "Page",
    title="Lorem ipsum",
    _globals={"request": request, "current_user": request.user},
  )
```

Then any component in the tree can use those names directly:

```html+jinja
{#- Navbar.jinja, rendered somewhere inside Page -#}
<nav>
  {% if current_user %}
    <a href="/profile">{{ current_user.name }}</a>
  {% endif %}
  <span>{{ request.path }}</span>
</nav>
```

Some details to be aware of:

- The values are scoped to that `render()` call. The next call starts with an empty set, so values never leak between requests, and the globals are safe to use when rendering from multiple threads at the same time.
- They are globals, not arguments, so you don't declare them in the component's `{#def ... #}` header, and they don't show up in `attrs`.
- An explicit argument with the same name takes precedence over the global of the same name.
- `_globals` is only read by `catalog.render()`. If you call `catalog.irender()` inside a template, the globals of the enclosing `render()` call are already in effect.

If you need values that are the same for every render call, like helper functions or site-wide settings, use the catalog-level `globals` instead (see "Reusing Jinja's Globals, Filters, and Tests" below).

In this example, we're rendering a component for the whole page, but you can also render smaller components, even from inside a regular Jinja template by adding the catalog as a global:

```python
app.jinja_env.globals["catalog"] = catalog
```

```html+jinja
{% block content %}
<div>
  {{ catalog.irender("LikeButton", title="Like and subscribe!", post=post) }}
</div>
<p>Lorem ipsum</p>
{{ catalog.irender("CommentForm", post=post) }}
{% endblock %}
```

## How It Works

JinjaX uses Jinja to render component templates. It works as a pre-processor, replacing code like:

```html
<Component attr="value">content</Component>
```

with function calls like:

```html+jinja
{% call catalog.irender("Component", attr="value") %}content{% endcall %}
```

These calls are evaluated at render time. Each call loads the component file's source, extracts the names of CSS/JS files and required/optional attributes, pre-processes the template (replacing components with function calls as described above), and finally renders the complete template.

### Reusing Jinja's Globals, Filters, and Tests

You can add your own global variables and functions, filters, tests, and Jinja extensions when creating the catalog:

```python
from jinjax import Catalog

catalog = Catalog(
    globals={ ... },
    filters={ ... },
    tests={ ... },
    extensions=[ ... ],
)
```

or afterward.

```python
catalog.jinja_env.globals.update({ ... })
catalog.jinja_env.filters.update({ ... })
catalog.jinja_env.tests.update({ ... })
catalog.jinja_env.add_extension(MyExtension)
```

The ["do" extension](https://jinja.palletsprojects.com/en/3.0.x/extensions/#expression-statement) is enabled by default, so you can write things like:

```html+jinja
{% do attrs.set(class="btn", disabled=True) %}
```

JinjaX also adds a `get_random_id()` global function and an equivalent `random_id` filter to the environment. They are useful for generating unique HTML `id` attributes:

```html+jinja
{% set uid = get_random_id("dropdown") %}  {# "dropdown-xxxxxxxx..." #}
```

### Reusing an Existing Jinja Environment

You can also reuse an existing Jinja Environment, for example:

#### Flask:

```python
app = Flask(__name__)

# Here we add the Flask Jinja globals, filters, etc., like `url_for()`
catalog = jinjax.Catalog(jinja_env=app.jinja_env)
```

#### Django:

First, configure Jinja in `settings.py` and [jinja_env.py](https://docs.djangoproject.com/en/5.0/topics/templates/#django.template.backends.jinja2.Jinja2).

To have a separate "components" folder for shared components and also have "components" subfolders at each Django app level:

```python
import jinjax
from jinja2.loaders import FileSystemLoader

def environment(loader: FileSystemLoader, **options):
    env = Environment(loader=loader, **options)

    ...

    env.add_extension(jinjax.JinjaX)
    catalog = jinjax.Catalog(jinja_env=env)

    catalog.add_folder("components")
    for dir in loader.searchpath:
        catalog.add_folder(os.path.join(dir, "components"))

    return env
```

#### FastAPI:

```python
import jinjax
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

templates.env.add_extension(jinjax.JinjaX)
catalog = jinjax.Catalog(jinja_env=templates.env)
catalog.add_folder("templates/components")

@app.get("/")
def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
```
