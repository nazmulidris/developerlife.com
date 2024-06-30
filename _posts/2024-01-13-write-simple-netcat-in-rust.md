---
title: "Write a simple netcat client and server in Rust"
author: Nazmul Idris
date: 2024-01-13 15:00:00+00:00
excerpt: |
  A guide on how to a simple Rust netcat client and server
layout: post
categories:
  - Rust
  - CLI
  - Server
---

<img class="post-hero-image" src="{{ 'assets/netcat-hero.svg' | relative_url }}"/>

<!-- TOC -->

- [Build a Swiss Army knife for networking](#build-a-swiss-army-knife-for-networking)
- [Add dependencies to Cargo.toml](#add-dependencies-to-cargotoml)
- [Configure clap to parse command line arguments](#configure-clap-to-parse-command-line-arguments)
- [Create the client](#create-the-client)
- [Create the server](#create-the-server)
- [Next steps](#next-steps)

<!-- /TOC -->

## Build a Swiss Army knife for networking
<a id="markdown-build-a-swiss-army-knife-for-networking" name="build-a-swiss-army-knife-for-networking"></a>

In this tutorial we will learn how to use Rust to write a simple netcat client and server
using the standard library only. A netcat client is like a Swiss Army knife for
networking. It is similar to PuTTY and telnet. You can use it to connect to a server and
send and receive data. We will create an app that can behave both as a client and server.

1. Our client will allow the user to type a message and send it to any TCP socket server,
   and display the response from the server, in an endless loop.
2. Our server will listen for incoming TCP connections from clients, and display the
   message from the client, and send a response back to the client.


<!--
simple-netcat-in-rust video
Source: https://github.com/nazmulidris/developerlife.com/issues/3
-->
> Here's a video of the app that we are going to build in action.
> <video width="100%" controls>
>   <source src="https://github.com/nazmulidris/developerlife.com/assets/2966499/ffe83b3e-6997-4afc-bdf3-5d867f995611" type="video/mp4"/>
> </video>

> You can find the finished source code for this tutorial
> [here](https://github.com/nazmulidris/rust-scratch/tree/main/rtelnet).

## Add dependencies to Cargo.toml
<a id="markdown-add-dependencies-to-cargo.toml" name="add-dependencies-to-cargo.toml"></a>

Let's create a new project by running `cargo create --bin rtelnet`. Then we will add the
following dependencies to our `Cargo.toml` file.

```toml
# Command line argument parsing.
clap = { version = "4.4.13", features = ["derive"] }

# Pretty logging.
femme = { version = "2.2.1" }
log = { version = "0.4.20" }

# Colorization and ANSI escape sequence codes.
r3bl_tui = { version = "0.5.1" }
r3bl_ansi_color = { version = "0.6.9" }
```

## Configure clap to parse command line arguments
<a id="markdown-configure-clap-to-parse-command-line-arguments" name="configure-clap-to-parse-command-line-arguments"></a>

This Rust app has a single binary, and depending on the command line arguments, it will behave
either as a client or server. We will use the `clap` crate to parse the command line arguments.

We will configure `clap` so that the following commands will work:

```bash
cargo run server
cargo run client
```

We want to allow the user to specify the following options and chose their own address and
port. If the user does not specify any options, we will use the default values. The
default value for `--address` is `127.0.0.1`, and the default value for `--port` is
`3000`.

```bash
cargo run server --address 127.0.0.1 --port 8080
cargo run server --address 127.0.0.1
cargo run server --port 8080

cargo run client --address 127.0.0.1 --port 8080
cargo run client --address 127.0.0.1
cargo run client --port 8080
```

Let's also add an option that we can use to disable log output to stdout. By default, we
will log to stdout. But if the user specifies the `--log-disable` flag, then we disable
all log output.

Here's the clap configuration that gives us this behavior.

```rust
use clap::{Parser, Subcommand};

pub use defaults::*;
mod defaults {
    use super::*;

    pub const DEFAULT_PORT: u16 = 3000;
    pub const DEFAULT_ADDRESS: &str = "127.0.0.1";
}

pub use clap_config::*;
mod clap_config {
    use super::*;

    #[derive(Parser, Debug)]
    pub struct CLIArg {
        /// IP Address to connect to or start a server on
        #[clap(long, short, default_value = DEFAULT_ADDRESS, global = true)]
        pub address: IpAddr,

        /// TCP Port to connect to or start a server on
        #[clap(long, short, default_value_t = DEFAULT_PORT, global = true)]
        pub port: u16,

        /// Logs to stdout by default, set this flag to disable it
        #[clap(long, short = 'd', global = true)]
        pub log_disable: bool,

        /// The subcommand to run
        #[clap(subcommand)]
        pub subcommand: CLISubcommand,
    }

    #[derive(Subcommand, Debug)]
    pub enum CLISubcommand {
        /// Start a server on the given address and port
        Server,
        /// Connect to a server running on the given address and port
        Client,
    }
}
```

## Create the client
<a id="markdown-create-the-client" name="create-the-client"></a>

Let's start with the simpler of the two, the client. We will use `std::net::TcpStream` to
create a TCP socket client. We will need an IP address and port in order to make a TCP
connection. And to run the client we will need to run the following command:

```bash
cargo run client
```

Here's what the main function of our app looks like:

```rust
fn main() {
    println!("Welcome to rtelnet");

    let cli_arg = CLIArg::parse();
    let address = cli_arg.address;
    let port = cli_arg.port;
    let socket_address = format!("{}:{}", address, port);

    if !cli_arg.log_disable {
        femme::start()
    }

    match match cli_arg.subcommand {
        CLISubcommand::Server => start_server(socket_address),
        CLISubcommand::Client => start_client(socket_address),
    } {
        Ok(_) => {
            println!("Program exited successfully");
        }
        Err(error) => {
            println!("Program exited with an error: {}", error);
        }
    }
}
```

The function that performs the client logic looks like this.

```rust
fn start_client(socket_address: String) -> IOResult<()> {
    log::info!("Start client connection");
    let tcp_stream = TcpStream::connect(socket_address)?;
    let (mut reader, mut writer) = (BufReader::new(&tcp_stream), BufWriter::new(&tcp_stream));

    // Client loop.
    loop {
        // Read user input.
        let outgoing = {
            let mut it = String::new();
            let _ = stdin().read_line(&mut it)?;
            it.as_bytes().to_vec()
        };

        // Tx user input to writer.
        let _ = writer.write(&outgoing)?;
        writer.flush()?;

        // Rx response from reader.
        let incoming = {
            let mut it = vec![];
            let _ = reader.read_until(b'\n', &mut it);
            it
        };

        let display_msg = String::from_utf8_lossy(&incoming);
        let display_msg = display_msg.trim();

        let reset = SgrCode::Reset.to_string();
        let display_msg = format!("{}{}", display_msg, reset);
        println!("{}", display_msg);

        // Print debug.
        log::info!(
            "-> Tx: '{}', size: {} bytes{}",
            String::from_utf8_lossy(&outgoing).trim(),
            outgoing.len(),
            reset,
        );
        log::info!(
            "<- Rx: '{}', size: {} bytes{}",
            String::from_utf8_lossy(&incoming).trim(),
            incoming.len(),
            reset,
        );
    }
}
```

Here are a few things to note about the client code:
- We create a `BufReader` and `BufWriter` for the `TcpStream` that we get from
  `TcpStream::connect()`. This is because we want to read and write data in chunks, and
  not one byte at a time, for performance reasons, and to simplify the logic. These two
  structs allow us to read and write data very easily in chunks that are delimited by new
  lines (`\n`).
- There's a client loop that runs forever. This is because we want to keep the client
  running forever, so that the user can type a message and send it to the server, and
  receive a response from the server.
- How do we exit this infinite client loop? Only when the user presses `Ctrl+C` will the
  client exit. The [default behavior](https://g.co/bard/share/ac5d3480eb37) for Rust is to
  exit the process when this happens. This drops the TCP connection causing the server to exit as
  well.
- When we read data from user input, it too uses a stream, not a `TcpStream`, but the
  `stdin()` stream. This behaves very similarly to the `TcpStream` stream. We can read
  data from it in chunks delimited by new lines (`\n`). Once the user types a message and
  presses enter that message, eg: `"hi"`, and the new line are stored in the `it`
  variable, eg: `"hi\n"`. We then convert the String into a byte array, eg: `[104, 105,
  10]`, and then convert it into a `Vec<u8>`. We then send it to the server. We must call
  `flush()` since `BufWriter` buffers the data and does not send it to the server until we
  call `flush()` for IO performance reasons. It queue's up the data and sends it in
  chunks, instead of sending it one byte at a time.
- Reading there response from the server is similar to reading it from `stdin()` as we
  have already seen. The main thread blocks until there is some data that can be read from
  the server. Or if the TCP connection errors out in any way (timeout or closed by various
  means). If there is an error, then this function returns an error, and the main thread
  exits. Note that the `start_client()` function itself returns an `IOResult`, which is
  just a type alias for `pub type IOResult<T> = std::io::Result<T>;`. The error handling
  is quite simple. If there is an error, we print it out and exit the program.
- We read the data from the server into the `incoming` variable using
  `reader.read_until(b'\n', &mut it);)`. This is because we expect the server to send us
  data that is terminated by a new line (`\n`). So we read the data until we encounter a
  new line. This is a blocking call, so the main thread blocks until there is some data
  that can be read from the server. Note that the `\n` is included in `incoming` variable,
  much like it is in `stdin()`.
  - We use this function `String::from_utf8_lossy(&incoming);` to convert this `incoming:
    Vec<u8>` into a `String`. We call `.trim()` on the String, so that the trailing `\n`
    is removed.
  - Note that `trim()` returns a `&str`, so if you want to turn it into a String, you have
    to run in through this expression `format!("{}",
    String::from_utf8_lossy(&incoming).trim())` function.
- This is a pedagogical example and this algorithm is somewhat contrived to demonstrate
  how to send bytes back and forth between client and server and have them interpret the
  bytes in a certain way. A more formalized version of this "dance" is called a
  "protocol", eg: HTTP, SMTP, etc.
- In the final step of the `loop`, after the incoming data has been read from the server,
  we print it out to the terminal. Since the server will send us ANSI escape sequence
  codes that colorize the text that we print to the terminal, we want to reset the color
  after we print the text, so it does not pollute our `stdout()` output stream. We use the
  [`SgrCode::Reset` code to reset the
  color](https://github.com/r3bl-org/r3bl-open-core/blob/main/ansi_color/src/ansi_escape_codes.rs#L23)
  of the text that we print to the terminal.

## Create the server
<a id="markdown-create-the-server" name="create-the-server"></a>

Now let's create the server. We will use `std::net::TcpListener` to create a TCP socket
server. We will need an IP address and port in order to make a TCP connection. To run the
server we will need to run the following command:

```bash
cargo run server
```

The server code is very similar to the client code. We need a server loop that runs
forever, and we need to first read (blocking until there is any data available) and then
write data in chunks delimited by new lines (`\n`). When there is no data available to
read `EOF` is reached on the reader (aka, input TCP stream) then we break out of this loop
and exit. When data comes in (delimited by `\n`) we process it and send a response back to
the client. We process this data by applying a [lolcat
effect](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/color_wheel/color_wheel_struct.rs#L457)
on it, so the client will get a very colorful version of whatever text message that they
sent to the server.

One more thing we will see when implementing the server is having to spawn multiple
threads to handle each incoming client connection. While the client is a single threaded
app, the server is a multi-threaded app. The client is only concerned w/ a single TCP
connection, but the server is concerned with multiple TCP connections, each connection
emanating from a different client process running the `cargo run client` and creating a
new OS process. Fortunately Rust is built for fearless concurrency and parallelism from
the ground up.

Here's the main function of our server app:

```rust
pub fn start_server(socket_address: String) -> IOResult<()> {
    let tcp_listener = TcpListener::bind(socket_address)?;
    // Server connection accept loop.
    loop {
        log::info!("Waiting for a incoming connection...");
        let (tcp_stream, ..) = tcp_listener.accept()?; // This is a blocking call.

        // Spawn a new thread to handle this connection.
        thread::spawn(|| match handle_connection(tcp_stream) {
            Ok(_) => {
                log::info!("Successfully closed connection to client...");
            }
            Err(_) => {
                log::error!("Problem with client connection...");
            }
        });
    }
}
```

Here are a few things to note about the server code:
- We are using `IOResult` just like the client code. There are frequent calls to the `?`
  operator, which is shorthand for matching on the `Result` and returning early if there's
  an error. This is rudimentary error handling, and its good enough for this pedagogical
  example. Note that even in this pedagogical example, we don't use the `unwrap()` method
  which will induce a panic if there's an error. We always use the `?` operator, which
  will return early if there's an error. It isn't a good idea to get into the habit of
  using `unwrap()` outside of tests. These habits are hard to break once they're formed.
  You can even add the following
  [`#![warn(clippy::unwrap_in_result)]`](https://rust-lang.github.io/rust-clippy/master/index.html#/unwrap_used)
  in the top level module of your project to have the compiler warn you if you use
  `unwrap()` outside of tests. Here's an
  [example](https://github.com/r3bl-org/r3bl-open-core/blob/main/ansi_color/src/lib.rs#L171).
- The first thing the server has to do is reserve a port on the given address. This is called
  binding, and we do it using `TcpListener::bind(socket_address)?;`. This does not start a server
  yet. It just reserves a port on the given address, assuming that it is available. If some other
  process has already bound to that port, then this will return an error.
- Once we have a `TcpListener` instance, we can call `accept()` on it to start listening
  for incoming connections. This is a blocking call, so the main thread blocks until there
  is an incoming connection. Once there is an incoming connection, we get a `TcpStream`
  instance, which we can use to read and write data to the client. This is a blocking
  call. Which means that the main thread won't be able to do anything else, like process
  other incoming connections, while it is waiting here, for a connection to come in.
- This is why we use `thread::spawn()` to create a new thread and have it handle the
  incoming connection. We spawn a new thread for each incoming connection. This is [not a
  scalable solution](https://g.co/bard/share/74f433bad400), but it is good enough for this
  pedagogical example. We will learn about more scalable solutions in a the [Write a
  simple TCP chat server in Rust]({{ '/2024/01/13/write-simple-chat-server-in-rust/' |
  relative_url}}) tutorial.

Now, let's look at the `handle_connection()` function that is called by the spawned
thread. This is the function that handles the incoming connection from the client. And it
defines our "protocol", along with the client code. We aren't using any formalized
protocol like HTTP or SMTP. We are just sending bytes back and forth between the client
and server, and interpreting them in a certain way, which is our informal protocol. This
code is very similar to the client side code, including the `loop` and the `BufReader` and
`BufWriter` structs. And even looking for `EOF` to break out of the loop. Except that we
don't block on `stdin()` for input here.

```rust
fn handle_connection(tcp_stream: TcpStream) -> IOResult<()> {
    log::info!("Start handle connection");

    let reader = &mut BufReader::new(&tcp_stream);
    let write = &mut BufWriter::new(&tcp_stream);

    // Process client connection loop.
    loop {
        let mut incoming: Vec<u8> = vec![];

        // Read from reader.
        let num_bytes_read = reader.read_until(b'\n', &mut incoming)?;

        // Check for EOF. The stream is closed.
        if num_bytes_read == 0 {
            break;
        }

        // Process.
        let outgoing = process(&incoming);

        // Write to writer.
        write.write(&outgoing)?;
        let _ = write.flush()?;

        // Print debug.
        log::info!("-> Rx(bytes) : {:?}", &incoming);
        log::info!(
            "-> Rx(string): '{}', size: {} bytes",
            String::from_utf8_lossy(&incoming).trim(),
            incoming.len(),
        );
        log::info!(
            "<- Tx(string): '{}', size: {} bytes",
            String::from_utf8_lossy(&outgoing).trim(),
            outgoing.len()
        );
    }

    log::info!("End handle connection - connection closed");

    Ok(())
}
```

Finally, let's look at the `process()` function that takes the incoming bytes to the
outgoing bytes. This is where we add some fun and color and flair to our app. We colorize
the incoming bytes using a lolcat effect and send it back to the client.

```rust
use r3bl_tui::ColorWheel;

fn process(incoming: &Vec<u8>) -> Vec<u8> {
    // Convert incoming to String, and remove any trailing whitespace (includes newline).
    let incoming = String::from_utf8_lossy(incoming);
    let incoming = incoming.trim();

    // Prepare outgoing payload.
    let outgoing = incoming.to_string();

    // Colorize it w/ a gradient.
    let outgoing = ColorWheel::lolcat_into_string(&outgoing);

    // Generate outgoing response. Add newline to the end of output (so client can process it).
    let outgoing = format!("{}\n", outgoing);

    // Return outgoing payload.
    outgoing.as_bytes().to_vec()
}
```

## Next steps
<a id="markdown-next-steps" name="next-steps"></a>

Now that you have a handle on the basics of writing a simple netcat client and server, you
can read [this tutorial]({{ '/2024/01/13/write-simple-chat-server-in-rust/' |
relative_url}}) to learn more about creating a more advanced TCP server that netcat,
telnet, or PuTTY clients can connect to, in order to have multiple client apps chat with
each other.
