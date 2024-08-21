---
title: "Build with Naz : Rust async in practice tokio::select!, actor pattern & cancel safety"
author: Nazmul Idris
date: 2024-07-10 15:00:00+00:00
excerpt: |
    This tutorial, video, and repo are a deep dive into the concept of cancellation safety in
    async code using Tokio and Rust. It affects the `tokio::select!` macro, and what happens
    to the racing `Future`s that don't win. The examples provided here, along with the video,
    will go over both code that is is cancellation safe and code that is not. These examples
    reflect real-world patterns, and are a generalized form of them.
layout: post
categories:
  - Rust
  - CLI
  - Server
  - TUI
---

<img class="post-hero-image" src="{{ 'assets/tokio-async-cancel-safety.svg' | relative_url }}"/>

<!-- TOC -->

- [Introduction](#introduction)
- [What can go wrong when racing futures?](#what-can-go-wrong-when-racing-futures)
- [YouTube video for this article](#youtube-video-for-this-article)
- [Examples of cancellation safety in async Rust using tokio::select!](#examples-of-cancellation-safety-in-async-rust-using-tokioselect)
  - [Example 1: Right and wrong way to sleep, and interval](#example-1-right-and-wrong-way-to-sleep-and-interval)
    - [Difference between interval and sleep](#difference-between-interval-and-sleep)
  - [Example 2: Safe cancel of a future using interval and mpsc channel](#example-2-safe-cancel-of-a-future-using-interval-and-mpsc-channel)
  - [Example 3: Inducing cancellation safety issues](#example-3-inducing-cancellation-safety-issues)
- [Build with Naz video series on developerlife.com YouTube channel](#build-with-naz-video-series-on-developerlifecom-youtube-channel)

<!-- /TOC -->

## Introduction
<a id="markdown-introduction" name="introduction"></a>

This tutorial, video, and repo are a deep dive into the concept of cancellation safety in
async code using Tokio and Rust. It affects the `tokio::select!` macro, and what happens
to the racing `Future`s that don't win. The examples provided here, along with the video,
will go over both code that is is cancellation safe and code that is not. These examples
reflect real-world patterns, and are a generalized form of them.

`tokio::select!` might as well have been called `tokio::race!` (there's a [The Fast and
Furious : Tokyo
Drift](https://en.wikipedia.org/wiki/The_Fast_and_the_Furious:_Tokyo_Drift) joke in there
somewhere).

It races the given futures in the branches of the macro, and the first one to resolve wins
(it is `Ready` when `poll()`ed). The other futures are dropped. These futures are run
concurrently, not in parallel, on the same worker thread, since we are not using
`tokio::spawn!` or its variants.

Here's the basic setup:

```rust
loop {
    tokio::select!{
        branch_1_result = future_1 => {
            // handle branch_1_result
        },
        branch_2_result = future_2 => {
            // handle branch_2_result
        },
        // and so on
    }
}
```

A classic example is that you're reading something from an *async* network or file stream.
And you want to have a timeout that breaks out of the `loop` if it takes too long. In this
case you might have two branches:
1. A `tokio::time::sleep()` `Future` in the timeout branch.
2. Some code to get the data asynchronously from the stream in the other branch.

> Another example is that you might be waiting for the user to type something from the
> keyboard or mouse (such as a TUI app) and also listen for signals to shut down the app,
> or other signals to perform re-rendering of the TUI. You can see this [in `r3bl_tui`
> here](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/terminal_window/main_event_loop.rs#L94)
> and [in `r3bl_terminal_async`
> here](https://github.com/r3bl-org/r3bl-open-core/blob/main/terminal_async/src/readline_impl/readline.rs#L468).

Note that all branches must have a `Future` to call `.await` on. The macro does not
require you to call `.await`. The code it generates take care of this.

> It might be worth your time (if you haven't already) to read the [official Tokio
> docs](https://docs.rs/tokio/latest/tokio/macro.select.html#cancellation-safety) on
> `tokio::select!` macro and the concept of cancellation safety before diving into the
> examples below.

## What can go wrong when racing futures?
<a id="markdown-what-can-go-wrong-when-racing-futures%3F" name="what-can-go-wrong-when-racing-futures%3F"></a>

If you recall, in Rust, a `Future` is just a data structure that doesn't really do
anything until you `.await` it.
- The Tokio runtime actually does work on the `Future`s by polling them to see whether
  they are `Ready` or `Pending`.
- If they're not `Ready` they go back to waiting until their `Waker` is called, and then
  Tokio will `poll()` them again.
- They are cheap to create, they are stateful, and they can be nested (easily composed).

> Please read our article on [effective async
> Rust](https://developerlife.com/2024/05/19/effective-async-rust/) to get a better
> understanding of how async Rust, and `Future`s works and how runtimes are implemented.

These are some of the great things about Rust `Future`s. However, the nature of a Rust
`Future` is what may cause a problem with "cancellation safety" in the `tokio::select!`
macro.

So what happens to `future_2` (the branch reading or writing from an async stream) if the
timeout branch (for `future_1`) wins the race?
- Is the `future_2` in the middle of doing something when this happens?
- And if so, what happens to the work it was doing when it hits the `.await` point in its
  code, and then stops?

This is the crux of the issue with cancellation safety in async Rust code. Lots of `tokio`
code is built to be cancellation safe, so if you're using `mpsc` or `broadcast` channels,
async streams, etc. you will be fine. However if you're maintaining state inside the
`future_2` and then it is dropped, then this article will help you understand what
happens.

## YouTube video for this article
<a id="markdown-youtube-video-for-this-article" name="youtube-video-for-this-article"></a>

This blog post has examples from this live coding video. If you like
to learn via video, please watch the companion video on the [developerlife.com YouTube
channel](https://www.youtube.com/@developerlifecom).

<!-- video on tokio-async-cancel-safety -->
<iframe
    src="https://www.youtube.com/embed/cQq5i8J1ELg?si=UDgJdFFQn0-yNXsS"
    title="YouTube video player" frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    referrerpolicy="strict-origin-when-cross-origin"
    allowfullscreen
    >
</iframe>

<br/>

## Examples of cancellation safety in async Rust using tokio::select!
<a id="markdown-examples-of-cancellation-safety-in-async-rust-using-tokio%3A%3Aselect!" name="examples-of-cancellation-safety-in-async-rust-using-tokio%3A%3Aselect!"></a>

Let's create some examples to illustrate how to use the typestate pattern in Rust. You can run
`cargo new --lib async_cancel_safe` to create a new library crate.

> 💡 You can get the code from the
> [`rust-scratch`](https://github.com/nazmulidris/rust-scratch/tree/main/async_cancel_safe) repo.

Then add the following to the `Cargo.toml` file that's generated. These pull in all the
dependencies that we need for these examples.

```toml
[package]
name = "async_cancel_safe"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio = { version = "1.38.0", features = ["full"] }

# Async stream testing.
r3bl_test_fixtures = { version = "0.0.2" }
futures-util = "0.3.30"
```

We are going to add all the examples below as tests to the `lib.rs` file in this crate.

### Example 1: Right and wrong way to sleep, and interval
<a id="markdown-example-1%3A-right-and-wrong-way-to-sleep%2C-and-interval" name="example-1%3A-right-and-wrong-way-to-sleep%2C-and-interval"></a>

Add the following code to your `lib.rs` file. Both these examples show similar ways of using
`tokio::time::sleep(..)` incorrectly in a `tokio::select!` block.

```rust
/// Equivalent to [test_sleep_right_and_wrong_ways_v2]. This test uses
/// [`tokio::pin`] and [`tokio::time::sleep`].
/// Run the test using:
/// `cargo test -- --nocapture test_sleep_right_and_wrong_ways_v1`
#[tokio::test]
async fn test_sleep_right_and_wrong_ways_v1() {
    let mut count = 5;

    let sleep_time = 100;
    let duration = std::time::Duration::from_millis(sleep_time);

    let sleep = tokio::time::sleep(duration);
    tokio::pin!(sleep);

    loop {
        tokio::select! {
            // Branch 1 (right way)
            // This branch executes a deterministic number of times. The same
            // sleep future is re-used on each iteration.
            _ = &mut sleep => {
                println!("branch 1 - tick : {count}");
                count -= 1;
                if count == 0 {
                    break;
                }
            }

            // Branch 2 (wrong way)
            // This branch is executed a non deterministic number of times.
            // This is because the sleep future is not pinned. It is dropped
            // when the other branch is executed. Then on the next iteration,
            // a new sleep future is created.
            _ = tokio::time::sleep(duration) => {
                println!("branch 2 - sleep");
            }
        }
    }
}

/// Equivalent to [test_sleep_right_and_wrong_ways_v1]. This test uses
/// [`tokio::time::interval()`]
/// Run the test using:
/// `cargo test -- --nocapture test_sleep_right_and_wrong_ways_v2`
#[tokio::test]
async fn test_sleep_right_and_wrong_ways_v2() {
    let mut count = 5;

    let sleep_time = 100;
    let duration = std::time::Duration::from_millis(sleep_time);

    let mut interval = tokio::time::interval(duration);

    loop {
        tokio::select! {
            // Branch 1 (right way)
            // This branch executes a deterministic number of times. The same
            // sleep future is re-used on each iteration.
            _ = interval.tick() => {
                println!("branch 1 - tick : {count}");
                count -= 1;
                if count == 0 {
                    break;
                }
            }

            // Branch 2 (wrong way)
            // This branch is executed a non deterministic number of times.
            // This is because the sleep future is not pinned. It is dropped
            // when the other branch is executed. Then on the next iteration,
            // a new sleep future is created.
            _ = tokio::time::sleep(duration) => {
                println!("branch 2 - sleep");
            }
        }
    }
}
```

You can run these tests to see what they do by running the following in your terminal:
- `cargo test -- --nocapture test_sleep_right_and_wrong_ways_v1`
- `cargo test -- --nocapture test_sleep_right_and_wrong_ways_v2`

They are flaky and its not possible to really make accurate assertions at the end of
each of these tests.

Let's break down `v1` first to see what is happening.

- Branch 1 (right way): This branch executes a deterministic number of times. The same
  sleep future is re-used on each iteration. This is achieved using the `tokio::pin!`
  macro. Since futures are stateful, ensuring that the same one is re-used between
  iterations of the `loop` ensures that state isn't lost when the other branch is
  executed, or when this branch finishes and its future is dropped.
- Branch 2 (wrong way): This branch is executed a non deterministic number of times. This
  is because the sleep future is not pinned. It is dropped when the other branch is
  executed. Then on the next iteration, a **new** sleep future is created. This means that
  the state of the future is lost, and its behavior with providing a reliable delay is
  non deterministic.

Let's break down `v2` next.

- Branch 1 (right way): This branch executes a deterministic number of times. However, we
  are using `tokio::time::interval()` this time around. It is re-used between many
  iterations of the `loop`. This function returns a `Interval` struct that has a `tick()`
  method that returns a `Future` that resolves when the interval has elapsed.
- Branch 2 (wrong way): Same as before.

#### Difference between interval and sleep
<a id="markdown-difference-between-interval-and-sleep" name="difference-between-interval-and-sleep"></a>

This is the mental model that I've developed for using these.

1. If your intention is to have a single timeout then, `sleep` might be the way to go. You
   create and `tokio::pin!` the `sleep` future, and then re-use it in the `loop`. Once
   this timeout expires, then you can handle your timeout condition in that branch.
2. If your intention is to have a re-usable timer that ticks on a regular interval, then
   `interval` is the way to go. You create the `interval` outside the `loop`, and then
   call `tick()` on it in the `loop`. This will give you a `Future` that resolves when the
   interval has elapsed. And you can safely use this same `Interval` repeatedly in the
   loop. And even accumulate how many times it runs to decide when to break.

### Example 2: Safe cancel of a future using interval and mpsc channel
<a id="markdown-example-2%3A-safe-cancel-of-a-future-using-interval-and-mpsc-channel" name="example-2%3A-safe-cancel-of-a-future-using-interval-and-mpsc-channel"></a>

Add the following snippet to your `lib.rs` file.

```rust
/// Run the test using:
/// `cargo test -- --nocapture test_safe_cancel_example`
#[tokio::test]
async fn test_safe_cancel_example() {
    let sleep_time = 100;
    let duration = std::time::Duration::from_millis(sleep_time);

    let mut count = 5;
    let mut interval = tokio::time::interval(duration);

    // Shutdown channel.
    let (tx, mut rx) = tokio::sync::mpsc::channel(1);
    let mut vec: Vec<usize> = vec![];

    loop {
        tokio::select! {
            // Branch 1.
            _ = interval.tick() => {
                println!("branch 1 - tick : count {}", count);

                vec.push(count);
                count = count.saturating_sub(1);

                if count == 0 {
                    _ = tx.try_send(());
                }
            }
            // Branch 2.
            _ = rx.recv() => {
                println!("branch 2 => shut down");
                break;
            }
        }
    }

    assert_eq!(vec, vec![5, 4, 3, 2, 1]);
}
```

When you run this test using `cargo test -- --nocapture test_safe_cancel_example`, you should
get this output in your terminal:

```
running 1 test
branch 1 - tick : count 5
branch 1 - tick : count 4
branch 1 - tick : count 3
branch 1 - tick : count 2
branch 1 - tick : count 1
branch 2 => shut down
```

Let's break down what's happening in this test.

- `Branch 1` - The `interval` is created outside the `loop` and is used to create a
  `Future` that resolves when the interval has elapsed. This happens in `Branch 1` and we
  let this branch run `5` times before sending a message on the `tx` channel.
- `Branch 2` - The `tx` channel is used to send a message to the `rx` channel. This is
  done in `Branch 1` when `count` reaches `0`. The `rx` channel is used to receive a
  message. This is done in `Branch 2` and when a message is received, we break out of the
  `loop`.

`Branch 1` runs 5 times, and `Branch 1` runs 1 time and breaks out of the loop. If you
look at the `vec` that we accumulate outside of the `loop` this contains what we expect.

### Example 3: Inducing cancellation safety issues
<a id="markdown-example-3%3A-inducing-cancellation-safety-issues" name="example-3%3A-inducing-cancellation-safety-issues"></a>

This is the example we have all been waiting for. Let's start with copying the
following snippet in your `lib.rs` file. We will create a new module here.

```rust
#[cfg(test)]
pub mod test_unsafe_cancel_example {
    use r3bl_test_fixtures::{gen_input_stream_with_delay, PinnedInputStream};

    pub fn get_input_vec() -> Vec<usize> {
        vec![1, 2, 3, 4]
    }

    pub fn get_stream_delay() -> std::time::Duration {
        std::time::Duration::from_millis(100)
    }

    fn get_input_stream() -> PinnedInputStream<usize> {
        gen_input_stream_with_delay(get_input_vec(), get_stream_delay())
    }

    /// This is just to see how to use the async stream [gen_input_stream()].
    #[tokio::test]
    async fn test_generate_event_stream_pinned() {
        use futures_util::StreamExt;

        let mut count = 0;
        let mut stream = get_stream();

        while let Some(item) = stream.next().await {
            let lhs = item;
            let rhs = get_input_vec()[count];
            assert_eq!(lhs, rhs);
            count += 1;
        }
    }
    // <more stuff to add later>
}
```

Let's break down what's happening here.
- `get_input_vec()` - This function returns a `Vec<usize>` that we will use to generate
  events in the `gen_input_stream()` function. This is meant to simulate the stream of
  `usize` values that may be generated from reading a file or a network source. Or even
  write to a file or network source. We could have just made these `u8`, but this is a
  made up test, so we are using `usize`.
- `gen_input_stream()` - This is where things get interesting. This function creates an
  async stream that yields the values from the `Vec<usize>` returned by `get_input_vec()`.
  It waits for `100ms` between each value that it yields. This is to simulate the delay
  that might be present when reading from a file or network source. Note the trait magic
  and imports that are used to make this work; to get the details on this, check our
  article on [trait pointers and
  testing](https://developerlife.com/2024/04/28/rust-polymorphism-dyn-impl-trait-objects-for-testing-and-extensibiity/).
- These two functions are our test fixture to simulate a slow async stream. Now, let's
  test the test fixtures in `test_generate_event_stream_pinned()`. This test simply reads
  from the async stream and compares the values that it reads with the values that are
  expected from the `Vec<usize>` returned by `get_input_vec()`.

> You can get the `r3bl_test_fixtures` [source
> here](https://github.com/r3bl-org/r3bl-open-core/tree/main/test_fixtures). You can get
> the crate from [crates.io](https://crates.io/crates/r3bl_test_fixtures).

In `lib.rs` replace the `// <more stuff to add later>` with the following code:

```rust
/// There is no need to [futures_util::FutureExt::fuse()] the items in each
/// [tokio::select!] branch. This is because Tokio's event loop is designed to handle
/// this efficiently by remembering the state of each future across iterations.
///
/// More info: <https://gemini.google.com/app/e55fd62339b674fb>
#[rustfmt::skip]
async fn read_3_items_not_cancel_safe(stream: &mut PinnedInputStream<usize>)
    -> Vec<usize>
{
    use futures_util::StreamExt;
    let mut vec = vec![];

    println!("branch 2 => entering read_3_items_not_cancel_safe");

    for _ in 0..3 {
        let item = stream.next() /* .fuse() */ .await.unwrap();
        println!("branch 2 => read_3_items_not_cancel_safe got item: {item}");
        vec.push(item);
        println!("branch 2 => vec so far contains: {vec:?}");
    }

    vec
}

/// There is no need to [futures_util::FutureExt::fuse()] the items in each
/// [tokio::select!] branch. This is because Tokio's event loop is designed to handle
/// this efficiently by remembering the state of each future across iterations.
///
/// More info: <https://gemini.google.com/app/e55fd62339b674fb>
#[tokio::test]
async fn test_unsafe_cancel_stream() {
    use futures_util::StreamExt;

    let mut stream = get_input_stream();
    let sleep_time = 300;
    let duration = std::time::Duration::from_millis(sleep_time);
    let sleep = tokio::time::sleep(duration);
    tokio::pin!(sleep);

    loop {
        tokio::select! {
            // Branch 1 - Timeout.
            _ = &mut sleep => {
                println!("branch 1 - time is up - end");
                break;
            }
            // Branch 2 - Read from stream.
            it = read_3_items_not_cancel_safe(&mut stream) /* .fuse() */ => {
                println!("branch 2 - got 3 items: {it:?}");
            }
        }
    }

    println!("loop exited");

    // Only [1, 2] is consumed by Branch 2 before the timeout happens
    // in Branch 1.
    let it = stream.next().await.unwrap();
    assert_eq!(it, 3);
}
```

When you run this test using `cargo test -- --nocapture test_unsafe_cancel_stream`, you
can expect the following output in your terminal.

```
branch 2 => entering read_3_items_not_cancel_safe
yielding item: 1
branch 2 => read_3_items_not_cancel_safe got item: 1
branch 2 => vec so far contains: [1]
yielding item: 2
branch 2 => read_3_items_not_cancel_safe got item: 2
branch 2 => vec so far contains: [1, 2]
branch 1 - time is up - end
loop exited
yielding item: 3
```

So let's break down what's happening in this test.

- `Branch 1` - This branch is a timeout branch. It waits for `300ms` before breaking out
  of the loop. This is to simulate a timeout that might happen when reading from a file or
  network source. With this delay, we ensure that `Branch 2` doesn't get to read all the
  values from the async stream. And thus we induce a cancellation safety issue, due the
  way `read_3_items_not_cancel_safe()` is implemented.
- `Branch 2` - This branch needs to reads `3` items from the async stream before
  resolving. This is done in a loop that reads `3` items in
  `read_3_items_not_cancel_safe()`. This is not safe because if the timeout branch wins
  the race, then the stream is dropped and the `read_3_items_not_cancel_safe()` future is
  dropped, along with the contained `vec`! This means that the stream is dropped before
  all the items are read from it. This is the cancellation safety issue that we are
  inducing in this test.

There are many ways to resolve this. The key is not to hold state inside of a `Future`
that you don't want to lose if the `Future` is dropped. You can use `mpsc` channels or a
pinned `Vec` to get around this issue.

> Note that in the case of a graceful shutdown, where you might not care about what data
> in some buffer is dropped, then this is not a problem.

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
