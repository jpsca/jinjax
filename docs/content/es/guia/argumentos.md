# Argumentos de componentes

A menudo, un componente toma uno o más argumentos para renderizar, podría ser una fecha, una lista de artículos o un texto.

Cada argumento debe ser declarado en la metadata (el comentario al principio) del componente con `{#def arguments #}`. La sintaxis es muy similar a la declaración de una función en python:

```html+jinja title="components/Form.jinja"
{#def action, method='post', multipart=False #}

<form method="{{ method }}" action="{{ action }}"
  {%- if multipart %} enctype="multipart/form-data"{% endif %}
>
  {{ content }}
</form>
```

En este ejemplo, el componente toma tres argumentos: "action", "method", y "multipart". Los últimos dos tienen un valor por defecto, de modo que son opcionales - no necesitas pasarlos para llamar al componente. El primer argumento no tiene un valor, asi que tienes que pasarle un valor cuando llames al componente.


Así que todas estas son formas válidas de usar este componente:

```html+jinja
<Form action="/new">...</Form>
<Form action="/new" method="PATCH">...</Form>
<Form multipart={False} action="/new">...</Form>
```

Los valores de los argumentos declarados pueden usarse en la plantilla como variables con el mismo nombre.


## Atributos que no son textos

En el ejemplo anterior, tanto "action" como "method" son cadenas de texto, pero "multipart" es un booleano. No podemos pasarlo como `multipart="false"` porque eso lo volveria un texto, que además evaluaría a verdadero, que es lo opuesto a lo que queremos.

En vez de eso, debemos usar llaves en vez de comillas(`nombre={ valor }` en vez de `nombre="valor"`).

Dentro de las llaves, puedes usar fechas, objetos, listas, o cualquier expresión de Python.

```html+jinja
{# Un valor de fecha #}
<DateTime date={datetime_value} />

{# Un objeto #}
<Post post={post} />

{# Cálculos al vuelo #}
<FooBar number={2**10} />

{# Una lista #}
<FooBar items={[1,2,3,4]} />
```


## Componentes con contenido

Hasta ahora, hemos visto componentes que terminan en `/>`, sin una etiqueta de cierre. Pero hay otro tipo, mucho más útil: componentes que envuelven otras etiquetas HTML y/o a otros componentes.


```html+jinja
{# Componente de cierre automático #}
<Name arguments />

{# Componente con contenido #}
<Name arguments> ...content here... </Name>
```

Un gran caso de uso es hacer componentes de base:

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
  <Post post={{ post }} />
  {% endfor %}
</PageLayout>
```

Todo entre las etiquetas inicial y de cierre del componente será renderizado y pasado al componente `PageLayout` en una variable implícita especial `content`.

Para probar un componente en aislamiento, puedes también definir manualmente el contenido con el argumento especial `__content`:

```python
catalog.render("PageLayout", title="Hello world", __content="TEST")
```

## Atributos extra

Si le pasas argumentos no declarados a un componentes, estos no son descartados, si no, en cambio, recogidos en un objeto `attrs`. Lee más acerca de esto en la siguiente sección.
