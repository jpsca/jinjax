---
title: Extra Arguments
description: If you pass arguments not declared in a component, those are not discarded, but rather collected in a `attrs` object that can render these extra arguments calling `attrs.render()`
---

<Header title="Extra Arguments">
If you pass arguments not declared in a component, those are not discarded, but rather collected in a `attrs` object that can render these extra arguments calling `attrs.render()`
</Header>

For example, this component:

```html+jinja title="components/Card.jinja"
{#def title #}
<div {{ attrs.render() }}>
  <h1>{{ title }}</h1>
  {{ content }}
</div>
```

Called as:

```html+jinja
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

## `attrs` methods


### `.render(name=value, ...)`

Renders the current attributes and properties as a string.
Any attributes/properties you pass to this method, will be used to call `attrs.set(**kwargs)` before rendering.

- Pass a name and a value to set an attribute (e.g. `type="text"`)
- Use `True` as value to set a property (e.g. `disabled`)
- Use `False` to remove an attribute or property

The underscores in the names will be translated automatically to dashes, so `aria_selected`
becomes the attribute `aria-selected`.

The current attribute/property are overwritten **except** if is "class" or "classes".
In those cases, the new classes are appended to the old ones instead of replacing them.

To provide consistent output, the attributes and properties are sorted by name and rendered like this: `<sorted attributes> + <sorted properties>`.

```html+jinja
<button {{ attrs.render() }}>
  {{ content }}
</button>
```

<Callout type="warning">
Using `<Component {{ attrs.render() }}>` to pass the extra arguments to other components **WILL NOT WORK**. That is because the components are translated to macros before the page render.

You must pass them as the special argument `__attrs`.

```html+jinja
{#--- WRONG 😵 ---#}
<MyButton {{ attrs.render() }} />

{#--- GOOD 👍 ---#}
<MyButton :__attrs="attrs" />
```
</Callout>


### `.set(name=value, ...)`

Sets an attribute or property:

- Pass a name and a value to set an attribute (e.g. `type="text"`)
- Use `True` as value to set a property (e.g. `disabled`)
- Use `False` to remove an attribute or property

The underscores in the names will be translated automatically to dashes, so `aria_selected`
becomes the attribute `aria-selected`.

The current attribute/property are overwritten **except** if is "class" or "classes".
In those cases, the new classes are appended to the old ones instead of replacing them.


#### Adding attributes/properties

```html+jinja
{% do attrs.set(
  id="loremipsum",
  disabled=True,
  data_test="foobar",
  class="m-2 p-4",
) %}
```

#### Removing attributes/properties

```html+jinja
{% do attrs.set(
  title=False,
  disabled=False,
  data_test=False,
  class=False,
) %}
```


### `.setdefault(name=value, ...)`

Adds an attribute or sets a property, *but only if it's not already present*.
Doesn't work eith properties.

The underscores in the names will be translated automatically to dashes, so `aria_selected`
becomes the attribute `aria-selected`.

```html+jinja
{% do attrs.setdefault(
    aria_label="Products"
) %}
```


### `.remove_class(name1, name2, ...)`

Removes one or more classes from the list of classes.

```html+jinja
{% do attrs.remove_class("hidden") %}
{% do attrs.remove_class("active", "animated") %}
```


### `.get(name, default=None)`

Returns the value of the attribute or property, or the default value if it doesn't exists.

```html+jinja
{%- set role = attrs.get("role", "tab") %}
```

...
