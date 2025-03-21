---
title: Adding CSS and JS assets
description: Your components might need custom styles or custom JavaScript for many reasons.
---

Instead of using global stylesheets or script files, writing assets for each individual component has several advantages:

- **Portability**: You can copy a component from one project to another, knowing it will keep working as expected.
- **Performance**: Only load the CSS and JS that you need on each page. Additionally, the browser will have already cached the assets of the components for other pages that use them.
- **Simple testing**: You can test the JS of a component independently from others.

## Auto-loading assets

JinjaX searches for `.css` and `.js` files with the same name as your component in the same folder and automatically adds them to the list of assets included on the page. For example, if your component is `components/common/Form.jinja`, both `components/common/Form.css` and `components/common/Form.js` will be added to the list, but only if those files exist.

## Manually declaring assets

In addition to auto-loading assets, the CSS and/or JS of a component can be declared in the metadata header with `{#css ... #}` and `{#js ... #}`.

```html
{#css lorem.css, ipsum.css #}
{#js foo.js, bar.js #}
```

- The file paths must be relative to the root of your components catalog (e.g., `components/form.js`) or absolute (e.g., `http://example.com/styles.css`).
- Multiple assets must be separated by commas.
- Only **one** `{#css ... #}` and **one** `{#js ... #}` tag is allowed per component at most, but both are optional.

### Global assets

The best practice is to store both CSS and JS files of the component within the same folder. Doing this has several advantages, including easier component reuse in other projects, improved code readability, and simplified debugging.

However, there are instances when you may need to rely on global CSS or JS files, such as third-party libraries. In such cases, you can specify these dependencies in the component's metadata using URLs that start with either "/", "http://", or "https://".

When you do this, JinjaX will render them as is, instead of prepending them with the component's prefix like it normally does.

For example, this code:

```html+jinja
{#css foo.css, bar.css, /static/bootstrap.min.css #}
{#js http://example.com/cdn/moment.js, bar.js  #}

{{ catalog.render_assets() }}
```

will be rendered as this HTML output:

```html
<link rel="stylesheet" href="/static/components/foo.css">
<link rel="stylesheet" href="/static/components/bar.css">
<link rel="stylesheet" href="/static/bootstrap.min.css">
<script type="module" src="http://example.com/cdn/moment.js"></script>
<script type="module" src="/static/components/bar.js"></script>
```

## Including assets in your pages

The catalog will collect all CSS and JS file paths from the components used on a "page" and store them in the `catalog.collected_css` and `catalog.collected_js` lists.

For example, after rendering this component:

```html+jinja title="components/MyPage.jinja"
{#css mypage.css #}
{#js mypage.js #}

<Layout title="My page">
  <Card>
    <CardBody>
      <h1>Lizard</h1>
      <p>The Iguana is a type of lizard</p>
    </CardBody>
    <CardActions>
      <Button size="small">Share</Button>
    </CardActions>
  </Card>
</Layout>
```

Assuming the `Card` and `Button` components declare CSS assets, this will be the state of the `collected_css` list:

```py
catalog.collected_css
['mypage.css', 'card.css', 'button.css']
```

You can add the `<link>` and `<script>` tags to your page automatically by calling `catalog.render_assets()` like this:

```html+jinja title="components/Layout.jinja" hl_lines="8"
{#def title #}

<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<title>{{ title }}</title>
	{{ catalog.render_assets() }}
</head>
<body>
	{{ content }}
</body>
</html>
```

The variable will be rendered as:

```html
<link rel="stylesheet" href="/static/components/mypage.css">
<link rel="stylesheet" href="/static/components/card.css">
<link rel="stylesheet" href="/static/components/button.css">
<script type="module" src="/static/components/mypage.js"></script>
<script type="module" src="/static/components/card.js"></script>
<script type="module" src="/static/components/button.js"></script>
```

## Middleware

The tags above will not work if your application can't return the content of those files. Currently, it can't.

For that reason, JinjaX includes WSGI middleware that will process those URLs if you add it to your application.

**This is not needed if your components don't use static assets or if you serve them by other means.**

```py
from flask import Flask
from jinjax import Catalog

app = Flask(__name__)

# Here we add the Flask Jinja globals, filters, etc., like `url_for()`
catalog = jinjax.Catalog(jinja_env=app.jinja_env)

catalog.add_folder("myapp/components")

app.wsgi_app = catalog.get_middleware(
    app.wsgi_app,
    autorefresh=app.debug,
)
```

The middleware uses the battle-tested [Whitenoise library](http://whitenoise.evans.io/) and will only respond to the *.css* and *.js* files inside the component(s) folder(s).
You must install it first:

```bash
pip install jinjax[whitenoise]
```

Then, you can configure it to also return files with other extensions. For example:

```python
catalog.get_middleware(app, allowed_ext=[".css", ".js", ".svg", ".png"])
```

Be aware that if you use this option, `get_middleware()` must be called **after** all folders are added.

## Good practices

### CSS Scoping

The styles of your components will not be auto-scoped. This means the styles of a component can affect other components and likewise, they will be affected by global styles or the styles of other components.

To protect yourself against that, *always* add a custom class to the root element(s) of your component and use it to scope the rest of the component styles.

You can even use this syntax now supported by [all modern web browsers](https://caniuse.com/css-nesting):

```sass
.Parent {
  .foo { ... }
  .bar { ... }
}
```

The code above will be interpreted as

```css
.Parent .foo { ... }
.Parent .bar { ... }
```

Example:

```html+jinja title="components/Card.jinja"
{#css card.css #}

<div {{ attrs.render(class="Card") }}>
  <h1>My Card</h1>
  ...
</div>
```

```sass title="components/card.css"
/* 🚫 DO NOT do this */
h1 { font-size: 2em; }
h2 { font-size: 1.5em; }
a { color: blue; }

/* 👍 DO THIS instead */
.Card {
  & h1 { font-size: 2em; }
  & h2 { font-size: 1.5em; }
  & a { color: blue; }
}

/* 👍 Or this */
.Card h1 { font-size: 2em; }
.Card h2 { font-size: 1.5em; }
.Card a { color: blue; }
```

<Callout type="warning">
Always use a class **instead of** an `id`, or the component will not be usable more than once per page.
</Callout>

### JS events

Your components might be inserted in the page on-the-fly, after the JavaScript files have been loaded and executed. So, attaching events to the elements on the page on load will not be enough:

```js title="components/card.js"
// This will fail for any Card component inserted after page load
document.querySelectorAll('.Card button.share')
  .forEach((node) => {
    node.addEventListener("click", handleClick)
  })

/* ... etc ... */
```

A solution can be using event delegation:

```js title="components/card.js"
// This will work for any Card component inserted after page load
document.addEventListener("click", (event) => {
  if (event.target.matches(".Card button.share")) {
    handleClick(event)
  }
})
```
