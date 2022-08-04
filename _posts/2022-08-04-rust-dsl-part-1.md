---
title: "Create DSLs with Rust - Part 1"
author: Nazmul Idris
date: 2022-08-04 15:00:00+00:00
excerpt: |
  Procedural macros are a way for you to extend the Rust complier and provide plugins
  that you can use to extend the language. They allow to create your own DSL (domain
  specific language). This article goes into the details of creating a simple DSL to 
  mimic the CSS language but in Rust, for a TUI app framework.
layout: post
categories:
  - Rust
  - MP
  - CLI
  - TUI
---

<img class="post-hero-image" src="{{ 'assets/rust-dsl.svg' | relative_url }}"/>

<!-- TOC -->

- [Create a simple DSL for CSS](#create-a-simple-dsl-for-css)
- [What are procedural macros](#what-are-procedural-macros)
- [Heading 1](#heading-1)
- [Heading 2](#heading-2)
- [Learning resources](#learning-resources)
- [Wrapping up](#wrapping-up)

<!-- /TOC -->

## Create a simple DSL for CSS like styling

<a id="markdown-create-a-simple-dsl-for-css" name="create-a-simple-dsl-for-css"></a>

- TK: provide an intro to what we are going to achieve in this article (simple CSS syntax)
- TK: provide context (the tui library) for this work (why is it important to build this?)
- TK: provide some hint about what greater ambitions we have (stylesheet syntax, JSX like syntax)

## What are procedural macros

<a id="markdown-what-are-procedural-macros" name="what-are-procedural-macros"></a>

For an introduction to procedural macros, please read our article
[Procedural Macros](https://developerlife.com/2022/03/30/rust-proc-macro/). The following is a
snippet from this article.

> 🔮 **Procedural macros** are a way for you to extend the Rust complier and provide plugins that
> you can use to extend the language. They are really powerful and require some more work to setup
> in an existing project (you have to create a new library create just for them and they all have to
> be declared in the `lib.rs` file). Here are the key benefits of procedural macros:
>
> - Minimize the amount of manual work you have to do in order to generate boilerplate code 🎉. This
>   is similar to
>   [annotation processing](https://developerlife.com/2020/07/11/annotation-processing-kotlin-android/)
>   in Java and Kotlin.
> - You can create your own domain specific language like React JSX in Rust 🎉. Create your own
>   [DSL (domain specific language)](https://developerlife.com/2020/04/04/kotlin-dsl-intro/) like in
>   Kotlin and babel and JavaScript.

> 🪄 **Declarative macros** have many limitations (eg: they can't work with generics) but are easier
> to use. If you have simple use cases they work great, since they are so easy to write. Here are
> some resources to help you w/ learning declarative macros.
>
> 1. [Declarative macros included in this article's repo (but not covered in this article)](https://github.com/nazmulidris/rust_scratch/blob/main/macros/tests/decl/main.rs)
> 2. [Little book of Rust macros](https://veykril.github.io/tlborm/introduction.html)
> 3. [Great YT video on declarative macros](https://youtu.be/q6paRBbLgNw)

> Here's a summary:
>
> | Macro type                 | Capabilities & limitations                                                                                               |
> | -------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
> | Declarative                | Can't handle generics, patterns capture items as _wholes_ and can't be broken down in the macro body                     |
> | Procedural - function like | Operates on the code passed inside parenthesis of invocation to produce new token stream.                                |
> | Procedural - derive        | Can't touch token stream of annotated `struct` or `enum`, only add new token stream below; can declare helper attributes |
> | Procedural - attribute     | Like function-like, replaces token stream of annotated item (not just `struct` or `enum`)                                |

## Heading 1

<a id="markdown-heading-1" name="heading-1"></a>

## Heading 2

<a id="markdown-heading-2" name="heading-2"></a>

## Learning resources

<a id="markdown-learning-resources" name="learning-resources"></a>

## Wrapping up

<a id="markdown-wrapping-up" name="wrapping-up"></a>

In the future we will expand this DSL to include more features like generating the entire stylesheet
declaratively. And then move on to creating JSX like syntax in Rust for the TUI library.

> 📜 You can find all the examples of procedural macros shown in this article in the
> `r3bl_rs_utils_macro` [repo](https://github.com/r3bl-org/r3bl_rs_utils/tree/main/macro/). This is
> just part of the `r3bl_rs_utils` [crate](https://crates.io/crates/r3bl_rs_utils).
