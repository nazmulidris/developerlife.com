---
title: "How to use Ockam Routing (with the Rust library) to build end-to-end channels"
author: Nazmul Idris
date: 2023-08-04 15:00:00+00:00
excerpt: |
  A guide on how to use Ockam Routing, using the Rust library, to secure your apps by building
  end-to-end channels. It is to get us thinking about security when building apps
  and consider the "who and where" for the data that is sent and received by our apps.
layout: post
categories:
  - Rust
---

<!--
    This is to ensure that search engines don’t get mad about duplication, since the original
    article is posted on ockam.io.
-->
<link rel="canonical" href="https://www.ockam.io/blog/routing" />

<img class="post-hero-image" src="{{ 'assets/ockam.svg' | relative_url }}"/>

<!-- TOC -->

- [Mitigating risk](#mitigating-risk)
- [Our journey](#our-journey)
- [Let's dive in](#lets-dive-in)
- [Simple example](#simple-example)
- [Complex example](#complex-example)
  - [Initiator node](#initiator-node)
  - [Middle node](#middle-node)
  - [Responder node](#responder-node)
- [Next steps](#next-steps)

<!-- /TOC -->

[Ockam](https://github.com/build-trust/ockam) is a suite of programming libraries, command
line tools, and managed cloud services to orchestrate end-to-end encryption, mutual
authentication, key management, credential management, and authorization policy
enforcement &mdash; all at massive scale. Ockam's end-to-end
[secure channels](https://docs.ockam.io/reference/command/secure-channels) guarantee authenticity,
integrity, and confidentiality of all data-in-motion at the application layer.

One of the key features that makes this possible is
[Ockam Routing](https://docs.ockam.io/reference/command/routing#routing).
Routing allows us to create secure channels over multi-hop, multi-protocol routes which
can span various network topologies (servers behind NAT firewalls with no external ports
open, etc) and transport protocols (TCP, UDP, WebSockets, BLE, etc).

In this blog post we will explore the Ockam Rust Library and see how routing works in Ockam.
We will work with Rust code and look at some code examples that demonstrate the simple
case, and more advanced use cases.

## Mitigating risk
<a id="markdown-mitigating-risk" name="mitigating-risk"></a>

Before we get started, let's quickly discuss the pitfalls of using existing approaches to
securing communications within applications. Security is not something that most of us
think about when we are building systems and are focused on getting things working and
shipping.

Traditional secure communication implementations are typically tightly coupled with
transport protocols in a way that all their security is limited to the length and duration
of one underlying transport connection.

1. For example, most TLS implementations are tightly coupled with the underlying TCP
   connection. If your application's data and requests travel over two TCP connection hops
   (TCP → TCP), then all TLS guarantees break at the bridge between the two networks. This
   bridge, gateway, or load balancer then becomes a point of weakness for application
   data.
2. Traditional secure communication protocols are also unable to protect your
   application's data if it travels over multiple different transport protocols. They
   can't guarantee data authenticity or data integrity if your application's communication
   path is UDP → TCP or BLE → TCP.

In other words using traditional secure communication implementations you may be opening
the doors to losing trust in the data that your apps are working on. Here are some aspects
of your apps that may be at risk:

1. Lack of trust in the data your app receives.
   - Who sent it to my app?
   - Is it actually the data they sent my app?
   - Missing authentication, data integrity.
2. Lack of trust in the data your app sends.
   - Who am I sending the data to?
   - Would someone else, other than them, be able to see it?

## Our journey
<a id="markdown-our-journey" name="our-journey"></a>

In this blog post we will create two examples of Ockam nodes communicating with each other
using Ockam Routing and Ockam Transports. We will use the Rust library to create these Ockam
nodes and setup routing. Ockam Routing and transports enable other
Ockam protocols to provide end-to-end guarantees like trust, security, privacy, reliable
delivery, and ordering at the application layer.

- *Ockam Routing*: is a simple and lightweight message-based protocol that makes it possible to
  bidirectionally exchange messages over a large variety of communication topologies: TCP ->
  TCP or TCP -> TCP -> TCP or BLE -> UDP -> TCP or BLE -> TCP -> TCP or TCP -> Kafka -> TCP
  or any other topology you can imagine.
- *Ockam Transports*: adapt Ockam Routing to various transport protocols.

An Ockam node is any running application that can communicate with other applications
using various Ockam protocols like
[Routing, Relays, and Portals](https://docs.ockam.io/reference/command/advanced-routing),
Secure Channels, etc.

An Ockam node can be defined as any independent process which provides an API supporting
the Ockam Routing protocol. We can create Ockam nodes using the
[Ockam command line interface (CLI)](https://docs.ockam.io/reference/command) (`ockam` command)
or using various Ockam programming libraries like our Rust and Elixir libraries. We will
be using the Rust library in this blog post.

## Let's dive in
<a id="markdown-let's-dive-in" name="let's-dive-in"></a>

<Alert status='info'>
  To get started please follow
  [this guide](https://docs.ockam.io/reference/libraries/rust#introduction) to get the Rust toolchain setup
  on your machine along with an empty project.
  1. The empty project is named `hello_ockam`.
  2. This will be the starting point for all our examples in this blog post.
</Alert>

## Simple example
<a id="markdown-simple-example" name="simple-example"></a>

For our first example, we will create a simple Ockam node that will send a message over
some hops (in the same node) to a worker (in the same node) that just echoes the message
back. There are no TCP transports involved and all the messages are being passed back and
forth inside the same node. This will give us a feel for building workers and routing at a
basic level.

When a worker is started on a node, it is given one or more addresses. The node
maintains a mailbox for each address and whenever a message arrives for a specific address
it delivers that message to the corresponding registered worker.

<Alert status='info'>
  For more information on creating nodes and workers using the Rust library, please refer to this
  [guide](https://docs.ockam.io/reference/libraries/rust/nodes).
</Alert>

We will need to create a Rust source file with a `main()` program, and two other Rust
source files with two workers: `Hopper` and `Echoer`. We can then send a string message
and see if we can get it echoed back.

Before we begin let's consider routing. When we send a message inside of a node it
carries with it 2 metadata fields, `onward_route` and `return_route`, where a `route` is
simply a list of `addresses`. Each worker gets an `address` in a node.

So, if we wanted to send a message from the `app` address to the `echoer` address, with 3
hops in the middle, we can build a route like the following.

```text
┌───────────────────────┐
│  Node 1               │
├───────────────────────┤
│  ┌────────────────┐   │
│  │ Address:       │   │
│  │ 'app'          │   │
│  └─┬────────────▲─┘   │
│  ┌─▼────────────┴─┐   │
│  │ Address:       │   │
│  │ 'hopper1..3'   │x3 │
│  └─┬────────────▲─┘   │
│  ┌─▼────────────┴─┐   │
│  │ Address:       │   │
│  │ 'echoer'       │   │
│  └────────────────┘   │
└───────────────────────┘
```

Here's the Rust code to build this route.

```rust
/// Send a message to the echoer worker via the "hopper1", "hopper2", and "hopper3" workers.
let route = route!["hopper1", "hopper2", "hopper3", "echoer"];
```

Let's add some source code to make this happen next. The first thing we will do is add one
more dependency to this empty `hello_ockam` project. The
[`colored` crate](https://docs.rs/colored/latest/colored/)
will give us colorized console output which will make the output from our examples so much
easier to read and understand.

```sh
cargo add colored
```

Then we add the `echoer` worker (in our `hello_ockam` project) by creating a new
`/src/echoer.rs` file and copy / pasting the following code in it.

```rust
use colored::Colorize;
use ockam::{Context, Result, Routed, Worker};

pub struct Echoer;

/// When a worker is started on a node, it is given one or more addresses. The node
/// maintains a mailbox for each address and whenever a message arrives for a specific
/// address it delivers that message to the corresponding registered worker.
///
/// Workers can handle messages from other workers running on the same or a different
/// node. In response to a message, an worker can: make local decisions, change its
/// internal state, create more workers, or send more messages to other workers running on
/// the same or a different node.
#[ockam::worker]
impl Worker for Echoer {
    type Context = Context;
    type Message = String;

    async fn handle_message(&mut self, ctx: &mut Context, msg: Routed<String>) -> Result<()> {
        // Echo the message body back on its return_route.
        let addr_str = ctx.address().to_string();
        let msg_str = msg.as_body().to_string();
        let new_msg_str = format!("👈 echo back: {}", msg);

        // Formatting stdout output.
        let lines = [
            format!("📣 'echoer' worker → Address: {}", addr_str.bright_yellow()),
            format!("    Received: '{}'", msg_str.green()),
            format!("    Sent: '{}'", new_msg_str.cyan()),
        ];
        lines
            .iter()
            .for_each(|line| println!("{}", line.white().on_black()));

        ctx.send(msg.return_route(), new_msg_str).await
    }
}
```

Next we add the `hopper` worker (in our `hello_ockam` project) by creating a new
`/src/hopper.rs` file and copy / pasting the following code in it.

Note how this worker manipulates the `onward_route` & `return_route` fields of the message
to send it to the next hop. We will actually see this in the console output when we run
this code soon.

```rust
use colored::Colorize;
use ockam::{Any, Context, Result, Routed, Worker};

pub struct Hopper;

#[ockam::worker]
impl Worker for Hopper {
    type Context = Context;
    type Message = Any;

    /// This handle function takes any incoming message and forwards. it to the next hop
    /// in it's onward route.
    async fn handle_message(&mut self, ctx: &mut Context, msg: Routed<Any>) -> Result<()> {
        // Cast the msg to a Routed<String>
        let msg: Routed<String> = msg.cast()?;

        let msg_str = msg.to_string().white().on_bright_black();
        let addr_str = ctx.address().to_string().white().on_bright_black();

        // Some type conversion.
        let mut message = msg.into_local_message();
        let transport_message = message.transport_mut();

        // Remove my address from the onward_route.
        let removed_address = transport_message.onward_route.step()?;
        let removed_addr_str = removed_address
            .to_string()
            .white()
            .on_bright_black()
            .strikethrough();

        // Formatting stdout output.
        let lines = [
            format!("🐇 'hopper' worker → Addr: '{}'", addr_str),
            format!("    Received: '{}'", msg_str),
            format!("    onward_route -> remove: '{}'", removed_addr_str),
            format!("    return_route -> prepend: '{}'", addr_str),
        ];
        lines
            .iter()
            .for_each(|line| println!("{}", line.black().on_yellow()));

        // Insert my address at the beginning return_route.
        transport_message
            .return_route
            .modify()
            .prepend(ctx.address());

        // Send the message on its onward_route.
        ctx.forward(message).await
    }
}
```

And finally let's add a `main()` to our `hello_ockam` project. This will be the entry
point for our example.

<Alert status='info'>
  When a new node starts and calls an `async` `main` function, it turns that function into a
  worker with an address of `app`. This makes it easy to send and receive messages from the
  `main` function (i.e the `app` worker).
</Alert>

Create an empty file `/examples/03-routing-many.hops.rs` (note this is in the `examples/`
folder and not `src/` folder like the workers above).

```rust
use colored::Colorize;
use hello_ockam::{Echoer, Hopper};
use ockam::{node, route, Context, Result};

#[rustfmt::skip]
const HELP_TEXT: &str =r#"
┌───────────────────────┐
│  Node 1               │
├───────────────────────┤
│  ┌────────────────┐   │
│  │ Address:       │   │
│  │ 'app'          │   │
│  └─┬────────────▲─┘   │
│  ┌─▼────────────┴─┐   │
│  │ Address:       │   │
│  │ 'hopper1..3'   │x3 │
│  └─┬────────────▲─┘   │
│  ┌─▼────────────┴─┐   │
│  │ Address:       │   │
│  │ 'echoer'       │   │
│  └────────────────┘   │
└───────────────────────┘
"#;

/// This node routes a message through many hops.
#[ockam::node]
async fn main(ctx: Context) -> Result<()> {
    println!("{}", HELP_TEXT.green());

    print_title(vec![
        "Run a node w/ 'app', 'echoer' and 'hopper1', 'hopper2', 'hopper3' workers",
        "then send a message over 3 hops",
        "finally stop the node",
    ]);

    // Create a node with default implementations.
    let mut node = node(ctx);

    // Start an Echoer worker at address "echoer".
    node.start_worker("echoer", Echoer).await?;

    // Start 3 hop workers at addresses "hopper1", "hopper2" and "hopper3".
    node.start_worker("hopper1", Hopper).await?;
    node.start_worker("hopper2", Hopper).await?;
    node.start_worker("hopper3", Hopper).await?;

    // Send a message to the echoer worker via the "hopper1", "hopper2", and "hopper3" workers.
    let route = route!["hopper1", "hopper2", "hopper3", "echoer"];
    let route_msg = format!("{:?}", route);
    let msg = "Hello Ockam!";
    node.send(route, msg.to_string()).await?;

    // Wait to receive a reply and print it.
    let reply = node.receive::<String>().await?;

    // Formatting stdout output.
    let lines = [
        "🏃 Node 1 →".to_string(),
        format!("    sending: {}", msg.green()),
        format!("    over route: {}", route_msg.blue()),
        format!("    and receiving: '{}'", reply.purple()), // Should print "👈 echo back:  Hello Ockam!"
        format!("    then {}", "stopping".bold().red()),
    ];
    lines
        .iter()
        .for_each(|line| println!("{}", line.black().on_white()));

    // Stop all workers, stop the node, cleanup and return.
    node.stop().await
}

fn print_title(title: Vec<&str>) {
    let line = format!("🚀 {}", title.join("\n  → ").white());
    println!("{}", line.black().on_bright_black())
}
```

Now it is time to run our program to see what it does! 🎉

In your terminal app, run the following command. Note that `OCKAM_LOG=none` is used to
disable logging output from the Ockam library. This is done to make the output of the
example easier to read.

```sh
OCKAM_LOG=none cargo run --example 03-routing-many-hops
```

And you should see something like the following. Our example program creates multiple hop
workers (three `hopper` workers) between the `app` and the `echoer` and route our message
through them 🚀.

![Output from running 03-routing-many-hops]({{'assets/ockam-routing-1-images/03-routing-many-hops.png' | relative_url}})

## Complex example
<a id="markdown-complex-example" name="complex-example"></a>

<Alert status='info'>
  This example continues from the simple example above, we are going to reuse all the dependencies
  and workers in this example so please make sure to complete the [simple example](#simple-example)
  before working on this one.
</Alert>

In this example, we will introduce
[TCP transports](https://docs.ockam.io/reference/libraries/rust/routing)
in between the hops. Instead of passing messages around between workers in the same node,
we will spawn multiple nodes. Then we will have a few TCP transports (TCP socket client
and listener combos) that will connect the nodes.

An Ockam transport is a plugin for Ockam Routing. It moves Ockam Routing messages using a
specific transport protocol like TCP, UDP, WebSockets, Bluetooth, etc.

We will have three nodes:
1. `node_initiator`: The first node initiates sending the message over TCP to the middle
   node (port `3000`).
2. `node_middle`: Then middle node simply forwards this message on to the last node over
   TCP again (port `4000` this time).
3. `node_responder`: And finally the responder node receives the message and sends a reply
   back to the initiator node.

The following diagram depicts what we will build next. In this example all these nodes
are on the same machine, but they can easy just be nodes on different machines.

```text
┌──────────────────────┐
│node_initiator        │
├──────────────────────┤
│ ┌──────────────────┐ │
│ │Address:          │ │     ┌───────────────────────────┐
│ │'app'             │ │     │node_middle                │
│ └──┬────────────▲──┘ │     ├───────────────────────────┤
│ ┌──▼────────────┴──┐ │     │ ┌──────────────────┐      │
│ │TCP transport     └─┼─────┼─►TCP transport     │      │
│ │connect to 3000   ◄─┼─────┼─┐listening on 3000 │      │
│ └──────────────────┘ │     │ └──┬────────────▲──┘      │
└──────────────────────┘     │ ┌──▼────────────┴───────┐ │
                             │ │Address:               │ │   ┌──────────────────────┐
                             │ │'forward_to_responder' │ │   │node_responder        │
                             │ └──┬────────────▲───────┘ │   ├──────────────────────┤
                             │ ┌──▼────────────┴──┐      │   │ ┌──────────────────┐ │
                             │ │TCP transport     └──────┼───┼─►TCP transport     │ │
                             │ │connect to 4000   ◄──────┼───┼─┐listening on 4000 │ │
                             │ └──────────────────┘      │   │ └──┬────────────▲──┘ │
                             └───────────────────────────┘   │ ┌──▼────────────┴──┐ │
                                                             │ │Address:          │ │
                                                             │ │'echoer'          │ │
                                                             │ └──────────────────┘ │
                                                             └──────────────────────┘
```

Let's start by creating a new file `/examples/04-routing-over-two-transport-hops.rs` (in
the `/examples/` folder and not `/src/` folder). Then copy / paste the following code in
that file.

```rust
use colored::Colorize;
use hello_ockam::{Echoer, Forwarder};
use ockam::{
    node, route, AsyncTryClone, Context, Result, TcpConnectionOptions, TcpListenerOptions,
    TcpTransportExtension,
};

#[rustfmt::skip]
const HELP_TEXT: &str =r#"
┌──────────────────────┐
│node_initiator        │
├──────────────────────┤
│ ┌──────────────────┐ │
│ │Address:          │ │     ┌───────────────────────────┐
│ │'app'             │ │     │node_middle                │
│ └──┬────────────▲──┘ │     ├───────────────────────────┤
│ ┌──▼────────────┴──┐ │     │ ┌──────────────────┐      │
│ │TCP transport     └─┼─────┼─►TCP transport     │      │
│ │connect to 3000   ◄─┼─────┼─┐listening on 3000 │      │
│ └──────────────────┘ │     │ └──┬────────────▲──┘      │
└──────────────────────┘     │ ┌──▼────────────┴───────┐ │
                             │ │Address:               │ │   ┌──────────────────────┐
                             │ │'forward_to_responder' │ │   │node_responder        │
                             │ └──┬────────────▲───────┘ │   ├──────────────────────┤
                             │ ┌──▼────────────┴──┐      │   │ ┌──────────────────┐ │
                             │ │TCP transport     └──────┼───┼─►TCP transport     │ │
                             │ │connect to 4000   ◄──────┼───┼─┐listening on 4000 │ │
                             │ └──────────────────┘      │   │ └──┬────────────▲──┘ │
                             └───────────────────────────┘   │ ┌──▼────────────┴──┐ │
                                                             │ │Address:          │ │
                                                             │ │'echoer'          │ │
                                                             │ └──────────────────┘ │
                                                             └──────────────────────┘
"#;

#[ockam::node]
async fn main(ctx: Context) -> Result<()> {
    println!("{}", HELP_TEXT.green());

    let ctx_clone = ctx.async_try_clone().await?;
    let ctx_clone_2 = ctx.async_try_clone().await?;

    let mut node_responder = create_responder_node(ctx).await.unwrap();

    let mut node_middle = create_middle_node(ctx_clone).await.unwrap();

    create_initiator_node(ctx_clone_2).await.unwrap();

    node_responder.stop().await.ok();
    node_middle.stop().await.ok();

    println!(
        "{}",
        "App finished, stopping node_responder & node_middle".red()
    );

    Ok(())
}

fn print_title(title: Vec<&str>) {
    let line = format!("🚀 {}", title.join("\n  → ").white());
    println!("{}", line.black().on_bright_black())
}
```

This code won't actually compile, since there are 3 functions missing from this source
file. We are just adding this file first in order to stage the rest of the code we will
write next.

This `main()` function creates the three nodes like we see in the diagram above, and it
also stops them after the example is done running.

### Initiator node
<a id="markdown-initiator-node" name="initiator-node"></a>

So let's write the function that creates the initiator node first. Copy the following into
the source file we created earlier (`/examples/04-routing-over-two-transport-hops.rs`),
and paste it below the existing code there:

```rust
/// This node routes a message, to a worker on a different node, over two TCP transport
/// hops.
async fn create_initiator_node(ctx: Context) -> Result<()> {
    print_title(vec![
        "Create node_initiator that routes a message, over 2 TCP transport hops, to 'echoer' worker on node_responder",
        "stop",
    ]);

    // Create a node with default implementations.
    let mut node = node(ctx);

    // Initialize the TCP transport.
    let tcp_transport = node.create_tcp_transport().await?;

    // Create a TCP connection to the middle node.
    let connection_to_middle_node = tcp_transport
        .connect("localhost:3000", TcpConnectionOptions::new())
        .await?;

    // Send a message to the "echoer" worker, on a different node, over two TCP hops. Wait
    // to receive a reply and print it.
    let route = route![connection_to_middle_node, "forward_to_responder", "echoer"];
    let route_str = format!("{:?}", route);
    let msg = "Hello Ockam!";
    let reply = node
        .send_and_receive::<String>(route, msg.to_string())
        .await?;

    // Formatting stdout output.
    let lines = [
        "🏃 node_initiator →".to_string(),
        format!("    sending: {}", msg.green()),
        format!("    over route: '{}'", route_str.blue()),
        format!("    and received: '{}'", reply.purple()), // Should print "👈 echo back:  Hello Ockam!"
        format!("    then {}", "stopping".bold().red()),
    ];
    lines
        .iter()
        .for_each(|line| println!("{}", line.black().on_white()));

    // Stop all workers, stop the node, cleanup and return.
    node.stop().await
}
```

This (initiator) node will send a message to the responder using the following route.


```rust
let route = route![connection_to_middle_node, "forward_to_responder", "echoer"];
```

<Alert status='info'>
  Note the use of a mix of TCP transport routes as well as addresses for other workers.
  Also note that this node does not have to be aware of the full topology of the network of
  nodes. It just knows that it has to jump over the TCP transport
  `connection_to_middle_node` and then have its message routed to `forward_to_responder`
  address followed by `echoer` address.
</Alert>

### Middle node
<a id="markdown-middle-node" name="middle-node"></a>

Let's create the middle node next, which will run the worker `Forwarder` on this address:
`forward_to_responder`.

Copy and paste the following into the source file we created above
(`/examples/04-routing-over-two-transport-hops.rs`).

- This middle node simply forwards whatever comes into its TCP listener (on `3000`) to
  port `4000`.
- This node has a `Forwarder` worker on address `forward_to_responder`, so that's how the
  initiator can reach this address specified in its route at the start of this example.

```rust
/// - Starts a TCP listener at 127.0.0.1:3000.
/// - This node creates a TCP connection to a node at 127.0.0.1:4000.
/// - Starts a forwarder worker to forward messages to 127.0.0.1:4000.
/// - Then runs forever waiting to route messages.
async fn create_middle_node(ctx: Context) -> Result<ockam::Node> {
    print_title(vec![
        "Create node_middle that listens on 3000 and forwards to 4000",
        "wait for messages until stopped",
    ]);

    // Create a node with default implementations.
    let node = node(ctx);

    // Initialize the TCP transport.
    let tcp_transport = node.create_tcp_transport().await?;

    // Create a TCP connection to the responder node.
    let connection_to_responder = tcp_transport
        .connect("127.0.0.1:4000", TcpConnectionOptions::new())
        .await?;

    // Create a Forwarder worker.
    node.start_worker(
        "forward_to_responder",
        Forwarder {
            address: connection_to_responder.into(),
        },
    )
    .await?;

    // Create a TCP listener and wait for incoming connections.
    let listener = tcp_transport
        .listen("127.0.0.1:3000", TcpListenerOptions::new())
        .await?;

    // Allow access to the Forwarder via TCP connections from the TCP listener.
    node.flow_controls()
        .add_consumer("forward_to_responder", listener.flow_control_id());

    // Don't call node.stop() here so this node runs forever.
    Ok(node)
}
```

### Responder node
<a id="markdown-responder-node" name="responder-node"></a>

Finally, we will create the responder node. This node will run the worker `echoer` which
actually echoes the message back to the initiator. Copy and paste the following into the
source file above (`/examples/04-routing-over-two-transport-hops.rs`).

- This node has an `Echoer` worker on address `echoer`, so that's how the initiator can
  reach this address specified in its route at the start of this example.

```rust
/// This node starts a TCP listener and an echoer worker. It then runs forever waiting for
/// messages.
async fn create_responder_node(ctx: Context) -> Result<ockam::Node> {
    print_title(vec![
        "Create node_responder that runs tcp listener on 4000 and 'echoer' worker",
        "wait for messages until stopped",
    ]);

    // Create a node with default implementations.
    let node = node(ctx);

    // Initialize the TCP transport.
    let tcp_transport = node.create_tcp_transport().await?;

    // Create an echoer worker.
    node.start_worker("echoer", Echoer).await?;

    // Create a TCP listener and wait for incoming connections.
    let listener = tcp_transport
        .listen("127.0.0.1:4000", TcpListenerOptions::new())
        .await?;

    // Allow access to the Echoer via TCP connections from the TCP listener.
    node.flow_controls()
        .add_consumer("echoer", listener.flow_control_id());

    Ok(node)
}
```

Let's run this example to see what it does 🎉.

In your terminal app, run the following command. Note that `OCKAM_LOG=none` is used to
disable logging output from the Ockam library. This is done to make the output of the
example easier to read.

```sh
cargo run --example 04-routing-over-two-transport-hops
```

This should produce output similar to the following. Our example program creates a route
that traverses multiple nodes and TCP transports from the `app` to the `echoer` and routes
our message through them 🚀.

![Output from running 04-routing-over-two-transport-hops]({{'assets/ockam-routing-1-images/04-routing-over-two-transport-hops.png' | relative_url}})

## Next steps
<a id="markdown-next-steps" name="next-steps"></a>

Ockam Routing and transports are extremely powerful and flexible. They are one of the
key features that enables Ockam Secure Channels to be implemented. By layering Ockam
Secure Channels and other protocols over Ockam Routing, we can provide end-to-end
guarantees over arbitrary transport topologies that span many networks and clouds.

In a future blog post we will be covering [Ockam Secure
Channels](https://docs.ockam.io/reference/command/secure-channels) and how they can be
used to provide end-to-end guarantees over arbitrary transport topologies. So stay tuned!

In the meantime here are some good jumping off points to learn more about Ockam:
- [Deep dive into Ockam Routing](https://docs.ockam.io/reference/libraries/rust/routing).
- Install [Ockam command line interface (CLI)](https://github.com/build-trust/ockam#install-ockam-command)
  (`ockam` command) on your computer and try to
  [create end-to-end encrypted communication](https://github.com/build-trust/ockam#end-to-end-encrypted-and-mutually-authenticated-communication)
  between two apps. That will give you a taste of the experience of using Ockam on the
  command line in addition to our Rust library.