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

- [Introduction](#introduction)
- [What is Ink](#what-is-ink)
- [Items covered in this article](#items-covered-in-this-article)
- [Small example - moving a component with arrow keys](#small-example---moving-a-component-with-arrow-keys)
- [Medium size example - keyboard input & focus manipulation](#medium-size-example---keyboard-input--focus-manipulation)
- [Large example - full screen (terminal) app using Flexbox and keyboard input](#large-example---full-screen-terminal-app-using-flexbox-and-keyboard-input)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

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

## Items covered in this article

There are a wealth of examples that you can find in the
[ink repo](https://github.com/nazmulidris/ink/tree/master/examples) itself. I suggest browsing
through all of them to get some sense of how to use all the host components and hooks.

In this article, we will walk through three examples in order to get a sense of how to use the
entire API surface of Ink. There are a lot of community contributions in the form of npm packages
that are built using ink that we will not cover here. These examples will cover the usage of the
following API surface of ink.

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

> 🪄 You can find the source code for these examples in the
> [ink-cli-app3](https://github.com/nazmulidris/ts-scratch/tree/main/ink-cli-app3/) repo. Please
> clone this repo to run the samples below on your computer.
>
> Then navigate to the `ts-scratch/ink-cli-app3/` folder which contains the following.
>
> 1. `package.json` and npm start scripts. Make sure to run `npm i` after cloning this repo.
> 2. IDEA & VSCode projects. You can open this folder in your favorite IDE.

---

## Small example - moving a component with arrow keys

This small example is a CLI app that allows the user to move a component on the screen the cursor
around using arrow up, down, left, and right keys. It shows how we can use the `useInput()` hook to
make this happen. Here's the code.

> 🪄 Here's the source code for
> [`use-input.tsx`](https://github.com/nazmulidris/ts-scratch/blob/main/ink-cli-app3/src/examples/use-input.tsx).

```tsx
import React, { useState } from "react"
import { Box, render, Text, useApp, useInput } from "ink"
import { _callIfTruthy } from "r3bl-ts-utils"

const UseInputExample = () => {
  const { exit } = useApp()
  const [x, setX] = useState(1)
  const [y, setY] = useState(1)
  useInput((input, key) => {
    _callIfTruthy(input === "q", () => exit())
    _callIfTruthy(key.leftArrow, () => setX(Math.max(1, x - 1)))
    _callIfTruthy(key.rightArrow, () => setX(Math.min(20, x + 1)))
    _callIfTruthy(key.upArrow, () => setY(Math.max(1, y - 1)))
    _callIfTruthy(key.downArrow, () => setY(Math.min(10, y + 1)))
  })

  return (
    <Box flexDirection="column">
      <Text color={"green"}>Use arrow keys to move the X.</Text>
      <Text color={"red"}>Press “q” to exit.</Text>
      <Box height={12} paddingLeft={x} paddingTop={y}>
        <Text color={"blue"}>X</Text>
      </Box>
    </Box>
  )
}

render(<UseInputExample />)
```

Here's the output that it produces.

<pre><span style="color:#2f9ece">$ </span><span style="color:#F8F8F2">node</span> <span style="color:#FF79C6">-r</span> <span style="color:#FF79C6">tsm</span> <span style="color:#FF79C6"><u style="text-decoration-style:single">src/examples/use-input.tsx</u></span> 
<span style="color:#4E9A06">Use arrow keys to move the X.</span>
<span style="color:#CC0000">Press “q” to exit.</span>

   <span style="color:#3465A4">X</span>

</pre>

Here's a brief description of the lifecycle of the app.

1. First it is started from the terminal when the script is executed using
   <code><span style="color:#3A46FE">n</span><span style="color:#374AFE">o</span><span style="color:#334DFE">d</span><span style="color:#3051FD">e</span><span style="color:#2D55FC">
   </span><span style="color:#2A59FB">-</span><span style="color:#275DFB">r</span><span style="color:#2461F9">
   </span><span style="color:#2166F8">t</span><span style="color:#1E6AF7">s</span><span style="color:#1B6EF5">m</span><span style="color:#1972F4">
   </span><span style="color:#1676F2">s</span><span style="color:#147BF0">r</span><span style="color:#127FEE">c</span><span style="color:#1083EC">/</span><span style="color:#0E87E9">e</span><span style="color:#0C8CE7">x</span><span style="color:#0A90E4">a</span><span style="color:#0994E2">m</span><span style="color:#0798DF">p</span><span style="color:#069CDC">l</span><span style="color:#05A0D9">e</span><span style="color:#04A4D6">s</span><span style="color:#03A8D3">/</span><span style="color:#02ACD0">u</span><span style="color:#02B0CD">s</span><span style="color:#01B4C9">e</span><span style="color:#01B8C6">-</span><span style="color:#01BCC2">i</span><span style="color:#01BFBF">n</span><span style="color:#01C3BB">p</span><span style="color:#01C7B7">u</span><span style="color:#01CAB3">t</span><span style="color:#02CEAF">.</span><span style="color:#02D1AB">t</span><span style="color:#03D4A7">s</span><span style="color:#04D7A3">x</span></code>.
2. Once the `useInput()` hook is called the Node.js process is listening for input events on
   `process.stdin`. This prevents the Node.js process from exiting once the app is rendered once.
3. When the user presses up, down, left, or right, this causes the X and Y padding of the app to be
   changed, which makes it look like the `X` is moving around the terminal.
4. When the user presses <kbd>q</kbd> or <kbd>Ctrl+c</kbd> this will exit the Node.js process. The
   `useApp()` hook supplies an `exit()` function which can be used to do this.

---

## Medium size example - keyboard input & focus manipulation

This medium size example goes deep into the hooks `useFocus()` and `useFocusManager()` to
demonstrate how to manage input focus in a CLI app. Not only can <kbd>Tab</kbd> and
<kbd>Shift+Tab</kbd> be used to move keyboard focus from one component to another, but shortcuts are
provided that allow giving focus to a given component (by pressing <kbd>Shift+1</kbd> to focus the
first component, <kbd>Shift+2</kbd> the second, and <kbd>Shift+3</kbd> the third). A debug component
is provided which shows what keys are actually being pressed. Additionally, flexbox is used via
`Box` to organize the components in a sophisticated way.

> 🪄 Here's the source code for
> [`use-focus.tsx`](https://github.com/nazmulidris/ts-scratch/blob/main/ink-cli-app3/src/examples/use-focus.tsx).

```tsx
import { Box, Key, Newline, render, Text, useApp, useFocus, useFocusManager, useInput } from "ink"
import {
  _callIfTrue,
  KeyPressed,
  keyPressedToString,
  makeReactElementFromArray,
  StateHook,
} from "r3bl-ts-utils"
import React, { FC, useState } from "react"

const UseFocusExample: FC = function (): JSX.Element {
  const userInputPressed = useKeyboard()

  return (
    <Box flexDirection="column">
      {userInputPressed && (
        <Row_Debug keyPressed={userInputPressed?.key} inputPressed={userInputPressed?.input} />
      )}
      <Row_Instructions />
      <Row_FocusableItems />
    </Box>
  )
}

interface UserInput {
  input: string
  key: Key
}

function useKeyboard(): UserInput | undefined {
  const { exit } = useApp()
  const { focus } = useFocusManager()

  const [userInputPressed, setUserInputPressed]: StateHook<UserInput | undefined> = useState()

  useInput((input, key) => {
    setUserInputPressed({ input, key })
    _callIfTrue(input === "q", exit)
    _callIfTrue(key.ctrl && input === "q", exit)
    _callIfTrue(input === "!", () => focus("1"))
    _callIfTrue(input === "@", () => focus("2"))
    _callIfTrue(input === "#", () => focus("3"))
  })

  return userInputPressed
}

function Row_Debug(props: { keyPressed: KeyPressed; inputPressed: KeyPressed }) {
  const { inputPressed, keyPressed } = props
  return (
    <>
      <Text color={"magenta"}>input: {keyPressedToString(inputPressed)}</Text>
      <Text color={"gray"}>key: {keyPressedToString(keyPressed)}</Text>
    </>
  )
}

const Row_Instructions: FC = function (): JSX.Element {
  return makeReactElementFromArray(
    [
      ["blue", "Press Tab to focus next element"],
      ["blue", "Shift+Tab to focus previous element"],
      ["blue", "Esc to reset focus."],
      ["green", "Press Shift+<n> to directly focus on 1st through 3rd item."],
      ["red", "To exit, press Ctrl+q, or q"],
    ],
    (item: string[], id: number): JSX.Element => (
      <Text color={item[0]} key={id}>
        {item[1]}
      </Text>
    )
  )
}

const Row_FocusableItems: FC = function (): JSX.Element {
  return (
    <Box padding={1} flexDirection="row" justifyContent={"space-between"}>
      <FocusableItem id="1" label="First" />
      <FocusableItem id="2" label="Second" />
      <FocusableItem id="3" label="Third" />
    </Box>
  )
}

const FocusableItem: FC<{ label: string; id: string }> = function ({ label, id }): JSX.Element {
  const { isFocused } = useFocus({ id })
  return (
    <Text>
      {label}
      {isFocused ? (
        <>
          <Newline />
          <Text color="green">(*)</Text>
        </>
      ) : (
        <>
          <Newline />
          <Text color="gray">n/a</Text>
        </>
      )}
    </Text>
  )
}

render(<UseFocusExample />)
```

This is what the output looks like when <kbd>Shift+2</kbd> (ie `@`) is typed to gain focus to the
"Second" component.

<pre><span style="color:#2f9ece">$ </span><span style="color:#F8F8F2">node</span> <span style="color:#FF79C6">-r</span> <span style="color:#FF79C6">tsm</span> <span style="color:#FF79C6"><u style="text-decoration-style:single">src/examples/use-focus.tsx</u></span>
<span style="color:#75507B">input: @</span>
<span style="color:#88807C">key: n/a</span>
<span style="color:#3465A4">Press Tab to focus next element</span>
<span style="color:#3465A4">Shift+Tab to focus previous element</span>
<span style="color:#3465A4">Esc to reset focus.</span>
<span style="color:#4E9A06">Press Shift+&lt;n&gt; to directly focus on 1st through 3rd item.</span>
<span style="color:#CC0000">To exit, press Ctrl+q, or q</span>

 First                      Second                      Third
 <span style="color:#88807C">n/a</span>                        <span style="color:#4E9A06">(*)</span>                         <span style="color:#88807C">n/a</span>

</pre>

Here's a brief description of the lifecycle of the app.

1. You can launch this app by typing
   <code><span style="color:#D504A6">n</span><span style="color:#D203AA">o</span><span style="color:#CF02AE">d</span><span style="color:#CC01B2">e</span><span style="color:#C801B5">
   </span><span style="color:#C501B9">-</span><span style="color:#C101BD">r</span><span style="color:#BD01C1">
   </span><span style="color:#BA01C4">t</span><span style="color:#B601C8">s</span><span style="color:#B201CB">m</span><span style="color:#AE02CF">
   </span><span style="color:#AA03D2">s</span><span style="color:#A603D5">r</span><span style="color:#A204D8">c</span><span style="color:#9E06DB">/</span><span style="color:#9A07DE">e</span><span style="color:#9608E1">x</span><span style="color:#910AE3">a</span><span style="color:#8D0BE6">m</span><span style="color:#890DE8">p</span><span style="color:#850FEB">l</span><span style="color:#8111ED">e</span><span style="color:#7C13EF">s</span><span style="color:#7815F1">/</span><span style="color:#7418F3">u</span><span style="color:#701AF5">s</span><span style="color:#6B1DF6">e</span><span style="color:#6720F8">-</span><span style="color:#6322F9">i</span><span style="color:#5F25FA">n</span><span style="color:#5B28FB">p</span><span style="color:#572CFC">u</span><span style="color:#532FFD">t</span><span style="color:#4F32FD">.</span><span style="color:#4B35FE">t</span><span style="color:#4739FE">s</span><span style="color:#443DFE">x</span></code>.
2. The main UI is a flexbox container (`flexDirection="column"`) which lays out three components top
   to bottom.
   1. The first row is `Row_Debug` component which displays which key is currently pressed if any.
   2. The second row is `Row_Instructions` component which displays the keyboard shortcuts to use to
      interact with the CLI app.
   3. The third row is `Row_FocusableItems` component which is another flexbox container
      (`flexDirection="row"` this time) which lays out the focusable `Text` components left to
      right.
3. The custom hook `useKeyboard()` gets the key that is pressed (the `UserInput` object). It works
   hand in hand w/ the `FocusableItem` component in order to make all of this work.
   1. This custom hook just calls the `useInput()` hook (just like in the
      [example above](#small-example---moving-a-component-with-arrow-keys)). This prevents the
      Node.js process from exiting once the app is rendered once.
   2. When the user presses keys, this is saved to the state and then the `Row_Debug` is updated w/
      this information.
   3. When <kbd>Shift+1</kbd>, <kbd>Shift+2</kbd>, <kbd>Shift+3</kbd> is pressed, the
      `const { focus } = useFocusManager()` hook is used to directly bring focus to the `Text`
      components (via a call to `focus(id)`. As a setup for this to work, when each focusable
      component is declared (inside `Row_FocusableItems`) the `useFocus({ id })` hook has to be
      given the same ID that is used to bring focus directly to it.
   4. In `FocusableItem`, the `isFocused` boolean from the hook call
      `const { isFocused } = useFocus({ id })` is used to determine whether that component currently
      has keyboard focus and if so, it renders itself slightly differently.
   5. When the user presses <kbd>q</kbd>, <kbd>Ctrl+q</kbd>, or <kbd>Ctrl+c</kbd> this will exit the
      Node.js process. The `useApp()` hook supplies an `exit()` function which can be used to do
      this.

---

## Large example - full screen (terminal) app using Flexbox and keyboard input
