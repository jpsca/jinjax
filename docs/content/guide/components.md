---
title: Components
description: The components are `.jinja` files with snippets of template code. They look like a fragment of a regular Jinja template – and they could be – except for the optional special comments at the beginning of the file.
---

<Header title="Components">
The components are `.jinja` files with snippets of template code.
They look like a fragment of a regular Jinja template – and they could be – except for the optional special comments at the beginning of the file.
</Header>

<a href="" target="_blank">
  <img src="/static/img/anatomy-en.png" style="margin:0 auto;width:100%;max-width:40rem;">
</a>


## Component Arguments

More often than not, a component takes one or more arguments to render. Every argument must be declared at the beginning of the component with `{#def arguments #}`. The syntax is very similar to how you declare the arguments of a python function:

```html+jinja title="components/Form.jinja"
{#def action, method='post', multipart=False #}

<form method="{{ method }}" action="{{ action }}"
  {%- if multipart %} enctype="multipart/form-data"{% endif %}
>
  {{ content }}
</form>
```

In this example, the component takes three arguments: "action", "method", and "multipart". The last two have a default value, so they are optional, but the first one doesn't. That means it must be passed a value when rendering the component.

So all of these are valid forms to use this component:

```html+jinja
<Form action="/new"> ... </Form>
<Form action="/new" method="PATCH"> ... </Form>
<Form :multipart="False" action="/new"> ... </Form>
```

The values of the declared arguments can be used in the template as values with the same name.


### Components with content

There is actually always an extra implicit argument: the content inside the component. This could be anything: text, HTML, and/or other components; but the component recieves it already rendered to a string.

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

Everything between the open and close tags of the components will be rendered and passed to the `Layout` component as a implicit, `content` variable.

To test a component in isolation, you can also manually send a content argument using the special `__content` argument:

```python
catalog.render("PageLayout", title="Hello world", __content="TEST")
```

### Extra arguments

If you pass arguments not declared in a component, those are not discarded, but rather collected in a `attrs` object. Read more about it in the next section.
