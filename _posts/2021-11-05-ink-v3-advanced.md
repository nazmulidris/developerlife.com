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
- [Use the template to get a bare-bones CLI app](#use-the-template-to-get-a-bare-bones-cli-app)
- [Build a CLI app using Ink and flexbox w/ Redux](#build-a-cli-app-using-ink-and-flexbox-w-redux)
  - [The main app, Flexbox, and Redux store](#the-main-app-flexbox-and-redux-store)
  - [Flexbox](#flexbox)
  - [Redux store and effect function](#redux-store-and-effect-function)
  - [Underlying / managed Timer and Redux store connector](#underlying--managed-timer-and-redux-store-connector)
  - [Reducer, state, actions](#reducer-state-actions)
  - [Tests](#tests)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

---

## Introduction

This article is an advanced guide to using Ink v3.2.0 (with TypeScript and React) to create CLI
apps. IDEA Ultimate / Webstorm project files are provided.

To get started w/ Ink v3 please checkout this [introductory article][0.1].

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

## Use the template to get a bare-bones CLI app

The [first tutorial][1.5] was all about the mechanics of setting up an Ink CLI app, and
understanding executable modules in Node.js, configuring Jest, etc. Now we can get into Ink itself
and the CLI apps we can build w/ it.

The first thing we must do is clone the [`ts-ink-template`][1.6] repo. This will get our project
bootstrapped w/ all the configuration settings in `package.json`, `tsconfig.json`, and
`jest.config.js` sorted for us! It also sets up Eslint for TypeScript. And provide npm scripts,
along w/ run configurations for IDEA, and even settings for VSCode.

> 💡 In IDEA, you can simply run the `Run all tests (watch)` run configuration to continuously run
> Jest and execute all your tests when any file changes. This is a great way to see if the code that
> you're writing is breaking anything that you've already written.

> 💡 If you install the
> [Jest extension](https://marketplace.visualstudio.com/items?itemName=Orta.vscode-jest) in VSCode,
> you can do the same thing as well (`settings.json` is provided in this template for VSCode, so
> this extension is automatically configured for you).

Here are the 2 main TSX files we need to look at to get started.

1. `source/cli.tsx` - This uses `commander` to parse the command line arguments that may be passed
   to the CLI app. So if we want to change the arguments that the app takes, we have to change the
   `commander` options. The values that we pass via the command line are actually passed as props to
   the `App` component described next.

2. `source/ui.tsx` - We use React and Ink host components in this file to define the `App` component
   which takes props that correspond to the values which are passed into the command line above.

Also, we can customize the name of our app. Currently it's called `"name": "ts-ink-template-app"` in
`package.json` and we can change it to `ink-cli-app2`. If we want to be able to run this app from
anywhere on your computer, we have to run `npm link`. In this tutorial, we are just going to use the
`npm start` script that is provided w/ the template.

To see the app in action we can simply run the following.

```shell
$ npm start -- -h
```

And it will display the help screen.

<pre><span style="color:#069CDC;">&gt;</span><span style="color:#05A0D9;"> </span><span style="color:#04A4D6;">i</span><span style="color:#03A8D3;">n</span><span style="color:#02ACD0;">k</span><span style="color:#02B0CD;">-</span><span style="color:#01B4C9;">c</span><span style="color:#01B8C6;">l</span><span style="color:#01BCC2;">i</span><span style="color:#01BFBF;">-</span><span style="color:#01C3BB;">a</span><span style="color:#01C7B7;">p</span><span style="color:#01CAB3;">p</span><span style="color:#02CEAF;">2</span><span style="color:#02D1AB;">@</span><span style="color:#03D4A7;">0</span><span style="color:#04D7A3;">.</span><span style="color:#05DA9F;">0</span><span style="color:#06DD9B;">.</span><span style="color:#08E097;">0</span><span style="color:#09E393;"> </span><span style="color:#0BE58F;">s</span><span style="color:#0CE88A;">t</span><span style="color:#0EEA86;">a</span><span style="color:#10EC82;">r</span><span style="color:#12EE7E;">t</span>
<span style="color:#03A8D3;">&gt;</span><span style="color:#02ACD0;"> </span><span style="color:#02B0CD;">d</span><span style="color:#01B4C9;">i</span><span style="color:#01B8C6;">s</span><span style="color:#01BCC2;">t</span><span style="color:#01BFBF;">/</span><span style="color:#01C3BB;">c</span><span style="color:#01C7B7;">l</span><span style="color:#01CAB3;">i</span><span style="color:#02CEAF;">.</span><span style="color:#02D1AB;">j</span><span style="color:#03D4A7;">s</span><span style="color:#04D7A3;"> </span><span style="color:#05DA9F;">&quot;</span><span style="color:#06DD9B;">-</span><span style="color:#08E097;">h</span><span style="color:#09E393;">&quot;</span>

<span style="color:#01BFBF;">U</span><span style="color:#01C3BB;">s</span><span style="color:#01C7B7;">a</span><span style="color:#01CAB3;">g</span><span style="color:#02CEAF;">e</span><span style="color:#02D1AB;">:</span><span style="color:#03D4A7;"> </span><span style="color:#04D7A3;">c</span><span style="color:#05DA9F;">l</span><span style="color:#06DD9B;">i</span><span style="color:#08E097;"> </span><span style="color:#09E393;">[</span><span style="color:#0BE58F;">o</span><span style="color:#0CE88A;">p</span><span style="color:#0EEA86;">t</span><span style="color:#10EC82;">i</span><span style="color:#12EE7E;">o</span><span style="color:#15F079;">n</span><span style="color:#17F275;">s</span><span style="color:#19F471;">]</span>

<span style="color:#03D4A7;">O</span><span style="color:#04D7A3;">p</span><span style="color:#05DA9F;">t</span><span style="color:#06DD9B;">i</span><span style="color:#08E097;">o</span><span style="color:#09E393;">n</span><span style="color:#0BE58F;">s</span><span style="color:#0CE88A;">:</span>
<span style="color:#06DD9B;"> </span><span style="color:#08E097;"> </span><span style="color:#09E393;">-</span><span style="color:#0BE58F;">n</span><span style="color:#0CE88A;">,</span><span style="color:#0EEA86;"> </span><span style="color:#10EC82;">-</span><span style="color:#12EE7E;">-</span><span style="color:#15F079;">n</span><span style="color:#17F275;">a</span><span style="color:#19F471;">m</span><span style="color:#1CF66D;">e</span><span style="color:#1FF769;"> </span><span style="color:#22F865;">&lt;</span><span style="color:#24FA60;">n</span><span style="color:#27FB5C;">a</span><span style="color:#2BFC58;">m</span><span style="color:#2EFD54;">e</span><span style="color:#31FD50;">&gt;</span><span style="color:#34FE4C;"> </span><span style="color:#38FE49;"> </span><span style="color:#3BFE45;">n</span><span style="color:#3FFE41;">a</span><span style="color:#43FE3D;">m</span><span style="color:#46FE3A;">e</span><span style="color:#4AFE36;"> </span><span style="color:#4EFE33;">t</span><span style="color:#52FD30;">o</span><span style="color:#56FC2C;"> </span><span style="color:#5AFB29;">d</span><span style="color:#5EFA26;">i</span><span style="color:#62F923;">s</span><span style="color:#66F820;">p</span><span style="color:#6AF61E;">l</span><span style="color:#6FF51B;">a</span><span style="color:#73F318;">y</span>
<span style="color:#0BE58F;"> </span><span style="color:#0CE88A;"> </span><span style="color:#0EEA86;">-</span><span style="color:#10EC82;">h</span><span style="color:#12EE7E;">,</span><span style="color:#15F079;"> </span><span style="color:#17F275;">-</span><span style="color:#19F471;">-</span><span style="color:#1CF66D;">h</span><span style="color:#1FF769;">e</span><span style="color:#22F865;">l</span><span style="color:#24FA60;">p</span><span style="color:#27FB5C;"> </span><span style="color:#2BFC58;"> </span><span style="color:#2EFD54;"> </span><span style="color:#31FD50;"> </span><span style="color:#34FE4C;"> </span><span style="color:#38FE49;"> </span><span style="color:#3BFE45;"> </span><span style="color:#3FFE41;"> </span><span style="color:#43FE3D;"> </span><span style="color:#46FE3A;">d</span><span style="color:#4AFE36;">i</span><span style="color:#4EFE33;">s</span><span style="color:#52FD30;">p</span><span style="color:#56FC2C;">l</span><span style="color:#5AFB29;">a</span><span style="color:#5EFA26;">y</span><span style="color:#62F923;"> </span><span style="color:#66F820;">h</span><span style="color:#6AF61E;">e</span><span style="color:#6FF51B;">l</span><span style="color:#73F318;">p</span><span style="color:#77F116;"> </span><span style="color:#7BF014;">f</span><span style="color:#80ED11;">o</span><span style="color:#84EB0F;">r</span><span style="color:#88E90E;"> </span><span style="color:#8CE70C;">c</span><span style="color:#90E40A;">o</span><span style="color:#95E108;">m</span><span style="color:#99DF07;">m</span><span style="color:#9DDC06;">a</span><span style="color:#A1D905;">n</span><span style="color:#A5D604;">d</span></pre>

If we don't pass any arguments in and run the following.

```shell
$ npm run start
```

We get this output.

<pre>&gt; ts-ink-template-app@0.0.1 start
&gt; dist/cli.js

Hello, <span style="color:#A3BE8C">Stranger</span>
</pre>

And if we pass it a name argument, like so.

```shell
$ npm run start -- -n Grogu
```

We get this output.

<pre>&gt; ts-ink-template-app@0.0.1 start
&gt; dist/cli.js &quot;-n&quot; &quot;Grogu&quot;

Hello, <span style="color:#A3BE8C">Grogu</span>
</pre>

There are a lot of great [scripts][1.7] that we can use, such as:

- `npm run test-watch` - This will run Jest and watch your source code for changes and re-run all
  the tests.
- An IDEA run configuration is also provided so you run and watch all the Jest tests in IDEA!
- `npm run dev` - This will wat your source code for changes and run `tsc` to compile all the TS to
  JS and also run the app so you can see the changes in a terminal. Hot reloading 🌶 for CLI apps 🎉.

## Build a CLI app using Ink and flexbox w/ Redux

Starting w/ this simple and functional base we can now start adding some interesting Ink host
components and React hooks into the mix! In this section we will build a React component that uses
hooks (`useEffect`), Redux (`useSelector`), timers (`setInterval`), and even flexbox!

### The main app, Flexbox, and Redux store

Let's rename `ui.tsx` to `app.tsx` and update it w/ the following code.

```tsx
import React, { FC } from "react"
import { Box, Text } from "ink"
import { TimerDisplayComponent, effectFn, store } from "./timer-component"
import { Provider } from "react-redux"

// App functional component.
const Style = {
  backgroundColor: "#161b22",
  textColor: "#e6e6e6",
  brandColor: "#2f9ece",
}
type PropTypes = {
  name?: string
}
export const App: FC<PropTypes> = ({ name = "Stranger" }) => {
  return (
    <Box
      borderStyle="round"
      borderColor={Style.brandColor}
      flexDirection="column"
      alignItems="center"
    >
      <Text color={Style.textColor} backgroundColor={Style.backgroundColor}>
        {`👋 Hello 👋`}
      </Text>
      <Text bold color={Style.textColor} backgroundColor={Style.brandColor}>
        {name}
      </Text>
      <Provider store={store}>
        <TimerDisplayComponent onComponentMountEffect={effectFn} />
      </Provider>
    </Box>
  )
}
```

### Flexbox

The `Box` host component is our Flexbox container. It is used to wrap other nested host components
(`Text`) and composite components (`TimerDisplayComponent`) w/ [flexbox directives][1.3] that you
expect.

There's no CSS styling since this isn't a web app and there's no browser. The declarative styling
that we would normally express in the CSS now has to be expressed in JSX (thankfully also
declaratively). If you've ever used [React Native][1.6], this should seem familiar.

And here's the `TimerDisplayComponent` composite component which is a functional component that uses
React hooks (`useEffect`, `useSelector`), and a is passed a function via `onComponentMountEffect`
props to start the timer that will update the Redux store 5 times w/ a delay of 100 ms.

```tsx
import React, { EffectCallback, FC } from "react"
import { Text } from "ink"
import { useSelector } from "react-redux"
import { State } from "./reducer"

type PropType = {
  onComponentMountEffect: EffectCallback
}

export const TimerDisplayComponent: FC<PropType> = ({ onComponentMountEffect }) => {
  const state = useSelector((state) => state) as State

  React.useEffect(onComponentMountEffect, [] /* componentDidMount */)

  return render()

  function render() {
    return (
      <Text color={"green"}>
        [{state.count} tests passed]
        {showSkullIfTimerIsStopped()}
      </Text>
    )
  }

  function showSkullIfTimerIsStopped() {
    return !state.run ? "💀" : null
  }
}
```

### Redux store and effect function

Here's the code that creates the Redux store and calls the function that generates the effect
function (that is passed to the component).

```tsx
import { EffectCallback } from "react"
import { configureStore, EnhancedStore } from "@reduxjs/toolkit"
import { Action, reducerFn, ReducerType } from "./reducer"
import { createAndManageTimer } from "./timer-store-connector"

// Create Redux store.
export type TimerStore = EnhancedStore<ReducerType, Action, any>
export const store = configureStore<ReducerType>({
  reducer: reducerFn,
}) as TimerStore

// Create Timer and connect it to the Redux store.
export const effectFn: EffectCallback = createAndManageTimer(store)
```

### Underlying / managed Timer and Redux store connector

This functional component is very simple and it relies on the Redux store's state in order to render
itself. It does use 1 effect - this is run `onComponentDidMount` and kicks of the `Timer`. Here's
the code that generates the function which is passed to the effect (in `timer-store-connector.tsx`).

```tsx
import { EffectCallback } from "react"
import { _also, createTimer, Timer } from "r3bl-ts-utils"
import { TimerStore } from "./store"

/**
 * Create a Timer and manage it by connecting it to the Redux store (dispatch the right actions to
 * it based on the Timer's lifecycle).
 */
export function createAndManageTimer(store: TimerStore): EffectCallback {
  const maxCount = 4
  const timer: Timer = _also(
    createTimer("Timer in App, count from 0 to 5, at 1s interval", 1000),
    (it) => {
      it.onStart = getOnStartFn()
      it.onTick = getOnTickFn()
      it.onStop = getOnStopFn()
    }
  )
  return effectFn

  /* Function that is passed to useEffect. */
  function effectFn() {
    if (!timer.isRunning) {
      timer.startTicking()
    }
    return () => {
      if (timer.isRunning) timer.stopTicking()
    }
  }

  function getOnStartFn() {
    return () => store.dispatch({ type: "startTimer" })
  }

  function getOnTickFn() {
    return () => {
      // Update count in UI.
      store.dispatch({
        type: "setCount",
        payload: timer.counter.value,
      })

      // Stop timer when maxCount is reached.
      if (timer.counter.value >= maxCount && timer.isRunning) timer.stopTicking()
    }
  }

  function getOnStopFn() {
    return () => store.dispatch({ type: "stopTimer" })
  }
}
```

This function does quite a bit of heavy lifting. It connects the lifecycle of the underlying `Timer`
which it creates to the Redux store's state (by dispatching actions) that it is passed as an
argument. Here are some other notes on this code.

1. There's a `Timer` (imported from `r3bl-ts-utils`) that actually manages a `setInterval()`
   underlying timer. This timer must be started and stopped, and once started, it calls the tick
   function at the given interval until the timer is stopped. The tick function also terminates the
   timer after its been called a few times.
2. The lifecycles of the state and timer objects are separate, one doesn't know about the other. For
   this reason, some glue has to be added in order to tie the lifecycle of the `Timer` to the Redux
   store's state.

### Reducer, state, actions

Finally, here's the reducer function, actions, and state, which constitute all the Redux code.

```tsx
import { Reducer } from "react"
import _ from "lodash"

export type State = {
  count: number
  run: boolean
}

interface ActionStartTimer {
  type: "startTimer"
}
interface ActionStopTimer {
  type: "stopTimer"
}
interface ActionSetCount {
  type: "setCount"
  payload: number
}
export type Action = ActionStartTimer | ActionStopTimer | ActionSetCount

export type ReducerType = Reducer<State | undefined, Action>

export function reducerFn(current: State | undefined, action: Action): State {
  // Initial state.
  if (!current) {
    return {
      count: 0,
      run: false,
    }
  }

  const currentCopy: State = _.clone(current)
  switch (action.type) {
    case "setCount":
      currentCopy.count = action.payload
      break
    case "startTimer":
      currentCopy.run = true
      break
    case "stopTimer":
      currentCopy.run = false
      break
  }
  return currentCopy
}
```

When you run the following command in the terminal.

```shell
$ npm run start -- -n Grogu
```

It will produce the following output 🎉.

<pre>&gt; ink-cli-app2@0.0.0 start
&gt; dist/cli.js &quot;-n&quot; &quot;Grogu&quot;

<span style="color:#2F9ECE">╭─────────────────────────────────────────────────╮</span>
<span style="color:#2F9ECE">│</span>                   <span style="background-color:#161B22"><span style="color:#E6E6E6">👋 Hello 👋</span></span>                   <span style="color:#2F9ECE">│</span>
<span style="color:#2F9ECE">│</span>                      <span style="background-color:#2F9ECE"><span style="color:#E6E6E6"><b>Grogu</b></span></span>                      <span style="color:#2F9ECE">│</span>
<span style="color:#2F9ECE">│</span>               <span style="color:#A3BE8C">[4 tests passed]💀</span>                <span style="color:#2F9ECE">│</span>
<span style="color:#2F9ECE">╰─────────────────────────────────────────────────╯</span>
</pre>

---

### Tests

Here's a UI test that exercises all the classes that we have created so far.

```tsx
import { Provider } from "react-redux"
import {
  Action,
  TimerDisplayComponent,
  reducerFn,
  ReducerType,
  TimerStore,
} from "../timer-component"
import React from "react"
import { render } from "ink-testing-library"
import { configureStore, EnhancedStore } from "@reduxjs/toolkit"

let store: TimerStore

beforeEach(() => {
  // Create Redux store.
  store = configureStore<ReducerType>({
    reducer: reducerFn,
  }) as EnhancedStore<ReducerType, Action, any>
})

describe("ComponentToDisplayTimer", () => {
  test("renders correctly when timer is not started", () => {
    const { lastFrame } = render(React.createElement(TestFC, null))
    expect(lastFrame()).toContain("[0 tests passed]💀")
  })
})

describe("ComponentToDisplayTimer", () => {
  test("renders correctly when timer is started (which calls the tickFn)", () => {
    // Simulate a timer that is started, and then a tickFn is executed.
    store.dispatch({
      type: "startTimer",
    })
    store.dispatch({
      type: "setCount",
      payload: 10,
    })
    const { lastFrame } = render(React.createElement(TestFC, null))
    expect(lastFrame()).toContain("[10 tests passed]")
  })
})

const TestFC = () => (
  <Provider store={store}>
    <TimerDisplayComponent onComponentMountEffect={() => {}} />
  </Provider>
)
```
