---
title: "Build a grep CLI app in Rust"
author: Nazmul Idris
date: 2022-03-02 14:00:00+00:00
excerpt: |
  This article illustrates how we can build a CLI app in Rust that is a very basic implementation of
  grep. This app will have 2 modes of operation: piping lines in from `stdin` and searching them, and
  reading a file and searching thru it. The output of the program will be lines that match the search
  term w/ the term being highlighted. Topics like `stdin` manipulation in a terminal, detecting when
  the terminal is in `tty` mode vs `piped` mode, doing simple file I/O, creating non consuming
  builders, and managing `Result`s, along w/ building a simple CLI interface are covered in this
  article.
layout: post
categories:
  - Rust
  - CLI
---

<img class="post-hero-image" src="{{ 'assets/rust-grep-cli-app.svg' | relative_url }}"/>

<!-- TOC -->

- [Introduction](#introduction)
- [Building the main function](#building-the-main-function)
- [Reading piped input from stdin mode 1](#reading-piped-input-from-stdin-mode-1)
- [Reading a file and searching thru it mode 2](#reading-a-file-and-searching-thru-it-mode-2)
- [Wrapping up](#wrapping-up)
- [Build with Naz video series on developerlife.com YouTube channel](#build-with-naz-video-series-on-developerlifecom-youtube-channel)

<!-- /TOC -->

## Introduction
<a id="markdown-introduction" name="introduction"></a>

This article illustrates how we can build a CLI app in Rust that is a very basic
implementation of grep. This app will have 2 modes of operation: piping lines in from
`stdin` and searching them, and reading a file and searching thru it. The output of the
program will be lines that match the search term w/ the term being highlighted. Topics
like `stdin` manipulation in a terminal, detecting when the terminal is in `tty` mode vs
`piped` mode, doing simple file I/O, creating non consuming builders, and managing
`Result`s, along w/ building a simple CLI interface are covered in this article.

The app we are building is very simple by design so we can get a handle on command line
arguments, stdin, stdout, and piping.

> 📜 The source code for the finished app named `rust-grep-cli` can be found
> [here](https://github.com/nazmulidris/rust_scratch/tree/main/rust-grep-cli).

> For more information on general Rust type system design (functional approach rather than
> object oriented), please take a look at this [paper](https://arxiv.org/pdf/2307.07069.pdf)
> by Will Crichton demonstrating Typed Design Patterns with Rust.

## Building the main function
<a id="markdown-building-the-main-function" name="building-the-main-function"></a>

The first thing we need to do is build the main function. This is where we will be routing
our app to be in mode 1 or mode 2. We have to detect whether the terminal is in `tty` mode
or `piped` mode. In order to do this we have to use a crate
[`is_terminal`](https://crates.io/crates/is_terminal). Helper methods based on this crate
are available in the [`r3bl_tuify`](https://crates.io/crates/r3bl_tuify) crate, which is
what we will be using in our app.

Here's the `main` function, w/ the most important thing being the call to
`is_stdin_piped()`. This uses the `r3bl_rs_utils` crate which itself uses `atty` to
determine whether the terminal is currently accepting input piped to `stdin`.

> 📜 You can find the source for `is_stdin_piped()` (in `r3bl_tuify` crate) [in
> `term.rs`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tuify/src/term.rs). You
> will also find these other functions that are related: `is_tty()`, `is_stdout_piped`.
>
> 🌟 Please star the [`r3bl-open-core` repo](https://github.com/r3bl-org/r3bl-open-core) on
> github if you like it 🙏. If you would like to contribute to it, please click
> [here](https://github.com/r3bl-org/r3bl-open-core/contribute).

```rust
fn main() {
  let args = args().collect::<Vec<String>>();
  with(run(args), |it| match it {
    Ok(()) => exit(0),
    Err(err) => {
      eprintln!("{}: {}", style_error("Problem encountered"), err);
      exit(1);
    }
  });
}

fn run(args: Vec<String>) -> Result<(), Box<dyn Error>> {
  match is_stdin_piped() {
    true => piped_grep(PipedGrepOptionsBuilder::parse(args)?)?,
    false => grep(GrepOptionsBuilder::parse(args)?)?,
  }
  Ok(())
}
```

Please note the following things in the `run()` function:

1. It returns a `Result` and all the functions that it calls also return `Result`:

- `PipedGrepOptionsBuilder::parse()`
- `piped_grep()`
- `GrepOptionsBuilder::parse()`
- `grep()`

2. It uses the `?` operator to unwrap the `Result` (produced by each of the four functions that it
   calls) to propagate any `Error` that may have been produced to the caller (`main()` function).

## Reading piped input from stdin (mode 1)
<a id="markdown-reading-piped-input-from-stdin-mode-1" name="reading-piped-input-from-stdin-mode-1"></a>

The arguments that our app will take are different for each mode. In this mode, we need to know what
our search term is, and whether to apply case-sensitive or insensitive search. We don't need a file
path like we do in [mode 2](#reading-a-file-and-searching-thru-it-mode-2).

We want our user to be able to run our app like this:

<!--prettier-ignore-start-->

> <span style="color:#ea1bf5"> $
> <span style="color:#6FF51B">c</span><span style="color:#73F318">a</span><span style="color:#77F116">t</span><span style="color:#7BF014">
> </span><span style="color:#80ED11">R</span><span style="color:#84EB0F">E</span><span style="color:#88E90D">A</span><span style="color:#8CE70C">D</span><span style="color:#90E40A">M</span><span style="color:#95E108">E</span><span style="color:#99DF07">.</span><span style="color:#9DDC06">m</span><span style="color:#A1D905">d</span><span style="color:#A5D604">
> </span><span style="color:#A9D303">|</span><span style="color:#ADCF02">
> </span><span style="color:#B1CC01">c</span><span style="color:#B5C901">a</span><span style="color:#B9C501">r</span><span style="color:#BCC201">g</span><span style="color:#C0BE01">o</span><span style="color:#C4BA01">
> </span><span style="color:#C7B601">r</span><span style="color:#CBB301">u</span><span style="color:#CEAF02">n</span><span style="color:#D1AB02">
> </span><span style="color:#D5A703">S</span><span style="color:#D8A304">E</span><span style="color:#DB9F05">A</span><span style="color:#DE9A07">R</span><span style="color:#E09608">C</span><span style="color:#E39209">H</span><span style="color:#E68E0B">_</span><span style="color:#E88A0D">T</span><span style="color:#EA850F">E</span><span style="color:#ED8111">R</span><span style="color:#EF7D13">M</span><span style="color:#F17915">
> </span><span style="color:#F37417">C</span><span style="color:#F4701A">A</span><span style="color:#F66C1D">S</span><span style="color:#F7681F">E</span><span style="color:#F96422">_</span><span style="color:#FA6025">S</span><span style="color:#FB5C28">E</span><span style="color:#FC582B">N</span><span style="color:#FD542E">S</span><span style="color:#FD5032">I</span><span style="color:#FE4C35">T</span><span style="color:#FE4838">I</span><span style="color:#FE443C">V</span><span style="color:#FE4040">E</span>

<!--prettier-ignore-end-->

1. The left hand side of the pipe `|` is just a call to `cat` command w/ a file name `README.md`,
   but you can replace it w/ whatever command pipes its output into the terminal, like `echo`, etc.
2. The user will have to supply the `SEARCH_TERM` and `CASE_SENSITIVE` arguments.
   - Note these are just placeholders for the actual arguments that will be passed in the terminal.
   - Another note is that the `CASE_SENSITIVE` argument can be any string, we will just look for the
     existence of a 2nd argument and if it exists, we will assume that the user wants case-sensitive
     search, otherwise we default to case-insensitive search.

The `main()` function will provide the `std::env::args` that contain the arguments the user passes
in the terminal, as an iterator, which we turn into a `Vec<String>`.

This `Vec<String>` will be passed to the `PipedGrepOptionsBuilder` which will parse the arguments
into this struct.

```rust
pub struct PipedGrepOptions {
  pub search: String,
  pub case_sensitive: bool,
}
```

> ⚡ `PipedGrepOptionsBuilder` is a
> [non-consuming builder](https://github.com/nazmulidris/rust_scratch/blob/main/rust-book/src/intermediate/builders.rs),
> which makes it a little easier to work w/ (than a consuming builder).

Once these steps are complete, now we can step into the `piped_grep()` function that actually parses
each line from `stdin` and checks to see whether it contains the search term. Here's the full
[source file](https://github.com/nazmulidris/rust_scratch/blob/main/rust-grep-cli/src/piped_grep.rs).

```rust
stdin()
  .lock()
  .lines()
  .filter(|line| {
    let line = line.as_ref().unwrap();
    if options.case_sensitive {
      line.contains(&options.search)
    } else {
      line.to_lowercase().contains(&options.search.to_lowercase())
    }
  })
  .map(|line| line.unwrap())
  .for_each(|line| {
    let from = &options.search;
    let to = format!("{}", style_primary(&options.search));
    let line = line.replace(from, &to);
    println!("{}", line);
  });
```

Let's break down each line of the above code:

1. We first get the `stdin` handle by calling `std::io::stdin()`. And we call `.lock()` on it to get
   a `StdinLock` handle which implements the `BufRead` trait. This allows us to call `lines()` on it
   in order to get an iterator over every single line that is read from `stdin`.
2. We then call `.filter()` on the `lines()` iterator to filter out any lines that don't contain the
   search term. And this is also where we implement case-sensitive vs case-insensitive search.
3. We then call `.map()` on the `filter()` iterator to map each line to a `String` from `Result` by
   unwrapping it.
4. We then call `.for_each()` on the `map()` iterator to iterate over each line and find every
   instance of the search term and replace it with the formatted version. Then print it to the
   console.

Next, we will look at implementing mode 2.

## Reading a file and searching thru it (mode 2)
<a id="markdown-reading-a-file-and-searching-thru-it-mode-2" name="reading-a-file-and-searching-thru-it-mode-2"></a>

The arguments that our app will take in this mode are the search term, the file path, and whether to
apply case-sensitive or case-insensitive search. These are different than the arguments for
[mode 1](#reading-piped-input-from-stdin-mode-1).

We want our use to be able to run our app like this:

<!--prettier-ignore-start-->
> <span style="color:#46FE3A">c</span><span style="color:#4AFE36">a</span><span style="color:#4EFE33">r</span><span style="color:#52FD30">g</span><span style="color:#56FC2C">o</span><span style="color:#5AFB29">
> </span><span style="color:#5EFA26">r</span><span style="color:#62F923">u</span><span style="color:#66F820">n</span><span style="color:#6AF61E">
> </span><span style="color:#6FF51B">S</span><span style="color:#73F318">E</span><span style="color:#77F116">A</span><span style="color:#7BF014">R</span><span style="color:#80ED11">C</span><span style="color:#84EB0F">H</span><span style="color:#88E90E">_</span><span style="color:#8CE70C">T</span><span style="color:#90E40A">E</span><span style="color:#95E108">R</span><span style="color:#99DF07">M</span><span style="color:#9DDC06">
> </span><span style="color:#A1D905">F</span><span style="color:#A5D604">I</span><span style="color:#A9D303">L</span><span style="color:#ADCF02">E</span><span style="color:#B1CC01">N</span><span style="color:#B5C901">A</span><span style="color:#B9C501">M</span><span style="color:#BCC201">E</span><span style="color:#C0BE01">
> </span><span style="color:#C4BA01">C</span><span style="color:#C7B601">A</span><span style="color:#CBB301">S</span><span style="color:#CEAF02">E</span><span style="color:#D1AB02">_</span><span style="color:#D5A703">S</span><span style="color:#D8A304">E</span><span style="color:#DB9F05">N</span><span style="color:#DE9A07">S</span><span style="color:#E09608">I</span><span style="color:#E39209">T</span><span style="color:#E68E0B">I</span><span style="color:#E88A0D">V</span><span style="color:#EA850F">E</span>
<!--prettier-ignore-end-->

1. The first argument is the search term.
2. The second argument is the file path.
3. The third argument is whether to apply case-sensitive or case-insensitive search.

The `main()` function will provide the `std::env::args` that contain the arguments the user passes
in the terminal, as an iterator, which we turn into a `Vec<String>`.

This `Vec<String>` will be passed to the `GrepOptionsBuilder` which will parse the arguments into
this struct. This builder is also a non-consuming builder.

```rust
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct GrepOptions {
  pub search: String,
  pub file_path: String,
  pub case_sensitive: bool,
}
```

We can then pass this struct into the `grep()` function which does the following.

```rust
let content = fs::read_to_string(options.file_path)?;
let filtered_content = content
  .lines()
  .filter(|line| {
    if options.case_sensitive {
      line.contains(&options.search)
    } else {
      line.to_lowercase().contains(&options.search.to_lowercase())
    }
  })
  .map(|line| {
    let from = &options.search;
    let to = format!("{}", style_primary(&options.search));
    line.replace(from, &to)
  })
  .collect::<Vec<String>>();
println!("{}", filtered_content.join("\n"));
```

Similar to what happened in [mode 1](#reading-piped-input-from-stdin-mode-1), we first read the
contents of the file into a string, and then we filter out any lines that don't contain the search,
and finally replace the search term with the formatted version. Then print the result to the
console.

## Wrapping up
<a id="markdown-wrapping-up" name="wrapping-up"></a>

You can get the code for this app
[here](https://github.com/nazmulidris/rust_scratch/tree/main/rust-grep-cli).

Here are a list of crates that are used in this app.

1. `r3bl_rs_utils` - <https://crates.io/crates/r3bl_rs_utils>
2. `atty` - <https://crates.io/crates/atty>

We will explore more complex TUIs built w/ Rust in the future.

## Build with Naz video series on developerlife.com YouTube channel
<a id="markdown-build-with-naz-video-series-on-developerlife.com-youtube-channel" name="build-with-naz-video-series-on-developerlife.com-youtube-channel"></a>

> If you have comments and feedback on this content, or would like to request new content
> (articles & videos) on developerlife.com, please join our [discord
> server](https://discord.gg/8M2ePAevaMi).

You can watch a video series on building this crate with Naz on the
[developerlife.com YouTube channel](https://www.youtube.com/@developerlifecom).

- [YT channel](https://www.youtube.com/@developerlifecom)
- Playlists
    - [Build with Naz, fundamental effective Rust](https://www.youtube.com/playlist?list=PLofhE49PEwmza94sS7UmJnN9gSCHTVTfz)
    - [Build with Naz, effective async Rust and tokio](https://www.youtube.com/playlist?list=PLofhE49PEwmwO69E7eiQ-ewnMME8ydgQ5)
    - [Build with Naz, async readline and spinner for CLI in Rust](https://www.youtube.com/watch?v=3vQJguti02I&list=PLofhE49PEwmwelPkhfiqdFQ9IXnmGdnSE)
    - [Build with Naz, testing in Rust](https://www.youtube.com/watch?v=Xt495QLrFFk&list=PLofhE49PEwmwLR_4Noa0dFOSPmSpIg_l8)
