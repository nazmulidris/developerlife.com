---
title: "Write a Redux library in Rust"
author: Nazmul Idris
date: 2022-03-12 15:00:00+00:00
excerpt: |
  This article illustrates how we can build a Redux library in Rust. This library is thread safe and
  asynchronous (using Tokio). The middleware and subscribers will be run in parallel. But the reducer
  functions will be run in sequence.
layout: post
categories:
  - Rust
  - CLI
  - TUI
  - CC
  - State
---

<img class="post-hero-image" src="{{ 'assets/rust-redux.svg' | relative_url }}"/>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [Architecture](#architecture)
- [Of "things" and their "managers"](#of-things-and-their-managers)
- [Using the Redux library](#using-the-redux-library)
- [The Store struct](#the-store-struct)
- [Reducer functions](#reducer-functions)
- [Middleware functions](#middleware-functions)
- [Subscriber functions](#subscriber-functions)
- [Wrapping up](#wrapping-up)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

This article illustrates how we can build a Redux library in Rust. This library is thread safe and
asynchronous (using Tokio). The middleware and subscribers will be run in asynchronously via Tokio
tasks. But the reducer functions will be run in sequence (not in separate Tokio tasks).

> 💡 Learn more about:
>
> - Redux [from the official docs](https://redux.js.org/). You can get familiar w/ the store,
>   reducer functions, `async` middleware, and subscribers. Along w/ the idea of finite state
>   machines as an effective way to manage your application's state.
> - Tokio [from our article](https://developerlife.com/2022/03/12/rust-tokio/). You can get familiar
>   with the `async` programming model and the Tokio runtime. And get some insights into writing
>   macros that help you write `async` code.

> 📜 The source code for the finished Redux library can be found
> [here](https://github.com/r3bl-org/r3bl-rs-utils).

> 📦 You can use this Redux library today by adding
> [`r3bl_rs_utils`](https://crates.io/crates/r3bl_rs_utils/) crate as a dependency in your
> `Cargo.toml`.
>
> 🌟 Please star the [`r3bl_rs_utils` repo](https://github.com/r3bl-org/r3bl_rs_utils) on github if
> you like it 🙏.

This article is getting us ready to building more complex TUI apps next using crates like `termion`
and `tui`.

> For more information on general Rust type system design (functional approach rather than
> object oriented), please take a look at this [paper](https://arxiv.org/pdf/2307.07069.pdf)
> by Will Crichton demonstrating Typed Design Patterns with Rust.

## Architecture

Before we start, let's get familiar with the Redux architecture.

1. The store is a central place to manage the state of your application. It is the only place where
   you can change the state of your application. In order to change the state, you need to dispatch
   an action. State is immutable. So you can't change it once it is created. The only way to change
   the state is to dispatch an action, which will generate a new and also immutable state. This is
   the key to Redux's unidirectional data flow.
2. An action describes your desired change and includes any data (in the form of arguments that will
   end up going to middleware or reducer functions).
3. Once an action has been dispatched to the store, the reducer functions are responsible for
   updating the state based on these incoming actions. Reducer functions must also be pure
   functions, ie, no side effects are allowed (can't generate unique ids, perform `async` function
   calls, use random number generators, or even use the current time). This is severely limiting,
   since these side effects are where most important things in an application's business logic
   actually happen. This is where middleware functions come in.
4. The middleware is a function that takes an action and returns a new action. This is where all
   kinds of `async` operations can be performed. Ultimately, each middleware function call
   asynchronously resolves into a new action. This action is then dispatched to the store (where the
   pure reducer function will use it to generate a new state).
5. The subscriber is a function that is called whenever the state of the store changes. This is
   where you would normally perform UI updates, but they don't have to be restricted to just UI. Any
   kind of data can be observed by the subscriber.

In our implementation of Redux, we will make the middleware and subscriber functions asynchronous.
And we will use the Tokio runtime that allows us to run them concurrently and in parallel. However,
we will run the reducer functions in sequence.

Here are some of our assumptions about the performance characteristics of these components.

1. A reducer function is pure and is really fast. It isn't allowed to do any `async` work, so its
   very limited in what it can do. It is best to run these in sequence.
2. A middleware function is `async` and can be really slow (doing computations or waiting around for
   IO). These are heavy functions and its good that we can run them asynchronously using Tokio.
3. A Subscriber function can be really slow as well, since it can render some really complex UI.
   However, since this is separate from state changes, we can run them asynchronously using Tokio.

> 💡 Please read
> [our article on Tokio](http://developerlife.com/2022/03/12/rust-tokio/#asyncawait-rust-and-tokio)
> to learn more about the terms: Tokio runtime, synchronous, asynchronous, concurrent, parallel.

To make things even more flexible, we will provide 2 ways of dispatching actions:

1. **A spawning dispatch function**. This frees the main thread from waiting around for the
   middleware, reducer, and subscriber functions to complete. Even the reducer functions will not
   block the calling thread. A new Tokio task is spawned inside of which the reducers are run, the
   `async` middleware and `async` subscribers are also run.
2. **A regular dispatch function**. This does not spawn a new Tokio task. Instead, it runs the
   reducer functions on the calling thread. However, the middleware and subscriber functions will be
   run asynchronously in other Tokio tasks. You can actually await the results of all of them to
   complete.

## Of "things" and their "managers"

This brings us into the implementation of the Redux library. The first thing we will need is a Redux
store that is shareable between threads / tasks and also allows thread safe interior mutability. We
will also need other structures that have these same requirements (wrapped functions / lambdas,
lists, etc).

> 💡 Please read
> [our article on shared ownership and interior mutability](https://developerlife.com/2022/02/24/rust-non-binary-tree/#naive-approach-using-weak-and-strong-references).

Before starting our implementation, let's take a close look at the following pattern we will heavily
lean on which to make this "shareability" happen, which is:

1. Wrap a "thing" that we want to be shareable inside of a `Mutex` or `RwLock`, and then wrap that
   inside of an `Arc`. The naming convention that we apply to this is prefixing the word `Safe`
   before the "thing" (e.g. `SafeThing`).
   - The "thing" in this case is `Vec<T>`.
   - And the `Safe` "thing" is `Arc<Mutex<Vec<T>>>` or `Arc<RwLock<Vec<T>>>`.
2. So far, we've just made some type aliases. Where is all this instantiated, what holds memory?
   Let's make a struct which has a single property (named `my_arc`) that holds the `Safe` "thing".
   We will call this struct a `Manager` of the `Safe` "thing", (e.g. `SafeThingManager`). In other
   words your code will work w/ the "manager" and not the "thing" directly.
   - The `Manager` of the `Safe` "thing" (or just "manager") is what your code will work with. And
     not directly with the `Safe` "thing".
   - The "manager" is the struct that occupies memory.
3. The "manager" will:
   - Provide a constructor method `new()` that allows you to instantiate it.
   - Allow shared ownership by providing a `get()` method that simply returns a clone of the
     underlying `Arc` which we call `my_arc`.

> 💡 This is a fantastic cheat sheet of pointers and ownership in Rust. Here's more info on
> `vtable`, `dyn Trait`, dynamically sized types:
>
> 1. [discussion](https://users.rust-lang.org/t/where-does-the-vtable-pointer-go-in-box-trait/17437/2)
> 2. [book - wide pointers](https://doc.rust-lang.org/nomicon/exotic-sizes.html#exotically-sized-types)
> 3. [book - trait objects](https://doc.rust-lang.org/book/ch17-02-trait-objects.html?highlight=dynamic%20dispatch#using-trait-objects-that-allow-for-values-of-different-types)
> 4. [book - trait object safety](https://doc.rust-lang.org/reference/items/traits.html#object-safety)
> 5. [article - super traits](https://alschwalm.com/blog/static/2017/03/07/exploring-dynamic-dispatch-in-rust/)
>
> <img src="{{'assets/rust-container-cheat-sheet.svg' | relative_url}}"/>

Here is an example 🎉.

```rust
use std::sync::Arc;
use tokio::sync::RwLock;

pub type Thing<T> = Vec<T>;

pub type SafeThing<T> = Arc<RwLock<Thing<T>>>;

pub struct SafeThingManager<T>
where
  T: Sync + Send + 'static,
{
  my_arc: SafeThing<T>,
}

impl<T> SafeThingManager<T>
where
  T: Sync + Send + 'static,
{
  pub fn new() -> SafeThing<T> {
    Self {
      my_arc: Arc::new(RwLock::new(Thing::new())),
    }
  }

  pub fn get(&self) -> SafeThing<T> {
    self.my_arc.clone()
  }
}
```

You might be asking yourself: <kbd> Ok, how do we access the "thing" inside the "manager"? 🤔 </kbd>

Excellent question 👍. The pattern we will use to do this is also repeated throughout the rest of
the library codebase. The logic goes something like this:

1. Call `get()` on the "manager".
   - This returns a cloned `Arc`.
2. Call `.lock()` or `read()` or `write()` on it (depending on whether you used `Mutex` or
   `RwLock`).
   - This returns a `MutexGuard`, `RwLockReadGuard` or `RwLockWriteGuard`). Which we then have to
     [`.await`](https://docs.rs/tokio/1.17.0/tokio/sync/struct.Mutex.html) (since these are
     [Tokio locks](https://tokio.rs/tokio/tutorial/shared-state)).
3. Finally we have access to the underlying "thing" that we can now use 🎉.

As you can see these steps can be tedious and repetitive. One way to handle this repetition is via
the use of macros. We can use `macro_rules!` to create some macros for this common pattern across
some of our structs. Here are two examples of such macros.

> 💡 Please take a look at our
> [Tokio article](http://localhost:4000/2022/03/12/rust-tokio/#with-macros) to learn more about
> macros and how they can be used w/ this "manager" and "thing" pattern.

```rust
/// The `$lambda` expression is not `async`.
macro_rules! iterate_over_vec_with {
  ($this:ident, $locked_list_arc:expr, $lambda:expr) => {
    let locked_list = $locked_list_arc.get();
    let list_r = locked_list.read().await;
    for item_fn in list_r.iter() {
      $lambda(&item_fn);
    }
  };
}

/// The `$lambda` expression is `async`.
macro_rules! iterate_over_vec_with_async {
  ($this:ident, $locked_list_arc:expr, $lambda:expr) => {
    let locked_list = $locked_list_arc.get();
    let list_r = locked_list.read().await;
    for item_fn in list_r.iter() {
      $lambda(&item_fn).await;
    }
  };
}

pub(crate) use iterate_over_vec_with;
pub(crate) use iterate_over_vec_with_async;
```

Here's a snippet of how this ends up being used in the Redux library. This snippet might not make
sense at this point, its just there to give you a sense of how this macro is used. We will get into
the details of all of this in the next sections.

```rust
pub async fn actually_dispatch_action<'a>(
  &mut self,
  action: &A,
) {
  // Run reducers.
  {
    iterate_over_vec_with!(
      self,
      self.reducer_manager,
      |reducer_fn: &'a ReducerFnWrapper<S, A>| {
        let new_state = reducer_fn.invoke(&self.state, &action);
        self.update_history(&new_state);
        self.state = new_state;
      }
    );
  }
}
```

With this, we can now dive into the Redux library implementation 🚀.

> 📦 There are ways to automate the generation of all this boilerplate in Rust using
> [procedural macros](https://developerlife.com/2022/03/30/rust-proc-macro/#eg-2---function-like-macro-that-parses-custom-syntax).
> To see a real world example of using code generation to express this pattern, please check out the
> [`manager_of_things.rs`](https://github.com/r3bl-org/r3bl-rs-utils/blob/main/my_proc_macros_lib/src/manager_of_things.rs)
> file in our [`r3bl_rs_utils` crate](https://crates.io/crates/r3bl_rs_utils). You can also look at
> the
> [tests](https://github.com/r3bl-org/r3bl-rs-utils/blob/main/tests/test_manager_of_things_macro.rs)
> to see how this macro is used.
>
> 🌟 Please star the [`r3bl_rs_utils` repo](https://github.com/r3bl-org/r3bl_rs_utils) on github if
> you like it 🙏.

## Using the Redux library

> 🚀 You can find a CLI app that uses this Redux library to manage an address book
> [here](https://github.com/nazmulidris/rust_scratch/tree/main/address-book-with-redux) called
> `address_book_with_redux`. Please clone that repo on github and run it using `cargo run` to play
> with this library and see what it can do. If you type `help` when the CLI starts up, it will give
> you a list of commands you can use. Try `add-async` and `add-sync` to see what happens.

The `Store` struct is the heart of the Redux library. It is the "thing" that we will use to manage
our shared application state. It allows for a few things:

1. `Store` creation.
2. Dispatching actions.
3. Getting the current state.
4. Accessing history of state changes.
5. Managing middleware.
6. Managing reducers.
7. Managing subscribers.

> ⚡ **Any functions or blocks that you write which uses the Redux library will have to be marked
> `async` as well. And you will have to spawn the Tokio runtime by using the `#[tokio::main]` macro.
> If you use the default runtime then Tokio will use multiple threads and its task stealing
> implementation to give you parallel and concurrent behavior. You can also use the single threaded
> runtime; its really up to you.**

> 📦 You can use this Redux library today by adding
> [`r3bl_rs_utils`](https://crates.io/crates/r3bl_rs_utils/) crate as a dependency in your
> `Cargo.toml`.
>
> 🌟 Please star the [`r3bl_rs_utils` repo](https://github.com/r3bl-org/r3bl_rs_utils) on github if
> you like it 🙏.

This is what the API looks like when we use it our app. Let's say we have the following action enum,
and state struct.

```rust
/// Action enum.
#[derive(Debug, PartialEq, Eq, Hash, Clone)]
pub enum Action {
  Add(i32, i32),
  AddPop(i32),
  Clear,
  MiddlewareCreateClearAction,
}

/// State.
#[derive(Clone, Default, PartialEq, Debug, Hash)]
pub struct State {
  pub stack: Vec<i32>,
}
```

Here's an example of the reducer function.

```rust
// Reducer function (pure).
let reducer_fn = |state: &State, action: &Action| match action {
  Action::Add(a, b) => {
    let sum = a + b;
    State { stack: vec![sum] }
  }
  Action::AddPop(a) => {
    let sum = a + state.stack[0];
    State { stack: vec![sum] }
  }
  Action::Clear => State { stack: vec![] },
  _ => state.clone(),
};
```

Here's an example of an `async` subscriber function (which are run in parallel after an action is
dispatched). The following example uses a lambda that captures a shared object. This is a pretty
common pattern that you might encounter when creating subscribers that share state in your enclosing
block or scope.

```rust
// This shared object is used to collect results from the subscriber function
// & test it later.
let shared_object = Arc::new(Mutex::new(Vec::<i32>::new()));
// This subscriber function is curried to capture a reference to the shared object.
let subscriber_fn = with(shared_object.clone(), |it| {
  let curried_fn = move |state: State| {
    let mut stack = it.lock().unwrap();
    stack.push(state.stack[0]);
  };
  curried_fn
});
```

Here are two types of `async` middleware functions. One that returns an action (which will get
dispatched once this middleware returns), and another that doesn't return anything (like a logger
middleware that just dumps the current action to the console). Note that both these functions share
the `shared_object` reference from above.

```rust
// This middleware function is curried to capture a reference to the shared object.
let mw_returns_none = with(shared_object.clone(), |it| {
  let curried_fn = move |action: Action| {
    let mut stack = it.lock().unwrap();
    match action {
      Action::Add(_, _) => stack.push(-1),
      Action::AddPop(_) => stack.push(-2),
      Action::Clear => stack.push(-3),
      _ => {}
    }
    None
  };
  curried_fn
});

// This middleware function is curried to capture a reference to the shared object.
let mw_returns_action = with(shared_object.clone(), |it| {
  let curried_fn = move |action: Action| {
    let mut stack = it.lock().unwrap();
    match action {
      Action::MiddlewareCreateClearAction => stack.push(-4),
      _ => {}
    }
    Some(Action::Clear)
  };
  curried_fn
});
```

Here's how you can setup a store with the above reducer, middleware, and subscriber functions.

```rust
// Setup store.
let mut store = Store::<State, Action>::new();
store
  .add_reducer(ReducerFnWrapper::new(reducer_fn))
  .await
  .add_subscriber(SafeSubscriberFnWrapper::new(subscriber_fn))
  .await
  .add_middleware(SafeMiddlewareFnWrapper::new(mw_returns_none))
  .await;
```

Finally here's an example of how to dispatch an action in a test. You can dispatch actions
asynchronously using `dispatch_spawn()` which is "fire and forget" meaning that the caller won't
block or wait for the `dispatch_spawn()` to return. Then you can dispatch actions synchronously if
that's what you would like using `dispatch()`.

```rust
// Test reducer and subscriber by dispatching Add and AddPop actions asynchronously.
store.dispatch_spawn(Action::Add(10, 10)).await;
store.dispatch(&Action::Add(1, 2)).await;
assert_eq!(shared_object.lock().unwrap().pop(), Some(3));
store.dispatch(&Action::AddPop(1)).await;
assert_eq!(shared_object.lock().unwrap().pop(), Some(21));
store.clear_subscribers().await;

// Test `async` middleware: mw_returns_action.
shared_object.lock().unwrap().clear();
store
  .add_middleware(SafeMiddlewareFnWrapper::new(mw_returns_action))
  .dispatch(&Action::MiddlewareCreateClearAction)
  .await;
assert_eq!(store.get_state().stack.len(), 0);
assert_eq!(shared_object.lock().unwrap().pop(), Some(-4));
```

## The Store struct

The `Store` is actually a "manager" for the "thing" which is `SafeStoreStateMachineWrapper`. The
"thing" that it manages actually has all the good stuff like the following:

1. The current state.
2. The history of states.
3. The subscriber manager (which itself is a "manager" for the "thing" that is a function).
4. The middleware manager (which itself is a "manager" for the "thing" that is a function).
5. The reducer manager (which itself is a "manager" for the "thing" that is a function).

Here's a code snippet that shows how to use the `Store` struct. In terms of "manager" and "thing"
here's the breakdown:

1. "manager": `Store` is a "manager" for the "thing" that is `SafeStoreStateMachineWrapper`.
2. "thing": `SafeStoreStateMachineWrapper` is a "thing" that holds the current state, the history of
   states, the subscriber manager, the middleware manager, and the reducer manager.

```rust
pub struct StoreStateMachine<S, A>
where
  S: Sync + Send + 'static,
  A: Sync + Send + 'static,
{
  pub state: S,
  pub history: Vec<S>,
  pub subscriber_manager: SubscriberManager<S>,
  pub middleware_manager: MiddlewareManager<A>,
  pub reducer_manager: ReducerManager<S, A>,
}
```

The `Store` itself has quite a few methods that allows to add/remove/dispatch/get/clear/etc. Here
are some of these methods.

1. `dispatch` and `dispatchSpawn` which allow us to dispatch action objects synchronously or
   asynchronously.
2. `add_subscriber` and `clear_subscribers` which allow us to add/remove subscriber functions.
3. `add_middleware` and `clear_middlewares` which allow us to add/remove middleware functions.
4. `add_reducer` which allows us to add a reducer function.

## Reducer functions

> With `0.7.12` of the library, the codebase has been refactored to make all the things `async`.
> Please read the [README](https://github.com/r3bl-org/r3bl-rs-utils/blob/main/README.md#redux) for
> details on these changes and how to build your own reducers. Instead of using function pointers,
> the new implementation uses `async` trait objects (which are much easier to reason about and
> create, and also can be made `async`).

These live in the `SafeStoreStateMachineWrapper` struct. The reducer functions are managed by a
`ReducerManager` which is just a type alias for `SafeListManager`. Here's the breakdown of this in
terms of "manager" and "thing".

1. "manager": `SafeListManager` which holds a list of functions.
2. "thing": a `ReducerFnWrapper` function wrapper that is safe to share (it's actually a "manager"
   for the actual function that is the "thing").

```rust
// Reducer manager.
pub type ReducerManager<S, A> = SafeListManager<ReducerFnWrapper<S, A>>;
```

> 💡 This `SafeListManager` is used all over the place. It is used to manage a vector of things,
> where the things could be other managers.

The reducer function itself (which is a "thing") is wrapped in a `ReducerFnWrapper` which is a
"manager". Here's the breakdown:

1. "manager": `ReducerFnWrapper` which manages a function.
2. "thing": `SafeFnSafeReducerFn` which wraps a function that takes an action and state and returns
   a new state.

The function wrapper itself is a "manager" for the "thing" that is a lambda that accepts an action
and returns a new state.

```rust
/// Reducer function.
pub type ReducerFn<S, A> = dyn Fn(&S, &A) -> S;
pub type SafeReducerFn<S, A> = Arc<Mutex<dyn Fn(&S, &A) -> S + Send + Sync + 'static>>;

#[derive(Clone)]
pub struct ReducerFnWrapper<S, A>
where
  S: Sync + Send + 'static,
  A: Sync + Send + 'static,
{
  fn_mut: SafeReducerFn<S, A>,
}
```

When an action is dispatched to the store, each reducer function is called one after another, and
the state is updated. These happen sequentially (not in separate Tokio tasks). Before the reducers
are run the middleware functions are run.

## Middleware functions

> With `0.7.12` of the library, the codebase has been refactored to make all the things `async`.
> Please read the [README](https://github.com/r3bl-org/r3bl-rs-utils/blob/main/README.md#redux) for
> details on these changes and how to build your own reducers. Instead of using function pointers,
> the new implementation uses `async` trait objects (which are much easier to reason about and
> create, and also can be made `async`).

These live in the `SafeStoreStateMachineWrapper` struct. The middleware functions are managed by a
`MiddlewareManager` which is just a type alias for `SafeListManager`. Here's the breakdown of this
in terms of "manager" and "thing".

1. "manager": `SafeListManager` which holds a list of functions.
2. "thing": a `SafeMiddlewareFnWrapper` function wrapper that is safe to share (it's actually a
   "manager" for the actual function that is the "thing").

The middleware function itself (which is a "thing") is wrapped in a `SafeMiddlewareFnWrapper` which
is a "manager". Here's the breakdown:

1. "manager": `SafeMiddlewareFnWrapper` which manages an `async` function.
2. "thing": `SafeMiddlewareFn` which wraps a function that takes an action and returns an option
   that can hold an action. This means that it can return `None` or `Some` containing an action.

```rust
use std::{
  marker::{Send, Sync},
  sync::Arc,
};
use tokio::{task::JoinHandle, sync::RwLock};

pub type SafeMiddlewareFn<A> = Arc<RwLock<dyn FnMut(A) -> Option<A> + Sync + Send>>;
//                             ^^^^^^^^^^                             ^^^^^^^^^^^
//                             Safe to pass      Declare`FnMut` has thread safety
//                             around.           requirement to rust compiler.

#[derive(Clone)]
pub struct SafeMiddlewareFnWrapper<A> {
  fn_mut: SafeMiddlewareFn<A>,
}
```

> 💡 Here are some excellent resources on lifetimes and returning references:
>
> 1. <https://stackoverflow.com/questions/59442080/rust-pass-a-function-reference-to-threads>
> 2. <https://stackoverflow.com/questions/68547268/cannot-borrow-data-in-an-arc-as-mutable>
> 3. <https://willmurphyscode.net/2018/04/25/fixing-a-simple-lifetime-error-in-rust/>

When an action is dispatched, each middleware is run in its own Tokio task. Then the store waits for
all of these to finish. If any actions have been created then these are queued up and passed to the
reducer functions (which actually generate new states). These reducers are run sequentially. When
the final state is ready, it is then passed to each subscriber function; each subscriber function is
run in a separate Tokio task).

## Subscriber functions

> With `0.7.12` of the library, the codebase has been refactored to make all the things `async`.
> Please read the [README](https://github.com/r3bl-org/r3bl-rs-utils/blob/main/README.md#redux) for
> details on these changes and how to build your own reducers. Instead of using function pointers,
> the new implementation uses `async` trait objects (which are much easier to reason about and
> create, and also can be made `async`).

These live in the `SafeStoreStateMachineWrapper` struct. The subscriber functions are managed by a
`SubscriberManager` which is just a type alias for `SafeListManager`. Here's the breakdown of this
in terms of "manager" and "thing".

1. "manager": `SafeListManager` which holds a list of functions.
2. "thing": a `SafeSubscriberFnWrapper` function wrapper that is safe to share (it's actually a
   "manager" for the actual function that is the "thing").

The middleware function itself (which is a "thing") is wrapped in a `SafeSubscriberFnWrapper` which
is a "manager". Here's the breakdown:

1. "manager": `SafeSubscriberFnWrapper` which manages an `async` function.
2. "thing": `SafeSubscriberFn` which wraps a function that takes a state and returns nothing.

```rust
use std::sync::Arc;
use tokio::{task::JoinHandle, sync::RwLock};

/// Subscriber function.
pub type SafeSubscriberFn<S> = Arc<RwLock<dyn FnMut(S) + Sync + Send>>;

#[derive(Clone)]
pub struct SafeSubscriberFnWrapper<S> {
  fn_mut: SafeSubscriberFn<S>,
}
```

The last stage of action dispatch is to call each subscriber function. These happen in their own
Tokio tasks.

## Wrapping up

> 🚀 You can find a CLI app that uses this Redux library to manage an address book
> [here](https://github.com/nazmulidris/rust_scratch/tree/main/address-book-with-redux) called
> `address_book_with_redux`. Please clone that repo on github and run it using `cargo run` to play
> with this library and see what it can do. If you type `help` when the CLI starts up, it will give
> you a list of commands you can use. Try `add-async` and `add-sync` to see what happens.

> 📜 The source code for the finished Redux library can be found
> [here](https://github.com/r3bl-org/r3bl-rs-utils). You can always find the most up to date
> information on this library in it's
> [`README`](https://github.com/r3bl-org/r3bl-rs-utils/blob/main/README.md#redux) file.

> 📦 You can use this Redux library today by adding
> [`r3bl_rs_utils`](https://crates.io/crates/r3bl_rs_utils/) crate as a dependency in your
> `Cargo.toml`.
>
> 🌟 Please star the [`r3bl_rs_utils` repo](https://github.com/r3bl-org/r3bl_rs_utils) on github if
> you like it 🙏.
