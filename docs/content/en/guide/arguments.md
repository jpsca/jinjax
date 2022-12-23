# Component Arguments

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
<Form action="/new">...</Form>
<Form action="/new" method="PATCH">...</Form>
<Form multipart={False} action="/new">...</Form>
```

The values of the declared arguments can be used in the template as values with the same name.


## Non-string arguments

In the example above, both "action" and "method" are strings, but "multipart" is a boolean, so we cannot pass it like `multipart="false"`
because that will make it a string that evaluates as `True`, which is the opposite of what we want.

Instead, you must use curly brackets: `multipart={False}`, instead of quotes: `multipart="False"`.

<Callout>
  Using lowercase booleans (`true` or `false`) is also valid.
</Callout>

Between the brackets, you can use datetimes, objects, lists, or any Python expressions.

```html+jinja
{# A datetime value #}
<DateTime date={datetime_value} />

{# A query result #}
<Post post={post} />

{# In-place calculations #}
<FooBar number={2**10} />

{# A list #}
<FooBar items={[1,2,3,4]} />
```


## Components with content

So far we have seen self-closing components, but there is another, much more useful type: components that wrap other HTML content and/or other components.

```html+jinja
{# Self-closing component #}
<Name arguments />

{# Component with content #}
<Name arguments> ...content here... </Name>
```

A great use case is to make layout components:

```html+jinja title="components/PageLayout.jinja"
{#def title #}

<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<title>{{ title }}</title>
</head>
<body>
{{ content }}
</body>
```

```html+jinja title="components/ArchivePage.jinja"
{#def posts #}

<PageLayout title="Archive">
  {% for post in posts %}
  <Post post={post} />
  {% endfor %}
</PageLayout>
```

Everything between the open and close tags of the components will be rendered and passed to the `PageLayout` component as a special, implicit, `content` variable.

To test a component in isolation, you can also manually send a content argument using the special `__content` argument:

```python
catalog.render("PageLayout", title="Hello world", __content="TEST")
```

## Extra arguments

If you pass arguments not declared in a component, those are not discarded, but rather collected in a `attrs` object. Read more about it in the next section.
