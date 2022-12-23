---
title: JinjaX
component: PageHome
---
<section class="p-7 max-w-3xl mx-auto text-[3rem] leading-tight flex flex-start">
  <img src="/static/img/logo.svg" width="80" height="80" class="h-20 w-20 inline-block">
  <div class="pl-4"><b>JinjaX</b> is a server-side component system to replace your old templates</div>
</section>

<section class="p-7 max-w-5xl mx-auto mb-10 md:flex md:items-stretch">
  <div class="md:w-1/2 pr-2">
    <h2 class="text-2xl bold mb-5 text-center">
      From <span class="inline-block font-['Comic_Sans_MS'] -rotate-3 tracking-tighter pr-1">chaos</span>...
    </h2>

		<div
			markdown="1"
			class="h-full max-h-[470px] [&_.highlight]:h-full [&_pre]:h-full [&_code]:h-full text-sm"
		>
		```html+jinja
		{% extends "layout.html" %}
		{% block title %}My pasta tracker{% endblock %}
		{% from "button.html" import button_macro %}
		{% macro render_pasta(kind) -%}
		<tr>
			<td>
				<a href="...">
					{{ kind.name }}
					<i class="fa fa-pencil ml-2"></i>
				</a>
			</td>
			<td>{{ kind.origin }}</td>
			<td>
				<time datetime="{{ kind.created_at }}">
					{{ kind.created_at | format_date }}
				</time>
			</td>
			<td>
				<form action="" method="post">
					<input type="hidden" name="_csrf_token"
						value="{{ csrf_token() }}">
					<input name="method" value="delete">
					<button type="submit">Delete</button>
				</form>
			</td>
		</tr>
		{% endmacro %}

		{% block content -%}
		<div>
			<h2>Kinds of pasta</h2>
			<div>
				{% call button_macro(
					tag="a",
					href=url_for('pasta.new')
				) %}Add kind of pasta
				{% endcall %}
			</div>
		</div>
		<table>
		{% for kind in pasta %}
			{{ render_pasta(pasta) }}
		{% endfor %}
		</table>
		{% with paginator=pasta %}
		{% include "snippets/pagination.html" %}
		{% endwith %}
		{%- endblock %}
		```
		</div>
  </div>

  <div class="md:w-1/2 pl-2">
    <h2 class="text-2xl bold mb-5 text-center">
      ... to <span class="font-light [text-shadow:rgba(56,189,248,0.5)_1px_0_1px]">clarity</span>
    </h2>
     {% ui_TabGroup %}
			{% CodeTabs %}
      	{% CodeTab target="home-pasta-1", active=True %}PastaIndex.jinja{% endCodeTab %}
			{% endCodeTabs %}
      {% ui_TabPanel id="home-pasta-1" %}
				<div
					markdown="1"
					class="h-full max-h-[470px] [&_.highlight]:h-full [&_pre]:h-full [&_code]:h-full text-sm mt-0"
				>
					```html+jinja
					<Layout title="My pasta tracker">
						<header>
							<h2>Kinds of pasta</h2>
							<div>
								<Button tag="a" href={url_for('pasta.new')}>
									Add kind of pasta
								</Button>
							</div>
						</header>

						<table>
						{% for kind in pasta %}
							<Pasta kind={kind} />
						{% endfor %}
						</table>

						<Paginator items={pasta} />
					<Layout>
					```
				</div>
    	{% endui_TabPanel %}
		{% endui_TabGroup %}
  </div>
</section>

<section class="p-7 max-w-4xl mx-auto mb-10">
  <h2 class="text-4xl font-extrabold mb-5 text-center">
    Better than <code>include</code> and <code>macros</code>
  </h2>
  <ul class="list-disc [&_li]:py-1 [&_b]:bold [&_b]:text-[1.4rem]">
    <li><b>Simple:</b>
      easier to read and use because they look like regular HTML.
    <li>
      <b>Practical:</b>
      just regular Jinja files and no need to import them.
    <li>
      <b>Composable:</b>
      can wrap content (HTML, other components, etc.) in a natural way.
    <li>
      <b>Encapsulated:</b>
      can link to their own <i>css</i> or <i>js</i> files and be copy/pasted to other projects with no modifications.
  </ul>
</section>

<section class="p-7 max-w-4xl mx-auto mb-10">
  <h2 class="text-4xl font-extrabold mb-5 text-center">Say goodbye to spaghetti templates</h2>
  <div>
    <p class="mb-4">
      We want our Python code to be easy to understand and test.
    </p>
    <p class="mb-4">
      <b>Template code, however, often fails even basic code standards</b>: long methods, deep conditional nesting, and mystery variables everywhere.
    </p>
    <p class="mb-4">
      <b>But when it's built with components, you see</b> where everything is, understand what are the possible states of every piece of UI, and know exactly what data need to have.
    </p>
    <p class="mb-4">
      You can replace <b>all</b> your templates with components, or start with one section.
    </p>
  </div>
</section>

<section class="bg-zinc-200 dark:bg-zinc-900 py-10">
  <div class="p-7 max-w-4xl mx-auto text-center mb-10">
    <h3 class="text-4xl font-extrabold mb-5 text-center">
      Ready to get going? Engage
    </h3>
    <Button tag="a" href="/guide/" class="bl4ck bold mb-5 text-center mx-auto">See the Documentation</Button>
    <div class="text-xs">Millions of people clicked a button in the last week alone!</div>
  </div>
</section>
