---
title: Introduction
---

<Header title="Introduction">
JinjaX is a Python library for creating reusable "components": encapsulated template snippets that can take arguments and render to HTML. They are similar to React or Vue components, but they render on the server side, not in the browser.
</Header>

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

JinjaX components are simple Jinja templates. You use them as if they were HTML tags without having to import them: easy to use and easy to read.

### Encapsulated

They are independent of each other and can link to their own CSS and JS, so you can freely copy and paste components between applications.

### Testable

All components can be unit tested independently of the pages where they are used.

### Composable

A JinjaX component can wrap HTML code or other components with a natural syntax, as if they were another tag.

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

Finally, you must create a "catalog" of components in your app. This is the object that manages the components and their global settings. You then add the path of the folder with your components to the catalog:

```python
from jinjax import Catalog

catalog = Catalog()
catalog.add_folder("myapp/components")
```

#### Render

You will use the catalog to render components from your views.

```python
def myview():
  ...
  return catalog.render(
    "Page",
    title="Lorem ipsum",
    message="Hello",
  )
```

In this example, it is a component for the whole page, but you can also render smaller components, even from inside a regular Jinja template if you add the catalog as a global:

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

JinjaX uses Jinja to render the component templates. In fact, it currently works as a pre-processor, replacing all:

```html
<Component attr="value">content</Component>
```

with function calls like:

```html+jinja
{% call catalog.irender("Component", attr="value") %}content{% endcall %}
```

These calls are evaluated at render time. Each call loads the source of the component file, parses it to extract the names of CSS/JS files, required and/or optional attributes, pre-processes the template (replacing components with function calls, as before), and finally renders the new template.

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
catalog.jinja_env.extensions.extend([ ... ])
```

The ["do" extension](https://jinja.palletsprojects.com/en/3.0.x/extensions/#expression-statement) is enabled by default, so you can write things like:

```html+jinja
{% do attrs.set(class="btn", disabled=True) %}
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

TBD