---
title: "Write code using async/await in Rust"
author: Nazmul Idris
date: 2022-03-12 13:00:00+00:00
excerpt: |
  This article illustrates how to write concurrent and parallel code in Rust using Tokio. The
  pedagogical example we will use is building an asynchronous implementation of a middleware runner
  that you might find in a Redux store.
layout: post
categories:
  - Rust
  - CLI
  - TUI
  - CC
---

<img class="post-hero-image" src="{{ 'assets/rust-tokio-3.svg' | relative_url }}"/>

<!-- TOC -->

- [Introduction](#introduction)
- [Concurrency and async/await, vs parallelism](#concurrency-and-asyncawait-vs-parallelism)
- [Async/await, Rust, and Tokio](#asyncawait-rust-and-tokio)
  - [Learn more about Tokio](#learn-more-about-tokio)
- [Implementing async middleware w/ function pointers](#implementing-async-middleware-w-function-pointers)
- [Implementing async middleware w/ async traits](#implementing-async-middleware-w-async-traits)
- [Writing tests](#writing-tests)
- [Advanced topic - locks and tokio](#advanced-topic---locks-and-tokio)
- [Async lambdas](#async-lambdas)
  - [Without macros](#without-macros)
  - [With macros](#with-macros)
- [Wrapping up](#wrapping-up)
- [Build with Naz video series on developerlife.com YouTube channel](#build-with-naz-video-series-on-developerlifecom-youtube-channel)

<!-- /TOC -->

## Introduction
<a id="markdown-introduction" name="introduction"></a>

This article illustrates how to write concurrent and parallel code in Rust using Tokio. The
pedagogical example we will use is building an asynchronous implementation of a middleware runner
that you might find in a Redux store.

This will get us ready to build a [Redux](https://redux.js.org/) library that will be the heart of
more complex TUI apps next using crates like `termion` and `tui`.

> 📜 The source code for the finished app named `tokio_example` can be found
> [here](https://github.com/nazmulidris/rust_scratch/tree/main/tokio).

> For more information on general Rust type system design (functional approach rather than
> object oriented), please take a look at this [paper](https://arxiv.org/pdf/2307.07069.pdf)
> by Will Crichton demonstrating Typed Design Patterns with Rust.

## Concurrency and async/await, vs parallelism
<a id="markdown-concurrency-and-async%2Fawait%2C-vs-parallelism" name="concurrency-and-async%2Fawait%2C-vs-parallelism"></a>

Concurrency is being able to break up your program or function into smaller tasks that can be
interleaved, possibly on the _same thread_. This approach lends itself well to speeding up _many_ IO
bound (where the CPU is mostly idling while waiting around for data to arrive) workloads or tasks

Parallelism is being able to break up your program or function so that it can be run on multiple
hardware threads at the same time. This approach is well suited to speeding up CPU bound workloads
or tasks.

| Concurrency                                            | Parallelism                                        |
| ------------------------------------------------------ | -------------------------------------------------- |
| Break up code into small tasks that can be interleaved | Break up code so it can be run on multiple threads |
| Can run on single thread                               | Run on multiple hardware threads                   |
| Good for IO bound workloads                            | Good for CPU bound workloads                       |

Concurrency means that multiple tasks can be executed in an interleaving fashion.

- Concurrency **does not mean** that these tasks are running in parallel.
- Concurrency lends itself well in improving throughput of IO bound tasks.
- It is possible to implement concurrency using a single thread (just like its done in JavaScript).

The key to making this work is having yield points in the code that makes up a function, and the
ability to resume execution of the function at a later time, resuming from a previously suspended
yield point.

1. In Rust, a yield point is declared in your function's code when you use the `.await` call. When
   you `await` a future inside of an `async` block, it will be able to schedule itself off the
   thread and make way for another task.
2. If a function (or lambda or code block) has a yield point, then it must be marked `async`. It
   might be useful to think of `async` as something that allows `await` inside a function or a
   block, but doesn’t actually make anything "async" (the yield points in your code makes it so).

Together, they tell the compiler (and Tokio) to generate the appropriate code to make this all work
for the code that you write.

For IO bound operations, when a task is waiting for some IO, it can yield, and then another task can
be run in the meantime. This prevents resources (threads, CPU, etc) from being tied up while the
task just idles waiting around for IO to appear. When there is data is available, then the yielded
task can be resumed, and can do some useful work w/ this data.

> ⚡ [Here are details](https://tokio.rs/tokio/tutorial/async) on how Rust implements the "waker"
> which is the thing that lets the yielded function know that the data is ready.

This is also how Node.js gets its incredible throughput in a single threaded runtime environment.
Using a single native thread to wait around for IO bound operations results in really poor
throughput since the
[number of native threads is severely hardware constrained in most modern operating systems](https://www.baeldung.com/linux/max-threads-per-process#factors-that-affect-maximum-thread-count).

- However, green threads can be used to mimic the behavior of native threads, while using this yield
  and resume mechanism under the hood.
- To give you some perspective, native threads may be in the order of 30K-60K per process on a
  modern machine, whereas you can have millions of green threads running per process.

> ☕ If you are familiar with Java, check out our
> [Project Loom](https://developerlife.com/2019/12/02/project-loom-experiment/) article which goes
> into this new JVM implementation of green threads and structured concurrency w/out using the
> `async` and `await` keywords, but its a similar kind of idea.

In contrast, parallelism means that multiple tasks can be run in parallel at the same time, usually
relying on multiple CPU cores that a machine has. This is different than concurrency in that there
are no yield points and interleaving of tasks. Instead each task is run in its own thread. This is
especially useful in tasks that are CPU bound (and not IO bound).

> 🔅 Here's a [great video on YouTube](https://www.youtube.com/watch?v=FNcXf-4CLH0), by JT, that
> explains the difference between concurrency and parallelism. And introduces `async`/`await` in
> Rust.

## Async/await, Rust, and Tokio
<a id="markdown-async%2Fawait%2C-rust%2C-and-tokio" name="async%2Fawait%2C-rust%2C-and-tokio"></a>

You don't need to use [Tokio](https://https://tokio.rs/) in order to use `async` and `await` in
Rust. However, Tokio is very powerful and makes very easy to do complex things with it.

- Tokio is an asynchronous runtime for Rust.
- It provides a nice abstraction layer over the native threading by providing a multi-threaded
  runtime for executing asynchronous code.

> 🔅 Here's an [excellent video](https://youtu.be/MZyleK8elPk) by the author of Tokio on what it is
> and how to use it.

> 🔅 Here's another [excellent video](https://www.youtube.com/watch?v=ThjvMReOXYM) by Jon Gjengset
> that goes into how to use `async` / `await` and Tokio.

You can configure the runtime to be single or multi-threaded (under the hood). If you use the
[`#[tokio::main]`](https://docs.rs/tokio/latest/tokio/attr.main.html#using-the-multi-thread-runtime)
macro then you are using the multi-threaded runtime, which uses a native thread pool that is
configured to use the number of cores on your machine's CPU and it has a task stealing algorithm to
provide high parallel performance. Here's the code that the macro expands to (it gives you an idea
of how the Tokio runtime works):

```rust
fn main() {
    tokio::runtime::Builder::new_multi_thread()
        .enable_all()
        .build()
        .unwrap()
        .block_on(async {
            println!("Hello world");
        })
}
```

### Learn more about Tokio
<a id="markdown-learn-more-about-tokio" name="learn-more-about-tokio"></a>

Basics:
- <https://tokio.rs/tokio/tutorial>
- It provides a great introduction for what use cases Tokio is good for and what use cases
  that it doesn't really work for.
- For example if you're reading a lot of files, then you can just use an ordinary thread
  pool in Rust instead of Tokio, since it doesn't really provide additional benefit over
  it.
- Another example is if your tasks involve running lots of CPU bound computations in
  parallel then you should consider using [`rayon`](https://docs.rs/rayon/latest/rayon/).
- However if you are doing a lot of IO bound tasks at the same time then Tokio rocks 🎉.

Deep dives:
1. You can get more info on this topic
    [here](https://users.rust-lang.org/t/socket-per-thread-in-tokio/83712/7).
2. For an even deeper dive into how Tokio tasks themselves are implemented for intra-task
   concurrency, please take a look at this [excellent
   article](https://without.boats/blog/let-futures-be-futures/).

## Implementing async middleware w/ function pointers
<a id="markdown-implementing-async-middleware-w%2F-function-pointers" name="implementing-async-middleware-w%2F-function-pointers"></a>

A Redux middleware is just a function. It takes an action as an argument, and may return nothing, or
it may return a new action. The middleware is where you are allowed to run side effects. So it is a
natural candidate for `async`/`await` and Tokio. We will implement a simple middleware runner
framework that allows middleware functions to be run asynchronously and produce either a new action
or nothing.

> 📦 For a real implementation of this middleware and Redux library, check out the
> [`r3bl_rs_utils`](https://crates.io/crates/r3bl_rs_utils/) crate. The README has excellent
> documentation on async traits, parallel and concurrent execution, and Tokio.
>
> 🌟 Please star the [`r3bl-open-core` repo](https://github.com/r3bl-org/r3bl-open-core) on github if
> you like it 🙏.

So, a middleware function is of type `SafeFn<A>`, where `A` is the action type. Here's what the
struct looks like.

```rust
use tokio::{sync::RwLock};

pub type SafeFn<A> = Arc<RwLock<dyn FnMut(A) -> Option<A> + Sync + Send>>;
//                   ^^^^^^^^^^                             ^^^^^^^^^^^
//                   Safe to pass      Declare`FnMut` has thread safety
//                   around.           requirement to rust compiler.

pub struct SafeFnWrapper<A> {
  fn_mut: SafeFn<A>,
}
```

Here's how we can read the `SafeFn` definition.

1. The middleware function signature is just `FnMut(A) -> Option<A>`.
2. However, we want to make this asynchronous and parallel, so we have to wrap it in a `RwLock`
   (which is a mutex), and then wrap that in an `Arc`. Now we can safely clone the `Arc` and pass it
   between thread boundaries. Please note that the `RwLock` is nor a "blocking" mutex or lock,
   rather it is an `async` one. More on this in [this section](#advanced-topic---locks-and-tokio).
3. Finally, we also have to mark the function w/ 2 other traits: `Sync` and `Send`. This is to be
   explicit and let the Rust compiler know that we intend for this lambda to be passed between
   thread boundaries, and that it should ensure that this is safe to do so! This is part of the
   awesomeness that is Rust and what allows us to use "fearless concurrency".

> 💡 To understand the lifetimes and traits that are used, here are some excellent resources on
> lifetimes, closures, and returning references:
>
> 1. <https://stackoverflow.com/questions/59442080/rust-pass-a-function-reference-to-threads>
> 2. <https://stackoverflow.com/questions/68547268/cannot-borrow-data-in-an-arc-as-mutable>
> 3. <https://willmurphyscode.net/2018/04/25/fixing-a-simple-lifetime-error-in-rust/>
> 4. <https://medium.com/@alistairisrael/demystifying-closures-futures-and-async-await-in-rust-part-3-async-await-9ed20eede7a4>

Please note that so far we don't have any mention of `async` or `await`. And we also have another
struct called `SafeFnWrapper<A>` that we haven't mentioned yet.

1. We actually don't work directly with `SafeFn` type, and instead we use the `SafeFnWrapper` struct
   which simply manages a `SafeFn` type. This allows us to manage the complexity of the
   `Arc<RwLock<dyn FnMut...>>` thread-safe lambda and be able to easily clone the `Arc` then unwrap
   and use it as needed.
2. This is a very useful pattern that we will be using more extensively when we
   [create the full Redux store](https://developerlife.com/2022/03/12/rust-redux/).

Here's the impl block of the `SafeFnWrapper` struct.

```rust
use tokio::{sync::RwLock, task::JoinHandle};

pub type Future<T> = JoinHandle<T>;

impl<A: Sync + Send + 'static> SafeFnWrapper<A> {
  pub fn new(
    fn_mut: impl FnMut(A) -> Option<A> + Send + Sync + 'static
  ) -> SafeFnWrapper<A> {
    SafeFnWrapper::set(Arc::new(RwLock::new(fn_mut)))
  }

  pub fn set(fn_mut: SafeFn<A>) -> Self {
    Self { fn_mut }
  }

  /// Get a clone of the `fn_mut` field (which holds a thread safe `FnMut`).
  pub fn get(&self) -> SafeFn<A> {
    self.fn_mut.clone()
  }

  /// This is an `async` function. Make sure to use `await` on the return value.
  pub fn spawn(
    &self,
    action: A,
  ) -> Future<Option<A>> {
    let arc_lock_fn_mut = self.get();
    tokio::spawn(async move {
      // Delay before calling the function.
      let delay_ms = rand::thread_rng().gen_range(100..1_000) as u64;
      tokio::time::sleep(tokio::time::Duration::from_millis(delay_ms)).await;
      let mut fn_mut = arc_lock_fn_mut.write().await; // 👀 `unwrap()` for blocking.
      fn_mut(action)
    })
  }
}
```

> ⚡ There are some subtleties to using a "blocking" lock / mutex instead of an async one. Read more
> about it in [this section](#advanced-topic---locks-and-tokio).

We have just used the `async` keyword, but not `await` yet. We have a `spawn()` function that
returns a `Future<Option<A>>` type. Its just a type alias for `tokio::task::JoinHandle`.

1. This is returned by a call to `tokio::spawn()` which **actually asynchronously runs the lambda**.
2. This allows the calling thread not to be blocked while the lambda is running 🎉.
3. Just to simulate a task w/ long and unknown delay, each spawn operation will wait between 1 and 5
   seconds before calling the lambda.

So we could `await` the results that come back from the `spawn()` function. This is just like
TypeScript promises. The `spawn()` function returns a promise, that the caller can `await` and
unwrap into a result. So we have set the caller up to be an `async` function that `await`s the
result of `spawn()`.

> 🤔 A Tokio task is an asynchronous green thread. They are created by passing an `async` block to
> `tokio::spawn`. The `tokio::spawn` function returns a `JoinHandle`, which the caller may use to
> interact with the spawned task. The `async` block may have a return value. The caller may obtain
> the return value using `.await` on the `JoinHandle`.
>
> Tasks are the unit of execution managed by the scheduler. Spawning the task submits it to the
> Tokio scheduler, which then ensures that the task executes when it has work to do. The spawned
> task may be executed on the same thread as where it was spawned, or it may execute on a different
> runtime thread. The task can also be moved between threads after being spawned.
>
> Tasks in Tokio are very lightweight. Under the hood, they require only a single allocation and 64
> bytes of memory. Applications should feel free to spawn thousands, if not millions of tasks. Read
> more about Tokio's `spawn()` function [here](https://tokio.rs/tokio/tutorial/spawning).

Please note the use of `'static` bound in the impl block (with `Sync + Send`). When you spawn a task
on the Tokio runtime, its type's lifetime must be `'static`. This means that the spawned task must
not contain any references to data owned outside the task.

> 🤔 It is a common misconception that `'static` always means "lives forever", but this is not the
> case. Just because a value is `'static` does not mean that you have a memory leak. You can read
> more in Common Rust Lifetime Misconceptions
> [here](https://github.com/pretzelhammer/rust-blog/blob/master/posts/common-rust-lifetime-misconceptions.md#2-if-t-static-then-t-must-be-valid-for-the-entire-program).
>
> 🐝 `Sync` + `Send` traits:
>
> - Tasks spawned by `tokio::spawn` must implement the `Send` marker trait. This allows the Tokio
>   runtime to move the tasks between threads while they are suspended at an `.await`.
> - Tasks are `Send` when all data that is held across `.await` calls is `Send`. This is a bit
>   subtle. When `.await` is called, the task yields back to the scheduler. The next time the task
>   is executed, it resumes from the point it last yielded.
> - To make this work, all state that is used after `.await` must be saved by the task. If this
>   state is `Send`, i.e. can be moved across threads, then the task itself can be moved across
>   threads. Conversely, if the state is not `Send`, then neither is the task.

Now that we have `SafeWrapperFn` struct, let's take a look at some middleware functions. Below, we
have two of them: `logger_mw()` and `adder_mw()`. And we have also defined the action enum called
`Action`.

```rust
use crate::middleware::SafeFnWrapper;

/// Does not capture context or return anything.
pub fn logger_mw() -> SafeFnWrapper<Action> {
  let logger_lambda = |action: Action| {
    println!("logging: {:?}", action);
    None
  };
  SafeFnWrapper::new(logger_lambda)
}

/// Captures context and returns a `Future<Action>`.
pub fn adder_mw() -> SafeFnWrapper<Action> {
  let mut stack: Vec<i32> = Vec::new();
  let adder_lambda = move |action: Action| match action {
    Action::Add(a, b) => {
      let sum = a + b;
      stack.push(a + b);
      Some(Action::Result(sum))
    }
    _ => None,
  };
  SafeFnWrapper::new(adder_lambda)
}

/// Action enum.
#[derive(Debug, PartialEq, Eq, Hash, Clone)]
pub enum Action {
  Add(i32, i32),
  Result(i32),
}
```

Finally, let's put it all together into the `main` function of our program.

```rust
// Imports.
use tokio_example_lib::{
  middleware::{Future, SafeFnWrapper},
  my_middleware::{adder_mw, logger_mw, Action},
};

#[tokio::main]
async fn main() {
  let mut handles = Vec::<Future<Option<Action>>>::new();

  // Spawn tasks and don't await their completion - fire and forget so to speak.
  {
    let mw_fun: SafeFnWrapper<Action> = logger_mw();
    handles.push(mw_fun.spawn(Action::Add(1, 2)));
    handles.push(mw_fun.spawn(Action::Add(1, 2)));
  }

  // Spawn tasks and await their completion.
  {
    let mw_fun: SafeFnWrapper<Action> = adder_mw();
    println!("{:?}", mw_fun.spawn(Action::Add(1, 2)).await.unwrap());
    println!("{:?}", mw_fun.spawn(Action::Add(1, 2)).await.unwrap());
  }

  // Needed to wait for all the spawned futures to complete, otherwise
  // the tokio runtime spawned in `main()` before the spawned futures complete.
  // More info: https://tokio.rs/tokio/topics/bridging
  for handle in handles {
    handle.await.unwrap();
  }
}
```

Here you can finally see the use of the `async` and `await` keywords. Both middleware functions can
be spawned and run concurrently by the Tokio runtime. You can see that there are multiple calls to
the `spawn()` method on both of the middleware function objects.

1. `spawn()` without `await`:
   - We don't really care what result the `logger_mw()` call produces. So we don't have to `.await`
     it. We can safely fire and forget it.
   - The two calls to `mw_fun.spawn()` run in parallel 🚀. The `main()` function doesn't wait for
     these functions to return anything. And `mw_fun.spawn()` is the first call that the `main()`
     function waits for it to complete.
   - However, in order to prevent the Tokio runtime from
     [exiting before the spawned tasks have been completed](https://tokio.rs/tokio/topics/bridging),
     we have to `await` the futures (in the for loop at the end).
2. `spawn()` with `await`:
   - We want to do something w/ result from the `adder_mw()` calls.
   - So we `.await` them, and the result is then unwrapped and printed to the console.
   - The `async` `main()` function waits after each `mw_fun.spawn()` call with the `.await` call
     then unwraps the result and prints it.

Here's the output that's produced by the program before it exits. Note that each function will show
up in the terminal w/ a different delay since each task can take between 100 and 1000 ms. However,
the program won't exit until all 4 tasks have been completed, regardless of how long they take 👏.

```shell
$ cargo run
logging: Add(1, 2)
logging: Add(1, 2)
Some(Result(3))
Some(Result(3))
```

## Implementing async middleware w/ async traits
<a id="markdown-implementing-async-middleware-w%2F-async-traits" name="implementing-async-middleware-w%2F-async-traits"></a>

You can use the `async-trait` crate in order to use the `async` keyword in your trait methods. This
is an alternative approach to using function pointers in the previous section.

Please read the [README](https://github.com/r3bl-org/r3bl-rs-utils/blob/main/README.md#redux) of the
[`r3bl_rs_utils` crate](https://crates.io/crates/r3bl_rs_utils/) for details on how to use them, for
both parallel and concurrent execution of `async` middleware. Instead of using function pointers,
the new implementation uses `async` trait objects (which are much easier to reason about and create,
and also can be made `async`).

> 📦 For a real implementation of this middleware and Redux library, check out the
> [`r3bl_rs_utils`](https://crates.io/crates/r3bl_rs_utils/) crate. The README has excellent
> documentation on async traits, parallel and concurrent execution, and Tokio.
>
> 🌟 Please star the [`r3bl-open-core` repo](https://github.com/r3bl-org/r3bl-open-core) on github if
> you like it 🙏.

## Writing tests
<a id="markdown-writing-tests" name="writing-tests"></a>

Tokio provides [testing support](https://docs.rs/tokio/latest/tokio/attr.test.html) for the code
that we've just written. Here's an integration test for the middleware functions that are shown
above.

```rust
use std::sync::{Arc, Mutex};

use tokio_example_lib::{
  middleware::SafeFnWrapper,
  my_middleware::{adder_mw, logger_mw, Action},
};

#[tokio::test]
async fn test_logger_mw_works() {
  let result = logger_mw().spawn(Action::Add(1, 2)).await.unwrap();
  assert!(result.is_none());
}

#[tokio::test]
async fn test_adder_mw_works() {
  let result = adder_mw().spawn(Action::Add(1, 2)).await.unwrap();
  assert_eq!(result, Some(Action::Result(3)));
}

#[tokio::test]
async fn test_complex_mw_example_works() {
  let stack = Arc::new(Mutex::new(vec![]));
  let stack_ref = stack.clone();
  let adder_lambda = move |action: Action| match action {
    Action::Add(a, b) => {
      let sum = a + b;
      let mut stack_ref = stack_ref.lock().unwrap();
      stack_ref.push(a + b);
      Some(Action::Result(sum))
    }
    _ => None,
  };
  let foo = SafeFnWrapper::new(adder_lambda);
  let result = foo.spawn(Action::Add(1, 2)).await.unwrap();
  assert_eq!(result, Some(Action::Result(3)));
  assert_eq!(stack.lock().unwrap().len(), 1);
}
```

## Advanced topic - locks and tokio
<a id="markdown-advanced-topic---locks-and-tokio" name="advanced-topic---locks-and-tokio"></a>

The standard library provides `RwLock` and `Mutex` types. These are meant to be used using "regular"
blocking code, rather than "async" code. You can spawn threads that work well with these locks.
However, if you mix and match these locks with `async` code, you'll get problems and the Rust
compiler will complain. Here's the kind of issue that you might face.

1. Locking the mutex will block the thread, which is generally something you want to avoid in
   `async` code as it can prevent other tasks from running.
2. The compiler error will warn you that the mutex guard that you get by locking can't be shared
   between threads safely, so it won't compile.

In order to fix it, you'll need to use the `tokio::sync::Mutex` or `tokio::sync::RwLock` type. And
you will have to:

1. Replace calls to (`lock().` or `write().` or `read().`) `unwrap()` with `.await`.
2. Make sure to use `.await` in an `async` block.

This version of the lock will yield control back to the task executor when it needs to wait rather
than blocking the thread, and will also allow it to be shared between threads if necessary.

> 🚀 Here's more information on this topic:
>
> 1. [Official tokio docs on `async` mutex](https://tokio.rs/tokio/tutorial/shared-state).
> 2. [SO thread](https://stackoverflow.com/a/67277503/2085356).
> 3. Please take a look at our
>    [Redux library implementation](https://developerlife.com/2022/03/12/rust-redux/) which makes
>    extensive use of this.

Here's an example using "regular" blocking code.

```rust
use std::sync::Arc;
use std::sync::RwLock; // 👀 Different for async lock.
use tokio::task::JoinHandle;

pub fn spawn(
  &self,
  action: A,
) -> Future<Option<A>> {
  let arc_lock_fn_mut = self.get();
  tokio::spawn(async move {
    // Delay before calling the function.
    let delay_ms = rand::thread_rng().gen_range(100..1_000) as u64;
    tokio::time::sleep(tokio::time::Duration::from_millis(delay_ms)).await;
    let mut fn_mut = arc_lock_fn_mut.write().unwrap(); // 👀 Different for `async` lock.
    fn_mut(action)
  })
}
```

Here's an example after switching to `async` locks.

```rust
use std::sync::Arc;
use tokio::sync::RwLock; // 👀 Different from blocking.
use tokio::task::JoinHandle;

pub fn spawn(
  &self,
  action: A,
) -> Future<Option<A>> {
  let arc_lock_fn_mut = self.get();
  tokio::spawn(async move {
    // Delay before calling the function.
    let delay_ms = rand::thread_rng().gen_range(100..1_000) as u64;
    tokio::time::sleep(tokio::time::Duration::from_millis(delay_ms)).await;
    let mut fn_mut = arc_lock_fn_mut.write().await;  // 👀 Different from blocking.
    fn_mut(action)
  })
}
```

## Async lambdas
<a id="markdown-async-lambdas" name="async-lambdas"></a>

> 🪄 Currently `async` lambdas are only supported in Rust nightly channel, after enabling the
> feature `async_closure`. Please see this
> [async RFC for more details](https://github.com/rust-lang/rfcs/blob/master/text/2394-async_await.md#async--closures).

### Without macros
<a id="markdown-without-macros" name="without-macros"></a>

The following snippet is an example of an `async` function that accepts a lambda, w/out enabling
`async_closure`. Note that the return type is of type `Fun` which is `Future<Output = R>`.
Essentially, this is a function that returns a `Future` just like a TypeScript promises. However, it
has severe limitations since the `receiver_fn` argument below can't be an `async` function.

For more information, see this [SO thread](https://stackoverflow.com/a/60723870/2085356).

```rust
use tokio::sync::RwLock;
use std::future::Future;
use std::sync::Arc;

pub async fn unwrap_arc_write_lock_and_call_async<Fn, T, Fut, R>(
  arc_lock_wrapped_value: &Arc<RwLock<T>>,
  receiver_fn: &mut Fn,
) -> Fut
where
  Fn: FnMut(&mut T) -> Fut,
  Fut: Future<Output = R>,
{
  let arc_copy = arc_lock_wrapped_value.clone();
  let mut write_guard: RwLockWriteGuard<T> = arc_copy.write().await;
  receiver_fn(&mut write_guard)
}
```

### With macros
<a id="markdown-with-macros" name="with-macros"></a>

The `SafeListManager` struct shown below simply wraps a `Vec` in an `async` `RwLock` in an `Arc` and
manages that reference, allowing for a safe way to add and remove items from the list. And passing
that list around between threads (green or otherwise).

```rust
use std::sync::Arc;
use tokio::sync::RwLock;

pub type SafeList<T> = Arc<RwLock<Vec<T>>>;

pub struct SafeListManager<T>
where
  T: Sync + Send + 'static,
{
  list: SafeList<T>,
}

impl<T> SafeListManager<T>
where
  T: Sync + Send + 'static,
{
  pub fn get(&self) -> SafeList<T> {
    self.list.clone()
  }

  pub async fn push(
    &mut self,
    item: T,
  ) {
    let arc = self.get();
    let mut locked_list = arc.write().await;
    locked_list.push(item);
  }

  pub async fn clear(&mut self) {
    let arc = self.get();
    let mut locked_list = arc.write().await;
    locked_list.clear();
  }
}
```

Here's a macro called `iterate_over_vec_with_async` that can iterate over the list and call a
function on each item. This function is passed as a lambda to this macro.

> 💡 For more information on creating macros, check out these resources:
>
> - <https://stackoverflow.com/questions/28953262/pass-member-function-body-as-macro-parameter>
> - <https://cheats.rs/#tooling-directives>
> - <https://dhghomon.github.io/easy_rust/Chapter_61.html>
> - <https://stackoverflow.com/questions/26731243/how-do-i-use-a-macro-across-module-files>

```rust
// Define macro.
macro_rules! iterate_over_vec_with_async {
  ($locked_list_arc:expr, $receiver_fn:expr) => {
    let locked_list = $locked_list_arc.get();
    let list = locked_list.read().await;
    for (_i, list_item) in list.iter().enumerate() {
      $receiver_fn(list_item.clone()).await;
    }
  };
}

pub(crate) use iterate_over_vec_with_async;
```

Here's some code that uses the macro.

```rust
// Use macro.
let state_clone = &self.get_state_clone();
iterate_over_vec_with_async!(
  self.subscriber_manager,
  |subscriber_fn: SafeSubscriberFnWrapper<S>| async move {
    subscriber_fn.spawn(state_clone.clone()).await.unwrap();
  }
);
```

Without the macro, this is what the code would look like.

```rust
let locked_list = self.subscriber_manager.get();
let list = locked_list.read().await;
for subscriber_fn in list.iter() {
  subscriber_fn.spawn(self.state.clone()).await.unwrap();
}
```

> ⚡ You can find this code in the full Redux library implementation
> [here](https://developerlife.com/2022/03/12/rust-redux/).

## Wrapping up
<a id="markdown-wrapping-up" name="wrapping-up"></a>

This is a simple introduction to Tokio. The tutorials and videos are a great resource for learning
Tokio, along w/ the tutorials that are provided on the [Tokio website](https://tokio.rs/).

We will take this and build upon it further to create a full Redux library in Rust using Tokio
[here](https://developerlife.com/2022/03/12/rust-redux/).

## Build with Naz video series on developerlife.com YouTube channel
<a id="markdown-build-with-naz-video-series-on-developerlife.com-youtube-channel" name="build-with-naz-video-series-on-developerlife.com-youtube-channel"></a>

> If you have comments and feedback on this content, or would like to request new content
> (articles & videos) on developerlife.com, please join our [discord
> server](https://discord.gg/8M2ePAevaMi).

You can watch a video series on building this crate with Naz on the
[developerlife.com YouTube channel](https://www.youtube.com/@developerlifecom).

- [YT channel](https://www.youtube.com/@developerlifecom)
- Playlists
    - [Build with Naz, Linux TTY, process, signals, commands in async Rust](https://www.youtube.com/watch?v=bolScvh4x7I&list=PLofhE49PEwmw3MKOU1Kn3xbP4FRQR4Mb3)
    - [Build with Naz, fundamental effective Rust](https://www.youtube.com/playlist?list=PLofhE49PEwmza94sS7UmJnN9gSCHTVTfz)
    - [Build with Naz, effective async Rust and tokio](https://www.youtube.com/playlist?list=PLofhE49PEwmwO69E7eiQ-ewnMME8ydgQ5)
    - [Build with Naz, async readline and spinner for CLI in Rust](https://www.youtube.com/watch?v=3vQJguti02I&list=PLofhE49PEwmwelPkhfiqdFQ9IXnmGdnSE)
    - [Build with Naz, testing in Rust](https://www.youtube.com/watch?v=Xt495QLrFFk&list=PLofhE49PEwmwLR_4Noa0dFOSPmSpIg_l8)
