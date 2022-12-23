# Agregando CSS y JS

Tus componentes pueden necesitar estilos propios o JavaScript por muchas razones. En vez de usar estilos o scripts globales a todo el sitio, escribir CSS/JS para cada componente individual tiene muchas ventajas:

- **Portabilidad**: Puedes copiar un componente, de un proyecto a otro, sabiendo que seguirá funcionando como debe.
- **Rendimiento**: En cada página solo carga el CSS/JS que necesitas. Además, el navegador habrá guardado en caché los recursos de los componentes que ya hayas usado en otras páginas, así que no tendrá que cargarlos de nuevo.
- **Pruebas más simple**: Puedes probar el JavaScript de un componente independientemente de los otros.


## Declarando CSS/JS

El CSS y/o el JS de un componente deben ser declarados en la metadata de la cabecera usando `{#css ... #}` y `{#js ... #}`

```html+jinja
{#css lorem.css ipsum.css #}
{#js foo.js bar.js #}
```

Ambas listas son opcionales.
Las rutas deben ser relativas a la raíz del folder de componentes (e.g.: `components/`).


## Incluyendo los CSS/JS en tu página

El catálogo recogerá todas las rutas de los archivos CSS y JS de los componentes usados en una página en las listas `catalog.collected_css` y `catalog.collected_js`.

Por ejemplo, despues de renderizar este componente:

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

Suponiendo que los componentes `Card`, y `Button` declaren recursos CSS, este será el estado de la lista `collected_css`:

```py
catalog.collected_css
['mypage.css', 'card.css', 'button.css']
```

Puedes agregar etiquetas `<link>` y `<script>` en tu página automáticamente, imprimiendo la variable global implícita `components_assets` en tu componente base, así:

```html+jinja title="components/Layout.jinja" hl_lines="7"
{#def title #}

<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<title>{{ title }}</title>
	{{ components_assets }}
</head>
<body>
	{{ content }}
</body>
</html>
```

Esa variable se renderizará como:

```html
<link rel="stylesheet" href="/static/components/mypage.css">
<link rel="stylesheet" href="/static/components/card.css">
<link rel="stylesheet" href="/static/components/button.css">
<script src="/static/components/mypage.js" defer></script>
<script src="/static/components/card.js" defer></script>
<script src="/static/components/button.js" defer></script>
```

## Middleware

Las etiquetas `<link>` y `<script>` de arriba no servirán de nada si tu aplicación no puede servir esos archivos, y no puede hacerlo aún.

Por esa razón, JinjaX incluye un middleware WSGI que procesará URLs como esas y devolverá los archivos correctos, si lo agregas a tu aplicación.

```py hl_lines="16-19"
from flask import Flask
from jinjax import Catalog

app = Flask(__name__)

# Aquí agregamos las variables globales, filtros, etc. de
# las plantillas de Flask, como por ejemplo `url_for()`
catalog = jinjax.Catalog(
    globals=app.jinja_env.globals,
    filters=app.jinja_env.filters,
    tests=app.jinja_env.tests,
    extensions=app.jinja_env.extensions,
)
catalog.add_folder("myapp/components")

app.wsgi_app = catalog.get_middleware(
    app.wsgi_app,
    autorefresh=app.debug,
)
```
El middleware usa la "probada en batalla" [librería Whitenoise](http://whitenoise.evans.io/) y solo devolverá archivos *.css* y/o *.js* dentro de el(los) folder(s) de los componentes (puedes configurarlo para que también devuelva archivos con otras extensiones).


## Buenas prácticas

### Alcance del CSS

Los estilos no se auto-limitarán a tu componente. Esto significa que podrían afectar a otros componentes y, a la inversa, ser afectados por estilos globales o de otros componentes.

Para protegerte de esto, *siempre* usa una clase única en la(s) etiqueta(s) raíz del componente y úsala para limitar el resto de los estilos.

Ejemplo:

```html+jinja title="components/Card.jinja"
{#css card.css #}

{% do attrs.add_class("Card") -%}
<div {{ attrs.render() }}>
  <h1>My Card</h1>
  ...
</div>
```

```css title="components/card.css"
/* 🚫 NO HAGAS ESTO */
h1 { font-size: 2em; }
h2 { font-size: 1.5em; }
a { color: blue; }

/* 👍 HAZ ESTO en vez */
.Card h1 { font-size: 2em; }
.Card h2 { font-size: 1.5em; }
.Card a { color: blue; }

```

Siempre usa una clase en vez de un `id`, o el componente no podrá ser usado más de una vez en una misma página.


### Eventos de JavaScript

Tus componentes podrían ser insertados al vuelo en la página, después de que el JavaScript haya sido cargado y ejecutado. Por eso, conectar eventos a los elementos al cargar la página no será suficiente:

```js title="components/card.js"
// Esto fallará para cualquier <Card> insertado después
document.querySelectorAll('.Card button.share')
  .forEach( (node) => {
    node.addEventListener("click", handleClick)
  })

/* ... etc. ... */
```

Una alternativa puede ser usar el API JavaScript `MutationObserver` para detectar cambios en el documento y conectar eventos a los nuevos componentes insertados:

```js title="components/card.js"
new MutationObserver( (mutationList) => {
  mutationList.forEach( (mutation) => {
    if (mutation.type !== "childList") return
    mutation.addedNodes.forEach( (node) => {
      if (node.nodeType === 1) {
        addEvents(node)
      }
    })
  })
})
.observe(document.body, {
    subtree: true,
    childList: true,
    attributes: false,
    characterData: false
})

function addEvents (root) {
  /* Agrega eventos a todos los elementos hijos de los nuevos
  elementos insertados */
  root.querySelectorAll('.Card button.share')
    .forEach( (node) => {
      node.addEventListener("click", handleClick)
    })
}

// Una primera llamada para conectar los eventos a los componentes
// presentes en la página cuando carga
addEvents(document)

/* ... etc ... */
```
