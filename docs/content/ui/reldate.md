---
title: Relative date
description: A component to convert datetimes to relative dates strings, such as "a minute ago", "in 2 hours", "yesterday", "3 months ago", etc. using JavaScript's Intl.RelativeTimeFormat API.
---

<Header title="Relative date" section="UI components">
A component to convert datetimes to relative dates strings,
such as "a minute ago", "in 2 hours", "yesterday", "3 months ago",
etc. using JavaScript's <a class="link" href="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/RelativeTimeFormat" target="_blank">Intl.RelativeTimeFormat API</a>.
</Header>

*Some examples (as if the datetime was `June 20th, 2024 6:30pm`)*:

| Source      | Relative date
| ------------| --------------
| `<RelDate datetime="2024-01-01"/>` | <RelDate datetime="2024-01-01" now="2024-06-20T18:30"/>
| `<RelDate datetime="2024-06-19T18:30"/>` | <RelDate datetime="2024-06-19T18:30" now="2024-06-20T18:30"/>
| `<RelDate datetime="2024-06-20T14:00"/>` | <RelDate datetime="2024-06-20T14:00" now="2024-06-20T18:30"/>
| `<RelDate datetime="2024-06-21T14:00"/>` | <RelDate datetime="2024-06-21T14:00" now="2024-06-20T18:30"/>
| `<RelDate datetime="2024-06-30T10:00"/>` | <RelDate datetime="2024-06-30T10:00" now="2024-06-20T18:30"/>
| `<RelDate datetime="1992-10-01"/>` | <RelDate datetime="1992-10-01" now="2024-06-20T18:30"/>


## How it works

The `RelDate` component is rendered as an empty `<time datetme="..." data-relative>` tag and, when the page load, the datetime is rendered by JavaScript.

There is also a `MutationObserver` in place to render the datetime on any `<time datetme="..." data-relative>` inserted later to the page by JavaScript.


## Localization

The locale used for the localization of the dates is, in order of priority:

1. The optional `lang` attribute of the component; or
2. The `lang` attribute of the `<body>` tag

Both can be a comma-separated lists of locales (e.g.: `"en-US,en-UK,en`). If none of these attributes exists, or if the locales are not supported by the browser, it fallsback to the default browser language.

*Some examples (as if the datetime was `June 20th, 2024 6:30pm`)*:

| Source      | Relative date
| ------------| --------------
| `<RelDate datetime="2024-01-01" lang="it"/>` | <RelDate datetime="2024-01-01" now="2024-06-20T18:30" lang="it"/>
| `<RelDate datetime="2024-06-19T18:30" lang="fr"/>` | <RelDate datetime="2024-06-19T18:30" now="2024-06-20T18:30" lang="fr"/>
| `<RelDate datetime="2024-06-21T14:00" lang="es"/>` | <RelDate datetime="2024-06-21T14:00" now="2024-06-20T18:30" lang="es"/>
| `<RelDate datetime="2024-06-21T14:00" lang="es-PE,es-ES,es"/>` | <RelDate datetime="2024-06-21T14:00" now="2024-06-20T18:30" lang="es"/>


## Component arguments

## RelDate

| Argument   | Type  | Description
| -----------| ----- | --------------
| `datetime` | `str` | Required.
| `lang`     | `str` | Optional comma-separated list of locales to use for formatting. If not defined, the attribute `lang` of the `<body>` tag will be used. If that is also not defined, or none of the locales are supported by the browser, the default browser language is used
| `now`      | `str` | Optional ISO-formatted date to use as the "present time". Useful for testing.
