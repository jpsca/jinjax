---
title: Menu (Dropdown)
description: Displays a list of options that a user can choose with robust support for keyboard navigation. Built using the Popover API.
---

<Header title="Menu" section="UI components">
  Displays a list of options that a user can choose with robust support for
  keyboard navigation. Built using the Popover API.
</Header>

<ExampleTabs
  prefix="menu-demo"
  :panels="{
    'Result': 'ui.Menu.DemoResult',
    'HTML': 'ui.Menu.DemoHTML',
    'CSS': 'ui.Menu.DemoCSS',
  }"
/>

**Note:** This component does not handle keyboard shortcuts, here are shown only as an example.

Menus are built using the `Menu`, `MenuButton`, `MenuItem`, and `MenuItemSub` components. Clicking on menu button or activating it with the keyboard will show the corresponding menu.

```html+jinja
<MenuButton>Open menu</<MenuButton>
<Menu>
  <MenuItem> item1 </MenuItem> 〈-- Regular item
  <MenuItem> item2 </MenuItem>
  <MenuItem> item3 </MenuItem>
  <MenuItemSub> item4 〈----------- An item with a submenu
    <Menu> ... </Menu>〈----------- Submenu
  </MenuItemSub>
</Menu>
```

A `Menu` starts hidden on page load by having `display:none` set on it (the Popover API does it automatically). To show/hide the menu, you need to add a `MenuButton`.

When a `Menu` is shown, it has `display:none` removed from it and it is put into the top layer so, unlike just using `position: absolute`, it's guaranteed that it will sit on top of all other page content.


## Anchor positioning

By default, the menu appears centered in the layout view, but this component allows you to  position it relative to an specific element in the page, using the `anchor` and `anchor-to` attributes.

`anchor` is the ID of the element used as a reference, and  `anchor-to` which side of the anchor to use: "top", "bottom", "right", or "left"; with an optional postfix of "start" or "end" ("center" is the default).

<p>
  <img src="/static/img/anchors.png" alt="Anchor positioning"
    width="595" height="324" style="display:block;margin:60px auto;" />
</p>

The positioning is done every time the menu opens, but you can trigger the re-position, for example, on windows resizing, by calling the `jxui-popover/setPosition(menu)` function.


## Styling states

| CSS selector            | Description
| ----------------------- | --------------
| `.ui-menu`              | Every menu has this class
| `.ui-menu:popover-open` | This pseudo-class matches only menus that are currently being shown
| `::backdrop`            | This pseudo-element is a full-screen element placed directly behind showing menu elements in the top layer, allowing effects to be added to the page content behind the menu(s) if desired. You might for example want to blur out the content behind the menu to help focus the user's attention on it

To animate a menu, follow the [Animating popovers section](/headless/popover#animating-popovers) in the Popover page.


## Component arguments

### MenuButton

| Argument        | Type      | Default    | Description
| --------------- | --------- | ---------- | --------------
| `target`        | `str`     |            | Required. The ID of the linked `Popover` component.
| `action`        | `str`     | `"toggle"` | `"open"`, `"close"`, or `"toggle"`.
| `tag`           | `str`     | `"button"` | HTML tag of the component.

### Menu

| Argument     | Type  | Default  | Description
| ------------ | ----- | -------- | --------------
| `mode`       | `str` | `"auto"` | `"auto"` or `"manual"`.
| `anchor`     | `str` |          | ID of the element used as an anchor
| `anchor-to`  | `str` |          | Which side/position of the anchor to use: "**top**", "**bottom**", "**right**", or "**left**"; with an optional postfix of "**start**", "**end**", "**center**".
| `tag`        | `str` | `"div"`  | HTML tag of the component.

### MenuItem

| Argument     | Type  | Default  | Description
| ------------ | ----- | -------- | --------------
| `mode`       | `str` | `"auto"` | `"auto"` or `"manual"`.

### MenuSubItem

| Argument     | Type  | Default  | Description
| ------------ | ----- | -------- | --------------
| `mode`       | `str` | `"auto"` | `"auto"` or `"manual"`.


## Accessibility notes

### Mouse interaction

- Clicking a `PopButton` will trigger the button action (open, close, or toggle state).

- Clicking outside of a `Popover` will close *all* the `Popover` with `mode="auto"`.


### Keyboard interaction

- Pressing the <kbd>Enter</kbd> or <kbd>Space</kbd> keys on a `PopButton` will trigger
the button action (open, close, or toggle state), and close *all* the `Popover` with `mode="auto"`.

- Pressing the <kbd>Escape</kbd> key will close *all* the `Popover` with `mode="auto"`.
