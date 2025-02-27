---
title: Introduction
description: Unstyled, fully accessible UI components, to integrate with your projects.
---

<Header title="Introduction" section="UI components">
  Accessible UI components, to integrate with your projects.
</Header>

<div class="cd-cards not-prose">
  <a class="card" href="/ui/tabs">
    <h2>Tabs</h2>
    <img src="/static/img/ui-tabs.png" />
  </a>
  <a class="card" href="/ui/popover">
    <h2>Popover</h2>
    <img src="/static/img/ui-popover.png" />
  </a>
  <a class="card" href="/ui/menu">
    <h2>Menu</h2>
    <img src="/static/img/ui-menu.png" />
  </a>
  <a class="card" href="/ui/accordion">
    <h2>Accordion</h2>
    <img src="/static/img/ui-accordion.png" />
  </a>
  <a class="card" href="/ui/linkedlist">
    <h2>LinkedList</h2>
    <img src="/static/img/ui-linkedlist.png" />
  </a>
  <a class="card" href="/ui/reldate">
    <h2>RelDate</h2>
    <img src="/static/img/ui-reldate.png" />
  </a>
</div>


## How to use

1. Install the `jinjax-ui` python library doing

  ```bash
  pip install jinjax-ui
  ```

2. Add it to your *JinjaX* catalog:

  ```python
  import jinjax_ui

  catalog.add_folder(jinjax_ui.components_path, prefix="")
  ```

3. Use the UI components in your components/templates:

  ```html+jinja
  <Popover> ... </Popover>
  ```