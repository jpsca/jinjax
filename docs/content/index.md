---
title: Super components powers for your Jinja templates
---

<section class="hero">
  <h1>JinjaX</h1>
  <h2>
    Super
    <span class="g1">components powers</span>
    for your
    <span class="g2">Jinja&nbsp;templates</span>
  </h2>
</section>

:::: div code
::: div panel
<h2>Before: chaos!</h2>

```html+jinja
{% extends "layout.html" %}
{% block title %}My title{% endblock %}

{% from "bunch_of_macros.html"
  import card_macro, another_macro %}

{% block content -%}
  <div>
    <h2>Hello {{ mistery or "World?" }}</h2>
    <div>
      {% call card_macro(div="So verbose") %}
        {% for product in products %}
          {{ another_macro(product) }}
        {% endfor %}
      {% endcall %}
    </div>
  </div>
  {% with items=products %}
    {% include "snippets/pagination.html" %}
  {% endwith %}
{%- endblock %}
```
:::

::: div panel
<h2>After: ✨ clarity ✨</h2>

```html+jinja
{#def products, msg="World!" #}

<Layout title="My title">
  <div>
    <h2>Hello, {{ msg }}</h2>
    <div>
      <Card div="So clean">
        {% for product in products %}
          <Product product={{ product }} />
        {% endfor %}
      </Card>
    </div>
  </div>
  <Paginator items={{ products }} />
</Layout>
```
:::
::::

<section class="features">
  <h2>Better than <code>include</code> and&nbsp;<code>macros</code></h2>
  <div class="cards">
    <article class="card">
      <div class="card-header">
        <h3>Encapsulated</h3>
        <img src="/assets/images/encapsulated.svg" width="32" height="32" alt="">
      </div>
      <div class="body">
        Link to their own <code>css</code> and/or <code>js</code> files
        and can be copy/pasted to other projects without&nbsp;modifications.
      </div>
    </article>
    <article class="card">
      <div class="card-header">
        <h3>Simple</h3>
        <img src="/assets/images/simple.svg" width="32" height="32" alt="">
      </div>
      <div class="body">
        Just regular Jinja files and no need to import&nbsp;them.
        Easier to use and easier to&nbsp;read.
      </div>
    </article>
    <article class="card">
      <div class="card-header">
        <h3>Modern</h3>
        <img src="/assets/images/modern.svg" width="32" height="32" alt="">
      </div>
      <div class="body">
        Components works great with
        <a href="https://htmx.org/" target="_blank">htmx</a>,
        <a href="https://tailwindcss.com/" target="_blank">TailwindCSS</a>,
        or&nbsp;<a href="https://hotwired.dev/" target="_blank">Hotwire</a>
      </div>
    </article>
    <article class="card">
      <div class="card-header">
        <h3>Composable</h3>
        <img src="/assets/images/composable.svg" width="32" height="32" alt="">
      </div>
      <div class="body">
        Can wrap content (HTML, other components, etc.) in a natural&nbsp;way.
      </div>
    </article>
  </div>
</section>

<section class="spaghetti">
  <div class="wrapper">
    <h2>Say goodbye to spaghetti&nbsp;templates</h2>
    <div class="text">
      <img src="/assets/images/spaghetti_code.png" alt="Spaghetti code">
      <p>Your Python code should be easy to understand and&nbsp;test.</p>
      <p><b>Template code, however, often fails even basic code standards</b>: long methods, deep conditional nesting, and mystery variables&nbsp;everywhere.</p>
      <p><b>But when it's built with components, you see</b> where everything is, understand what are the possible states of every piece of UI, and know exactly what data need to&nbsp;have.</p>
      <p>You can replace <b>all</b> your templates with components, or start with one&nbsp;section.</p>
    </div>
  </div>
</section>

<section class="engage">
  <div class="wrapper">
    <h3>Ready to get going? Engage!</h3>
    <a class="engage" href="/docs/">Get started <i>&rarr;</i></a>
    <div class="hint">Millions of people clicked a button in the last week alone!</div>
  </div>
</section>
