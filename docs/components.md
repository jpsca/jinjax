---
title: Components
description: Declaring and using components.
---

## Declaring and Using Components

Components are simple text files that look like regular Jinja templates, with three requirements:

**First**, components must be placed inside a folder registered in the catalog or a subfolder of it.

```python
catalog.add_folder("myapp/components")
```

You can name that folder whatever you want (not just "components"). You can also add more than one folder:

```python
catalog.add_folder("myapp/layouts")
catalog.add_folder("myapp/components")
```

If you end up having more than one component with the same name, the one in the first folder will take priority.

**Second**, they must have a ".jinja" extension. This also helps code editors automatically select the correct language syntax for highlighting. However, you can configure this extension in the catalog.

**Third**, the filename must be either PascalCased (like Python classes) or "kebab-cased" (lowercase with words separated by dashes).

The PascalCased name of the file (minus the extension) is always how you call the component (even if the
filename is kebab-cased). This is how JinjaX differentiates a component from a regular HTML tag when using it.

For example, if the file is "components/PersonForm.jinja":

```
└ myapp/
  ├── app.py
  ├── components/
        └─ PersonForm.jinja
```

The name of the component is "PersonForm" and can be called like this:

From Python code or a non-component template:

- `catalog.render("PersonForm")`

From another component:

- `<PersonForm> some content </PersonForm>`, or
- `<PersonForm />`


If you prefer you can also choose to use kebab-cased filenames:

```
└ myapp/
  ├── app.py
  ├── components/
        └─ person-form.jinja
```

The name of the component **will still be "PersonForm"** and you will use it in the same way as before.

<Alert variant="warning">
Do not mix PascalCased files with kebab-cased files. Choose a name format you like
and stick with it.
</Alert>


If the component is in a subfolder, the name of that folder becomes part of its name too:

```
└ myapp/
  ├── app.py
  ├── components/
        └─ person
            └─ PersonForm.jinja
```

A "components/person/PersonForm.jinja" component is named "person.PersonForm", meaning the name of the subfolder and the name of the file separated by a dot. This is the full name you use to call it:

From Python code or a non-component template:

- `catalog.render("person.PersonForm")`

From another component:

- `<person.PersonForm> some content </person.PersonForm>`, or
- `<person.PersonForm />`

Notice that the folder name doesn't need to follow any naming convention if you don't want it to.

<a href="./img/anatomy-en.png" target="_blank">
  <img src="./img/anatomy-en.png" style="margin:0 auto;width:90%;max-width:35rem;">
</a>


## Taking Arguments

More often than not, a component takes one or more arguments to render. Every argument must be declared at the beginning of the component with `{#def arg1, arg2, ... #}`.

```html+jinja
{#def action, method="post", multipart=False #}

<form method="{{ method }}" action="{{ action }}"
  {%- if multipart %} enctype="multipart/form-data"{% endif %}
>
  {{ content }}
</form>
```

In this example, the component takes three arguments: "action", "method", and "multipart". The last two have default values, so they are optional, but the first one doesn't. That means it must be passed a value when rendering the component.

The syntax is exactly like how you declare the arguments of a Python function (in fact, it's parsed by the same code), so it can even include type comments, although they are not used by JinjaX (yet!).

```python
{#def
  data: dict[str, str],
  method: str = "post",
  multipart: bool = False
#}
...
```

## Passing Arguments

There are two types of arguments: strings and expressions.

### String

Strings are passed like regular HTML attributes:

```html+jinja
<Form action="/new" method="PATCH"> ... </Form>

<Alert message="Profile updated" />

<Card title="Hello world" type="big"> ... </Card>
```

### Expressions

There are two different but equivalent ways to pass non-string arguments:

"Jinja-like", where you use double curly braces instead of quotes:

```html+jinja title="Jinja-like"
<Example
    columns={{ 2 }}
    tabbed={{ False }}
    panels={{ {'one': 'lorem', 'two': 'ipsum'} }}
    class={{ 'bg-' + color }}
/>
```

... and "Vue-like", where you keep using quotes, but prefix the name of the attribute with a colon:

```html+jinja title="Vue-like"
<Example
    :columns="2"
    :tabbed="False"
    :panels="{'one': 'lorem', 'two': 'ipsum'}"
    :class="'bg-' + color"
/>
```

<Alert variant="info">
  For `True` values, you can just use the name, like in HTML:
  <br>
  ```html+jinja
  <Example class="green" hidden />
  ```
</Alert>

<Alert variant="info">
  You can also use dashes when passing an argument, but they will be translated to underscores:
  <br>
  ```html+jinja
  <Example aria-label="Hi" />
  ```
  <br>
  ```html+jinja title="Example.jinja"
  {#def aria_label = "" #}
  ...
  ```
</Alert>


## With Content

There is always an extra implicit argument: **the content** inside the component. Read more about it in the [next](/guide/slots) section.


## Extra Arguments

If you pass arguments not declared in a component, those are not discarded but rather collected in an `attrs` object.

You then call `attrs.render()` to render the received arguments as HTML attributes.

For example, this component:

```html+jinja title="Card.jinja"
{#def title #}
<div {{ attrs.render() }}>
  <h1>{{ title }}</h1>
  {{ content }}
</div>
```

Called as:

```html
<Card title="Products" class="mb-10" open>bla</Card>
```

Will be rendered as:

```html
<div class="mb-10" open>
  <h1>Products</h1>
  bla
</div>
```

You can add or remove arguments before rendering them using the other methods of the `attrs` object. For example:

```html+jinja
{#def title #}
{% do attrs.set(id="mycard") -%}

<div {{ attrs.render() }}>
  <h1>{{ title }}</h1>
  {{ content }}
</div>
```

Or directly in the `attrs.render()` call:

```html+jinja
{#def title #}

<div {{ attrs.render(id="mycard") }}>
  <h1>{{ title }}</h1>
  {{ content }}
</div>
```

<Alert variant="info">
The string values passed into components as attrs are not cast to `str` until their string representation is **actually** needed, for example when `attrs.render()` is invoked.
</Alert>

### `attrs` Methods

#### `.render(name=value, ...)`

Renders the attributes and properties as a string.

Any arguments you use with this function are merged with the existing
attributes/properties by the same rules as the `HTMLAttrs.set()` function:

- Pass a name and a value to set an attribute (e.g. `type="text"`)
- Use `True` as a value to set a property (e.g. `disabled`)
- Use `False` to remove an attribute or property
- The existing attribute/property is overwritten **except** if it is `class`.
  The new classes are appended to the old ones instead of replacing them.
- The underscores in the names will be translated automatically to dashes,
  so `aria_selected` becomes the attribute `aria-selected`.

To provide consistent output, the attributes and properties
are sorted by name and rendered like this:
`<sorted attributes> + <sorted properties>`.

```html+jinja
<Example class="ipsum" width="42" data-good />
```

```html+jinja
<div {{ attrs.render() }}>
<!-- <div class="ipsum" width="42" data-good> -->

<div {{ attrs.render(class="abc", data_good=False, tabindex=0) }}>
<!-- <div class="abc ipsum" width="42" tabindex="0"> -->
```

<Alert variant="warning">
Using `<Component {{ attrs.render() }}>` to pass the extra arguments to other components **WILL NOT WORK**. That is because the components are translated to macros before the page render.

You must pass them as the special argument `_attrs`.

```html+jinja
{#--- WRONG 😵 ---#}
<MyButton {{ attrs.render() }} />

{#--- GOOD 👍 ---#}
<MyButton _attrs={{ attrs }} />
<MyButton :_attrs="attrs" />
```
</Alert>

#### `.set(name=value, ...)`

Sets an attribute or property

- Pass a name and a value to set an attribute (e.g. `type="text"`)
- Use `True` as a value to set a property (e.g. `disabled`)
- Use `False` to remove an attribute or property
- If the attribute is "class", the new classes are appended to
  the old ones (if not repeated) instead of replacing them.
- The underscores in the names will be translated automatically to dashes,
  so `aria_selected` becomes the attribute `aria-selected`.

```html+jinja title="Adding attributes/properties"
{% do attrs.set(
  id="loremipsum",
  disabled=True,
  data_test="foobar",
  class="m-2 p-4",
) %}
```

```html+jinja title="Removing attributes/properties"
{% do attrs.set(
  title=False,
  disabled=False,
  data_test=False,
  class=False,
) %}
```

#### `.setdefault(name=value, ...)`

Adds an attribute, but only if it's not already present.

The underscores in the names will be translated automatically to dashes, so `aria_selected`
becomes the attribute `aria-selected`.

```html+jinja
{% do attrs.setdefault(
    aria_label="Products"
) %}
```

#### `.add_class(name1, name2, ...)`

Adds one or more classes to the list of classes, if not already present.

```html+jinja
{% do attrs.add_class("hidden") %}
{% do attrs.add_class("active", "animated") %}
```

#### `.remove_class(name1, name2, ...)`

Removes one or more classes from the list of classes.

```html+jinja
{% do attrs.remove_class("hidden") %}
{% do attrs.remove_class("active", "animated") %}
```

#### `.get(name, default=None)`

Returns the value of the attribute or property,
or the default value if it doesn't exist.

```html+jinja
{%- set role = attrs.get("role", "tab") %}
```


## Organizing your components

There are two ways to organize your components to your liking: using subfolders and/or adding multiple component folders.

### Using subfolders

To call components inside subfolders, you use a dot after each subfolder name. For example,
to call a `Button.jinja` component inside a `form` subfolder, you use the name:

```html+jinja
<form.Button> ... </form.Button>
```

If the component is inside a sub-subfolder, for instance `product/items/Header.jinja`, you use a dot for each subfolder:

```html+jinja
<product.items.Header> ... </product.items.Header>
```

### Adding multiple separate folders

Adding multiple separate folders makes JinjaX search for a component in each folder, in order, until it finds it. This means that even if different folders have components with the same name, the component found first will be used.

For example, imagine that you add these three folders:

```
A/
├── Alert.jinja
└── common
    └── Error.jinja

whatever/B/
├── Alert.jinja
└── form
    └── Error.jinja
└── common
    └── Welcome.jinja

C/
├── Alert.jinja
├── Header.jinja
└── common
    └── Error.jinja
    └── Welcome.jinja
```

```python
catalog.add_folder("A")
catalog.add_folder("whatever/B")
catalog.add_folder("C")
```

- Even though there is an `Alert.jinja` in all three folders, it will be loaded from "A",
  because that folder was added first.
- `common.Error` will also be loaded from "A", but `form.Error` will be loaded from "B",
  because the subfolder is part of the component's name.
- `common.Welcome` will be loaded from "B" and `Header` from "C", because that's where
  they will be found first.
- Finally, using `common.Header` will raise an error, because there is no component under
  that name.

### Third-party components libraries

You can also add a folder of components from an installed library. For example:

```python
import jinjax_ui
...
catalog.add_folder(jinjax_ui.components_path)
```

In order for this to work, the path given by the library should be absolute.

### Prefixes

The `add_folder()` method takes an optional `prefix` argument.

The prefix acts like a namespace. For example, the name of a
`Card.jinja` component is, by default, "Card", but under
the prefix "common", it becomes "common.Card".

The rule for subfolders remains the same: a `wrappers/Card.jinja`
name is, by default, "wrappers.Card", but under the prefix "common", it becomes
"common.wrappers.Card".

An important caveat is that when a component under a prefix calls another
component without a prefix, the called component is searched **first**
under the caller's prefix and then under the empty prefix. This allows third-party
component libraries to call their own components without knowing under what prefix
your app is using them.

<Alert variant="warning">
The prefixes take precedence over subfolders, so don't create a subfolder with
the same name as a prefix because it will be ignored.
</Alert>

If **under the same prefix** there is more than one component with the same name
in multiple added folders, the one in the folder added **first** takes precedence.
You can use this to override components loaded from a library by simply adding your folder first.
