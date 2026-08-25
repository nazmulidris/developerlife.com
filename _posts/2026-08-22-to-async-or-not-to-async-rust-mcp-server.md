---
title: "To Async or Not to Async: Building a Rust MCP Server for rust-analyzer"
author: Nazmul Idris
date: 2026-08-22 10:00:00+00:00
excerpt:
    "When I/O is involved, Rustaceans often instinctively reach for Tokio. While Tokio is
    a fantastic tool for the right use cases, it should not be used indiscriminately for
    every I/O based use case. This article explores why Tokio was deliberately omitted in
    r3bl-rust-analyzer-mcp-server in favor of a simple, synchronous 3-thread pipeline over
    stdio. It is a deep dive into architectural trade-offs, async-by-default dogma, and
    fit-for-purpose architecture."
layout: post
categories:
    - Rust
    - CLI
    - CC
    - CS
    - Server
    - AI-LLM
---

<!-- cspell:words rmcp ciresnave zeenix dexwritescode mpsc epoll kqueue proc mktoc -->
<!-- cspell:words deadlocks JSONRPC backtraces -->

<!-- BEGIN mktoc -->

- [Pragmatism Over Dogma](#pragmatism-over-dogma)
- [How We Got to "Async-by-Default"](#how-we-got-to-async-by-default)
- [1:1 Process Pipes vs. 1:N Network Servers](#11-process-pipes-vs-1n-network-servers)
    - [1. The End-to-End Flow](#1-the-end-to-end-flow)
    - [2. How MCP Layers Over LSP](#2-how-mcp-layers-over-lsp)
    - [3. No Need To Multiplex Over `stdio`](#3-no-need-to-multiplex-over-stdio)
    - [4. The Illusion of Async `stdio`](#4-the-illusion-of-async-stdio)
- [The 3-Thread Architecture](#the-3-thread-architecture)
    - [Thread 1: Main MCP Loop](#thread-1-main-mcp-loop)
    - [Thread 2: `stdout` Reader](#thread-2-stdout-reader)
    - [Thread 3: `stderr` Drainer](#thread-3-stderr-drainer)
    - [Request-Response Via `sync_channel(1)`](#request-response-via-sync_channel1)
- [Advantages](#advantages)
    - [Sub-Millisecond Cold Starts](#sub-millisecond-cold-starts)
    - [Transparent Stack Traces](#transparent-stack-traces)
    - [Deterministic Teardown](#deterministic-teardown)
- [Choosing the Right Tool](#choosing-the-right-tool)

<!-- END mktoc -->

## Pragmatism Over Dogma

When we build tools in Rust where I/O is involved, we might feel a strong pull toward
"async all the things". It is understandable that we may instinctively run
`cargo add tokio`, decorate the `main` function with `#[tokio::main]`, make all the
functions `async`, and add `.await` to the call sites.

I love both synchronous and asynchronous Rust. This article is not an ideological critique
of asynchronous Rust. This article is in support of using the right tool for the job, and
not the wrong one (even when that tool is our beloved Tokio).

As the author of [`r3bl_tui`], I have spent years building asynchronous foundations for
terminal applications. In `r3bl_tui`, everything from custom `readline` primitives and
asynchronous signal listeners to multi-producer event-driven render loops is built with
async Rust from the ground up to uphold the core invariant: **never block the main
thread**.

To achieve this, the `r3bl_tui` crate cleanly separates these responsibilities:

1. **Async Event Multiplexing (with Tokio Primitives)** - It relies on Tokio constructs
   (such as `tokio::select!`, asynchronous tasks, `mpsc` and `broadcast` channels) to
   multiplex high-frequency user inputs (e.g., keypresses, mouse drags, window resize
   events) and background worker streams concurrently without task starvation.
2. **Blocking I/O Isolation** via [Resilient Reactor Thread][RRT] (RRT) - Invoking
   blocking system calls (like reading raw `stdin`) directly on async executor threads
   would starve Tokio and freeze the terminal UI. So, I designed the **RRT pattern**. RRT
   wraps blocking I/O sources (and allows me to eliminate external dependencies like
   `crossterm`) and isolates them inside dedicated, self-healing OS threads that feed
   non-blocking broadcast channels into the async loop. This pattern is easily extensible
   to other blocking sources, modern completion engines like `io_uring`, and is even a
   good fit for in-process server use cases.

With that out of the way, here's the **"but"**. Great engineering is about **fit for
purpose**, not dogmatic conformity. Applying a high-concurrency async runtime designed for
web servers handling hundreds of thousands of concurrent TCP sockets to a 1:1 local
standard I/O pipe introduces [accidental complexity][cantrill-complexity] without
providing performance, readability, or maintainability benefits.

The motivation to write this article happened recently, after I built
[`r3bl-rust-analyzer-mcp-server`], a Model Context Protocol (MCP) server designed to
bridge AI / LLM coding agents (such as Google Antigravity, Claude Code, and Cursor) with
the [`rust-analyzer`] Language Server Protocol (LSP) subprocess. Why build yet another
crate to do this? Because a few existing Rust MCP server crates that I tried didn't work
with Antigravity, and some of them were consuming a lot of CPU and crashing.

> 📦 The `r3bl-rust-analyzer-mcp-server` crate is available on
> [crates.io][`r3bl-rust-analyzer-mcp-server`].

I made a deliberate (dare I say, counter-cultural) architectural choice and completely
omitted Tokio in favor of standard library OS threads and channels over `stdio`.

This article explores the engineering rationale behind that choice. We will examine the
mechanics of standard I/O pipes on Linux, macOS and Windows, contrast the 1:1 workload of
local AI / LLM coding agents against 1:N networked servers, and break down the simple
3-thread architecture that delivers the following benefits:

- Sub-millisecond cold starts (<2ms). Spawns instantly without the overhead of Tokio
  runtime initialization, thread-pool spin-up, or timer wheel setup.
- Eliminates [stream corruption][cancel-safe] caused by futures dropping mid-write at
  `.await` points and prevents orphaned zombie `rust-analyzer` processes.
- Easy to understand architecture and code. Control flow is linear, and the type system
  makes invalid states unrepresentable.

## How We Got to "Async-by-Default"

Anthropic released the [Model Context Protocol specification][mcp-spec] in November 2024,
soon after which they released the official Rust SDK [`rmcp`][rmcp].

By architecting `rmcp` around Tokio (`#[tokio::main]`, `tokio::io::{stdin, stdout}`, and
[async traits][async-trait]), Anthropic established a default pattern that future Rust MCP
crates would mimic.

All the open source _Rust MCP server for `rust-analyzer` (or generic LSP gateway)_ crates
that I was able to find have been built with Tokio, including:

- [`lsp-mcp`][lsp-mcp]: A generic LSP-to-MCP gateway built with Tokio.
- [`dexwritescode/rust-mcp`][dexwritescode]: A `rust-analyzer` MCP server built on Tokio.
- [`ciresnave/rust-analyzer-mcp-server`][ciresnave]: A `rust-analyzer` bridge on Tokio.
- [`zeenix/rust-analyzer-mcp`][zeenix]: A `rust-analyzer` bridge built on Tokio.

All of these binary crates are designed to run as local child processes communicating
strictly over `stdio`.

**So, why do they all use Tokio?**

Perhaps the authors of these crates implicitly accepted Anthropic's design choices as
correct, without critically examining them. Or perhaps the AI / LLM coding agents (used by
the authors to create these crates) blindly accepted Anthropic's choice. The power of
defaults? I have no way of knowing.

When the official reference SDK uses Tokio, it is easy for an entire ecosystem to assume
that an async runtime is a prerequisite for writing an MCP server.

**TL;DR:** An asynchronous runtime is the wrong tool for local standard I/O streams /
pipes. For 1:1 process pipes, synchronous threads are faster, simpler, and far more
reliable.

## 1:1 Process Pipes vs. 1:N Network Servers

To understand why synchronous threads are optimal for a local MCP server, we must look at
how an AI / LLM coding agent actually interacts with its tools (like the
`rust-analyzer-mcp-server` binary in the `r3bl-rust-analyzer-mcp-server` crate).

### 1. The End-to-End Flow

The complete interaction workflow (User -> AI / LLM Coding Agent -> MCP Server ->
`rust-analyzer`) consists of these steps:

1. **User Launches Agent**
    - The user starts their AI / LLM coding agent (such as Google Antigravity `agy`,
      Claude Code, Cursor, or VS Code) in a local folder containing a Rust project.
2. **Agent Configuration**
    - The user configures the agent to register `rust-analyzer-mcp-server` binary as a
      local tool provider (via its MCP configuration mechanism) and gives it a name like
      `rust-refactor`.
3. **User Prompts the Agent**
    - The user issues a prompt requiring Rust semantic analysis (e.g., _"Use rust-refactor
      to find all references to `MyStruct` and refactor its constructor"_).
4. **Agent Spawns Bridge Process**
    - To execute the requested tools, the AI / LLM coding agent spawns
      `rust-analyzer-mcp-server` as a dedicated 1:1 child process communicating over
      standard I/O (`stdin` and `stdout`).
5. **Bridge Translates MCP to LSP**
    - The MCP server receives JSON-RPC tool calls over `stdin`, converts them into LSP
      queries for `rust-analyzer`, and writes formatted responses to `stdout`:

```text
┌────────────────────────────────────────────────────────┐
│          HOST PROCESS: AI / LLM CODING AGENT           │
│            (Antigravity / VSCode / Claude)             │
└───────────────────────────┬────────────────────────────┘
                            │
        [Launches rust-analyzer-mcp-server binary]
              (1:1 dedicated child process)
                            │
     stdin / stdout (MCP: Newline-delimited JSON-RPC)
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                rust-analyzer-mcp-server                │
│   (3 OS threads: Main, stdout-reader, stderr-reader)   │
│                                                        │
│  1. Reads MCP JSON-RPC tool calls from stdin           │
│  2. Converts tool calls into LSP JSON-RPC queries      │
│  3. Writes LSP requests to rust-analyzer stdin         │
│  4. Receives LSP responses from background thread      │
│  5. Formats and writes MCP responses to stdout         │
└───────────────────────────┬────────────────────────────┘
                            │
            [Spawns rust-analyzer subprocess]
              (1:1 dedicated child process)
                            │
      stdin / stdout (LSP: Header-delimited JSON-RPC)
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│       LANGUAGE SERVER: rust-analyzer subprocess        │
│               (The Rust Language Server)               │
└────────────────────────────────────────────────────────┘
```

1. **Process Lifecycle:** The AI / LLM coding agent (e.g., Antigravity, Claude Code,
   Cursor) spawns `rust-analyzer-mcp-server` as a direct, dedicated child process for the
   duration of the editing session.
2. **Channel:** Communication occurs exclusively over standard OS anonymous pipes (`stdin`
   and `stdout`).

### 2. How MCP Layers Over LSP

The Model Context Protocol (MCP) does not define language-server-specific endpoints.
Instead, MCP provides generic JSON-RPC primitives:

1. **`initialize`:** Handshake and capability negotiation.
2. **`tools/list`:** Dynamic tool discovery via JSON Schemas.
3. **`tools/call`:** Generic tool execution request and response.

`rust-analyzer-mcp-server` serves as an **adapter**: it implements those standard MCP
endpoints on the outside and internally translates them into `rust-analyzer`'s Language
Server Protocol (LSP 3.17) queries.

#### Protocol Layering Flow

```text
┌────────────────────────────────────────────────────────┐
│               AI / LLM CODING AGENT (agy)              │
└───────────────────────────┬────────────────────────────┘
                            │
              1. "tools/list" (Standard MCP)
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                rust-analyzer-mcp-server                │
│                                                        │
│  Returns list of 10 tool schemas:                      │
│   • rust_analyzer_hover                                │
│   • rust_analyzer_definition                           │
│   • rust_analyzer_references                           │
│   • rust_analyzer_diagnostics                          │
│   • ...                                                │
└───────────────────────────┬────────────────────────────┘
                            │
              2. Agent injects tool schemas into LLM
                            │
              3. LLM decides: call "rust_analyzer_hover"
                            │
              4. "tools/call" (Standard MCP)
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                rust-analyzer-mcp-server                │
│                                                        │
│  Translates tools/call -> textDocument/hover (LSP)     │
└───────────────────────────┬────────────────────────────┘
                            │
              5. LSP JSON-RPC over stdio
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                 rust-analyzer subprocess               │
└────────────────────────────────────────────────────────┘
```

The sections below trace this execution flow chronologically:

1. Discovery (`tools/list`): The AI / LLM coding agent queries capabilities; our MCP
   server immediately replies with tool schemas that we define, without invoking
   `rust-analyzer`.
2. Tool Request (`tools/call`): The AI / LLM coding agent dispatches a tool execution
   request, e.g., `rust_analyzer_hover` with a file path and coordinates
   (`line: 42, character: 10`).
3. Bridge Translation (MCP -> LSP): Our MCP server translates the MCP tool call into an
   LSP query (`textDocument/hover`), writes it to `rust-analyzer`, and awaits the AST
   response.
4. Tool Response (`CallToolResult`): `rust-analyzer` produces the symbol information (with
   hover documentation and type signatures natively formatted in Markdown). Our MCP server
   packages this into a standard MCP `CallToolResult` and returns the JSON-RPC response to
   the AI / LLM coding agent with the matching request ID.

#### 1. Dynamic Tool Discovery (`tools/list`)

When the AI / LLM coding agent (e.g. `agy`) spawns our MCP server, it queries available
tools by sending an MCP `tools/list` request over `stdin`:

```json
{ "jsonrpc": "2.0", "id": 1, "method": "tools/list" }
```

> `rust-analyzer` is not used at all to produce this response. Because `rust-analyzer` is
> a pure LSP language server with zero awareness of MCP, our bridge binary
> (`rust-analyzer-mcp-server`) statically defines and serves all 10 tool descriptors,
> documentation, and JSON Schemas directly from its internal catalog.

Our MCP server writes this JSON-RPC response back to the AI / LLM coding agent over
`stdout`:

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "tools": [
            {
                "name": "rust_analyzer_hover",
                "description": "Hover documentation, types, and signatures for a symbol.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Absolute file path"
                        },
                        "line": {
                            "type": "integer",
                            "description": "0-based line number"
                        },
                        "character": {
                            "type": "integer",
                            "description": "0-based character offset"
                        }
                    },
                    "required": ["file_path", "line", "character"]
                }
            },
            {
                "name": "rust_analyzer_definition",
                "description": "Find symbol definition location.",
                "inputSchema": {}
            }
        ]
    }
}
```

The coding agent registers these schemas with the LLM, enabling the model to invoke any of
the 10 tools when inspecting code.

#### 2. Tool Execution (`tools/call`)

When the LLM decides to inspect a symbol at line 42, character 10, the coding agent sends
a standard MCP `tools/call` request to our MCP server's `stdin`:

```json
{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "rust_analyzer_hover",
        "arguments": {
            "file_path": "/path/to/main.rs",
            "line": 42,
            "character": 10
        }
    }
}
```

#### 3. The Bridge Translation: MCP to LSP

Our MCP server translates the tool name and arguments into an LSP 3.17 request:

| Standard MCP Method / Tool Name                      | Translates To LSP 3.17 Method                |
| :--------------------------------------------------- | :------------------------------------------- |
| `tools/call` (`rust_analyzer_hover`)                 | `textDocument/hover`                         |
| `tools/call` (`rust_analyzer_definition`)            | `textDocument/definition`                    |
| `tools/call` (`rust_analyzer_references`)            | `textDocument/references`                    |
| `tools/call` (`rust_analyzer_symbols`)               | `textDocument/documentSymbol`                |
| `tools/call` (`rust_analyzer_completion`)            | `textDocument/completion`                    |
| `tools/call` (`rust_analyzer_format`)                | `textDocument/formatting`                    |
| `tools/call` (`rust_analyzer_code_actions`)          | `textDocument/codeAction`                    |
| `tools/call` (`rust_analyzer_diagnostics`)           | `textDocument/diagnostic` (or push fallback) |
| `tools/call` (`rust_analyzer_workspace_diagnostics`) | `workspace/diagnostic`                       |
| `tools/call` (`rust_analyzer_set_workspace`)         | `workspace/didChangeConfiguration`           |

#### 4. Returning the Response to the AI / LLM Coding Agent

`rust-analyzer` answers the LSP query with symbol data (for `textDocument/hover`, it
natively formats the Rust signature and doc comments as Markdown in its `MarkupContent`
response). Our MCP server packages this into a standard MCP `CallToolResult` text payload
and returns it:

````json
{
    "jsonrpc": "2.0",
    "id": 2,
    "result": {
        "content": [
            {
                "type": "text",
                "text": "```rust\nfn foo()->bool\n```\nDoes stuff..."
            }
        ]
    }
}
````

The coding agent passes this text directly back into the LLM context so it can continue
reasoning.

### 3. No Need To Multiplex Over `stdio`

Neither JSON-RPC 2.0 nor the MCP specification dictates the transport layer. You can run
JSON-RPC over WebSockets, TCP, Unix domain sockets, or `stdio`. Over network sockets (such
as TCP or WebSockets), async request multiplexing makes sense, since thousands of remote
clients can connect to a single daemon, each over its own independent socket connection.

However, when an AI / LLM coding agent launches our MCP server locally, communication
relies on **OS anonymous pipes** (`stdin` and `stdout`). An OS pipe is a unidirectional,
in-memory FIFO buffer in the kernel (typically 64 KB on Linux). Because these are single
serialized byte streams, communication between the coding agent and our server is
inherently sequential by design:

1. **`stdin` (Accepting Requests from the Coding Agent):** The coding agent writes MCP
   JSON-RPC requests into our MCP server's `stdin` pipe, delimited by newlines (`\n`).
   Reading from `stdin` must be serialized: multiple concurrent reader threads would race
   to consume chunks from the byte stream, splitting JSON lines in half and breaking JSON
   parsing. A single synchronous reader loop in our main thread naturally consumes
   incoming requests line-by-line with zero synchronization overhead.
2. **`stdout` (Returning Responses to the Coding Agent):** Our MCP server writes JSON-RPC
   tool responses back to the coding agent over `stdout`. Multiple concurrent threads or
   tasks cannot write to `stdout` simultaneously without garbling the response stream.
   Even if a multi-threaded async runtime executes tool queries concurrently, all tasks
   must ultimately synchronize on a mutex to write their responses line-by-line. An async
   runtime cannot provide parallel I/O throughput over a single pipe; it simply adds mutex
   contention and task scheduling overhead.
3. **Turn-Based Agent Structure:** LLM workflows operate in discrete conversational turns.
   When the LLM generates a tool call, the coding agent writes the JSON-RPC request data
   to our MCP server's `stdin` and waits for the tool output before prompting the model
   for the next reasoning step. Because AST tool execution (done by `rust-analyzer`) is so
   fast (1 to 10 ms) compared to LLM inference (500 to 3,000 ms), sequential execution
   latency is completely imperceptible to the user.
4. **The Synchronous Event Loop:** In `src/mcp/server.rs`, the main thread runs a
   single-threaded line reader with no lock contention:

    ```rust
    // Block and read incoming JSON-RPC lines sequentially.
    for line in stdin.lock().lines() {
        let line = line?;
        let trimmed_line = line.trim();
        if trimmed_line.is_empty() {
            continue;
        }

        // Parse the MCP request payload.
        let request_payload = serde_json::from_str::<McpRequest>(trimmed_line);
        let Ok(request) = request_payload else {
            continue;
        };

        // Synchronously execute the tool query against rust-analyzer.
        let response_payload = self.handle_request(request);
        if let Some(response) = response_payload {
            // Write the response back to stdout.
            serde_json::to_writer(&mut stdout, &response)?;
            stdout.write_all(b"\n")?;
            stdout.flush()?;
        }
    }
    ```

    Each MCP request is consumed, translated into an LSP request, synchronously resolved
    against `rust-analyzer`, and the response is written back to `stdout` before the next
    line is read.

### 4. The Illusion of Async `stdio`

A common misconception in the Rust ecosystem is that calling
`tokio::io::stdin().read_line(&mut buf).await` transforms standard input into
non-blocking, asynchronous I/O. It does not.

#### How Tokio Reads `stdin` Under the Hood

On Unix-like operating systems (Linux, macOS, BSD), OS kernel event notification
mechanisms (`epoll` and `kqueue`) are designed for network sockets, event fds, and
specific character devices. `stdin` cannot be reliably polled via `epoll` edge-triggered
event loops without edge-case stalls.

To provide an `AsyncRead` interface over `stdin`, Tokio's `tokio::io::stdin()` literally:

1. Spawns a dedicated OS worker thread via `spawn_blocking`.
2. Runs a standard blocking `libc::read(0, ...)` call on that background thread.
3. Copies incoming bytes across an internal async channel to wake up your Tokio task.

> Tokio ends up doing the exact same thing we do by spawning a dedicated thread with a
> blocking read. However, Tokio also adds all the async runtime machinery (channel
> handoffs, and task scheduler overhead) on top just to maintain the illusion of being
> `async`!

#### The Workload Reality: There is Nothing to Multiplex

In a web server or network gateway, async runtimes shine because a single daemon must
multiplex potentially thousands of idle TCP connections waiting for bytes.

For a local MCP server, however, the coding agent operates in discrete conversational
turns.

- It writes a tool request into our MCP server's `stdin` pipe and pauses to await the
  response.
- While the LLM is reasoning, generating tokens, or waiting for user input, our MCP
  server's `stdin` pipe is idle 99% of the time. Our main thread simply sits blocked
  waiting for the next line, with zero concurrent traffic to multiplex.

When an async runtime delegates `stdio` to blocking worker threads anyway, wrapping that
pipeline inside a multi-threaded async state machine does not make it faster or better. It
simply adds runtime initialization overhead, future state machine transformations, and
task scheduling latency. It is simply not fit for this purpose, adding complexity without
providing any of the benefits of asynchronous I/O.

## The 3-Thread Architecture

While communication from the AI / LLM coding agent to the MCP server over `stdio` is
synchronous and sequential, communication between the MCP server and `rust-analyzer` is
inherently asynchronous. `rust-analyzer` can emit unprompted notifications (such as
compiler diagnostics via `textDocument/publishDiagnostics` or indexing progress via
`experimental/serverStatus`) at any time, interleaved with query responses.

To handle this cleanly without an async runtime, `r3bl-rust-analyzer-mcp-server` uses
**exactly 3 dedicated OS threads**:

```text
┌──────────────────────────────────────────────────────────────┐
│                r3bl-rust-analyzer-mcp-server                 │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ 1. MAIN THREAD (main)                                  │  │
│  │    • Reads MCP JSON-RPC from coding agent stdin.       │  │
│  │    • Translates tool calls to LSP JSON-RPC.            │  │
│  │    • Writes query to rust-analyzer stdin writer.       │  │
│  │    • Blocks on single-use sync_channel(1) receiver.    │  │
│  │    • Formats ToolResult & writes response to stdout.   │  │
│  └──────────────┬────────────────────────▲────────────────┘  │
│                 │                        │                   │
│                 │ Writes LSP             │ Delivers payload  │
│                 │ Request                │ via SyncSender    │
│                 ▼                        │                   │
│    ┌──────────────────────────┐   ┌──────┴────────────────┐  │
│    │ rust-analyzer stdin pipe │   │ pending_requests:     │  │
│    └──────────────────────────┘   │ Arc<Mutex<HashMap>>   │  │
│                                   └──────▲────────────────┘  │
│                                          │                   │
│  ┌───────────────────────────────────────┴────────────────┐  │
│  │ 2. LSP STDOUT READER THREAD (lsp-stdout-reader)        │  │
│  │    • Reads Content-Length framed JSON-RPC from RA.     │  │
│  │    • Matches ID to pending_requests & unblocks Main.   │  │
│  │    • Ingests compiler diagnostics & server status.     │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ 3. LSP STDERR READER THREAD (lsp-stderr-reader)        │  │
│  │    • Continuously drains rust-analyzer stderr pipe.    │  │
│  │    • Forwards stderr lines to structured tracing.      │  │
│  │    • CRITICAL: Prevents 64 KB kernel pipe deadlocks.   │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Thread 1: Main MCP Loop

The Main Thread is the orchestrator. It executes the synchronous MCP loop:

1. Reads a line from `std::io::stdin()`.
2. Parses the MCP JSON-RPC payload.
3. If it is a tool invocation (e.g. `rust_analyzer_hover` or `rust_analyzer_definition`),
   it converts the request into an LSP message and dispatches it via `send_request()`.
4. Writes the MCP response back to `std::io::stdout()`.

### Thread 2: `stdout` Reader

Spawned immediately after the `rust-analyzer` subprocess is launched, this background
thread takes ownership of the child's `stdout` pipe and runs a dedicated loop parsing
`Content-Length: ...\r\n\r\n` framed messages:

- **Response Payloads:** Extracts the `id`, looks up the transmitter in
  `pending_requests`, and unblocks the Main Thread via `sender.send(payload)`.
- **Compiler Diagnostics:** Ingests `textDocument/publishDiagnostics` notifications into a
  thread-safe cache (`Arc<Mutex<HashMap<String, Vec<Value>>>>`).
- **Indexing Progress:** Parses `experimental/serverStatus` notifications and updates the
  thread-safe `ServerReadinessMonitor`.

### Thread 3: `stderr` Drainer

Many language server bridges suffer from subtle, intermittent freezes. On Linux and macOS,
anonymous pipes have a default kernel buffer capacity of **64 KB**.

If `rust-analyzer` prints heavy debug tracing, cargo warnings, or proc-macro diagnostic
messages to `stderr`, and the parent process does not read `stderr`, the 64 KB kernel
buffer fills up. Once full, any subsequent write by `rust-analyzer` to `stderr` blocks the
entire compiler process at the OS kernel level, deadlocking the server indefinitely.

Thread 3 continuously drains `stderr` in a tight loop and routes the lines to structured
tracing logs, guaranteeing that `rust-analyzer`'s `stderr` pipe never fills up or
deadlocks.

### Request-Response Via `sync_channel(1)`

Instead of complex async runtime state machines, request-response synchronization between
Thread 1 and Thread 2 uses a standard library synchronous channel with a buffer capacity
of 1 (`std::sync::mpsc::sync_channel(1)`).

Thread 1 creates a fresh channel pair for each outbound LSP request, registers the
transmitter in the `pending_requests` thread-safe lookup table keyed by request ID, and
blocks on the receiver until Thread 2 delivers the response:

```rust
pub fn send_request(
    &mut self,
    method: &str,
    params: Option<Value>,
) -> Result<Value, McpServerError> {
    // Generate unique request ID.
    let request_id = self.next_request_id();

    // Allocate single-use channel with buffer capacity 1.
    let (tx, rx) = std::sync::mpsc::sync_channel(1);

    // Register transmitter in pending_requests table.
    {
        let mut guard = self.pending_requests.lock().unwrap();
        guard.insert(request_id, tx);
    }

    // Write framed LSP request to rust-analyzer stdin.
    self.write_lsp_message(request_id, method, params)?;

    // Block waiting for response with timeout.
    let timeout = Duration::from_secs(10);
    match rx.recv_timeout(timeout) {
        Ok(response) => Ok(response),
        Err(_) => {
            // Clean up pending request on timeout.
            self.pending_requests.lock().unwrap().remove(&request_id);
            Err(McpServerError::RequestCancelled)
        }
    }
}
```

This pattern has the following advantages:

1. Zero Contention: The channel has an exact capacity of 1 (`sync_channel(1)`).
2. Deterministic Timeout: If `rust-analyzer` hangs or crashes, `rx.recv_timeout()` cleanly
   unblocks the main thread without leaving dangling futures.
3. Automatic Cleanup: When `rx` drops, the channel is deallocated immediately.

## Advantages

By replacing Tokio with standard library threads, `r3bl-rust-analyzer-mcp-server` achieves
tangible advantages:

### Sub-Millisecond Cold Starts

AI / LLM coding agents frequently spin up MCP servers dynamically per repository or
worktree. Without Tokio's runtime initialization sequence, thread-pool allocation, and
timer wheel setup, `rust-analyzer-mcp-server` enters its main loop and begins spawning the
`rust-analyzer` subprocess in less than 2 milliseconds on average (tested on an Intel Core
i7-14700 on Linux).

### Transparent Stack Traces

When debugging an issue in a multi-threaded async codebase, backtraces often look like an
maze of `poll`, `wake`, `Task::run`, and internal runtime state-machine steps.

In this synchronous architecture, every stack trace is transparent:

- Thread 1 is in `enter_main_event_loop` -> `send_request` -> `recv_timeout`.
- Thread 2 is in `read_exact` parsing `Content-Length` headers.
- Thread 3 is in `read_line` draining stderr.

Inspecting the tracing log output gives an exact, unambiguous view of the entire
application state.

### Deterministic Teardown

In async runtimes, graceful teardown often requires coordinating `CancellationToken`
hierarchies across worker thread pools. If an async task forgets to check the token, child
processes become orphaned zombies eating 100% CPU. Furthermore, dropping a future
mid-execution cancels it at whichever `.await` point it was suspended at, potentially
leaving partially written LSP messages in a shared pipe and corrupting the transport
stream.

In a synchronous thread architecture, teardown is naturally governed by standard OS pipe
mechanics:

```text
AI / LLM Coding Agent Closes Stdin (Process exits or session terminates)
   │
   ▼
stdin.lock().lines() returns Ok(None) / EOF on Main Thread
   │
   ▼
enter_main_event_loop exits cleanly
   │
   ▼
RustAnalyzerClient::shutdown() executes (or runs in Drop):
   1. Sends LSP "shutdown" request and "exit" notification.
   2. Closes child stdin writer handle (signaling EOF to rust-analyzer).
   3. Calls child_proc.kill() and child_proc.wait() to reap zombie PID.
   4. Background reader threads reach EOF on stdout/stderr and terminate.
   │
   ▼
Process exits cleanly with exit code 0 in <1ms.
```

This makes shutdown straightforward. When `stdin` reaches EOF, the main loop exits,
terminates `rust-analyzer`, and the reader threads finish naturally as soon as their pipes
close. There are no background tasks or child processes left behind.

## Choosing the Right Tool

The goal of this architectural comparison is not to discourage the use of Tokio or async
Rust. Async Rust is one of the most powerful paradigms in modern systems programming when
applied to the problem domain it was created for: high-concurrency 1:N I/O multiplexing
across thousands of network sockets or complex, multi-source event-driven user interfaces.

However, for a 1:1 local standard I/O translation bridge, standard library threads and
channels offer a superior design:

- **Lower Cognitive Load:** Simple, linear control flow without async function coloring.
- **Superior Reliability:** Deadlock-free 3-thread pipe isolation with deterministic EOF
  teardown.
- **Lean Footprint:** Zero runtime overhead, minimal dependencies, and instant cold
  starts.

### Resources & Links

- Crate: [`r3bl-rust-analyzer-mcp-server`][`r3bl-rust-analyzer-mcp-server`]
- Model Context Protocol Specification: [modelcontextprotocol.io][mcp-spec]
- Language Server Protocol 3.17 Specification: [language-server-protocol][lsp-spec]
- R3BL Open Core Project: [github.com/r3bl-org/r3bl-open-core][r3bl-open-core-repo]

<!-- prettier-ignore-start -->

[mcp-spec]: https://modelcontextprotocol.io/
[`rust-analyzer`]: https://rust-analyzer.github.io/
[`r3bl-rust-analyzer-mcp-server`]: https://crates.io/crates/r3bl-rust-analyzer-mcp-server
[`r3bl_tui`]: https://crates.io/crates/r3bl_tui
[rmcp]: https://github.com/modelcontextprotocol/rust-sdk
[zeenix]: https://github.com/zeenix/rust-analyzer-mcp
[ciresnave]: https://github.com/ciresnave/rust-analyzer-mcp-server
[dexwritescode]: https://github.com/dexwritescode/rust-mcp
[lsp-mcp]: https://crates.io/crates/lsp-mcp
[cancel-safe]: https://docs.rs/tokio/latest/tokio/macro.select.html#cancellation-safety
[async-trait]: https://crates.io/crates/async-trait
[RRT]: https://github.com/r3bl-org/r3bl-open-core/tree/main/tui/src/core/resilient_reactor_thread
[cantrill-complexity]: https://www.youtube.com/watch?v=Cum5uN2634o
[lsp-spec]: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/
[r3bl-open-core-repo]: https://github.com/r3bl-org/r3bl-open-core

<!-- prettier-ignore-end -->
