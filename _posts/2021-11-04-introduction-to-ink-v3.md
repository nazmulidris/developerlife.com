---
author: Nazmul Idris
date: 2021-11-04 14:00:00+00:00
excerpt: |
  This article is an introduction to using Ink v3.2.0 (with TypeScript and React) to create CLI apps.
  IDEA Ultimate / Webstorm project files are provided.
layout: post
title: "Introduction to Ink v3.2.0 (w/ React, Node.js and TypeScript)"
categories:
  - TypeScript
  - React
  - Web
  - Node
  - Server
  - CLI
---

<img class="post-hero-image" src="{{ 'assets/ink-intro.svg' | relative_url }}"/>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [What is Ink](#what-is-ink)
- [React core, renderer, reconciler](#react-core-renderer-reconciler)
- [Create Ink project with TypeScript](#create-ink-project-with-typescript)
  - [1. 📄 package.json](#1--packagejson)
  - [2. 🤖 npm link](#2--npm-link)
  - [3. 📄 dist/cli.js](#3--distclijs)
  - [4. 📄 tsconfig.json](#4--tsconfigjson)
  - [5. 📂 source/](#5--source)
  - [6. 📄 readme.md](#6--readmemd)
  - [7. 📄 .editorconfig](#7--editorconfig)
- [Resolving permissions problems on Linux](#resolving-permissions-problems-on-linux)
- [Node.js executable modules, npm link, and npm bin](#nodejs-executable-modules-npm-link-and-npm-bin)
  - [What is an executable module?](#what-is-an-executable-module)
  - [My Node.js configuration](#my-nodejs-configuration)
  - [Installing a module globally and then executing it](#installing-a-module-globally-and-then-executing-it)
  - [Creating your own executable module](#creating-your-own-executable-module)
    - [Running this module using the symlink generated via npm link](#running-this-module-using-the-symlink-generated-via-npm-link)
    - [Running this module using npm exec -c in the module's folder](#running-this-module-using-npm-exec--c-in-the-modules-folder)
  - [Specify more than one executable in bin property](#specify-more-than-one-executable-in-bin-property)
  - [Meta example](#meta-example)
  - [npm install -g](#npm-install--g)
  - [npm files](#npm-files)
  - [npm config](#npm-config)
- [Make major changes to create-ink-app v2.1.1 scaffolding](#make-major-changes-to-create-ink-app-v211-scaffolding)
  - [Rename source to src](#rename-source-to-src)
  - [Update a few dependencies](#update-a-few-dependencies)
  - [Break all the things 💣 - Switch TS strict mode & commander](#break-all-the-things----switch-ts-strict-mode--commander)
  - [Drop support for xo](#drop-support-for-xo)
  - [Drop support for ava](#drop-support-for-ava)
  - [Use Jest for testing](#use-jest-for-testing)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

This article is an introduction to using Ink v3.2.0 (with TypeScript and React) to create CLI apps.
IDEA Ultimate / Webstorm project files are provided.

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

## React core, renderer, reconciler

<!-- prettier-ignore-start -->

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

The following is an overview of React to understand custom renderers like Ink.

React core only includes APIs that are needed to define components. They don't have any platform
specific code or diffing algorithm. Things like `React.createElement()`, `React.createClass()`,
`React.Component`, `React.Children`, and `React.PropTypes` are defined here.

Renderers are needed to transform React component trees into DOM nodes in a browser
([`react-dom`][2.2]), or native platform views ([React Native][2.11]).

A React component tree is made up of [`host` and `composite`][2.10] components.

1. `host` components are platform specific components that belong to the host environment, eg:
   browser / DOM, [React Native][2.11], [React Canvas][2.12], [React PDF][2.13], [React Docx][2.14],
   [React Hardware][2.15] etc.

- For a browser / DOM host these could be things like `div` or `img` (aka regular DOM nodes). They
  typically begin with lower-case in the case of [`react-dom`][2.2].
- For a React Native app on Android these could be things like `Text` or `View` that map to the
  Android View hierarchy.

2. `composite` components are user-defined components that you write in React. These are things that
   you write using React like `<MyButton>`, `<MyContent>`, etc.

The reconciler is a diffing algorithm that helps React figure out what host components to update on
a state change. The [Fiber reconciler][2.17] is the default since React v16. Fiber reconciler can
perform the reconciliation of the tree by splitting work into minor chunks and hence can prioritize,
pause and resume work thus freeing up the main thread to perform work efficiently.

Ink provides its own custom renderer and host components that you can use.

> ### 💡 Resources to help you create your own renderer
>
> | Resource         | Notes                                                          |
> | ---------------- | -------------------------------------------------------------- |
> | [Video][2.7]     | Build your own renderer & learn how React works under the hood |
> | [Tutorial][2.10] | Build your own renderer & learn how React works under the hood |
> | [Video][2.16]    | Understand React Fiber Reconciler                              |

---

## Create Ink project with TypeScript

Ink provides the equivalent of [`create-react-app`][3.4] for its projects called
[`create-ink-app`][3.2]. You can run it via [`npx`][3.1] to generate a TypeScript "scaffold" project
using the following commands.

```shell
$ mkdir ink-cli-app
$ cd ink-cli-app
$ npx create-ink-app --typescript
```

This will create quite a few files and folders that form the scaffolding. You can also add a
`.gitignore` file that contains the following.

```text
node_modules
package-lock.json
dist
```

A lot of important things happen when the scaffolding is created by running `create-ink-app`. Here
are some of highlights of the files that are generated and the npm global configuration that is
changed.

> ⚠ If you don't know what symlinks are, please read [this][5.1] before continuing.

### 1. 📄 package.json

This file names the module, pulls in all the dependencies for the Ink app, and sets up the module to
be executable.

`name`:

- The name of the folder in which you run `npx create-ink-app` is used for the value of this
  property. In this case it is `ink-cli-app`.

`devDependencies`:

- Notably it pulls in `xo` for linting, and [`ava`][3.5] for testing.
- And TypeScript as expected.

`dependencies`:

- Notably it pulls in [`meow`][3.3] which does command line argument parsing gets added.
- And `react` and `ink` as expected.

`bin`:

- This module is executable since the `bin` property value is `dist/cli.js`. You can run this module
  by executing this command in a terminal (in the folder where `package.json` resides).

  ```shell
  npm exec -c 'ink-cli-app --name=Grogu'
  ```

  In the command above, `ink-cli-app` refers to the value of the `name` property. Please refer to
  the [npm link and bin](#nodejs-executable-modules-npm-link-and-npm-bin) section for more
  information on executable modules.

  > ⚠ If you define your `bin` property value (in `package.json`) to be a JS file, eg: `dist/cli.js`
  > then it is imperative that this file be marked executable on Linux or MacOS. Also this JS file
  > needs to have a header that tells the OS that it can be run, eg: `#!/usr/bin/env node`.

`scripts`:

- You can run the `start` script in order to run the module. This script builds the module and then
  runs the same file path that's specified in `bin` property (`dist/cli.js`). Here's how you can
  pass [command line arguments to this script](https://stackoverflow.com/a/14404223/2085356).

  ```shell
  $ npm run start -- --name=Grogu
  ```

- You can run the `test` script in order to run the tests included in this module using `xo` and
  `ava`.
- You can run the `build` script in order to run `tsc` and compile the TypeScript files to JS and
  dump them in the `dist` folder (as specified in `tsconfig.json`).

`files`:

- This property acts as a whitelist (and we don't have an `.npmignore` file, which acts as a
  blacklist) which tells npm which classes to included when publishing this module. The value is the
  same as `bin` property, which just means that any dependent classes should be included as required
  source for this module to operate.

`engines`:

- This just says that any Node.js v10.x or later runtime is acceptable.

### 2. 🤖 npm link

The `create-ink-app` runs [`npm link`](#nodejs-executable-modules-npm-link-and-npm-bin) in the
folder that has `package.json` file, which allows you to run `ink-cli-app` from your terminal (in
any folder). This does two **"things"**.

1. **"Thing" #1 🧙 - List of globally installed modules updated**

   If you run [`npm list -g`](#npm-install--g) you will find a new entry for your module has been
   added to the list of modules that are globally installed via npm on your machine.

   ```shell
    $ npm list -g | lolcat
   ```

   On my machine it looks like this.

   <pre class="pre-manual-highlight"><span style="color:#0E87E9">/</span><span style="color:#0C8CE7">h</span><span style="color:#0A90E4">o</span><span style="color:#0994E2">m</span><span style="color:#0798DF">e</span><span style="color:#069CDC">/</span><span style="color:#05A0D9">l</span><span style="color:#04A4D6">i</span><span style="color:#03A8D3">n</span><span style="color:#02ACD0">u</span><span style="color:#02B0CD">x</span><span style="color:#01B4C9">b</span><span style="color:#01B8C6">r</span><span style="color:#01BCC2">e</span><span style="color:#01C0BE">w</span><span style="color:#01C3BB">/</span><span style="color:#01C7B7">.</span><span style="color:#01CAB3">l</span><span style="color:#02CEAF">i</span><span style="color:#02D1AB">n</span><span style="color:#03D4A7">u</span><span style="color:#04D7A3">x</span><span style="color:#05DA9F">b</span><span style="color:#06DD9B">r</span><span style="color:#08E097">e</span><span style="color:#09E393">w</span><span style="color:#0BE58F">/</span><span style="color:#0CE88A">l</span><span style="color:#0EEA86">i</span><span style="color:#10EC82">b</span>
   <span style="color:#0994E2">├</span><span style="color:#0798DF">─</span><span style="color:#069CDC">─</span><span style="color:#05A0D9"> </span><span style="color:#04A4D6">a</span><span style="color:#03A8D3">l</span><span style="color:#02ACD0">l</span><span style="color:#02B0CD">-</span><span style="color:#01B4C9">t</span><span style="color:#01B8C6">h</span><span style="color:#01BCC2">e</span><span style="color:#01C0BE">-</span><span style="color:#01C3BB">p</span><span style="color:#01C7B7">a</span><span style="color:#01CAB3">c</span><span style="color:#02CEAF">k</span><span style="color:#02D1AB">a</span><span style="color:#03D4A7">g</span><span style="color:#04D7A3">e</span><span style="color:#05DA9F">-</span><span style="color:#06DD9B">n</span><span style="color:#08E097">a</span><span style="color:#09E393">m</span><span style="color:#0BE58F">e</span><span style="color:#0CE88A">s</span><span style="color:#0EEA86">@</span><span style="color:#10EC82">1</span><span style="color:#12EE7E">.</span><span style="color:#15F079">3</span><span style="color:#17F275">9</span><span style="color:#19F471">0</span><span style="color:#1CF66D">5</span><span style="color:#1FF769">.</span><span style="color:#22F864">0</span>
   <span style="color:#05A0D9">├</span><span style="color:#04A4D6">─</span><span style="color:#03A8D3">─</span><span style="color:#02ACD0"> </span><span style="color:#02B0CD">d</span><span style="color:#01B4C9">o</span><span style="color:#01B8C6">c</span><span style="color:#01BCC2">t</span><span style="color:#01C0BE">o</span><span style="color:#01C3BB">c</span><span style="color:#01C7B7">@</span><span style="color:#01CAB3">2</span><span style="color:#02CEAF">.</span><span style="color:#02D1AB">0</span><span style="color:#03D4A7">.</span><span style="color:#04D7A3">1</span>
   <span style="color:#02ACD0">├</span><span style="color:#02B0CD">─</span><span style="color:#01B4C9">─</span><span style="color:#01B8C6"> </span><span style="color:#01BCC2">i</span><span style="color:#01C0BE">n</span><span style="color:#01C3BB">k</span><span style="color:#01C7B7">-</span><span style="color:#01CAB3">c</span><span style="color:#02CEAF">l</span><span style="color:#02D1AB">i</span><span style="color:#03D4A7">-</span><span style="color:#04D7A3">a</span><span style="color:#05DA9F">p</span><span style="color:#06DD9B">p</span><span style="color:#08E097">@</span><span style="color:#09E393">0</span><span style="color:#0BE58F">.</span><span style="color:#0CE88A">0</span><span style="color:#0EEA86">.</span><span style="color:#10EC82">0</span><span style="color:#12EE7E"> </span><span style="color:#15F079">-</span><span style="color:#17F275">&gt;</span><span style="color:#19F471"> </span><span style="color:#1CF66D">.</span><span style="color:#1FF769">/</span><span style="color:#22F864">.</span><span style="color:#24FA60">.</span><span style="color:#27FB5C">/</span><span style="color:#2BFC58">.</span><span style="color:#2EFD54">.</span><span style="color:#31FD50">/</span><span style="color:#34FE4C">.</span><span style="color:#38FE49">.</span><span style="color:#3BFE45">/</span><span style="color:#3FFE41">n</span><span style="color:#43FE3D">a</span><span style="color:#46FE3A">z</span><span style="color:#4AFE36">m</span><span style="color:#4EFE33">u</span><span style="color:#52FD30">l</span><span style="color:#56FC2C">/</span><span style="color:#5AFB29">g</span><span style="color:#5EFA26">i</span><span style="color:#62F923">t</span><span style="color:#66F820">h</span><span style="color:#6BF61E">u</span><span style="color:#6FF51B">b</span><span style="color:#73F318">/</span><span style="color:#77F116">t</span><span style="color:#7BF014">s</span><span style="color:#80ED11">-</span><span style="color:#84EB0F">s</span><span style="color:#88E90D">c</span><span style="color:#8CE70C">r</span><span style="color:#90E40A">a</span><span style="color:#95E108">t</span><span style="color:#99DF07">c</span><span style="color:#9DDC06">h</span><span style="color:#A1D905">/</span><span style="color:#A5D604">i</span><span style="color:#A9D303">n</span><span style="color:#ADCF02">k</span><span style="color:#B1CC01">-</span><span style="color:#B5C901">c</span><span style="color:#B9C501">l</span><span style="color:#BCC201">i</span><span style="color:#C0BE01">-</span><span style="color:#C4BA01">a</span><span style="color:#C7B601">p</span><span style="color:#CBB301">p</span>
   <span style="color:#01B8C6">├</span><span style="color:#01BCC2">─</span><span style="color:#01C0BE">─</span><span style="color:#01C3BB"> </span><span style="color:#01C7B7">n</span><span style="color:#01CAB3">p</span><span style="color:#02CEAF">m</span><span style="color:#02D1AB">@</span><span style="color:#03D4A7">8</span><span style="color:#04D7A3">.</span><span style="color:#05DA9F">1</span><span style="color:#06DD9B">.</span><span style="color:#08E097">0</span>
   <span style="color:#01C3BB">├</span><span style="color:#01C7B7">─</span><span style="color:#01CAB3">─</span><span style="color:#02CEAF"> </span><span style="color:#02D1AB">p</span><span style="color:#03D4A7">r</span><span style="color:#04D7A3">e</span><span style="color:#05DA9F">t</span><span style="color:#06DD9B">t</span><span style="color:#08E097">i</span><span style="color:#09E393">e</span><span style="color:#0BE58F">r</span><span style="color:#0CE88A">@</span><span style="color:#0EEA86">2</span><span style="color:#10EC82">.</span><span style="color:#12EE7E">4</span><span style="color:#15F079">.</span><span style="color:#17F275">1</span>
   <span style="color:#02CEAF">├</span><span style="color:#02D1AB">─</span><span style="color:#03D4A7">─</span><span style="color:#04D7A3"> </span><span style="color:#05DA9F">t</span><span style="color:#06DD9B">s</span><span style="color:#08E097">-</span><span style="color:#09E393">n</span><span style="color:#0BE58F">o</span><span style="color:#0CE88A">d</span><span style="color:#0EEA86">e</span><span style="color:#10EC82">-</span><span style="color:#12EE7E">d</span><span style="color:#15F079">e</span><span style="color:#17F275">v</span><span style="color:#19F471">@</span><span style="color:#1CF66D">1</span><span style="color:#1FF769">.</span><span style="color:#22F864">1</span><span style="color:#24FA60">.</span><span style="color:#27FB5C">8</span>
   <span style="color:#04D7A3">├</span><span style="color:#05DA9F">─</span><span style="color:#06DD9B">─</span><span style="color:#08E097"> </span><span style="color:#09E393">t</span><span style="color:#0BE58F">s</span><span style="color:#0CE88A">-</span><span style="color:#0EEA86">n</span><span style="color:#10EC82">o</span><span style="color:#12EE7E">d</span><span style="color:#15F079">e</span><span style="color:#17F275">@</span><span style="color:#19F471">1</span><span style="color:#1CF66D">0</span><span style="color:#1FF769">.</span><span style="color:#22F864">2</span><span style="color:#24FA60">.</span><span style="color:#27FB5C">1</span>
   <span style="color:#08E097">└</span><span style="color:#09E393">─</span><span style="color:#0BE58F">─</span><span style="color:#0CE88A"> </span><span style="color:#0EEA86">t</span><span style="color:#10EC82">y</span><span style="color:#12EE7E">p</span><span style="color:#15F079">e</span><span style="color:#17F275">s</span><span style="color:#19F471">c</span><span style="color:#1CF66D">r</span><span style="color:#1FF769">i</span><span style="color:#22F864">p</span><span style="color:#24FA60">t</span><span style="color:#27FB5C">@</span><span style="color:#2BFC58">4</span><span style="color:#2EFD54">.</span><span style="color:#31FD50">4</span><span style="color:#34FE4C">.</span><span style="color:#38FE49">3</span>
   </pre>

   As you can see an entry has been created for `ink-cli-app` and added to the list of all the
   globally installed npm modules.

   > Here are some notes on this.
   >
   > 1. To remove this entry run `npm uninstall -g ink-cli-app` (which we aren't going to do).
   >
   > 2. Each entry in this list has a corresponding folder in the global `node_modules` folder which
   >    we get into next.

2. **"Thing" #2 🧙 - Two symlinks created for your module**

   The first symlink has been created _in_ the global `node_modules` folder _pointing to_ the folder
   in which our module resides.

   We can find where this global `node_modules` folder is located by running
   [`npm root -g`](#npm-install--g).

   This is what it looks like on my machine.

   ```shell
   $ npm root -g
   /home/linuxbrew/.linuxbrew/lib/node_modules
   ```

   I run the following command to see what the contents of this folder are.

   ```shell
   lsd -1 (npm root -g) | lolcat
   ```

   The `ink-cli-app` symlink is pointing to the actual folder
   (`/home/nazmul/github/ts-scratch/ink-cli-app`) where the node module resides.

   <pre class="pre-manual-highlight"><span style="color:#9FDA05">a</span><span style="color:#A3D704">l</span><span style="color:#A7D403">l</span><span style="color:#ABD102">-</span><span style="color:#AFCE02">t</span><span style="color:#B3CA01">h</span><span style="color:#B7C701">e</span><span style="color:#BBC301">-</span><span style="color:#BEC001">p</span><span style="color:#C2BC01">a</span><span style="color:#C5B801">c</span><span style="color:#C9B401">k</span><span style="color:#CCB102">a</span><span style="color:#D0AD02">g</span><span style="color:#D3A903">e</span><span style="color:#D6A504">-</span><span style="color:#D9A105">n</span><span style="color:#DC9C06">a</span><span style="color:#DF9807">m</span><span style="color:#E29409">e</span><span style="color:#E4900A">s</span>
   <span style="color:#ABD102">d</span><span style="color:#AFCE02">o</span><span style="color:#B3CA01">c</span><span style="color:#B7C701">t</span><span style="color:#BBC301">o</span><span style="color:#BEC001">c</span>
   <span style="color:#B7C701">i</span><span style="color:#BBC301">n</span><span style="color:#BEC001">k</span><span style="color:#C2BC01">-</span><span style="color:#C5B801">c</span><span style="color:#C9B401">l</span><span style="color:#CCB102">i</span><span style="color:#D0AD02">-</span><span style="color:#D3A903">a</span><span style="color:#D6A504">p</span><span style="color:#D9A105">p</span><span style="color:#DC9C06"> </span><span style="color:#DF9807">⇒</span><span style="color:#E29409"> </span><span style="color:#E4900A">.</span><span style="color:#E78C0C">.</span><span style="color:#E9880E">/</span><span style="color:#EC8310">.</span><span style="color:#EE7F12">.</span><span style="color:#F07B14">/</span><span style="color:#F27716">.</span><span style="color:#F37219">.</span><span style="color:#F56E1B">/</span><span style="color:#F76A1E">.</span><span style="color:#F86621">.</span><span style="color:#F96223">/</span><span style="color:#FA5E26">n</span><span style="color:#FB5A29">a</span><span style="color:#FC562D">z</span><span style="color:#FD5230">m</span><span style="color:#FE4E33">u</span><span style="color:#FE4A37">l</span><span style="color:#FE463A">/</span><span style="color:#FE423E">g</span><span style="color:#FE3F41">i</span><span style="color:#FE3B45">t</span><span style="color:#FE3749">h</span><span style="color:#FE344D">u</span><span style="color:#FD3151">b</span><span style="color:#FC2D55">/</span><span style="color:#FC2A59">t</span><span style="color:#FB275D">s</span><span style="color:#FA2461">-</span><span style="color:#F82165">s</span><span style="color:#F71E69">c</span><span style="color:#F51C6D">r</span><span style="color:#F41971">a</span><span style="color:#F21776">t</span><span style="color:#F0147A">c</span><span style="color:#EE127E">h</span><span style="color:#EC1082">/</span><span style="color:#EA0E87">i</span><span style="color:#E70C8B">n</span><span style="color:#E50B8F">k</span><span style="color:#E20993">-</span><span style="color:#E00897">c</span><span style="color:#DD069C">l</span><span style="color:#DA05A0">i</span><span style="color:#D704A4">-</span><span style="color:#D403A8">a</span><span style="color:#D002AC">p</span><span style="color:#CD02B0">p</span>
   <span style="color:#C2BC01">n</span><span style="color:#C5B801">p</span><span style="color:#C9B401">m</span>
   <span style="color:#CCB102">p</span><span style="color:#D0AD02">r</span><span style="color:#D3A903">e</span><span style="color:#D6A504">t</span><span style="color:#D9A105">t</span><span style="color:#DC9C06">i</span><span style="color:#DF9807">e</span><span style="color:#E29409">r</span>
   <span style="color:#D6A504">t</span><span style="color:#D9A105">s</span><span style="color:#DC9C06">-</span><span style="color:#DF9807">n</span><span style="color:#E29409">o</span><span style="color:#E4900A">d</span><span style="color:#E78C0C">e</span>
   <span style="color:#DF9807">t</span><span style="color:#E29409">s</span><span style="color:#E4900A">-</span><span style="color:#E78C0C">n</span><span style="color:#E9880E">o</span><span style="color:#EC8310">d</span><span style="color:#EE7F12">e</span><span style="color:#F07B14">-</span><span style="color:#F27716">d</span><span style="color:#F37219">e</span><span style="color:#F56E1B">v</span>
   <span style="color:#E78C0C">t</span><span style="color:#E9880E">y</span><span style="color:#EC8310">p</span><span style="color:#EE7F12">e</span><span style="color:#F07B14">s</span><span style="color:#F27716">c</span><span style="color:#F37219">r</span><span style="color:#F56E1B">i</span><span style="color:#F76A1E">p</span><span style="color:#F86621">t</span></pre>

   One more symlink is created and this one has everything to do with being able to run
   `ink-cli-app` from any folder in a terminal (or a GUI app).

   **How does Node.js know to execute `ink-cli-app` when run from a terminal or GUI app?** 🤔 After
   all this global `node_modules` folder is not in my `$PATH`.

   > The answer is a little tricky and before we begin our journey to answering this question,
   > here's what some Node.js and npm related folders look like on my machine.
   >
   > | Type                           | Path                                           |
   > | ------------------------------ | ---------------------------------------------- |
   > | Node.js location in `$PATH`    | `/home/linuxbrew/.linuxbrew/bin/`              |
   > | Symlinks created by `npm link` | `/home/linuxbrew/.linuxbrew/bin/`              |
   > | Global `node_modules`          | `/home/linuxbrew/.linuxbrew/lib/node_modules/` |
   > | Actual `ink-cli-app` folder    | `/home/nazmul/github/ts-scratch/ink-cli-app/`  |

   Here are two things that happen to allow `ink-cli-app` to be run from anywhere.

   1. When we install Node.js (via brew or nvm or apt or whatever) we have to add the folder
      containing the `node` and `npm` binary into the `$PATH` environment variable.

      - For me this is `/home/linuxbrew/.linuxbrew/bin/` since I'm using brew.

      - Since I'm using GNOME, I added this folder to my `$PATH` in my `$HOME/.profile` file, making
        it available to terminal and GUI apps after I log into my desktop GNOME session.

   2. `npm link` cleverly creates a symlink _in this folder_ (which is accessible by `$PATH`) that
      _points to_ the file specified by the `bin` property of the `package.json` for the
      `ink-cli-app` node module. Thus allowing us to be able to run this CLI app from any folder in
      a terminal, or any GUI app! 🎉

   When I look in my `/home/linuxbrew/.linuxbrew/bin`, I find this `ink-cli-app` symlink.

   ```shell
   $ cd /home/linuxbrew/.linuxbrew/bin
   $ lsd -1 | grep ink | lolcat
   ```

   Which produces this output.

   <pre class="pre-manual-highlight"><span style="color:#0994E2">i</span><span style="color:#0798DF">n</span><span style="color:#069CDC">k</span><span style="color:#05A0D9">-</span><span style="color:#04A4D6">c</span><span style="color:#03A8D3">l</span><span style="color:#02ACD0">i</span><span style="color:#02B0CD">-</span><span style="color:#01B4C9">a</span><span style="color:#01B8C6">p</span><span style="color:#01BCC2">p</span><span style="color:#01C0BE"> </span><span style="color:#01C3BB">⇒</span><span style="color:#01C7B7"> </span><span style="color:#01CAB3">.</span><span style="color:#02CEAF">.</span><span style="color:#02D1AB">/</span><span style="color:#03D4A7">l</span><span style="color:#04D7A3">i</span><span style="color:#05DA9F">b</span><span style="color:#06DD9B">/</span><span style="color:#08E097">n</span><span style="color:#09E393">o</span><span style="color:#0BE58F">d</span><span style="color:#0CE88A">e</span><span style="color:#0EEA86">_</span><span style="color:#10EC82">m</span><span style="color:#12EE7E">o</span><span style="color:#15F079">d</span><span style="color:#17F275">u</span><span style="color:#19F471">l</span><span style="color:#1CF66D">e</span><span style="color:#1FF769">s</span><span style="color:#22F864">/</span><span style="color:#24FA60">i</span><span style="color:#27FB5C">n</span><span style="color:#2BFC58">k</span><span style="color:#2EFD54">-</span><span style="color:#31FD50">c</span><span style="color:#34FE4C">l</span><span style="color:#38FE49">i</span><span style="color:#3BFE45">-</span><span style="color:#3FFE41">a</span><span style="color:#43FE3D">p</span><span style="color:#46FE3A">p</span><span style="color:#4AFE36">/</span><span style="color:#4EFE33">d</span><span style="color:#52FD30">i</span><span style="color:#56FC2C">s</span><span style="color:#5AFB29">t</span><span style="color:#5EFA26">/</span><span style="color:#62F923">c</span><span style="color:#66F820">l</span><span style="color:#6BF61E">i</span><span style="color:#6FF51B">.</span><span style="color:#73F318">j</span><span style="color:#77F116">s</span></pre>

   This is how we read this: the `🔗 ink-cli-app` symlink in this folder (`📂 .linuxbrew/bin`) is 👉
   _pointing to_ the symlink `🔗 ink-cli-app` in the global `📂 node_modules` folder, which itself
   is 👉 _pointing to_ the actual module folder (`📂 github/ts-scratch/ink-cli-app`) which contains
   a `📄 dist/cli.js` file (which is specified in the `bin` property in `package.json`).

   Whew! 😅

   > 💡 For more details on how `npm link` works along w/ executable modules in npm, please read
   > [`this section`](#nodejs-executable-modules-npm-link-and-npm-bin).

### 3. 📄 dist/cli.js

The [`📄 dist/cli.js`][3.9] file is marked as executable. This is a really important step because
this file is actually used in the `bin` entry in `package.json` and tells Node.js that this is a
binary executable file that will launch this module when run from the command line. Also this JS
file needs to have a header that tells the OS that it can be run, eg: `#!/usr/bin/env node`.

> ⚠ Note that the `dist/cli.js` file is compiled from the TypeScript file `source/cli.tsx`. The
> `build` script generates this file and its not checked into git.

### 4. 📄 tsconfig.json

The `📄 tsconfig.json` tells `tsc` to dump the compiled JS files to the `dist/` folder.

- This is why we ignore `dist/` in our `.gitignore` file above.
- You can run `tsc` directly or run `npm run build` to generate the JS files.

### 5. 📂 source/

The `📂 source/` folder has three files, the main one being `cli.tsx`.

- `📄 cli.tsx` - This is the main entry point that launches our app from the command line using
  Node.js. If you run `npm run start` then this file is executed (after the `build` script runs).

- `📄 ui.tsx` - This is where you write your React code. `App` is defined here.

- `📄 test.tsx` - This is what gets run when `npm run test` is executed (which runs [`xo` and
  `ava`][3.5]).

### 6. 📄 readme.md

The `📄 readme.md` file is auto generated and has some information on how to launch your newly
minted CLI app. It basically says that you run the following commands.

```shell
ink-cli-app --help
ink-cli-app --name=Grogu
```

The following UML diagram that pulls all this together, and illustrates everything we have covered
in the following sections: [What is Ink](#what-is-ink),
[React core, renderer, reconciler](#react-core-renderer-reconciler), and
[Install Ink and create a project scaffold in TypeScript](#create-ink-project-with-typescript).

<img src="{{ 'assets/cli.tsx.uml.svg' | relative_url }}"/>

1. You can see the dependencies that `source/cli.tsx` (which is compiled into `cli.js`) pulls in.
   This is the main entry point of the module (the `bin` property in `package.json`).
2. The `render` function from `ink` is used, since we are using Ink to render the JSX and not
   `react-dom`.
3. `meow` is used to parse the command line arguments.

### 7. 📄 .editorconfig

This file sets the default indentation character to tab, and width to 4. I replace it w/ spaces
and 2. Then I had to reformat the code in each of the files in `source`.

```text
root = true

[*]
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true
indent_style = space
indent_size = 2
```

<!-- prettier-ignore-start -->

[3.1]: https://docs.npmjs.com/cli/v7/commands/npx
[3.2]: https://www.npmjs.com/package/create-ink-app
[3.3]: https://www.npmjs.com/package/meow
[3.4]: https://create-react-app.dev/docs/getting-started/
[3.5]: https://blog.logrocket.com/code-testing-and-linting-using-ava-and-xo/
[3.6]: https://github.com/vadimdemedes/create-ink-app/pull/22
[3.7]: https://www.npmjs.com/package/prettier
[3.8]: https://www.npmjs.com/package/doctoc
[3.9]: https://github.com/nazmulidris/ts-scratch/blob/main/ink-cli-app/source/cli.tsx

<!-- prettier-ignore-end -->

---

## Resolving permissions problems on Linux

<!-- prettier-ignore-start -->

[4.1]: https://developerlife.com/2021/07/02/nodejs-typescript-handbook/#nodejs-installation-on-linux-using-brew
[4.2]: https://developerlife.com/2021/07/02/nodejs-typescript-handbook/#publishing-npm-packages
[4.3]: https://developerlife.com/2021/07/02/nodejs-typescript-handbook/#child-process

<!-- prettier-ignore-end -->

When using `create-ink-app` on Pop_OS! 21.04 I experienced some very strange issues when trying to
run the CLI app using `npm run start`, or even `ink-cli-app`. I got a
`sh: 1: node: Permission denied` error when running either of these commands 🤔.

This led to some wild goose chasing which resulted in a deeper understanding of executable Node.js
modules, npm config, execution permissions, and such. So the
[next section](#nodejs-executable-modules-npm-link-and-npm-bin) is dedicated to background knowledge
of all these things and might be useful for deeper understanding or debugging when you run into
issues.

Ultimately I solved it by re-running the `npx create-ink-app` command, which did the following
things.

- It regenerated the `dist`.
- It marked the `cli.js` as executable (**the original problem was that this wasn't marked as
  executable**).
- Then it linked the module to npm via `npm link`, so that the `ink-cli-app` command would run on my
  terminal.

---

## Node.js executable modules, npm link, and npm bin

This section goes into the details of how npm global modules work, what npm `bin` entry means in
`package.json`, and what executable node modules actually are (you're actually making one in this
handbook).

> 💡 To learn more about installing and configuring Node.js itself, check out this section in the
> [Node.js handbook][4.1]. This will walk you thru where Node.js stores its files and modules, etc.

Let's consider the high level uses cases that you've already used npm for.

1. Install dependencies (eg: `npm i react`).
2. Install applications and run them (eg `npm i -g prettier; prettier --help`) or just run them
   w/out installing first (eg: `npx create-react-app`).

npm is powerful (and can be confusing) because it serves 2 roles:

1.  Allowing you to manage (create, publish, export, and import) dependencies (modules) for code
    that you write (eg: `npm i react`). To learn more about publishing npm packages, check out this
    section in the [Node.js handbook][4.2].
2.  Allowing you to create and use command line apps that are run from your terminal (eg:
    `npx create-react-app` or `prettier --write *md`). **👈 We will focus on this use case and how
    it works**.

### What is an executable module?

To make command line apps and distribute them via npm, so that our users can install them and run
them via npm, we have to create not just any node module, but an executable one.

> ⚠ We are going to use the sample app we are working on started
> [here](#create-ink-project-with-typescript) called `ink-cli-app`. Before reading further:
>
> 1. Please read this [section](#create-ink-project-with-typescript) to understand what
>    `package.json` file does and what `npm link` does.
> 2. In order to understand how Node.js executes programs, please read this section in the [Node.js
>    handbook][4.3].

So how does a module become executable?

In `package.json` you can define a [`bin` property][5.4]. When someone tries to "run" your node
module from the terminal or GUI app, Node.js will attempt to execute the the file path in `bin`
property. Here more details on this.

- You can simply define a `string` value for `bin`, which is a file path where the executable of
  your node module resides (eg: `dist/cli.js`).
- This file can be a JS file or some other kind of binary executable file. Think of marking a file
  executable in your terminal and then running it, whether it's a JS file, .fish file, etc.
  - This file will also need to be marked as executable.
  - It must have a [`shebang`](<https://en.wikipedia.org/wiki/Shebang_(Unix)>) header like
    `#!/usr/bin/env node`, so that your OS knows how to execute this file.

Next, we are going to look at how to run this executable module! Here is a brief overview of what we
will see next.

1. How `npm link` works to allow this module to be executed from anywhere on our machine.
2. How `npm exec -c` works to allow this module to only be executed from the folder in which it
   resides.

### My Node.js configuration

Here are all the interesting folders on my machine that are related to the npm things we will dive
into next. I used [brew](https://brew.sh/) to get Node.js on
[Pop_OS! 21.04](https://pop.system76.com/) (based on Ubuntu).

| Type                           | Path                                           |
| ------------------------------ | ---------------------------------------------- |
| Node.js location in `$PATH`    | `/home/linuxbrew/.linuxbrew/bin/`              |
| Symlinks created by `npm link` | `/home/linuxbrew/.linuxbrew/bin/`              |
| Global `node_modules`          | `/home/linuxbrew/.linuxbrew/lib/node_modules/` |
| Actual `ink-cli-app` folder    | `/home/nazmul/github/ts-scratch/ink-cli-app/`  |

> **Node.js & `$PATH`**
>
> - I installed Node.js via brew.
>   1. I manually added `/home/linuxbrew/.linuxbrew/bin` to my `$PATH`
>   2. I put this in `~/.profile` (for GNOME, so I can run npm modules from any terminal or GUI
>      app).
> - `node` and `npm` binaries themselves are a [symlinked][5.1] in this folder which is how `node`
>   is found along w/ `npm` binaries when I use them in the terminal.
>
> **Symlinks created by `npm link`**
>
> - All the symlinks `npm link` creates show up in this folder `/home/linuxbrew/.linuxbrew/bin/`
>   (which is also in the `$PATH`).
> - This is where symlinks for `prettier` and even `ink-cli-app` are stored.
>
> **Global `node_modules`**
>
> - Node.js stores globally installed modules in this this folder like `prettier`.
> - For me this is `/home/linuxbrew/.linuxbrew/lib/node_modules`.

### Installing a module globally and then executing it

Before going over our executable module (`ink-cli-app`), let's use an existing example of
`prettier`.

To install it, you have to run `npm i -g prettier`. It downloads the module and creates a symlink
`prettier` which you can use in the terminal and GUI apps.

> 💡 You can find what modules are installed globally by running [`npm list -g`](#npm-install--g).
> You can uninstall the module by running `npm uninstall -g <MODULE_NAME>`.

1. `prettier` is downloaded to the global `node_modules` folder. So in
   `/home/linuxbrew/.linuxbrew/lib/node_modules/prettier/` the files are downloaded from npm.

   ```shell
   $ cd /home/linuxbrew/.linuxbrew/lib/node_modules
   $ realpath prettier | lolcat
   ```

   Which produces the following output.

   <pre class="pre-manual-highlight"><span style="color:#1E6AF7">/</span><span style="color:#1B6EF5">h</span><span style="color:#1972F4">o</span><span style="color:#1676F2">m</span><span style="color:#147BF0">e</span><span style="color:#127FEE">/</span><span style="color:#1083EC">l</span><span style="color:#0E87E9">i</span><span style="color:#0C8CE7">n</span><span style="color:#0A90E4">u</span><span style="color:#0994E2">x</span><span style="color:#0798DF">b</span><span style="color:#069CDC">r</span><span style="color:#05A0D9">e</span><span style="color:#04A4D6">w</span><span style="color:#03A8D3">/</span><span style="color:#02ACD0">.</span><span style="color:#02B0CD">l</span><span style="color:#01B4C9">i</span><span style="color:#01B8C6">n</span><span style="color:#01BCC2">u</span><span style="color:#01BFBF">x</span><span style="color:#01C3BB">b</span><span style="color:#01C7B7">r</span><span style="color:#01CAB3">e</span><span style="color:#02CEAF">w</span><span style="color:#02D1AB">/</span><span style="color:#03D4A7">l</span><span style="color:#04D7A3">i</span><span style="color:#05DA9F">b</span><span style="color:#06DD9B">/</span><span style="color:#08E097">n</span><span style="color:#09E393">o</span><span style="color:#0BE58F">d</span><span style="color:#0CE88A">e</span><span style="color:#0EEA86">_</span><span style="color:#10EC82">m</span><span style="color:#12EE7E">o</span><span style="color:#15F079">d</span><span style="color:#17F275">u</span><span style="color:#19F471">l</span><span style="color:#1CF66D">e</span><span style="color:#1FF769">s</span><span style="color:#22F865">/</span><span style="color:#24FA60">p</span><span style="color:#27FB5C">r</span><span style="color:#2BFC58">e</span><span style="color:#2EFD54">t</span><span style="color:#31FD50">t</span><span style="color:#34FE4C">i</span><span style="color:#38FE49">e</span><span style="color:#3BFE45">r</span></pre>

2. A symlink is created for `prettier` in the `/home/linuxbrew/.linuxbrew/bin/` folder which points
   to the file specified in the `bin` property in the global `node_modules/prettier/package.json`
   folder.

   ```shell
   $ cd /home/linuxbrew/.linuxbrew/bin
   $ lsd -1 prettier | lolcat
   ```

   This produces the following output.

   <pre class="pre-manual-highlight"><span style="color:#01C8B5">p</span><span style="color:#01CCB1">r</span><span style="color:#02CFAD">e</span><span style="color:#03D2A9">t</span><span style="color:#04D6A5">t</span><span style="color:#05D9A1">i</span><span style="color:#06DC9D">e</span><span style="color:#07DE99">r</span><span style="color:#08E195"> </span><span style="color:#0AE491">⇒</span><span style="color:#0CE68D"> </span><span style="color:#0DE988">.</span><span style="color:#0FEB84">.</span><span style="color:#11ED80">/</span><span style="color:#14EF7C">l</span><span style="color:#16F177">i</span><span style="color:#18F373">b</span><span style="color:#1BF56F">/</span><span style="color:#1DF66B">n</span><span style="color:#20F867">o</span><span style="color:#23F962">d</span><span style="color:#26FA5E">e</span><span style="color:#29FB5A">_</span><span style="color:#2CFC56">m</span><span style="color:#2FFD52">o</span><span style="color:#33FD4E">d</span><span style="color:#36FE4A">u</span><span style="color:#3AFE47">l</span><span style="color:#3DFE43">e</span><span style="color:#41FE3F">s</span><span style="color:#44FE3C">/</span><span style="color:#48FE38">p</span><span style="color:#4CFE35">r</span><span style="color:#50FD31">e</span><span style="color:#54FD2E">t</span><span style="color:#58FC2B">t</span><span style="color:#5CFB28">i</span><span style="color:#60FA25">e</span><span style="color:#64F922">r</span><span style="color:#68F71F">/</span><span style="color:#6DF61C">b</span><span style="color:#71F41A">i</span><span style="color:#75F217">n</span><span style="color:#79F115">-</span><span style="color:#7DEF13">p</span><span style="color:#82EC10">r</span><span style="color:#86EA0E">e</span><span style="color:#8AE80D">t</span><span style="color:#8EE50B">t</span><span style="color:#92E309">i</span><span style="color:#97E008">e</span><span style="color:#9BDD06">r</span><span style="color:#9FDA05">.</span><span style="color:#A3D704">j</span><span style="color:#A7D403">s</span>
   </pre>

### Creating your own executable module

We are going to use the sample app we are working on started
[here](#create-ink-project-with-typescript) called `ink-cli-app`.

> ⚠ Please read this [section](#create-ink-project-with-typescript) before moving on to understand
> what `package.json` file does and what `npm link` does as well.

To recap, `npm create-ink-app` does the following:

- A `package.json` file is created here w/ a `bin` property defined, which is the `dist/cli.js`
  file. This JS file is also marked executable.
- [`npm link`][5.3] is run in this module's folder which creates a symlink `ink-cli-app`.

#### Running this module using the symlink generated via npm link

Let's take a closer look at the `ink-cli-app` symlink itself (which is generated by `npm link`)
using the following commands. This symlink is in my `$PATH`.

```shell
$ cd /home/linuxbrew/.linuxbrew/bin
$ lsd -1 ink-cli-app | lolcat
```

This produces the following output.

<pre class="pre-manual-highlight"><span style="color:#27FB5C">i</span><span style="color:#2BFC58">n</span><span style="color:#2EFD54">k</span><span style="color:#31FD50">-</span><span style="color:#34FE4C">c</span><span style="color:#38FE49">l</span><span style="color:#3BFE45">i</span><span style="color:#3FFE41">-</span><span style="color:#43FE3D">a</span><span style="color:#46FE3A">p</span><span style="color:#4AFE36">p</span><span style="color:#4EFE33"> </span><span style="color:#52FD30">⇒</span><span style="color:#56FC2C"> </span><span style="color:#5AFB29">.</span><span style="color:#5EFA26">.</span><span style="color:#62F923">/</span><span style="color:#66F820">l</span><span style="color:#6AF61E">i</span><span style="color:#6FF51B">b</span><span style="color:#73F318">/</span><span style="color:#77F116">n</span><span style="color:#7BF014">o</span><span style="color:#80ED11">d</span><span style="color:#84EB0F">e</span><span style="color:#88E90E">_</span><span style="color:#8CE70C">m</span><span style="color:#90E40A">o</span><span style="color:#95E108">d</span><span style="color:#99DF07">u</span><span style="color:#9DDC06">l</span><span style="color:#A1D905">e</span><span style="color:#A5D604">s</span><span style="color:#A9D303">/</span><span style="color:#ADCF02">i</span><span style="color:#B1CC01">n</span><span style="color:#B5C901">k</span><span style="color:#B9C501">-</span><span style="color:#BCC201">c</span><span style="color:#C0BE01">l</span><span style="color:#C4BA01">i</span><span style="color:#C7B601">-</span><span style="color:#CBB301">a</span><span style="color:#CEAF02">p</span><span style="color:#D1AB02">p</span><span style="color:#D5A703">/</span><span style="color:#D8A304">d</span><span style="color:#DB9F05">i</span><span style="color:#DE9A07">s</span><span style="color:#E09608">t</span><span style="color:#E39209">/</span><span style="color:#E68E0B">c</span><span style="color:#E88A0D">l</span><span style="color:#EA850F">i</span><span style="color:#ED8111">.</span><span style="color:#EF7D13">j</span><span style="color:#F17915">s</span>
</pre>

We can simply run the CLI app by running `ink-cli-app` from the terminal as shown here.

```shell
$ ink-cli-app --name=Grogu
```

Which results in the following output.

<pre class="pre-manual-highlight">Hello, <span style="color:#A3BE8C">Grogu</span></pre>

> ⚡ This [tutorial][5.5] goes into the details of how Node.js symlinks work for globally installed
> modules and local ones using `npm link`.

#### Running this module using npm exec -c in the module's folder

However, we might also want to run it w/out using the symlink above. To do this we can use
`npm exec -c` in the module folder itself.

```shell
$ cd /home/nazmul/github/ts-scratch/ink-cli-app/
$ npm exec -c 'ink-cli-app --name=Grogu'
```

Which results in the following output.

<pre class="pre-manual-highlight">Hello, <span style="color:#A3BE8C">Grogu</span></pre>

> ⚡ Here's more information on [`npm exec -c`][5.2].

> 💡 We can also run [`npm link`][5.3] in this module's folder in order to generate a symlink to the
> `bin` property value.

### Specify more than one executable in bin property

If you want to specify more than a single executable for your module, you can provide an object
rather a `string` value for `bin`. Here's an example.

```json
{
  "bin": {
    "myClientApp": "./cli.js",
    "myServerApp": "./server.js"
  }
}
```

So if you wanted to run `myServerApp` you can call.

```shell
npm exec -c 'myServerApp --port=1234'
```

> 💡 When you run [`npm link`][5.3] it will create multiple symlinks one for each key-value pair in
> `bin`. These symlinks are stored in `/home/linuxbrew/.linuxbrew/bin/` in my brew install of
> Node.js.

<!-- prettier-ignore-start -->

[5.1]: https://linuxize.com/post/how-to-create-symbolic-links-in-linux-using-the-ln-command/
[5.2]: https://docs.npmjs.com/cli/v7/commands/npm-exec#synopsis
[5.3]: https://newbedev.com/install-a-locally-developed-npm-package-globally
[5.4]: https://docs.npmjs.com/cli/v7/configuring-npm/package-json#bin
[5.5]: https://medium.com/@alexishevia/the-magic-behind-npm-link-d94dcb3a81af

<!-- prettier-ignore-end -->

### Meta example

A "meta" example of all of the concepts above is the [`create-ink-app`][3.2] npm module itself.

1. You can run it via [`npx`][3.1] without installing it locally.
2. After you run it, it will globally install your CLI app via npm and mark the `dist/cli.js` file
   executable. This JS file is the main entry point for your newly minted CLI app.

### npm install -g

When you tell npm to install a module globally, it will actually install it in the global folder
(which is different depending on how you installed Node.js in the first place). It will also create
a [symlink for the `bin` entry](#nodejs-executable-modules-npm-link-and-npm-bin) in `package.json`
using the value of `name`. This will allow you to run this module from the terminal (for eg:
[`prettier`][3.7] or [`doctoc`][3.8]).

To find out where npm actually installs global modules, run the following command.

```shell
npm root -g
```

To list all the globally installed modules, you can run the following command.

```shell
npm list -g
```

Conversely to uninstall a module globally, you can use the following command.

```shell
npm uninstall -g <PACKAGE_NAME>
```

### npm files

This isn't really related to the `bin` property in `package.json`. The
[`files` property](https://docs.npmjs.com/cli/v7/configuring-npm/package-json#files) tells Node.js
that all the files listed in this array should be whitelisted and included in the module. So provide
at least one entry point into your code, typically, the same entry as the `bin` property. You can
bypass using this property by using a
[`.npmignore` blacklist file](https://stackoverflow.com/a/53381692/2085356).

### npm config

npm stores global configuration as well as user specific configuration settings. These are stored as
key-value pairs using JSON. In order to show the list of npm config key-value pairs use the
following.

```shell
npm config ls -l
```

The user specific settings are stored in `$HOME/.npmrc`.

Executing the following command will change a user default config key's value and will update the
`$HOME/.npmrc` file w/ this value (and create the file if it didn't exist before).

```shell
npm config set unsafe-perm true
```

You can then check to see the value of this key using.

```shell
npm config get unsafe-perm
```

If you delete the `$HOME/.npmrc` file, then this will remove all the key-value pairs that you have
set using `npm config set <KEY> <VALUE>`.

> The `unsafe-perm` setting actually affects which user is actually used by Node.js when running
> modules. You can read more about it in these links.
>
> - [npm docs on unsafe-perm](https://docs.npmjs.com/cli/v6/using-npm/config).
> - [Tutorial explaining unsafe-perm](https://geedew.com/What-does-unsafe-perm-in-npm-actually-do/).

---

## Make major changes to create-ink-app v2.1.1 scaffolding

We are now going to majorly deviate from code that was generated by the scaffolding.

1. Notably, we are going to drop `ava` v4.x for testing and use RTL and Jest instead.
2. We are going to drop `xo` (no need for this linter package).
3. We are going to drop `meow` and use `commander` instead.
4. We are also going to change some folder names.

The following are the details.

> ### ⚡ Use this template repo instead of create-ink-app
>
> I've created a [GitHub template repo][6.1] that we are going use in future articles instead of
> `create-ink-app`. Here's a link to [ts-ink-template][6.2] repo; all the changes shown in this
> section are reflected in this repo.

<!-- prettier-ignore-start -->

[6.1]: https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository
[6.2]: https://github.com/nazmulidris/ts-ink-template

<!-- prettier-ignore-end -->

### Rename source to src

The `create-ink-app` generates a `source` folder, but I prefer to use `src`. To make this change:

1. Rename the folder (`mv source src`).
2. Update references to `source` in `package.json` and `tsconfig.json`
   (`sed -i s/source/src/g *json`).

### Update a few dependencies

In `package.json` we are going to update the following dependency `meow` to `^10.0.0`.

> 💡 You can run `npm outdated` to see a what package in your `package.json` can be updated. Then
> you can update them by typing `npm i <PACKAGE>@latest`.

Here's the new `package.json`.

```json
{
  "name": "ink-cli-app",
  "version": "0.0.1",
  "license": "Apache 2.0",
  "bin": "dist/cli.js",
  "engines": {
    "node": ">=10"
  },
  "scripts": {
    "build": "tsc",
    "build-watch": "tsc --watch",
    "start": "dist/cli.js",
    "build-and-start": "npm run build && dist/cli.js",
    "pretest": "npm run build",
    "test": "jest",
    "start-watch": "nodemon --exitcrash -e ts,tsx,js,jsx --exec 'node dist/cli.js || exit 1'",
    "dev": "npm-run-all -p -r build-watch start-watch"
  },
  "files": ["dist/cli.js"],
  "dependencies": {
    "chalk": "^4.1.2",
    "commander": "^8.3.0",
    "ink": "^3.2.0",
    "r3bl-ts-utils": "^1.0.5",
    "react": "^17.0.2",
    "tslib": "^2.3.1"
  },
  "devDependencies": {
    "@sindresorhus/tsconfig": "^2.0.0",
    "@types/jest": "^27.0.2",
    "@types/react": "^17.0.34",
    "eslint-plugin-react": "^7.27.0",
    "eslint-plugin-react-hooks": "^4.3.0",
    "ink-testing-library": "^2.1.0",
    "jest": "^27.3.1",
    "nodemon": "^2.0.15",
    "npm-run-all": "^4.1.5",
    "prettier": "^2.4.1",
    "ts-jest": "^27.0.7",
    "ts-node": "^10.4.0",
    "typescript": "^4.4.4"
  }
}
```

A lot of scripts have been added, to make it easy to work w/ building, running, testing and
watching. Here's more
[information on this](https://github.com/nazmulidris/ts-ink-template/blob/main/README.md#npm-scripts)
from the template repo which you should be using instead of `create-ink-app`.

### Break all the things 💣 - Switch TS strict mode & commander

This is going to be a **huge divergence** to the configuration and code that's generated by the
scaffolding. We will use CommonJS as the module format for maximum backward compatibility (ESM isn't
there yet).

1. Here are the changes that need to be made to `tsconfig.json`.

   ```json
   {
     "extends": "@sindresorhus/tsconfig",
     "compilerOptions": {
       "esModuleInterop": true,
       "outDir": "dist",
       "sourceMap": true,
       "target": "ESNext",
       "//ESNext": "https://stackoverflow.com/a/62837086/2085356",
       "module": "CommonJS"
     },
     "include": ["src"]
   }
   ```

2. Here are the changes that need to be made the `src/cli.tsx` file.

   In `cli.tsx` the call to `meow()` has to be changed to use `commander`.

   ```tsx
   #!/usr/bin/env node

   import React from "react"
   import { render } from "ink"
   import App from "./ui"
   import { _let } from "r3bl-ts-utils"
   import { Command } from "commander"

   const name: string = _let(new Command(), (command) => {
     command.option("-n, --name <name>", "name to display")
     command.parse(process.argv)
     const options = command.opts()
     return options["name"]
   })

   render(<App name={name} />)
   ```

3. Here is a change that need to be made to the `src/ui.tsx` file.

   There's a `module.exports = App` line that needs to be deleted. We are now only using
   `export default App`.

### Drop support for xo

By running `npm uninstall -D xo` we drop the linter dependency.

### Drop support for ava

By running `npm uninstall -D ava @ava/typescript` we drop support for `ava` test runner. Delete
the`src/test.tsx` file as well, since it will no longer compile.

### Use Jest for testing

We will use Jest to add tests to our node module. To start here are the packages that need to be
installed.

```shell
$ npm i -D jest ts-jest ts-node @types/jest
```

Then we need a new `jestconfig.json` file.

```json
{
  "#comments": [
    "https://jestjs.io/docs/configuration#projects-arraystring--projectconfig",
    "https://jestjs.io/docs/configuration#testenvironment-string",
    "https://gist.github.com/thebuilder/15a084f74b1c6a1f163fc6254ad5a5ba"
  ],
  "projects": [
    {
      "displayName": "node  (default project)",
      "transform": {
        "^.+\\.(t|j)sx?$": "ts-jest"
      },
      "testEnvironment": "node",
      "testMatch": ["**/__tests__/**/*.test.ts?(x)"]
    },
    {
      "displayName": "jsdom (browser project)",
      "transform": {
        "^.+\\.(t|j)sx?$": "ts-jest"
      },
      "testEnvironment": "jsdom",
      "testMatch": ["**/__tests__/**/*.test.jsdom.ts?(x)"]
    }
  ]
}
```

> 💡 We have setup two projects in the `jestconfig.json` file above. Depending on the code we want
> to test, it might expect to run in a browser environment or in node. By default tests will run in
> the `node` test environment. If a test is named `*.test.jsdom.ts(x)` then it will be run in a
> `jsdom` test environment (which emulates a browser environment w/ a pure JS implementation of DOM
> and BOM that is headless).

Finally, here's a simple test `ui.test.ts` that uses
[`ink-testing-library`](https://github.com/vadimdemedes/ink-testing-library) to create the UI test.

```typescript
import React from "react"
import chalk from "chalk"
import { render } from "ink-testing-library"
import App from "../ui"

describe("ink test suite", () => {
  test("greet unknown user", () => {
    const { lastFrame } = render(React.createElement(App, null))
    expect(lastFrame()).toEqual("Hello, \u001b[32mStranger\u001b[39m")
  })

  test("greet user with a name", () => {
    const { lastFrame } = render(React.createElement(App, { name: "Jane" }))
    expect(lastFrame()).toEqual(chalk`Hello, {green Jane}`)
  })
})
```

> ⚡ Here's a
> [commit](https://github.com/nazmulidris/ts-scratch/commit/2cf82a147dcb48bcfccbf899c35fff859336d466)
> that adds all the testing stuff.
