---
title: "Build with Naz : Box and Pin exploration in Rust"
author: Nazmul Idris
date: 2024-07-16 15:00:00+00:00
excerpt: |
    This tutorial, video, and repo are a deep dive into Rust `Pin` and `Box` types, along with
    concepts of ownership and borrowing. We will also cover a lot of background information on
    the concepts of operating system process, memory allocation and access, stack, and heap.
    The examples we create are designed to demonstrate  the different semantics around the use
    of boxes and pinned boxes in Rust.
layout: post
categories:
  - Rust
  - CLI
  - Server
  - TUI
---

<img class="post-hero-image" src="{{ 'assets/box-and-pin.svg' | relative_url }}"/>

<!-- TOC -->

- [Introduction](#introduction)
- [Why do we need both Box and Pin?](#why-do-we-need-both-box-and-pin)
- [Formatting pointers](#formatting-pointers)
- [What is a smart pointer?](#what-is-a-smart-pointer)
- [YouTube video for this article](#youtube-video-for-this-article)
- [Examples Rust Box smart pointer, and Pin](#examples-rust-box-smart-pointer-and-pin)
  - [Example 1: Getting the address of variables on the stack and heap](#example-1-getting-the-address-of-variables-on-the-stack-and-heap)
  - [Example 2: What does Box move do?](#example-2-what-does-box-move-do)
  - [Example 3: How do we swap the contents of two boxes?](#example-3-how-do-we-swap-the-contents-of-two-boxes)
  - [Example 4: What does pining a box do?](#example-4-what-does-pining-a-box-do)
- [Build with Naz video series on developerlife.com YouTube channel](#build-with-naz-video-series-on-developerlifecom-youtube-channel)

<!-- /TOC -->

## Introduction
<a id="markdown-introduction" name="introduction"></a>

This tutorial, video, and repo are a deep dive into Rust `Pin` and `Box` types, along with
concepts of ownership and borrowing. We will also cover a lot of background information on
the concepts of operating system process, memory allocation and access, stack, and heap.
The examples we create are designed to demonstrate  the different semantics around the use
of boxes and pinned boxes in Rust.

## Why do we need both Box and Pin?
<a id="markdown-why-do-we-need-both-box-and-pin%3F" name="why-do-we-need-both-box-and-pin%3F"></a>

It is common to use `Pin` for `tokio::select!` macro branches in [Rust async
code](https://developerlife.com/2024/05/19/effective-async-rust/). And `Box` is used
commonly for [trait
pointers](https://developerlife.com/2024/04/28/rust-polymorphism-dyn-impl-trait-objects-for-testing-and-extensibiity/).

This article, video, and repo illustrate the concepts (moving a box, swapping box
contents, and pinning a box) by example. Lots of pretty formatted output is generated so
that you can run tests and see what's happening (and make sense of it).

## Formatting pointers
<a id="markdown-formatting-pointers" name="formatting-pointers"></a>

To format pointers in Rust, we can use the formatting trait
[`{:p}`](https://doc.rust-lang.org/std/fmt/#formatting-traits). You can format a
pointer by using two approaches:
1. Get the address of the pointer using [`std::ptr::addr_of!`] and then format it
   using `{:p}`. Eg: `let x = 1; println!("{:p}", std::ptr::addr_of!(x));`
2. Get a reference to the pointer using `&` and then format it using `{:p}`. Eg: `let
   x = 1; println!("{:p}", &x);`

## What is a smart pointer?
<a id="markdown-what-is-a-smart-pointer%3F" name="what-is-a-smart-pointer%3F"></a>

Smart pointers in Rust are data structures that act like pointers but also have additional
metadata and capabilities. They provide a level of abstraction over raw pointers, offering
features like ownership management, reference counting, and more. Smart pointers often
manage ownership of the data they point to, ensuring proper deallocation when no longer
needed.

> For a great visualization of memory allocation, stack and heap please read this
> [article](https://courses.grainger.illinois.edu/cs225/fa2022/resources/stack-heap/).

## YouTube video for this article
<a id="markdown-youtube-video-for-this-article" name="youtube-video-for-this-article"></a>

This blog post has examples from this live coding video. If you like
to learn via video, please watch the companion video on the [developerlife.com YouTube
channel](https://www.youtube.com/@developerlifecom).

<!-- video on tokio-async-cancel-safety -->
<iframe
    src="https://www.youtube.com/embed/SZtZkM2Ujhs?si=6wtfI_Q8ORpKUU_G"
    title="YouTube video player" frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    referrerpolicy="strict-origin-when-cross-origin"
    allowfullscreen
    >
</iframe>

<br/>

## Examples Rust Box smart pointer, and Pin
<a id="markdown-examples-rust-box-smart-pointer%2C-and-pin" name="examples-rust-box-smart-pointer%2C-and-pin"></a>

Let's create some examples to illustrate how `Box` and `Pin` and pointers to stack
allocations and heap allocations work in Rust. You can run `cargo new --lib box-and-pin`
to create a new library crate.

> 💡 You can get the code from the
> [`rust-scratch`](https://github.com/nazmulidris/rust-scratch/blob/main/box-and-pin/) repo.

Then add the following to the `Cargo.toml` file that's generated. These pull in all the
dependencies that we need for these examples.

```toml
[package]
name = "box-and-pin"
version = "0.1.0"
edition = "2021"

[dependencies]
crossterm = { version = "0.27.0", features = ["event-stream"] }
serial_test = "3.1.1"
```

Here are the dependencies we are using:
1. The `serial_test` dep allows us to run Rust tests serially, so that we can examine the
   output of each test, without it being clobbered by other test output running in
   parallel.
2. The `crossterm` dep allows us to generate colorful `println!` output in the terminal
   which will help us visualize what is going on with the pointers and memory allocations.

We are going to add all the examples below as tests to the `lib.rs` file in this crate.

### Example 1: Getting the address of variables on the stack and heap
<a id="markdown-example-1%3A-getting-the-address-of-variables-on-the-stack-and-heap" name="example-1%3A-getting-the-address-of-variables-on-the-stack-and-heap"></a>

Let's add the following imports and macros to the top of the `lib.rs` file. These will
help us print output from the tests, so that we can track where a pointer is located in
memory and what the size of the thing it points to is. There are two macros, one for a
reference or pointer, and another one for pinned pointers. And we have an assertion
function that can return true if all 3 arguments are equal.

```rs
use crossterm::style::Stylize;
use serial_test::serial;

/// Given a pointer `$p`, it prints:
/// 1. it's address,
/// 2. and size of the thing it points to (in bytes).
macro_rules! print_ptr_addr_size {
    ($p: expr) => {
        format!("{:p}┆{}b", $p, std::mem::size_of_val($p))
    };
}

/// Given a pinned pointer `$p`, it prints:
/// 1. it's address,
/// 2. and size of the thing it points to (in bytes).
macro_rules! print_pin_addr_size {
    ($p: expr) => {
        format!("{:p}┆{}b", $p, std::mem::size_of_val(&(*$p)))
    };
}

fn assert_three_equal<T: PartialEq + std::fmt::Debug>(a: &T, b: &T, c: &T) {
    assert_eq!(a, b, "a and b are not equal");
    assert_eq!(a, c, "a and c are not equal");
}
```

So, before we start with the examples, let's add a test that demonstrates how to get the
address of a variable on the stack and heap. Add the following code to your `lib.rs` file.

```rs
#[test]
#[serial]
fn print_ptr_addr_size() {
    // Using `std::ptr::addr_of!` to get the memory address of a variable.
    let x = 100u8;
    let x_addr = std::ptr::addr_of!(x);
    println!(
        "x: {}, x_addr  : {}",
        x.to_string().blue().underlined(),
        format!("{:?}", x_addr).red().italic(),
    );

    // Using `format!` to get the memory address of a variable.
    let x_addr_2 = format!("{:p}", &x);
    println!(
        "x: {}, x_addr_2: {}",
        x.to_string().blue().underlined(),
        x_addr_2.red().italic().on_black(),
    );

    // Get size of `x` in bytes.
    let x_size = std::mem::size_of_val(&x);
    println!(
        "x: {}, x_size  : {}b",
        x.to_string().blue().underlined(),
        x_size.to_string().magenta().italic().on_black(),
    );

    // Using `print_ptr_addr_size!` to get the memory address of a variable.
    let x_addr_3 = print_ptr_addr_size!(&x);
    println!(
        "x: {}, x_addr_3: {}",
        x.to_string().blue().underlined(),
        x_addr_3.red().italic().on_black(),
    );
}
```

Here's the output of the test above, after you run `cargo watch -x "test --lib -- --show-output print"`.

<pre class="pre-manual-highlight">
---- print_ptr_addr_size stdout ----
x: <span style="color:#81A1C1"><u style="text-decoration-style:solid">100</u></span>, x_addr  : <span style="color:#BF616A"><i>0x7e17cd9feb97</i></span>
x: <span style="color:#81A1C1"><u style="text-decoration-style:solid">100</u></span>, x_addr_2: <span style="background-color:#3B4252"><span style="color:#BF616A"><i>0x7e17cd9feb97</i></span></span>
x: <span style="color:#81A1C1"><u style="text-decoration-style:solid">100</u></span>, x_size  : <span style="background-color:#3B4252"><span style="color:#B48EAD"><i>1</i></span></span>b
x: <span style="color:#81A1C1"><u style="text-decoration-style:solid">100</u></span>, x_addr_3: <span style="background-color:#3B4252"><span style="color:#BF616A"><i>0x7e17cd9feb97┆1b</i></span></span>
</pre>

Let's walk through the output above:
1. We have a variable `x` that is a `u8` with a value of `100`. This is a stack
   allocation. It occupies 1 byte of memory (its size).
2. We get the address of `x` using `std::ptr::addr_of!(x)` and `format!("{:p}", &x)`.
3. We get the size of `x` in bytes using `std::mem::size_of_val(&x)`. The size is 1 byte.
4. We get the address of `x` and the size of `x` using the `print_ptr_addr_size!` macro.

### Example 2: What does Box move do?
<a id="markdown-example-2%3A-what-does-box-move-do%3F" name="example-2%3A-what-does-box-move-do%3F"></a>

Add the following snippet to the `lib.rs` file next. This
[link](https://courses.grainger.illinois.edu/cs225/fa2022/resources/stack-heap/) provids
lots of great diagrams on how stack and heap memory works in an operating system.

```rs
/// <https://courses.grainger.illinois.edu/cs225/fa2022/resources/stack-heap/>
#[test]
#[serial]
fn move_a_box() {
    let b_1 = Box::new(255u8);
    let b_1_addr = print_ptr_addr_size!(b_1.as_ref()); // Pointee (heap)
    let b_1_ptr_addr = print_ptr_addr_size!(&b_1); // Pointer (stack)

    println!(
        "1. {}: {}, {} (pointee, heap): {}, {} (ptr, stack): {}",
        "b_1".green(),
        b_1.to_string().blue().underlined(),
        "b_1_addr".green(),
        b_1_addr.clone().magenta().italic().on_black(),
        "b_1_ptr_addr".green(),
        b_1_ptr_addr.clone().magenta().italic().on_black(),
    );

    let b_2 = b_1;
    // println!("{b_1:p}"); // ⛔ error: use of moved value: `b_1`
    let b_2_addr = print_ptr_addr_size!(b_2.as_ref()); // Pointee (heap)
    let b_2_ptr_addr = print_ptr_addr_size!(&b_2); // Pointer (stack)

    println!(
        "2. {}: {}, {} (pointee, heap): {}, {} (ptr, stack): {}",
        "b_2".green(),
        b_2.to_string().blue().underlined(),
        "b_2_addr".green(),
        b_2_addr.clone().magenta().italic().on_black(),
        "b_2_ptr_addr".green(),
        b_2_ptr_addr.clone().magenta().italic().on_black(),
    );

    // The heap memory allocation does not change (does not move). Pointee does not move.
    assert_eq!(b_1_addr, b_2_addr);

    // The stack memory allocation does change (does move). Boxes aka pointers have move.
    assert_ne!(b_1_ptr_addr, b_2_ptr_addr);

    // When b_2 is dropped, the heap allocation is deallocated. This is why Box is a smart pointer.
}
```

Let's walk through the output above:
1. We have a `Box` `b_1` that points to a heap allocation of a `u8` with a value of `255`.
   `b_1` is a variable on the stack that points to a heap allocation. We get the address
   of the pointee and the pointer using the `print_ptr_addr_size!` macro with
   `b_1.as_ref()`. And we get the address of the pointer by passing `&b_1` to
   `print_ptr_addr_size!`.
2. We move `b_1` into `b_2`. The heap memory allocation does not change (does not move).
   The pointee does not move. But the stack memory allocation does change (does move).
   Boxes aka pointers have moved. The `b_1` variable gets dropped. We can get the address
   of the pointee using `print_ptr_addr_size!` macro with `b_2.as_ref()`. We can get the
   address of the pointer using `print_ptr_addr_size!` macro with `&b_2`.
3. In the assertions, we check that the heap memory allocation does **not** change (does
   not move). And we check that the stack memory allocation **does** change (does move).

### Example 3: How do we swap the contents of two boxes?
<a id="markdown-example-3%3A-how-do-we-swap-the-contents-of-two-boxes%3F" name="example-3%3A-how-do-we-swap-the-contents-of-two-boxes%3F"></a>

Add the following snippet to the `lib.rs` file next.

```rs
#[test]
#[serial]
fn swap_box_contents() {
    let mut b_1 = Box::new(100u8);
    let mut b_2 = Box::new(200u8);

    let og_b_1_addr = print_ptr_addr_size!(b_1.as_ref());
    let og_b_2_addr = print_ptr_addr_size!(b_2.as_ref());

    assert_eq!(*b_1, 100u8);
    assert_eq!(*b_2, 200u8);

    println!(
        "1. {}: {}, {} (pointee, heap): {}, {} (ptr, stack): {}",
        "b_1".green(),
        b_1.to_string().blue().underlined(),
        "b_1_addr".green(),
        og_b_1_addr.clone().red().italic().on_black(),
        "b_1_ptr_addr".green(),
        print_ptr_addr_size!(&b_1)
            .clone()
            .magenta()
            .italic()
            .on_black(),
    );
    println!(
        "2. {}: {}, {} (pointee, heap): {}, {} (ptr, stack): {}",
        "b_2".green(),
        b_2.to_string().blue().underlined(),
        "b_2_addr".green(),
        og_b_2_addr.clone().magenta().italic().on_black(),
        "b_2_ptr_addr".green(),
        print_ptr_addr_size!(&b_2)
            .clone()
            .cyan()
            .italic()
            .on_black(),
    );

    std::mem::swap(&mut b_1, &mut b_2);
    println!("{}", "Swapped b_1 and b_2".cyan().underlined());

    let new_b_1_addr = print_ptr_addr_size!(b_1.as_ref());
    let new_b_2_addr = print_ptr_addr_size!(b_2.as_ref());

    assert_eq!(*b_1, 200u8);
    assert_eq!(*b_2, 100u8);

    assert_eq!(og_b_1_addr, new_b_2_addr);
    assert_eq!(og_b_2_addr, new_b_1_addr);

    println!(
        "3. {}: {}, {} (pointee, heap): {}, {} (ptr, stack): {}",
        "b_1".green(),
        b_1.to_string().blue().underlined(),
        "b_1_addr".green(),
        new_b_1_addr.clone().magenta().italic().on_black(),
        "b_1_ptr_addr".green(),
        print_ptr_addr_size!(&b_1)
            .clone()
            .magenta()
            .italic()
            .on_black(),
    );
    println!(
        "4. {}: {}, {} (pointee, heap): {}, {} (ptr, stack): {}",
        "b_2".green(),
        b_2.to_string().blue().underlined(),
        "b_2_addr".green(),
        new_b_2_addr.clone().red().italic().on_black(),
        "b_2_ptr_addr".green(),
        print_ptr_addr_size!(&b_2)
            .clone()
            .cyan()
            .italic()
            .on_black(),
    );
}
```

Here's the output of the test above, after you run `cargo watch -x "test --lib -- --show-output swap"`.

<pre class="pre-manual-highlight">
---- swap_box_contents stdout ----
1. <span style="color:#A3BE8C">b_1</span>: <span style="color:#81A1C1"><u style="text-decoration-style:solid">100</u></span>, <span style="color:#A3BE8C">b_1_addr</span> (pointee, heap): <span style="background-color:#3B4252"><span style="color:#BF616A"><i>0x722b38000d10┆1b</i></span></span>, <span style="color:#A3BE8C">b_1_ptr_addr</span> (ptr, stack): <span style="background-color:#3B4252"><span style="color:#B48EAD"><i>0x722b3cbfdad0┆8b</i></span></span>
2. <span style="color:#A3BE8C">b_2</span>: <span style="color:#81A1C1"><u style="text-decoration-style:solid">200</u></span>, <span style="color:#A3BE8C">b_2_addr</span> (pointee, heap): <span style="background-color:#3B4252"><span style="color:#B48EAD"><i>0x722b38001f30┆1b</i></span></span>, <span style="color:#A3BE8C">b_2_ptr_addr</span> (ptr, stack): <span style="background-color:#3B4252"><span style="color:#8FBCBB"><i>0x722b3cbfdad8┆8b</i></span></span>
<span style="color:#8FBCBB"><u style="text-decoration-style:solid">Swapped b_1 and b_2</u></span>
3. <span style="color:#A3BE8C">b_1</span>: <span style="color:#81A1C1"><u style="text-decoration-style:solid">200</u></span>, <span style="color:#A3BE8C">b_1_addr</span> (pointee, heap): <span style="background-color:#3B4252"><span style="color:#B48EAD"><i>0x722b38001f30┆1b</i></span></span>, <span style="color:#A3BE8C">b_1_ptr_addr</span> (ptr, stack): <span style="background-color:#3B4252"><span style="color:#B48EAD"><i>0x722b3cbfdad0┆8b</i></span></span>
4. <span style="color:#A3BE8C">b_2</span>: <span style="color:#81A1C1"><u style="text-decoration-style:solid">100</u></span>, <span style="color:#A3BE8C">b_2_addr</span> (pointee, heap): <span style="background-color:#3B4252"><span style="color:#BF616A"><i>0x722b38000d10┆1b</i></span></span>, <span style="color:#A3BE8C">b_2_ptr_addr</span> (ptr, stack): <span style="background-color:#3B4252"><span style="color:#8FBCBB"><i>0x722b3cbfdad8┆8b</i></span></span>
</pre>

Let's walk through the output above:
1. We have two `Box`es `b_1` and `b_2` that point to heap allocations of `u8` with values
   `100` and `200` respectively. We get the address of the pointees using
   the `print_ptr_addr_size!` macro with `b_1.as_ref()` and `b_2.as_ref()`. We get the
   address of the pointers using the `print_ptr_addr_size!` macro with `&b_1` and `&b_2`.
2. We swap the contents of `b_1` and `b_2` using `std::mem::swap(&mut b_1, &mut b_2)`.
   The values of `b_1` and `b_2` are now `200` and `100` respectively.
3. We get the new addresses of the pointees using the `print_ptr_addr_size!` macro with
   `b_1.as_ref()` and `b_2.as_ref()`. We get the new addresses of the pointers using the
   `print_ptr_addr_size!` macro with `&b_1` and `&b_2`.
4. In the assertions, we check that the values of `b_1` and `b_2` are `200` and `100`
   respectively. We check that the addresses of the pointees **have** swapped. And we check
   that the addresses of the pointers have **not** swapped.

### Example 4: What does pining a box do?
<a id="markdown-example-4%3A-what-does-pining-a-box-do%3F" name="example-4%3A-what-does-pining-a-box-do%3F"></a>

Add the following code to your `lib.rs` file.

```rs
fn box_and_pin_dynamic_duo() {
    let b_1 = Box::new(100u8);
    // Pointee.
    let b_1_addr = print_ptr_addr_size!(b_1.as_ref());

    let p_b_1 = std::boxed::Box::<u8>::into_pin(b_1);
    // Pinned.
    let p_b_1_addr = print_pin_addr_size!(p_b_1);

    let b_2 = p_b_1;
    // println!("{}", p_b_1); // ⛔ error: use of moved value: `p_b_1`

    // Pin does not move.
    let b_2_addr = print_pin_addr_size!(b_2);

    // Pointee has not moved!
    assert_eq!(b_1_addr, b_2_addr);

    // Pointer has not moved!
    assert_three_equal(&b_1_addr, &p_b_1_addr, &b_2_addr);
}
```

When you run the command `cargo watch -x "test --lib -- --show-output dynamic"` it doesn't
really produce any output.

Let's walk through the code above:
1. We have a `Box` `b_1` that points to a heap allocation of a `u8` with a value of `100`.
   We get the address of the pointee using the `print_ptr_addr_size!` macro with
   `b_1.as_ref()`.
2. We pin `b_1` into `p_b_1` using `std::boxed::Box::<u8>::into_pin(b_1)`. The pointee
   does not move. We get the address of the pinned pointer using the
   `print_pin_addr_size!` macro with `p_b_1`.
3. We move `p_b_1` into `b_2`. The pin does not move. We get the address of the pinned
   pointer using the `print_pin_addr_size!` macro with `b_2`.
4. In the assertions, we check that the pointee has **not** moved. And we check that the
   pointer has **not** moved.

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
