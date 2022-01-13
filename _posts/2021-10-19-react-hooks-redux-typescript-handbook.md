---
author: Nazmul Idris
date: 2021-10-19 14:00:00+00:00
excerpt: |
  This handbook will take you thru using function components in React and Redux (using TypeScript) 
  and writing tests for them (using react-testing-library). IDEA Ultimate / Webstorm project files
  are provided. This handbook is written as a reference. You can easily jump to the section that
  is relevant to you or read them in any order that you like.
layout: post
title: "React hooks (v17.0.3) and Redux handbook using TypeScript (v4.3.4)"
categories:
  - TypeScript
  - React
  - Web
---

<img class="post-hero-image" src="{{ 'assets/react-hooks-handbook.svg' | relative_url }}"/>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [React](#react)
- [React Hooks](#react-hooks)
  - [Why?](#why)
  - [Limitations when using hooks (must follow these rules)](#limitations-when-using-hooks-must-follow-these-rules)
  - [Example w/ explanation of React memory model](#example-w-explanation-of-react-memory-model)
  - [useEffect](#useeffect)
    - [First render and subsequent re-renders using useRef and useEffect](#first-render-and-subsequent-re-renders-using-useref-and-useeffect)
  - [useState](#usestate)
    - [Example](#example)
    - [Shared stateful logic vs shared state](#shared-stateful-logic-vs-shared-state)
    - [Resources](#resources)
  - [useReducer](#usereducer)
    - [Two examples (one w/out network, and one w/ network)](#two-examples-one-wout-network-and-one-w-network)
  - [useCallback and useMemo](#usecallback-and-usememo)
  - [How to write complex function components](#how-to-write-complex-function-components)
  - [Custom hooks](#custom-hooks)
  - [References about hooks](#references-about-hooks)
- [Keyboard focus and React](#keyboard-focus-and-react)
  - [Declarative](#declarative)
  - [Imperative using useRef](#imperative-using-useref)
- [React and CSS](#react-and-css)
  - [CSS Modules example](#css-modules-example)
  - [Styled component example](#styled-component-example)
    - [TooltipOverlay w/ just CSS](#tooltipoverlay-w-just-css)
    - [TooltipOverlay w/ just React](#tooltipoverlay-w-just-react)
- [React and SVG](#react-and-svg)
  - [References on SVG and React](#references-on-svg-and-react)
- [Redux](#redux)
  - [Step 1 - Define the types for the state, action, then use them to create a reducer function](#step-1---define-the-types-for-the-state-action-then-use-them-to-create-a-reducer-function)
    - [No side effects, pure functions only](#no-side-effects-pure-functions-only)
  - [Step 2 - Create a store that uses this reducer function](#step-2---create-a-store-that-uses-this-reducer-function)
  - [Step 3 - Wrap the component(s) that will share this state with a Provider tag](#step-3---wrap-the-components-that-will-share-this-state-with-a-provider-tag)
  - [Step 4 - Subscribe your component(s) to the store with useSelector hook](#step-4---subscribe-your-components-to-the-store-with-useselector-hook)
  - [Step 5 - Make sure to dispatch actions in your component(s) to change shared state](#step-5---make-sure-to-dispatch-actions-in-your-components-to-change-shared-state)
  - [Immutability](#immutability)
  - [Selectors](#selectors)
    - [useSelector hook and React](#useselector-hook-and-react)
  - [Split and combine reducers](#split-and-combine-reducers)
  - [Enhancer](#enhancer)
    - [Intercept action dispatch](#intercept-action-dispatch)
    - [Intercept state creation](#intercept-state-creation)
    - [Combining both overrides](#combining-both-overrides)
  - [Middleware](#middleware)
  - [Async logic and data fetching](#async-logic-and-data-fetching)
    - [Redux "Thunk" middleware](#redux-thunk-middleware)
  - [Memoized selectors and Reselect](#memoized-selectors-and-reselect)
  - [Undo history](#undo-history)
    - [Data structure and algorithm](#data-structure-and-algorithm)
    - [Naive implementation](#naive-implementation)
    - [Using the redux-undo package](#using-the-redux-undo-package)
- [Testing with react-testing-library](#testing-with-react-testing-library)
  - [Use RTL instead of Enzyme](#use-rtl-instead-of-enzyme)
  - [Install the required packages for RTL](#install-the-required-packages-for-rtl)
  - [Basic unit tests](#basic-unit-tests)
  - [Complex unit tests](#complex-unit-tests)
  - [Basic UI tests](#basic-ui-tests)
  - [Complex UI tests](#complex-ui-tests)
  - [Writing integration tests](#writing-integration-tests)
    - [Install msw package](#install-msw-package)
    - [Mocking the server (REST API endpoints)](#mocking-the-server-rest-api-endpoints)
    - [Testing the mocked server (REST API endpoints) itself](#testing-the-mocked-server-rest-api-endpoints-itself)
    - [Using the mocked server in a UI test](#using-the-mocked-server-in-a-ui-test)
  - [Writing snapshot tests](#writing-snapshot-tests)
- [Data APIs for development](#data-apis-for-development)
- [Debugging in Webstorm or IDEA Ultimate](#debugging-in-webstorm-or-idea-ultimate)
- [Upgrade CRA itself to the latest version](#upgrade-cra-itself-to-the-latest-version)
- [Using CRA and environment variables](#using-cra-and-environment-variables)
- [CSS Reset](#css-reset)
- [Using CSS class pseudo selectors to style child elements of a parent](#using-css-class-pseudo-selectors-to-style-child-elements-of-a-parent)
- [Composition over inheritance](#composition-over-inheritance)
- [Callable](#callable)
- [TypeScript namespaces](#typescript-namespaces)
- [TypeScript readonly vs ReadonlyArray](#typescript-readonly-vs-readonlyarray)
- [TypeScript prop and state types](#typescript-prop-and-state-types)
- [TypeScript and ReactNode, ReactElement, JSX.Element](#typescript-and-reactnode-reactelement-jsxelement)
- [TypeScript types in array and object destructuring](#typescript-types-in-array-and-object-destructuring)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

This handbook and its accompanying TypeScript [code][gh-repo] is a reference guide on how to use
React Hooks with TypeScript (and write tests for them using react-testing-library).

1. This is not a React primer, and is primarily aimed at developers who know React class components
   and want to learn to use Hooks to create function components using TypeScript.
2. You can jump directly to any topic in the table of contents that you are curious about in this
   handbook, you don't have to read it from start to finish.

> ⚡ The source code for this handbook can be found in this [github repo][gh-repo].

> 💡 The source code project accompanying this handbook created using
> [`create-react-app` or CRA](https://github.com/facebook/create-react-app).

[gh-repo]: https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro

## React

To learn more about how React actually works and generates Virtual DOM objects which are then
rendered to the actual DOM, please refer to this great
[video on how to create a custom React renderer](https://youtu.be/CGpMlWVcHok). Here's the github
repo for the toy [React DOM Mini](https://github.com/sophiebits/react-dom-mini).

## React Hooks

React hooks exist because there were severe limitations in versions before React 16 on what function
components could do. And there were some problems w/ how class components function. By adding hooks
to function components, it basically eliminates these 2 groups of problems.

### Why?

Here are the details on the problems w/ class components mentioned above. It is difficult to reuse
stateful logic between components, which results in people doing things like:

- [render props](https://reactjs.org/docs/render-props.html): Passing functions down the component
  hierarchy as via props is cumbersome. However, there are situations where this can't be avoided.
- [higher-order components](https://reactjs.org/docs/higher-order-components.html): State can be
  stored at the top most component in the hierarchy in order to be shared between children
  components, which makes it necessary to add "artificial" components at the top most level (to have
  a shared scope in the children) just to wrap everything else underneath it, which is not optimal.

With hooks, it is now possible to reuse stateful logic between function components! Thru the use of
`useState` hook and others, you can create your own more complex hooks. The official docs have
[Hooks at a Glance](https://reactjs.org/docs/hooks-overview.html) which is a great overview of hooks
along w/ an example of how you can make your own.

### Limitations when using hooks (must follow these rules)

Read this [deep dive](https://reactjs.org/docs/hooks-rules.html#explanation) on how hooks are
implemented and follow these [rules](https://reactjs.org/docs/hooks-rules.html). Hooks in functional
components get turned into objects that are stored in a linked list inside of a
[fiber](https://github.com/acdlite/react-fiber-architecture) (which is an object representation of
the DOM that each React component has).

> 💡 More info on
> [React fibers](https://blog.ag-grid.com/inside-fiber-an-in-depth-overview-of-the-new-reconciliation-algorithm-in-react/).

1. By following these rules:
2. You ensure that Hooks are called in the same order each time a component renders.
3. You ensure that all stateful logic in a component is clearly visible from its source code.
4. Hooks should not be called in loops, nested functions or conditions. Instead, always use Hooks at
   the top level of your React function, before any early returns.
5. Don’t call Hooks from regular JavaScript functions.
6. React function components can call Hooks.
7. Custom Hooks can call other Hooks.
8. If we want to run an effect conditionally, we can put that condition _inside_ our Hook.
   ```jsx
   useEffect(() => (name !== "" ? null : localStorage.setItem("name_field", name)))
   ```

### Example w/ explanation of React memory model

Here's an example from the React official docs.

```jsx
import React, { useState, useEffect } from "react"

/** Custom hook. */
function useFriendStatus(friendID) {
  const [isOnline, setIsOnline] = useState(null)

  function handleStatusChange(status) {
    setIsOnline(status.isOnline)
  }

  useEffect(() => {
    ChatAPI.subscribeToFriendStatus(friendID, handleStatusChange)
    return () => {
      ChatAPI.unsubscribeFromFriendStatus(friendID, handleStatusChange)
    }
  })

  return isOnline // This comes from `useState()`.
}

// FC.
function FriendStatus(props) {
  const isOnline = useFriendStatus(props.friend.id)

  if (isOnline === null) {
    return "Loading..."
  }
  return isOnline ? "Online" : "Offline"
}

// FC.
function FriendListItem(props) {
  const isOnline = useFriendStatus(props.friend.id)

  return <li style={getColor(isOnline)}>{props.friend.name}</li>

  function getColor(isOnline) {
    return "color: " + isOnline ? "green" : "black"
  }
}
```

Here are some notes on the code to understand what is happening here and how to think about state in
a function component, and how that maps to React's memory model.

1. With classes, it was easier to understand React's memory model, because a stateful class
   component has a constructor, which then allocates the state up front.
   `ReactDOM.render(virtualDom, actualDom)` actually takes the `JSX.Element` that this class
   component represents, and mounts and renders it. Then there are subsequent re-renders which is
   where state actually comes into play. In hooks, this part is a little bit confusing, since there
   is no constructor. Here's one way to think about it.

1. The first time the function component is rendered (after being mounted), React will allocate any
   state variables that are declared via calls to `useState()`. This is stored in memory by React
   and the initial value is the argument passed to `useState(initialValue)`.
1. This is also why React cares that these calls should not be wrapped in conditional logic or
   loops, because it relies on the lexical order in which these `useState()` calls are declared to
   do internal bookkeeping to figure out what the values of each stateful variable is (in its
   [internal memory model][h-1]).
1. When the setter returned by `useState<T>(initialValue:T)` which is of type
   `Dispatch<SetStateAction<T>>`, is called w/ a new value, it will trigger a re-render. A function
   can also be passed to `useState<T>(initialValue:(T)=>T)` which will compute the subsequent value
   based on the previous state's value. When a re-render is triggered then the new value of this
   state will be used to generate the UI.

1. Note that when stateful logic is reused, the state of each component is completely independent.
   Hooks are a way to reuse stateful logic, not state itself. In fact, each call to a Hook has a
   completely isolated state — so you can even use the same custom Hook twice in one component.

1. Custom Hooks are more of a convention than a feature. If a function’s name starts with ”use” and
   it calls other Hooks, we say it is a custom Hook. The "useSomething" naming convention is how the
   linter plugin is able to find bugs in the code using Hooks.

### useEffect

This [hook](https://reactjs.org/docs/hooks-effect.html) is kind of `componentDidMount`,
`componentDidUpdate`, and `componentWillUnmount` combined!

It allows you to register a function that is called whenever anything is rendered to the DOM on the
page. And it can be scoped to an array of dependencies (which are state variables that can change in
order to trigger this effect to be run).

> 1. Read the
>    [official docs](https://reactjs.org/docs/hooks-effect.html#tip-optimizing-performance-by-skipping-effects)
>    to get the details.
> 2. This [SO thread](https://stackoverflow.com/a/53974039/2085356) also has some good insight on
>    how to use this hook.

Here is an example that mimics `componentDidMount`.

```typescript
export const ReactReplayFunctionComponent: FC<AnimationFramesProps> = (props): ReactElement => {
  /** State: animator (immutable). */
  const [animator] = useState<Animator>(
    new Animator(MyConstants.delayMs, tick, "[FunctionalComponentAnimator]")
  )

  useEffect(runAnimatorAtStart, [animator])

  /** Starts the animator. */
  function runAnimatorAtStart() {
    animator.start()

    // Cleanup.
    return () => {
      if (animator.isStarted) animator.stop()
    }
  }

  /* snip */
}
```

This `useEffect` hook is scoped to the `animator` variable, which is returned by `useState`.

> ⚠ This is similar to `componentDidMount`, unmount, update, etc. However, there are some _big_
> differences.
>
> - To mimic the functionality of `componentDidMount` you have to pass a 2nd argument to `useEffect`
>   which is either an empty array `[]` or some state variable that doesn't really change.
> - To watch for changes in some specific variables, you can pass them in that array.
>
> 💡 Read more about the difference between passing an empty deps array and passing nothing on this
> [SO thread](https://stackoverflow.com/a/58579462/2085356).

If you want a hook to run on every single DOM render, then you can write something like this.

```typescript
import { ReactElement } from "react"

export const ReactReplayFunctionComponent: FC<AnimationFramesProps> = (props): ReactElement => {
  useEffect(runForEveryDomChange)

  function runForEveryDomChange() {
    /* code */
  }

  /* snip */
}
```

> ⚠ Beware the issue of ["stale closures"](https://dmitripavlutin.com/react-hooks-stale-closures/)
> when using `useEffect()`. The stale closure problem occurs when a closure captures outdated
> variables.

#### First render and subsequent re-renders using useRef and useEffect

Out of the box the callback that you pass to `useEffect()` can't tell the difference between first
render, and subsequent re-renders. This is where `useRef` can be very useful (we have seen it used
for keyboard focus in [this section](#imperative-using-useref).

You can set whatever value you want in the `current` property of the `ref` (which is returned by
`React.useRef(initialValue)`). This value will be stable when the component is re-rendered. This can
be a simple way of detecting when the first render occurs, and when subsequent re-renders occur.

> 💡 Note that storing a value in an object returned by `useRef` is different than simply using
> `setState` because React isn't watching for changes in the state in order to trigger a re-render.

Here's an example of a custom hook that allows you to use `localStorage` in order to get and set
key-value pairs.

```typescript
export type MyLocalStorageHook = [string, Dispatch<SetStateAction<string>>]
const useMyLocalStorageHook = (key: string): MyLocalStorageHook => {
  const isMounted = React.useRef(false)

  const [value, setValue] = React.useState(localStorage.getItem(key) || "N/A")

  React.useEffect(() => {
    if (!isMounted.current) {
      console.log("First render")
      isMounted.current = true
      return
    }

    console.log("Subsequent re-render")
    localStorage.setItem(key, value)
  }, [key, value])

  return [value, setValue]
}
```

> ⚠ Note that the value of the object returned by `useRef` (the `current` property of `ref`) is only
> set in the `useEffect` callback. It isn't set in the code that is doing the rendering for example.

1. This hook can tell the difference between the first render and subsequent re-renders since it is
   using `useRef(boolean)` in order to set the `current` property to `true` on first render (and
   then doing an early return).
2. Subsequent re-renders will skip over this early return condition check and will actually the work
   it is intended to.
3. When the `setValue` dispatch is used to assign a new value to the key, then it will actually save
   the key-value pair to local storage.

> 💡 Note that `ref.current` can also be used as a place to store the results of an expensive
> computation that are local to a function component, but isn't part of the state. This can be a
> cache that is local to the component. Perhaps this cache can be populated on first render and then
> re-used for subsequent renders.

### useState

Reusing _stateful logic_ isn't the same as _sharing state between function components_. For the
latter, [`useContext`](https://reactjs.org/docs/context.html) or [Redux](#redux) might be more
appropriate.

#### Example

The following code uses the `useState` hook in a function component.

```typescript
import { ReactElement } from "react"

type IndexStateHookType = [number, Dispatch<SetStateAction<number>>]

export const ReactReplayFunctionComponent: FC<AnimationFramesProps> = (props): ReactElement => {
  /** State: currentAnimationFrameIndex (mutable). */
  const [frameIndex, setFrameIndex]: IndexStateHookType = useState<number>(0)

  /** State: animator (immutable). */
  const [animator] = useState<Animator>(
    new Animator(MyConstants.delayMs, tick, "[FunctionalComponentAnimator]")
  )

  /* snip */
}
```

> ⚡ Here's the complete source file
> [ReactReplayFunctionComponent.tsx](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/animate/ReactReplayFunctionComponent.tsx).

Here's the anatomy of each call to `useState`.

1. On the 👈 _left hand side_ of the call to `useState` hook, it returns an array (of type
   `IndexStateHookType`).
2. The first item is a reference to the state variable (of type `T`).
3. The second item is the setter function for it (of type `Dispatch<SetStateAction<T>>`). This
   mutates the state and triggers are render of the function component.
4. It has to be initialized w/ whatever value is on the _right hand side_ 👉 expression. So it is a
   pretty simple way of making function components have initial state.

> ⚠ Beware the issue of ["stale closures"](https://dmitripavlutin.com/react-hooks-stale-closures/)
> when using `useState()`. The stale closure problem occurs when a closure captures outdated
> variables.

#### Shared stateful logic vs shared state

Here's a [SO question about this](https://stackoverflow.com/a/53455474/2085356) that goes into quite
a bit of detail about the differences between sharing state between components and stateful logic
that is shared. Here are some tips from this SO answer.

- Stateful logic is different from state. Stateful logic is stuff that you do that modifies state.
  For e.g., a component subscribing to a store in `componentDidMount()` and unsubscribing in
  `componentWillUnmount()`. This subscribing/unsubscribing behavior can be implemented in a hook and
  components which need this behavior can just use the hook.

- Here are some ways to share state between components (each w/ its pros and cons):

  1. Lift state up to a common ancestor component of the two components. This is the same approach
     taken with class components, the only difference w/ hook is how we declare the state.

     ```typescript
     const Parent: FC = () => {
       const [count, setCount] = useState(1)
       return (
         <>
           <ChildA count={count} onCountChange={setCount} />
           <ChildB count={count} onCountChange={setCount} />
         </>
       )
     }
     ```

  2. If the child components are deep in the hierarchy to be passed down at every level, then
     [`useContext`](https://reactjs.org/docs/context.html#when-to-use-context) hook might be the way
     to go.

  3. External state management libraries like [Redux](#redux) might be the way to go. Your state
     will then live in a store outside of React and components can subscribe to the store to receive
     updates.

  > ⚠ Note - Avoid the open source custom hook called
  > [`useBetween`](https://github.com/betula/use-between) since it is a useless hack.

#### Resources

Here are some great resources on learning about `useState`.

1. [Official docs](https://reactjs.org/docs/hooks-state.html)
2. [TypeScript and useState](https://www.carlrippon.com/typed-usestate-with-TypeScript/)

### useReducer

This hook is very similar to the `useState` hook. You can use both in a component as well. The main
difference between them is unlike `setState`, a reducer function must be provided that deals w/
generating a new state when employing `useReducer`.

> 💡 This is very similar to Redux! And this might just be the simplest way to learn Redux patterns.
> Jump to this [section](#redux) to learn all about how to use React and Redux (using the modern
> `redux-toolkit` and not old-school `redux-react`).

It is possible to replace code that employs `useState` w/ code that employs `useReducer`. Here's an
example.

Code that employs `useState` hook.

```typescript
type StoriesStateHookType = [Story[], Dispatch<SetStateAction<Story[]>>]
export const ListOfStoriesComponent: FC<ListOfStoriesProps> = (props) => {
  // Store Story[] in the function component's state.
  const [myStories, setMyStories]: StoriesStateHookType = React.useState<Story[]>([])

  // Simply call `setMyStories` to set a value to the function component's state.
  React.useEffect(
    () => {
      getAsyncStoriesWithSimulatedNetworkLag().then((value) => {
        setMyStories(value)
      })
    },
    [] /* Only run this effect once; akin to componentDidMount. */
  )
}

// Function to remove a story by simply using `setMyStories`.
const handleRemoveItem = (id: number): void => {
  setMyStories(myStories.filter((it) => it.objectID !== id))
  console.log(`handleRemoveItem('${id}) called'`)
}
```

Equivalent code that employs `useReducer` hook.

```typescript
export const ListOfStoriesComponent: FC<ListOfStoriesProps> = (props) => {
  // Create a reducer to manage Story[] in the state.
  const [myStories, dispatchMyStories]: ReducerHookType = React.useReducer<ReducerType>(
    storiesReducer,
    new Array<Story>()
  )

  // To make changes to the state managed by the reducer, you have to dispatch an action w/
  // a payload. In this example, we have 2 actions: "setState" and "removeItem".

  React.useEffect(
    () => {
      getAsyncStoriesWithSimulatedNetworkLag().then((value) => {
        dispatchMyStories({
          type: "setState",
          payload: value,
        })
      })
    },
    [] /* Only run this effect once; akin to componentDidMount. */
  )

  const handleRemoveItem: FnWithSingleArg<Story> = (objectToRemove: Story) => {
    console.log("handleRemoveItem called w/", objectToRemove)
    dispatchMyStories({
      type: "removeItem",
      payload: objectToRemove,
    })
  }
}

// This is the reducer function.

export type StateType = Story[]
interface ActionSetState {
  type: "setState"
  payload: Story[]
}
interface ActionRemoveItem {
  type: "removeItem"
  payload: Story
}
export type ActionType = ActionSetState | ActionRemoveItem
export type ReducerType = Reducer<StateType, ActionType>
export type ReducerHookType = [StateType, Dispatch<ActionType>]

export const storiesReducer = (currentState: StateType, action: ActionType): StateType => {
  console.log("storiesReducer -> \ncurrentState:", currentState, "\n-> action:", action)
  let newState: StateType
  switch (action.type) {
    case "removeItem":
      const itemToRemove = action?.payload
      newState = currentState.filter((story) => story.objectID !== itemToRemove.objectID)
      break
    case "setState":
      newState = action.payload
      break
    default:
      throw new Error(`Invalid action: ${action}`)
  }
  console.log("return newState", newState)
  return _.clone(newState)
}
```

#### Two examples (one w/out network, and one w/ network)

1. For a simple example that doesn't use any network, and that is decomposed into many files, check
   out the
   [`ListOfStoriesComponent`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/list/ListOfStoriesComponent.tsx)
   which utilizes both `useState` and `useReducer` hooks.
2. For an example that has network calls, and does everything in one file, check out the
   [`CatApiComponent`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/cat_api/CatApiComponent.tsx)
   which only uses `useReducer` and no `useState`.

### useCallback and useMemo

These two hooks are very tricky, since they cache objects that are tightly bound to React's
lifecycle, and might have memory and CPU impacts that you're not able to predict using your
intuition. Most of the time, its best not to use them.

These articles go into great details about why they should not be used unless you have a very
specific use case that warrants their use as.

1. [Article - useMemo and useCallback](https://kentcdodds.com/blog/usememo-and-usecallback)
2. [Article - Don't overuse React useCallback](https://dmitripavlutin.com/dont-overuse-react-usecallback)

Reference docs

- [useMemo](https://reactjs.org/docs/hooks-reference.html#usememo)
- [useCallback](https://reactjs.org/docs/hooks-reference.html#usecallback)

Here are some acceptable use cases where these can be used.

- When functions that are declared inside of a hook have some internal state, such as when the
  function is debounced or throttled.
- When the function object is a dependency on other hooks (eg: passing the function returned by
  `useCallback` to `useEffect`).
- When the function component wrapped inside of `useMemo` accepts a function object prop.

### How to write complex function components

If the FCs (`ItemComponent`, `ListComponent`, `SearchComponent` ) are defined inside the
[`ListOfStoriesComponent`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/list/ListOfStoriesComponent.tsx)
they behave differently with keyboard focus, than if they are defined outside it!

1. If they are declared _outside_, the keyboard focus inside the `input` element is retained as you
   type different search terms.
2. If they are declared _inside_, the keyboard focus is lost every time you generate a single
   keyboard event.

   > ⚠ This might have something to do with [this](https://stackoverflow.com/a/56655447/2085356),
   > function components being stateless. If things are declared inside of a function, then they
   > will be recreated everytime that function is run, vs if they are declared outside, then they
   > won't be recreated on every (render) call.

### Custom hooks

When writing custom hooks, that relay external async events (eg, happening in a listener that is
attached to the DOM, or Node.js, or a database), it is important to keep in mind that callback
functions that are passed to `useEffect()` **can not directly call** into the React function
component 🧨!

> 🤔 This is a pretty subtle and important point to remember when figuring how to "relay" the
> non-React async event into the React function component world (via a custom hook that you're
> writing).

It might be tempting to simply pass a React-function-component-callback function to a hook, which
then passes it on to an external event emitter listener 😈. When the listener is then executed by
the external event emitter (which is not a React function component) then problems will arise! The
state information that this React-function-component-callback will get will be wrong. If you use
Redux you can bypass this problem, but if you're using `useEffect()` then you will be in trouble.

The way to get around this issue is to do the following:

1. Introduce an intermediate state variable (via `useState()` hook).
2. Have your external event listener use the setter for this state variable to let your hook know
   that some external event just came in.
3. Use `useEffect()` and pass the getter for this state variable as a dependency to a function that
   gets called when this state variable changes. This function will be able to then run the
   React-function-component-callback that is passed into the hook to begin with.

Here's a diagram of this.

<img src="{{ 'assets/use-hook-outside.svg' | relative_url }}"/>

For a real world example, please take a look at this
[commit in r3bl-ts-utils](https://github.com/r3bl-org/r3bl-ts-utils/commit/a3248540ea325d3896ee56a84d003f15529169cd)
for more information on how the hook "binds" the two disparate worlds of Node.js `process.stdin`'s
`keypress` events, and the React function component that ends up using this hook to get async events
that are generated by an end user who's typing in a terminal.

Here are some simple examples:

- [`useLocalStorage`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/list/hooks.tsx)
  - `useLocalStorage` shows how to use `localStorage` to back a state variable.
  - `LocalStorageEvents` shows how to deal w/ `localStorage` limitations when setting the value in
    the same `document`. `localStorage` changes can be initiated in 3 ways:
    1.  from this hook (calls to the setter / dispatcher returned by this hook).
    2.  from calls to MyLocalStorageEvents.storage.setValue().
    3.  from other document(s) (running the same app in other tabs in the same browser instance)
        changing the key value pairs in localStorage.
- [`useAnimator`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/animate/hooks.tsx)
  - [`ReactReplayFunctionComponent`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/animate/ReactReplayFunctionComponent.tsx)
    uses this hook in order to show frames in a pre-rendered array of frames (`ReactElement[]`).

### References about hooks

To learn about hooks, here are some important resources.

- [Great video introducing hooks][h-2]
- [Best practices on using React function components][h-5]
- [Official docs on writing custom hooks][h-4]
- [Official Hooks API Reference for useState][h-3]
- [Deep dive into useState hook and React memory model][h-1]

[h-1]: https://www.newline.co/@CarlMungazi/a-journey-through-the-usestate-hook--a4983397
[h-2]: https://youtu.be/dpw9EHDh2bM
[h-3]: https://reactjs.org/docs/hooks-reference.html#usestate
[h-4]: https://reactjs.org/docs/hooks-custom.html
[h-5]: https://www.infoworld.com/article/3603276/how-to-use-react-functional-components.html

## Keyboard focus and React

We can do this declaratively (which is relatively simple, but extremely limiting) or imperatively,
which is probably more realistic (and more complex).

### Declarative

Here's a way to get keyboard focus into a single element declaratively. The `autoFocus` attribute on
the `input` element is set to a boolean value that is passed as a props.

```typescript
type SearchProps = { searchTerm: string; onSearchFn: OnSearchFn; initialKeybFocus: boolean }

const ListOfStoriesComponent: FC = () => {
  /** snip */
  return (
    <div className={"Container"}>
      <strong>My Searchable Stories</strong>
      <SearchComponent searchTerm={searchTerm} onSearchFn={onSearchFn} initialKeybFocus={true}>
        <strong>Search: </strong>
      </SearchComponent>
      <ListComponent list={filteredStories} />
    </div>
  )
}

const SearchComponent: FC<SearchProps> = ({
  searchTerm,
  onSearchFn,
  children,
  initialKeybFocus,
}) => {
  return (
    <section>
      <label htmlFor="search">{children}</label>
      <input
        id="search"
        type="text"
        value={searchTerm}
        onChange={onSearchFn}
        autoFocus={initialKeybFocus}
      />
    </section>
  )
}
```

### Imperative using useRef

Here's another way to do the same thing imperatively (programmatically) using `useRef()` and
`useEffect()`.

> 💡 Using ref (DOM element of a React element) and hooks:
>
> 1. In order to use a ref, you must first create it using the `useRef()` hook, and then pass it to
>    use the `ref` attribute in a React component.
> 2. When this component is rendered to DOM, it will "set" the `current` property of this ref (which
>    is the DOM element corresponding to this React component). This is used later in the
>    `useEffect()` hook to actually call `focus()` on the DOM element.

```typescript
const SearchComponent: FC<SearchProps> = ({
  takeInitialKeyboardFocus,
  searchTerm,
  onSearchFn,
  children,
}) => {
  // useEffect hook for initial keyboard focus on input element.
  const inputRef: React.MutableRefObject<any> = React.useRef()
  React.useEffect(() => {
    if (inputRef.current && takeInitialKeyboardFocus) {
      inputRef.current.focus()
    }
  })

  // Run this effect to log inputRef.
  const [showUi, setShowUi] = React.useState(true)
  function onButtonClicked() {
    setShowUi((prevState) => !prevState)
    console.log("showUi", showUi)
  }
  React.useEffect(() => {
    console.log("✨ Creating inputRef related effect")
    const logInputRef = (msg: string) => {
      console.log(
        `${msg}\n`,
        inputRef.current ? "🎉 has DOM element" : "🧨 does not have DOM element"
      )
    }
    logInputRef("🎹✨ inputRef")
    return () => {
      logInputRef("🎹🗑 Do something here to unregister the DOM element, inputRef")
    }
  }, [showUi])

  return (
    <section>
      {showUi && (
        <>
          <label htmlFor="search">{children}</label>
          <input id="search" type="text" value={searchTerm} onChange={onSearchFn} ref={inputRef} />
        </>
      )}
      <button onClick={onButtonClicked}>mount/unmount</button>
    </section>
  )
}
```

> 💡 You can also utilize `useRef()` in order to detect the first render vs subsequent re-render by
> pairing it w/ `useEffect()` hook; more in
> [this section](#first-render-and-subsequent-re-renders-using-useref-and-useeffect).

## React and CSS

At a high level there are 2 strategies to consider when using CSS in React (which are both bundled
when you use `create-react-app` (CRA).

1. Styled components (CSS in JS) - This is where you simply use the `className` prop to specify
   which CSS rules to use.
2. CSS Modules (CSS in CSS) - This is where you leverage
   [CSS modules](https://css-tricks.com/css-modules-part-1-need/) which locally scope the styles to
   prevent collisions w/ synonymous styles declared in other files. Look
   [below](#css-modules-example) for more details.

### CSS Modules example

The following are the main differences that you have to be aware of when compared to styled
components:

1. Instead of using `XXX.css`, make `XXX.module.css` files. This tells CRA to use CSS modules.
2. Instead of importing the CSS file like you would for a styled component, do this instead
   `import YYY from './XXX.module.css'`, where `YYY` is what you choose to call the variable holding
   all the imported styles.
   > When using styled components you only have to import the CSS file once (eg: in `App.tsx`) and
   > these are available (implicitly) to all the React components that are nested in it. But using
   > modules you have to import them in each file that uses the style.
3. Then use these styles in your JSX like this: `<Component className{YYY.XYZ}/>`.

Here's a simple example that shows how to use CSS modules or CSS in CSS approach.

> ⚡ Read the
> [CRA official docs](https://create-react-app.dev/docs/adding-a-css-modules-stylesheet/) on using
> CSS modules.

Step 1 - Create a `XYZ.module.css` file, eg: `App.module.css` and not a `App.css` file.

```css
.container {
  height: 100vw;
  padding: 20px;
  background: linear-gradient(to left, #b6fbff, #83a4d4);
  color: #171212;
}
```

Step 2 - In your JSX component, you have to do the following import to use the style.

```typescript
import React from "react"
import myStyles from "./App.module.css"

const App: FC = () => <div className={myStyles.container}>Content</div>
```

> ⚠ Note how this is different from the usual `<div className="container">...</div>`.

### Styled component example

#### TooltipOverlay w/ just CSS

It is actually very simple to implement a tooltip using just CSS. The key is using the `:hover`
pseudo selector on the tooltip's parent container to display a tooltip.

Here's an overview of what this CSS does:

- An empty parent container (`span`) is created so that its position can be set to `relative`, so
  that any child elements inside of it (other `span` elements) can be positioned as `absolute` w/ a
  `z-index` of `1000`.
- The `:hover` pseudo selector on the `.tooltipContainer` takes care of showing the `.tooltip` by
  setting its `display` to `block`.

> ⚡
> [`TooltipOverlay.module.css`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/utils/Tooltip.module.css)

```css
.tooltipContainer {
  position: relative;
}

.tooltip {
  --radius: 5px;
  --alpha: 0.8;
  --fillColor: rgba(26, 31, 48, var(--alpha));
  --borderColor: rgba(100, 149, 237, var(--alpha));
}

.tooltip {
  display: none;
  position: absolute;
  z-index: 1000;

  padding: calc(var(--defaultPadding) * 0.5);
  background: var(--fillColor);
  border-radius: var(--radius);
  border: 2px solid var(--borderColor);

  /* This ensures that the tooltip does not obstruct the element that is being hovered */
  top: 100%;
  width: auto;
}

.tooltipContainer:hover .tooltip {
  display: block;
}
```

The (minimal) React component below uses the CSS above.

> ⚡
> [`TooltipOverlay.tsx`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/utils/TooltipOverlay.tsx)

```typescript
import React, { FC, PropsWithChildren } from "react"
import componentStyles from "./TooltipOverlay.module.css"

export type TooltipOverlayProps = {
  tooltipText: string
}

export const TooltipOverlay: FC<PropsWithChildren<TooltipOverlayProps>> = ({
  children,
  tooltipText,
}) => {
  return (
    <span className={componentStyles.tooltipContainer}>
      <span className={componentStyles.tooltip}>{tooltipText}</span>
      {children}
    </span>
  )
}
```

> ⚡ React bootstrap package has an example using this pattern
> [here](https://react-bootstrap.github.io/components/overlays/).

#### TooltipOverlay w/ just React

Here is an example of implementing a tooltip that uses mostly React, and not much CSS as shown in
the previous example.

Here's the React code - The `useState` hook is essentially used to apply a "hover" effect on any
React elements that are children of a `TooltipOverlay` component.

```typescript
import componentStyles from "./TooltipOverlay.module.css"

export type TooltipOverlayProps = {
  tooltipText: string
}

export const TooltipOverlay: FC<PropsWithChildren<TooltipOverlayProps>> = ({
  children,
  tooltipText,
}) => {
  const [showTooltip, setShowTooltip] = React.useState(false)
  const onMouseEnter = () => setShowTooltip(true)
  const onMouseLeave = () => setShowTooltip(false)

  const styleVisible = componentStyles.tooltip + " " + componentStyles.visible
  const styleInvisible = componentStyles.tooltip

  return (
    <span
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      className={componentStyles.tooltipContainer}
    >
      <span className={showTooltip ? styleVisible : styleInvisible}>{tooltipText}</span>
      {children}
    </span>
  )
}
```

The CSS is the same as in the previous example, with the only following difference.

```css
.tooltip.visible {
  display: block;
}
```

## React and SVG

It is very easy to use SVG w/ React. There are various ways of importing the SVG asset into a React
component itself:

1. You can import it from a file (static asset). The imported file is actually a React component
   itself. And you can style the SVG directly by passing `className` or inline styles to this
   component. Here's an example of importing the SVG file.

   ```typescript
   import { ReactComponent as Car } from "./car.svg"
   export const SvgExample: FC = (props) => <Car className={"SvgImage"} />
   ```

   Here's an example of styling it in CSS.

   ```css
   .SvgImage {
     height: 100px;
     width: 100px;
   }

   .SvgImage:hover > g {
     stroke: yellow;
     stroke-width: 8px;
   }
   ```

2. You can declare it in JSX. Here's an example.

   ```typescript
   const BasicSvg = () => (
     <svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
       <circle cx="50" cy="50" r="40" stroke="blue" strokeWidth="4" fill="lightblue" />
     </svg>
   )
   ```

   You can then just use it as a React component.

   ```typescript
   export const SvgExample: FC = (props) => <BasicSvg />
   ```

   Or you can use it inside an `img` tag like so.

   ```typescript
   export const SvgExample: FC = (props) => <img src={logo} className="logo" alt="logo" />
   ```

3. You can load it as a string using the `data:image/svg+xml` pattern. Here's an example of defining
   the SVG in CSS.

   ```css
   .topography-pattern {
     background-color: #ffffff;
     background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' ... ");
   }
   ```

   And then using it in a React component.

   ```typescript
   export const SvgExample: FC = (props) => <div className={"topography-pattern"}></div>
   ```

### References on SVG and React

- [CRA and SVG](https://create-react-app.dev/docs/adding-images-fonts-and-files/)
- [Using SVG as backgrounds in React](https://www.robinwieruch.de/react-svg-patterns)

## Redux

[Redux](https://redux.js.org/tutorials/fundamentals/part-1-overview) is a great way to share state
between components. The `redux-toolkit` uses the underlying `react-redux` module, but is easier to
use. Here's how you can install it in your project.

```shell
npm install @reduxjs/toolkit react-redux
```

> 💡 To understand Redux it is best to start w/ 'useReducer' hook as show in this
> [section](#usereducer). It is an easy way to understand the fundamentals of Redux which is
> actions, state, reducer functions, and immutable state.

While Redux helps you deal with shared state management, it has tradeoffs. You have to buy into its
mental model, and structure your code and thoughts in a Redux-compliant way. As a developer you are
used to modifying state imperatively, and the notion of having to request changes to be made
declaratively might be something you've not seen before. It also adds some indirection to your code,
and asks you to follow certain restrictions. It's a trade-off between short term and long term
productivity.

Here's a simple example (no async, middleware, thunks, or splitting reducers, etc). There are the 5
steps to using Redux in your React component(s).

### Step 1 - Define the types for the state, action, then use them to create a reducer function

We will use a TypeScript feature called
[discriminated unions](https://www.TypeScriptlang.org/docs/handbook/2/narrowing.html#discriminated-unions)
in order to make our actions typesafe.

1. The type of the reducer function is `Reducer<State | undefined, Action>`. The `undefined` is to
   cover the case when the initial state must be created by the reducer.
2. If you try and replace the `Reducer<State ... , Action>` w/ a type variable that holds the same
   thing, then it will not work for some reason w/ TypeScript.

> 💡 The reducer function is called that because it is meant to be analogous to
> [`Array.reduce()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/reduce)
> which takes all the items in an array and returns a single "thing".
>
> Reducer functions take the state and current action and produce a single "thing", which is the new
> state.
>
> Now, imagine putting all the actions that would be dispatched over the lifetime of an app and then
> put them into an array and then "apply" them to the reducer function (taking the resulting state
> from dispatching an action and passing it to the next action and so on). Ultimately you end up w/
> a single result which is the final state of the app. Thinking of it this way, it sort of fits how
> the `Array.reduce()` function works 🤷.

```typescript
// Types.
type Text = {
  id: string
  content: string
}
type State = {
  textArray: Array<Text>
}
interface ActionAdd {
  type: "add"
  content: string
}
interface ActionRemove {
  type: "remove"
  id: string
}
type Action = ActionAdd | ActionRemove

// Reducer function.
const reducerFn: Reducer<State | undefined, Action> = (state, action): State => {
  if (!state)
    return {
      textArray: [
        { id: _.uniqueId("id"), content: "fffff" },
        { id: _.uniqueId("id"), content: "gggg" },
      ],
    }

  switch (action.type) {
    case "add": {
      const newText: Text = { id: _.uniqueId("id"), content: action.content }
      console.log("add", newText)
      const copyOfArray = new Array<Text>().concat(state.textArray)
      copyOfArray.push(newText)
      return Object.assign({} as State, state, { textArray: copyOfArray })
    }
    case "remove": {
      // Get the index (the string we want to remove).
      const id: string = action.id
      // Make a copy of the old state and remove the element w/ the given id
      const copyOfArray = new Array<Text>().concat(state.textArray).filter((it) => it.id !== id)
      console.log("remove", id)
      return Object.assign({} as State, state, { textArray: copyOfArray })
    }
  }
  return state
}
```

#### No side effects, pure functions only

Reducer functions can't have side effects, and must be pure functions; so there can't be things like
fetch calls, async timers, console logging, random number generator use, or even `Date.now()` in
them.

In order to do these important things, please use [enhancers](#enhancer) and / or
[middleware](#middleware).

Here are a
[list of rules](https://redux.js.org/tutorials/fundamentals/part-3-state-actions-reducers#rules-of-reducers)
that reducers must follow.

> 💡 One of the benefits of using pure functions here is easy implementation of
> [undo history](#undo-history).

### Step 2 - Create a store that uses this reducer function

> 💡 If you split reducers, then this is where you would declare all the ones that comprise the root
> reducer function.

```tsx
// Redux store.
export const store = configureStore({
  reducer: reducerFn,
})
```

### Step 3 - Wrap the component(s) that will share this state with a Provider tag

Wrap the component(s) that will share this state with `<Provider store={store}>...</Provider>` where
`store` is what you created and exported in
[this step](#step-2---create-a-store-that-uses-this-reducer-function).

> 💡 Wrapping your component in this tag and passing the store allows hooks like
> [`useDispatch()`](#step-5---make-sure-to-dispatch-actions-in-your-components-to-change-shared-state)
> and [`useSelector()`](#step-4---subscribe-your-components-to-the-store-with-useselector-hook) to
> work their "magic" (ie, not having to explicitly import and use the store).

```tsx
<Provider store={store}>
  <SimpleReduxComponent />
</Provider>
```

> 💡 Here's the official Redux documentation on using a
> [`Provider`](https://redux.js.org/tutorials/fundamentals/part-5-ui-react#passing-the-store-with-provider).

### Step 4 - Subscribe your component(s) to the store with useSelector hook

In your component, make sure to subscribe to the store, using the
[`useSelector()`](#useselector-hook-and-react) hook.

> 💡 This is used instead of the old
> [`mapStateToProps` / 'connect'](https://react-redux.js.org/using-react-redux/connect-mapstate)
> mechanism. When the state changes in the store then, the new state will be passed to this
> component (by the hook), and it will be re-rendered.
>
> This is somewhat equivalent to the [`useReducer()`](#usereducer) hook, in the sense that you will
> get the state from this hook.
>
> If you split reducers, then you can select just a subset of the state that you are interested in
> (in the function that you pass to the `useSelector()` hook).

```tsx
import { _also } from "r3bl-ts-utils"

// function component.
export const SimpleReduxComponent: FC = () => {
  const state: DefaultRootState = useSelector((state) => state)
  const myState = state as State
  /* snip */
}
```

> ⚡ Note the `_also` is a scope function (that is inspired by Kotlin) which you can get from
> [`r3bl-ts-utils`](https://www.npmjs.com/package/r3bl-ts-utils) npm module.

### Step 5 - Make sure to dispatch actions in your component(s) to change shared state

In your component, make sure to call `store.dispatch({/* action */})` in order to request changes to
happen to your store. This will trigger re-renders of the components that are subscribed to the
store.

> 💡 Instead of importing the store in order to dispatch actions to it, you can also use the
> [`useDispatch()`](https://redux.js.org/tutorials/fundamentals/part-5-ui-react#dispatching-actions-with-usedispatch)
> hook, which simply returns the store (that your React component has access to, since there's a
> `Provider` in its hierarchy).

```typescript
import { _also } from "r3bl-ts-utils"

// function component.
export const SimpleReduxComponent: FC = () => {
  const state: DefaultRootState = useSelector((state) => state)
  const myState = state as State

  const addListItem = () =>
    _also(
      {
        type: "add",
        content: "NazmulMaretIdris".substring(Math.floor(Math.random() * 15)),
      } as ActionAdd,
      (it) => {
        store.dispatch(it)
      }
    )

  const removeListItem = (it: string) =>
    _also({ type: "remove", id: it } as ActionRemove, (it) => {
      store.dispatch(it)
    })

  const render = () => (
    <div className={"Container"}>
      <button onClick={addListItem}>Add</button>
      <ol>
        {myState.textArray.map((text) => (
          <li key={text.id} onClick={() => removeListItem(text.id)}>
            {text.content}
          </li>
        ))}
      </ol>
    </div>
  )

  return render()
}
```

> ⚡ Here's the full example in a single source file
> [`SimpleReduxComponent.tsx`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/redux/SimpleReduxComponent.tsx).

### Immutability

One of the core concepts in Redux is that the state is immutable. There are a few approaches to make
this happen.

This is a great
[article](https://reactkungfu.com/2015/08/pros-and-cons-of-using-immutability-with-react-js/) on
reference equality, value equality, shallow and deep copy, and how to achieve immutability w/out
using any external libraries using the following idioms.

- Objects: `Object.assign({}, originalObject, {propertyToChange:'value'})`
- Arrays: `[].concat(oldArray)`

Since Redux and React compare references to determine equality, it isn't necessary to perform a deep
copy of all the things, and copying objects and arrays that are contained in the state should
suffice for most situations.

> 💡 Here are other approaches you can take instead of the idioms shown above.
>
> 1. You can use lodash [`clone`](https://lodash.com/docs#clone).
> 2. Yet another approach is to use the [immer](https://immerjs.github.io/immer/) library.

### Selectors

[Selectors](https://redux.js.org/tutorials/fundamentals/part-2-concepts-data-flow#selectors) are
simply functions that know how to extract specific pieces of information from a store's state value.
As an application grows larger, this is a way to keep from repeating this logic which would provide
slices of state data needed by different parts of the app. Here's an example:

```typescript
type State = { foo: Foo }
type Foo = object

const selectFooValue: Foo = (state: State) => state.foo

const fooValue: Foo = selectFooValue(store.getState())
```

#### useSelector hook and React

The
[`useSelector()`](https://redux.js.org/tutorials/fundamentals/part-5-ui-react#reading-state-from-the-store-with-useselector)
hook that comes w/ `react-redux` takes a selector and automatically subscribes it to the store, all
in a single step. It also
[automatically unsubscribes](https://github.com/reduxjs/react-redux/blob/v7.2.2/src/hooks/useSelector.js#L81)
from the store.

> 💡 When you wrap your component in a `Provider` tag, this allows the hook to get access to the
> store and do its thing. This is similar to how the `useDispatch()` hook gets access to the store.

### Split and combine reducers

Instead of having a single "root" reducer function you can split them up based on the shape of your
store's state value. For example if your state has two top level properties like this
`{ foo:{}, bar:{} }` then you could have two reducer functions: `fooReducer()` and `barReducer()`.

> ⚠ The state parameter is different for every reducer, and corresponds to the part of the state it
> manages.

You can then join them together like this:

```typescript
type State = { foo: Foo; bar: Bar }
type Foo = object
type Bar = object

function fooReducer(stateFragment: Foo, action) {}

function barReducer(stateFragment: Bar, action) {}

export const rootReducer = (state: State, action) => ({
  foo: fooReducer(state.foo, action),
  bar: barReducer(state.bar, action),
})
```

Or even more concisely using the following:

```typescript
import { combineReducers } from "redux"

export const rootReducer = combineReducers({
  foo: fooReducer,
  bar: barReducer,
})
```

> 💡 Here's more information on
> [splitting](https://redux.js.org/tutorials/fundamentals/part-3-state-actions-reducers#splitting-reducers)
> and
> [combining](https://redux.js.org/tutorials/fundamentals/part-3-state-actions-reducers#combining-reducers)
> reducers.

### Enhancer

A
[store enhancer](https://redux.js.org/tutorials/fundamentals/part-4-store#creating-a-store-with-enhancers)
is a [higher-order function](https://en.wikipedia.org/wiki/Higher-order_function#JavaScript) that
allows you to override the following store methods, and allow you to write code that hooks into the
store's lifecycle events.

1. `dispatch()` - You can modify the original `store.dispatch()` method, and do things like log
   actions and states.

   > 💡 You can generate [side effects](#no-side-effects-pure-functions-only), by making async calls
   > here (timers and REST APIs), do logging, crash reporting, routing, modify actions, pause or
   > even stop the action entirely, etc. If you just want to override this and nothing else, you can
   > use [middleware](#middleware) instead of [enhancers](#enhancer).

2. `getState()` - You can modify the original `store.getState()` method, and modify the state that
   gets returned.
3. `subscribe()` - You can modify the original `store.subscribe()` method.

> ⚡ Here's a source code example from the official Redux docs.
>
> 1. [codesandbox.io](https://codesandbox.io/s/github/reduxjs/redux-fundamentals-example-app/tree/master/).
> 2. [github repo](https://github.com/reduxjs/redux-fundamentals-example-app/tree/master/).

#### Intercept action dispatch

Here's an example of how to create an enhancer that just calls `console.log` when actions are
dispatched.

> 💡 Note that the original store is enhanced w/ a new `dispatch` property which has the
> `myDispatchFn` function (which simply adds to the original `store.dispatch()` function).

```typescript
import { createStore } from "redux"

export const consoleLogOnDispatch = (createStore) => {
  return (rootReducer, preloadedState, enhancers) => {
    const store = createStore(rootReducer, preloadedState, enhancers)

    function myDispatchFn(action) {
      const result = store.dispatch(action)
      console.log("action dispatched", action)
      console.log("new state", result)
      return result
    }

    return { ...store, dispatch: myDispatchFn }
  }
}

export const store = createStore(rootReducer, undefined, consoleLogOnDispatch)
```

#### Intercept state creation

You can also intercept new state creation. This is a really powerful way of modifying the state.
This is an example of state modification that adds `timestampMs` which is a property that holds the
current time in ms when the state was created.

> 💡 Note that the original store is enhanced w/ a new `getState` property which has the
> `myGetStateFn` function (which simply adds to the original `store.getState()` function).

```typescript
export const includeTimestamp = (createStore) => {
  return (rootReducer, preloadedState, enhancers) => {
    const store = createStore(rootReducer, preloadedState, enhancers)

    function myGetStateFn() {
      return {
        ...store.getState(),
        timestampMs: Date.now(),
      }
    }

    return { ...store, getState: myGetStateFn }
  }
}
```

#### Combining both overrides

In order to use both of these enhancers shown above, you can use the
[`compose`](https://redux.js.org/api/compose) function.

```typescript
import { createStore, compose } from "redux"

export const store = createStore(
  rootReducer,
  undefined,
  compose(includeTimestamp, consoleLogOnDispatch)
)
```

### Middleware

Unlike [enhancers](#enhancer) middleware restrict store enhancements to just changing the
`dispatch()` function. Redux middleware provides an extension point, where we can attach our code,
between Redux dispatching an action to the store, and the moment it reaches the reducer.

> 💡 You can generate [side effects](#no-side-effects-pure-functions-only), by making async calls
> here (timers and REST APIs), do logging, crash reporting, routing, modify actions, pause or even
> stop the action entirely, etc. If you just want to override this and nothing else, you can use
> [middleware](#middleware) instead of [enhancers](#enhancer).

> ⚡ Here is the
> [official Redux middleware documentation](https://redux.js.org/tutorials/fundamentals/part-4-store#middleware).

Here's an example of a single middleware function. You can actually have many of them chained
together.

```typescript
import { createStore, applyMiddleware } from "redux"
import { composeWithDevTools } from "redux-devtools-extension"

function myMiddlewareWithResultOnDispatch(store) {
  return function wrapDispatch(next) {
    return function handleAction(action) {
      // Do anything here, then pass the action onwards with next(action),
      // or restart the pipeline with store.dispatch(action).
      console.log("dispatching", action)
      let result = next(action)

      // Can also use store.getState() here.
      console.log("next state", store.getState())
      // Will be returned by store.dispatch(action).
      return result
    }
  }
}

export const store = createStore(
  rootReducer,
  undefined,
  composeWithDevTools(applyMiddleware(myMiddlewareWithResultOnDispatch))
)
const result = store.dispatch({ type: "foo", payload: "bar" })
```

> 💡 [`composeWithDevTools`](https://github.com/zalmoxisus/redux-devtools-extension) wraps the
> middleware so that you can debug it in
> [Chrome DevTools](https://developer.chrome.com/docs/devtools/) after you install the
> [Redux DevTools Chrome extension](https://github.com/zalmoxisus/redux-devtools-extension).

Notes on this code.

1. This middleware actually returns something when `store.dispatch(action)` is called. You don't
   have to use this but its there if you need this behavior. Typically the last line would be
   `return next(action)`.
2. The call to `next(action)` is a continuation of the journey of the `action` to the next
   middleware in the chain of middleware that may be in the pipeline.
3. You can use `store.getState()` to access the store's state object at any point.

Here's a chain of simpler middleware that don't return a result and use more concise arrow functions
syntax.

```typescript
import { createStore, applyMiddleware } from "redux"

export const middlewareConsoleLog = (store) => (next) => (action) => {
  console.log("action", action, "state", store.getState())
  return next(action)
}

export const middlewareConsoleError = (store) => (next) => (action) => {
  console.error("action", action, "state", store.getState())
  return next(action)
}

export const store = createStore(
  rootReducer,
  undefined,
  applyMiddleware(middlewareConsoleLog, middlewareConsoleError)
)
store.dispatch({ type: "foo", payload: "bar" })
```

Notes on this code.

1. Middleware form a pipeline around the store's dispatch method. When we call
   `store.dispatch(action)` we are actually just calling the first middleware in the pipeline (which
   is `middlewareConsoleLog` function). Typically, a middleware will check to see if the action is a
   specific type that it cares about, much like a reducer would. If it's the right type, the
   middleware might run some custom logic. Otherwise, it passes the action to the next middleware in
   the pipeline.
2. Unlike a reducer, middleware can have [side effects](#no-side-effects-pure-functions-only),
   including timeouts and other async logic.
3. When an action is dispatched to the store, the `middlewareConsoleLog` middleware is the first to
   run and the last to finish. Here are the functions that the `action` is passed thru, when
   `store.dispatch(action)` is called.
4. `middlewareConsoleLog` (due to `store.dispatch(action)` call)
5. `middlewareConsoleError`
6. Original call to `store.dispatch(action)`
7. The root reducer inside `store`

### Async logic and data fetching

Here is an example of running async code in middleware:

1. `delayedActionMiddleware` uses `setTimeout()` to delay execution of an action.
2. `fetchTodosMiddleware` uses `axios` to make a REST API call.

```typescript
import { createStore, applyMiddleware } from "redux"

const delayedActionMiddleware = (store) => (next) => (action) => {
  if (action.type === "todos/todoAdded") {
    // Delay this action by one second.
    setTimeout(() => {
      store.dispatch(action)
    }, 1000)
    return
  }

  return next(action)
}

const fetchTodosMiddleware = (store) => (next) => (action) => {
  if (action.type === "todos/fetchTodos") {
    // Make an async API call to fetch todos from the server.
    _also("https://myapi.com/endpoint", async (it) => {
      const { data: payload } = await axios.get(it)
      // Dispatch an action with the todos we received.
      store.dispatch({ type: "todos/todosLoaded", payload })
    })
  }

  return next(action)
}

export const store = createStore(
  rootReducer,
  undefined,
  applyMiddleware(delayedActionMiddleware, fetchTodosMiddleware)
)
store.dispatch({ type: "todos/todoAdded", payload: [] })
store.dispatch({ type: "todos/fetchTodos" })
```

#### Redux "Thunk" middleware

Additionally, Redux provides a [`redux-thunk` middleware](https://github.com/reduxjs/redux-thunk)
which allows you to dispatch functions to the store rather than actions.

> ⚡ This is available via npm (`npm i redux-thunk`) if you want to use it.

- Pros:
  1. You can re-use business logic that isn't tied to a specific store.
- Cons:
  1. You [lose](https://redux.js.org/usage/usage-with-TypeScript#type-checking-middleware) some
     TypeScript protections and have to
     [`unknown`](https://mariusschulz.com/blog/the-unknown-type-in-TypeScript) type escape hatch.
  2. It is yet another pattern to learn / adopt, even though you can just make your own
     [enhancer](#enhancer) or [middleware](#middleware). And the code for thunk middleware is about
     [14 LOC](https://github.com/reduxjs/redux-thunk/blob/master/src/index.js).

> 💡 This [article](https://morioh.com/p/8f447daaaca6) goes into a lot of detail about thunks and
> how to think about them, and use them.

This is how you can use the `redux-thunk` middleware.

> 💡 A thunk can also return a promise. And a component can await the result of that promise in a
> component. You can pass both async and "normal" functions to `dispatch`. Here are the
> [official Redux docs](https://redux.js.org/tutorials/fundamentals/part-7-standard-patterns#thunks-and-promises)
> on this.

```typescript
import { createStore, applyMiddleware } from "redux"
import thunkMiddleware from "redux-thunk"
import { composeWithDevTools } from "redux-devtools-extension"

// The store now has the ability to accept thunk functions in `dispatch`.
const store = createStore(
  rootReducer,
  undefined,
  composeWithDevTools(applyMiddleware(thunkMiddleware))
)

// This function returns a function which returns a promise.
// More info: https://stackoverflow.com/q/54426176/2085356
function loadDataReturnsPromise() {
  return (dispatch) => {
    return axios
      .get("https://myapi.com/endpoint")
      .then((res) => res.json())
      .then((data) => store.dispatch({ type: "todos/todosLoaded", data }))
      .catch((err) => console.error("error loading data", err))
  }
}

// function component that uses the async function (aka a promise is returned) above.
const Header = () => {
  const [text, setText] = useState("")
  const [status, setStatus] = useState("idle")
  const dispatch = useDispatch()

  const handleChange = (e) => setText(e.target.value)

  const handleKeyDown = async (e) => {
    // If the user pressed the Enter key:
    const trimmedText = text.trim()
    if (e.which === 13 && trimmedText) {
      // Create and dispatch the thunk function itself
      setStatus("loading")

      // Wait for the promise returned by loadDataReturnsPromise.
      await store.dispatch(loadDataReturnsPromise) // We are dispatching a function, not an action!

      // And clear out the text input
      setText("")
      setStatus("idle")
    }
  }

  let isLoading = status === "loading"
  let placeholder = isLoading ? "" : "Press enter to load data"
  let loader = isLoading ? <div className="loader" /> : null

  return (
    <header>
      <input
        placeholder={placeholder}
        autoFocus={true}
        value={text}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        disabled={isLoading}
      />
      {loader}
    </header>
  )
}
```

> 💡 [`composeWithDevTools`](https://github.com/zalmoxisus/redux-devtools-extension) wraps the
> middleware so that you can debug it in
> [Chrome DevTools](https://developer.chrome.com/docs/devtools/) after you install the
> [Redux DevTools Chrome extension](https://github.com/zalmoxisus/redux-devtools-extension).

The following is a simplistic example of how we could implement the "Thunk" middleware itself. Also,
[here is the actual implementation](https://github.com/reduxjs/redux-thunk/blob/master/src/index.js)
of `redux-thunk`.

> 💡 The core idea here is creating a function that takes `dispatch` and `getState` functions from
> the store, and then uses them in order to dispatch an action after executing some async logic. By
> passing the `dispatch` and `getState` to the lambda that you're passing, it frees this logic from
> being tied to a specific store.

```typescript
const asyncFunctionMiddleware = (store) => (next) => (action) => {
  // If the "action" is actually a function instead ...
  if (typeof action === "function") {
    // Then call the function and pass `dispatch` and `getState` as arguments.
    return action(store.dispatch, store.getState)
  }

  // Otherwise, it's a normal action - send it onwards.
  return next(action)
}

const fetchSomeData = (dispatch, getState) => {
  // Make an async API call to fetch todos from the server.
  _also("https://myapi.com/endpoint", async (it) => {
    const { data: payload } = await axios.get(it)
    // Dispatch an action with the todos we received.
    store.dispatch({ type: "todos/todosLoaded", payload })
    // Check the updated store state after dispatching
    console.log("State after loading: ", getState())
  })
}

const store = createStore(rootReducer, applyMiddleware(asyncFunctionMiddleware))
store.dispatch(fetchSomeData) // We are dispatching a function, not an action!
```

> ⚡ If you want to explore `redux-thunk` more deeply, here are the
> [official Redux docs](https://redux.js.org/tutorials/fundamentals/part-6-async-logic#redux-async-data-flow).

### Memoized selectors and Reselect

[Selector](#useselector-hook-and-react) functions accept the Redux `state` object as an argument and
return a value. This is a great place where we can not only access parts of the state, but also
_derive_ data from it.

Here's an example of a selector function that takes some "todo" items in the state and only returns
an array of ids (for each todo item).

```typescript
interface Todo {
  id: string
  text: string
  done: boolean
}
interface State {
  todos: Todo[]
}
const selectTodoIds = (state: State): string[] => state.todos.map((it: Todo) => it.id)
```

However, `Array.map()` will always return a new array reference. The `useSelector()` hook will be
run after every action is dispatched. And since this will result in a new array, the component will
re-render. Regardless of whether the `state.todos` has changed or not.

Clearly this is not desirable. We need to cache this array, so as not to force needless re-renders.
But we do need this selector function to return a new array when the underlying `state.todos`
actually changes.

What we need is a
[memoized selector function](https://redux.js.org/tutorials/fundamentals/part-7-standard-patterns#memoized-selectors).
Memoized selector functions are selectors that save the most recent result value, and if you call
them multiple times with the same inputs, will return the same result value. If you call them with
different inputs than last time, they will recalculate a new result value, cache it, and return the
new result.

This is where the `reselect` npm package comes in. We do have to modify our selector function in
order to use it w/ `reselect`.

> ⚡ You can install `reselect` via `npm i reselect`.

We have to split our logic into two pieces:

1. _Input selector_ - This function allows `reselect` to understand what the inputs are. It can
   cache the output for a given input, and if these don't change, then it will be a cache hit. When
   the input changes (from what was calculated earlier) then this is a cache miss.
2. _Output selector_ - This function allows the output value that will be cached, to actually be
   generated. When there's a cache hit, this won't be run. When there's a cache miss, this will be
   executed with the argument(s) passed from the input selector.

```typescript
import { createSelector } from "reselect"
import React, { FC } from "react"
import { useSelector } from "react-redux"
import { _also } from "r3bl-ts-utils"

interface Todo {
  id: string
  text: string
  done: boolean
}
interface State {
  todos: Todo[]
}

const selectTodoIds = createSelector(
  /* Input selector : */ (state: State): Todo[] => state.todos,
  /* Output selector: */ (todos: Todo[]): string[] => todos.map((it: Todo) => it.id)
)

const TodoList: FC = () => {
  const todoIds: string[] = useSelector(selectTodoIds)

  return (
    <ul>
      {_also(new Array<ReactElement>(), (elem: ReactElement[]) => {
        todoIds.forEach((todoId: string) => elem.push(<li key={todoId}>todoId={todoId}</li>))
      })}
    </ul>
  )
}
```

Any time the `state.todos` array changes, we're going to create a new todo IDs array as a result.
That includes any immutable updates to todo items like toggling their `done` field, since we have to
create a new array for the immutable update.

This example only showed how to deal w/ one argument. What if you have a selector that can handle
multiple arguments? The `createSelector()` function can actually take any number of input selectors
as long as there is a single output selector. The set of values for the input selectors and the
output selector be cached. So let's say that we want to extend the example above to create a
selector that only returns the todo ids that are marked as done. Here's what this might look like.

```typescript
import { createSelector } from "reselect"

interface Todo {
  id: string
  text: string
  done: boolean
}
interface State {
  todos: Todo[]
  filterByDone: boolean
}

const selectDoneTodoIds = createSelector(
  /* Input selector #1 : */ (state: State): Todo[] => state.todos,
  /* Input selector #2 : */ (state: State): boolean => state.filterByDone,
  /* Output selector   : */ (todos: Todo[], filterByDone: boolean): string[] =>
    todos.filter((todo: Todo) => todo.done === true).map((todo: Todo) => todo.id)
)
```

### Undo history

With Redux implementing undo history is a breeze.
[Here](https://redux.js.org/usage/implementing-undo-history) are the official docs on this. Since
reducers are pure functions w/ no [side effects](#no-side-effects-pure-functions-only), state is
immutable, it makes it possible to very easily switch to an older state in the stack of state
histories!

#### Data structure and algorithm

Here's the basic shape of the undo history data structure (or stack). `T` is the type of the `state`
object that's in our Redux store.

```typescript
interface UndoHistory<T> {
  past: T[]
  present: T
  future: T[]
}
```

We have to define two additional
[actions](#step-1---define-the-types-for-the-state-action-then-use-them-to-create-a-reducer-function)
to operate on this state: `UndoAction` and `RedoAction`.

```typescript
// Undo and redo actions.
interface ActionUndo {
  type: "UNDO"
}
interface ActionRedo {
  type: "REDO"
}

// Other actions.
interface ActionAdd {
  type: "add"
  content: string
}
interface ActionRemove {
  type: "remove"
  id: string
}

type Action = ActionAdd | ActionRemove | ActionUndo | ActionRedo
```

> ⚠ The undo and redo action types are both in all caps to preserve compatibility w/ the
> `redux-undo` package (in case you want to use that) which is shown in the
> [next section](#using-the-redux-undo-package).

Here's our algorithm to implement undo and redo.

- Handling Other Actions:
  1. Insert the `present` at the end of the `past`.
  2. Set the `present` to the new state after handling the action.
  3. Clear the `future`.
- Handling Undo:
  1. Remove the last element from the `past`.
  2. Set the `present` to the element we removed in the previous step.
  3. Insert the old `present` state at the beginning of the `future`.
- Handling Redo:
  1. Remove the first element from the `future`.
  2. Set the `present` to the element we removed in the previous step.
  3. Insert the old `present` state at the end of the `past`.

#### Naive implementation

Here's what the code for this might look like, by creating a higher-order reducer to handle the undo
and redo actions.

```typescript
import { createStore } from "redux"

/**
 * Define the undo reducer enhancer function, and the wrapped state shape.
 *
 * - S: the type of the actual state.
 * - A: the Action type of the discriminated union.
 */

interface UndoHistoryStateWrapper<S> {
  past: S[]
  present: S
  future: S[]
}

function undoable<S, A>(reducer: (wrappedState: UndoHistoryStateWrapper<S>, action: A) => S) {
  // Call the reducer with empty action to populate the initial state.
  const initialState: UndoHistoryStateWrapper<S> = {
    past: new Array<S>(),
    present: reducer(undefined, {}),
    future: new Array<S>(),
  }

  // Return a reducer that handles undo and redo
  return function (
    wrappedState: UndoHistoryStateWrapper<S> = initialState,
    action: A
  ): UndoHistoryStateWrapper<S> {
    const { past, present, future } = wrappedState

    switch (action.type) {
      case "undo":
        const previous = past[past.length - 1]
        const newPast = past.slice(0, past.length - 1)
        return {
          past: newPast,
          present: previous,
          future: [present, ...future],
        }
      case "redo":
        const next = future[0]
        const newFuture = future.slice(1)
        return {
          past: [...past, present],
          present: next,
          future: newFuture,
        }
      default:
        // Delegate handling the action to the passed reducer.
        const newPresent: S = reducer(present, action)
        if (present === newPresent) {
          return wrappedState
        }
        return {
          past: [...past, present],
          present: newPresent,
          future: [],
        }
    }
  }
}

// Use the enhanced reducer in the code below.

interface ActionUndo {
  type: "UNDO" // All caps for compatibility w/ `redux-undo` package.
}
interface ActionRedo {
  type: "REDO" // All caps for compatibility w/ `redux-undo` package.
}
interface ActionAdd {
  type: "add"
  content: string
}
interface ActionRemove {
  type: "remove"
  id: string
}
type Action = ActionAdd | ActionRemove | ActionUndo | ActionRedo

interface ActualState {
  todos: Todo[]
}
interface Todo {
  text: string
  done: boolean
}

const reducerFn = (state: UndoHistoryStateWrapper<ActualState>, action: Action) => {}
const store = createStore(undoable<ActualState, Action>(reducerFn))
store.dispatch({
  type: "add",
  content: "Use Redux",
})
store.dispatch({
  type: "UNDO",
})
```

#### Using the redux-undo package

Instead of implementing all this from scratch (like we did in previous section), we can simply use
the `redux-undo` package.

> ⚡ You can install the `redux-undo` package using `npm i redux-undo`.

This package provides an `undoable()` function, that replaces ours (which is shown in the previous
section). You can use it like so.

```typescript
import undoable from "redux-undo"

const store = createStore(undoable(reducerFn))
store.dispatch({
  type: "add",
  content: "Use Redux",
})
store.dispatch({
  type: "UNDO",
})
```

If you were using your actual reducer function (`reducerFn`) in other parts of your code, then you
can just continue doing so w/out any changes (eg: in any `combineReducers()` calls).

However, the way in which you access your state will change. Instead of using `state.todos` like you
would in the past, you now have to use `state.todos.present`, since the `ActualState` is wrapped in
`UndoHistoryStateWrapper<ActualState>`.

If you want to add buttons for undo and redo, you will need the following information.

- `state.todos.past.length > 0` means you can enable undo button.
- `state.todos.future.length > 0` means you can enable redo button.
- In order to dispatch the undo action, you can write `store.dispatch( {type: "UNDO"} )`.
- In order to dispatch the redo action, you can write `store.dispatch( {type: "REDO"} )`.

> ⚡ Here's more information on undo redo in the
> [official Redux documentation](https://redux.js.org/usage/implementing-undo-history).

## Testing with react-testing-library

CRA comes w/ Jest and TypeScript support built-in, so writing tests using Jest, TypeScript, and
`react-testing-library` (aka RTL or React Testing Library) is really straightforward.

> ⚡ You can get more info about what comes out of the box w/ CRA
> [here](https://create-react-app.dev/docs/running-tests/#react-testing-library).

Here are some of the top benefits of using Jest & RTL:

1. You can test your components in isolation from the child components they render.
2. You can use real DOM nodes because the tests assert actual behavior that a user would experience
   and not React [Virtual DOM](https://reactjs.org/docs/faq-internals.html) implementation /
   internals.
3. A real browser isn't used to run your tests. Jest will use
   [JSDOM](https://github.com/jsdom/jsdom) which implements the DOM API in pure Javascript, and runs
   in a Node.js instance on your machine (or whatever machine you run the tests on).
4. You can do blackbox and integration testing by
   [mocking web services](https://github.com/mswjs/msw).

> ⚡ More information on RTL:
>
> 1. [Introduction](https://testing-library.com/docs/react-testing-library/intro/)
> 2. [Example w/ explanation](https://testing-library.com/docs/react-testing-library/example-intro/)
> 3. [Example in codesandbox.io](https://codesandbox.io/s/github/kentcdodds/react-testing-library-examples)
> 4. [Cheatsheet](https://testing-library.com/docs/react-testing-library/cheatsheet)

### Use RTL instead of Enzyme

1. RTL is a replacement for [`Enzyme`](http://airbnb.io/enzyme/).

- Both `Enzyme` and RTL are built on top of:
  - [`react-dom`](https://reactjs.org/docs/react-dom.html)
  - [`react-dom/test-utils`](https://reactjs.org/docs/test-utils.html)
  - [`react-test-renderer`](https://reactjs.org/docs/test-renderer.html)
- `Enzyme` encourages (and provides utilities for) testing implementation details with rendered
  instances of components, whereas RTL encourages testing only the "end result" by querying for and
  making assertions about actual DOM nodes.
- [Here is a list](https://stackoverflow.com/a/54153026/2085356) of differences between the two.

2. Rather than dealing with ([Virtual DOM](https://reactjs.org/docs/faq-internals.html)) instances
   of rendered React components, your tests will work with actual DOM nodes.

- The utilities RTL provides facilitate querying the DOM in the same way the user would.
- Finding form elements by their label text (just like a user would), finding links and buttons from
  their text (like a user would).
- It also exposes a recommended way to find elements by a `data-testid` as an "escape hatch" for
  elements where the text content and label do not make sense or is not practical.

> 💡 RTL is built on top of
> [`dom-testing-library`](https://testing-library.com/docs/dom-testing-library/intro/) which
> provides the underlying APIs for testing DOM nodes.
>
> - Jest runs RTL tests in a
>   [headless environment](https://testing-library.com/docs/dom-testing-library/intro/#this-solution),
>   since the entire DOM API is implemented in pure Javascript by
>   [JSDOM](https://github.com/jsdom/jsdom).
> - The DOM implementation runs in a Node.js environment on the machine in which the tests are
>   running in and not a real browser.
> - This isn't like
>   [`Karma`](https://developerlife.com/2019/07/06/starter-project-TypeScript-karma-jasmine-webpack/)
>   test runner which will spool up an actual browser to run the tests in. This makes these tests
>   very fast.

3. You can also mock web services for your tests (Node.js instances are spawned on the machine in
   which you are running the tests), using [`msw`](https://github.com/mswjs/msw) to test out `fetch`
   calls.
   [Here is an example](https://testing-library.com/docs/react-testing-library/example-intro).

### Install the required packages for RTL

To get started you should install the RTL and `jest-dom` packages.

```shell
npm install --save @testing-library/react @testing-library/jest-dom
```

Next, modify your
[`src/setupTests.ts`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/setupTests.ts)
file by adding this line.

```typescript
// react-testing-library renders your components to document.body,
// this adds jest-dom's custom assertions
import "@testing-library/jest-dom"
```

### Basic unit tests

Writing simple unit tests are no different in Jest than they are using Jasmine. Here's an example of
a simple unit test that is self contained and doesn't really have a system under test. The system
under test is the `MyMatcher` class which is declared in the test itself. This class is meant to
mimic a Jasmine matcher. And the tests assert that it works as expected.

```typescript
import { _also } from "r3bl-ts-utils"

class MyMatcher {
  constructor(private _arg: boolean = false) {}

  set arg(value: boolean) {
    this._arg = value
  }
  get arg(): boolean {
    return this._arg
  }

  isFalse = (): boolean => !this.arg

  isTrue = (): boolean => this.arg

  get not(): MyMatcher {
    return new MyMatcher(!this.arg)
  }
}

describe("MyMatcher -> myMatcher(arg)", () => {
  const myMatcher: MyMatcher =
    /* new MyMatcher(true) */
    _also(new MyMatcher(), (it) => (it.arg = true))
  test("myMatcher.isTrue() is true", () => expect(myMatcher.isTrue()).toBe(true))
  test("myMatcher.isFalse() is false", () => expect(myMatcher.isFalse()).toBe(false))
  test("myMatcher.not.isTrue() is false", () => expect(myMatcher.not.isTrue()).toBe(false))
})
```

> 💡 TypeScript has an awesome
> ["escape hatch"](https://github.com/microsoft/TypeScript/issues/19335) to allow private variables
> to be accessed in tests. Here's a detailed
> [SO answer](https://stackoverflow.com/a/35991491/2085356) on this topic.
>
> Here's an example:
>
> - Let's say you have a class with a private variable named `_x` like so:
>   `class Clazz {private _x:number = 0}`
> - Then you can access it w/ type safety in a test when using the array access syntax, eg:
>   `new Clazz()[_x]`, which will be treated as a `number`.
> - So you can assert `expect(typeof new Clazz()[_x]).toBe('number')`.

### Complex unit tests

Let's write a test for the reducer function of
[`SimpleReduxComponent.tsx`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/redux/SimpleReduxComponent.tsx).
The tests will be pretty simple, w/ the only complication being the way in which the function and
types themselves are exported. The test needs to know some internals about the component which users
of this component don't really need to know about (nor should they, since that would break
encapsulation).

In order to implement this, one approach is to use a namespace that simply exports only the required
symbols for testing (this is done in the `SimpleReduxComponent.tsx` file). Here are the fewest
symbols that need to be accessible by the test.

```typescript
// Export namespace for testing.
export namespace SimpleReduxComponentForTesting {
  export const _reducerFn: Reducer<State | undefined, Action> = reducerFn
  export type _State = State
  export type _Action = Action
}
```

> 💡 The symbols all have to be renamed for this namespace, otherwise, they would collide w/ their
> original declarations.

These symbols are then imported in the actual test, like this:

```typescript
import { SimpleReduxComponentForTesting } from "../SimpleReduxComponent"
type State = SimpleReduxComponentForTesting._State | undefined
type Action = SimpleReduxComponentForTesting._Action
const reducerFn: Reducer<State, Action> = SimpleReduxComponentForTesting._reducerFn
```

Now that the exports are complete, the test itself is pretty simple. Here's the
[`SimpleReduxComponent.test.tsx`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/redux/__tests__/SimpleReduxComponent.test.tsx).
The test is pretty simple, it does the following things:

1. Tests to see that the initial state is generated correctly by the reducer function.
2. Tests to see whether dispatching an add action actually adds something to the state.
3. Tests to see whether dispatching a remove action actually removes something from the state.

```typescript
import { SimpleReduxComponentForTesting } from "../SimpleReduxComponent"
import { Reducer } from "@reduxjs/toolkit"

describe("SimpleReduxComponent reducer function", () => {
  type State = SimpleReduxComponentForTesting._State | undefined
  type Action = SimpleReduxComponentForTesting._Action
  const reducerFn: Reducer<State, Action> = SimpleReduxComponentForTesting._reducerFn

  test("sets initial state", () => {
    const ignoredAction: Action = { type: "add", content: "text" }
    const state: State = reducerFn(undefined, ignoredAction)
    console.log(state)
    expect(state!!.textArray).toHaveLength(2)
  })

  test("dispatch add action works", () => {
    const action: Action = { type: "add", content: "foo" }
    const initialState: State = {
      textArray: [
        { id: "id4", content: "fffff" },
        { id: "id5", content: "gggg" },
      ],
    }
    const newState: State = reducerFn(initialState, action)
    console.log(newState)
    expect(initialState).not.toEqual(newState)
    expect(newState!!.textArray).toHaveLength(3)
    expect(newState!!.textArray[2]).toMatchObject({ content: "foo" })
  })

  test("dispatch remove action works", () => {
    const action: Action = { type: "remove", id: "id4" }
    const initialState: State = {
      textArray: [
        { id: "id4", content: "fffff" },
        { id: "id5", content: "gggg" },
      ],
    }
    const newState: State = reducerFn(initialState, action)
    console.log(newState)
    expect(initialState).not.toEqual(newState)
    expect(newState!!.textArray).toHaveLength(1)
    expect(newState!!.textArray[0]).toMatchObject({ content: "gggg" })
  })
})
```

### Basic UI tests

In order to write UI tests we will be using a combination of APIs from:

1. [RTL](https://testing-library.com/docs/react-testing-library/api) - APIs like
   [`render()`](https://testing-library.com/docs/react-testing-library/api#render) will render your
   component into a container that is appended to `document.body`. This container is
   [automatically removed](https://testing-library.com/docs/react-testing-library/api#cleanup) from
   when the test completes, so make sure to call `render()` at the start of each `it` or `test`
   block.
2. [dom-testing-library](https://testing-library.com/docs/queries/about) - APIs like
   [`getByRole()`](https://testing-library.com/docs/queries/byrole) will allow you to interrogate
   the JSDOM and assert things about it. Here's a list of
   [HTML ARIA roles](https://www.w3.org/TR/html-aria/#docconformance) that are used to match DOM
   elements.

> ⚡ Here's an example of a simple UI tests
> [`SimpleReduxCompoennt.test.tsx`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/redux/__tests__/SimpleReduxComponent.test.tsx).

The basic structure of the UI tests are very similar.

1. Render some component that you are testing (the system under test).
2. Wait for HTML element to be added to the DOM (via call to `screen`).
3. Assert that the DOM looks the way you expect. Or fire an event here, and then check to see that
   the DOM is what you expect.

Here's the simplest test case.

```typescript
test("displays few list items at start", async () => {
  render(
    <Provider store={store}>
      <SimpleReduxComponent />
    </Provider>
  )
  await waitFor(() => screen.getByRole("list"))
  expect(screen.getByRole("list").children).toHaveLength(2)
})
```

Here's a test case where an event is fired before the DOM is checked.

```typescript
test("clicking item removes it", async () => {
  render(
    <Provider store={store}>
      <SimpleReduxComponent />
    </Provider>
  )
  await waitFor(() => screen.getByRole("list"))
  fireEvent.click(screen.getByRole("list").children[0])
  expect(screen.getByRole("list").children).toHaveLength(2)
})
```

### Complex UI tests

In this section we will write a test that deals with resizing a browser window (such as what you
would need to do to test media queries). Here are the key things that we will cover in this example:

1. How to resize a JSDOM browser window (since an actual browser is not used).
2. How to wrap React updates in
   [`act()`](https://davidwcai.medium.com/react-testing-library-and-the-not-wrapped-in-act-errors-491a5629193b).

Here's the system under test.

> ⚡
> [`ComponentWithoutState.tsx`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/basics/ComponentWithoutState.tsx).

```typescript
import { MessagePropsWithChildren } from "../types"
import styles from "../../styles/App.module.css"
import React, { Dispatch, SetStateAction, useEffect, useState } from "react"
import { _let } from "r3bl-ts-utils"

export const TestIdWindowSize = "test-id-window-size"

const setWindowSize = (
  setWidth: Dispatch<SetStateAction<number>>,
  setHeight: Dispatch<SetStateAction<number>>
) => {
  setWidth(window.innerWidth)
  setHeight(window.innerHeight)
}

type SizeStateHookType = [number, Dispatch<SetStateAction<number>>]

export const ComponentWithoutState = (props: MessagePropsWithChildren) => {
  const [width, setWidth]: SizeStateHookType = useState(0)
  const [height, setHeight]: SizeStateHookType = useState(0)

  useEffect(
    () =>
      _let(
        (event: UIEvent) => setWindowSize(setWidth, setHeight),
        (it) => {
          window.addEventListener("resize", it)
          return () => window.removeEventListener("resize", it)
        }
      ),
    [] /* Run once, like componentDidMount. */
  )

  useEffect(() => setWindowSize(setWidth, setHeight), [] /* Run once, like componentDidMount. */)

  const render = () => (
    <section className={styles.Container}>
      <code>{props.message}</code>
      {props.children}
      <div data-testid={TestIdWindowSize}>{`${width} x ${height}`}</div>
    </section>
  )

  return render()
}
```

And here's the test file itself. In this test, the window is resized after rendering the component.
Then the component is checked to see whether it got this change in width and height. If you were
using a media query then you would check the DOM to see whether the structure that you were
expecting is actually present.

> ⚡
> [`MediaQueryTest.test.tsx`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/__tests__/MediaQueryTest.test.tsx)

```typescript
import { render, screen, waitFor } from "@testing-library/react"
import React from "react"
import { act } from "react-dom/test-utils"
import { ComponentWithoutState, TestIdWindowSize } from "../components/basics/ComponentWithoutState"

/** Get around `window.innerWidth` and `window.innerHeight` are readonly. */
const resizeWindow = (x: number, y: number) => {
  window = Object.assign(window, { innerWidth: x })
  window = Object.assign(window, { innerHeight: y })
  window.dispatchEvent(new Event("resize"))
}

describe("media query test", () => {
  it("should be large window size", async () => {
    render(
      <div>
        <ComponentWithoutState message={"test"} />
      </div>
    )

    // Wrap any calls to React state changes in act().
    // More info: https://davidwcai.medium.com/react-testing-library-and-the-not-wrapped-in-act-errors-491a5629193b
    act(() => resizeWindow(2000, 1000))

    await waitFor(() => screen.getByTestId(TestIdWindowSize))

    const checkContent = screen.getByTestId(TestIdWindowSize)
    expect(checkContent).toHaveTextContent("2000 x 1000")
  })
})
```

> 💡 Note the use of [`act()`](https://reactjs.org/docs/testing-recipes.html#act) to wrap the call
> to `resizeWindow()`. This is necessary when you write code that mutates a component's state using
> one of your functions. This ensures that all the required work has been done before you make your
> DOM assertions.

### Writing integration tests

#### Install msw package

In order to mock web services, you will need to install the
[`msw` module](https://github.com/mswjs/msw) as a dev dependency.

```shell
npm i -D msw
```

> ⚡ Learn more about mocking REST APIs (using `msw`)
> [here](https://mswjs.io/docs/getting-started/mocks/rest-api).

> ⚡ This is a great
> [tutorial](https://dev.to/kettanaito/type-safe-api-mocking-with-mock-service-worker-and-TypeScript-21bf)
> on using `msw` and TypeScript.

#### Mocking the server (REST API endpoints)

Before we get started writing the test, here are some functions that need to be created in order to
mock the search endpoint of the `TheCatApi.com`.

> ⚡ Here's the full source file
> [`TestUtils.ts`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/cat_api/__tests__/TestUtils.ts).

1. **Setup and teardown** - Create the server and tie its start and stop w/ the lifecycle of the
   tests.

   ```typescript
   export function setupAndTeardown(): SetupServerApi {
     const server: SetupServerApi = setupServer()
     beforeAll(() => server.listen())
     afterEach(() => server.resetHandlers())
     afterAll(() => server.close())
     return server
   }
   ```

   > ⚠ Make sure to call `setupAndTeardown()` at the start of your actual UI test.

2. **[Define](https://stackoverflow.com/questions/1410563/what-is-the-difference-between-a-definition-and-a-declaration)
   the data returned by the mock API** - Here are some supporting constants that are needed in the
   next steps.

   ```typescript
   export const cannedResponseOk = [
     {
       breeds: [],
       categories: [],
       id: "jK5X2xGJ7",
       url: "https://cdn2.thecatapi.com/images/jK5X2xGJ7.jpg",
     },
     {
       breeds: [],
       categories: [],
       id: "9c6",
       url: "https://cdn2.thecatapi.com/images/9c6.jpg",
     },
     {
       breeds: [],
       categories: [],
       id: "ab8",
       url: "https://cdn2.thecatapi.com/images/ab8.jpg",
     },
   ]
   const TheCatApi = {
     apiKey: process.env.REACT_APP_CAT_API_KEY,
     search: {
       host: "https://api.thecatapi.com",
       endpoint: "/v1/images/search",
       config: { params: { limit: 3, size: "full" } },
     },
   }
   ```

3. **Mock the REST API w/ handlers for the happy path** - Create the function that handles HTTP GET
   requests that are made to `https://api.thecatapi.com/v1/images/search`.

   ```typescript
   // More info: https://mswjs.io/docs/getting-started/mocks/rest-api
   export const restHandlerSearchOk: RestHandler = rest.get(
     TheCatApi.search.host + TheCatApi.search.endpoint,
     (
       req: RestRequest<DefaultRequestBody, RequestParams>,
       res: ResponseComposition,
       ctx: RestContext
     ) => {
       console.log("restHandlerSearchOk.req", req)
       // console.log("req.url.searchParams", req.url.searchParams)
       // console.log("req.params", req.params)
       return res(ctx.json(cannedResponseOk))
     }
   )
   ```

4. **Mock the REST API w/ handlers for the unhappy path** - Create a function that handles returning
   a  
   [`500` HTTP error code](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500) for HTTP
   GET requests that are made to `https://api.thecatapi.com/v1/images/search`.

   ```typescript
   export const restHandlerSearchError: RestHandler = rest.get(
     TheCatApi.search.host + TheCatApi.search.endpoint,
     (
       req: RestRequest<DefaultRequestBody, RequestParams>,
       res: ResponseComposition,
       ctx: RestContext
     ) => {
       console.log("restHandlerSearchError.req", req)
       // console.log("req.url.searchParams", req.url.searchParams)
       // console.log("req.params", req.params)
       return res(ctx.status(500))
     }
   )
   ```

#### Testing the mocked server (REST API endpoints) itself

Now w/ the setup and supporting functions out of the way, we can actually write the tests. The tests
shown here actually don't have a React component under test, they're just tests that make `axios`
calls to the mocked API endpoints.

> ⚡ Here's the full source file
> [`TheCatApiEndpointMock.test.tsx`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/cat_api/__tests__/TheCatApiEndpointMock.test.tsx).

1. **Setup the server** - The first step is calling `setupAndTeardown()` at the start of your test.

   ```typescript
   const server: SetupServerApi = setupAndTeardown()
   ```

2. **Test the happy path mocked endpoint** - The test does quite a few things.

   ```typescript
   test("TheCatApi search endpoint works", async () => {
     server.use(restHandlerSearchOk)
     axios.defaults.headers.common["x-api-key"] = TheCatApi.apiKey
     _also(TheCatApi.search, async (it) => {
       const { data: payload } = await axios.get(it.host + it.endpoint, it.config)
       expect(payload).toHaveLength(3)
     })
   })
   ```

3. First, it sets up the server to handle the search endpoint of the REST API.

   - It binds the `restHandlerSearchOk` to the server via `server.use()`.
   - All `RestHandlers` registered via `use()` will be torn down after each test in the
     `afterEach()` call (declared in in the first step).

4. Then, it connects to the `msw` mock server and makes the GET request, gets the response, and
   makes the assertion that 3 items are in the `payload`.

   > ⚠ One thing to note is that the URL query params that are sent via HTTP GET (from the `axios`
   > call in the following step) don't actually show up on the mocked server. However, the headers
   > do show up.

5. **Test the unhappy path mocked endpoint** - This test is very similar to the previous one, except
   that the REST API is mocked to throw a
   [`500` HTTP error code](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500). It also
   demonstrates how to detect errors for async functions.

   ```typescript
   // More info: https://stackoverflow.com/a/47887098/2085356
   const makeGetRequest: () => Promise<any> = async () =>
     _let(TheCatApi.search, async (it) => {
       axios.defaults.headers.common["x-api-key"] = TheCatApi.apiKey
       const { data: payload } = await axios.get(it.host + it.endpoint, it.config)
       return payload
     })

   test("TheCatApi endpoint fails as expected", async () => {
     server.use(restHandlerSearchError)
     await expect(makeGetRequest()).rejects.toThrow(Error)
   })
   ```

#### Using the mocked server in a UI test

Now that we have the endpoints mocked and tested, we can write tests that renders a React component
which uses these endpoints.

> ⚡ Here's the full source file
> [`TheCatApiEndpointMock.test.tsx`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/cat_api/__tests__/TheCatApiEndpointMock.test.tsx).

We are going to write two tests. One that makes sure that the `CatApiComponent` renders a list of
images when the search endpoint returns a valid result. Another that renders an error message when
the search endpoint returns an error. Here's the `describe` block containing these which is simply
added to our previous test.

```typescript
import { CatApiComponent, TheCatApi } from "../CatApiComponent"

describe("CatApiComponent works as expected ⤵", () => {
  test("Component renders results with API happy path", async () => {
    server.use(restHandlerSearchOk)
    render(<CatApiComponent.FC />)
    await waitFor(() => screen.getByRole("list"))
    console.log(prettyDOM(screen.getByRole("list")))
    expect(screen.getAllByRole("listitem").length).toBe(3)
  })

  test("Component renders error state with API unhappy path", async () => {
    server.use(restHandlerSearchError)
    render(<CatApiComponent.FC />)
    await waitFor(() => screen.getByTestId(CatApiComponent.TestIds.fetchError))
    console.log(prettyDOM(screen.getByTestId(CatApiComponent.TestIds.fetchError)))
    expect(screen.getByRole("heading")).toHaveTextContent(
      "Error: Request failed with status code 500"
    )
  })
})
```

There are a couple of things to note in this test.

1. You can use ARIA to search for components using `screen.getByRole()` or you can use the
   `data-testid` / `screen.getByTestId()` mechanism. You can see the use of each one in the test
   above.
2. Since we are using test ids, we are wrapping the ids and the React component in the
   `CatApiComponent` namespace. This allows us to have clean import statements that don't result in
   collisions of this component's test ids w/ any other variables or imports.

3. We can access the test ids via `CatApiComponent.TestIds`.
4. We can access the React component via `CatApiComponent.FC`.

5. The
   [`prettyDOM()`](https://testing-library.com/docs/dom-testing-library/api-debugging/#prettydom)
   function is really useful when trying to get a handle on the structure of the DOM for your
   assertions.
6. Since we are making async `axios` calls, we need to use `await waitFor(()=>screen.???)` so that
   the DOM is actually populated before we make our assertions.

### Writing snapshot tests

Snapshot testing was introduced in Jest around 2016, and it's meant to be a lightweight way to
perform UI tests and it is meant to be a complement (not replacement) for unit and integration
testing.

> 💡 Here are some good reference guides on snapshot testing:
>
> - [Why use snapshot testing](https://benmccormick.org/2016/09/19/testing-with-jest-snapshots-first-impressions/).
> - [Snapshot testing philosophy](https://jestjs.io/blog/2016/07/27/jest-14#why-snapshot-testing).
> - [Snapshot testing official guide](https://jestjs.io/docs/snapshot-testing).

The idea behind snapshot testing is that it should be easy to take a snapshot of what a component
should look like, and then compare any future changes to a component to this snapshot. This is meant
to be an easy way to do UI testing. There is no need to write any assertions for what is expected in
the DOM. Simply save the "last known good" snapshot of a component, and when any changes are made to
this component they will automatically be compared to the saved snapshot (when the tests are run).

> ⚡ Install the required packages for react-test-renderer
>
> In order to write these tests we must use `react-test-renderer` and not the RTL or
> `dom-testing-library`. Here are the things you must install to get started.
>
> ```shell
> # Install the package.
> npm install react-test-renderer
> # Get the TypeScript bindings for your IDE.
> npm i --save-dev @types/react-test-renderer
> ```

Here's a simple snapshot test for the
[`ComponentWithoutState.tsx`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/basics/ComponentWithoutState.tsx).

> 💡 Note that the first time you run this you will have to
> [update the snapshot](https://jestjs.io/docs/snapshot-testing#updating-snapshots). You can do that
> by doing any of the following:
>
> 1. Running the test in IDEA Ultimate or Webstorm.
> 2. In a terminal by using `npm test -u`. You can also interactively update the snapshots if you
>    run `npm test` in your terminal.

```typescript
import React from "react"
import renderer from "react-test-renderer"
import { ComponentWithoutState } from "../ComponentWithoutState"

it("ComponentWithoutState renders correctly", function () {
  const tree = renderer.create(<ComponentWithoutState message={"snapshot test"} />).toJSON()
  expect(tree).toMatchSnapshot()
})
```

> ⚡
> [ComponentWithoutState.snapshot.test.tsx](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/basics/__tests__/ComponentWithoutState.snapshot.test.tsx).

When a snapshot is updated it will create a file that you should check into your version control.
Here's an example of a snapshot file generated by the test above
[`/__tests__/__snapshots__/ComponentWithoutState.snapshot.test.tsx.snap`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/basics/__tests__/__snapshots__/ComponentWithoutState.snapshot.test.tsx.snap).

## Data APIs for development

Here are some data APIs that might be useful when building prototype apps.

- [TheCatApi](https://docs.thecatapi.com/api-reference/)
- [doc.ceo/dog-api](https://dog.ceo/dog-api/documentation/)
- [Hacker News API](https://hn.algolia.com/api)

## Debugging in Webstorm or IDEA Ultimate

Use this [guide](https://blog.jetbrains.com/webstorm/2017/01/debugging-react-apps/) for
`create-react-app`.

1. Simply `package.json` and click on the green arrow beside the "run" script.
2. In the tool window, press "Ctrl+Shift" and click on the `localhost:3000` hyperlink and that will
   spawn a debugging session w/ a Chrome browser that is spawned just for this session!
3. Save the run configurations produced by the steps above in the project file.
4. Also now that the JavaScript debugging session run configuration is created, you can just use
   `npm run start` to start the server in a terminal and still be able to debug it!

## Upgrade CRA itself to the latest version

Follow instructions in the
[CRA changelog](https://github.com/facebook/create-react-app/blob/main/CHANGELOG.md). For example,
you can run something like the following w/out ejecting CRA itself.

```shell
npm install --save --save-exact react-scripts@4.0.3
```

> ⚡ You can find the list of releases
> [here](https://github.com/facebook/create-react-app/releases).

You can upgrade any npm packages that you're using with the following.

```shell
npm update
```

## Using CRA and environment variables

Read all about how to do this in this
[guide](https://create-react-app.dev/docs/adding-custom-environment-variables/).

For example, to use the [Cat API](https://docs.thecatapi.com/), you have to do the following steps:

1. Get an API key from [https://thecatapi.com/](https://thecatapi.com/).
2. Save this API key as `REACT_APP_CAT_API_KEY` in `$HOME/.profile` (for Ubuntu & GNOME).

- You have to logout and log back in, in order for this to take effect on GUI apps launched via
  GNOME.
- CRA will grab all the environment variables that are prefixed w/ `REACT_APP` and compile them into
  the minified Javascript code that it generates.

3. In your TypeScript code, you can use the following variable `process.env.REACT_APP_CAT_API_KEY`
   in order to access the value of this environment variable.

## CSS Reset

In order to use CSS Reset, do the following:

1. Copy the contents of this [CSS file](https://meyerweb.com/eric/tools/css/reset/reset.css) into
   [`reset.css`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/styles/reset.css).
   Feel free to modify this file to suit your needs.
2. Then add `@import "reset.css";` to
   [`App.module.css`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/styles/App.module.css),
   which is used by
   [`App.tsx`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/App.tsx).
3. I also add entries for elements like `button` and `input` which are not explicitly set by the
   default Reset CSS stylesheet (and thus end up using user agent stylesheet, which isn't what I
   want and why I'm using Reset CSS in the first place).

> ⚠ `normalize.css` **did not work** for my needs (it's supported by CRA). Even after using the
> following instructions, the `browser user agent stylesheet` was just messing up all the spacing.
>
> - Using `normalize.css` is pretty straight forwards following this
>   [guide](https://www.albertgao.xyz/2018/11/11/8-features-you-can-add-after-using-create-react-app-without-ejecting/).
>   1. Simply run `npm install normalize.css`
>   2. Then add `import 'normalize.css'` line to the top of
>      [`index.tsx`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/index.tsx)
> - CRA comes w/ [`normalize.css`](https://create-react-app.dev/docs/adding-css-reset/).

## Using CSS class pseudo selectors to style child elements of a parent

Using CSS class pseudo selectors in order to style child elements of a parent (which has this style
applied) w/out having to manually assign classes to each of these children. Let's say that the
parent has this class
[`DottedBox`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/styles/App.module.css),
which will do this, here's the CSS. Here's a [video](https://youtu.be/9e-lWQdO-DA) by Kevin Powell
where he uses this pattern for flexbox.

1. `.DottedBox { padding: 8pt; border: 4pt dotted cornflowerblue; }`
2. `.DottedBox > * { /* this gets applied to all the children */ }`

## Composition over inheritance

Use [composition over inheritance](https://reactjs.org/docs/composition-vs-inheritance.html) to make
components reusable.

1. This happens when you think about a component as a "generic box" and simply pass other JSX
   elements inside of them as `props.children`.
2. You can see this in
   [`ComponentWithoutState`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/basics/ComponentWithoutState.tsx).
3. In order to get this to work with TypeScript you have to make sure to add this to the props type
   `childComp?: React.ReactNode`. For example, take a look at `MessagePropsWithChildren` in
   [`types.tsx`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/types.tsx)

## Callable

`Callable` interfaces are great, and I've done an implementation of this in
[`ColorConsole`](https://github.com/r3bl-org/r3bl-ts-utils/blob/main/src/color-console-utils.ts)
included in [`r3bl-ts-utils`](https://www.npmjs.com/package/r3bl-ts-utils).

- I took a slightly different approach this time, using the great information in this
  [SO Answer](https://stackoverflow.com/questions/12769636/how-to-make-a-class-implement-a-call-signature-in-TypeScript)
  which I also used in the `ColorConsole` implementation.
- Here are the key takeaways in the
  [`ReactReplayClassComponent`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/animate/ReactReplayClassComponent.tsx)
  implementation:
  1. A class can't implement the `Callable` interface.
  2. However, any member of the class can, and that member can be exposed as `Callable`.
  3. This member is exposed as a getter.
  4. This member can then be the only export in the module.
- In this case, the getter simply returns the reference to the 'generatorImpl' method. So we can
  write things like `GenerateReactElement.generator(...)` instead of just
  `GenerateReactElement.generator` (which is the normal use of a getter).

## TypeScript namespaces

> ⚡ Read the official TypeScript docs on
> [namespaces](https://www.TypeScriptlang.org/docs/handbook/namespaces.html).

They allow encapsulation of variables, types, and other symbols in a neat package. This can be
exported to other modules that need them or just be used inside a single file to organize and hide
details.

Here's an example of using this in
[`CatApiComponent.tsx`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/cat_api/CatApiComponent.tsx).
Here are some excerpts from this file.

Here is a snippet that shows the use of `namespace` to encapsulate the details of accessing this web
API.

```typescript
export namespace TheCatApi {
  export const apiKey = process.env.REACT_APP_CAT_API_KEY as string
  export const search = {
    host: "https://api.thecatapi.com",
    endpoint: "/v1/images/search",
    config: { params: { limit: 3, size: "full" } },
  } as const
  export type SearchResults = { id: string; url: string }
}
```

It is possible to import a symbol from one namespace, into another namespace, even in the same file.
Here's an excerpt from the
[`CatApiComponent.tsx`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/cat_api/CatApiComponent.tsx)
file used above.

```typescript
namespace MyActions {
  interface ActionFetchStart {
    type: "fetchStart"
  }

  interface ActionFetchOk {
    type: "fetchOk"
    payload: TheCatApi.SearchResults[]
  }

  interface ActionFetchError {
    type: "fetchError"
    error: any
  }

  export type Action = ActionFetchStart | ActionFetchOk | ActionFetchError
}
```

The encapsulated `namespace` for this web API can then be used in other files (eg:
[`TestUtils.ts`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/cat_api/__tests__/TestUtils.ts))
and
[`TheCatApiEndpointMock.test.tsx`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/cat_api/__tests__/TheCatApiEndpointMock.test.tsx).
Here are some excerpts from these files.

```typescript
import { TheCatApi } from "../CatApiComponent"

export const restHandlerSearchOk: RestHandler = rest.get(
  TheCatApi.search.host + TheCatApi.search.endpoint,
  (
    req: RestRequest<DefaultRequestBody, RequestParams>,
    res: ResponseComposition,
    ctx: RestContext
  ) => res(ctx.json(cannedResponseOk))
)

export const makeGetRequest: () => Promise<any> = async () =>
  _let(TheCatApi.search, async (it) => {
    axios.defaults.headers.common["x-api-key"] = TheCatApi.apiKey
    const { data: payload } = await axios.get(it.host + it.endpoint, it.config)
    return payload
  })
```

The following sections show different ways to use `namespace`.

- [One way of using namespaces to encapsulate React components for testing](#using-the-mocked-server-in-a-ui-test).
- [Another way of using namespaces to only export testing related symbols for testing](#complex-unit-tests)

## TypeScript readonly vs ReadonlyArray

More info on `readonly` vs `ReadonlyArray`:

- [Read-Only Array and Tuple Types in TypeScript](https://mariusschulz.com/blog/read-only-array-and-tuple-types-in-TypeScript)
- [Readonly vs ReadonlyArray](https://basarat.gitbook.io/TypeScript/type-system/readonly)

> 💡 Here's more info on TypeScript type narrowing, truthy/falsy, user defined type predicates, and
> discriminated unions from the
> [official docs](https://www.TypeScriptlang.org/docs/handbook/2/narrowing.html).

If you mark an variable holding an array as `readonly`, you can't reassign it. However, you can
`push()`, `pop()`, and mutate it! In the example below, `values` supports mutation!

```typescript
class ContainsArray {
  constructor(readonly values: string[]) {}
}

const object = new ContainsArray(["a", "b"])
object.values.push("d") // This is ok! 👎
```

So, in order to lock down that array, you can do the following. Note the subtle difference in the
keyword `readonly` showing up twice!

```typescript
class ContainsArray {
  constructor(readonly values: readonly string[]) {}
}

const object = new ContainsArray(["a", "b"])
object.values.push("d") // This is NOT ok! 👍
```

Another way to write the same thing is as follows.

```typescript
class ContainsArray {
  constructor(readonly values: ReadonlyArray<string>) {}
}

const object = new ContainsArray(["a", "b"])
object.values.push("d") // This is ok!
```

In the code for
[`ReactReplayClassComponent`](https://github.com/nazmulidris/ts-scratch/tree/main/react-app-hooks-intro/src/components/animate/ReactReplayClassComponent.tsx),
the following lines do the same thing (preventing any mutations on `elementArray`):

- `readonly elementArray: readonly JSX.Element[]`
- `readonly elementArray: ReadonlyArray<JSX.Element>`

## TypeScript prop and state types

In strict mode, the prop and state types (if any) need to be declared explicitly. The React codebase
supports generics which is how these types are declared.

> 💡 You can also pass `{}` to specify that there are no props or state.

Here is a [tutorial](https://fettblog.eu/TypeScript-react/components/#class-components) that shows
how to specify prop and state types for function and class components.

Here's an example for a class component which takes props but contains no state. Note that no
children can be passed.

```typescript
export interface AnimationFramesProps {
  animationFrames: Readonly<ReactElement>
}

export class ReactReplayClassComponent extends React.Component<AnimationFramesProps, {}> {
  /* snip */
}
```

If you wanted children to be passed, you could do something like this.

```typescript
export interface AnimationFramesPropsWithKids extends AnimationFramesProps {
  /** More info: https://linguinecode.com/post/pass-react-component-as-prop-with-TypeScript */
  children?: Readonly<ReactElement>
}

export class ReactReplayClassComponent extends React.Component<AnimationFramesPropsWithKids, {}> {
  /* snip */
}
```

You can also wrap your prop type, eg: `MyPropType`, w/ `PropsWithChildren<MyPropType>` when
declaring your function component to declare that your component can accept `children`. And then you
can use the destructuring syntax to get the required props out.

> 💡 TypeScript supports built-in and user defined
> [utility types](https://www.TypeScriptlang.org/docs/handbook/utility-types.html) and
> [advanced types](https://www.TypeScriptlang.org/docs/handbook/advanced-types.html#type-guards-and-differentiating-types)
> which are in leverage in `PropsWithChildren` type. It takes your prop type as an argument and
> returns a new type which includes everything in your type and `children?: ReactNode | undefined`.

Here's an example.

```typescript
export type TooltipOverlayProps = {
  text: string
}

export const TooltipOverlay: FC<PropsWithChildren<TooltipOverlayProps>> = ({ children, text }) => {
  /* snip */
}
```

> Note the use of the destructuring syntax to get the specific properties (`children`, `text`) out
> of the passed `props` object. The types are defined in `TooltipOverlayProps` (`text` comes from
> this) and `PropsWithChildren` (`children` comes from this).

Here's an example for a function component. Note the use of `FC` to specify that this is a function
component that takes a prop. Being a function component, you can't declare any state types.

```typescript
export const ReactReplayFunctionComponent: FC<AnimationFramesProps> = (props): ReactElement => {
  /* snip */
}
```

## TypeScript and ReactNode, ReactElement, JSX.Element

This [SO thread](https://stackoverflow.com/a/58123882/2085356) has the answers. Basically,

1. Use `ReactElement` where possible.
2. When TypeScript complains at times, use `ReactElement | null`.
3. Class components (return `ReactElement | null`) and function components (return `ReactElement`)
   actually return different things.

## TypeScript types in array and object destructuring

More info:

- [Array and object destructuring in ES6](https://basarat.gitbook.io/TypeScript/future-javascript/destructuring#array-destructuring)
- [Typing destructured objects in TypeScript](https://mariusschulz.com/blog/typing-destructured-object-parameters-in-TypeScript#typing-immediately-destructured-parameters)
- [Typing destructed arrays in TypeScript](https://www.carlrippon.com/strongly-typed-destructuring-and-rest-parameters/)

Example of object destructuring.

```typescript
type AnimationFrames = Readonly<Array<ReactElement>>
type MyProps = { animationFrames: AnimationFrames }
const { animationFrames }: MyProps = props
```

Example of array destructuring.

```typescript
type FrameIndexStateType = [number, Dispatch<SetStateAction<number>>]
const [frameIndex, setFrameIndex]: FrameIndexStateType = useState<number>(0)
```
