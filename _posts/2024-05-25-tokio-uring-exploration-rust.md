---
title:
  "Build with Naz : Linux io_uring and tokio-uring exploration with Rust"
author: Nazmul Idris
date: 2024-05-25 15:00:00+00:00
excerpt: |
  Explore the Linux io_uring syscall with the tokio-uring crate in Rust. This article,
  video, and repo will show you how to use the tokio-uring do async file IO at the OS level,
  and how to use it to build a simple echo TCP server, for use with netcat.
layout: post
categories:
  - Rust
  - CLI
  - Server
---

<img class="post-hero-image" src="{{ 'assets/rust_tokio_uring.svg' | relative_url }}"/>

<!-- TOC -->

- [What is Linux io_uring?](#what-is-linux-io_uring)
- [YouTube video for this article](#youtube-video-for-this-article)
- [Examples of using tokio-uring in Rust](#examples-of-using-tokio-uring-in-rust)
  - [Example 1: Read a file using tokio-uring and async, non-blocking IO](#example-1-read-a-file-using-tokio-uring-and-async-non-blocking-io)
  - [Example 2: Building a TCP echo server using tokio-uring that also uses tokio](#example-2-building-a-tcp-echo-server-using-tokio-uring-that-also-uses-tokio)
  - [Parting thoughts](#parting-thoughts)
- [Build with Naz video series on developerlife.com YouTube channel](#build-with-naz-video-series-on-developerlifecom-youtube-channel)

<!-- /TOC -->

## What is Linux io_uring?
<a id="markdown-what-is-linux-io_uring%3F" name="what-is-linux-io_uring%3F"></a>

When using async Rust and `tokio`, you don't get async file IO at the OS level. Here are
links from the official docs that discourage using `tokio` for file IO:
- [Tokio tutorial, when not to use Tokio](https://tokio.rs/tokio/tutorial).
- [Tokio::io::copy slower than std
  io::copy](https://users.rust-lang.org/t/tokio-copy-slower-than-std-io-copy/111242).

This is because `tokio` uses the `mio` crate, which uses `epoll` on Linux. These are not
the most efficient ways to do async IO on Linux. The most efficient way to do async IO on
Linux is to use the `io_uring` syscall. This is a new syscall that was added to the Linux
kernel in version 5.1. It is a more efficient way to do async IO on Linux, and is used by
the `tokio-uring` crate. Here are some great links to learn more about `io_uring`:
- [io_uring mental
  model](https://unixism.net/loti/what_is_io_uring.html#the-io-uring-interface).
- [How io_uring and eBPF Will Revolutionize Programming in
  Linux](https://www.scylladb.com/2020/05/05/how-io_uring-and-ebpf-will-revolutionize-programming-in-linux/0/).
- [io_uring and Intel Optane
  stats](https://lore.kernel.org/io-uring/4af91b50-4a9c-8a16-9470-a51430bd7733@kernel.dk/T/#u).
- [Announcing io_uring support for Tokio -
  tokio-uring](https://tokio.rs/blog/2021-07-tokio-uring).

In this article, we will explore how to use `tokio-uring` to do async file IO at the OS
level, and how to use it to build a simple echo TCP server, for use with `netcat`.

## YouTube video for this article
<a id="markdown-youtube-video-for-this-article" name="youtube-video-for-this-article"></a>

This blog post has short examples on how to use the `tokio-uring` crate. If you like to
learn via video, please watch the companion video on the [developerlife.com YouTube
channel](https://www.youtube.com/@developerlifecom).

<!-- rust tokio-uring exploration-->
<iframe
    src="https://www.youtube.com/embed/VKL52XmY6Os?si=RgUKu-CZSXvKpJ7M"
    title="YouTube video player"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    referrerpolicy="strict-origin-when-cross-origin"
    allowfullscreen>
</iframe>

<br/>

## Examples of using tokio-uring in Rust
<a id="markdown-examples-of-using-tokio-uring-in-rust" name="examples-of-using-tokio-uring-in-rust"></a>

Let's create some examples to illustrate how to use `tokio-uring`. You can run
`cargo new --bin tokio-uring` to create a new binary crate.

> The code in the video and this tutorial are all in [this GitHub
> repo](https://github.com/nazmulidris/rust-scratch/tree/main/tokio-uring).

Then add the following to the `Cargo.toml` file that's generated. These pull in all the
dependencies that we need for these examples.

```toml
[package]
name = "tokio-uring"
version = "0.1.0"
edition = "2021"

[[bin]]
name = "readfile"
path = "src/readfile.rs"

[[bin]]
name = "socketserver"
path = "src/socketserver.rs"

[dependencies]
tokio-uring = "0.4.0"
tokio = { version = "1.37.0", features = ["full", "tracing"] }
tokio-util = "0.7.11"
tracing = "0.1.40"
tracing-subscriber = "0.3.18"

ctrlc = "3.4.4"
miette = { version = "7.2.0", features = ["fancy"] }

crossterm = { version = "0.27.0", features = ["event-stream"] }

r3bl_terminal_async = { version = "0.5.3" }
```

### Example 1: Read a file using tokio-uring and async, non-blocking IO
<a id="markdown-example-1%3A-read-a-file-using-tokio-uring-and-async%2C-non-blocking-io" name="example-1%3A-read-a-file-using-tokio-uring-and-async%2C-non-blocking-io"></a>

Then you can add the following code to the `src/readfile.rs` file.

```rust
use crossterm::style::Stylize;
use miette::IntoDiagnostic;
use std::path::Path;

fn main() -> miette::Result<()> {
    tokio_uring::start(read_file("Cargo.toml"))?;
    Ok(())
}

async fn read_file(name: impl AsRef<Path>) -> miette::Result<()> {
    let file = tokio_uring::fs::File::open(name).await.into_diagnostic()?;

    let buf_move = vec![0; 4096];

    // Read some data, the buffer is passed by ownership and submitted
    // to the kernel. When the operation completes, we get the buffer
    // back.
    let (result, buf_from_kernel) = file.read_at(buf_move, 0).await;
    let bytes_read = result.into_diagnostic()?;

    println!(
        "{}",
        format!("Read {} bytes", bytes_read)
            .yellow()
            .underlined()
            .bold()
    );

    println!(
        "{}\n{}",
        "Data (bytes):".yellow().bold().underlined(),
        format!("{:?}", &buf_from_kernel[..bytes_read])
            .blue()
            .bold()
    );

    println!(
        "{}\n{}",
        "Data (string):".yellow().bold().underlined(),
        String::from_utf8_lossy(&buf_from_kernel[..bytes_read])
            .cyan()
            .bold()
    );

    Ok(())
}
```

> The code for this example is
> [here](https://github.com/nazmulidris/rust-scratch/tree/main/tokio-uring/src/readfile.rs).

The main things to note about this code.

- We use the `tokio_uring::fs::File` struct to open a file.
- We use the `read_at` method to read from the file at a specific offset. The buffer is
  passed by ownership to the kernel, and when the operation completes, we get the buffer
  back. This is different than how it works with `tokio` and `std`.
- We print out the bytes that were read from the file, and the string representation of
  those bytes.

When you run this code (using `cargo run --bin readfile`), it should produce the following
output:

<pre class="pre-manual-highlight">
<span style="color:#81A1C1"><u style="text-decoration-style:single">read file using tokio_uring: </u></span><span style="color:#BF616A"><u style="text-decoration-style:single"><b>Cargo.toml</b></u></span>
<span style="color:#81A1C1"><u style="text-decoration-style:single">read </u></span><span style="color:#EBCB8B"><u style="text-decoration-style:single"><b>604</b></u></span> bytes from file
<span style="color:#A3BE8C">file contents: [package]</span>
<span style="color:#A3BE8C">name = &quot;tokio-uring&quot;</span>
<span style="color:#A3BE8C">version = &quot;0.1.0&quot;</span>
<span style="color:#A3BE8C">edition = &quot;2021&quot;</span>

<span style="color:#A3BE8C">[[bin]]</span>
<span style="color:#A3BE8C">name = &quot;readfile&quot;</span>
<span style="color:#A3BE8C">path = &quot;src/readfile.rs&quot;</span>

<span style="color:#A3BE8C">[[bin]]</span>
<span style="color:#A3BE8C">name = &quot;socketserver&quot;</span>
<span style="color:#A3BE8C">path = &quot;src/socketserver.rs&quot;</span>

<span style="color:#A3BE8C">[dependencies]</span>
<span style="color:#A3BE8C">tokio-uring = &quot;0.4.0&quot;</span>
<span style="color:#A3BE8C">tokio = { version = &quot;1.37.0&quot;, features = [&quot;full&quot;, &quot;tracing&quot;] }</span>
<span style="color:#A3BE8C">tokio-util = &quot;0.7.11&quot;</span>
<span style="color:#A3BE8C">tracing = &quot;0.1.40&quot;</span>
<span style="color:#A3BE8C">tracing-subscriber = &quot;0.3.18&quot;</span>

<span style="color:#A3BE8C">ctrlc = &quot;3.4.4&quot;</span>

<span style="color:#A3BE8C">miette = { version = &quot;7.2.0&quot;, features = [&quot;fancy&quot;] }</span>

<span style="color:#A3BE8C">crossterm = { version = &quot;0.27.0&quot;, features = [&quot;event-stream&quot;] }</span>

<span style="color:#A3BE8C">r3bl_terminal_async = { version = &quot;0.5.3&quot; }</span>
<span style="color:#A3BE8C"># r3bl_terminal_async = { path = &quot;../../r3bl-open-core/terminal_async&quot; }</span>
</pre>

### Example 2: Building a TCP echo server using tokio-uring that also uses tokio
<a id="markdown-example-2%3A-building-a-tcp-echo-server-using-tokio-uring-that-also-uses-tokio" name="example-2%3A-building-a-tcp-echo-server-using-tokio-uring-that-also-uses-tokio"></a>

For this example, let's add the following code to the `src/socketserver.rs` file.
- This will simply add the required imports to `tokio_uring` for `TcpListener` and
  `TcpStream`.
- And we will also configure the `tracing_subscriber` to use the formatted subscriber, so
  that we get pretty printed log output to stdout and we have information about what thread
  generated that log event.
- We use the `tokio_uring::start` function to spawn the runtime. This runtime isn't the
  same as the one that we get from using `#[tokio::main]` and later in this example, we
  will see how we can handle both.

```rust
use crossterm::style::Stylize;
use miette::IntoDiagnostic;
use r3bl_terminal_async::port_availability;
use std::net::SocketAddr;
use tokio::task::AbortHandle;
use tokio_uring::{
    buf::IoBuf,
    net::{TcpListener, TcpStream},
};
use tokio_util::sync::CancellationToken;

/// Run `netcat localhost:8080` to test this server (once you run this main function).
fn main() -> miette::Result<()> {
    // Register tracing subscriber.
    tracing_subscriber::fmt()
        .without_time()
        .compact()
        .with_target(false)
        .with_line_number(false)
        .with_thread_ids(true)
        .with_thread_names(true)
        .init();

    let cancellation_token = CancellationToken::new();

    // TODO: Add ctrlc handler.

    // TODO: Add code to use the `tokio` runtime and run some futures on it.

    tokio_uring::start(start_server(cancellation_token))?;
}
```

> You can get the source code for this example
> [here](https://github.com/nazmulidris/rust-scratch/tree/main/tokio-uring/src/socketserver.rs).

Next, we will add the code to handle the server logic. The following code handles the
incoming connections (using `tokio_uring` structs). This code is very similar to what we
would write if we were using `tokio` directly.

- The main difference is that we are checking for port availability before binding to the
  address, and we are using `tokio_uring::spawn` to spawn the futures, to handle incoming
  connections.
- We will also use `tokio::select!` to create the main event loop. Since `tokio_uring` is
  in the same family as `tokio`, we can do that!
- The `port_availability` module comes from `r3bl_terminal_async` crate, which is a
  dependency in the `Cargo.toml` file. It allows us to check whether a port is available
  or not, and find a free port in a given port range.

```rust
async fn start_server(cancellation_token: CancellationToken) -> miette::Result<()> {
    let tcp_listener = {
        let addr: SocketAddr = "0.0.0.0:8080".parse().into_diagnostic()?;
        // You can bind to the same address repeatedly, and it won't return
        // an error! Might have to check to see whether the port is open or
        // not before binding to it!
        match port_availability::check(addr).await? {
            port_availability::Status::Free => {
                tracing::info!("Port {} is available", addr.port());
            }
            port_availability::Status::Occupied => {
                tracing::info!(
                    "Port {} is NOT available, can't bind to it",
                    addr.port()
                );
                return Err(miette::miette!(
                    "Port {} is NOT available, can't bind to it",
                    addr.port()
                ));
            }
        }
        TcpListener::bind(addr).into_diagnostic()?
    };

    tracing::info!("{}", "server - started".to_string().red().bold());

    let mut abort_handles: Vec<AbortHandle> = vec![];

    loop {
        tokio::select! {
            _ = cancellation_token.cancelled() => {
                abort_handles.iter().for_each(|handle| handle.abort());
                break;
            }
            it = tcp_listener.accept() => {
                let (tcp_stream, _addr) = it.into_diagnostic()?;
                let join_handle = tokio_uring::spawn(
                    handle_connection(tcp_stream)
                );
                abort_handles.push(join_handle.abort_handle());
            }
        }
    }

    tracing::info!("{}", "server - stopped".to_string().red().bold());
    Ok(())
}
```

Add the following code to handle the echo logic. This code reads from the stream using
`tokio_uring` and its function signature is quite different from what we would write if we
were using `tokio` directly. It is similar to what happens with `read_at` in the previous
example, and it moves ownership to `read`. Which returns a tuple:
1. `Result` containing the number of bytes read.
2. Buffer that was passed from the kernel.

The `write_all` function also returns a tuple that is similar.

```rust
async fn handle_connection(stream: TcpStream) -> miette::Result<()> {
    tracing::info!("handle_connection - start");

    let mut total_bytes_read = 0;
    let mut buf = vec![0u8; 10];

    loop {
        // Read from the stream.
        // Read some data, the buffer is passed by ownership and submitted
        // to the kernel. When the operation completes, we get the buffer
        // back.
        let (result_num_bytes_read, return_buf) = stream.read(buf).await;
        buf = return_buf;
        let num_bytes_read = result_num_bytes_read.into_diagnostic()?;

        // Check for EOF.
        if num_bytes_read == 0 {
            break;
        }

        // Write to the stream.
        let (result_num_bytes_written, slice) =
            stream.write_all(buf.slice(..num_bytes_read)).await;
        result_num_bytes_written.into_diagnostic()?; // Make sure no errors.

        // Update the buffer.
        buf = slice.into_inner();
        total_bytes_read += num_bytes_read;

        tracing::info!(
            "{}: {}",
            "handle_connection - num_bytes_read".to_string().red(),
            num_bytes_read
        );
    }

    tracing::info!(
        "handle_connection - end, total_bytes_read: {}",
        total_bytes_read
    );
    Ok(())
}
```

To test this, you can run the server using `cargo run --bin socketserver`. Then you can
connect to the server using `netcat` (or `nc`) by running `netcat localhost 8080`. You can
type some text and hit enter, and you should see the text echoed back to you.

This is what the output from `netcat` might look like:

<pre class="pre-manual-highlight">netcat localhost 8080
echo echo echo
echo echo echo
</pre>

This is what the output from the server might look like:

<pre class="pre-manual-highlight"> cargo run --bin socketserver
<span style="color:#A3BE8C"> INFO</span> main ThreadId(01) Port is available
<span style="color:#A3BE8C"> INFO</span> main ThreadId(01) <span style="color:#BF616A"><b>server - started</b></span> - 0.0.0.0:8080
<span style="color:#A3BE8C"> INFO</span> main ThreadId(01) <span style="color:#BF616A"><b>handle_connection - start</b></span>
<span style="color:#A3BE8C"> INFO</span> main ThreadId(01) <span style="color:#BF616A">handle_connection - num_bytes_read</span>: 10
<span style="color:#A3BE8C"> INFO</span> main ThreadId(01) <span style="color:#BF616A">handle_connection - num_bytes_read</span>: 5
<span style="color:#A3BE8C"> INFO</span> main ThreadId(01) <span style="color:#BF616A"><b>handle_connection - end, total bytes read</b></span> : 15 bytes
</pre>

There are two more bonus rounds that we can add to this example:
1. Add a `ctrlc` handler to gracefully shutdown the server, when the user types
   <kbd>Ctrl+C</kbd>.
2. Add code to use the `tokio` runtime and run some futures on it.

In the `socketserver.rs` file, you can add the following code to replace
the comment <kbd>//TODO: Add ctrlc handler.</kbd>.
The following code will add a `ctrlc` handler to gracefully
shutdown the server, by cancelling the `cancellation_token`.

```rust
let cancellation_token_clone = cancellation_token.clone();
ctrlc::set_handler(move || {
    tracing::info!("Received Ctrl+C!");
    cancellation_token_clone.cancel();
})
.into_diagnostic()?;
```

And finally, the following code will replace the comment <kbd>// TODO: Add code to use the `tokio` runtime and run some futures on it.</kbd>.
This code will spawn a new OS thread (using `std`) and then create a new multi-threaded
`tokio` runtime on that thread. We will then run some futures on that runtime by passing an async
block to the `block_on` function of the runtime.

```rust
// Can't use #[tokio::main] for `main()`, so we have to use the
// `tokio::runtime::Builder` API. However, we have to launch this in a separate
// thread, because we don't want it to collide with the `tokio_uring::start()`
// call.
let cancellation_token_clone = cancellation_token.clone();
std::thread::spawn(move || {
    // If you use `Builder::new_current_thread()`, the runtime will
    // use the single / current thread scheduler.
    // `Builder::new_multi_thread()` will use a thread pool.
    tokio::runtime::Builder::new_multi_thread()
        .enable_all()
        .worker_threads(4)
        .build()
        .into_diagnostic()
        .unwrap()
        .block_on(async_main(cancellation_token_clone))
});
```

Here's the `async_main` function that we are calling in the code above. This function
simply runs some futures on the `tokio` runtime that we created in the code above. You can
see from the log output that the tasks are run in parallel (sometimes on the same thread
and sometimes on different threads), and are scheduled in a non-deterministic order.

```rust
async fn async_main(cancellation_token: CancellationToken) {
    tracing::info!("{}", "async_main - start".to_string().magenta().bold());

    let mut interval =
        tokio::time::interval(std::time::Duration::from_millis(2_500));

    loop {
        tokio::select! {
            _ = interval.tick() => {
                tracing::info!(
                    "{}",
                    "async_main - tick".to_string().magenta().bold()
                    );

                // Notice in the output, that these tasks are NOT spawned
                // in the same order repeatedly. They are run in parallel
                // on different threads. And these are scheduled in a
                // non-deterministic order.
                let task_1 = tokio::spawn(async {
                    tokio::time::sleep(
                        std::time::Duration::from_millis(10)
                    ).await;
                    tracing::info!("async_main - tick {} - spawn", "#1"
                        .to_string().on_green().black().bold()
                    );
                });
                let task_2 = tokio::spawn(async {
                    tokio::time::sleep(
                        std::time::Duration::from_millis(10)
                    ).await;
                    tracing::info!("async_main - tick {} - spawn", "#2"
                        .to_string().on_red().black().bold()
                    );
                });
                let task_3 = tokio::spawn(async {
                    tokio::time::sleep(
                        std::time::Duration::from_millis(10)
                    ).await;
                    tracing::info!("async_main - tick {} - spawn", "#3"
                        .to_string().on_blue().black().bold()
                    );
                });
                let _ = tokio::join!(task_1, task_2, task_3);
            }
            _ = cancellation_token.cancelled() => {
                tracing::info!("async_main - cancelled");
                break;
            }
        }
    }

    tracing::info!("{}", "async_main - end".to_string().magenta().bold());
}
```

Here's what the output from the server might look like, after adding the `ctrlc` handler and
the `tokio` runtime code and running it for about 10 seconds.

<pre class="pre-manual-highlight"> cargo run --bin socketserver
<span style="color:#A3BE8C"> INFO</span> main ThreadId(01) Port is available
<span style="color:#A3BE8C"> INFO</span> ThreadId(03) <span style="color:#B48EAD"><b>async_main - start</b></span>
<span style="color:#A3BE8C"> INFO</span> main ThreadId(01) <span style="color:#BF616A"><b>server - started</b></span> - 0.0.0.0:8080
<span style="color:#A3BE8C"> INFO</span> ThreadId(03) <span style="color:#B48EAD"><b>async_main - tick</b></span>
<span style="color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(04) async_main - tick <span style="background-color:#81A1C1"><span style="color:#3B4252"><b>#3</b></span></span> - spawn
<span style="color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(06) async_main - tick <span style="background-color:#BF616A"><span style="color:#3B4252"><b>#2</b></span></span> - spawn
<span style="color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(05) async_main - tick <span style="background-color:#A3BE8C"><span style="color:#3B4252"><b>#1</b></span></span> - spawn
<span style="color:#A3BE8C"> INFO</span> ThreadId(03) <span style="color:#B48EAD"><b>async_main - tick</b></span>
<span style="color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(06) async_main - tick <span style="background-color:#BF616A"><span style="color:#3B4252"><b>#2</b></span></span> - spawn
<span style="color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(05) async_main - tick <span style="background-color:#A3BE8C"><span style="color:#3B4252"><b>#1</b></span></span> - spawn
<span style="color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(04) async_main - tick <span style="background-color:#81A1C1"><span style="color:#3B4252"><b>#3</b></span></span> - spawn
<span style="color:#A3BE8C"> INFO</span> ThreadId(03) <span style="color:#B48EAD"><b>async_main - tick</b></span>
<span style="color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(06) async_main - tick <span style="background-color:#81A1C1"><span style="color:#3B4252"><b>#3</b></span></span> - spawn
<span style="color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(05) async_main - tick <span style="background-color:#A3BE8C"><span style="color:#3B4252"><b>#1</b></span></span> - spawn
<span style="color:#A3BE8C"> INFO</span> tokio-runtime-worker ThreadId(04) async_main - tick <span style="background-color:#BF616A"><span style="color:#3B4252"><b>#2</b></span></span> - spawn
<span style="color:#A3BE8C"> INFO</span> ThreadId(03) <span style="color:#B48EAD"><b>async_main - tick</b></span>
</pre>

### Parting thoughts
<a id="markdown-parting-thoughts" name="parting-thoughts"></a>

There are areas of improvement in this codebase, such as port binding issues, and
connection management issues.
1. If you run more than one instance of the process `cargo run --bin startserver` then the
   log output is pretty strange. The 2nd process that's started seems to trigger the
   `handle_connection` function of the first process.
2. When you run the server and connect a client to it using `netcat`, and then kill the
   server process, using <kbd>Ctrl+C</kbd>, the client doesn't drop the connection.

If you can figure out how to fix these issues, please raise a PR on the [GitHub
repo](https://github.com/nazmulidris/rust-scratch/issues). I'd love to see how you solve
these problems!

## Build with Naz video series on developerlife.com YouTube channel
<a id="markdown-build-with-naz-video-series-on-developerlife.com-youtube-channel" name="build-with-naz-video-series-on-developerlife.com-youtube-channel"></a>

You can watch a video series on building this crate with Naz on the
[developerlife.com YouTube channel](https://www.youtube.com/@developerlifecom).

- [YT channel](https://www.youtube.com/@developerlifecom)
- Playlists
    - [Build with Naz, Linux TTY, process, signals, commands in async Rust](https://www.youtube.com/watch?v=bolScvh4x7I&list=PLofhE49PEwmw3MKOU1Kn3xbP4FRQR4Mb3)
    - [Build with Naz, fundamental effective Rust](https://www.youtube.com/playlist?list=PLofhE49PEwmza94sS7UmJnN9gSCHTVTfz)
    - [Build with Naz, effective async Rust and tokio](https://www.youtube.com/playlist?list=PLofhE49PEwmwO69E7eiQ-ewnMME8ydgQ5)
    - [Build with Naz, async readline and spinner for CLI in Rust](https://www.youtube.com/watch?v=3vQJguti02I&list=PLofhE49PEwmwelPkhfiqdFQ9IXnmGdnSE)
    - [Build with Naz, testing in Rust](https://www.youtube.com/watch?v=Xt495QLrFFk&list=PLofhE49PEwmwLR_4Noa0dFOSPmSpIg_l8)
