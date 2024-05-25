---
title:
  "Build with Naz : tokio tracing & OTel and how to use it in Rust"
author: Nazmul Idris
date: 2024-05-15 15:00:00+00:00
excerpt: |
  Learn how to use tokio tracing and OpenTelemetry (with Jaeger) in async Rust to instrument your code and collect
  telemetry data for observability.
layout: post
categories:
  - Rust
  - CLI
  - Server
---

<img class="post-hero-image" src="{{ 'assets/tracing_otel_rust.svg' | relative_url }}"/>

<!-- TOC -->

- [Why use observability in async Rust?](#why-use-observability-in-async-rust)
- [Tokio tracing usage](#tokio-tracing-usage)
- [Video of this in action in the real world](#video-of-this-in-action-in-the-real-world)
- [Short example to illustrate the use of tracing and OTel in Rust](#short-example-to-illustrate-the-use-of-tracing-and-otel-in-rust)
- [Build with Naz video series on developerlife.com YouTube channel](#build-with-naz-video-series-on-developerlifecom-youtube-channel)

<!-- /TOC -->

## Why use observability in async Rust?
<a id="markdown-why-use-observability-in-async-rust%3F" name="why-use-observability-in-async-rust%3F"></a>

In synchronous systems, it's often easy to understand the flow of execution by looking at
log messages. For example, if a thread walking through a single function ends up calling a whole
host of other functions, and they all emit log messages, you can often piece together what
happened by looking at the log messages in order.

However, in asynchronous systems, this is challenging. When using Tokio, for example,
different threads might be executing the same task, as it goes from being parked, to being
woken up, to being parked again. Both temporality (when a log event happened) and
causality (what caused the event) get muddled. This is where observability comes in,
provided by Tokio `tracing` crate and OpenTelemetry (OTel) crates.

The `tracing` crate expands upon logging-style diagnostics by allowing libraries and
applications to record structured events with additional information about temporality and
causality. Unlike a log message, a `Span` in tracing has a beginning and end time, may be
entered and exited by the flow of execution, and may exist within a nested tree of similar
spans.

For representing things that occur at a single moment in time, tracing provides the
complementary concept of events. Both `Spans` and `Events` are structured, with the ability to
record typed data as well as textual messages.

## Tokio tracing usage
<a id="markdown-tokio-tracing-usage" name="tokio-tracing-usage"></a>

Code:
- [`tcp-api-server` crate is the sample project that uses `tracing` and OTel and the
  modules below (provided by the `r3bl_terminal_async`
  crate](https://github.com/nazmulidris/rust-scratch/tree/main/tcp-api-server).
- [`r3bl_terminal_async` Tokio `tracing`
  setup](https://github.com/r3bl-org/r3bl-open-core/blob/nazmulidris/otel/terminal_async/src/public_api/tracing_setup.rs).
- [`r3bl_terminal_async` Jaeger & OTel
  setup](https://github.com/r3bl-org/r3bl-open-core/blob/nazmulidris/otel/terminal_async/src/public_api/jaeger_setup.rs#L1).

Here's an example of using the `tracing` crate. Some key symbols to note are::
- `#[instrument]` attribute is used to create a span.
- `Span::current().record()` is used to add fields to the span (when the function is
  running, and this information is not known statically beforehand).
- `info!`, `error!`, etc are used to emit log or tracing events. However, these are not
  used to create spans; they are used to emit events within a span.
- `#[tokio::main]` is used to run the async main function.

```rust
use tracing::{info, instrument, Span};

#[tokio::main]
async fn main() {
    // Set up the tracing subscriber, so you can see the output of log events in stdout.
    // https://docs.rs/tracing-subscriber/latest/tracing_subscriber/fmt/fn.fmt.html
    tracing_subscriber::fmt()
        .with_test_writer()
        .with_env_filter("info")
        .init();

    // Call the entry point function.
    client_task::entry_point(1234).await;
}

mod client_task {
    #[instrument(name = "caller", skip_all, fields(?client_id))]
    pub async fn entry_point(client_id: usize) {
        info!("entry point");
        more_context("bar").await;
        handle_message(client_id, "foo").await;
        no_instrument("baz").await;
    }

    #[instrument(name = "callee", skip_all, fields(%message))]
    pub async fn handle_message(client_id: usize, message: String) {
        info!("handling message");
    }

    #[instrument(fields(extra))]
    pub async fn more_context(extra: &str) {
        CurrentSpan::current().record("extra", &extra);
        info!("more context");
    }

    pub async fn no_instrument(arg: &str) {
        info!("no instrument fn");
    }

}
```

Here are some key points to remember when using `tracing` from the code above:

- You have to be careful about recording the same field multiple times, in an async call
  chain. In the example above, `client_task::entry_point()` is the entry point, and is the
  only function that should log the `?client_id`; `?` means debug. And not any other
  functions that it calls, like `handle_message()`.

- When you call `entry_point()`, it will call `handle_message()`, and the span that is
  generated by `handle_message()` will have the `client_id` field added to it, because of
  the call chain. So the output of `info!("handling message")` will have the `client_id`
  included in it (for free). It will also have the `%message` field in it; `%` means
  display. You don't have to explicitly add either of these fields to the `info!()` call 🎉.

- If you use the `client_id` field in multiple `#[instrument..]` attributes in functions
  (that are in the call chain), then this will show up multiple times in the log output
  (when using `info!`, `debug!`, etc) of the leaf function in the call chain. So when you
  see the same fields showing up multiple times in the output from `info!`, `debug!`, etc,
  then you know that you have to remove that field from the `#[instrument..]` attribute
  somewhere in the call chain (that the span covers).

- You have to be careful about how to use
  [`[#instrument]`](https://docs.rs/tracing/latest/tracing/attr.instrument.html) attribute
  with `tracing::Span::record`. You have to call
  `tracing::Span::current().record("foo","bar")` in the same function where the
  `#[instrument(fields(foo))]` attribute is used.

- When a function is called that isn't instrumented, by another one, which is, any log
  events generated in the un-instrumented function will be associated with the span of the
  instrumented function. In the `no_instrument` function's log output, you will see
  addition context from the `entry_point` function that looks something like `INFO
  caller{client_id=1234}: no instrument fn`.

Here are some helpful links to learn more about this topic:

- [Tokio tracing docs](https://tokio.rs/tokio/topics/tracing).
- [Difference between `#[instrument]` (create spans) and emitting events (eg: `info!`, `debug!`, etc:](https://gemini.google.com/app/5b106a8100c4dcf4).
- [Tokio and OTel integration docs](https://tokio.rs/tokio/topics/tracing-next-steps).
- [Tokio tracing and OTel integration crate](https://github.com/tokio-rs/tracing-opentelemetry).
- [Blog post to connect tracing and OTel](https://broch.tech/posts/rust-tracing-opentelemetry/).
- [Code examples for using Jaeger with tracing](https://github.com/open-telemetry/opentelemetry-rust/blob/main/examples/tracing-jaeger/src/main.rs).
- [OTel primer](https://opentelemetry.io/docs/concepts/observability-primer/#spans).
- [Jaeger docs](https://www.jaegertracing.io/docs/1.57/getting-started/).

## Video of this in action in the real world
<a id="markdown-video-of-this-in-action-in-the-real-world" name="video-of-this-in-action-in-the-real-world"></a>

This blog post only has a short example to illustrate how to use Rust tracing and OTel
with Jaeger. To see how these ideas can be used in production code, with real-world
examples, please watch the following video on the [developerlife.com YouTube
channel](https://www.youtube.com/@developerlifecom).

<!-- rust tokio tracing and otel for async rust & playlist -->
<iframe
    src="https://www.youtube.com/embed/Wf8JrLgBuKI?si=cmLaUWs-pbJ39lLc"
    title="YouTube video player"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    referrerpolicy="strict-origin-when-cross-origin"
    allowfullscreen>
</iframe>

Here's the code for this real world example:

- [Repo for the `tcp-api-server` crate, which is an example of creating a TCP server and
  client that are observable using `tracing` and
  OTel](https://github.com/nazmulidris/rust-scratch/tree/main/tcp-api-server).
  - It uses the `r3bl_terminal_async` crate to allow async, non-blocking readline
    functionality, along with `stdout` and `stderr` that are also async.
  - This crate is also used to configure Jaeger and tracing subscribers for file, stdout
    logging.

- [README for `tcp-api-server` crate, which shows how to use Jaeger, and configure file
  logging and stdout
  logging](https://github.com/nazmulidris/rust-scratch/tree/main/tcp-api-server#tokio-tracing-usage).

- [How to build up tracing subscribers using layers (type erasure, decl macros,
  etc)](https://github.com/r3bl-org/r3bl-open-core/blob/nazmulidris/refactor-tokio-tracing/terminal_async/src/public_api/tracing_setup.rs).

- [How to add an OTel layer to a
  subscriber](https://github.com/nazmulidris/rust-scratch/pull/34).

- [How the subscriber is configured with custom layers in `r3bl_terminal_async`
  crate](https://github.com/r3bl-org/r3bl-open-core/pull/326).

## Short example to illustrate the use of tracing and OTel in Rust
<a id="markdown-short-example-to-illustrate-the-use-of-tracing-and-otel-in-rust" name="short-example-to-illustrate-the-use-of-tracing-and-otel-in-rust"></a>

Let's look a single example (that fits in one file) that illustrates the use of tracing
in Rust. You can run `cargo new --lib tracing-otel` to create a new library crate, and then run
the following:

```sh
cargo add miette --features fancy
cargo add tracing tracing-subscriber
cargo add tokio --features full
```

Then you can add the following code to the `src/main.rs` file.

```rust
use miette::IntoDiagnostic;
use tracing::Span;

#[tokio::main]
async fn main() -> miette::Result<()> {
    let subscriber = tracing_subscriber::fmt()
        .without_time()
        .pretty()
        .with_max_level(tracing::Level::DEBUG)
        .finish();

    tracing::subscriber::set_global_default(subscriber).into_diagnostic()?;

    print_message("foo").await;

    Ok(())
}
```

The first part of the code sets up the tracing subscriber. In this case we are using a formatting
subscriber that prints logs to the console. This subscriber is configured to not print the time of
the log message, to pretty print the logs, and to print logs at the `DEBUG` level or higher.

When you use `#[attribute]` along with `info!`, `debug!`, etc, Tokio will emit log events
that are associated with a span. This is the "emitter" side of the process. The other side
is the "subscriber" side, which is where the logs are actually printed to the console, or
sent to a file, or sent to an OTel collector service like Jaeger (using OTLP protocol over
gRPC).

Tokio `tracing` allows us to use this simple default subscriber, or create our own custom
subscribers. It even allows a subscriber to be composed from layers. We can create our own
custom layers, or use some default ones (like the level filter layer).

OTel is itself a tracing layer. In the video & `tcp-api-server` repo, you will see how to
use OTel with Jaeger, and how to configure the OTel layer with a custom layer.

Next you can add the following code to the `src/main.rs` file.

```rust
#[tracing::instrument(fields(arg = ?arg, client_id), ret)]
async fn print_message(arg: &str) {
    tracing::info!("log message one");
    println!("{}", prepare_message().await);

    Span::current().record("client_id", 1234);

    tracing::warn!("log message two");
}

#[tracing::instrument(ret)]
async fn prepare_message() -> String {
    tracing::debug!("preparing message");
    let it = "Hello, world!".to_string();
    tracing::debug!("message prepared");
    it
}
```

The `print_message` function is annotated with the `#[tracing::instrument]` attribute.
This attribute creates a span for the function, and adds the `arg` field to the span along
with the `client_id` field. In all the log events are emitted within the span, the `arg`
and `client_id` field will be included in the log output. This additional context is
provided by a span. And you don't have to write any code to the `info!`, `warn!`, etc
calls to include these fields in the log output.

You can run the code using `cargo run`. The code will produce the following output.

```
   INFO tracing_otel: log message one
    at src/main.rs:38
    in tracing_otel::print_message with arg: "foo"

  DEBUG tracing_otel: preparing message
    at src/main.rs:48
    in tracing_otel::prepare_message
    in tracing_otel::print_message with arg: "foo"

  DEBUG tracing_otel: message prepared
    at src/main.rs:50
    in tracing_otel::prepare_message
    in tracing_otel::print_message with arg: "foo"

   INFO tracing_otel: return: "Hello, world!"
    at src/main.rs:46
    in tracing_otel::prepare_message
    in tracing_otel::print_message with arg: "foo"

Hello, world!

   WARN tracing_otel: log message two
    at src/main.rs:43
    in tracing_otel::print_message with arg: "foo", client_id: 1234

   INFO tracing_otel: return: ()
    at src/main.rs:36
    in tracing_otel::print_message with arg: "foo", client_id: 1234
```

Beyond this simple example, to dive deeper, please check out the video and the
`tcp-api-server` repo to get a sense of how this can all be used in a real world example
that has lots of moving parts and pieces. Observability here can tell the story of what
happened in the system, so it can be another way of getting an understanding of the
system's behavior.

## Build with Naz video series on developerlife.com YouTube channel
<a id="markdown-build-with-naz-video-series-on-developerlife.com-youtube-channel" name="build-with-naz-video-series-on-developerlife.com-youtube-channel"></a>

You can watch a video series on building this crate with Naz on the
[developerlife.com YouTube channel](https://www.youtube.com/@developerlifecom).

- [YT channel](https://www.youtube.com/@developerlifecom)
- Playlists
    - [Build with Naz, async Rust and tokio](https://www.youtube.com/playlist?list=PLofhE49PEwmwO69E7eiQ-ewnMME8ydgQ5)
    - [Build with Naz, async readline and spinner for CLI in Rust](https://www.youtube.com/watch?v=3vQJguti02I&list=PLofhE49PEwmwelPkhfiqdFQ9IXnmGdnSE)
    - [Build with Naz, testing in Rust](https://www.youtube.com/watch?v=Xt495QLrFFk&list=PLofhE49PEwmwLR_4Noa0dFOSPmSpIg_l8)
