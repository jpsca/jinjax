---
title: Tabs
description: Easily create accessible, fully customizable tab interfaces, with robust focus management and keyboard navigation support.
---

<Header title="Tabs" section="UI components">
  Easily create accessible, fully customizable tab interfaces, with robust focus management and keyboard navigation support.
</Header>

<ExampleTabs
  prefix="demo"
  panels={{ {
    'Result': 'ui.Tabs.DemoResult',
    'HTML': 'ui.Tabs.DemoHTML',
    'CSS': 'ui.Tabs.DemoCSS',
  } }}
/>

Tabs are built using the `TabGroup`, `TabList`, `Tab`, and `TabPanel` components. Clicking on any tab or selecting it with the keyboard will activate the corresponding panel.


## Styling states

| CSS selector     | Description
| ---------------  | --------------
| `.ui-hidden`     | Added to all `TabPanel` except the one that is active.
| `.ui-selected`   | Added to the selected `Tab`.
| `.ui-disabled`   | Added to disabled `Tab`s.


## Disabling a tab

To disable a tab, use the disabled attribute on the `Tab` component. Disabled tabs cannot be selected with the mouse, and are also skipped when navigating the tab list using the keyboard.

<Callout type="warning">
Disabling tabs might be confusing for users. Instead, I reccomend you either remove it or explain why there is no content for that tab when is selected.
</Callout>


## Manually activating tabs

By default, tabs are automatically selected as the user navigates through them using the arrow kbds.

If you'd rather not change the current tab until the user presses <kbd>Enter</kbd> or <kbd>Space</kbd>, use the `manual` attribute on the `TabGroup` component.

Remember to add styles to the `:focus` state of the tab so is clear to the user that the tab is focused.

<ExampleTabs
  prefix="manual"
  panels={{{
    'HTML': 'ui.Tabs.ManualHTML',
    'Result': 'ui.Tabs.ManualResult',
  } }}
/>

The manual prop has no impact on mouse interactions — tabs will still be selected as soon as they are clicked.


## Vertical tabs

If you've styled your `TabList` to appear vertically, use the `vertical` attribute to enable navigating with the <kbd title="arrow up">↑</kbd> and <kbd title="arrow down">↓</kbd> arrow kbds instead of <kbd title="arrow left">←</kbd> and <kbd title="arrow right">→</kbd>, and to update the `aria-orientation` attribute for assistive technologies.

<ExampleTabs
  prefix="vertical"
  panels={{ {
    'HTML': 'ui.Tabs.VerticalHTML',
    'Result': 'ui.Tabs.VerticalResult',
  } }}
/>


## Controlling the tabs with a `<select>`

Sometimes, you want to display a `<select>` element in addition to tabs. To do so, use the `TabSelect` and `TabOption` components.
A `TabSelect` component is a wrapper for a `<select>` element, and it accepts `TabOption` components as children.

Note that a `TabSelect` **is not a replacement for a `TabList`**. For accessibility the `TabList` must be remain in your code, even if it's visually hidden.

<ExampleTabs
  prefix="select"
  :panels="{
    'HTML': 'ui.Tabs.SelectHTML',
    'Result': 'ui.Tabs.SelectResult',
  }"
/>


## Component arguments

### TabGroup

| Argument    | Type     | Default    | Description
| ----------- | -------- | ---------- | --------------
| tag         | `str`    | `"div"`    | HTML tag used for rendering the wrapper.

### TabList

| Argument    | Type     | Default    | Description
| ----------- | -------- | ---------- | --------------
| vertical    | `bool`   | `false`    | Use the <kbd title="arrow up">↑</kbd> and <kbd title="arrow down">↓</kbd> arrow kbds to move between tabs instead of the defaults <kbd title="arrow left">←</kbd> and <kbd title="arrow right">→</kbd> arrow kbds.
| manual      | `bool`   | `false`    | If `true`, selecting a tab with the keyboard won't activate it, you must press <kbd>Enter</kbd> os <kbd>Space</kbd> kbds to do it.
| tag         | `str`    | `"nav"`    | HTML tag used for rendering the wrapper.


### Tab

| Argument    | Type     | Default    | Description
| ----------- | -------- | ---------- | --------------
| target      | `str`    |            | Required. HTML id of the panel associated with this tab.
| selected    | `bool`   | `false`    | Initially selected tab. Only one tab in the `TabList` can be selected at the time.
| disabled    | `bool`   | `false`    | If the tab can be selected.
| tag         | `str`    | `"button"` | HTML tag used for rendering the tab.

### TabPanel

| Argument    | Type     | Default    | Description
| ----------- | -------- | ---------- | --------------
| hidden      | `bool`   | `false`    | Initially hidden panel.
| tag         | `bool`   | `"div"`    | HTML tag used for rendering the panel.


### TabSelect

No arguments.


### TabOption

| Argument    | Type     | Default    | Description
| ----------- | -------- | ---------- | --------------
| target      | `str`    |            | Required. HTML id of the panel associated with this tab.
| disabled    | `bool`   | `false`    | Display the option but not allow to select it.


## Events

A tab emits a `jxui:tab:selected` event every time is selected. The event contains the `target` property with the tag node.

```js
document.addEventListener("jxui:tab:selected", (event) => {
  console.log(`'${event.target.textContent}' tab selected`);
});
```


## Accessibility notes

### Mouse interaction

Clicking a `Tab` will select that tab and display the corresponding `TabPanel`.

### Keyboard interaction

All interactions apply when a `Tab` component is focused.

| Command                                                                                           | Description
| -------------------------------------------------------------------------------------             | -----------
| <kbd title="arrow left">←</kbd> / <kbd title="arrow right">→</kbd> arrow kbds                     | Selects the previous/next non-disabled tab, cycling from last to first and vice versa.
| <kbd title="arrow up">↑</kbd> / <kbd title="arrow down">↓</kbd> arrow kbds when `vertical` is set | Selects the previous/next non-disabled tab, cycling from last to first and vice versa.
| <kbd>Enter</kbd> or <kbd>Space</kbd> when `manual` is set                                         | Activates the selected tab
| <kbd>Home</kbd> or <kbd>PageUp</kbd>                                                              | Activates the **first** tab
| <kbd>End</kbd> or <kbd>PageDown</kbd>                                                             | Activates the **last** tab
