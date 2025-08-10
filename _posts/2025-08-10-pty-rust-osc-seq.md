---
title: "Build with Naz : Capturing Real-Time Build Progress from Cargo Using PTY and OSC Sequences"
author: Nazmul Idris
date: 2025-08-10
excerpt: |
  When building Rust projects, Cargo emits hidden OSC (Operating System Command) terminal
  control sequences that communicate build progress to compatible terminals like WezTerm.
  However, capturing these sequences programmatically is surprisingly tricky - standard
  process pipes won't work because Cargo only emits them when connected to a real TTY, and
  inheriting stdio bypasses your program entirely. This article explores how to use
  pseudo-terminals (PTY) with the portable-pty crate to create a virtual terminal that
  tricks Cargo into emitting OSC sequences while still allowing you to capture and parse
  them in real-time. We'll dive into the PTY architecture, understand why blocking I/O with
  cloned file descriptors causes hangs, and implement a production-ready solution using a
  detached task pattern that processes build progress events (0-100%) as they happen, not
  after the build completes.
layout: post
categories:
  - Rust
  - CLI
  - Server
---

<img class="post-hero-image" src="{{ 'assets/pty.png' | relative_url }}"/>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Overview](#overview)
- [Quick Summary for Developers](#quick-summary-for-developers)
- [OSC Sequence Format](#osc-sequence-format)
  - [State Values](#state-values)
  - [Example Sequences](#example-sequences)
- [Implementation Details](#implementation-details)
  - [Key Files](#key-files)
  - [Terminal Detection](#terminal-detection)
  - [Progress Flow](#progress-flow)
- [Configuration](#configuration)
- [Capturing OSC Sequences from Cargo](#capturing-osc-sequences-from-cargo)
  - [Quick Start: Dependencies](#quick-start-dependencies)
  - [The TTY Problem](#the-tty-problem)
  - [Why Stdio::inherit() Won't Work for Capture](#why-stdioinherit-wont-work-for-capture)
- [The Solution: Using PTY with portable-pty](#the-solution-using-pty-with-portable-pty)
  - [Understanding PTY Architecture](#understanding-pty-architecture)
    - [How PTY Solves the OSC Problem](#how-pty-solves-the-osc-problem)
    - [Why Other Approaches Fail](#why-other-approaches-fail)
    - [The Virtual Terminal Effect](#the-virtual-terminal-effect)
- [Minimal Code Snippet](#minimal-code-snippet)
- [Complete Working Example](#complete-working-example)
  - [Full POC Implementation](#full-poc-implementation)
  - [Running the POC](#running-the-poc)
  - [Expected Output](#expected-output)
  - [Troubleshooting](#troubleshooting)
- [Environment Considerations](#environment-considerations)
- [Testing](#testing)
- [References](#references)
- [Build with Naz video series on developerlife.com YouTube channel](#build-with-naz-video-series-on-developerlifecom-youtube-channel)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Overview

Cargo emits OSC (Operating System Command) terminal control sequences during build operations to
communicate progress status to compatible terminal emulators. These sequences allow terminals to
display build progress in title bars, taskbars, or other UI elements.

This document explains how to programmatically capture and parse these OSC sequences when spawning
`cargo build` from a Rust program.

Here are some useful links for context:

1. [Cargo source code](https://github.com/rust-lang/cargo)
2. [ANSI escape codes](https://en.wikipedia.org/wiki/ANSI_escape_code#Operating_System_Command_sequences)
3. [OSC terminal control sequences](https://blog.vucica.net/2017/07/what-are-osc-terminal-control-sequences-escape-codes.html)

## Quick Summary for Developers

1. **Goal:**
   - Capture and parse progress information from `cargo build` using OSC escape sequences.
2. **Key Challenge:**

   - Cargo only emits OSC sequences when connected to an interactive TTY, and a compatible terminal
     (like `wezterm`).
   - Spawning a child process using `std::process::Command` and standard process pipes don't work,
     since the child process correctly detects the terminal is not-interactive (not connected to
     TTY).
   - Inheriting stdio from the current process doesn't work either, for two reasons. While the child
     process does detect the terminal as interactive (connected to TTY), it also clobbers output
     from the parent CLI or TUI process by sending all the output including OSC sequences directly
     to the terminal, bypassing the parent process. And there is no way to capture or parse the
     output/OSC codes.

     | Method             | `is_terminal()` | OSC Emitted? | Can Capture? | Problem                      |
     | ------------------ | --------------- | ------------ | ------------ | ---------------------------- |
     | **Standard pipes** | ❌ false        | ❌ No        | ✅ Yes       | No OSC sequences generated   |
     | **Stdio inherit**  | ✅ true         | ✅ Yes       | ❌ No        | Output bypasses your program |
     | **PTY**            | ✅ true         | ✅ Yes       | ✅ Yes       | Perfect solution!            |

3. **Solution:**
   - Use a pseudo-terminal (PTY) via the `portable-pty` crate to simulate a terminal environment.
   - And "fake" that `wezterm` is the terminal program by setting `TERM_PROGRAM=WezTerm`.
4. **What You'll Get:**
   - Real-time build progress updates (0-100%) that you can process programmatically.
5. **Jump to:**
   - [Minimal Code Snippet](#minimal-code-snippet) for a quick start.
   - [Complete Working Example](#complete-working-example) for a ready-to-run POC.

## OSC Sequence Format

Cargo uses the **OSC 9;4** format (ConEmu-style progress reporting):

```
ESC ] 9 ; 4 ; st ; pr ST
```

Where:y

- `ESC` = `\x1b` (escape character)
- `]` = OSC introducer
- `9;4` = ConEmu-specific progress command
- `st` = state (0-4)
- `pr` = progress value (0-100)
- `ST` = `\x1b\\` (string terminator)

### State Values

- `0`: Remove progress indicator
- `1`: Set progress value (0-100)
- `2`: Set error state in taskbar
- `3`: Set indeterminate state (animated, no specific progress)
- `4`: Set paused state (not used by Cargo)

### Example Sequences

- Start progress: `\x1b]9;4;1;0\x1b\\`
- 50% complete: `\x1b]9;4;1;50\x1b\\`
- Build error: `\x1b]9;4;2;100\x1b\\`
- Remove progress: `\x1b]9;4;0;0\x1b\\`

## Implementation Details

> - Repo with the source for this article:
>   [nazmulidris/rust-scratch/pty_cargo_build_progress_osc_codes](https://github.com/nazmulidris/rust-scratch/blob/main/pty_cargo_build_progress_osc_codes)
> - Tracking issue: [rust-scratch 117](https://github.com/nazmulidris/rust-scratch/issues/117)
> - Related issue: [r3bl-cmdr 437](https://github.com/r3bl-org/r3bl-open-core/issues/437)

### Key Files

You can get the source code for Cargo from [Cargo GitHub repo](https://github.com/rust-lang/cargo).

Let's say you cloned the Cargo source code in `/home/your-username/github/cargo/` folder. Then you
will find the following:

1. **`src/cargo/util/progress.rs`**

   - Contains the main progress bar implementation
   - `StatusValue` enum (lines 87-99) defines progress states
   - `Display` implementation (lines 161-179) formats OSC sequences
   - `TerminalIntegration` struct manages OSC emission

2. **`src/cargo/core/shell.rs`**

   - Terminal capability detection (lines 594-600)
   - Checks environment variables for terminal support

3. **`src/cargo/core/compiler/job_queue/mod.rs`**
   - Creates progress bar during build (line 481)
   - Updates progress as compilation proceeds
   - Marks progress as error on build failure (line 872)

### Terminal Detection

Cargo detects OSC support by checking environment variables in `supports_term_integration()`:

```rust
fn supports_term_integration(
    stream: &dyn IsTerminal
) -> bool {
    let windows_terminal = std::env::var("WT_SESSION")
        .is_ok();
    let conemu = std::env::var("ConEmuANSI").ok() ==
        Some("ON".into());
    let wezterm = std::env::var("TERM_PROGRAM").ok() ==
        Some("WezTerm".into());

    (windows_terminal || conemu || wezterm) &&
        stream.is_terminal()
}
```

Supported terminals:

- **Windows Terminal**: Detected via `WT_SESSION` environment variable
- **ConEmu**: Detected via `ConEmuANSI=ON`
- **WezTerm**: Detected via `TERM_PROGRAM=WezTerm`

### Progress Flow

1. Build starts → Progress bar created with `Progress::with_style()`
2. Terminal integration initialized based on detection and config
3. During compilation:
   - `tick()` or `tick_now()` called with current/max units
   - Progress percentage calculated
   - OSC sequence emitted to stderr
4. On completion or error:
   - Final state sent (100% or error)
   - Progress cleared with remove sequence

## Configuration

Users can control OSC emission via `.cargo/config.toml`:

```toml
[term]
progress.term-integration = true   # Enable OSC sequences
                                   # (auto-detected by default)
# or
progress.term-integration = false  # Disable OSC sequences

# Other progress options
progress.when = "auto"     # "auto", "always", or "never"
progress.width = 80        # Terminal width for progress bar
```

## Capturing OSC Sequences from Cargo

### Quick Start: Dependencies

Add this to your `Cargo.toml`:

```toml
[dependencies]
portable-pty = "0.8"
tokio = { version = "1.0", features = ["full"] }
miette = { version = "7.2", features = ["fancy"] }
```

### The TTY Problem

**Important**: When using pipes with `std::process::Command`, the spawned process detects it's NOT
connected to a TTY, causing `is_terminal()` to return false and **no OSC sequences will be
emitted**. You need a pseudo-terminal (PTY) to capture OSC sequences.

### Why Stdio::inherit() Won't Work for Capture

While you can use `Stdio::inherit()` to let the spawned process use your real terminal (and OSC
codes will be displayed), this approach has a critical limitation:

```rust
use std::process::{Command, Stdio};

let mut cmd = Command::new("cargo");
cmd.arg("build")
   .env("TERM_PROGRAM", "WezTerm")
   .stdin(Stdio::inherit())
   .stdout(Stdio::inherit())
   .stderr(Stdio::inherit());  // Uses real TTY, OSC goes
                               // directly to terminal

let mut child = cmd.spawn()?;
child.wait()?;
// Problem: Cannot capture or parse the output/OSC codes!
```

**Why this doesn't work for capture:**

- Output goes directly to your terminal, bypassing your program
- You cannot intercept, parse, or process the OSC sequences
- You have no programmatic access to the build progress data
- This is only useful if you want to display progress without processing it

## The Solution: Using PTY with portable-pty

The only way to both trigger OSC emission AND capture the sequences is to use a pseudo-terminal
(PTY).

### Understanding PTY Architecture

A **PTY (Pseudo-Terminal)** is a software-based virtual terminal that creates two connected
endpoints:

- **Controller endpoint**: Your program connects here to manage the virtual terminal
- **Controlled endpoint**: The spawned process connects here, believing it's a real terminal

```
┌─────────────┐   ┌───────────┐   ┌───────────────┐
│ Your Program│◄─►│    PTY    │◄─►│Spawned Process│
│(Controller) │   │Controller/│   │ (Controlled)  │
│             │   │Controlled │   │               │
└─────────────┘   └───────────┘   └───────────────┘
```

#### How PTY Solves the OSC Problem

The genius of PTY is that it creates a **bidirectional pipe that appears to be a real terminal** to
the spawned process:

1. **Your program** creates a PTY pair and gets handles to both endpoints
2. **Cargo process** is launched with the controlled endpoint as its terminal
3. **Cargo believes** it's connected to a real terminal → `is_terminal()` returns `true`
4. **OSC sequences are emitted** because terminal integration is enabled
5. **Your program** can read all output (including OSC) through the controller endpoint

#### Why Other Approaches Fail

| Method             | `is_terminal()` | OSC Emitted? | Can Capture? | Problem                      |
| ------------------ | --------------- | ------------ | ------------ | ---------------------------- |
| **Standard pipes** | ❌ false        | ❌ No        | ✅ Yes       | No OSC sequences generated   |
| **Stdio inherit**  | ✅ true         | ✅ Yes       | ❌ No        | Output bypasses your program |
| **PTY**            | ✅ true         | ✅ Yes       | ✅ Yes       | Perfect solution!            |

#### The Virtual Terminal Effect

PTY essentially turns your program into a "virtual terminal emulator":

- **Satisfies Cargo's terminal detection** (makes `is_terminal()` return true)
- **Enables OSC emission** (because it looks like a compatible terminal)
- **Allows programmatic capture** (your program controls the virtual terminal)
- **Provides full control** (you can process, filter, or transform the data)

This elegant solution is **the only method** that satisfies both requirements: triggering OSC
emission AND capturing the sequences for programmatic processing.

## Minimal Code Snippet

> **Note**: The `portable-pty` crate uses the legacy API terms `master`/`slave` for historical
> compatibility, but conceptually these represent the controller/controlled relationship described
> above.

````rust
// Cargo.toml dependencies:
// portable-pty = "0.9.0"
// tokio = { version = "1.0", features = ["full"] }
// miette = { version = "7.0", features = ["fancy"] }
use portable_pty::{
    CommandBuilder, PtySize, native_pty_system
};
use miette::IntoDiagnostic;
use std::io::Read; // For reading from the PTY controller

/// ```text
/// ┌────────────┐   ┌────────────┐   ┌─────────────────┐
/// │Your Program│◄─►│Controller  │   │Cargo Process    │
/// │            │   │     ↕      │   │                 │
/// │Reads/writes│   │    PTY     │   │stdin/stdout/    │
/// │through     │   │     ↕      │   │stderr redirected│
/// │controller  │   │  Controlled│◄─►│to controlled    │
/// └────────────┘   └────────────┘   └─────────────────┘
/// ```
async fn spawn_with_pty() -> miette::miette::miette::Result<()> {
    // Create a pseudo-terminal
    let pty_system = native_pty_system();
    let pty_pair = pty_system.openpty(PtySize {
        rows: 30,           // Terminal height for cargo's
                            // output formatting
        cols: 80,           // Terminal width for progress
                            // bar display
        pixel_width: 0,     // Not needed for text-based
                            // output
        pixel_height: 0,    // Not needed for text-based
                            // output
    }).map_err(|e|
        miette::miette!("Failed to open PTY: {}", e)
    )?;

    // Extract endpoints with descriptive names
    let controller = pty_pair.master;  // Where your program
                                       // reads/writes
    let controlled = pty_pair.slave;   // Where the spawned
                                       // process connects

    // Configure the command
    let mut cmd = CommandBuilder::new("cargo");
    cmd.arg("build");
    cmd.env("TERM_PROGRAM", "WezTerm"); // Without this Cargo
                                      // won't emit OSC
                                      // sequences

    // CRITICAL: Set working directory - without this, PTY
    // spawns in home folder!
    let current_dir = std::env::current_dir()
        .map_err(|e|
            miette::miette!(
                "Failed to get current directory: {}", e
            )
        )?;
    cmd.cwd(current_dir);

    // Spawn with PTY (this makes is_terminal() return true!)
    // Note: The cargo child process uses 'controlled' as its
    // stdin/stdout/stderr
    // This makes cargo believe it's connected to a real
    // terminal
    let mut controlled_child = controlled.spawn_command(cmd)
        .map_err(|e|
            miette::miette!(
                "Failed to spawn cargo build: {}", e
            )
        )?;

    // Read output with OSC sequences
    // Note: controller is the "controller" endpoint where
    // your program reads from
    let mut controller_reader = controller
        .try_clone_reader()
        .map_err(|e|
            miette::miette!("Failed to clone reader: {}", e)
        )?;

    // Spawn the reading operation on a separate async task
    // NOTE: This approach reads ALL output into a string at
    // once after the process completes.
    // This is simple but NOT ideal for real-time progress
    // monitoring since OSC sequences
    // are only processed after the entire build finishes.
    // For real-time progress updates,
    // use the buffered reading approach shown in the full
    // example.
    let read_handle = tokio::spawn(async move {
        let mut output = String::new();
        // Read entire output stream into a single string
        // (blocks until EOF)
        controller_reader.read_to_string(&mut output)
            .map_err(|e|
                miette::miette!("Failed to read from PTY: {}", e)
            )?;

        // Note: if you println!("{output}"); here,
        // it will print the entire output including OSC
        // sequences, which will clobber your terminal
        // display. Instead, we will parse the output
        // for OSC codes and build a report.

        // Check for OSC codes
        let has_osc_codes = output.contains("\x1b]");

        // Build report
        let mut report = String::new();
        report.push_str(&format!(
            "Total bytes read: {}\n", output.len()
        ));
        report.push_str(&format!(
            "OSC codes found: {}\n",
            if has_osc_codes { "YES ✓" } else { "NO ✗" }
        ));

        Ok::<String, miette::Error>(report)
    });

    // Wait for the child process to complete
    //
    // IMPORTANT: Use spawn_blocking because child.wait() is
    // a synchronous blocking operation.
    // If we called controlled_child.wait() directly in this
    // async context, it would block
    // the entire tokio runtime thread, preventing other
    // async tasks from running.
    // spawn_blocking moves the blocking operation to a
    // dedicated thread pool.
    // The `.into_diagnostic()?.into_diagnostic()?` handles
    // two layers of miette::Result unwrapping:
    // - First `?` unwraps the JoinResult from spawn_blocking
    //   (handles task panics/cancellation)
    // - Second `?` unwraps the miette::Result from child.wait()
    //   (handles process wait errors)
    //
    // NOTE: portable-pty doesn't have native async support,
    // but provides async-compatible methods:
    // - try_clone_reader() returns readers that work with
    //   std::io::Read
    // - child.wait() is blocking, so we use spawn_blocking
    //   to avoid blocking the async runtime
    // - For fully async PTY operations, consider
    //   alternatives like tokio-ptyprocess (experimental)
    let status = tokio::task::spawn_blocking(
        move || controlled_child.wait()
    )
        .await
        .into_diagnostic()?
        .into_diagnostic()?;

    // Wait for the reading task to complete and get the
    // report
    // The `.into_diagnostic()??` handles two layers of
    // miette::Result unwrapping:
    // - First `?` unwraps the JoinResult from tokio::spawn
    //   (handles task panics/cancellation)
    // - Second `?` unwraps the miette::Result<String, Error> from
    //   the task's return value
    let report = read_handle.await.into_diagnostic()??;

    println!("Build completed with status: {}", status);
    println!("{}", report);

    Ok(())
}
````

**Why PTY works:**

- Creates a virtual terminal that satisfies `is_terminal()` check
- Allows your program to act as the "terminal" for the spawned process
- Captures all output including OSC sequences
- Provides full programmatic control over the data

## Complete Working Example

### Full POC Implementation

Save this as `src/main.rs`:

```rust
use miette::IntoDiagnostic;
use portable_pty::{CommandBuilder, PtySize, native_pty_system};
use std::io::Read;
use tokio::sync::mpsc::{unbounded_channel, UnboundedSender};

// ANSI color codes for better output
const GREEN: &str = "\x1b[32m";
const RED: &str = "\x1b[31m";
const YELLOW: &str = "\x1b[33m";
const RESET: &str = "\x1b[0m";

/// Represents the different types of OSC progress events
/// that Cargo can emit
#[derive(Debug, Clone, PartialEq)]
enum OscEvent {
    /// Set specific progress value 0-100% (OSC state 1)
    ProgressUpdate(u8),
    /// Clear/remove progress indicator (OSC state 0)
    ProgressCleared,
    /// Build error occurred (OSC state 2)
    BuildError,
    /// Indeterminate progress - build is running but no
    /// specific progress (OSC state 3)
    IndeterminateProgress,
}

/// OSC 9;4 sequence constants
const OSC_START: &str = "\x1b]9;4;";
const OSC_END: &str = "\x1b\\";

/// Buffer for accumulating and parsing OSC sequences
struct OscBuffer {
    data: String,
}

impl OscBuffer {
    fn new() -> Self {
        Self { data: String::new() }
    }

    /// Append new bytes and extract complete OSC sequences
    fn append_and_extract(
        &mut self,
        buffer: &[u8],
        n: usize
    ) -> Vec<OscEvent> {
        // Convert bytes to string and append to accumulated data
        let text = String::from_utf8_lossy(&buffer[..n]);
        self.data.push_str(&text);

        let mut events = Vec::new();

        // Find and process all complete OSC sequences
        while let Some(event) = self.extract_next_sequence() {
            events.push(event);
        }

        events
    }

    /// Extract the next complete OSC sequence from buffer
    fn extract_next_sequence(&mut self) -> Option<OscEvent> {
        // Find start of OSC sequence
        let start_idx = self.data.find(OSC_START)?;
        let after_start_idx = start_idx + OSC_START.len();

        // Find end of sequence
        let end_idx = self.data[after_start_idx..].find(OSC_END)?;
        let params_end_idx = after_start_idx + end_idx;
        let sequence_end_idx = params_end_idx + OSC_END.len();

        // Extract and parse parameters
        let params = &self.data[after_start_idx..params_end_idx];
        let event = self.parse_osc_params(params);

        // Remove processed portion from buffer
        self.data.drain(0..sequence_end_idx);

        event
    }

    /// Parse OSC parameters into an OscEvent
    fn parse_osc_params(&self, params: &str) -> Option<OscEvent> {
        let parts: Vec<&str> = params.split(';').collect();
        if parts.len() != 2 {
            return None;
        }

        let state = parts[0].parse::<u8>().ok()?;
        let progress = parts[1].parse::<f64>().ok()?;

        match state {
            0 => Some(OscEvent::ProgressCleared),
            1 => Some(OscEvent::ProgressUpdate(progress as u8)),
            2 => Some(OscEvent::BuildError),
            3 => Some(OscEvent::IndeterminateProgress),
            _ => None,
        }
    }
}

#[tokio::main]
async fn main() -> miette::Result<()> {
    // Run cargo clean first to ensure we see progress
    println!("{}🧹 Running cargo clean...{}", YELLOW, RESET);
    std::process::Command::new("cargo")
        .arg("clean")
        .arg("-q")
        .status()
        .into_diagnostic()?;

    println!(
        "\n{}Starting Cargo build with OSC capture...{}",
        YELLOW, RESET
    );
    println!(
        "{}========================================{}\n",
        YELLOW, RESET
    );

    // Create channel for OSC events
    let (sender, mut receiver) = unbounded_channel::<OscEvent>();

    // Spawn cargo build task
    let build_handle = spawn_cargo_with_osc_capture(sender);

    // Process events until cargo completes
    loop {
        tokio::select! {
            // Check if build completed
            result = build_handle => {
                let status = result.into_diagnostic()??;
                println!(
                    "\n{}✅ Build completed with status: {:?}{}",
                    GREEN, status, RESET
                );
                break;
            }
            // Handle OSC events
            Some(event) = receiver.recv() => {
                match event {
                    OscEvent::ProgressUpdate(percentage) => {
                        println!(
                            "{}📊 cargo build progress: {}%{}",
                            GREEN, percentage, RESET
                        );
                    }
                    OscEvent::ProgressCleared => {
                        println!(
                            "{}✓ Progress tracking cleared{}",
                            GREEN, RESET
                        );
                    }
                    OscEvent::BuildError => {
                        println!(
                            "{}❌ Build error occurred{}",
                            RED, RESET
                        );
                    }
                    OscEvent::IndeterminateProgress => {
                        println!(
                            "{}⏳ Build in progress (indeterminate){}",
                            GREEN, RESET
                        );
                    }
                }
            }
        }
    }

    Ok(())
}

/// Spawn cargo build in a PTY and capture OSC sequences
async fn spawn_cargo_with_osc_capture(
    event_sender: UnboundedSender<OscEvent>
) -> miette::Result<portable_pty::ExitStatus> {
    tokio::task::spawn(async move {
        // Create a pseudo-terminal
        let pty_system = native_pty_system();
        let pair = pty_system.openpty(PtySize {
            rows: 24,
            cols: 80,
            pixel_width: 0,
            pixel_height: 0,
        }).map_err(|e| {
            miette::miette!("Failed to open PTY: {}", e)
        })?;

        let controller = pair.master;
        let controlled = pair.slave;

        // Configure cargo command
        let mut cmd = CommandBuilder::new("cargo");
        cmd.arg("build");
        cmd.env("TERM_PROGRAM", "WezTerm"); // Critical for OSC

        // Set working directory - PTY defaults to $HOME!
        let cwd = std::env::current_dir()
            .map_err(|e| {
                miette::miette!("Failed to get current dir: {}", e)
            })?;
        cmd.cwd(cwd);

        // Spawn cargo with PTY
        let mut child = controlled.spawn_command(cmd)
            .map_err(|e| {
                miette::miette!("Failed to spawn cargo: {}", e)
            })?;

        // Spawn reader task to process OSC sequences
        //
        // CRITICAL: PTY LIFECYCLE AND FILE DESCRIPTOR MANAGEMENT
        // ======================================================
        // A PTY consists of two sides: master (controller) and
        // slave (controlled). The kernel's PTY implementation
        // requires BOTH conditions for EOF:
        //
        // 1. The slave side must be closed (happens when the
        //    child process exits)
        // 2. The reader must be the ONLY remaining reference
        //    to the master
        //
        // How File Descriptors Work Here:
        // - controller: Holds the master side file descriptor
        // - controlled: Holds the slave side file descriptor
        // - When cargo exits, it closes its copy of the slave FD
        // - BUT our `controlled` variable STILL holds the
        //   original slave FD!
        //
        // The Solution:
        // 1. Move controller into spawn_blocking - ensures it
        //    drops after creating reader
        // 2. Explicitly drop controlled after cargo exits -
        //    closes our slave FD
        // 3. This allows the reader to receive EOF and exit
        //    cleanly
        //
        let reader_handle = tokio::task::spawn_blocking(move || {
            // Controller is MOVED into this closure, so it will
            // be dropped when this task completes, allowing
            // proper PTY cleanup.
            let mut reader = controller.try_clone_reader()
                .map_err(|e| {
                    miette::miette!("Failed to clone reader: {}", e)
                })?;

            let mut buffer = [0u8; 4096];
            let mut osc_buffer = OscBuffer::new();

            loop {
                // This will receive EOF when:
                // 1. The slave side (controlled) is closed/dropped
                // 2. No other references to the master exist
                match reader.read(&mut buffer) {
                    Ok(0) => break, // EOF - PTY closed
                    Ok(n) => {
                        for event in osc_buffer.append_and_extract(
                            &buffer, n
                        ) {
                            let _ = event_sender.send(event);
                        }
                    }
                    Err(_) => break, // Error reading - PTY closed
                }
            }

            // Controller drops here automatically when the
            // closure ends, decrementing the master side's
            // reference count.
            Ok::<(), miette::Error>(())
        });

        // Wait for cargo to complete
        let status = tokio::task::spawn_blocking(
            move || child.wait()
        )
            .await
            .into_diagnostic()?
            .into_diagnostic()?;

        // Explicitly drop the controlled (slave) side after
        // cargo exits. This closes the slave end of the PTY,
        // which is necessary for the reader to receive EOF.
        // Without this, the slave FD would remain open until
        // this function returns, preventing EOF delivery to
        // the reader.
        drop(controlled);

        // Wait for the reader task to complete.
        // Now that controlled is dropped, the reader will get
        // EOF on its next read() call and exit cleanly.
        let _ = reader_handle.await.into_diagnostic()??;

        Ok(status)
    }).await.into_diagnostic()?
}
```

### Running the POC

1. **Create a new Rust project:**

   ```shell
   cargo new pty_cargo_build_progress_osc_codes
   cd pty_cargo_build_progress_osc_codes
   ```

2. **Update `Cargo.toml`:**

   ```toml
   [package]
   name = "pty_cargo_build_progress_osc_codes"
   version = "0.1.0"
   edition = "2021"

   [dependencies]
   portable-pty = "0.8"
   tokio = { version = "1.0", features = ["full"] }
   miette = { version = "7.2", features = ["fancy"] }
   ```

3. **Replace `src/main.rs` with the code above**

4. **Run the POC:**

   ```shell
   cargo run
   ```

### Expected Output

When running in a project with dependencies, you should see output like:

```
Starting Cargo build with OSC capture...

📊 Build progress: 0.0%
📊 Build progress: 12.5%
📊 Build progress: 25.0%
📊 Build progress: 37.5%
📊 Build progress: 50.0%
📊 Build progress: 75.0%
📊 Build progress: 100.0%

✓ Progress tracking cleared
✅ Build completed with status: exit status: 0
```

### Troubleshooting

1. **No OSC sequences detected:**

   - Ensure the project being built has enough compilation units to trigger progress reporting
   - Try building a larger project or one with dependencies
   - Verify the TERM_PROGRAM environment variable is set correctly

2. **Build output mixed with progress:**

   - Uncomment the `print!("{}", text);` line to see full cargo output
   - OSC sequences are embedded in the normal output stream

3. **Permission errors:**
   - Some systems may require additional permissions for PTY creation
   - The portable-pty crate handles most platform differences automatically

## Environment Considerations

- **CI/CD**: Progress bars (and OSC) disabled when `CI` env var is set
- **Quiet mode**: No progress or OSC when `--quiet` flag used
- **TERM=dumb**: Progress disabled for dumb terminals
- **Non-TTY**: OSC only emitted when stderr is a TTY

## Testing

To test OSC emission:

1. Set `TERM_PROGRAM=WezTerm` (or use actual WezTerm)
2. Run `cargo build` on a large project
3. Monitor terminal title bar for progress updates
4. Or capture stderr and look for `\x1b]9;4;` sequences

## References

- [ConEmu OSC Documentation](https://conemu.github.io/en/AnsiEscapeCodes.html#ConEmu_specific_OSC)
- [OSC Escape Codes Overview](https://blog.vucica.net/2017/07/what-are-osc-terminal-control-sequences-escape-codes.html)
- [ANSI Escape Code Wikipedia](https://en.wikipedia.org/wiki/ANSI_escape_code)

## Build with Naz video series on developerlife.com YouTube channel

You can watch Rust live coding videos with Naz on the
[developerlife.com YouTube channel](https://www.youtube.com/@developerlifecom).

- [YT channel](https://www.youtube.com/@developerlifecom)
- Playlists
  - [Build with Naz, Linux TTY, process, signals, commands in async Rust](https://www.youtube.com/watch?v=bolScvh4x7I&list=PLofhE49PEwmw3MKOU1Kn3xbP4FRQR4Mb3)
  - [Build with Naz, fundamental effective Rust](https://www.youtube.com/playlist?list=PLofhE49PEwmza94sS7UmJnN9gSCHTVTfz)
  - [Build with Naz, effective async Rust and tokio](https://www.youtube.com/playlist?list=PLofhE49PEwmwO69E7eiQ-ewnMME8ydgQ5)
  - [Build with Naz, async readline and spinner for CLI in Rust](https://www.youtube.com/watch?v=3vQJguti02I&list=PLofhE49PEwmwelPkhfiqdFQ9IXnmGdnSE)
  - [Build with Naz, testing in Rust](https://www.youtube.com/watch?v=Xt495QLrFFk&list=PLofhE49PEwmwLR_4Noa0dFOSPmSpIg_l8)
