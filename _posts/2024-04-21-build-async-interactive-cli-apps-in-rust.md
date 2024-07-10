---
title: "Build with Naz : Build interactive and non blocking CLI apps with ease in Rust using r3bl_terminal_async"
author: Nazmul Idris
date: 2024-04-21 15:00:00+00:00
excerpt: |
  The r3bl_terminal_async library lets your CLI program be asynchronous and interactive without
  blocking the main thread. Your spawned tasks can use it to concurrently write to the display
  output, pause and resume it. You can also display of colorful animated spinners ⌛🌈 for long
  running tasks. With it, you can create beautiful, powerful, and interactive REPLs
  (read execute print loops) with ease.
layout: post
categories:
  - Rust
  - CLI
  - Server
---

<img class="post-hero-image" src="{{ 'assets/r3bl_terminal_async-hero.svg' | relative_url }}"/>

<!-- TOC -->

- [Why use this crate](#why-use-this-crate)
- [Demo of this in action](#demo-of-this-in-action)
- [Example of using this crate](#example-of-using-this-crate)
- [Video series on developerlife.com YouTube channel on building this crate with Naz](#video-series-on-developerlifecom-youtube-channel-on-building-this-crate-with-naz)

<!-- /TOC -->

The `r3bl_terminal_async` library lets your CLI program be asynchronous and interactive without
blocking the main thread. Your spawned tasks can use it to concurrently write to the display output,
pause and resume it. You can also display of colorful animated spinners ⌛🌈 for long running tasks.
With it, you can create beautiful, powerful, and interactive REPLs (read execute print loops) with
ease.

## Why use this crate

<a id="markdown-why-use-this-crate" name="why-use-this-crate"></a>

- Because [read_line()](https://doc.rust-lang.org/std/io/struct.Stdin.html#method.read_line) is
  blocking. And there is no way to terminate an OS thread that is blocking in Rust. To do this you
  have to exit the process (who’s thread is blocked in `read_line()`).
- Another annoyance is that when a thread is blocked in `read_line()`, and you have to display
  output to stdout concurrently, this poses some challenges.

## Demo of this in action

<a id="markdown-demo-of-this-in-action" name="demo-of-this-in-action"></a>

Here's a screen capture of the types of interactive REPLs that you can expect to build in Rust,
using this crate.

![](https://github.com/r3bl-org/r3bl-open-core/blob/main/terminal_async/docs/r3bl_terminal_async_clip_ffmpeg.gif?raw=true)

A couple of things to note about this demo:

1. You can use up, down to access history in the multi-line editor.
2. You can use left, right, ctrl+left, ctrl+right, to jump around in the multi-line editor.
3. You can edit content in this multi-line editor without blocking the main thread, and while other
   tasks (started via `tokio::spawn` are concurrently producing output to the display.
4. You can pause the output while spinners are being displayed, and these spinners support many
   different kinds of animations!

## Example of using this crate

<a id="markdown-example-of-using-this-crate" name="example-of-using-this-crate"></a>

There are great examples in the `examples` folder of the repo
[here](https://github.com/r3bl-org/r3bl-open-core/tree/main/terminal_async/examples). Let's walk
through a simple example of using this crate. Let's create a new example using the following
commands:

```bash
cargo new --bin async-cli
cd async-cli
cargo add r3bl_terminal_async
cargo add miette --features fancy
cargo add tokio --features full
```

Now, let's add a `main.rs` file in the `src` folder.

```rust
use std::time::Duration;

use r3bl_terminal_async::{tracing_setup, TerminalAsync, TracingConfig};
use tokio::time::interval;

#[tokio::main]
async fn main() -> miette::Result<()> {
    let maybe_terminal_async = TerminalAsync::try_new("> ").await?;

    // If the terminal is not fully interactive, then return early.
    let mut terminal_async = match maybe_terminal_async {
        None => return Ok(()),
        _ => maybe_terminal_async.unwrap(),
    };

    // Initialize tracing w/ the "async stdout".
    tracing_setup::init(TracingConfig::new(Some(
        terminal_async.clone_shared_writer(),
    )))?;

    // Start tasks.
    let mut interval_1_task = interval(Duration::from_secs(1));
    let mut interval_2_task = interval(Duration::from_secs(4));

    terminal_async
        .println("Welcome to your async repl! press Ctrl+D or Ctrl+C to exit.")
        .await;

    loop {
        tokio::select! {
            _ = interval_1_task.tick() => {
                terminal_async.println("interval_1_task ticked").await;
            },
            _ = interval_2_task.tick() => {
                terminal_async.println("interval_1_task ticked").await;
            },
            user_input = terminal_async.get_readline_event() => match user_input {
                Ok(readline_event) => {
                    match readline_event {
                        r3bl_terminal_async::ReadlineEvent::Eof => break,
                        r3bl_terminal_async::ReadlineEvent::Interrupted => break,
                        _ => (),
                    }

                    let msg = format!("{:?}", readline_event);
                    terminal_async.println(msg).await;
                },
                Err(err) => {
                    let msg = format!("Received err: {:?}. Exiting.", err);
                    terminal_async.println(msg).await;
                    break;
                },
            }
        }
    }

    // Flush all writers to stdout
    let _ = terminal_async.flush().await;

    Ok(())
}
```

You can then run this program using `cargo run`. Play with it to get a sense of the asynchronous and
non blocking nature of the REPL. Press Ctrl+C, or Ctrl+D to exit this program.

## Video series on developerlife.com YouTube channel on building this crate with Naz
<a id="markdown-video-series-on-developerlife.com-youtube-channel-on-building-this-crate-with-naz" name="video-series-on-developerlife.com-youtube-channel-on-building-this-crate-with-naz"></a>

> If you have comments and feedback on this content, or would like to request new content
> (articles & videos) on developerlife.com, please join our [discord
> server](https://discord.gg/8M2ePAevaMi).

You can watch a video series on building this crate with Naz on the
[developerlife.com YouTube channel](https://www.youtube.com/@developerlifecom).

Here's the video that is tied to this blog post:

<iframe
  src="https://www.youtube.com/embed/X5wDVaZENOo?si=yYfXuCxSilWh4Gd5"
  title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin"
  allowfullscreen>
</iframe>

- [YT channel](https://www.youtube.com/@developerlifecom)
  - [Part 1: Why?](https://youtu.be/6LhVx0xM86c)
  - [Part 2: What?](https://youtu.be/3vQJguti02I)
  - [Part 3: Do the refactor and rename the crate](https://youtu.be/uxgyZzOmVIw)
  - [Part 4: Build the spinner](https://www.youtube.com/watch?v=fcb6rstRniI)
  - [Part 5: Add color gradient animation to spinner](https://www.youtube.com/watch?v=_QjsGDds270)
  - [Part 6: Publish the crate and overview](https://youtu.be/X5wDVaZENOo)
  - [Testing playlist](https://www.youtube.com/watch?v=Xt495QLrFFk&list=PLofhE49PEwmwLR_4Noa0dFOSPmSpIg_l8)
    - [Part 1: Intro](https://www.youtube.com/watch?v=Xt495QLrFFk)
    - [Part 2: Deep dive](https://www.youtube.com/watch?v=4iM9t5dgvU4)
  - Playlists
      - [Build with Naz, fundamental effective Rust](https://www.youtube.com/playlist?list=PLofhE49PEwmza94sS7UmJnN9gSCHTVTfz)
      - [Build with Naz, effective async Rust and tokio](https://www.youtube.com/playlist?list=PLofhE49PEwmwO69E7eiQ-ewnMME8ydgQ5)
      - [Build with Naz, async readline and spinner for CLI in Rust](https://www.youtube.com/watch?v=3vQJguti02I&list=PLofhE49PEwmwelPkhfiqdFQ9IXnmGdnSE)
      - [Build with Naz, testing in Rust](https://www.youtube.com/watch?v=Xt495QLrFFk&list=PLofhE49PEwmwLR_4Noa0dFOSPmSpIg_l8)
