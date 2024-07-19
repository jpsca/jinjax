---
title: Components
description: All about declaring and using components.
---

<Header title="Components">
</Header>
## Declaring and Using Components

The components are simple text files that look like regular Jinja templates, with three requirements:

**First**, components must be placed inside a folder registered in the catalog or a subfolder of it.

```python
catalog.add_folder("myapp/components")
```

You can call that folder whatever you want, not just "components". You can also add more than one folder:

```python
catalog.add_folder("myapp/layouts")
catalog.add_folder("myapp/components")
```

If you end up having more than one component with the same name, the one in the first folder will take priority.

**Second**, they must have a ".jinja" extension. This also helps code editors automatically select the correct language syntax to highlight. However, you can configure it in the catalog.

**Third**, the component name must start with an uppercase letter. Why? This is how JinjaX differentiates a component from a regular HTML tag when using it. I recommend using PascalCase names, like Python classes.

The name of the file (minus the extension) is also how you call the component. For example, if the file is "components/PersonForm.jinja":

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

Notice how the folder name doesn't need to start with an uppercase if you don't want it to.

<a href="/static/img/anatomy-en.png" target="_blank">
  <img src="/static/img/anatomy-en.png" style="margin:0 auto;width:90%;max-width:35rem;">
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

<Callout type="note">
  For `True` values, you can just use the name, like in HTML:
  <br>
  ```html+jinja
  <Example class="green" hidden />
  ```
</Callout>

<Callout type="note">
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
</Callout>

## With Content

There is always an extra implicit argument: **the content** inside the component. This could be anything: text, HTML, and/or other components; but when the component receives it, it is already rendered to a string.

```html+jinja
{# Component with content #}
<Name _arguments_ > ...content here... </Name>

{# Self-closing component, `content` is an empty string #}
<Name _arguments_ />
```

A great use case of the `content` is to make layout components:

<ExampleTabs
  prefix="comp-layouts"
  :panels="{
    'ArchivePage.jinja': 'guide.CompArchive',
    'Layout.jinja': 'guide.CompLayout',
  }"
/>

Everything between the open and close tags of the components will be rendered and passed to the `Layout` component as an implicit `content` variable.

To test a component in isolation, you can also manually send a content argument using the special `__content` argument:

```python
catalog.render("PageLayout", title="Hello world", __content="TEST")
```

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

<Callout type="info">
The string values passed into components as attrs are not cast to `str` until the string representation is **actually** needed, for example when `attrs.render()` is invoked.
</Callout>

### `attrs` Methods

#### `.render(name=value, ...)`

Renders the attributes and properties as a string.

Any arguments you use with this function are merged with the existing
attibutes/properties by the same rules as the `HTMLAttrs.set()` function:

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

<Callout type="warning">
Using `<Component {{ attrs.render() }}>` to pass the extra arguments to other components **WILL NOT WORK**. That is because the components are translated to macros before the page render.

You must pass them as the special argument `__attrs`.

```html+jinja
{#--- WRONG 😵 ---#}
<MyButton {{ attrs.render() }} />

{#--- GOOD 👍 ---#}
<MyButton __attrs={{ attrs }} />
<MyButton :__attrs="attrs" />
```
</Callout>

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

...