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
- [Example 1 - moving a component with arrow keys](#example-1---moving-a-component-with-arrow-keys)
- [Example 2 - keyboard input & focus manipulation](#example-2---keyboard-input--focus-manipulation)
- [Example 3 - full screen app](#example-3---full-screen-app)

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

## Example 1 - moving a component with arrow keys

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

<pre class="pre-manual-highlight"><span style="color:#2f9ece">$ </span><span style="color:#F8F8F2">node</span> <span style="color:#FF79C6">-r</span> <span style="color:#FF79C6">tsm</span> <span style="color:#FF79C6"><u style="text-decoration-style:single">src/examples/use-input.tsx</u></span> 
<span style="color:#4E9A06">Use arrow keys to move the X.</span>
<span style="color:#CC0000">Press “q” to exit.</span>

   <span style="color:#3465A4">X</span>

</pre>

Here's a brief description of the lifecycle of the app.

1. First it is started from the terminal when the script is executed using the `node ...` command
   shown above.
2. Once the `useInput()` hook is called the Node.js process is listening for input events on
   `process.stdin`. This prevents the Node.js process from exiting once the app is rendered once.
3. When the user presses up, down, left, or right, this causes the X and Y padding of the app to be
   changed, which makes it look like the `X` is moving around the terminal.
4. When the user presses <kbd>q</kbd> or <kbd>Ctrl+c</kbd> this will exit the Node.js process. The
   `useApp()` hook supplies an `exit()` function which can be used to do this.

---

## Example 2 - keyboard input & focus manipulation

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
import { Box, Newline, render, Text, useApp, useFocus, useFocusManager } from "ink"
import {
  _callIfTrue,
  KeyboardInputHandlerFn,
  makeReactElementFromArray,
  useKeyboard,
  UserInputKeyPress,
} from "r3bl-ts-utils"
import React, { FC } from "react"

//#region Main functional component.
const UseFocusExample: FC = function (): JSX.Element {
  const [keyPress, inRawMode] = useKeyboard(
    onKeyPress.bind({ app: useApp(), focusManager: useFocusManager() })
  )

  return (
    <Box flexDirection="column">
      {keyPress && (
        <Row_Debug
          inRawMode={inRawMode}
          keyPressed={keyPress?.key}
          inputPressed={keyPress?.input}
        />
      )}
      <Row_Instructions />
      <Row_FocusableItems />
    </Box>
  )
}
//#endregion

//#region Keypress handler.
const onKeyPress: KeyboardInputHandlerFn = function (
  this: { app: ReturnType<typeof useApp>; focusManager: ReturnType<typeof useFocusManager> },
  userInputKeyPress: UserInputKeyPress
) {
  const { app, focusManager } = this
  const { exit } = app
  const { focus } = focusManager
  const { input, key } = userInputKeyPress

  _callIfTrue(input === "q", exit)
  _callIfTrue(key === "ctrl" && input === "q", exit)
  _callIfTrue(input === "!", () => focus("1"))
  _callIfTrue(input === "@", () => focus("2"))
  _callIfTrue(input === "#", () => focus("3"))
}
//#endregion

//#region UI.

function Row_Debug(props: {
  inRawMode: boolean
  keyPressed: string | undefined
  inputPressed: string | undefined
}) {
  const { inputPressed, keyPressed, inRawMode } = props
  return inRawMode ? (
    <>
      <Text color={"magenta"}>input: {inputPressed}</Text>
      <Text color={"gray"}>key: {keyPressed}</Text>
    </>
  ) : (
    <Text>keyb disabled</Text>
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

//#endregion

render(<UseFocusExample />)
```

This is what the output looks like when <kbd>Shift+2</kbd> (ie `@`) is typed to gain focus to the
"Second" component.

<pre class="pre-manual-highlight"><span style="color:#2f9ece">$ </span><span style="color:#F8F8F2">node</span> <span style="color:#FF79C6">-r</span> <span style="color:#FF79C6">tsm</span> <span style="color:#FF79C6"><u style="text-decoration-style:single">src/examples/use-focus.tsx</u></span>
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

1. First it is started from the terminal when the script is executed using the `node ...` command
   shown above.
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

## Example 3 - full screen app

This large size example is similar to the medium size one, except that it has a more complex UI. It
takes up the full height and width of the terminal that it is started in. And it listens for
keyboard input. It also uses a lot of custom hooks. For the UI, it splits the screen into two
columns, and adds components to each column. The UI also features a ticking clock that updates every
1 second.

> 🪄 Here's the source code for
> [`cli.tsx`](https://github.com/nazmulidris/ts-scratch/blob/main/ink-cli-app3/src/cli.tsx). You can
> find all the other files that are loaded by `cli.tsx` in the repo.

You can run the program using the following command
<code><font color="#F82067">n</font><font color="#F61D6B">p</font><font color="#F51A6F">m</font><font color="#F31874">
</font><font color="#F11678">r</font><font color="#EF137C">u</font><font color="#ED1180">n</font><font color="#EB0F84">
</font><font color="#E90D89">s</font><font color="#E60B8D">t</font><font color="#E40A91">a</font><font color="#E10895">r</font><font color="#DE0799">t</font><font color="#DB069E">-</font><font color="#D804A2">d</font><font color="#D504A6">e</font><font color="#D203AA">v</font></code>.

The following output is produced.

<pre>   <span style="color:#2F9ECE">╭──────────────────────────────────────────────────╮</span>
   <span style="color:#2F9ECE">│</span> <span style="background-color:#2F9ECE"><span style="color:#161B22"><b> 1st column </b></span></span>     <span style="background-color:#2F9ECE"><span style="color:#161B22"><b> 2nd column </b></span></span>                    <span style="color:#2F9ECE">│</span>
   <span style="color:#2F9ECE">│</span> <span style="background-color:#161B22"><span style="color:#2F9ECE"><b> Hello </b></span></span>          <span style="color:#E6E6E6">Item 1</span>                          <span style="color:#2F9ECE">│</span>
   <span style="color:#2F9ECE">│</span> <span style="color:#E6E6E6"><i><b>Stranger</b></i></span>         <span style="color:#E6E6E6">Item 2</span>                          <span style="color:#2F9ECE">│</span>
   <span style="color:#2F9ECE">│</span> <span style="background-color:#161B22"><span style="color:#2F9ECE"><b> 7:16:58 PM </b></span></span>     <span style="background-color:#2F9ECE"><span style="color:#161B22"><b> rows: 19, columns: 58 </b></span></span>         <span style="color:#2F9ECE">│</span>
   <span style="color:#2F9ECE">│</span> <span style="background-color:#161B22"><span style="color:#2F9ECE"><b> keyb enabled </b></span></span>                                   <span style="color:#2F9ECE">│</span>
   <span style="color:#2F9ECE">│</span>                                                  <span style="color:#2F9ECE">│</span>
   <span style="color:#2F9ECE">│</span>                                                  <span style="color:#2F9ECE">│</span>
   <span style="color:#2F9ECE">│</span>                                                  <span style="color:#2F9ECE">│</span>
   <span style="color:#2F9ECE">│</span>                                                  <span style="color:#2F9ECE">│</span>
   <span style="color:#2F9ECE">│</span>                                                  <span style="color:#2F9ECE">│</span>
   <span style="color:#2F9ECE">│</span>                                                  <span style="color:#2F9ECE">│</span>
   <span style="color:#2F9ECE">│</span>                                                  <span style="color:#2F9ECE">│</span>
   <span style="color:#2F9ECE">│</span>                                                  <span style="color:#2F9ECE">│</span>
   <span style="color:#2F9ECE">│</span>                                                  <span style="color:#2F9ECE">│</span>
   <span style="color:#2F9ECE">│</span>                                                  <span style="color:#2F9ECE">│</span>
   <span style="color:#2F9ECE">│</span>                                                  <span style="color:#2F9ECE">│</span>
   <span style="color:#2F9ECE">│</span>                                                  <span style="color:#2F9ECE">│</span>
   <span style="color:#2F9ECE">╰──────────────────────────────────────────────────╯</span><span style="color:#A1A1A1"> </span></pre>

Let's start w/ the main `app.tsx` file which is loaded via `cli.tsx` when the CLI app is run from
the terminal. Here's the one line that kicks everything off. `appFn` is a functional React
component.

```tsx
export const appFn: FC<{ name: string }> = ({ name }) => render(runHooks(name))
```

There are quite a few hooks which are executed (custom ones) that return an object, which is then
used by the `render` function to paint the UI. Here's what the `runHooks()` function looks like.

```tsx
function runHooks(name: string): LocalVars {
  usePreventProcessExitDuringTesting() // For testing using `npm run start-dev-watch`.
  const ttySize: TTYSize = useTTYSize()
  const time = useClock()
  const inRawMode = _let(useApp(), (it) => {
    const [_, inRawMode] = useKeyboard(onKeyboardFn.bind({ useApp: it }))
    return inRawMode
  })
  return {
    name,
    ttySize,
    time,
    inRawMode,
  }
}
interface LocalVars {
  ttySize: TTYSize
  inRawMode: boolean
  time: number
  name: string
}
```

Here is a brief overview of what the hooks do.

1. `usePreventProcessExitDuringTesting()` is a hook that comes from `r3bl-ts-utils`. It checks to
   see if the terminal is in raw mode (which is needed to enable keyboard input). If it's not in raw
   mode & keyboard input isn't possible, it just starts a `Timer` that doesn't do anything so that
   the Node.js process won't exit.
2. `useTTYSize()` is a hook that comes from `r3bl-ts-utils`. It provides the width and height of the
   terminal. This is used by the UI code below in order to take up the full width and height of the
   terminal. A "resize" listener is also registered so that if this terminal is resized, the new
   width and height, will be propagated and the UI re-rendered by React.
3. `useClock()` is a hook that comes from `r3bl-ts-utils` that simply starts a `Timer` and returns
   the current time. This time is displayed in the UI. It is updated every second and `setState()`
   is used in order to re-render the React UI.
4. `useKeyboard()` is a hook that comes from `r3bl-ts-utils` that simply attaches the given function
   to handle key input from the terminal. The `useApp()` hook is provided by Ink, and it allows
   access to the `exit()` function which can be used to exit the CLI app. This is useful when you
   create keyboard shortcuts that allow the user to exit the terminal app (eg: <kbd>Ctrl+q</kbd>).
5. Finally, an object (implementing `LocalVars`) is returned that is used by the `render()` function
   in order to paint the UI. This explicit passing of local state is meant to make it clear that
   this is a stateless functional component.

> 🪄 There are quite a few hooks & utility classes that are provided by `r3bl-ts-utils` that are used
> here (like `Timer`, `useTTYSize()`, `_let()`, etc.). Learn more about this package
> [here](https://github.com/r3bl-org/r3bl-ts-utils/).

Here's the code that provides the function for keyboard input handling.

```tsx
/**
 * 🪄 This function implements `KeyboardInputHandlerFn` interface.
 *
 * `this` binds it to an object of type OnKeyboardContext. Since this function is a callback that's
 * executed by Ink itself, it can't make any calls to hooks (like `useApp()` which is why re-binding
 * `this` is needed).
 */
function onKeyboardFn(
  this: {
    useApp: ReturnType<typeof useApp>
  },
  keyPress: UserInputKeyPress
) {
  const { useApp } = this

  _callIfTrue(keyPress.toString() === "ctrl+q", useApp.exit)
  _callIfTrue(keyPress.toString() === "q", useApp.exit)
  _callIfTrue(keyPress.toString() === "escape", useApp.exit)
}
```

And here's the function that renders the UI, using the objects in `LocalVars` that is generated by
`runHooks()`.

```tsx
//#region render().
function render(locals: LocalVars) {
  const { inRawMode, ttySize, time } = locals
  return (
    <Box flexDirection="row" alignSelf={"center"} height={ttySize.rows}>
      <Box
        borderStyle="round"
        borderColor={Style.brandColor}
        flexDirection="row"
        paddingLeft={1}
        paddingRight={1}
        width={Style.appWidth}
      >
        <Box flexDirection="column" flexBasis={Style.column1Width}>
          {renderColumn1(locals)}
          {TextStyle.subHeading(new Date(time).toLocaleTimeString())}
          {inRawMode ? TextStyle.subHeading("keyb enabled") : TextStyle.subHeading("keyb disabled")}
        </Box>
        <Box flexDirection="column" flexGrow={1}>
          {renderColumn2(locals)}
        </Box>
      </Box>
    </Box>
  )
}
//#endregion

//#region UI.
function renderColumn1(locals: LocalVars): JSX.Element {
  const { name } = locals
  return (
    <>
      {TextStyle.heading("1st column")}
      {TextStyle.subHeading("Hello")}
      {TextStyle.emphasis(name)}
    </>
  )
}

function renderColumn2(locals: LocalVars): JSX.Element {
  const { ttySize } = locals
  return (
    <>
      {TextStyle.heading("2nd column")}
      {TextStyle.styleNormal("Item 1")}
      {TextStyle.styleNormal("Item 2")}
      {TextStyle.heading(ttySize.toString())}
    </>
  )
}
//#endregion
```

Most of this code is flexbox in order to create the 2 column layout that takes up the entire width
and height of the terminal in which this app is run.
