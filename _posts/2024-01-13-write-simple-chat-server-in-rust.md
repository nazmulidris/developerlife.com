---
title: "Write a simple TCP chat server in Rust"
author: Nazmul Idris
date: 2024-01-13 15:00:00+00:00
excerpt: |
  A guide on how to create write a simple TCP chat server in Rust
  using Tokio
layout: post
categories:
  - Rust
  - CLI
  - Server
---

<img class="post-hero-image" src="{{ 'assets/chatserver-hero.svg' | relative_url }}"/>

<!-- TOC -->

- [Build a chat server using Tokio](#build-a-chat-server-using-tokio)
- [The chat server comprises all these pieces](#the-chat-server-comprises-all-these-pieces)
- [Add dependencies to Cargo.toml](#add-dependencies-to-cargotoml)
- [Main function](#main-function)
  - [tokio::spawn does not spawn a new thread, so what does it actually do?](#tokiospawn-does-not-spawn-a-new-thread-so-what-does-it-actually-do)
- [Handle client task function](#handle-client-task-function)
  - [Two concurrent tasks in the tokio::select! block](#two-concurrent-tasks-in-the-tokioselect-block)
  - [Handle read from broadcast channel function](#handle-read-from-broadcast-channel-function)
  - [Handle socket read function](#handle-socket-read-function)
- [Build with Naz video series on developerlife.com YouTube channel](#build-with-naz-video-series-on-developerlifecom-youtube-channel)

<!-- /TOC -->

## Build a chat server using Tokio
<a id="markdown-build-a-chat-server-using-tokio" name="build-a-chat-server-using-tokio"></a>

In this tutorial we will build a simple chat server using Tokio. The server will be able
to handle multiple clients, and each client will be able to send messages to the server,
which will then broadcast the message to all other connected clients.

- We will use Tokio's `tokio::net::TcpListener` and `tokio::net::TcpStream` to create a
  TCP server that listens for incoming connections and handles them concurrently.
- We will also use Tokio's `tokio::sync::broadcast` to broadcast messages to all connected
  clients.

Read [this tutorial]({{ '/2024/01/13/write-simple-netcat-in-rust/' | relative_url}}) to
learn more about the basics of TCP client and server programming in Rust (without using
Tokio).

<!--
simple-netcat-in-rust video
Source: https://github.com/nazmulidris/developerlife.com/issues/4
-->
> Here's a video of the app that we are going to build in action.
> <video width="100%" controls>
>   <source src="https://github.com/nazmulidris/developerlife.com/assets/2966499/14ce32ce-0988-4853-acd5-1174b1864d57" type="video/mp4"/>
> </video>

> You can find the finished source code for this tutorial
> [here](https://github.com/nazmulidris/rust-scratch/tree/main/tcp-server-netcat-client).


## The chat server comprises all these pieces
<a id="markdown-the-chat-server-comprises-all-these-pieces" name="the-chat-server-comprises-all-these-pieces"></a>

```text
   ┌─CLIENT-1───────┐      ┌─CLIENT─2───────┐        ┌─CLIENT─3──────┐
   │                │      │                │        │               │
   └───────┼────────┘      └──────┼─────────┘        └─────┼─────────┘
           │                      │                        │
┌─SERVER───┼──────────────────────┼────────────────────────┼────────────┐
│          │                      │                        │            │
│                                                                       │
│ handle_client_task()   handle_client_task()    handle_client_task()   │
│ ┌───────────────────┐ ┌────────────────────┐  ┌─────────────────────┐ │
│ │   ┌────┐ ┌────┐   │ │   ┌────┐ ┌────┐    │  │    ┌────┐ ┌────┐    │ │
│ │   │ TX │ │ RX │   │ │   │ TX │ │ RX │    │  │    │ TX │ │ RX │    │ │
│ │   └─┬──┘ └─▲──┘   │ │   └─┬──┘ └─▲──┘    │  │    └─┬──┘ └─▲──┘    │ │
│ │     │      │      │ │     │      │       │  │      │      │       │ │
│ └─────┼──────┼──────┘ └─────┼──────┼───────┘  └──────┼──────┼───────┘ │
│       │      │              │      │                 │      │         │
│       │      │              │      │                 │      │         │
│ ┌─────▼──────┴──────────────▼──────┴─────────────────▼──────┴───────┐ │
│ │                    (TX, RX) = channel::broadcast()                │ │
│ └───────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────┘
```

<!-- Diagram source
https://asciiflow.com/#/share/eJztVs1Kw0AQfpVlTy1E0ApiA54kB0E8xCI5LJTYBhRjhDZCSylIzh56CCXP4TlP0ydxwzbtbnY2bdL1p9VhApOdmW9mv0yWneDAffawGbz6voF9d%2BwNsIknBI8INtvnxwbBY2q1ztrUCr1RSF8IRpks4pTq5fWVddM5OmFvsqKlLOL3RfzGoqnRog%2BkM0X8qSqekCDvBhVEqB7J3qjcexjIAqCMzbcAoRf8B4RfQ9dAMTSLqWJGmSa7ZeedA2QUpcSV%2BSgS286tZd9Zdj0q9kXZZvUQp%2BRSmVRTeOAHN%2Bj7XrfnP3pB2A3d4VOjyaKUHnUKD6yFXpQf1LvpTBtMcYsl3xI4QZfeaIPzZ4oA7IMfRCwu8TqDlgpNVU6CmkUdZ2XaDoKbi1gUM22Ho4RrZkNQBabmH2VMxeJBnORLWVa%2BJDVXMQmYnVUzwijx86OKiLYI%2BC%2F45QU1naP8tSAVf7aSRV4TbTDCFpGSDrSNV%2B389iIC7XOtdw2NaHWh5M3KJGbS6DgGPUeb6AL16GUh8HzTvB%2B8uP2eOwzzuwLArvax%2F7UKzKY22WPgP6gET%2FH0Ex1Q3VY%3D)
-->

The server has a `main` function that creates a `tokio::net::TcpListener` and listens for
incoming connections. When a new connection is received, it spawns a new task to handle
the connection using `tokio::spawn()`.

Using `tokio::select!`, the task tries to do the following concurrently, and waits until
one of them completes:
1. The task reads messages from its client and broadcasts them to all other connected
   clients. It also echoes the message back to its client.
2. The task listens for messages from other clients and sends them to its client.

When one task above completes, the other is dropped. Then the code path with the completed
task executes. Then the code returns to the infinite loop, if it hasn't returned already.

A client can be any TCP client, such as `telnet`, `nc`, or PuTTY.

## Add dependencies to Cargo.toml
<a id="markdown-add-dependencies-to-cargo.toml" name="add-dependencies-to-cargo.toml"></a>

Let's create a new project by running `cargo create --bin tcp-server-netcat-client`. Then
we will add the following dependencies to our `Cargo.toml` file.

```toml
# tokio.
tokio = { version = "1.35.1", features = ["full"] }

# stdout logging.
femme = { version = "2.2.1" }
log = { version = "0.4.20" }

# r3bl_rs_utils_core - friendly name generator.
r3bl_rs_utils_core = { version = "0.9.12" }
r3bl_tui = { version = "0.5.1" }
```

## Main function
<a id="markdown-main-function" name="main-function"></a>

We will implement the following algorithm for our server in our main function:
1. Create a broadcast channel. It will be shared by all the client tasks.
2. Create `TcpListener` and bind to an address & port.
3. Loop:
   - Accept socket connection, and get its `TCPStream`.
   - Use `tokio::spawn()` to spawn a task to handle this client connection and its
     `TCPStream`.

In the task that handles the connection:
1. Get `BufReader` & `BufWriter` from the `TCPStream`. The reader and writer allow us to
   read data from and write data to the client socket.
2. Loop:
   - Use `tokio::select!` to concurrently:
      - Read from broadcast channel (via `recv()`):
         - Send the message to the client (only if it is from a different client) over the
           socket (use `BufWriter` to write the message).
      - Read from socket (via `BufReader::read_line()`):
         - Read `incoming` from reader.
         - Call `process(incoming)` and generate `outgoing`. This colorizes the `incoming`
           message with a lolcat effect to generate the `outgoing` message.
         - Send `incoming` message to other connected clients (via the broadcast channel).

> You can find the finished source code for this tutorial
> [here](https://github.com/nazmulidris/rust-scratch/tree/main/tcp-server-netcat-client).

Here's the code for the main function, and some supporting type aliases and structs:

```rust
pub type IOResult<T> = std::io::Result<T>;

#[derive(Debug, Clone)]
pub struct MsgType {
    pub socket_addr: SocketAddr,
    pub payload: String,
    pub from_id: String,
}

#[tokio::main]
pub async fn main() -> IOResult<()> {
    let addr = "127.0.0.1:3000";

    // Start logging.
    femme::start();

    // Create TCP listener.
    let tcp_listener = TcpListener::bind(addr).await?;
    log::info!("Server is ready to accept connections on {}", addr);

    // Create channel shared among all clients that connect to the server loop.
    let (tx, _) = broadcast::channel::<MsgType>(10);

    // Server loop.
    loop {
        // Accept incoming socket connections.
        let (tcp_stream, socket_addr) = tcp_listener.accept().await?;

        let tx = tx.clone();
        tokio::spawn(async move {
            let result = handle_client_task(tcp_stream, tx, socket_addr).await;
            match result {
                Ok(_) => {
                    log::info!("handle_client_task() terminated gracefully")
                }
                Err(error) => log::error!("handle_client_task() encountered error: {}", error),
            }
        });
    }
}
```

To run the server, you can run `cargo run`. There are no command line arguments to pass or
parse.

### tokio::spawn does not spawn a new thread, so what does it actually do?
<a id="markdown-tokio%3A%3Aspawn-does-not-spawn-a-new-thread%2C-so-what-does-it-actually-do%3F" name="tokio%3A%3Aspawn-does-not-spawn-a-new-thread%2C-so-what-does-it-actually-do%3F"></a>

Since `tokio::spawn` sounds similar to `thread::spawn` it might be easy to assume that
`tokio::spawn` creates a new thread. This would go against the idea of even using tokio
(which is all about concurrency and non blocking IO), since handling one connection per
thread isn't [scalable](https://g.co/bard/share/74f433bad400), which is what we did in
this tutorial: [Write a simple TCP chat server in Rust]({{
'/2024/01/13/write-simple-netcat-in-rust/' | relative_url}}).

`tokio::spawn` does not create a thread; it creates a Tokio task, which is a
co-operatively scheduled entity that Tokio knows how to schedule on the Tokio runtime (in
turn, the Tokio runtime can have as many worker threads as you want - from 1 upwards).

By using `tokio::spawn`, you allow the Tokio runtime to switch to another task at points
in the task where it has a `.await`, and only those points. Your alternative, if you don't
want multiple tasks, is to use things like `select!`, `join!` and functions with `select`
or ` join` in their name to have concurrent I/O in a single task.

The point of spawning in Tokio is twofold:

1. If your runtime has multiple threads, then two tasks can execute in parallel on
   different threads, reducing latency.
2. It is almost always easier to understand a complex program in terms of different tasks
   doing their work, than in terms of a single large task doing lots of work concurrently
   (e.g. using `select` to wait for one of many options, or `join` to wait for all options
   to finish).

More information:
1. You can get more info on this topic
    [here](https://users.rust-lang.org/t/socket-per-thread-in-tokio/83712/7).
2. For an even deeper dive into how Tokio tasks themselves are implemented for intra-task
   concurrency, please take a look at this [excellent
   article](https://without.boats/blog/let-futures-be-futures/).

## Handle client task function
<a id="markdown-handle-client-task-function" name="handle-client-task-function"></a>

The `handle_client_task` function is where all the magic happens.
1. It reads messages from its client (over TCP socket) and broadcasts them to all other
   connected clients.
2. It processes the message from its client and echoes it back to its client (over TCP
   socket).
3. It reads messages from other clients (over broadcast channel) and sends them to its
   client (over socket).

Here's the code for the `handle_client_task()` function:

```rust
async fn handle_client_task(
    mut tcp_stream: TcpStream,
    tx: Sender<MsgType>,
    socket_addr: SocketAddr,
) -> IOResult<()> {
    log::info!("Handle socket connection from client");

    let id = friendly_random_id::generate_friendly_random_id();
    let mut rx = tx.subscribe();

    // Set up buf reader and writer.
    let (reader, writer) = tcp_stream.split();
    let mut reader = BufReader::new(reader);
    let mut writer = BufWriter::new(writer);

    // Send welcome message to client w/ ids.
    let welcome_msg_for_client =
        ColorWheel::lolcat_into_string(&format!("addr: {}, id: {}\n", socket_addr, id));
    writer.write(welcome_msg_for_client.as_bytes()).await?;
    writer.flush().await?;

    let mut incoming = String::new();

    loop {
        let tx = tx.clone();
        tokio::select! {
            // Read from broadcast channel.
            result = rx.recv() => {
                read_from_broadcast_channel(result, socket_addr, &mut writer, &id).await?;
            }

            // Read from socket.
            network_read_result = reader.read_line(&mut incoming) => {
                let num_bytes_read: usize = network_read_result?;
                // EOF check.
                if num_bytes_read == 0 {
                    break;
                }
                handle_socket_read(num_bytes_read, &id, &incoming, &mut writer, tx, socket_addr).await?;
                incoming.clear();
            }
        }
    }

    Ok(())
}
```

### Two concurrent tasks in the tokio::select! block
<a id="markdown-two-concurrent-tasks-in-the-tokio%3A%3Aselect!-block" name="two-concurrent-tasks-in-the-tokio%3A%3Aselect!-block"></a>

1. Read from broadcast channel. The function `read_from_broadcast_channel()` does this work.
2. Read from socket. The function `handle_socket_read()` does this work.

Whichever task completes first, the `tokio::select!` block will go down that code path,
and drop the other task.

### Handle read from broadcast channel function
<a id="markdown-handle-read-from-broadcast-channel-function" name="handle-read-from-broadcast-channel-function"></a>

Here's the code for the `read_from_broadcast_channel()` function:

```rust
async fn read_from_broadcast_channel(
    result: Result<MsgType, RecvError>,
    socket_addr: SocketAddr,
    writer: &mut BufWriter<WriteHalf<'_>>,
    id: &str,
) -> IOResult<()> {
    match result {
        Ok(it) => {
            let msg: MsgType = it;
            log::info!("[{}]: channel: {:?}", id, msg);
            if msg.socket_addr != socket_addr {
                writer.write(msg.payload.as_bytes()).await?;
                writer.flush().await?;
            }
        }
        Err(error) => {
            log::error!("{:?}", error);
        }
    }

    Ok(())
}
```

### Handle socket read function
<a id="markdown-handle-socket-read-function" name="handle-socket-read-function"></a>

Here's the code for the `handle_socket_read()` function:

```rust
async fn handle_socket_read(
    num_bytes_read: usize,
    id: &str,
    incoming: &str,
    writer: &mut BufWriter<WriteHalf<'_>>,
    tx: Sender<MsgType>,
    socket_addr: SocketAddr,
) -> IOResult<()> {
    log::info!(
        "[{}]: incoming: {}, size: {}",
        id,
        incoming.trim(),
        num_bytes_read
    );

    // Process incoming -> outgoing.
    let outgoing = process(&incoming);

    // outgoing -> Writer.
    writer.write(outgoing.as_bytes()).await?;
    writer.flush().await?;

    // Broadcast outgoing to the channel.
    let _ = tx.send(MsgType {
        socket_addr,
        payload: incoming.to_string(),
        from_id: id.to_string(),
    });

    log::info!(
        "[{}]: outgoing: {}, size: {}",
        id,
        outgoing.trim(),
        num_bytes_read
    );

    Ok(())
}

fn process(incoming: &str) -> String {
    // Remove new line from incoming.
    let incoming_trimmed = format!("{}", incoming.trim());
    // Colorize it.
    let outgoing = ColorWheel::lolcat_into_string(&incoming_trimmed);
    // Add new line back to outgoing.
    format!("{}\n", outgoing)
}
```

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
