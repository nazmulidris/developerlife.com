---
author: Nazmul Idris
date: 2021-11-25 14:00:00+00:00
excerpt: |
  This article is reference handbook for using Ink v3.2.0 (with TypeScript and React) components
  to create CLI apps.
  IDEA Ultimate / Webstorm project files are provided.
layout: post
title: "Reference handbook for using Ink v3.2.0 components (w/ React, Node.js and TypeScript)"
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
- [Examples from the ink repo](#examples-from-the-ink-repo)
- [Small example #1](#small-example-1)
- [Medium size example #2](#medium-size-example-2)
- [Large example #3](#large-example-3)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

---

## Introduction

This article is reference handbook for using Ink v3.2.0 (with TypeScript and React) components to
create CLI apps. IDEA Ultimate / Webstorm project files are provided.

To get started w/ Ink v3 please check out this [introductory article][0.1] and this [advanced
article][0.6].

> ### ⚠️ This isn't a reference for React, Node.js, TypeScript, or CSS
>
> Learn more about these topics on [developerlife.com][0.2]:
>
> | Resource                    | Notes                                                    |
> | --------------------------- | -------------------------------------------------------- |
> | [Node.js handbook][0.3]     | Learn Node.js w/ TypeScript                              |
> | [React Hooks handbook][0.4] | Learn React, Redux, and Testing w/ TypeScript            |
> | [CSS handbook][0.5]         | Learn CSS, grid, flexbox, to implement responsive design |

<!-- prettier-ignore-start -->

[0.1]: https://developerlife.com/2021/11/04/introduction-to-ink-v3/
[0.2]: https://developerlife.com/category/Web/
[0.3]: https://developerlife.com/2021/07/02/nodejs-typescript-handbook/
[0.4]: https://developerlife.com/2021/10/19/react-hooks-redux-typescript-handbook/
[0.5]: https://developerlife.com/2021/10/19/css-responsive-design-handbook/
[0.6]: https://developerlife.com/2021/11/05/ink-v3-advanced/

<!-- prettier-ignore-end -->

---

## What is Ink

Ink is a React renderer written in TypeScript using the [`react-reconciler`][2.8] package. So
instead of rendering React components to the DOM Ink actually renders them to a terminal based UI.

With it, you can make CLI apps that look like this:

<img src="{{ 'assets/ink-demo.svg' | relative_url }}"/>

Ink supplies its own [host][1.5] UI components (eg: `<Text>`) which has nothing to do w/
[react-dom][2.2] host components that come out of the box (eg: `<img>`) w/ React.

Ink supplied host UI components are rendered to a terminal based UI by using:

1. `console` streams to manipulate the [output to the console][2.1], and [input from the
   console][2.3].
2. [Yoga][2.4] to implement CSS flexbox layout and positioning. Yoga is written in C++ that allows
   flexbox layout itself to be implemented in various platforms (like [Lithio on Android][2.6],
   Node.js, .Net, etc).
3. You can take a look at the dependencies that Ink has in its [`package.json`][2.5]. It relies on
   packages like: `chalk`, `cli-boxes`, `cli-cursor`, `yoga-layout-prebuilt`, `react-reconciler`,
   `react-devtools-core`.

<!-- prettier-ignore-start -->

[1.1]: https://developerlife.com/2021/07/02/nodejs-typescript-handbook/
[1.2]: https://developerlife.com/2021/10/19/react-hooks-redux-typescript-handbook/
[1.3]: https://developerlife.com/2021/10/19/css-responsive-design-handbook/
[1.4]: https://developerlife.com/category/Web/
[1.5]: https://developerlife.com/2021/11/04/introduction-to-ink-v3/#react-core-renderer-reconciler
[1.6]: https://github.com/nazmulidris/ts-ink-template/blob/main/README.md
[1.7]: https://github.com/nazmulidris/ts-ink-template/blob/main/README.md#npm-scripts

[2.1]: https://github.com/r3bl-org/r3bl-ts-utils/blob/3251cdf13f029da641c9e467dad513f9a27abc47/src/color-console-utils.ts#L99
[2.2]: https://github.com/facebook/react/tree/main/packages/react-dom
[2.3]: https://developerlife.com/2021/07/02/nodejs-typescript-handbook/#user-input-and-output-via-stdin-stdout
[2.4]: https://github.com/facebook/yoga
[2.5]: https://github.com/vadimdemedes/ink/blob/master/package.json
[2.6]: https://github.com/facebook/litho
[2.7]: https://youtu.be/CGpMlWVcHok
[2.8]: https://github.com/facebook/react/tree/master/packages/react-reconciler
[2.10]: https://blog.atulr.com/react-custom-renderer-1/
[2.11]: https://facebook.github.io/react-native/
[2.12]: https://github.com/Flipboard/react-canvas
[2.13]: https://github.com/diegomura/react-pdf
[2.14]: https://github.com/nitin42/redocx
[2.15]: https://github.com/iamdustan/react-hardware
[2.16]: https://youtu.be/ZCuYPiUIONs
[2.17]: https://giamir.com/what-is-react-fiber

<!-- prettier-ignore-end -->

---

## Examples from the ink repo

There are a wealth of examples that you can find in the
[ink repo](https://github.com/nazmulidris/ink/tree/master/examples) itself. I suggest browsing
through all of them to get some sense of how to use all the host components and hooks.

In this article, we will walk through three examples in order to get a sense of how to use the
entire API surface of Ink. There are a lot of community contributions in the form of npm packages
that are built using ink that we will not cover here. These examples will cover the following things
in ink.

1. Components
   1. `Text`
   2. `Box`
   3. `Border`
   4. `Newline`
2. Hooks
   1. `useInput`
   2. `useApp`
   3. `useStdin`
   4. `useFocus`
   5. `useFocusManager`

---

## Small example #1

---

## Medium size example #2

---

## Large example #3

---
