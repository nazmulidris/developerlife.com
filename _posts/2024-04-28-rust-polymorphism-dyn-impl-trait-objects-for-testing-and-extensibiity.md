---
title:
  "Build with Naz : Rust Polymorphism, dyn, impl, using existing traits, trait objects for testing and extensibility"
author: Nazmul Idris
date: 2024-04-28 15:00:00+00:00
excerpt: |
  Learn how to implement effective Rust polymorphism, using `dyn`, `impl`, existing traits, and trait objects for
  testing and extensibility, in real world projects.
layout: post
categories:
  - Rust
  - CLI
  - Server
---

<img class="post-hero-image" src="{{ 'assets/rust_polymorphism.svg' | relative_url }}"/>

<!-- TOC -->

- [Why use polymorphism in Rust?](#why-use-polymorphism-in-rust)
- [Short example to illustrate both approaches](#short-example-to-illustrate-both-approaches)
- [Build with Naz video series on developerlife.com YouTube channel](#build-with-naz-video-series-on-developerlifecom-youtube-channel)

<!-- /TOC -->

## Why use polymorphism in Rust?
<a id="markdown-why-use-polymorphism-in-rust%3F" name="why-use-polymorphism-in-rust%3F"></a>


When it comes to polymorphism in Rust, which means that you want to be intentionally "vague" about
what arguments a function can receive or what values it can return, there are roughly two
approaches: static dispatch and dynamic dispatch. They are both tightly related to the notion of
sidedness in Rust.

There are many legitimate reasons to be intentionally vague about the types of arguments a function
can receive or the values it can return. Here are a few:

- Testing: You want swap out the implementation of a function with a test mock or test fixture, so
  that you can test the function in isolation.
- Extensibility: You want to accommodate integrations with other code that you don't control, and
  you want to be able to use dependency injection to provide the intended behaviors (from) systems
  that you don't control.
- Reuse: You want to reuse the same code in multiple places, since they only operate on on aspect
  (or trait) of the data.

Here are the two approaches to polymorphism in Rust:

| static  | dynamic |
| ------- | ------- |
| receive | receive |
| return  | return  |

There are pros and cons to each approach:

| approach | pros                                                                                                                                  | cons                                                                                                                          |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| static   | Compile time checks and dispatch. No runtime overhead.                                                                                | Code is more difficult to read and write since generics and their often verbose trait bounds have to be spread to the caller. |
| dynamic  | Code is more concise and easier to read and write since the trait objects are localized to the function that accepts or returns them. | Runtime overhead due to dynamic dispatch. Vtable lookup is required due to type erasure.                                      |

Here are some helpful links to learn more about this topic:

- [Great Crust of Rust video on monomorphization, generics, vtables, fat pointers, static dispatch, and dynamic dispatch](https://www.youtube.com/watch?v=xcygqF5LVmM&t=1162s)
- [Vtables](https://developerlife.com/2022/03/12/rust-redux/#of-things-and-their-managers)
- [Diagram of sizes](https://developerlife.com/assets/rust-container-cheat-sheet.svg)
- [Sizedness](https://github.com/pretzelhammer/rust-blog/blob/master/posts/sizedness-in-rust.md)
- [Difference between using `Arc` and `Box` with `dyn`](https://gemini.google.com/app/157980ca7d9b588c)
- [Book on `dyn` and `Box`](https://rust-unofficial.github.io/too-many-lists/index.html)

## Video of this in action in the real world
<a id="markdown-video-of-this-in-action-in-the-real-world" name="video-of-this-in-action-in-the-real-world"></a>

This blog post only has a short example to illustrate both approaches to polymorphism in
Rust. To see how these ideas can be used in production code, with real-world examples,
please watch the following video on the [developerlife.com YouTube
channel](https://www.youtube.com/@developerlifecom).

<!-- video on rust polymorphism (no playlist) -->
<iframe
    src="https://www.youtube.com/embed/kYTgGtJjSro?si=XmW-_CAvCfB5e269"
    title="YouTube video player" frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    referrerpolicy="strict-origin-when-cross-origin"
    allowfullscreen
    >
</iframe>

## Short example to illustrate both approaches
<a id="markdown-short-example-to-illustrate-both-approaches" name="short-example-to-illustrate-both-approaches"></a>


The code for this example lives
[here](https://github.com/nazmulidris/rust-scratch/tree/main/dyn-dispatch/src).

Let's look a single example (that fits in one file) that illustrates both approaches to polymorphism
in Rust. You can run `cargo new --lib dyn-dispatch` to create a new library crate, and then run
`cargo add rand`. Then you can add the following code to the `src/lib.rs` file.

This first part is the setup for this example. We have two structs, each of which
implements the [`Error`](https://doc.rust-lang.org/std/io/struct.Error.html) trait. We
want to be able to use both structs in functions that can receive or return
[`Error`](https://doc.rust-lang.org/std/io/struct.Error.html) trait objects.

```rust
use std::error::Error;
use std::fmt::Display;

// ErrorOne.
mod error_one {
    use super::*;

    #[derive(Debug)]
    pub struct ErrorOne;

    impl Display for ErrorOne {
        fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
            write!(f, "ErrorOne")
        }
    }

    impl Error for ErrorOne {}
}
use error_one::ErrorOne;

// ErrorTwo.
mod error_two {
    use super::*;

    #[derive(Debug)]
    pub struct ErrorTwo;

    impl Display for ErrorTwo {
        fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
            write!(f, "ErrorTwo")
        }
    }

    impl Error for ErrorTwo {}
}
use error_two::ErrorTwo;
```

In some of the code we will need to make a random decision, so we'll use the `rand` crate to
generate random booleans.

```rust
// Random boolean generator.
pub fn random_bool() -> bool {
    rand::random()
}
```

Here's the code for the static dispatch approach, using generics, trait bounds, and compiler
monomorphisation.

```rust
// Static dispatch.
mod static_dispatch {
    use super::*;

    mod receives {
        use super::*;

        pub fn accept_error<E: Error>(error: E) {
            println!("Handling ErrorOne Debug: {:?}", error);
            println!("Handling ErrorOne Display: {}", error);
        }

        pub fn accept_error_with_syntactic_sugar(error: impl Error) {
            println!("Handling ErrorOne Debug: {:?}", error);
            println!("Handling ErrorOne Display: {}", error);
        }
    }

    mod returns {
        use super::*;

        pub fn return_error_one() -> ErrorOne {
            ErrorOne
        }

        pub fn return_error_two() -> ErrorTwo {
            ErrorTwo
        }

        // 🚨 DOES NOT WORK! Need dynamic dispatch.
        // pub fn return_single_error() -> impl Error {
        //     if random_bool() {
        //         ErrorOne
        //     } else {
        //         ErrorTwo
        //     }
        // }

        pub fn return_single_error() -> impl Error {
            return ErrorOne;
        }
    }
}
```

Finally, here's the code for the dynamic dispatch approach, using trait objects and vtables to
enable runtime polymorphism.

```rust
// Dynamic dispatch.
mod dynamic_dispatch {
    use super::*;

    mod receives {
        use super::*;

        pub fn recieve_error_by_ref(error: &dyn Error) {
            println!("Handling Error Debug: {:?}", error);
            println!("Handling Error Display: {}", error);
        }

        pub fn example_1() {
            let error_one = ErrorOne;
            recieve_error_by_ref(&error_one);
            let error_two = ErrorTwo;
            recieve_error_by_ref(&error_two);
        }

        pub fn receive_error_by_box(error: Box<dyn Error>) {
            println!("Handling Error Debug: {:?}", error);
            println!("Handling Error Display: {}", error);
        }

        pub fn example_2() {
            let error_one = ErrorOne;
            let it = Box::new(error_one);
            receive_error_by_box(it);
            let error_two = ErrorTwo;
            receive_error_by_box(Box::new(error_two));
        }

        pub fn receive_slice_of_errors(arg: &[&dyn Error]) {
            for error in arg {
                println!("Handling Error Debug: {:?}", error);
                println!("Handling Error Display: {}", error);
            }
        }
    }

    mod returns {
        use super::*;

        pub fn return_one_of_two_errors() -> Box<dyn Error> {
            if random_bool() {
                Box::new(ErrorOne)
            } else {
                Box::new(ErrorTwo)
            }
        }

        pub fn return_one_of_two_errors_with_arc() -> std::sync::Arc<dyn Error> {
            if random_bool() {
                std::sync::Arc::new(ErrorOne)
            } else {
                std::sync::Arc::new(ErrorTwo)
            }
        }

        pub fn return_slice_of_errors() -> Vec<&'static dyn Error> {
            let mut errors: Vec<&dyn Error> = vec![];
            if random_bool() {
                errors.push(&(ErrorOne));
            } else {
                errors.push(&(ErrorTwo));
            }
            errors
        }

        pub fn mut_vec_containing_different_types_of_errors(mut_vec: &mut Vec<&dyn Error>) {
            mut_vec.push(&ErrorOne);
            mut_vec.push(&ErrorTwo);
        }
    }
}
```

## Build with Naz video series on developerlife.com YouTube channel
<a id="markdown-build-with-naz-video-series-on-developerlife.com-youtube-channel" name="build-with-naz-video-series-on-developerlife.com-youtube-channel"></a>

> If you have comments and feedback on this content, or would like to request new content
> (articles & videos) on developerlife.com, please join our [discord
> server](https://discord.gg/8M2ePAevaMi).

You can watch a video series on building this crate with Naz on the
[developerlife.com YouTube channel](https://www.youtube.com/@developerlifecom).

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
    - [Part 3: Polymorphism, static and dynamic dispatch](https://www.youtube.com/watch?v=kYTgGtJjSro)
    - Playlists
        - [Build with Naz, fundamental effective Rust](https://www.youtube.com/playlist?list=PLofhE49PEwmza94sS7UmJnN9gSCHTVTfz)
        - [Build with Naz, effective async Rust and tokio](https://www.youtube.com/playlist?list=PLofhE49PEwmwO69E7eiQ-ewnMME8ydgQ5)
        - [Build with Naz, async readline and spinner for CLI in Rust](https://www.youtube.com/watch?v=3vQJguti02I&list=PLofhE49PEwmwelPkhfiqdFQ9IXnmGdnSE)
        - [Build with Naz, testing in Rust](https://www.youtube.com/watch?v=Xt495QLrFFk&list=PLofhE49PEwmwLR_4Noa0dFOSPmSpIg_l8)
