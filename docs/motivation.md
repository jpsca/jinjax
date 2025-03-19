---
title: Motivation
description: An overview of what JinjaX is about, and a glimpse into the decision-making process that led to its creation.
---

## Components are cool

Despite the complexity of a single-page application, some programmers claim React or Vue offer a better development experience than traditional server-side rendered templates. I believe this is mostly because of the greatest improvement React introduced to web development: components.

<small>
Components, *as a way to organize template code*. Reactivity is cool too, but unrelated to the main issue.
</small>

When writing Python, we aim for the code to be easy to understand and test. However, we often forget all of that when writing templates that don't even meet basic standards: long methods, deep conditional nesting, and mysterious variables everywhere.

Components are far superior to the HTML soup tag approach of server-side rendered templates. They clearly specify what arguments they accept and how they render. More importantly, components are modular: markup, logic, and relevant styles all in one package. You can easily copy and paste them between projects and share them with others.

This means a community has formed around sharing these components. Now you can easily find hundreds of ready-to-use components—some of them very polished—for every common UI widget, even the "complex" ones, like color-pickers. The big problem is that you can only use them with React (and Vue components with Vue, etc.) and in a single-page application.

JinjaX is about bringing that innovation back to server-side-rendered applications.

## Not quite there: Jinja macros

An underestimated feature of Jinja is *macros*. Jinja [macros](https://jinja.palletsprojects.com/en/3.0.x/templates/#macros) are template snippets that work like functions: They can have positional or keyword arguments, and when called return the rendered text inside.

```html+jinja
{% macro input(name, value="", type="text", size=20) -%}
  <input type="{{ type }}" name="{{ name }}"
    value="{{ value|e }}" size="{{ size }}">
{%- endmacro %}

{% macro button(type="button") -%}
  <button type="{{ type }}" class="btn-blue">
    {{ caller() }}
  </button>
{%- endmacro %}
```

You can then import the macro to your template to use it:

```html+jinja
{% from 'forms.html' import input, button %}

<p>{{ input("username") }}</p>
<p>{{ input("password", type="password") }}</p>
{% call button("submit") %}Submit{% endcall %}
```
You must use the `{% call x %}` syntax to pass child content to the macro—by using the `{{ caller() }}` function—otherwise you can simply call it as if it were a regular function.

So, can we use macros as components and call it a day? Well... no. This looks terrible:

```html+jinja
{% call Card(label="Hello") %}
  {% call MyButton(color="blue", shadowSize=2) %}
    {{ Icon(name="ok") }} Click Me
	{% endcall %}
{% endcall %}
```

compared to how you would write it with JSX:

```html
<Card label="Hello">
  <MyButton color="blue" shadowSize={2}>
    <Icon name="ok" /> Click Me
  </MyButton>
</Card>
```

But macros are *almost* there. They would be a great foundation if we could adjust the syntax just a little.

## Strong alternative: Mako

At some point, I considered dropping this idea and switching to [Mako](https://www.makotemplates.org/), a template library by Michael Bayer (of SQLAlchemy fame).

It's a hidden gem that doesn't get much attention because of network effects. See how close you can get with it:

```html+mako
<%def name="layout()">       # <--- A "macro"
    <div class="mainlayout">
        <div class="header">
            ${caller.header()}
        </div>

        <div class="sidebar">
            ${caller.sidebar()}
        </div>

        <div class="content">
            ${caller.body()}
        </div>
    </div>
</%def>

## calls the layout def           <--- Look! Python-style comments

<%self:layout>
    <%def name="header()">       # <--- This is like a "slot"!
        I am the header
    </%def>
    <%def name="sidebar()">
        <ul>
            <li>sidebar 1</li>
            <li>sidebar 2</li>
        </ul>
    </%def>
    this is the body
</%self:layout>
```

Mako also has `<% include %>`s with arguments, which is another way of doing components if you don't need to pass content.

However, in the end, the network effects, familiarity with Jinja, and perhaps a touch of not-invented-here syndrome tipped the scales toward writing a Jinja extension instead.
