---
title: "Build with Naz : Explore Linux TTY, process, signals w/ Rust"
author: Nazmul Idris
date: 2024-08-20 15:00:00+00:00
excerpt: |
    This article, along with related videos and the repository, explores Linux TTY, shells,
    processes, sessions, jobs, PTYs, signals, and more using Rust. It explains /dev/tty and
    describes how terminal libraries like crossterm and termion build on top of stdio
    and /dev/tty. The article provides examples of using Rust to send and receive POSIX
    signals, communicate with processes via IPC, and spawn processes. Additionally, it
    includes examples of using PTY in Linux and controlling external commands (such as
    binaries like bash) using asynchronous Rust.
layout: post
categories:
  - Rust
  - CLI
  - Server
  - TUI
---

<img class="post-hero-image" src="{{ 'assets/linux-tty-proc-async-rust.svg' | relative_url }}"/>

<!-- TOC -->

- [Introduction](#introduction)
- [Prerequisite](#prerequisite)
- [GitHub repo for this article](#github-repo-for-this-article)
- [Related YouTube videos for this article](#related-youtube-videos-for-this-article)
  - [Part 1 / 3 : background info](#part-1--3--background-info)
  - [Part 2 / 3 : examples of send & recieve signals, proc spawn, and IPC](#part-2--3--examples-of-send--recieve-signals-proc-spawn-and-ipc)
  - [Part 3 / 3 : run tokio::process::Command in async Rust](#part-3--3--run-tokioprocesscommand-in-async-rust)
- [Limitations of using TTY in Linux, and why we like userland terminal emulators PTY](#limitations-of-using-tty-in-linux-and-why-we-like-userland-terminal-emulators-pty)
  - [Kernel TTY 👎🏽](#kernel-tty-)
  - [Userland PTY 👍🏽](#userland-pty-)
- [Examples of using PTY in Linux](#examples-of-using-pty-in-linux)
  - [Using redirection to write to another PTY run command in left terminal, see output in right terminal](#using-redirection-to-write-to-another-pty-run-command-in-left-terminal-see-output-in-right-terminal)
  - [Using redirection to read from another PTY type in left terminal, see it in right terminal](#using-redirection-to-read-from-another-pty-type-in-left-terminal-see-it-in-right-terminal)
  - [Breaking things in raw mode.](#breaking-things-in-raw-mode)
- [Shells, processes, sessions, jobs, PTYs, signals](#shells-processes-sessions-jobs-ptys-signals)
  - [Background information knowledgebase](#background-information-knowledgebase)
    - [File descriptors and processes, ulimit, stdin, stdout, stderr, pipes](#file-descriptors-and-processes-ulimit-stdin-stdout-stderr-pipes)
    - [Unix shells that run in terminals to execute built-in and program commands](#unix-shells-that-run-in-terminals-to-execute-built-in-and-program-commands)
      - [What is the relationship between linux shells, subshells, and fork, exec, and wait patterns?](#what-is-the-relationship-between-linux-shells-subshells-and-fork-exec-and-wait-patterns)
      - [Does exec change the current working directory or affect environment variables in the parent?](#does-exec-change-the-current-working-directory-or-affect-environment-variables-in-the-parent)
      - [Then how does the cd command change the current working directory of a shell?](#then-how-does-the-cd-command-change-the-current-working-directory-of-a-shell)
      - [How do subshells work, in the case where I don't the shell's environment to be affected at all?](#how-do-subshells-work-in-the-case-where-i-dont-the-shells-environment-to-be-affected-at-all)
      - [Deep dive of all this information in video format](#deep-dive-of-all-this-information-in-video-format)
    - [Processes, sessions, jobs, PTYs, signals using C](#processes-sessions-jobs-ptys-signals-using-c)
- [What is /dev/tty?](#what-is-devtty)
  - [How is crossterm built on top of stdio, PTY, etc?](#how-is-crossterm-built-on-top-of-stdio-pty-etc)
  - [How is termion built on top of stdio, PTY, etc?](#how-is-termion-built-on-top-of-stdio-pty-etc)
- [List of signals](#list-of-signals)
- [🦀 Sending and receiving signals in Rust](#-sending-and-receiving-signals-in-rust)
    - [Example using tokio to receive signals](#example-using-tokio-to-receive-signals)
    - [Example using signal-hook and signal-hook-tokio](#example-using-signal-hook-and-signal-hook-tokio)
- [🦀 Process spawning in Rust](#-process-spawning-in-rust)
    - [Example using procspawn to spawn processes](#example-using-procspawn-to-spawn-processes)
    - [Example using procspawn to spawn processes w/ ipc-channel](#example-using-procspawn-to-spawn-processes-w-ipc-channel)
- [🦀 Run tokio:process::Command in async Rust](#-run-tokioprocesscommand-in-async-rust)
  - [Example running echo process programmatically](#example-running-echo-process-programmatically)
  - [Example piping input to cat process programmatically](#example-piping-input-to-cat-process-programmatically)
  - [Example programmatically providing input into stdin and getting output from stdout of a process](#example-programmatically-providing-input-into-stdin-and-getting-output-from-stdout-of-a-process)
  - [Example programmatically piping the output of one process into another](#example-programmatically-piping-the-output-of-one-process-into-another)
  - [Example using r3bl_terminal_async to send commands to a long running bash child process](#example-using-r3bl_terminal_async-to-send-commands-to-a-long-running-bash-child-process)
- [Build with Naz video series on developerlife.com YouTube channel](#build-with-naz-video-series-on-developerlifecom-youtube-channel)

<!-- /TOC -->

## Introduction
<a id="markdown-introduction" name="introduction"></a>

This article, along with related videos and the repository, explores Linux TTY, shells,
processes, sessions, jobs, PTYs, signals, and more using Rust. It explains `/dev/tty` and
describes how terminal libraries like `crossterm` and `termion` build on top of `stdio`
and `/dev/tty`. The article provides examples of using Rust to send and receive POSIX
signals, communicate with processes via IPC, and spawn processes. Additionally, it
includes examples of using PTY in Linux and controlling external commands (such as
binaries like `bash`) using asynchronous Rust.

## Prerequisite
<a id="markdown-prerequisite" name="prerequisite"></a>

Read all about TTY history and implementation in Linux
[here](https://www.linusakesson.net/programming/tty/) before reading this repo and doing
the exercises here. There is so much background history and information in this article
that is a prerequisite to understanding anything in this repo.

## GitHub repo for this article
<a id="markdown-github-repo-for-this-article" name="github-repo-for-this-article"></a>

Here's the [`tty`
repo](https://github.com/nazmulidris/rust-scratch/blob/main/tty/README.md#list-of-signals)
containing the source code for this article and the videos.

## Related YouTube videos for this article
<a id="markdown-related-youtube-videos-for-this-article" name="related-youtube-videos-for-this-article"></a>

This article is a companion to the following YouTube videos. If you like to learn via
video, please watch the companion videos on the [developerlife.com YouTube
channel](https://www.youtube.com/@developerlifecom). Please
[subscribe](https://www.youtube.com/@developerlifecom?sub_confirmation=1) to the channel.

> ⏯️ Here's the [TTY
> playlist](https://www.youtube.com/watch?v=bolScvh4x7I&list=PLofhE49PEwmw3MKOU1Kn3xbP4FRQR4Mb3)
> containing all these videos.

### Part 1 / 3 : background info
<a id="markdown-part-1-%2F-3-%3A-background-info" name="part-1-%2F-3-%3A-background-info"></a>

<!-- video tty-1 -->
<iframe
    src="https://www.youtube.com/embed/bolScvh4x7I?si=9Cm95eajpdEym0zX"
    title="YouTube video player" frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    referrerpolicy="strict-origin-when-cross-origin"
    allowfullscreen
    >
</iframe>

<br/>

### Part 2 / 3 : examples of send & recieve signals, proc spawn, and IPC
<a id="markdown-part-2-%2F-3-%3A-examples-of-send-%26-recieve-signals%2C-proc-spawn%2C-and-ipc" name="part-2-%2F-3-%3A-examples-of-send-%26-recieve-signals%2C-proc-spawn%2C-and-ipc"></a>

<!-- video tty-2 -->
<iframe
    src="https://www.youtube.com/embed/58_9yjLI4WA?si=-CZA8vZGnVTJ5ILD"
    title="YouTube video player" frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    referrerpolicy="strict-origin-when-cross-origin"
    allowfullscreen
    >
</iframe>

<br/>

### Part 3 / 3 : run tokio::process::Command in async Rust
<a id="markdown-part-3-%2F-3-%3A-run-tokio%3A%3Aprocess%3A%3Acommand-in-async-rust" name="part-3-%2F-3-%3A-run-tokio%3A%3Aprocess%3A%3Acommand-in-async-rust"></a>

<!-- video tty-3 -->
<iframe
    src="https://www.youtube.com/embed/8JeL1sGozO4?si=9i1-booV0MoQXRGg"
    title="YouTube video player" frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    referrerpolicy="strict-origin-when-cross-origin"
    allowfullscreen
    >
</iframe>

<br/>

## Limitations of using TTY in Linux, and why we like userland terminal emulators (PTY)
<a id="markdown-limitations-of-using-tty-in-linux%2C-and-why-we-like-userland-terminal-emulators-pty" name="limitations-of-using-tty-in-linux%2C-and-why-we-like-userland-terminal-emulators-pty"></a>

### Kernel TTY 👎🏽
<a id="markdown-kernel-tty-%F0%9F%91%8E%F0%9F%8F%BD" name="kernel-tty-%F0%9F%91%8E%F0%9F%8F%BD"></a>

To switch to TTYs in Linux, press:

- <kbd>Ctrl + Alt + F3</kbd> to <kbd>Ctrl + Alt + F4</kbd>. To access two TTYs, one on <kbd>F3</kbd>
  and the other on <kbd>F4</kbd>.
- To switch back to the TTY in which the GUI is running, press <kbd>Ctrl + Alt + F2</kbd>.

In the Linux kernel, the TTY driver and line discipline provide basic line editing (and the
implementation of `cooked` or `raw` mode), and there is no
[`UART`](https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter) or physical
terminal involved. Instead, a video terminal (a complex state machine including a frame buffer of
characters and graphical character attributes) is emulated in software, and
[[video] rendered to a VGA display](https://www.youtube.com/watch?v=aAuw2EVCBBg).

> So if you run `edi` in a TTY, you will see that the font rendering and colors are different than
> in a GUI terminal emulator. However it still runs.

### Userland PTY 👍🏽
<a id="markdown-userland-pty-%F0%9F%91%8D%F0%9F%8F%BD" name="userland-pty-%F0%9F%91%8D%F0%9F%8F%BD"></a>

The (kernel TTY) console subsystem is somewhat rigid. Things get more flexible (and abstract) if we
move the terminal emulation into userland. This is how `xterm` and its clones work. To facilitate
moving the terminal emulation into userland, while still keeping the TTY subsystem (session
management and line discipline) intact, the pseudo terminal or PTY was invented. And as you may have
guessed, things get even more complicated when you start running pseudo terminals inside pseudo
terminals, aka `screen` or `ssh`.

> The primary use case for r3bl code is to run in this terminal emulator environment in userland and
> not the TTY environment supplied by the Linux kernel itself.

## Examples of using PTY in Linux
<a id="markdown-examples-of-using-pty-in-linux" name="examples-of-using-pty-in-linux"></a>

Each terminal in Linux is associated with a PTY (pseudo terminal). This is the device provided by
each terminal emulator program instance (aka process) that is currently running on the system. Use
the following command to get a list of all PTYs on the system.

```shell
ls /dev/pts
```

Here's sample output:

```
crw--w---- nazmul tty  0 B Wed Jul 17 11:36:35 2024  0
crw--w---- nazmul tty  0 B Wed Jul 17 11:38:32 2024  1
crw--w---- nazmul tty  0 B Wed Jul 17 11:38:06 2024  10
crw--w---- nazmul tty  0 B Wed Jul 17 11:23:20 2024  11
crw--w---- nazmul tty  0 B Sun Jul 14 16:19:36 2024  2
crw--w---- nazmul tty  0 B Mon Jul 15 13:22:48 2024  3
crw--w---- nazmul tty  0 B Tue Jul 16 09:58:08 2024  4
crw--w---- nazmul tty  0 B Wed Jul 17 10:34:48 2024  5
crw--w---- nazmul tty  0 B Wed Jul 17 11:30:32 2024  7
crw--w---- nazmul tty  0 B Wed Jul 17 11:36:36 2024  8
crw--w---- nazmul tty  0 B Wed Jul 17 11:30:48 2024  9
c--------- root   root 0 B Sat Jul 13 18:23:41 2024  ptmx
```

So which PTY is associated with the currently open terminal? Run the following command to get the
TTY number of the currently open terminal.

```shell
set my_tty_id (tty)
echo $my_tty_id
```

It will output something like this:

```
/dev/pts/1
```

Each `/dev/pts/*` is a file. And you can read / write / redirect to these files just like any other
file.

For the following examples, let's assume that you have 2 terminal emulator app windows open. One on
the left, and another one on the right.

```
┌────────────────────────────────┐  ┌────────────────────────────────┐
│                                │  │                                │
│    LEFT TERMINAL               │  │    RIGHT TERMINAL              │
│    /dev/pts/1                  │  │    /dev/pts/2                  │
│                                │  │                                │
└────────────────────────────────┘  └────────────────────────────────┘
```

### Using redirection to write to another PTY (run command in left terminal, see output in right terminal)
<a id="markdown-using-redirection-to-write-to-another-pty-run-command-in-left-terminal%2C-see-output-in-right-terminal" name="using-redirection-to-write-to-another-pty-run-command-in-left-terminal%2C-see-output-in-right-terminal"></a>

Let's say you have 2 terminals open, and one has the PTY number `/dev/pts/1` (on the left) and the
other has the TTY number `/dev/pts/2` (on the right).

From the left PTY `/dev/pts/1`, you can write to the right PTY `/dev/pts/2` using the following
command, and you will see "Hello, World!" in the right PTY.

```shell
# Run this in left terminal /dev/pts/1
echo "Hello, World!" > /dev/pts/2 # You will see this in the right terminal /dev/pts/2
```

### Using redirection to read from another PTY (type in left terminal, see it in right terminal)
<a id="markdown-using-redirection-to-read-from-another-pty-type-in-left-terminal%2C-see-it-in-right-terminal" name="using-redirection-to-read-from-another-pty-type-in-left-terminal%2C-see-it-in-right-terminal"></a>

From the right PTY `/dev/pts/2` you can read input from the left PTY `/dev/pts/1` using the
following command.

```shell
# Run this in right terminal /dev/pts/2
cat /dev/pts/1
```

Type the following in the left PTY.

```shell
# Run this in left terminal /dev/pts/1
abcdefgh
```

You will see the following output in the right PTY: `abcdefgh`.

### Breaking things in raw mode.
<a id="markdown-breaking-things-in-raw-mode." name="breaking-things-in-raw-mode."></a>

On the **right** terminal, run the following commands.

```shell
vi &
jobs
```

Here you will see the job number of the `vi` process. And you will see that it is in the background.

If you run `ps l` you will see the states of all the processes that are running. If you run `ps -l`
you will this information on just the processes spawned in the right terminal. For example:

```
F S   UID     PID    PPID  C PRI  NI ADDR SZ WCHAN  TTY          TIME CMD
0 S  1000  540327  540177  0  80   0 - 62854 futex_ pts/8    00:00:01 fish
0 T  1000  554675  540327  0  80   0 -  3023 do_sig pts/8    00:00:00 vi
4 R  1000  554850  540327  0  80   0 -  3478 -      pts/8    00:00:00 ps
```

Now if you bring `vi` to the foreground by running `fg`. The `vi` process is now in raw mode, and
the shell is no longer interpreting the input. It won't know what to do with input that comes in
over `stdin`.

Run `echo "foo" > /dev/pts/2` in the **left** terminal, you will see that the `vi` process gets
messed up, since it doesn't really interpret that input (as it's reading directly from keyboard and
mouse). However, the shell will send that output to `vi` and it's UI will be messed up. The same
thing happens if you use `micro` or `nano`.

```
┌────────────────────────────────┐  ┌────────────────────────────────┐
│    LEFT TERMINAL               │  │    RIGHT TERMINAL              │
│    /dev/pts/1                  │  │    /dev/pts/2                  │
│                                │  │                                │
│                                │  │  > vi &                        │
│                                │  │  > jobs                        │
│                                │  │  > fg                          │
│  > echo "foo" > /dev/pts/2     │  │  > # vi is messed up           │
└────────────────────────────────┘  └────────────────────────────────┘
```

To terminate the `vi` process (or many of them), run `killall -9 vi`. That sends the `SIGKILL`
signal to all the `vi` processes.

## Shells, processes, sessions, jobs, PTYs, signals
<a id="markdown-shells%2C-processes%2C-sessions%2C-jobs%2C-ptys%2C-signals" name="shells%2C-processes%2C-sessions%2C-jobs%2C-ptys%2C-signals"></a>

Let's say in a new terminal emulator program `xterm`, and then you run the following commands in
`fish`:

```shell
cat &
ls | sort
```

What happens here? What sessions and jobs are created? What about the pipe?

There are 4 jobs:

1. The job that runs `xterm` itself.

- This does not have any `stdin`, `stdout`, `stderr` `fd`s associated with it.
- This does not have a PTY associated with it.

2. The job that runs `bash` itself.

- This has `stdin`, `stdout`, `stderr` (from `xterm`), lets say, `/dev/pts/0`.
- This has a PTY associated with it, lets say, `/dev/pts/0`.

3. The job that runs `cat` in the background.

- This has `stdin`, `stdout`, `stderr` (from `xterm`), `/dev/pts/0`.
- This has a PTY associated with it, `/dev/pts/0`.

4. The job that runs `ls | sort` pipeline. This job has 2 processes inside of it which are spawned
   in parallel due to the pipe: 4.1. The process that runs `ls`.
   - This has `stdin`, `stderr` (from `xterm`), `/dev/pts/0`.
   - Due to the pipe `stdout` is set to `pipe0`.
   - This has a PTY associated with it, `/dev/pts/0`. 4.2. The process that runs `sort`.
   - This has `stdout`, `stderr` (from `xterm`), `/dev/pts/0`.
   - Due to the pipe, this has `stdin` set to `pipe0`.
   - This has a PTY associated with it, `/dev/pts/0`.

The basic idea is that every pipeline is a job, because every process in a pipeline should be
manipulated (stopped, resumed, killed) simultaneously. That's why `kill` allows you to send signals
to entire process groups. By default, `fork` places a newly created child process in the same
process group as its parent, so that e.g. a <kbd>^C</kbd> from the keyboard will affect both parent
and child. But the shell, as part of its session leader duties, creates a new process group every
time it launches a pipeline.

The TTY driver keeps track of the foreground process group id, but only in a passive way. The
session leader has to update this information explicitly when necessary. Similarly, the TTY driver
keeps track of the size of the connected terminal, but this information has to be updated
explicitly, by the terminal emulator or even by the user.

Several processes have `/dev/pts/0` attached to their standard input. With these constrains:

1. Only the foreground job (the `ls | sort` pipeline) will receive input from the TTY.
2. Likewise, only the foreground job will be allowed to write to the TTY device (in the default
   configuration).
3. If the `cat` process were to attempt to write to the TTY, the kernel would suspend it using a
   signal.

### Background information (knowledgebase)
<a id="markdown-background-information-knowledgebase" name="background-information-knowledgebase"></a>

The following sections are a deep live of the Linux kernel and how it works with processes, file
descriptors, shells, and PTYs.

#### File descriptors and processes, ulimit, stdin, stdout, stderr, pipes
<a id="markdown-file-descriptors-and-processes%2C-ulimit%2C-stdin%2C-stdout%2C-stderr%2C-pipes" name="file-descriptors-and-processes%2C-ulimit%2C-stdin%2C-stdout%2C-stderr%2C-pipes"></a>

Here's a
[[video] What's behind a file descriptor in Linux? Also, i/o redirection with `dup2`.](https://youtu.be/rW_NV6rf0rM?si=wcEkGPXnXzKeBn_G)
that goes into file descriptors, pipes, and process forking in Linux.

#### Unix shells (that run in terminals to execute built-in and program commands)
<a id="markdown-unix-shells-that-run-in-terminals-to-execute-built-in-and-program-commands" name="unix-shells-that-run-in-terminals-to-execute-built-in-and-program-commands"></a>

##### What is the relationship between linux shells, subshells, and fork, exec, and wait patterns?
<a id="markdown-what-is-the-relationship-between-linux-shells%2C-subshells%2C-and-fork%2C-exec%2C-and-wait-patterns%3F" name="what-is-the-relationship-between-linux-shells%2C-subshells%2C-and-fork%2C-exec%2C-and-wait-patterns%3F"></a>

In Linux, shells, subshells, and the fork-exec-wait pattern are interconnected concepts that play a
crucial role in process management and execution. Here's how they relate to each other:

1. **Shells**: A shell is a command-line interpreter that allows users to interact with the
   operating system. Shells provide a way for users to run commands, launch programs, and manage
   processes. Examples of popular shells in Linux include Bash, Zsh, and Fish.

2. **Fork-Exec-Wait Pattern**: This pattern is commonly used in shell scripting to spawn new
   processes and manage their execution. By forking a new process, executing a different program in
   the child process, and then waiting for the child process to finish, the shell can run multiple
   commands concurrently and coordinate their execution. If the parent does not wait for the child
   process to finish, the child is a zombie process.

   - **Fork**: When a process wants to execute a new program, it creates a copy of itself using the
     `fork()` system call. This creates a new process (child process) that is an exact copy of the
     original process (parent process) at the time of the `fork()` call. It needs to do this since
     `exec()`, which is called next, will swap the program binaries of the process which calls it!
     If it doesn't spawn a child, then the parent will cease to exist in memory after `exec()` is
     called.
   - **Exec**: After forking, the child process uses the `exec()` system call to replace its memory
     space with a new program. This allows the child process to run a different program than the
     parent process. The `exec()` system call loads the new program into the child process's memory
     and starts its execution.
   - **Wait**: After forking and executing a new program, the parent process may need to wait for
     the child process to finish its execution. The parent process can use the `wait()` system call
     to wait for the child process to terminate. This ensures that the parent process does not
     continue its execution until the child process has completed its task.

3. **Subshells**: A subshell is a separate instance of the shell that is spawned to execute a
   command or a group of commands. Subshells are created within the parent shell and can be used to
   run commands in a separate environment without affecting the parent shell.

> You can learn more about each of these system calls on your Linux machine simply by running
> `bash -c "man fork"`, `bash -c "man exec"`, and `bash -c "man wait"`. The `bash -c` is needed only
> if you're running some other shell like `fish` and not `bash`.

The relationship between these concepts is as follows:

- A shell process (the parent) creates a clone of their "self" process using `fork()`, called a
  child process. And then they use `exec()` to replace the memory space of the child process with a
  new program. Then the parent process waits for the child process to finish.
- The fork-exec-wait pattern is a common technique used in shells and subshells to spawn new
  processes, execute programs, and coordinate their execution.
- Shells can create subshells to run commands in a separate environment. For example if you want to
  run `cd` (which is a shell built-in command and not a external "program" command) and you don't
  want this to affect the parent shell, you can run it in a subshell.

Overall, these concepts work together to facilitate process management, execution, and command
interpretation in a Linux environment.

##### Does exec() change the current working directory or affect environment variables in the parent?
<a id="markdown-does-exec-change-the-current-working-directory-or-affect-environment-variables-in-the-parent%3F" name="does-exec-change-the-current-working-directory-or-affect-environment-variables-in-the-parent%3F"></a>

Running `exec()` on the child process does not change the current working directory of the parent
process.

When a process calls the `exec()` system call in Linux, it replaces its current image with a new
program. The `exec()` system call loads a new program into the process's memory space and starts its
execution.

Here's how `exec()` affects the current working directory and environment variables:

1. **Current Working Directory**: When a child process calls `exec()`, the current working directory
   of the parent process remains unchanged. The new program loaded by `exec()` will start executing
   with the same working directory as the original process. Therefore, the current working directory
   of the parent process is not affected by the child's `exec()` call.

2. **Environment Variables**: The environment of the new program loaded by `exec()` can be set
   explicitly by the program itself or inherited from the parent process. If the new program does
   not explicitly modify the environment variables, it will inherit the environment variables from
   the parent process. Any changes made to environment variables in the child process after the
   `exec()` call will not affect the environment variables of the parent process.

##### Then how does the cd command change the current working directory of a shell?
<a id="markdown-then-how-does-the-cd-command-change-the-current-working-directory-of-a-shell%3F" name="then-how-does-the-cd-command-change-the-current-working-directory-of-a-shell%3F"></a>

The `cd` command is a special command called a "shell built-in" command; there are about ~70 of
these. `echo`, `source` are examples of these "built-in" commands. These commands are built into the
shell itself. It is not a "external executable program" command like `ls`. So a shell does not have
to `fork` and `exec` to run these commands. The shell runs them inside of it's own "parent" process,
which affects "self".

If you think about it, `cd` has to be a built-in command since we know that child processes can't
affect the environment of the parent process, and the current working directory is part of a
process' environment.

> Watch this [video](https://youtu.be/GA2mIUQq48s?si=Sfbpre-MeNXlND_b&t=820) to get an understanding
> of `built-in` commands vs `external executable program` commands.

Let's say you want to `cd` into a folder but you don't want this to affect the parent shell. How do
you do this? This is where subshells come into play. If you're using `fish`, then a subshell is like
running `fish -c` with whatever is typed in between `""`.

##### How do subshells work, in the case where I don't the shell's environment to be affected at all?
<a id="markdown-how-do-subshells-work%2C-in-the-case-where-i-don't-the-shell's-environment-to-be-affected-at-all%3F" name="how-do-subshells-work%2C-in-the-case-where-i-don't-the-shell's-environment-to-be-affected-at-all%3F"></a>

In a Linux shell, a subshell is a separate instance of the shell that is spawned to execute a
command or a group of commands. When a user types a command to execute, the shell creates a subshell
to run that command.

Subshells are useful for various purposes, such as:

1. Running commands in a separate environment without affecting the parent shell.
2. Running commands in parallel to improve performance.
3. Running commands that need to be isolated from the parent shell.

Subshells are typically created using parentheses `()` in `fish` or the `$(...)` syntax in `bash`.
For example, when you run a command within parentheses like this:

```shell
(command1; command2)
```

The commands `command1` and `command2` will be executed in a subshell. Once the commands finish
executing, the subshell exits, and the parent shell continues its operation. If you run the `cd ..`
command in a subshell, it won't change the current working directory of the shell!

Subshells are used to manage sessions and jobs and pipelines. Things like foreground and background
jobs are managed using subshells. And signals are sent to processes using subshells in a pipeline.

> Watch this [video](https://youtu.be/N8kT2XRNEAg?si=iiv6i3mO6Lxi8qb1&t=60) to get an understanding
> of subshells, signals, jobs, pipelines, etc.

##### Deep dive of all this information in video format
<a id="markdown-deep-dive-of-all-this-information-in-video-format" name="deep-dive-of-all-this-information-in-video-format"></a>

Here's a
[[video playlist] Unix terminals and shells](https://www.youtube.com/playlist?list=PLFAC320731F539902)
that goes into details about shells, subshells, forking, exec (command), and wait works.

#### Processes, sessions, jobs, PTYs, signals using C
<a id="markdown-processes%2C-sessions%2C-jobs%2C-ptys%2C-signals-using-c" name="processes%2C-sessions%2C-jobs%2C-ptys%2C-signals-using-c"></a>

Here are some videos on forking processes, zombies, and signals in C:

- [[video] Create new process in C w/ `fork()`](https://www.youtube.com/watch?v=ss1-REMJ9GA)
- [[video] Send signals to processes in C w/ `kill()`, `signal()`, `sigaction()`](https://www.youtube.com/watch?v=83M5-NPDeWs)
- [[video] Zombie processes in C](https://www.youtube.com/watch?v=xJ8KenZw2ag)
- [[video] Stop process becoming zombie in C](https://www.youtube.com/watch?v=_5SCtRNnf9U)

## What is /dev/tty?
<a id="markdown-what-is-%2Fdev%2Ftty%3F" name="what-is-%2Fdev%2Ftty%3F"></a>

`/dev/tty` is a special file in Unix-like operating systems that represents the controlling terminal
of the current process. It is a synonym for the controlling terminal device file associated with the
process.

The controlling terminal is the terminal that is currently active and connected to the process,
allowing input and output interactions. It provides a way for processes to interact with the user
through the terminal interface.

The `/dev/tty` file can be used to read from or write to the controlling terminal.

In each process, `/dev/tty` is a synonym for the controlling terminal associated with the process
group of that process, if any. It is useful for programs or shell procedures that wish to be sure of
writing messages to or reading data from the terminal no matter how output has been redirected. It
can also be used for applications that demand the name of a file for output, when typed output is
desired and it is tiresome to find out what terminal is currently in use.

1. Definition from
   [IEEE Open Group Base Specifications for POSIX](https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap10.html).
2. You can see it used in `crossterm` crate
   [here](https://github.com/crossterm-rs/crossterm/blob/master/src/terminal/sys/file_descriptor.rs#L143).
3. Here's more info about this on
   [baeldung.com](https://www.baeldung.com/linux/monitor-keyboard-drivers#devtty).

### How is crossterm built on top of stdio, PTY, etc?
<a id="markdown-how-is-crossterm-built-on-top-of-stdio%2C-pty%2C-etc%3F" name="how-is-crossterm-built-on-top-of-stdio%2C-pty%2C-etc%3F"></a>

The [`crossterm`](https://github.com/crossterm-rs/crossterm) crate is built on top of Tokio's
[`mio`](https://docs.rs/mio/latest/mio/guide/index.html) crate, which uses Linux
[`epoll`](https://man7.org/linux/man-pages/man7/epoll.7.html) to work with file descriptors in an
async manner.

- Here's [`mio`'s `Poll`](https://docs.rs/mio/latest/mio/struct.Poll.html) using `epoll` under the
  hood.
- Here's an [example](https://docs.rs/mio/latest/mio/guide/index.html) of `mio` using Linux `epoll`
  in order to read from a file descriptor in an async manner.

> Linux `epoll` is able to work with `stdio` file descriptors (ie, `stdin`, `stdout`, `stderr`), as
> well as other file descriptors (network and file system). However, for throughput and performance
> (by reducing context switching and being efficient with buffers that hold IO data), Linux
> [`io_uring`](https://en.wikipedia.org/wiki/Io_uring) might be more suitable.

Here are some links to learn more about how `crossterm` works with `PTY`s and `stdio`:

- [Get a file descriptor for the TTY `tty_fd()`](https://github.com/crossterm-rs/crossterm/blob/master/src/terminal/sys/file_descriptor.rs#L143).
  It uses [`rustix::stdio::stdin()`](https://docs.rs/rustix/latest/rustix/stdio/fn.stdin.html) by
  default and falls back on `/dev/tty/`.
- This `fd` is used by
  [`UnixInternalEventSource`](https://github.com/crossterm-rs/crossterm/blob/master/src/event/source/unix/mio.rs#L35)
  which creates a `mio::Poll` object for the `fd`. This `Poll` object uses `epoll` under the hood.
  The
  [`EventSource` trait impl for `UnixInternalEventSource`](https://github.com/crossterm-rs/crossterm/blob/master/src/event/source/unix/mio.rs#L72)
  is used to actually
  [read](https://github.com/crossterm-rs/crossterm/blob/master/src/terminal/sys/file_descriptor.rs#L75)
  the bytes from the `fd` (using
  [`rustix::io::read()`](https://docs.rs/rustix/latest/rustix/io/fn.read.html)).
- Once a `Poll` has been created, a
  [`mio::Poll::registry()`](https://docs.rs/mio/latest/mio/struct.Registry.html) must be used to
  tell the OS to listen for events on the `fd`. A
  [source and interest must be registered](https://docs.rs/mio/latest/mio/guide/index.html#2-registering-event-source)
  with the registry next:
  - The `fd` [implements](https://docs.rs/mio/latest/mio/unix/struct.SourceFd.html) the
    [`Source` trait](https://docs.rs/mio/latest/mio/event/trait.Source.html) which
    [allows](https://docs.rs/mio/latest/mio/event/trait.Source.html#implementing-eventsource) `mio`
    to listen for events on the `fd`.
  - An `Interest::READABLE` must also be "registered" with the `registry`. For eg, for `stdin`, this
    tells the OS to listen for input from the keyboard, and wake the `Poll` when this is ready.
  - A `Token` is supplied that can be used when polling for events to see if they're available on
    the source. This happens in the
    [`loop`](https://docs.rs/mio/latest/mio/guide/index.html#3-creating-the-event-loop) that calls
    `poll()` to fill an `Event` buffer. If an event in this buffer matches the `Token`, then the
    `fd` is ready for reading.

You can see all the steps (outlined above) in action, in the following crates:

- [Guide in `mio` docs](https://docs.rs/mio/latest/mio/guide/index.html).
- [`mio.rs` file in `crossterm`](https://github.com/crossterm-rs/crossterm/blob/master/src/event/source/unix/mio.rs).
- This [PR](https://github.com/nazmulidris/crossterm/pull/1) in my fork of `crossterm` has
  `println!` traces so you can see how `mio` is used under the hood by `crossterm` to read from
  `stdin`.

### How is termion built on top of stdio, PTY, etc?
<a id="markdown-how-is-termion-built-on-top-of-stdio%2C-pty%2C-etc%3F" name="how-is-termion-built-on-top-of-stdio%2C-pty%2C-etc%3F"></a>

Here's a [PR](https://github.com/nazmulidris/termion/pull/1) to explore the examples in `termion`
crate. This is a beautifully simple and elegant crate that is much simpler than `crossterm`. It
simply uses the standard library and a few other crates to get bytes from `stdin` and write bytes to
`stdout`. It does not use `mio`, and neither does it support `async` `EventStream`. There is an
"async mode", which simply spawns another thread and uses a channel to send events to the main
thread.

## List of signals
<a id="markdown-list-of-signals" name="list-of-signals"></a>

Here are the reference docs on signals:
<!-- cspell:disable-next-line -->
- [POSIX](https://en.wikipedia.org/wiki/POSIX), pronounced "paw-siks", [signals](https://en.wikipedia.org/wiki/Signal_(IPC))
- [gnu libc termination signals](https://www.gnu.org/software/libc/manual/html_node/Termination-Signals.html)
- [gnu libc job control signals](https://www.gnu.org/software/libc/manual/html_node/Job-Control-Signals.html)

Here is a list of all the signals that a process might get:
[signals](https://www.linusakesson.net/programming/tty/#signal-madness:~:text=using%20a%20signal.-,Signal%20madness,-Now%20let%27s%20take).

You can also get a list of them using `kill -l`. It is different for `fish` and `bash`. However,
under the hood, the Linux kernel uses the same signal numbers for all shells.

<!-- cSpell:disable -->

````shell
$ fish -c "kill -l"
HUP INT QUIT ILL TRAP ABRT BUS FPE KILL USR1 SEGV USR2 PIPE ALRM TERM STKFLT
CHLD CONT STOP TSTP TTIN TTOU URG XCPU XFSZ VTALRM PROF WINCH POLL PWR SYS

```shell
$ bash -c "kill -l"
 1) SIGHUP	 2) SIGINT	 3) SIGQUIT	 4) SIGILL	 5) SIGTRAP
 6) SIGABRT	 7) SIGBUS	 8) SIGFPE	 9) SIGKILL	10) SIGUSR1
11) SIGSEGV	12) SIGUSR2	13) SIGPIPE	14) SIGALRM	15) SIGTERM
16) SIGSTKFLT	17) SIGCHLD	18) SIGCONT	19) SIGSTOP	20) SIGTSTP
21) SIGTTIN	22) SIGTTOU	23) SIGURG	24) SIGXCPU	25) SIGXFSZ
26) SIGVTALRM	27) SIGPROF	28) SIGWINCH	29) SIGIO	30) SIGPWR
31) SIGSYS	34) SIGRTMIN	35) SIGRTMIN+1	36) SIGRTMIN+2	37) SIGRTMIN+3
38) SIGRTMIN+4	39) SIGRTMIN+5	40) SIGRTMIN+6	41) SIGRTMIN+7	42) SIGRTMIN+8
43) SIGRTMIN+9	44) SIGRTMIN+10	45) SIGRTMIN+11	46) SIGRTMIN+12	47) SIGRTMIN+13
48) SIGRTMIN+14	49) SIGRTMIN+15	50) SIGRTMAX-14	51) SIGRTMAX-13	52) SIGRTMAX-12
53) SIGRTMAX-11	54) SIGRTMAX-10	55) SIGRTMAX-9	56) SIGRTMAX-8	57) SIGRTMAX-7
58) SIGRTMAX-6	59) SIGRTMAX-5	60) SIGRTMAX-4	61) SIGRTMAX-3	62) SIGRTMAX-2
63) SIGRTMAX-1	64) SIGRTMAX
````

<!-- cSpell:enable -->

Here are some important ones.

1. `SIGHUP`

- Default action: Terminate
- Possible actions: Terminate, Ignore, Function call
- `SIGHUP` is sent by the UART driver to the entire session when a hangup condition has been
  detected. Normally, this will kill all the processes. Some programs, such as `nohup` and `screen`,
  detach from their session (and TTY), so that their child processes won't notice a hangup.

2. `SIGINT`

- Default action: Terminate
- Possible actions: Terminate, Ignore, Function call
- `SIGINT` is sent by the TTY driver to the current foreground job when the interactive attention
  character (typically <kbd>^C</kbd>, which has ASCII code 3) appears in the input stream, unless
  this behavior has been turned off. Anybody with access permissions to the TTY device can change
  the interactive attention character and toggle this feature; additionally, the session manager
  keeps track of the TTY configuration of each job, and updates the TTY whenever there is a job
  switch.

3. `SIGQUIT`

- Default action: Core dump
- Possible actions: Core dump, Ignore, Function call
- `SIGQUIT` works just like SIGINT, but the quit character is typically <kbd>^\\</kbd> and the
  default action is different.

4. `SIGPIPE`

- Default action: Terminate
- Possible actions: Terminate, Ignore, Function call
- The kernel sends `SIGPIPE` to any process which tries to write to a pipe with no readers. This is
  useful, because otherwise jobs like `yes | head` would never terminate.

5. `SIGCHLD`

- Default action: Ignore
- Possible actions: Ignore, Function call
- When a process dies or changes state (stop/continue), the kernel sends a `SIGCHLD` to its parent
  process. The `SIGCHLD` signal carries additional information, namely the process id, the user id,
  the exit status (or termination signal) of the terminated process and some execution time
  statistics. The session leader (shell) keeps track of its jobs using this signal.

6. `SIGSTOP`

- Default action: Suspend
- Possible actions: Suspend
- This signal will unconditionally suspend the recipient, i.e. its signal action can't be
  reconfigured. Please note, however, that `SIGSTOP` isn't sent by the kernel during job control.
  Instead, <kbd>^Z</kbd> typically triggers a `SIGTSTP`, which can be intercepted by the
  application. The application may then e.g. move the cursor to the bottom of the screen or
  otherwise put the terminal in a known state, and subsequently put itself to sleep using `SIGSTOP`.

7. `SIGCONT`

- Default action: Wake up
- Possible actions: Wake up, Wake up + Function call
- `SIGCONT` will un-suspend a stopped process. It is sent explicitly by the shell when the user
  invokes the `fg` command. Since `SIGSTOP` can't be intercepted by an application, an unexpected
  `SIGCONT` signal might indicate that the process was suspended some time ago, and then
  un-suspended.

8. `SIGTSTP`

- Default action: Suspend
- Possible actions: Suspend, Ignore, Function call
- `SIGTSTP` works just like `SIGINT` and `SIGQUIT`, but the magic character is typically
  <kbd>^Z</kbd> and the default action is to suspend the process.

9. `SIGTTIN`

- Default action: Suspend
- Possible actions: Suspend, Ignore, Function call
- If a process within a background job tries to read from a TTY device, the TTY sends a `SIGTTIN`
  signal to the entire job. This will normally suspend the job.

10. `SIGTTOU`

- Default action: Suspend
- Possible actions: Suspend, Ignore, Function call
- If a process within a background job tries to write to a TTY device, the TTY sends a `SIGTTOU`
  signal to the entire job. This will normally suspend the job. It is possible to turn off this
  feature on a per-TTY basis.

11. `SIGWINCH`

- Default action: Ignore
- Possible actions: Ignore, Function call
- As mentioned, the TTY device keeps track of the terminal size, but this information needs to be
  updated manually. Whenever that happens, the TTY device sends `SIGWINCH` to the foreground job.
  Well-behaving interactive applications, such as editors, react upon this, fetch the new terminal
  size from the TTY device and redraw themselves accordingly.

## 🦀 Sending and receiving signals in Rust
<a id="markdown-%F0%9F%A6%80-sending-and-receiving-signals-in-rust" name="%F0%9F%A6%80-sending-and-receiving-signals-in-rust"></a>

| crate                                       | recv | send  |
| ------------------------------------------- | ---- | ----- |
| <https://docs.rs/tokio/latest/tokio/signal> | 🟢   | 🔴    |
| <https://crates.io/crates/ctrlc>            | 🟢   | 🔴    |
| <https://crates.io/crates/signal-hook>      | 🟢   | 🟢 \* |
| <https://docs.rs/nix/latest/nix/>           | 🟢   | 🟢    |

> \*: Via
> [`signal_hook::low_level::raise`](https://docs.rs/signal-hook/latest/signal_hook/low_level/fn.raise.html).

#### Example using tokio to receive signals
<a id="markdown-example-using-tokio-to-receive-signals" name="example-using-tokio-to-receive-signals"></a>

Please watch the live coding [videos](#related-youtube-videos-for-this-article) to get a
deep dive into what each line of code does.

Please clone this [repo](https://github.com/nazmulidris/rust-scratch) to your computer to
play w/ the examples in the [`rust-scratch/tty`
crate](https://github.com/nazmulidris/rust-scratch/blob/main/tty/README.md) shown below.

[`receive_signal.rs`](https://github.com/nazmulidris/rust-scratch/blob/main/tty/src/receive_signal.rs).
`tokio` has limited handling of signals. You can only receive certain signals, not send
them.

```rust
use miette::IntoDiagnostic;
use r3bl_rs_utils_core::ok;
use tokio::signal::unix;

#[tokio::main]
async fn main() -> miette::Result<()> {
    let signal = unix::SignalKind::window_change();
    let mut stream = unix::signal(signal).into_diagnostic()?;

    let mut tick_interval = tokio::time::interval(
        tokio::time::Duration::from_millis(500));

    let sleep_future = tokio::time::sleep(
        tokio::time::Duration::from_secs(5));
    tokio::pin!(sleep_future);

    let pid = std::process::id();
    println!("PID: {}", pid);

    // Copy child PID to clipboard.
    // Use `ClipboardProvider` trait.
    use cli_clipboard::ClipboardProvider as _;
    let mut ctx = cli_clipboard::ClipboardContext::new()
        .map_err(|e| miette::miette!(
            "couldn't create clip context: {}", e))?;
    ctx.set_contents(pid.to_string().to_owned())
        .map_err(|e| miette::miette!(
            "couldn't set clip contents: {}", e))?;
    ctx.get_contents()
        .map_err(|e| miette::miette!(
            "couldn't get clip contents: {}", e))?;

    loop {
        tokio::select! {
            // Respond to window change signal.
            _ = stream.recv() => {
                println!("\nSIGWINCH received");
                break;
            }

            // Sleep for 5 seconds & terminate the program if running.
            _ = &mut sleep_future => {
                println!("\nSlept for 5 seconds");
                break;
            }

            // Run at each tick interval.
            _ = tick_interval.tick() => {
                println!("Tick");
            }

            // Respond to ctrl-c signal.
            _ = tokio::signal::ctrl_c() => {
                println!("\nCtrl-C received");
                break;
            }
        }
    }

    ok!()
}
```

Here are some notes on the code:

- `tokio::signal::ctrl_c` is a utility function that creates a future that completes
  when `ctrl-c` is pressed. There is no need to write a signal stream for this like
  so:
  ```rust
  let mut stream_sigterm =
      tokio::signal::unix::signal(
          tokio::signal::unix::SignalKind::terminate())
          .into_diagnostic()?;
  loop {
      tokio::select! {
          _ = stream_sigterm.recv() => {
              println!("\nSIGTERM received");
              break;
          }
      }
  }
  ```
- `tokio::signal::unix::signal` is a lower level function that you can use to create a
  stream of signals of a given type (e.g., `tokio::signal::unix::SignalKind`). Some
  examples are:
  - `tokio::signal::unix::SignalKind::hangup`
  - `tokio::signal::unix::SignalKind::interrupt`
  - `tokio::signal::unix::SignalKind::pipe`
- There are limitations to what `tokio::signal::unix::SignalKind::from_raw` can do:
    - For example you can't just pass in `SIGSTOP` ie `19` and expect it to work. This
      is an [OS
      limitation](https://docs.rs/signal-hook/latest/signal_hook/#limitations) for both
      `SIGKILL` or `SIGSTOP`.
    - Here's a list of POSIX signals that are
      [`FORBIDDEN`](https://docs.rs/signal-hook/latest/signal_hook/low_level/fn.register.html#panics)
      from the `signal_hook` crate.
    - You can just pass the signal number directly to
      `tokio::signal::unix::SignalKind::from_raw`.
    - However, if you're doing more sophisticated things you might need to use the
      [signal-hook](https://github.com/vorner/signal-hook) crate (which not only
      supports sending and receiving signals, but also has async adapters for `tokio`).
    - Here are relevant docs:
        - [tokio::signal](https://docs.rs/tokio/latest/tokio/signal/index.html)
        - [tokio::signal::unix::signal](https://docs.rs/tokio/latest/tokio/signal/unix/fn.signal.html)
        - [tokio::signal::unix::SignalKind](https://docs.rs/tokio/latest/tokio/signal/unix/struct.SignalKind.html)

See it in action:

- Run the binary: `cargo run --bin send_receive_signal`
- Send signals to the process:
    - To get a list of all the signals that you can send to a process, you can run the
      following command: `kill -L`
    - To send Ctrl+C, aka, `SIGINT`, aka `tokio::signal::unix::SignalKind::interrupt`, to
      the process, you can run the following command: `kill -2 <PID>` or `kill -INT <PID>`
    - To send `SIGWINCH`, aka `tokio::signal::unix::SignalKind::window_change` to the
      process, simply change the terminal window size of the terminal that the process is
      running in. Or run the following command: `kill -28 <PID>` or `kill -WINCH <PID>`

> Other crate choices to receive signals:
>
> - [`ctrlc`](https://crates.io/crates/ctrlc)
> - [`signal-hook`](https://crates.io/crates/signal-hook)

#### Example using signal-hook and signal-hook-tokio
<a id="markdown-example-using-signal-hook-and-signal-hook-tokio" name="example-using-signal-hook-and-signal-hook-tokio"></a>

Please watch the live coding [videos](#related-youtube-videos-for-this-article) to get a
deep dive into what each line of code does.

Please clone this [repo](https://github.com/nazmulidris/rust-scratch) to your computer to
play w/ the examples in the [`rust-scratch/tty`
crate](https://github.com/nazmulidris/rust-scratch/blob/main/tty/README.md) shown below.

[`send_and_receive_signal.rs`](https://github.com/nazmulidris/rust-scratch/blob/main/tty/src/send_and_receive_signal.rs)
allows you to both send and receive signals in a process.

```rust
use futures::stream::StreamExt as _;
use miette::IntoDiagnostic;
use r3bl_rs_utils_core::ok;
use signal_hook::consts::signal::*;
use signal_hook_tokio::Signals;

#[tokio::main]
async fn main() -> miette::Result<()> {
    let pid = std::process::id();
    println!("PID: {}", pid);

    // Broadcast channel to shutdown the process.
    let (sender_shutdown_channel, _) =
        tokio::sync::broadcast::channel::<()>(1);

    // Register signal handlers.
    let signals_stream: Signals =
        Signals::new([SIGHUP, SIGTERM, SIGINT, SIGQUIT])
        .into_diagnostic()?;
    let signals_handle = signals_stream.handle();
    let join_handle_monitor_signals_task = tokio::spawn(
        handle_signals_task(
            signals_stream,
            sender_shutdown_channel.clone(),
        ));

    run_main_event_loop(sender_shutdown_channel.clone()).await;

    // Cleanup tasks after shutdown.
    signals_handle.close();
    join_handle_monitor_signals_task.await.into_diagnostic()?;

    ok!()
}

async fn run_main_event_loop(
    sender_shutdown_channel: tokio::sync::broadcast::Sender<()>
    ) {
    let mut receiver_shutdown_channel =
        sender_shutdown_channel.subscribe();

    let mut tick_interval = tokio::time::interval(
        std::time::Duration::from_millis(500));

    // Wait for 1 sec & then send SIGTERM signal.
    tokio::spawn(async move {
        tokio::time::sleep(
            tokio::time::Duration::from_secs(1)).await;
        _ = signal_hook::low_level::raise(SIGTERM);
        println!("🧨 Sent SIGTERM signal");
    });

    loop {
        tokio::select! {
            _ = tick_interval.tick() => {
                println!("Tick");
            }
            _ = receiver_shutdown_channel.recv() => {
                println!("Received shutdown signal");
                break;
            }
        }
    }
}

async fn handle_signals_task(
    mut signals_stream: Signals,
    sender_shutdown_channel: tokio::sync::broadcast::Sender<()>,
) {
    while let Some(signal) = signals_stream.next().await {
        match signal {
            SIGHUP | SIGTERM | SIGINT | SIGQUIT => {
                println!("📥 Received signal: {:?}", signal);
                _ = sender_shutdown_channel.send(());
            }
            _ => unreachable!(),
        }
    }
}
```

Notes on the code:

- Example of how to send and receive Linux (POSIX, Unix) signals in a process
  It uses the following crates to make this happen:
    - [signal-hook](https://docs.rs/signal-hook/)
    - [signal-hook-tokio](https://docs.rs/signal-hook-tokio/latest/signal_hook_tokio/)
- Signal handler registration limitations (to receive signals)
  POSIX allows signal handlers to be overridden in a process. This is a powerful feature
  that can be used to implement a wide variety of functionality.
    - However, there are
      [limitations](https://docs.rs/signal-hook/latest/signal_hook/#limitations) around
      overriding signal handlers in a process. For example, POSIX compliant operating
      systems will not allow you to override the
      [`SIGKILL`](https://docs.rs/signal-hook/latest/signal_hook/consts/signal/constant.SIGKILL.html)
      or
      [`SIGSTOP`](https://docs.rs/signal-hook/latest/signal_hook/consts/signal/constant.SIGSTOP.html)
      signals.
    - Here's a full list of
      [`FORBIDDEN`](https://docs.rs/signal-hook/latest/signal_hook/low_level/fn.register.html#panics)
      signals that will `panic` the `register` function, if used.
- The following dependencies need to be added to the `Cargo.toml` file for this to work:
  ```toml
  signal-hook = { version = "0.3.17" }
  signal-hook-tokio = {
      version = "0.3.1", features = ["futures-v0_3"] }
  futures = "0.3.30"
  ```

See it in action:

- Run the binary: `cargo run --bin send_and_receive_signal`

## 🦀 Process spawning in Rust
<a id="markdown-%F0%9F%A6%80-process-spawning-in-rust" name="%F0%9F%A6%80-process-spawning-in-rust"></a>

Please watch the live coding [videos](#related-youtube-videos-for-this-article) to get a
deep dive into what each line of code does.

Please clone this [repo](https://github.com/nazmulidris/rust-scratch) to your computer to
play w/ the examples in the [`rust-scratch/tty`
crate](https://github.com/nazmulidris/rust-scratch/blob/main/tty/README.md) shown below.

#### Example using procspawn to spawn processes
<a id="markdown-example-using-procspawn-to-spawn-processes" name="example-using-procspawn-to-spawn-processes"></a>

[`procspawn.rs`](https://github.com/nazmulidris/rust-scratch/blob/main/tty/src/procspawn.rs)
can be used to spawn child processes in Rust with great flexibility and control.

```rust
use miette::IntoDiagnostic;
use r3bl_rs_utils_core::ok;

fn main() -> miette::Result<()> {
    // A spawned process will execute every line of code up to here.
    procspawn::init();

    let pid_parent = std::process::id();

    let args: Vec<i64> = vec![1, 2, 3, 4];
    let (sum, pid_child, pid_child_from_clip) = configure_builder()
        .spawn(args, run_in_child_process)
        .join()
        .into_diagnostic()?
        .into_diagnostic()?;

    println!("Parent PID: {}", pid_parent);
    println!(
        "Child PID: {}, sum: {}, pid from clip: {}",
        pid_child, sum, pid_child_from_clip
    );

    assert_eq!(sum, 10);
    assert_eq!(pid_child, pid_child_from_clip);

    ok!()
}

// Create a new builder with stderr & stdout that's null.
fn configure_builder() -> procspawn::Builder {
    let mut it = procspawn::Builder::new();
    it.stderr(std::process::Stdio::null()); // Suppress stderr.
    it.stdout(std::process::Stdio::null()); // Suppress stdout.
    it
}

// This function will be executed in a child process.
fn run_in_child_process(
    /* serde */ param: Vec<i64>,
) -> std::result::Result<
    /* serde - Ok variant */
    (
        /* sum */ i64,
        /* pid */ String,
        /* pid from clip */ String,
    ),
    /* serde - Err variant */
    ClipboardError,
> {
    let pid_child = std::process::id();
    let sum = param.iter().sum();

    // Copy child pid to the clipboard.
    // Import `ClipboardProvider` trait.
    use cli_clipboard::ClipboardProvider as _;
    let mut ctx = cli_clipboard::ClipboardContext::new()
        .map_err(|_| ClipboardError::ContextUnavailable)?;
    ctx.set_contents(pid_child.to_string().to_owned())
        .map_err(|_| ClipboardError::SetContents)?;
    let pid_child_from_clip = ctx
        .get_contents()
        .map_err(|_| ClipboardError::GetContents)?;

    Ok((sum, pid_child.to_string(), pid_child_from_clip))
}

#[derive(
    Debug, serde::Deserialize, serde::Serialize, thiserror::Error
)]
pub enum ClipboardError {
    #[error("clipboard context unavailable")]
    ContextUnavailable,

    #[error("could not get clipboard contents")]
    GetContents,

    #[error("could not set clipboard contents")]
    SetContents,
}
```

Notes on the code:

- The [`procspawn`](https://docs.rs/procspawn/latest/procspawn/) crate provides the
  ability to spawn processes with a function similar to `thread::spawn`.
- Unlike `thread::spawn` data cannot be passed by the use of closures.
- Instead if must be explicitly passed as serializable object (specifically it must be
  `serde` serializable). Internally, the data is serialized using
  [`bincode`](https://docs.rs/procspawn/latest/procspawn/#bincode-limitations).
- The return value from the spawned closure also must be serializable and can then be
  retrieved from the returned join handle.
- If the spawned function causes a panic it will also be serialized across the process
  boundaries.
- Great [examples](https://github.com/mitsuhiko/procspawn/tree/master/examples) from the
  official docs.

See it in action:

- Run the binary: `cargo run --bin procspawn`

#### Example using procspawn to spawn processes w/ ipc-channel
<a id="markdown-example-using-procspawn-to-spawn-processes-w%2F-ipc-channel" name="example-using-procspawn-to-spawn-processes-w%2F-ipc-channel"></a>

[`procspawn_ipc_channel.rs`](https://github.com/nazmulidris/rust-scratch/blob/main/tty/src/procspawn_ipc_channel.rs)
can be used to manage complex IPC communication between parent and child processes.

```rust
use miette::IntoDiagnostic;
use r3bl_rs_utils_core::ok;

type Message = String;

const MSG_1: &str = "Hello";
const MSG_2: &str = "World";
const END_MSG: &str = "END";
const SHUTDOWN_MSG: &str = "SHUTDOWN";

fn main() -> miette::Result<()> {
    // A spawned process will execute every line of code up to here.
    procspawn::init();

    // Create a channel to send messages across processes.
    let (sender, receiver) = ipc_channel::ipc::channel::<Message>()
        .into_diagnostic()?;

    // Spawn a child process that will receive messages from the
    // parent process.
    let mut join_handle = configure_builder().spawn(
        /* arg from parent process */ receiver,
        /* param to child process; closure runs in child process */
        run_in_child_process,
    );

    parent_send_messages(sender)?;

    // Read the stdout, until EOF, of the child process into `buf`.
    let mut buf = String::new();
    // Import `Read` trait for `read_to_string`.
    use std::io::Read as _;
    let Some(stdout) = join_handle.stdout() else {
        miette::bail!("Failed to get stdout");
    };
    let bytes_read = stdout.read_to_string(&mut buf)
        .into_diagnostic()?;
    println!(
        "Output from child process: {:?}, bytes_read: {}",
        buf, bytes_read
    );

    // Make assertions.
    assert_eq!(buf, format!("{MSG_1}\n{MSG_2}\n{END_MSG}\n"));

    // Wait for the child process to exit and get its return value.
    join_handle.join().into_diagnostic()?;

    ok!()
}

fn parent_send_messages(
    sender: ipc_channel::ipc::IpcSender<Message>
) -> miette::Result<()>
{
    sender.send(MSG_1.to_string()).into_diagnostic()?;
    sender.send(MSG_2.to_string()).into_diagnostic()?;
    sender.send(SHUTDOWN_MSG.to_string()).into_diagnostic()?;
    ok!()
}

/// This function will be executed in the child process. It gets
/// [Message]s from the parent process and processes them.
fn run_in_child_process(
    receiver: ipc_channel::ipc::IpcReceiver<Message>
) {
    while let Ok(msg) = receiver.recv() {
        if msg == SHUTDOWN_MSG {
            break;
        }
        // Print the message to stdout.
        println!("{}", msg);
    }

    // Print `END_MSG` to stdout.
    println!("{END_MSG}");
}

/// Create a new builder with stdout piped and stderr muted.
fn configure_builder() -> procspawn::Builder {
    let mut it = procspawn::Builder::new();
    it.stdout(std::process::Stdio::piped());
    it.stderr(std::process::Stdio::null());
    it
}
```

Notes on the code:

- `ipc_channel::ipc::channel` is used to send messages across processes via IPC. These
  messages must be serializable.
- The parent process sends messages to the child process. This happens over an
  ipc_channel sender.
- The child process receives messages from the parent process. This happens over an
  ipc_channel receiver. The receiver is passed across process boundaries from
  the parent to the child process.

See it in action:

- Run the binary: `cargo run --bin procspawn_ipc_channel`

> Here's the [`procspawn` crate](https://crates.io/crates/procspawn) that we can use for this.

## 🦀 Run tokio:process::Command in async Rust
<a id="markdown-%F0%9F%A6%80-run-tokio%3Aprocess%3A%3Acommand-in-async-rust" name="%F0%9F%A6%80-run-tokio%3Aprocess%3A%3Acommand-in-async-rust"></a>

Please watch the live coding [videos](#related-youtube-videos-for-this-article) to get a
deep dive into what each line of code does.

> In `tokio` a good place to start is
> [`tokio::process`](https://docs.rs/tokio/latest/tokio/process/index.html) which mimics
> the `std::process` module.

### Example running echo process programmatically
<a id="markdown-example-running-echo-process-programmatically" name="example-running-echo-process-programmatically"></a>

Please clone this [repo](https://github.com/nazmulidris/rust-scratch) to your computer to
play w/ the examples in the [`rust-scratch/tty`
crate](https://github.com/nazmulidris/rust-scratch/blob/main/tty/README.md) shown below.

[`async_command_exec_1.rs`](https://github.com/nazmulidris/rust-scratch/blob/main/tty/src/async_command_exec_1.rs)

```rust
use crossterm::style::Stylize;
use miette::IntoDiagnostic;

#[tokio::main]
async fn main() -> miette::Result<()> {
    run_command_no_capture().await?;
    run_command_capture_output().await?;
    Ok(())
}

// - Run `echo hello world` and wait for it to complete.
// - Do not capture the output or provide the input.
async fn run_command_no_capture() -> miette::Result<()> {
    println!("{}", "run_command_no_capture".blue());

    // Without redirection, the output of the command will be
    // inherited from the process that starts the command. So
    // if this is running in a terminal, the output will be
    // printed to the terminal.
    //
    // Even though `spawn()` is called this child / command
    // doesn't make any progress until you call `wait().await`.
    let mut command = {
        let mut command = tokio::process::Command::new("echo");
        command
            .args(["hello", "world"])
            .stdin(std::process::Stdio::inherit())
            .stdout(std::process::Stdio::inherit())
            .stderr(std::process::Stdio::inherit());
        command
    };
    let mut child = command.spawn().into_diagnostic()?;

    // Wait for the command to complete. Don't capture the output,
    // it will go to `stdout` of the process running this program.
    let exit_status = child.wait().await.into_diagnostic()?;
    assert!(exit_status.success());

    // Print the exit status of the command.
    println!("exit status: {}", exit_status);

    Ok(())
}

// - Run `echo hello world` and wait for it to complete.
// - Capture its output and do not provide the input.
async fn run_command_capture_output() -> miette::Result<()> {
    println!("{}", "run_command_capture_output".blue());

    // Redirect the output of the command to a pipe `Stdio::piped()`.
    //
    // Even though `spawn()` is called this child / command doesn't
    // make any progress until you call `wait_with_out().await`.
    let mut command = {
        let mut command = tokio::process::Command::new("echo");
        command
            .args(["hello", "world"])
            .stdin(std::process::Stdio::null())
            .stdout(std::process::Stdio::piped())
            .stderr(std::process::Stdio::null());
        command
    };
    let child = command.spawn().into_diagnostic()?;

    // Wait for the command to complete and capture the output.
    // - Calling `wait()` consumes the child process, so we can't
    //   call `output.stdout` on it after this.
    // - That's why we use `wait_with_output()`, which actually
    //   returns a different type than `wait()`; this is also a
    //   great use of type state pattern.
    let output = child.wait_with_output().await.into_diagnostic()?;

    assert!(output.status.success());
    assert_eq!(output.stdout, b"hello world\n");

    Ok(())
}
```

Notes on the code:

- Run a command and wait for it to complete. Do not capture the output or provide the
  input.
- Run a command and capture the output. Do not provide the input. This example uses the
  [`tokio::process::Command`](https://docs.rs/tokio/latest/tokio/process/index.html)
  struct to execute a command asynchronously.
- In both cases, the pattern is the same:
    1. Create a `tokio::process::Command`.
    2. Configure it with the desired `stdin` and `stdout`.
    3. Spawn the command. Note this doesn't make any progress until you call
       `wait().await` or `wait_with_output().await`.
    4. Wait for the command to complete with or without output capture.

See it in action:

- Run the binary: `cargo run --bin async_command_exec_1`
- You should see something like the following in your terminal
  ```text
  hello world
  exit status: exit status: 0
  ```

### Example piping input to cat process programmatically
<a id="markdown-example-piping-input-to-cat-process-programmatically" name="example-piping-input-to-cat-process-programmatically"></a>

Please clone this [repo](https://github.com/nazmulidris/rust-scratch) to your computer to
play w/ the examples in the [`rust-scratch/tty`
crate](https://github.com/nazmulidris/rust-scratch/blob/main/tty/README.md) shown below.

[`async_command_exec_2.rs`](https://github.com/nazmulidris/rust-scratch/blob/main/tty/src/async_command_exec_2.rs)

```rust
use crossterm::style::Stylize;
use miette::IntoDiagnostic;
use r3bl_rs_utils_core::ok;
use std::process::Stdio;
use tokio::io::{AsyncBufReadExt, BufReader};

/// This variant requires the use of `tokio::spawn` to wait for the
/// child process to complete.
#[tokio::main]
async fn main() -> miette::Result<()> {
    // Create a child process that runs `cat`.
    // - Send the output of `cat` back to this child process.
    // - This child / command does not make progress until
    //   `wait().await` is called.
    let mut child = tokio::process::Command::new("cat")
        .stdin(Stdio::inherit())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .spawn()
        .into_diagnostic()?;

    // Get the stdout of the child process. Do this before the next
    // step, because the `child` struct is moved into the closure.
    let Some(child_stdout) = child.stdout.take() else {
        miette::bail!("Failed to capture stdout of child process");
    };

    // 🚀 Ensure the child process is spawned in the runtime, so it
    // can make progress on its own while we await any output.
    let child_task_join_handle = tokio::spawn(async move {
        let result_exit_status = child.wait().await;
        println!(
            "{}",
            format!(
                "Child process exited with status: {:?}",
                result_exit_status
            ).green()
        );
    });

    // As long as there is a line to be read from the child process,
    // print it to the terminal.
    let mut child_stdout_reader = BufReader::new(child_stdout).lines();
    while let Some(line) = child_stdout_reader
        .next_line().await.into_diagnostic()?
    {
        println!("{}", format!("❯ {}", line).cyan());
    }

    // Wait for the child task to complete.
    child_task_join_handle.await.into_diagnostic()?;

    ok!()
}

/// This is a simpler version of the `main` function above. It
/// doesn't need to use `tokio::spawn` to wait for the child
/// process to complete.
async fn main_simpler() -> miette::Result<()> {
    // Create a child process that runs `cat`.
    // - Send the output of `cat` back to this child process.
    // - This child / command does not make progress until
    //   `wait().await` is called.
    let mut child = tokio::process::Command::new("cat")
        .stdin(Stdio::inherit())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .spawn()
        .into_diagnostic()?;

    // Get the stdout of the child process. Do this before the next
    // step, because the `child` struct is moved into the closure.
    let Some(child_stdout) = child.stdout.take() else {
        miette::bail!("Failed to capture stdout of child process");
    };

    // As long as there is a line to be read from the child process,
    // print it to the terminal.
    let mut child_stdout_reader = BufReader::new(child_stdout).lines();
    while let Some(line) = child_stdout_reader
        .next_line().await.into_diagnostic()?
    {
        println!("{}", format!("❯ {}", line).cyan());
    }

    // Simultaneously waits for the child to exit and collect all
    // remaining output on the stdout/stderr handles, returning an
    // Output instance.
    let output = child.wait_with_output().await.into_diagnostic()?;
    println!(
        "{}",
        format!(
            "Child process exited with status: {:?}", output.status
        ).green()
    );

    ok!()
}

/// The nature of this function is different to the 2 above. For eg,
/// if you run this function in a terminal, you have to terminate
/// the input using `Ctrl-D` (EOF) if you want to see anything
/// displayed in the terminal output. In the two variants above,
/// output is captured in an "interactive" manner, as it comes
///  in from the stdin.
async fn main_non_interactive() -> miette::Result<()> {
    // Create a child process that runs `cat`.
    // - Send the output of `cat` back to this child process.
    // - This child / command does not make progress until
    // `wait().await` is called.
    let child = tokio::process::Command::new("cat")
        .stdin(Stdio::inherit())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .spawn()
        .into_diagnostic()?;

    // Simultaneously waits for the child to exit and collect
    // all remaining output on the stdout/stderr handles,
    // returning an Output instance.
    let output = child.wait_with_output().await.into_diagnostic()?;
    println!(
        "{}",
        format!(
            "Child process exited with status: {:?}", output.status
        ).green()
    );

    // Print the output.stdout to terminal.
    println!("{}", String::from_utf8_lossy(&output.stdout));

    ok!()
}
```

Notes on the code:

- This example uses the
  [`tokio::process::Command`](https://docs.rs/tokio/latest/tokio/process/index.html)
  struct to execute a command asynchronously, and then pipes the output of this command,
  back to itself. Then prints the output one line at a time.
- To run this program, pipe some input (from the shell) into this program.
  ```shell
  echo -e "hello world\nfoo\nbar\n" \
    | cargo run --bin async_command_exec_2
  ```
- This process will then run `cat` and capture the output from `cat`.
- It will then print the output from `cat` one line at time to the terminal.
- Flow diagram of the program:
  ```text
  Terminal emulator running fish/bash shell
  ┌────────────────────────────────────────────────────────────────┐
  │> echo -e "foo\nbar\nbaz" | cargo run --bin async_command_exec_2│
  └──────▲─────────────────────▲───────────────────────────────────┘
          │                     │        Pipeline above runs
          │                     │        in parallel
     external                 external
     process                  process
     command (fork & exec)    command (fork & exec)
                                │
                                ├────► create async Command for `cat`
                                │      with stdout = `Stdio::piped()`
                                │      to capture the output of `cmd`
                                │      back into this program
                                │
                                ├────► the stdin for this Command is
                                │      inherited from the current
                                │      process which is provided by
                                │      process the terminal & `pipe`
                                │
                                ├────► `cmd.spawn()` then sets up the
                                │      `cat` process to run with the
                                │      given stdin & stdout and
                                │      returns a `Child` struct
                                │
                                ├────► 🚀 instead of waiting
                                │      "normally", we must use
                                │      `tokio::spawn` to call
                                │      `child.wait().await` on the
                                │      child so it can make progress
                                │      while we wait for its output
                                │      below (in the current task)
                                │
                                └────► in our current task, we can
                                       now access `stdout` WHILE the
                                       child task is making progress
                                       above
  ```
- How to kill child process:
  - Note that similar to the behavior to the standard library, and unlike the futures
    paradigm of dropping-implies-cancellation, a spawned process will, by default,
    continue to execute even after the `tokio::process::Child` handle has been dropped.
    More info in the
    [docs](https://docs.rs/tokio/latest/tokio/process/index.html#caveats). To change this
    behavior you can use `tokio::process::Command::kill_on_drop` which isn't really
    recommended.
  - Instead, to kill a child process, you can do the following:
    - `tokio::process::Child::kill` - This forces the child process to exit.
    - `tokio::process::Child::wait` - This waits for the child process to cleanly exit.

See it in action:

- Run the binary: `echo -e "foo\nbar\nbaz" | cargo run --bin async_command_exec_2`
- Or run the binary: `cargo run --bin async_command_exec_2` and then type some input
  into the terminal and then press `Ctrl-D` to terminate the input.

### Example programmatically providing input into stdin and getting output from stdout of a process
<a id="markdown-example-programmatically-providing-input-into-stdin-and-getting-output-from-stdout-of-a-process" name="example-programmatically-providing-input-into-stdin-and-getting-output-from-stdout-of-a-process"></a>

Please clone this [repo](https://github.com/nazmulidris/rust-scratch) to your computer to
play w/ the examples in the [`rust-scratch/tty`
crate](https://github.com/nazmulidris/rust-scratch/blob/main/tty/README.md) shown below.

[`async_command_exec_3.rs`](https://github.com/nazmulidris/rust-scratch/blob/main/tty/src/async_command_exec_3.rs)

```rust
use crossterm::style::Stylize;
use miette::IntoDiagnostic;
use r3bl_rs_utils_core::ok;
use std::process::Stdio;
use tokio::{
    io::{AsyncBufReadExt, AsyncWriteExt, BufReader},
    process::{Child, ChildStdin, ChildStdout},
    task::JoinHandle,
};

#[tokio::main]
async fn main() -> miette::Result<()> {
    // Create a child process that runs `cat`.
    // 1. Send the output of `cat` back to this child process.
    // 2. Send the input to `cat` from this child process.
    // 3. This child / command does not make progress until
    //    `wait().await` is called.
    let mut child = tokio::process::Command::new("cat")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .spawn()
        .into_diagnostic()?;

    // These are the bytes that will be sent to the `stdin` of the
    // child process.
    let input = &["hello", "nadia!"];

    // Get the stdout & stdin of the child process. Do this before
    // the next step, because the `child` struct is moved into
    // the closure.
    let (stdout, stdin): (ChildStdout, ChildStdin) = {
        let Some(stdout) = child.stdout.take() else {
            miette::bail!("Child process did not have a stdout");
        };
        let Some(stdin) = child.stdin.take() else {
            miette::bail!("Child process did not have a stdin");
        };
        (stdout, stdin)
    };

    // Spawn tasks to:
    let join_handle_child_task = spawn_child_process(child);
    let join_handle_provide_input_task =
        spawn_provide_input(stdin, input);

    // Read the output of the child process, on the current thread.
    _ = read_stdout(stdout).await;

    // Wait for the child process to complete.
    _ = tokio::join!(
        join_handle_child_task, join_handle_provide_input_task);

    // Make assertions.
    assert_eq!(input.join("\n"), "hello\nnadia!");

    ok!()
}

/// As long as there is a line to be read from the child process,
/// print it to the terminal.
async fn read_stdout(stdout: ChildStdout) -> miette::Result<()> {
    let mut output: Vec<String> = vec![];
    let mut stdout_reader = BufReader::new(stdout).lines();
    while let Some(line) = stdout_reader
        .next_line().await.into_diagnostic()?
    {
        output.push(line.clone());
        println!(
            "🧵 read_stdout -> {}",
            format!("🫲  {}", line).cyan()
        );
    }
    ok!()
}

/// 🚀 Ensure the child process is spawned in the runtime, so it
/// can make progress on its own while we await any output.
fn spawn_child_process(mut child: Child) -> JoinHandle<()> {
    tokio::spawn(async move {
        let result_exit_status = child.wait().await;
        println!(
            "{}",
            format!(
                "🚀 spawn_child_process -> exit w/ status: {:?}",
                result_exit_status
            )
            .green()
        );
    })
}

/// 🚀 Provide input to the child process.
fn spawn_provide_input(
    mut stdin: ChildStdin, input: &[&str]
) -> JoinHandle<()> {
    let input = input
        .iter()
        .map(|s| s.to_string())
        .collect::<Vec<String>>()
        .join("\n");

    tokio::spawn(async move {
        // Write the input to the `stdin` of the child process.
        _ = stdin.write_all(input.as_bytes()).await;

        // Drop the handle to signal EOF to the child process.
        drop(stdin);

        println!(
            "{}: {}",
            "🚀 spawn_provide_input -> EOF to child 🫱  stdin"
                .green(),
            format!("{:?}", input).blue()
        );
    })
}
```

Notes on the code:

- This example is similar to `async_command_exec_2.rs`, except that there is no need to
  pipe input from the shell into this program. It does the following:
    1. Programmatically provides data to the `cat` command via `stdin`.
    2. Programmatically captures the output of `cat` via `stdout`.
- Flow diagram of the program:
  ```text
  Terminal emulator running fish/bash shell
  ┌────────────────────────────────────────┐
  │ > cargo run --bin async_command_exec_3 │
  └───▲────────────────────────────────────┘
      ├────► create async Command for `cat`
      │      with stdout = `Stdio::piped()` to
      │      capture the output of `cmd`
      │      back into this program
      │
      ├────► set stdin = `Stdio::piped()` to provide
      │      input to the `cat` command asynchronously
      │
      ├────► `cmd.spawn()` then sets up the `cat` process
      │      to run with the given stdin & stdout and
      │      returns a `Child` struct
      │
      ├────► 🚀 instead of waiting "normally", we must use
      │      `tokio::spawn` to call `child.wait().await`
      │      on the child so it can make progress while
      │      we wait for its output below (in the current task)
      │
      ├────► 🚀 also use `tokio::spawn` to call
      │      `child.stdin.write_all()` to provide input
      │      to the `cat` command
      │
      └────► in our current task, we can now access `stdout`
             WHILE the child task is making progress above
  ```
- How to kill child process:
  - Note that similar to the behavior to the standard library, and unlike the futures
    paradigm of dropping-implies-cancellation, a spawned process will, by default,
    continue to execute even after the `tokio::process::Child` handle has been dropped.
    More info in the
    [docs](https://docs.rs/tokio/latest/tokio/process/index.html#caveats). To change this
    behavior you can use `tokio::process::Command::kill_on_drop` which isn't really
    recommended.
  - Instead, to kill a child process, you can do the following:
    - `tokio::process::Child::kill` - This forces the child process to exit.
    - `tokio::process::Child::wait` - This waits for the child process to cleanly exit.

See it in action:

- Run the binary: `cargo run --bin async_command_exec_3`
- It should produce output that looks something like the following:
  ```text
  🚀 spawn_provide_input -> Finished providing input + EOF to child process 🫱  stdin: "hello\nnadia!"
  🧵 read_stdout -> 🫲  hello
  🧵 read_stdout -> 🫲  nadia!
  🚀 spawn_child_process -> Child process exited with status: Ok(ExitStatus(unix_wait_status(0)))
  ```

### Example programmatically piping the output of one process into another
<a id="markdown-example-programmatically-piping-the-output-of-one-process-into-another" name="example-programmatically-piping-the-output-of-one-process-into-another"></a>

Please clone this [repo](https://github.com/nazmulidris/rust-scratch) to your computer to
play w/ the examples in the [`rust-scratch/tty`
crate](https://github.com/nazmulidris/rust-scratch/blob/main/tty/README.md) shown below.

[`async_command_exec_4.rs`](https://github.com/nazmulidris/rust-scratch/blob/main/tty/src/async_command_exec_4.rs)

```rust
use crossterm::style::Stylize;
use miette::IntoDiagnostic;
use r3bl_rs_utils_core::ok;
use std::process::Stdio;
use tokio::{io::AsyncReadExt, process::Command};

type EchoResult = (
    tokio::process::ChildStdout, tokio::task::JoinHandle<()>);
type TrResult = (
    tokio::process::ChildStdout, tokio::task::JoinHandle<()>);

const INPUT: &str = "hello world";

#[tokio::main]
async fn main() -> miette::Result<()> {
    // Spawn the `echo` command & get its `stdout`.
    let (child_stdout_echo, join_handle_echo): EchoResult =
        spawn_child_echo_and_get_stdout()?;

    // Spawn the `tr` command & provide the `stdout` of `echo` to
    // its `stdin`.
    let (child_stdout_tr, join_handle_tr): TrResult =
        spawn_child_tr_and_provide_stdin(child_stdout_echo)?;

    // Wait for both child processes to complete.
    _ = tokio::try_join!(join_handle_echo, join_handle_tr);

    // Read the output of the `tr` command from `child_stdout_tr`.
    let output = {
        let mut buf = vec![];
        tokio::io::BufReader::new(child_stdout_tr)
            .read_to_end(&mut buf)
            .await
            .into_diagnostic()?;
        buf
    };

    // Make assertions.
    let expected_output = format!("{INPUT}\n").to_uppercase();
    assert_eq!(expected_output, String::from_utf8_lossy(&output));

    // Print the output of the `tr` command.
    println!(
        "{}: {}",
        "output".blue(),
        format!("{}", String::from_utf8_lossy(&output)).green()
    );

    ok!()
}

/// 🚀 Spawn `echo` command & get its `stdout`. We will pipe this
/// into the `stdin` of `tr`.
///
/// Return a tuple of:
/// 1. `stdout` of `echo`: [tokio::process::ChildStdout].
/// 2. [tokio::task::JoinHandle] of `echo` [tokio::process::Child]
///    process, spawned by the [tokio::process::Command] that
///    starts `echo`.
fn spawn_child_echo_and_get_stdout() -> miette::Result<EchoResult> {
    // Spawn the child process for `echo`.
    let mut child_echo = Command::new("echo")
        .arg(INPUT)
        .stdout(Stdio::piped())
        .stdin(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .into_diagnostic()?;

    // Take the `stdout` of the child process.
    let child_stdout = child_echo.stdout.take()
        .ok_or(miette::miette!(
            "Failed to capture stdout of `echo` child process"
        ))?;

    // Ensure the child process is spawned in the runtime, so it can
    // make progress on its own while we await any output.
    let join_handle = tokio::spawn(async move {
        _ = child_echo.wait().await;
    });

    // Return the `stdout` of `echo` and the `JoinHandle` of the
    // `echo` child process.
    Ok((child_stdout, join_handle))
}

/// 🚀 Spawn `tr` command & pass the given
/// [tokio::process::ChildStdout] to its `stdin`.
///
/// Return a tuple of:
/// 1. `stdout` of `tr`: [tokio::process::ChildStdout].
/// 2. [tokio::task::JoinHandle] of `tr` [tokio::process::Child]
///    process, spawned by the [tokio::process::Command] that
///    starts `tr`.
fn spawn_child_tr_and_provide_stdin(
    stdout_from_other_child: tokio::process::ChildStdout,
) -> miette::Result<TrResult> {
    // Convert `stdout_from_other_child`: tokio::process::ChildStdout
    // into tokio::process::ChildStdin, so it can be provided to the
    // `stdin` of the `tr` command.
    let stdout_from_other_child: std::process::Stdio =
        stdout_from_other_child.try_into().into_diagnostic()?;

    // Spawn child process.
    let mut child_tr = Command::new("tr")
        .arg("a-z")
        .arg("A-Z")
        .stdin(stdout_from_other_child)
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .spawn()
        .into_diagnostic()?;

    // Take the `stdout` of the child process.
    let child_stdout = child_tr.stdout.take().ok_or(miette::miette!(
        "Failed to capture stdout of `tr` child process"
    ))?;

    // Ensure the child process is spawned in the runtime, so it can
    // make progress on its own while we await any output.
    let join_handle = tokio::spawn(async move {
        _ = child_tr.wait().await;
    });

    Ok((child_stdout, join_handle))
}
```

Notes on the code:

- In this example, we will will orchestrate two processes and make a pipe between them
  programmatically (we are used to doing this using `|` in shells). We will replicate
  the following functionality in this program: `echo hello world | tr a-z A-Z`.
    1. Spawn the `echo` command, with arg `hello world` and get its `stdout`.
    2. Then we will provide this `stdout` to the `stdin` of the `tr` command, with arg
       `a-z A-Z` and spawn it.
    3. Finally we join the `echo` and `tr` child processes and wait for them both to
       complete.

See it in action:

- Run the binary: `cargo run --bin async_command_exec_4`
- You should see output that looks something like the following:
  ```text
  output: HELLO WORLD
  ```

### Example using r3bl_terminal_async to send commands to a long running bash child process
<a id="markdown-example-using-r3bl_terminal_async-to-send-commands-to-a-long-running-bash-child-process" name="example-using-r3bl_terminal_async-to-send-commands-to-a-long-running-bash-child-process"></a>

The following example is in the [`r3bl_terminal_async`
repo](https://github.com/r3bl-org/r3bl-open-core/blob/main/terminal_async). Please clone that repo to your computer to
play w/ the following example:

[`shell_async.rs`](https://github.com/r3bl-org/r3bl-open-core/blob/main/terminal_async/examples/shell_async.rs)

You can clone the [`r3bl-open-core`](https://github.com/r3bl-org/r3bl-open-core) repo to your computer
and then run the following command to run the example:

```shell
git clone https://github.com/r3bl-org/r3bl-open-core
cd r3bl-open-core/terminal_async
cargo run --example shell_async
```

Type the following commands to have a go at this.

```shell
msg="hello nadia!"
echo $msg
```

You should see something like the following.

```text
[1606192] > msg="hello nadia!"
[1606192] > echo $msg
hello nadia!
[1606192] >
```

Clean up any left over processes:

```shell
killall -9 bash shell_async
```

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
