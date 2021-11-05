---
author: Nazmul Idris
date: 2021-11-05 14:00:00+00:00
excerpt: |
  This article is an advanced guide to using Ink v3.2.0 (with TypeScript and React) to create CLI apps.
  IDEA Ultimate / Webstorm project files are provided.
layout: post
title: "Advanced guide to Ink v3.2.0 (w/ React, Node.js and TypeScript)"
categories:
  - TypeScript
  - React
  - Web
  - Node.js
  - Server
  - CLI
---

<img class="post-hero-image" src="{{ 'assets/ink-intro.svg' | relative_url }}"/>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [What is Ink](#what-is-ink)
- [Build a CLI app using Ink and flexbox](#build-a-cli-app-using-ink-and-flexbox)
  - [Use Ink host components](#use-ink-host-components)
  - [Use flexbox styling](#use-flexbox-styling)
- [Exploration of all the UI components](#exploration-of-all-the-ui-components)
  - [Text](#text)
  - [Box](#box)
  - [Newline](#newline)
  - [Spacer](#spacer)
  - [Static](#static)
  - [Transform](#transform)
- [Exploration of all the React hooks](#exploration-of-all-the-react-hooks)
  - [useInput](#useinput)
  - [useApp](#useapp)
  - [useStdin](#usestdin)
  - [useStdout](#usestdout)
  - [useStderr](#usestderr)
  - [useFocus](#usefocus)
  - [useFocusManager](#usefocusmanager)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

---

## Introduction

This article is an advanced guide to using Ink v3.2.0 (with TypeScript and React) to create CLI
apps. IDEA Ultimate / Webstorm project files are provided.

To get started w/ Ink v3 please checkout this [introductory article][1.5].

> ### ⚠️ This isn't a reference for: React, Node.js, TypeScript, CSS
>
> Learn more about these topics on [developerlife.com][1.4]:
>
> | Resource                    | Notes                                                    |
> | --------------------------- | -------------------------------------------------------- |
> | [Node.js handbook][1.1]     | Learn Node.js w/ TypeScript                              |
> | [React Hooks handbook][1.2] | Learn React, Redux, and Testing w/ TypeScript            |
> | [CSS handbook][1.3]         | Learn CSS, grid, flexbox, to implement responsive design |

<!-- prettier-ignore-start -->

[1.1]: https://developerlife.com/2021/07/02/nodejs-typescript-handbook/
[1.2]: https://developerlife.com/2021/10/19/react-hooks-redux-typescript-handbook/
[1.3]: https://developerlife.com/2021/10/19/css-responsive-design-handbook/
[1.4]: https://developerlife.com/category/Web/
[1.5]: https://developerlife.com/2021/11/04/introduction-to-ink-v3/

<!-- prettier-ignore-end -->

---

## What is Ink

Ink is a React renderer written in TypeScript using the [`react-reconciler`][2.8] package. So
instead of rendering React components to the DOM Ink actually renders them to a terminal based UI.

With it, you can make CLI apps that look like this:

<img src="{{ 'assets/ink-demo.svg' | relative_url }}"/>

Ink supplies its own [host](#react-core-renderer-reconciler) UI components (eg: `<Text>`) which has
nothing to do w/ [react-dom][2.2] host components that come out of the box (eg: `<img>`) w/ React.

Ink supplied host UI components are rendered to a terminal based UI by using:

1. `console` streams to manipulate the [output to the console][2.1], and [input from the
   console][2.3].
2. [Yoga][2.4] to implement CSS flexbox layout and positioning. Yoga is written in C++ that allows
   flexbox layout itself to be implemented in various platforms (like [Lithio on Android][2.6],
   Node.js, .Net, etc).
3. You can take a look at the dependencies that Ink has in its [`package.json`][2.5]. It relies on
   packages like: `chalk`, `cli-boxes`, `cli-cursor`, `yoga-layout-prebuilt`, `react-reconciler`,
   `react-devtools-core`.

---

## Build a CLI app using Ink and flexbox

The previous sections have all been about the mechanics of setting up an Ink CLI app, and
understanding executable modules in Node.js. Now we can get into Ink itself and the CLI apps we can
build w/ it.

There are 2 main TSX files we need to look at to get started.

1. `source/cli.tsx` - This uses `meow` to parse the command line arguments that may be passed to the
   CLI app. So if we want to change the arguments that the app takes, we have to change the `meow`
   configuration object in this file. The values that we pass via the command line are actually
   passed as props to the `App` component defined below.
2. `source/ui.tsx` - We use React and Ink host components in this file to define the `App` component
   which takes props that correspond to the values which are passed into the command line above.

### Use Ink host components

```yaml
🔥TODO:
  - Make some simple UI that uses functional components and hooks (maybe Redux)
```

### Use flexbox styling

```yaml
🔥TODO:
  - Use flexbox styling in this app
```

---

## Exploration of all the UI components

```yaml
🔥TODO:
  - Provide small working examples of each
```

### Text

### Box

### Newline

### Spacer

### Static

### Transform

---

## Exploration of all the React hooks

```yaml
🔥TODO:
  - Provide small working examples of each
```

### useInput

### useApp

### useStdin

### useStdout

### useStderr

### useFocus

### useFocusManager
