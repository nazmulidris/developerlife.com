---
title:
  "Build with Naz : Rust async, non-blocking, concurrent, parallel, event loops, graceful shutdown"
author: Nazmul Idris
date: 2024-05-19 15:00:00+00:00
excerpt: |
    In this article, video, and repo learn effective async Rust using real world patterns that
    show up consistently when creating non blocking, async, event loops, using channels. Delve
    into implementing the Future trait and async executor manually. Also explore graceful
    shutdown, when not to use async, and how to think about testing async code.
layout: post
categories:
  - Rust
  - CLI
  - Server
---

<img class="post-hero-image" src="{{ 'assets/rust_async_event_loops.svg' | relative_url }}"/>

<!-- TOC -->

- [Introduction](#introduction)
- [What is async Rust? Sequential vs concurrent code & parallelism as a resource](#what-is-async-rust-sequential-vs-concurrent-code--parallelism-as-a-resource)
- [What async Rust is not](#what-async-rust-is-not)
- [YouTube video for this article](#youtube-video-for-this-article)
- [Effective async Rust patterns by example](#effective-async-rust-patterns-by-example)
  - [Example 1: Build a timer future using Waker](#example-1-build-a-timer-future-using-waker)
  - [Example 2: Build an async runtime to run futures to completion](#example-2-build-an-async-runtime-to-run-futures-to-completion)
  - [Example 3: Running async code, concurrently, on a single thread](#example-3-running-async-code-concurrently-on-a-single-thread)
  - [Example 4: join!, select, spawn control flow constructors](#example-4-join-select-spawn-control-flow-constructors)
  - [Example 5: async streams](#example-5-async-streams)
  - [Example 6: Non-blocking event loops, channel safety, and graceful shutdown](#example-6-non-blocking-event-loops-channel-safety-and-graceful-shutdown)
  - [Parting thoughts](#parting-thoughts)
- [Build with Naz video series on developerlife.com YouTube channel](#build-with-naz-video-series-on-developerlifecom-youtube-channel)

<!-- /TOC -->

## Introduction
<a id="markdown-introduction" name="introduction"></a>

In this article, video, and repo learn effective async Rust using real world patterns that
show up consistently when creating non blocking, async, event loops, using channels. Delve
into implementing the Future trait and async executor manually. Also explore graceful
shutdown, when not to use async, and how to think about testing async code.

## What is async Rust? Sequential vs concurrent code & parallelism as a resource
<a id="markdown-what-is-async-rust%3F-sequential-vs-concurrent-code-%26-parallelism-as-a-resource" name="what-is-async-rust%3F-sequential-vs-concurrent-code-%26-parallelism-as-a-resource"></a>

In Rust, you can write sequential code, and concurrent code:
- Sequential code can be run sequentially, or in parallel (using `thread::spawn()`).
- Concurrent code can be run on a single thread or multiple threads.

Concurrency is a way to structure code into separate tasks. This does not define the
resources on a machine that will be used to run or execute tasks.

Parallelism is a way to specify what resources (CPU cores, or threads) will be used on a
machine's operating system to run tasks.

These 2 concepts are not the same. They are related but not the same.

## What async Rust is not
<a id="markdown-what-async-rust-is-not" name="what-async-rust-is-not"></a>

Generally speaking, using async Rust is not just a matter of attaching `async` as a prefix
to a function, when you define it, and postfix `.await` when you call it. In fact, if you
don't have at least one `.await` in your async function body, then it [might not need to
be async](https://ryhl.io/blog/async-what-is-blocking/). This article and video are a deep
dive into what async code is, what Rust `Future`s are, along with what async Runtimes are.
Along with some common patterns and anti-patterns when thinking in async Rust.

## YouTube video for this article
<a id="markdown-youtube-video-for-this-article" name="youtube-video-for-this-article"></a>

This blog post only has short examples on how to use Rust async effectively. To see how
these ideas can be used in production code, with real-world examples, please watch the
following video on the [developerlife.com YouTube
channel](https://www.youtube.com/@developerlifecom).

<!-- rust tokio tracing and otel for async rust & playlist -->
<iframe
    src="https://www.youtube.com/embed/qvIt8MF-pCM?si=S40pbhnvVDAohj-6"
    title="YouTube video player"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    referrerpolicy="strict-origin-when-cross-origin"
    allowfullscreen>
</iframe>

<br/>

## Effective async Rust patterns by example
<a id="markdown-effective-async-rust-patterns-by-example" name="effective-async-rust-patterns-by-example"></a>

Let's create some examples to illustrate how to use async Rust effectively. You can run
`cargo new --lib effective-async-rust` to create a new library crate.

> The code in the video and this tutorial are all in this GitHub repo:
> <https://github.com/nazmulidris/rust-scratch/blob/main/async_con_par/>

Then add the following to the `Cargo.toml` file that's generated. These pull in all the
dependencies that we need for these examples.

```toml
[package]
name = "effective-async-rust"
version = "0.1.0"
edition = "2021"

[dependencies]
crossterm = { version = "0.27.0", features = ["event-stream"] }
tokio = { version = "1.37.0", features = ["full", "tracing"] }
tracing = "0.1.40"
tracing-subscriber = "0.3.18"
futures = "0.3.30"
async-stream = "0.3.5"
```

### Example 1: Build a timer future using Waker
<a id="markdown-example-1%3A-build-a-timer-future-using-waker" name="example-1%3A-build-a-timer-future-using-waker"></a>

Then you can add the following code to the `src/lib.rs` file.

```rust
#[cfg(test)]
pub mod build_a_timer_future_using_waker;
```

We will implement the `Future` trait manually, in this example. Typically any `async` code
block is converted into a finite state machine which implements the `Future` trait.
Progress on the future only occurs when it is polled by the runtime or executor (eg:
Tokio).

- When a future is polled and it is `Ready` then the future is complete.
- If it is `Pending` then the future is not complete. And when it is ready (at some point
  in the future, due to some event like network IO available via `epoll` or `io_uring`),
  the runtime expects the future to wake up the, by calling `wake()` on the `Waker` that
  is passed to this future by the runtime, via the `Context` object.

Here are more details on this:

1. [Primer on async and await](https://rust-lang.github.io/async-book/01_getting_started/04_async_await_primer.html).
2. [`Future` trait](https://doc.rust-lang.org/std/future/trait.Future.html).
3. [Timer example](https://rust-lang.github.io/async-book/02_execution/03_wakeups.html).

> The code for this example is
> [here](https://github.com/nazmulidris/rust-scratch/blob/main/async_con_par/src/build_a_timer_future_using_waker.rs).

Create a new file `src/build_a_timer_future_using_waker.rs`. In this file, we are going
to:
- Build a timer that wakes up a task after a certain amount of time, to explore how
  `Waker` works.
- We'll just spin up a new thread when the timer is created, sleep for the required time,
  and then signal the timer future when the time window has elapsed.

Add the following code to the file, to define a new struct that will implement the
`Future` trait. This struct will have a `SharedState` struct that will contain the state
of the future, and an optional `Waker` that will be used to wake up the future when the
timer has elapsed. This `Waker` is not available until the very first time the future is
polled by the runtime.

```rust
#[derive(Default)]
pub struct TimerFuture {
    pub shared_state: Arc<Mutex<SharedState>>,
}

#[derive(Default)]
pub struct SharedState {
    pub completed: bool,
    pub waker: Option<Waker>,
}
```

Add the following code to implement the `Future` trait for the `TimerFuture` struct.
- This code will be used to poll the future, by the runtime, and check if the timer has
  elapsed.
- If it has, then the future is complete, and the runtime can move on to the next task. If
  the timer has not elapsed, then the future is not complete, and the runtime won't do
  anything further with this future. And will go on to the next task (top level `Future`)
  that it can make progress on.

Something has to wake up this future to let the runtime know that the timer has elapsed,
and that it needs to call `poll()` again on this `Future`. This is where the `Waker` comes
in.
- The first time `poll()` is called on this future, the runtime passes in a `Waker` and we
  save that to the `SharedState` struct.
- This will be used by the timer thread to wake up the future, when the timer has elapsed
  (which we will do next).

```rust
impl Future for TimerFuture {
    type Output = ();

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        let mut shared_state = self.shared_state.lock().unwrap();
        match shared_state.completed {
            true => {
                eprintln!("{}", "TimerFuture is completed".to_string().green());
                Poll::Ready(())
            }
            false => {
                eprintln!("{}", "TimerFuture is not completed".to_string().red());
                // Importantly, we have to update the Waker every time the
                // future is polled because the future may have moved to
                // a different task with a different Waker. This will happen
                // when futures are passed around between tasks after being
                // polled.
                shared_state.waker = Some(cx.waker().clone());
                Poll::Pending
            }
        }
    }
}
```

Add the following code to create a new timer `Future`, and start a new thread that will
sleep for the required time, and then wake up the `Future` when the timer has elapsed, by
using the optional `Waker` that was saved in the `SharedState` struct (when `poll()` is
called on the `Future`, by the runtime).

```rust
impl TimerFuture {
    pub fn new(duration: Duration) -> Self {
        let new_instance = TimerFuture::default();

        let shared_state_clone = new_instance.shared_state.clone();
        thread::spawn(move || {
            thread::sleep(duration);
            let mut shared_state = shared_state_clone.lock().unwrap();
            shared_state.completed = true;
            shared_state.waker.take().unwrap().wake();
        });

        new_instance
    }
}
```

Add the following test to run this code. The `#[tokio::test]` attribute macro generates
code to start a single threaded executor to run the test code.

```rust
#[tokio::test]
async fn run_timer_future_with_tokio() {
    let timer_future = TimerFuture::new(Duration::from_millis(10));
    let shared_state = timer_future.shared_state.clone();
    assert!(!shared_state.lock().unwrap().completed);
    timer_future.await;
    assert!(shared_state.lock().unwrap().completed);
}
```

When you run this test, it should produce the following output:

<pre class="pre-manual-highlight">
running 1 test
<span style="color:#BF616A">TimerFuture is not completed</span>
<span style="color:#A3BE8C">TimerFuture is completed</span>
test build_a_timer_future_using_waker::run_timer_future_with_tokio ... ok
</pre>

### Example 2: Build an async runtime to run futures to completion
<a id="markdown-example-2%3A-build-an-async-runtime-to-run-futures-to-completion" name="example-2%3A-build-an-async-runtime-to-run-futures-to-completion"></a>

For this example, let's add the following code to the `src/lib.rs` file.

```rust
#[cfg(test)]
pub mod build_an_executor_to_run_future;
```

In the example above, we use `tokio` to run the `TimerFuture` to completion. But in this
example, we will implement our own *simple* async runtime.

- This is a very simple runtime that will run futures to completion, by polling them until
  they are ready.
- It should highlight how the `Waker` and `Context` are supplied by the runtime to the
  `Future`.

> You can get the source code for this example
> [here](https://github.com/nazmulidris/rust-scratch/blob/main/async_con_par/src/build_an_executor_to_run_future.rs).

We will need a few things to implement this runtime:
1. `Task` struct that will contain the `Future` that needs to be run to completion.
2. `Task` queue that will contain all the tasks that need to be run. This will be a
   `std::sync::mpsc::sync_channel`.
3. `Waker` that will be used to wake up the runtime when a task is ready to be polled.
   `Context` that will be used to pass the `Waker` to the `Future` that is being polled.
5. `Spawner` struct that will be used to spawn new tasks into the runtime.
6. `Executor` struct that will be used to run the runtime.

Add the following code to the `src/build_an_executor_to_run_future.rs` file.

```rust
pub fn new_executor_and_spawner() -> (Executor, Spawner) {
    const MAX_TASKS: usize = 10_000;
    let (task_sender, task_receiver) = std::sync::mpsc::sync_channel(MAX_TASKS);
    (Executor { task_receiver }, Spawner { task_sender })
}

pub struct Executor {
    pub task_receiver: Receiver<Arc<Task>>,
}

pub struct Spawner {
    pub task_sender: SyncSender<Arc<Task>>,
}

pub struct Task {
    pub future: Mutex<Option<BoxFuture<'static, ()>>>,
    pub task_sender: SyncSender<Arc<Task>>,
}
```

Add the following code to the `Spawner` struct to spawn new tasks into the runtime.

```rust
impl Spawner {
    pub fn spawn(&self, future: impl Future<Output = ()> + 'static + Send) {
        let pinned_boxed_future = future.boxed();
        let task = Arc::new(Task {
            future: Mutex::new(Some(pinned_boxed_future)),
            task_sender: self.task_sender.clone(),
        });
        eprintln!(
            "{}",
            "sending task to executor, adding to channel"
                .to_string()
                .blue()
        );
        self.task_sender
            .send(task)
            .expect("too many tasks in channel");
    }
}
```

Add the following code to the `Executor` struct to run the runtime. This code will poll
the task queue, and block until it can get a task to run. Once it has a task, which it has
removed from the task channel or queue, it polls it (with the `Context` and `Waker`) to
check whether it is ready.

- If it is ready, then it is done.
- If it is not ready, then it does not do anything further with it. When the task is ready
  to be polled (eg: when the duration has passed in the `TimerFuture`'s thread), it will
  use the `Waker` to wake up the task when it is ready to be polled). The `ArcWake`
  implementation for the `Task` struct is used for this; all it does is send the task back
  to the task channel, so that it can be polled again by the executor 🎉.
- Here's what a real world implementation of `ArcWake` might look like using something
  like Linux `epoll` or `io_uring`:
  <https://rust-lang.github.io/async-book/02_execution/05_io.html>.

```rust
impl ArcWake for Task {
    /// Implement `wake` by sending this task back onto the task
    /// channel so that it will be polled again by the executor,
    /// since it is now ready.
    fn wake_by_ref(arc_self: &Arc<Self>) {
        let cloned = arc_self.clone();
        arc_self
            .task_sender
            .send(cloned)
            .expect("too many tasks in channel");
        eprintln!(
            "{}",
            "task woken up, added back to channel"
                .to_string()
                .underlined()
                .green()
                .bold()
        );
    }
}

impl Executor {
    #[allow(clippy::while_let_loop)]
    pub fn run(&self) {
        // Remove task from receiver, or block if nothing available.
        loop {
            eprintln!("{}", "executor loop".to_string().red());
            // Remove the task from the receiver.
            // If it is pending, then the ArcWaker
            // will add it back to the channel.
            match self.task_receiver.recv() {
                Ok(arc_task) => {
                    eprintln!(
                        "{}",
                        "running task - start, got task from receiver"
                            .to_string()
                            .red()
                    );
                    let mut future_in_task = arc_task.future.lock().unwrap();
                    match future_in_task.take() {
                        Some(mut future) => {
                            let waker = waker_ref(&arc_task);
                            let context = &mut Context::from_waker(&waker);
                            let poll_result = future.as_mut().poll(context);
                            eprintln!(
                                "{}",
                                format!(
                                  "poll_result: {:?}", poll_result)
                                  .to_string().red()
                            );
                            if poll_result.is_pending() {
                                // We're not done processing the future, so put it
                                // back in its task to be run again in the future.
                                *future_in_task = Some(future);
                                eprintln!("{}",
                                  "putting task back in slot"
                                  .to_string().red()
                                );
                            } else {
                                eprintln!("{}", "task is done".to_string().red());
                            }
                        }
                        None => {
                            panic!("this never runs");
                        }
                    }
                    eprintln!("{}", "running task - end".to_string().red());
                }
                Err(_) => {
                    eprintln!("no more tasks to run, breaking out of loop");
                    break;
                }
            }
        }
    }
}
```

And finally, add this test to run this code. Notice this code does not use `tokio` to run
the `TimerFuture` to completion. Instead, it uses the `Executor` and `Spawner` structs
that we implemented above.

```rust
#[test]
fn run_executor_and_spawner() {
    use super::build_a_timer_future_using_waker::TimerFuture;

    let results = Arc::new(std::sync::Mutex::new(Vec::new()));

    let (executor, spawner) = new_executor_and_spawner();

    let results_clone = results.clone();
    spawner.spawn(async move {
        results_clone.lock().unwrap().push("hello, start timer!");
        TimerFuture::new(std::time::Duration::from_millis(10)).await;
        results_clone.lock().unwrap().push("bye, timer finished!");
    });

    drop(spawner);

    executor.run();

    assert_eq!(
        *results.lock().unwrap(),
        vec!["hello, start timer!", "bye, timer finished!"]
    );
}
```

This should produce the following output, which maps to the flow that we described above:

<pre class="pre-manual-highlight">running 1 test
<span style="color:#81A1C1">sending task to executor, adding to channel</span>
<span style="color:#BF616A">executor loop</span>
<span style="color:#BF616A">running task - start, got task from receiver</span>
<span style="color:#BF616A">TimerFuture is not completed</span>
<span style="color:#BF616A">poll_result: Pending</span>
<span style="color:#BF616A">putting task back in slot</span>
<span style="color:#BF616A">running task - end</span>
<span style="color:#BF616A">executor loop</span>
<span style="color:#A3BE8C"><u style="text-decoration-style:single"><b>task woken up, added back to channel</b></u></span>
<span style="color:#BF616A">running task - start, got task from receiver</span>
<span style="color:#A3BE8C">TimerFuture is completed</span>
<span style="color:#BF616A">poll_result: Ready(())</span>
<span style="color:#BF616A">task is done</span>
<span style="color:#BF616A">running task - end</span>
<span style="color:#BF616A">executor loop</span>
no more tasks to run, breaking out of loop
test build_an_executor_to_run_future::run_executor_and_spawner ... ok
</pre>

### Example 3: Running async code, concurrently, on a single thread
<a id="markdown-example-3%3A-running-async-code%2C-concurrently%2C-on-a-single-thread" name="example-3%3A-running-async-code%2C-concurrently%2C-on-a-single-thread"></a>

For this example, let's add the following code to the `src/lib.rs` file.

```rust
#[cfg(test)]
pub mod local_set;
```

If you have async code, you can use a `LocalSet` to run the async code, in different
tasks, on a *single* thread. This ensures that any data that you have to pass between
these tasks can be `!Send`. Instead of wrapping the shared data in a `Arc` or
`Arc<Mutex>`, you can just wrap it in an `Rc`.

In this example, we will explore how to run async code concurrently, on a single thread.
This is an important concept to understand, as it is the basis for how async code can be
run concurrently, using non-blocking event loops.

> The code for this example is
> [here](https://github.com/nazmulidris/rust-scratch/blob/main/async_con_par/src/local_set.rs#L39).

Add the following code to the `src/local_set.rs` file.
- It shows how you can create a `Future` that uses a `Rc` to share data concurrently,
  running on a single thread.
- This is why the data is `!Send`, and we don't need to use an `Arc` or `Arc<Mutex>` to
  share it between tasks.
- Once the `LocalSet` is created, and `local_spawn()` is called, the task doesn't actually
  run until `local_set.run_until(..)` is called, or `local_set.await` is called.

```rust
#[tokio::test]
async fn run_local_set_and_spawn_local() {
    // Can't send this data across threads (not wrapped in `Arc` or `Arc<Mutex>`).
    let non_send_data = Rc::new("!SEND DATA");
    let local_set = LocalSet::new();

    // Spawn a local task (bound to same thread) that uses the non-send data.
    let non_send_data_clone = non_send_data.clone();

    let async_block_1 = async move {
        println!(
            // https://doc.rust-lang.org/std/fmt/index.html#fillalignment
            "{:<7} {}",
            "start",
            non_send_data_clone.as_ref().yellow().bold(),
        );
    };
    // Does not run anything.
    let join_handle_1 = local_set.spawn_local(async_block_1);

    // This is required to run `async_block_1`.
    let _it = local_set.run_until(join_handle_1).await;
```

Add the following code to the `src/local_set.rs` file. This is just a different variant
(from the first example) of creating a new async block, and running it using the
`LocalSet`.

```rust
    // Create a 2nd async block.
    let non_send_data_clone = non_send_data.clone();
    let async_block_2 = async move {
        sleep(std::time::Duration::from_millis(100)).await;
        println!(
            // https://doc.rust-lang.org/std/fmt/index.html#fillalignment
            "{:<7} {}",
            "middle",
            non_send_data_clone.as_ref().green().bold()
        );
    };

    // This is required to run `async_block_2`.
    let _it = local_set.run_until(async_block_2).await;
```

Finally add the following code to the `src/local_set.rs` file. This yet another way of how
you can create a new async block, and run it using the `LocalSet`. This one uses `local_set.await`
which runs all the futures that are associated with the `local_set`.

```rust
    // Spawn another local task (bound to same thread) that uses
    // the non-send data.
    let non_send_data_clone = non_send_data.clone();
    let async_block_3 = async move {
        sleep(std::time::Duration::from_millis(100)).await;
        println!(
            // https://doc.rust-lang.org/std/fmt/index.html#fillalignment
            "{:<7} {}",
            "end",
            non_send_data_clone.as_ref().cyan().bold()
        );
    };
    // Does not run anything.
    let _join_handle_3 = local_set.spawn_local(async_block_3);

    // `async_block_3` won't run until this is called.
    local_set.await;
}
```

Here's the output when you run this test:

<pre class="pre-manual-highlight">running 1 test
start   <span style = "color: #EBCB8B"><b>!SEND DATA</b></span>
middle  <span style = "color: #A3BE8C"><b>!SEND DATA</b></span>
end     <span style = "color: #8FBCBB"><b>!SEND DATA</b></span>
test local_set::run_local_set_and_spawn_local ... ok
</pre>


### Example 4: join!, select, spawn control flow constructors
<a id="markdown-example-4%3A-join!%2C-select%2C-spawn-control-flow-constructors" name="example-4%3A-join!%2C-select%2C-spawn-control-flow-constructors"></a>

For this example, let's add the following code to the `src/lib.rs` file.

```rust
#[cfg(test)]
pub mod demo_join_select_spawn;
```

You can use `join!`, `select!`, and `spawn` to control the flow of async code. These are
macros that are provided by the `tokio` crate. They are used to run multiple futures
concurrent, in parallel, and wait for them to complete.

> The code for this example is
> [here](https://github.com/nazmulidris/rust-scratch/blob/main/async_con_par/src/demo_join_select_spawn.rs).

Add the following code to the `src/demo_join_select_spawn.rs` file. This code shows how
you can use `join!` to run multiple futures concurrently, and wait for them to complete.

```rust
pub async fn task_1(time: u64) {
    sleep(Duration::from_millis(time)).await;
    println!("task_1");
}

pub async fn task_2(time: u64) {
    sleep(Duration::from_millis(time)).await;
    println!("task_2");
}

pub async fn task_3(time: u64) {
    sleep(Duration::from_millis(time)).await;
    println!("task_3");
}

#[tokio::test]
async fn test_join() {
    tokio::join!(task_1(100), task_2(200), task_3(300));
    println!("all tasks done");
}
```

Here's the output when you run this test:
<pre class="pre-manual-highlight">running 1 test
task_1
task_2
task_3
all tasks done
test demo_join_select_spawn::test_join ... ok
</pre>

Add the following code to the `src/demo_join_select_spawn.rs` file. This code shows how
you can use `select!` to run multiple futures concurrently, and wait for the first one to
complete.

```rust
#[tokio::test]
async fn test_select() {
    tokio::select! {
        _ = task_1(100) => println!("task_1 done"),
        _ = task_2(200) => println!("task_2 done"),
        _ = task_3(300) => println!("task_3 done"),
    }
    println!("one task done");
}
```

Here's the output when you run this test:
<pre class="pre-manual-highlight">running 1 test
task_1 done
one task done
test demo_join_select_spawn::test_select ... ok
</pre>


Add the following code to the `src/demo_join_select_spawn.rs` file. This code shows how
you can use `spawn` to run multiple futures in parallel, and wait for them to complete. We
pass the following to the `#[tokio::test]` attribute macro: `flavor = "multi_thread",
worker_threads = 5` which tells it to run the test on multiple threads (max of 5).

```rust
#[tokio::test(flavor = "multi_thread", worker_threads = 5)]
async fn test_spawn() {
    let handle_1 = tokio::spawn(task_1(100));
    let handle_2 = tokio::spawn(task_2(100));
    let handle_3 = tokio::spawn(task_3(100));

    handle_1.await.unwrap();
    handle_2.await.unwrap();
    handle_3.await.unwrap();
    println!("all tasks done");
}
```

When you run this test, it should produce the following output (the ordering of the tasks
which run first, second, and third, will vary):

<pre class="pre-manual-highlight">running 1 test
task_3
task_1
task_2
all tasks done
test demo_join_select_spawn::test_spawn ... ok
</pre>

### Example 5: async streams
<a id="markdown-example-5%3A-async-streams" name="example-5%3A-async-streams"></a>

For this example, let's add the following code to the `src/lib.rs` file.

```rust
#[cfg(test)]
pub mod async_stream;
```

You can use async streams to create a stream of values that are produced asynchronously.
This is useful for testing, for example in the `r3bl_terminal_async` crate [in
`readline.rs` in `test_streams`
module](https://github.com/r3bl-org/r3bl-open-core/blob/main/terminal_async/src/readline_impl/readline.rs#L796).

> The code for this example is
> [here](https://github.com/nazmulidris/rust-scratch/blob/main/async_con_par/src/async_stream.rs).

Add the following code to the `src/async_stream.rs` file.
- This code shows how you can use `async_stream` crate's `stream!` macro to create a
  stream of values that are generated from a vector of strings.
- This stream is then converted into a `PinnedInputStream` which is a `Pin<Box<dyn
  Stream<Item = Result<String, String>>>`.

```rust
pub type PinnedInputStream = Pin<Box<dyn Stream<Item = Result<String, String>>>>;

pub fn gen_input_stream() -> PinnedInputStream {
    let it = async_stream::stream! {
        for event in get_input_vec() {
            yield Ok(event);
        }
    };
    Box::pin(it)
}

pub fn get_input_vec() -> Vec<String> {
    vec![
        "a".to_string(),
        "b".to_string(),
        "c".to_string(),
        "d".to_string(),
    ]
}

#[tokio::test]
async fn test_stream() {
    let mut count = 0;
    let mut it = gen_input_stream();
    while let Some(event) = it.next().await {
        let lhs = event.unwrap();
        let rhs = get_input_vec()[count].clone();
        assert_eq!(lhs, rhs);
        count += 1;
    }
}
```

### Example 6: Non-blocking event loops, channel safety, and graceful shutdown
<a id="markdown-example-6%3A-non-blocking-event-loops%2C-channel-safety%2C-and-graceful-shutdown" name="example-6%3A-non-blocking-event-loops%2C-channel-safety%2C-and-graceful-shutdown"></a>

Let's add the following code to the `src/lib.rs` file.

```rust
#[cfg(test)]
pub mod non_blocking_async_event_loops;
```

You can use non-blocking event loops to create a loop that runs async code, and waits for
events to occur. This is useful for creating servers, clients, and other networked
applications. You can even use the same pattern to create
[CLI](https://crates.io/crates/r3bl_terminal_async) and
[TUI](https://crates.io/crates/r3bl_tui) applications that are non-blocking, and can
handle multiple events concurrently, such as when you're creating an interactive async
REPL.

> The source code for this example is
> [here](https://github.com/nazmulidris/rust-scratch/blob/main/async_con_par/src/non_blocking_async_event_loops.rs).

Add the following code to the `src/non_blocking_async_event_loops.rs` file.

```rust
#[tokio::test(flavor = "multi_thread", worker_threads = 5)]
async fn test_main_loop() {
    // Register tracing subscriber.
    tracing_subscriber::fmt()
        .without_time()
        .compact()
        .with_target(false)
        .with_line_number(false)
        .with_thread_ids(true)
        .with_thread_names(true)
        .init();

    // Create channels for events and shutdown signals.
    let event_channel = tokio::sync::mpsc::channel::<String>(1_000);
    let (event_sender, mut event_receiver) = event_channel;

    let shutdown_channel = tokio::sync::broadcast::channel::<()>(1_000);
    let (shutdown_sender, _) = shutdown_channel;

    // Spawn the main event loop.
    let mut shutdown_receiver = shutdown_sender.subscribe();
    let safe_count: std::sync::Arc<std::sync::Mutex<usize>> = Default::default();
    let safe_count_clone = safe_count.clone();
    let join_handle = tokio::spawn(async move {
        loop {
            tokio::select! {
                event = event_receiver.recv() => {
                    tracing::info!(?event, "task got event: event");
                    let mut count = safe_count_clone.lock().unwrap();
                    *count += 1;
                }
                _ = shutdown_receiver.recv() => {
                    tracing::info!("task got shutdown signal");
                    break;
                }
            }
        }
    });

    // Send events, in parallel.
    let mut handles = vec![];
    for i in 0..10 {
        let event_sender_clone = event_sender.clone();
        let join_handle = tokio::spawn(async move {
            tracing::info!(i, "sending event");
            let event = format!("event {}", i);
            let _ = event_sender_clone.send(event).await;
            tokio::time::sleep(std::time::Duration::from_millis(10)).await;
        });
        handles.push(join_handle);
    }

    // Wait for all events to be sent using tokio.
    futures::future::join_all(handles).await;

    // Shutdown the event loops.
    shutdown_sender.send(()).unwrap();

    // Wait for the event loop to shutdown.
    join_handle.await.unwrap();

    // Assertions.
    assert_eq!(shutdown_sender.receiver_count(), 1);
    assert_eq!(*safe_count.lock().unwrap(), 10);
}
```

Here are key points to note about this code:
- We use `tokio::sync::mpsc::channel` to create a channel for events, and
  `tokio::sync::broadcast::channel` to create a channel for shutdown signals.
- We spawn the main event loop, which listens for events and shutdown signals, and updates
  a shared counter.
- We spawn multiple tasks that send events to the event channel, in parallel.
  - The `#[tokio::test(flavor = "multi_thread", worker_threads = 5)]` attribute macro
    tells `tokio` to run the test on multiple threads (max of 5).
  - You can see this in the output when you run the test. By configuring Tokio `tracing`
    subscriber, we can see the thread IDs and names in the output
    (`.with_thread_ids(true)`, `.with_thread_names(true)`).
  - We wait for all events to be sent using `futures::future::join_all(handles).await`.
- We shutdown the event loop (using `shutdown_sender.send(())`), and wait for it to
  shutdown using `join_handle.await`..

When you run this test, it will produce the following output:
<pre class="pre-manual-highlight">running 1 test
<span style = "color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(05) sending event <i>i</i><span style = "color:#90949B">=2</span>
<span style = "color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(04) sending event <i>i</i><span style = "color:#90949B">=6</span>
<span style = "color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(06) sending event <i>i</i><span style = "color:#90949B">=0</span>
<span style = "color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(07) sending event <i>i</i><span style = "color:#90949B">=4</span>
<span style = "color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(03) sending event <i>i</i><span style = "color:#90949B">=7</span>
<span style = "color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(04) sending event <i>i</i><span style = "color:#90949B">=8</span>
<span style = "color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(06) sending event <i>i</i><span style = "color:#90949B">=1</span>
<span style = "color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(05) task got event: event <i>event</i><span style = "color:#90949B">=Some(&quot;event 2&quot;)</span>
<span style = "color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(07) sending event <i>i</i><span style = "color:#90949B">=5</span>
<span style = "color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(03) sending event <i>i</i><span style = "color:#90949B">=9</span>
<span style = "color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(05) task got event: event <i>event</i><span style = "color:#90949B">=Some(&quot;event 6&quot;)</span>
<span style = "color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(04) sending event <i>i</i><span style = "color:#90949B">=3</span>
<span style = "color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(05) task got event: event <i>event</i><span style = "color:#90949B">=Some(&quot;event 0&quot;)</span>
<span style = "color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(05) task got event: event <i>event</i><span style = "color:#90949B">=Some(&quot;event 4&quot;)</span>
<span style = "color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(05) task got event: event <i>event</i><span style = "color:#90949B">=Some(&quot;event 7&quot;)</span>
<span style = "color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(05) task got event: event <i>event</i><span style = "color:#90949B">=Some(&quot;event 8&quot;)</span>
<span style = "color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(05) task got event: event <i>event</i><span style = "color:#90949B">=Some(&quot;event 1&quot;)</span>
<span style = "color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(05) task got event: event <i>event</i><span style = "color:#90949B">=Some(&quot;event 5&quot;)</span>
<span style = "color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(05) task got event: event <i>event</i><span style = "color:#90949B">=Some(&quot;event 9&quot;)</span>
<span style = "color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(05) task got event: event <i>event</i><span style = "color:#90949B">=Some(&quot;event 3&quot;)</span>
<span style = "color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(05) task got shutdown signal
test non_blocking_async_event_loops::test_main_loop ... ok
</pre>

Interesting code links:
- Testing async code: <https://github.com/r3bl-org/r3bl-open-core/blob/main/terminal_async/src/readline_impl/readline.rs#L612>
- Using dependency injection and dealing with `dyn T` (trait objects): <https://github.com/r3bl-org/r3bl-open-core/blob/main/terminal_async/src/readline_impl/readline.rs#L344>.
- Event `loop`s and breaking out of them (lifecycle control mechanisms):
  <https://github.com/nazmulidris/rust-scratch/blob/main/tcp-api-server/src/server_task.rs#L43>
  and
  <https://github.com/nazmulidris/rust-scratch/blob/main/tcp-api-server/src/client_task.rs#L108>.

### Parting thoughts
<a id="markdown-parting-thoughts" name="parting-thoughts"></a>

- Try not to use cancellation token:
  <https://docs.rs/tokio-util/latest/tokio_util/sync/struct.CancellationToken.html>,
  instead do this: <https://github.com/nazmulidris/rust-scratch/pull/32> and
  <https://github.com/nazmulidris/rust-scratch/commit/e129b0f681dd1eea1bcdd3372cd08a05081922ff>
- Do not use async or Tokio for underlying sync OS file copy:
  <https://users.rust-lang.org/t/tokio-copy-slower-than-std-io-copy/111242>.
- Using the right `Mutex` in conjunction with `Arc` and holding them across await points
  from [tokio
  docs](https://docs.rs/tokio/latest/tokio/sync/struct.Mutex.html#which-kind-of-mutex-should-you-use).
- Good videos:
  - [Async Rust: the good, the bad, and the ugly - Steve Klabnik](https://www.youtube.com/watch?v=1zOd52_tUWg&t=2088s).
  - [Nicholas Matsakis - Rust 2024 and beyond](https://www.youtube.com/watch?v=04gTQmLETFI).

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
