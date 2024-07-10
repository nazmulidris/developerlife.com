---
title: "Guide to Rust procedural macros"
author: Nazmul Idris
date: 2022-03-30 15:00:00+00:00
excerpt: |
  Procedural macros are a way for you to extend the Rust compiler and provide plugins
  that you can use to extend the language. They allow you to reduce the need to write
  manual boilerplate code, and even allow you to create your own DSL (domain specific
  language). This article goes into the details of creating the 3 kinds of procedural
  macros in Rust.
layout: post
categories:
  - Rust
  - MP
---

<img class="post-hero-image" src="{{ 'assets/rust-proc-macro.svg' | relative_url }}"/>

<!-- TOC -->

- [What are procedural macros](#what-are-procedural-macros)
  - [Declarative macros have limitations](#declarative-macros-have-limitations)
  - [Summary of proc vs decl macros](#summary-of-proc-vs-decl-macros)
  - [Source code examples](#source-code-examples)
- [How to add a proc macro lib crate to your existing project](#how-to-add-a-proc-macro-lib-crate-to-your-existing-project)
  - [Add an internal or core crate](#add-an-internal-or-core-crate)
- [What does a syn AST look like?](#what-does-a-syn-ast-look-like)
- [How to write a proc macro of any kind](#how-to-write-a-proc-macro-of-any-kind)
  - [Strategy](#strategy)
  - [Examples](#examples)
  - [Writing your own Parse trait impl in different ways](#writing-your-own-parse-trait-impl-in-different-ways)
- [Eg 1 - Function-like macro that dumps the AST](#eg-1---function-like-macro-that-dumps-the-ast)
- [Eg 2 - Function-like macro that parses custom syntax](#eg-2---function-like-macro-that-parses-custom-syntax)
  - [Desired syntax and behavior](#desired-syntax-and-behavior)
  - [Implementing the syntax parser](#implementing-the-syntax-parser)
  - [Implementing the code generator](#implementing-the-code-generator)
- [Eg 3 - Derive macro that adds a method to a struct](#eg-3---derive-macro-that-adds-a-method-to-a-struct)
  - [Test for expected output](#test-for-expected-output)
  - [Watch macro expansion](#watch-macro-expansion)
  - [Naive implementation](#naive-implementation)
  - [Better implementation that handles generics](#better-implementation-that-handles-generics)
  - [Using quote!](#using-quote)
- [Eg 4 - Derive macro that generates a builder](#eg-4---derive-macro-that-generates-a-builder)
  - [Stub out the implementation](#stub-out-the-implementation)
  - [Testing the macro](#testing-the-macro)
  - [Implementation details](#implementation-details)
- [Eg 5 - Attribute macro that adds logging to a function](#eg-5---attribute-macro-that-adds-logging-to-a-function)
  - [Create entry in lib.rs](#create-entry-in-librs)
  - [How to parse item?](#how-to-parse-item)
  - [How to parse args containing attributes for variant 1?](#how-to-parse-args-containing-attributes-for-variant-1)
  - [How to parse args containing set of identifiers for variant 2?](#how-to-parse-args-containing-set-of-identifiers-for-variant-2)
- [Learning resources](#learning-resources)
- [Build with Naz video series on developerlife.com YouTube channel](#build-with-naz-video-series-on-developerlifecom-youtube-channel)

<!-- /TOC -->

## What are procedural macros
<a id="markdown-what-are-procedural-macros" name="what-are-procedural-macros"></a>

**Procedural macros** are a way for you to extend the Rust compiler and provide plugins that you can
use to extend the language. They are really powerful and require some more work to setup in an
existing project (you have to create a new library create just for them and they all have to be
declared in the `lib.rs` file). Here are the key benefits of procedural macros:

- Minimize the amount of manual work you have to do in order to generate boilerplate code 🎉. This
  is similar to
  [annotation processing](https://developerlife.com/2020/07/11/annotation-processing-kotlin-android/)
  in Java and Kotlin.
- You can create your own domain specific language like React JSX in Rust 🎉. Create your own
  [DSL (domain specific language)](https://developerlife.com/2020/04/04/kotlin-dsl-intro/) like in
  Kotlin and babel and JavaScript.

### Declarative macros have limitations
<a id="markdown-declarative-macros-have-limitations" name="declarative-macros-have-limitations"></a>

For example they can't work with generics. They are easier to write than procedural
macros. If you have simple use cases they work great, since they are so easy to write.
Here are some resources to help you w/ learning declarative macros.

1. [Declarative macros in `r3bl-open-core` repo](https://github.com/r3bl-org/r3bl-open-core/search?q=macro_rules)
2. [Declarative macros included in this article's repo (but not covered in this article)](https://github.com/nazmulidris/rust_scratch/blob/main/macros/tests/decl/main.rs)
3. [Little book of Rust macros](https://veykril.github.io/tlborm/introduction.html)
4. [Great YT video on declarative macros](https://youtu.be/q6paRBbLgNw)

### Summary of proc vs decl macros
<a id="markdown-summary-of-proc-vs-decl-macros" name="summary-of-proc-vs-decl-macros"></a>

| Macro type                 | Capabilities & limitations                                                                                               |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Declarative                | Can't handle generics, patterns capture items as _wholes_ and can't be broken down in the macro body                     |
| Procedural - function like | Operates on the code passed inside parenthesis of invocation to produce new token stream.                                |
| Procedural - derive        | Can't touch token stream of annotated `struct` or `enum`, only add new token stream below; can declare helper attributes |
| Procedural - attribute     | Like function-like, replaces token stream of annotated item (not just `struct` or `enum`)                                |

### Source code examples
<a id="markdown-source-code-examples" name="source-code-examples"></a>

1. You can find "real world" examples of both declarative and procedural macros in the
   `r3bl-open-core` [repo](https://github.com/r3bl-org/r3bl-open-core).
   - [proc macros](https://github.com/r3bl-org/r3bl-open-core/tree/main/macro)
   - [decl macros](https://github.com/r3bl-org/r3bl-open-core/search?q=macro_rules)
2. You can find all the pedagogical examples of macros shown in this article in this
   [repo](https://github.com/nazmulidris/rust_scratch/blob/main/macros/).

> For more information on general Rust type system design (functional approach rather than
> object oriented), please take a look at this [paper](https://arxiv.org/pdf/2307.07069.pdf)
> by Will Crichton demonstrating Typed Design Patterns with Rust.

## How to add a proc macro lib crate to your existing project
<a id="markdown-how-to-add-a-proc-macro-lib-crate-to-your-existing-project" name="how-to-add-a-proc-macro-lib-crate-to-your-existing-project"></a>

Rust has two kinds of macros: declarative and procedural. Declarative macros are made using
`macro_rules!` inline in your code w/out creating a new lib crate. This article is about procedural
macros which are the imperative style of creating Rust macros.

> 🤔 One complication with using procedural macros is that they are not allowed to be used in the
> same crate where your code lives. This requires us to create a new library create inside our
> existing Rust project.

The first step in using procedural macros is to create a new library crate.

Here are the steps that we must take starting in our existing Rust project (which maybe a lib or bin
or both project).

1. Create a new crate inside our existing Rust project.

   - Run the following command to create a new `my_proc_macros_lib` crate inside your existing
     project.
     ```shell
     $ cargo new --lib my_proc_macros_lib
     ```
   - Inside the newly created `my_proc_macros_lib` folder you will find:
     - A `Cargo.toml` file. Make sure to add these dependencies to this file:
       - `quote = "*"`
       - `syn = { version = "*", features = ["extra-traits"] }`
       - `proc-macro2 = "*"`
     - A `src` folder w/ a `lib.rs` file inside of it. All proc macro functions (annotated w/
       `#[proc_macro]`) must be defined in this file and no other. You can however import code from
       other modules just like normal. You can think of this file as a place where you "export" the
       definitions of your macros to other crates. Kind of like a registry or manifest of procedural
       macros in this lib crate that the Rust compiler can discover and use easily.

2. You now have to This declares this newly created crate as a dependency of your main project.

   - Add the following to your main project's `Cargo.toml` file:
     ```toml
     [dependencies]
     my_proc_macros_lib = { path = "my_proc_macros_lib" }
     ```

3. You can now use the code in this `my_proc_macros_lib` crate by importing them in the code of your
   main like so: `use my_proc_macros_lib::*`.

Here's an example of a `Cargo.toml` for the proc macro lib crate:

```toml
[package]
name = "my_proc_macros_lib"
version = "0.1.0"
edition = "2021"

[lib]
name = "my_proc_macros_lib"
path = "src/lib.rs"
proc-macro = true

[dependencies]
# https://github.com/dtolnay/proc-macro-workshop#debugging-tips
syn = { version = "*", features = ["extra-traits"] }
quote = "*"
proc-macro2 = "*"
r3bl_rs_utils = "*"
```

> 🗜️ It is also a good idea to install `cargo expand` to see what your code your macros actually
> expand into. You will need two things:
>
> 1. `cargo install cargo-expand` which installs `cargo expand`.
> 2. `rustup toolchain install nightly` which installs the Rust nightly toolchain that's needed by
>    `cargo expand`.
>
> Then you can run a command like the following `cargo expand --test test_derive_macro_describe` to
> expand the test `test_derive_macro_describe`.
>
> 👀 To watch for changes in your code and run the above command, you can install
> `cargo install cargo-watch` and then run:
> `cargo watch -x 'expand --test test_derive_macro_describe'`.
>
> 1. A script is provided called `cargo-watch-macro-expand-one-test.fish` which does this for the
>    test that you give that script as an argument.
> 2. Another script is provided called `cargo-watch-one-test.fish` which watches for changes in your
>    and then runs the test you give that script as an argument.

### Add an internal or core crate
<a id="markdown-add-an-internal-or-core-crate" name="add-an-internal-or-core-crate"></a>

There are situations where you will need to share code between your public crate and your procedural
macro crate. In this case you can add an internal or core crate to your project. The shared files
will all go inside of this core or internal crate.

For more information on this, please check out
[this stackoverflow thread](https://stackoverflow.com/a/64288799/2085356).

The basic steps look like this:

1. Add a new crate `my_core_lib` and create the following dependencies:
   - public crate (eg: `r3bl_rs_utils`) deps: `[my_core_lib, my_proc_macros_lib]`
   - proc macro crate (eg: `my_proc_macros_lib`) deps: `[my_core_lib]`
2. The files that need to be shared everywhere (public & proc macro crates) need to go in the
   `my_core_lib` crate.

> 📦 Here's a real example of this from the
> [`r3bl_rs_utils`](https://crates.io/crates/r3bl_rs_utils) crate which applies this change in this
> [commit](https://github.com/r3bl-org/r3bl-rs-utils/commit/c5b57f7b81e746a7277191dc1593237b5bc12867).
>
> 🌟 Please star the [`r3bl-open-core` repo](https://github.com/r3bl-org/r3bl-open-core) on github if
> you like it 🙏.

If you publish the public crate to crates.io, then you will need to publish each of the dependent
crates as well. This won't happen automatically when publishing the public crate, you have to go in
and run `cargo publish` on each and every dependent crate and they will be their own installable
crate on crates.io.

## What does a syn AST look like?
<a id="markdown-what-does-a-syn-ast-look-like%3F" name="what-does-a-syn-ast-look-like%3F"></a>

Before writing macros, let's talk about how we need to think about things:

1. Instead of working w/
   [`TokenStream`](https://doc.rust-lang.org/proc_macro/struct.TokenStream.html)s, we will work w/
   an [AST (abstract syntax tree)](https://en.wikipedia.org/wiki/Abstract_syntax_tree) generated by
   [`syn::*`](https://github.com/dtolnay/syn/tree/master/examples) functions and macros. This will
   make our life much easier.

2. We will then walk parts of this tree and generate code using
   [`quote!`](https://docs.rs/quote/latest/quote/macro.quote.html) which will generate a new
   `TokenStream` that will then be returned by our procedural macro.

Let's take a look at what an AST actually looks like. Here's an example of what you get from parsing
the string `"fn foo() -> u32 { 42 }"` using
[`syn::parse_str()`](https://docs.rs/syn/latest/syn/fn.parse_str.html):

```rust
    attrs: [],
    vis: Inherited,
    sig: Signature {
        constness: None,
        asyncness: None,
        unsafety: None,
        abi: None,
        fn_token: Fn,
        ident: Ident {
            ident: "foo",
            span: #5 bytes(91..125),
        },
        generics: Generics {
            lt_token: None,
            params: [],
            gt_token: None,
            where_clause: None,
        },
        paren_token: Paren,
        inputs: [],
        variadic: None,
        output: Type(
            RArrow,
            Path(
                TypePath {
                    qself: None,
                    path: Path {
                        leading_colon: None,
                        segments: [
                            PathSegment {
                                ident: Ident {
                                    ident: "u32",
                                    span: #5 bytes(91..125),
                                },
                                arguments: None,
                            },
                        ],
                    },
                },
            ),
        ),
    },
    block: Block {
        brace_token: Brace,
        stmts: [
            Expr(
                Lit(
                    ExprLit {
                        attrs: [],
                        lit: Int(
                            LitInt {
                                token: 42,
                            },
                        ),
                    },
                ),
            ),
        ],
    },
}
```

> 💡 Here's an example from the syn repo that shows you how to read in a Rust file and dump it into
> a syn AST:
> [dump-syntax](https://github.com/dtolnay/syn/blob/master/examples/dump-syntax/src/main.rs).

## How to write a proc macro of any kind
<a id="markdown-how-to-write-a-proc-macro-of-any-kind" name="how-to-write-a-proc-macro-of-any-kind"></a>

There are 3 kinds of proc macros. Once you've created a new library crate for them inside your
project, you write macros like the ones shown below.

> 📜 This article will provide examples of each of these types of macros. You can find them all in
> this [repo](https://github.com/nazmulidris/rust_scratch/blob/main/macros/).
>
> 💡 You can also take a look at this tutorial by
> [JetBrains](https://blog.jetbrains.com/rust/2022/03/18/procedural-macros-under-the-hood-part-i/)
> which goes into visual descriptions of the AST, token tree, etc.

```rust
extern crate proc_macro;
use proc_macro::TokenStream;

#[proc_macro]
pub fn my_fn_like_proc_macro(input: TokenStream) -> TokenStream {
  // 1. Use syn to parse the input tokens into a syntax tree.
  // 2. Use quote to generate new tokens based on what we parsed.
  // 3. Return the generated tokens.
  input
}

#[proc_macro_derive(MyDerive)]
pub fn my_derive_proc_macro(input: TokenStream) -> TokenStream {
  // 1. Use syn to parse the input tokens into a syntax tree.
  // 2. Generate new tokens based on the syntax tree. This is additive to the `enum` or
  //    `struct` that is annotated (it doesn't replace them).
  // 3. Return the generated tokens.
  input
}

#[proc_macro_attribute]
pub fn log_entry_and_exit(args: TokenStream, input: TokenStream) -> TokenStream {
  // 1. Use syn to parse the args & input tokens into a syntax tree.
  // 2. Generate new tokens based on the syntax tree. This will replace whatever `item` is
  //    annotated w/ this attribute proc macro.
  // 3. Return the generated tokens.
  input
}
```

### Strategy
<a id="markdown-strategy" name="strategy"></a>

The rough idea is that we will have to parse "things" into this `proc_macro2::TokenStream` in order
to manipulate them. They can be parsed into this AST from:

1. [Strings](https://docs.rs/syn/latest/syn/parse/index.html#the-synparse-functions),
2. Input to a derive macro,
3. Input to an attribute macro,
4. Input to a function like macro,
5. And even other ASTs generated by `quote!()` using
   [`parse_quote!()`](https://docs.rs/syn/latest/syn/macro.parse_quote.html).

In order to do this parsing you have to use the
[`syn::parse*` functions](https://docs.rs/syn/latest/syn/parse/index.html#the-synparse-functions).

- When using any of them (macro form or otherwise) you have to provide the type that you want the
  `TokenStream` to be parsed **into**.
- You have to supply the type that you want the `TokenStream` to be parsed **as**. So if you have a
  function then you want to tell syn to parse it `as ItemFn`. Here's an example:
  `let fun:ItemFn = parse_macro_input!(input as ItemFn)`. This will parse the `input` variable into
  an `ItemFn` AST and then you can work w/ the fields provided by `ItemFn` after that.

### Examples
<a id="markdown-examples" name="examples"></a>

So here are some examples of what this looks like.

1. This is how you parse a `TokenStream` into a `DeriveInput` using the `parse_macro_input!()`
   function (eg: in a derive macro):

   ```rust
   pub fn derive_proc_macro_impl(input: TokenStream) -> TokenStream {
     let DeriveInput {
       ident: struct_name_ident,
       data,
       generics,
       ..
     } = parse_macro_input!(input as DeriveInput); // Same as: syn::parse(input).unwrap();
     ...
   }
   ```

2. This is how you parse a string into a `proc_macro2::TokenStream` using the `parse_str()`
   function. Note that we have to provide the type that we want the `String` to be parsed **into**
   via the turbofish syntax, in this case `syn::Type`.

   ```rust
   let traits: Vec<&str> = vec!["std::default::Default", "std::fmt::Debug"];
   syn::parse_str::<syn::Type>(&traits.join(" + ")).unwrap();
   ```

3. It is possible to provide your own implementation of the `Parse` trait and hand it to syn to
   extract the AST you want out of the input `TokenStream`. The syn docs have an example of this
   [here](https://docs.rs/syn/latest/syn/parse/index.html#example). There's also a
   [`Parser` trait](https://docs.rs/syn/latest/syn/parse/index.html#the-parser-trait) that you can
   implement which allows you greater control over the parsing process.

### Writing your own Parse trait impl in different ways
<a id="markdown-writing-your-own-parse-trait-impl-in-different-ways" name="writing-your-own-parse-trait-impl-in-different-ways"></a>

This might not be intuitive, but you can parse the **same** `TokenStream` using various different
parsers. You can parse a `TokenStream` as a `Type` or `Ident` or whatever else depending on what you
need.

Try different traits until you get the one that gets you the AST you want. You can also write
[your own parser](https://docs.rs/syn/latest/syn/parse/index.html#example).

Let's illustrate this with an example. Let's say you want to provide a function like macro w/ the
following syntax: `fn_macro_custom_syntax! { ThingManager<T> for Vec<T> }`. You can write your own
`Parse` trait implementation and extract the AST from the `TokenStream` and you can write this
parser in many many different ways.

Here's one example.

```rust
struct ManagerOfThingInfo {
  manager_ident: Ident,
  manager_generics_ident: Ident,
  thing_type: Type,
}

/// [Parse docs](https://docs.rs/syn/latest/syn/parse/index.html)
impl Parse for ManagerOfThingInfo {
  fn parse(input: ParseStream) -> Result<Self> {
    let manager_ident: Ident = input.parse()?;
    if input.peek(Token![<]) {
      input.parse::<Token![<]>()?;
    }
    let manager_generics_ident: Ident = input.parse()?;
    if input.peek(Token![>]) {
      input.parse::<Token![>]>()?;
    }
    input.parse::<Token![for]>()?;
    let thing_type: Type = input.parse()?;
    Ok(ManagerOfThingInfo {
      manager_ident,
      manager_generics_ident,
      thing_type,
    })
  }
}
```

And here's another way of doing it.

```rust
struct ManagerOfThingInfo {
  manager_name_ident: Ident,
  manager_ty: Type,
  thing_ty: Type,
}

/// [Parse docs](https://docs.rs/syn/latest/syn/parse/index.html)
impl Parse for ManagerOfThingInfo {
  fn parse(input: ParseStream) -> Result<Self> {
    let manager_ty: Type = input.parse()?;
    input.parse::<Token![for]>()?;
    let thing_ty: Type = input.parse()?;

    let manager_name_ident = match manager_ty {
      Type::Path(ref type_path) => {
        let path = &type_path.path;
        let ident = &path
          .segments
          .first()
          .unwrap()
          .ident;
        ident.clone()
      }
      _ => panic!("Expected Type::Path::TypePath.segments to have an Ident"),
    };

    Ok(ManagerOfThingInfo {
      manager_name_ident,
      manager_ty,
      thing_ty,
    })
  }
}
```

> 📜 You can find all the syn examples in this
> [repo](https://github.com/dtolnay/syn/tree/master/examples).

> 📜 You can find the solution to the proc macro workshop
> [here](https://github.com/jonhoo/proc-macro-workshop).

> 📜 This [tutorial](https://ferrous-systems.com/blog/testing-proc-macros/) from the rust-analyzer
> team is also quite helpful.

## Eg 1 - Function-like macro that dumps the AST
<a id="markdown-eg-1---function-like-macro-that-dumps-the-ast" name="eg-1---function-like-macro-that-dumps-the-ast"></a>

Let's start our procedural macro journey w/ something very simple. It's a macro that doesn't really
emit any token stream. It just prints out the AST of the input as debug. So we won't be using
`quote!()` but we will be using syn.

We will start by turning this one line function that's represented by this string literal.

```rust
let output_token_stream_str = "fn foo() -> u32 { 42 }";
```

The first thing we must do is define the macro in the `lib.rs` file.

```rust
extern crate proc_macro;
use proc_macro::TokenStream;

mod ast_viz_debug;

#[proc_macro]
pub fn fn_macro_ast_viz_debug(input: TokenStream) -> TokenStream {
  ast_viz_debug::fn_proc_macro_impl(input)
}
```

Let's write the `ast_viz_debug.rs` file next.

```rust
/// https://docs.rs/syn/latest/syn/macro.parse_macro_input.html
pub fn fn_proc_macro_impl(_input: TokenStream) -> TokenStream {
  let output_token_stream_str = "fn foo() -> u32 { 42 }";
  let output = output_token_stream_str.parse().unwrap();

  let ast_item_fn: ItemFn = parse_str::<ItemFn>(output_token_stream_str).unwrap();
  viz_ast(ast_item_fn);

  output
}
```

Here's the function `viz_ast` that we'll use to print out the AST.

```rust
fn viz_ast(ast: ItemFn) {
  // Simply dump the AST to the console.
  let ast_clone = ast.clone();
  eprintln!("{} => {}", style_primary("Debug::ast"), ast_clone);

  // Parse AST to dump some items to the console.
  let ItemFn {
    attrs,
    vis,
    sig,
    block,
  } = ast;

  eprintln!(
    "{} ast_item_fn < attrs.len:{}, vis:{}, sig:'{}' stmt: '{}' >",
    style_primary("=>"),
    style_prompt(&attrs.len().to_string()),
    style_prompt(match vis {
      syn::Visibility::Public(_) => "public",
      syn::Visibility::Crate(_) => "crate",
      syn::Visibility::Restricted(_) => "restricted",
      syn::Visibility::Inherited => "inherited",
    }),
    style_prompt(&sig.ident.to_string()),
    style_prompt(&match block.stmts.first() {
      Some(stmt) => {
        let expr_str = stmt.to_token_stream().to_string().clone();
        expr_str
      }
      None => "empty".to_string(),
    }),
  );
}
```

> ⚡ To learn more about syn APIs, check out the following links:
>
> - <https://docs.rs/syn/latest/syn/fn.parse_str.html>
> - <https://docs.rs/syn/latest/syn/struct.ItemFn.html>
> - <https://docs.rs/syn/latest/syn/struct.Attribute.html>
> - <https://docs.rs/syn/latest/syn/enum.Visibility.html>
> - <https://docs.rs/syn/latest/syn/struct.Signature.html>
> - <https://docs.rs/syn/latest/syn/struct.Block.html>
> - <https://docs.rs/syn/latest/syn/enum.Stmt.html>
> - <https://github.com/dtolnay/proc-macro-workshop#debugging-tips>

To test this function we can write the following test.

```rust
use my_proc_macros_lib::fn_macro_ast_viz_debug;

#[test]
fn test_proc_macro() {
  fn_macro_ast_viz_debug!();
  assert_eq!(foo(), 42);
}
```

- We can watch this test run using this script:
  `./cargo-watch-one-test.fish test_fn_macro_ast_viz_debug`
- We can watch the macros generated by this test expanded using this script:
  `./cargo-watch-macro-expand-one-test.fish test_fn_macro_ast_viz_debug`

> 📜 You can find another example of a function like procedural macro from the syn docs called
> [`lazy-static`](https://github.com/dtolnay/syn/tree/master/examples/lazy-static). It shows how to
> parse a custom syntax.

## Eg 2 - Function-like macro that parses custom syntax
<a id="markdown-eg-2---function-like-macro-that-parses-custom-syntax" name="eg-2---function-like-macro-that-parses-custom-syntax"></a>

There are times when you need to create your own syntax or domain specific language. Examples of
this are JSX for React. Or DAO generators for a database. In these cases, it's not just about
outputting a token stream, but a large chunk of the work is coming up w/ a syntax that then has to
be parsed 🎉!

The idea is that your users will declaratively define the things that you want to happen, and the
procedural macro will do the rest.

- Declarative or the folks who are using the macros.
- For the implementors, it ends up generating imperative code.

> 📦 To see a real world example of a custom syntax parser, please check out
> [`manager_of_things.rs`](https://github.com/r3bl-org/r3bl-rs-utils/blob/main/my_proc_macros_lib/src/manager_of_things.rs).
>
> - This is part of the [`r3bl_rs_utils`](https://crates.io/crates/r3bl_rs_utils) crate.
> - You can also look at the
>   [tests](https://github.com/r3bl-org/r3bl-rs-utils/blob/main/tests/test_manager_of_things_macro.rs)
>   to see how this macro is used.
> - You can create your own custom keywords using syn via the
>   [`syn::custom_keyword!()`](https://docs.rs/syn/latest/syn/macro.custom_keyword.html) macro.
> - The code that's generated also uses [async traits](https://github.com/dtolnay/async-trait) which
>   are interesting.

> 📜 Take a look at the syn example called
> [`lazy-static`](https://github.com/dtolnay/syn/tree/master/examples/lazy-static) to get some more
> ideas on custom syntax parsing and creating custom error messages for the compiler.

### Desired syntax and behavior
<a id="markdown-desired-syntax-and-behavior" name="desired-syntax-and-behavior"></a>

Let's say that we want to parse a custom syntax like the following, which basically is a declaration
of how a manager for the struct `HashMap<K, V>` should be created.

```rust
fn_macro_custom_syntax! {
  ThingManager<K, V>
  where K: Send + Sync + Default + 'static, V: Send + Sync + Default + 'static
  for std::collections::HashMap<K, V>
}
```

1. `ThingManager` is just the name of the `struct` that should be generated by the macro.
2. `<K, V>` these are optional generic types.
3. The `where` clause is optional. If this is missing and optional generic types are provided above,
   then a default `where` clause will be generated.
4. Finally, the `for` clause allows you to specify the type that the generated manager will be
   managing.

So we want the declaration shown above to emit the following code.

```rust
/// Generated manager ThingManager.
struct ThingManager<K, V>
where
    K: Send + Sync + Default + 'static,
    V: Send + Sync + Default + 'static,
{
    wrapped_thing: std::collections::HashMap<K, V>,
}
```

Let's say that we want some more flexibility in our syntax and will allow the omission of the
`where` clause and we will generate it ourselves, based on the generic type arguments that are
passed to `ThingManager`, in other words `<K, V>`. So the syntax will now look like this.

```rust
fn_macro_custom_syntax! {
  ThingManager<K, V>

for std::collections::HashMap<K, V>
}
```

And we want to generate the following code. Notice that the `where` clause is generated
auto-magically 🪄.

```rust
/// Generated manager ThingManager.
struct ThingManager<K, V>
where
    K: Send + Sync + 'static,
    V: Send + Sync + 'static,
{
    wrapped_thing: std::collections::HashMap<K, V>,
}
```

### Implementing the syntax parser
<a id="markdown-implementing-the-syntax-parser" name="implementing-the-syntax-parser"></a>

So how would we implement this macro? The first thing is to create a custom parser for the syntax.
There are 2 main things we have to do:

1. Create a `struct` that holds all the pertinent information from parsing our syntax, which will
   need to generate the actual code.
2. Create a `Parse` trait implementation for this `struct` that will take care of parsing all the
   tokens that are provided in the `ParseStream`.

Here's the code that does these things. One thing to note is that the `where` clause is optional. If
one isn't provided, then one will be generated automatically for each of the generic types that are
provided to `ThingManager`. This is assuming generic type arguments are passed in with
`ThingManager`. If they aren't then no `where` clause will be generated.

````rust
/// Example of syntax to parse:
/// ```no_run
/// fn_macro_custom_syntax! {
///   ╭─L1──────────────────────────────────────────
///   │     manager_ty
///   │     ▾▾▾▾▾▾▾▾▾▾▾▾▾▾▾▾▾▾
///   named ThingManager<K, V>
///   │     ▴▴▴▴▴▴▴▴▴▴▴▴ ▴▴▴▴
///   │     │            manager_ty_generic_args
///   │     manager_name_ident
///   ╰─────────────────────────────────────────────
///   ╭─L2?─────────────────────────────────────────
///   where K: Send + Sync + 'static, V: Send + Sync + 'static
///   │     ▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴
///   │     where_clause
///   ╰─────────────────────────────────────────────
///   ╭─L3──────────────────────────────────────────
///   of_type std::collections::HashMap<K, V>
///   │       ▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴▴
///   │       thing_ty
///   ╰─────────────────────────────────────────────
/// }
#[derive(Debug)]
struct ManagerOfThingInfo {
  manager_name_ident: Ident,
  manager_ty: Type,
  manager_ty_generic_args: Option<Punctuated<GenericArgument, Comma>>,
  where_clause: Option<WhereClause>,
  thing_ty: Type,
}

/// [Parse docs](https://docs.rs/syn/latest/syn/parse/index.html)
impl Parse for ManagerOfThingInfo {
  fn parse(input: ParseStream) -> Result<Self> {
    // 👀 Manager Type, eg: `ThingManager<K,V>`.
    let manager_ty: Type = input.parse()?;
    let manager_ty_generic_args = match manager_ty.has_angle_bracketed_generic_args() {
      true => Some(
        manager_ty
          .get_angle_bracketed_generic_args_result()
          .unwrap(),
      ),
      false => None,
    };

    // 👀 Optional where clause,
    // eg: `where K: Send+Sync+'static, V: Send+Sync+'static`.
    let mut where_clause: Option<WhereClause> = None;
    if input.peek(Token![where]) {
      where_clause = Some(input.parse::<WhereClause>()?);
    } else {
      if manager_ty.has_angle_bracketed_generic_args() {
        let ident_vec = manager_ty
          .get_angle_bracketed_generic_args_idents_result()
          .unwrap();
        let my_ts = quote! {
          where #(#ident_vec: Send + Sync + 'static),*
        }
        .into();
        let my_where_clause: WhereClause = syn::parse(my_ts).unwrap();
        where_clause = Some(my_where_clause)
      }
    }

    // 👀 for keyword.
    input.parse::<Token![for]>()?;

    // 👀 Thing Type, eg: `std::collections::HashMap<K, V>`.
    let thing_ty: Type = input.parse()?;

    let manager_name_ident = if manager_ty.has_ident() {
      manager_ty.get_ident().unwrap()
    } else {
      panic!("Expected Type::Path::TypePath.segments to have an Ident")
    };

    Ok(ManagerOfThingInfo {
      manager_ty_generic_args,
      manager_name_ident,
      manager_ty,
      thing_ty,
      where_clause,
    })
  }
}
````

### Implementing the code generator
<a id="markdown-implementing-the-code-generator" name="implementing-the-code-generator"></a>

In this example almost all the work goes into parsing the custom syntax. The code generator we are
going to implement is trivial. Here's what it looks like.

```rust
pub fn fn_proc_macro_impl(input: TokenStream) ->:TokenStream {
  let manager_of_thing_info =
    parse_macro_input!(input as ManagerOfThingInfo);

  let ManagerOfThingInfo {
    manager_name_ident,
    manager_ty,
    thing_ty,
    manager_ty_generic_args,
    where_clause,
  } = manager_of_thing_info;

  let doc_struct_str = format!(
    " Generated manager {}.",
    &manager_name_ident,
  );

  quote! {
    #[doc = #doc_struct_str]
    struct #manager_ty #where_clause {
      wrapped_thing: #thing_ty
    }
  }
  .into()
}
```

> 📜 You can find the source code for this example
> [here](https://github.com/nazmulidris/rust_scratch/blob/main/macros/my_proc_macros_lib/src/custom_syntax.rs)
> in its repo.

- We can watch macro expansion by running this script:
  `./cargo-watch-macro-expand-one-test.fish test_fn_macro_custom_syntax`
- We can watch test output by running this script:
  `./cargo-watch-one-test.fish test_fn_macro_custom_syntax`

## Eg 3 - Derive macro that adds a method to a struct
<a id="markdown-eg-3---derive-macro-that-adds-a-method-to-a-struct" name="eg-3---derive-macro-that-adds-a-method-to-a-struct"></a>

We are going to come up w/ a made-up derive macro called `Describe` just for our pedagogical
purposes.

1. This derive macro will add a method to an annotated struct, enum, or union called `Describe`
   which simply returns a `String` that contains the names of the fields in the struct.
2. We will then extend this derive macro to handle generics.

### Test for expected output
<a id="markdown-test-for-expected-output" name="test-for-expected-output"></a>

Here are some simple cases that we should be able to handle in our initial implementation.

```rust
use my_proc_macros_lib::Describe;

#[test]
fn test_proc_macro() {
  #[derive(Describe)]
  struct MyStruct {
    my_string: String,
    my_enum: MyEnum,
    my_number: i32,
  }

  #[derive(Describe)]
  enum MyEnum {
    MyVariant1,
  }

  let foo = MyStruct {
    my_string: "Hello".to_string(),
    my_enum: MyEnum::MyVariant1,
    my_number: 42,
  };
  let foo = foo.describe();
  assert_eq!(
    foo,
    "MyStruct is a struct with these named fields: my_string, my_enum, my_number"
  );
}s
```

> ⚡ To run this test from the
> [repo](https://github.com/nazmulidris/rust_scratch/blob/main/macros/tests/test_derive_macro_describe.rs),
> in watch mode you can execute the following script:
> `./cargo-watch-one-test.fish test_derive_macro_describe`.

### Watch macro expansion
<a id="markdown-watch-macro-expansion" name="watch-macro-expansion"></a>

As we are developing this macro it is really useful not only to have the tests running (in watch
mode) but also have the macro expansion running in watch mode.

> ⚡ To run the macro expansion related to this test from the
> [repo](https://github.com/nazmulidris/rust_scratch/blob/main/macros/tests/test_derive_macro_describe.rs),
> in watch mode you can execute the following script:
> `./cargo-watch-macro-expand-one-test.fish test_derive_macro_describe`.

### Naive implementation
<a id="markdown-naive-implementation" name="naive-implementation"></a>

Let's implement this derive macro in a naive way. We won't handle generics, that will happen
[later](#better-implementation-that-handles-generics).

We have to define a function in `lib.rs` which will use the function that we will write here.

```rust
extern crate proc_macro;
use proc_macro::TokenStream;

mod describe;

#[proc_macro_derive(Describe)]
pub fn derive_macro_describe(input: TokenStream) -> TokenStream {
  describe::derive_proc_macro_impl(input)
}
```

Now to create the `describe.rs` file which will have the `derive_proc_macro_impl` function. This
macro has to to be able to do the following things:

- For a `struct` or `enum` annotated with `#[derive(Describe)]` it will generate a method called
  `describe` which will return a `String` containing the names of the fields (named and unnamed) in
  the struct or enum.
- For a `union` annotated with `#[derive(Describe)]` it will generate a method called `describe`
  which will return a `String` containing the names of all the named fields in the union.

Here's what we have so far.

```rust
pub fn derive_proc_macro_impl(input: TokenStream) -> TokenStream {
  let DeriveInput {
    ident,
    data,
    ..
  } = parse_macro_input!(input as DeriveInput);

  let description_str = match data {
    Struct(my_struct) => gen_description_str_for_struct(my_struct),
    Enum(my_enum) => gen_description_str_for_enum(my_enum),
    Union(my_union) => gen_description_str_for_union(my_union),
  };

  quote! { /* todo */ }
}
```

Here's what the implementation of the `gen_description_str_for_struct` function looks like.

```rust
fn gen_description_str_for_struct(my_struct: DataStruct) -> String {
  match my_struct.fields {
    Named(fields) => handle_named_fields(fields),
    Unnamed(fields) => handle_unnamed_fields(fields),
    Unit => handle_unit(),
  }
}

fn handle_named_fields(fields: FieldsNamed) -> String {
  let my_named_field_idents = fields.named.iter().map(|it| &it.ident);
  format!(
    "a struct with these named fields: {}",
    quote! {#(#my_named_field_idents), *}
  )
}

fn handle_unnamed_fields(fields: FieldsUnnamed) -> String {
  let my_unnamed_fields_count = fields.unnamed.iter().count();
  format!("a struct with {} unnamed fields", my_unnamed_fields_count)
}

fn handle_unit() -> String {
  format!("a unit struct")
}
```

And finally, here are the remainder of the functions.

```rust
fn gen_description_str_for_enum(my_enum: DataEnum) -> String {
  let my_variant_idents = my_enum.variants.iter().map(|it| &it.ident);
  format!(
    "an enum with these variants: {}",
    quote! {#(#my_variant_idents),*}
  )

fn gen_description_str_for_union(my_union: DataUnion) -> String {
  handle_named_fields(my_union.fields)
}
```

We actually haven't generated a token stream yet. We will do that in the next step using `quote!`
macro.

```rust
quote! {
  impl #generics #ident #generics #where_clause {
    fn describe(&self) -> String {
      let mut string = String::from(stringify!(#ident));
      string.push_str(" is ");
      string.push_str(#description_str);
      string
    }
  }
}
.into()
```

The `quote!` macro is incredibly powerful and it has a lot of smarts built into it which we will see
when we implement generics support next.

### Better implementation that handles generics
<a id="markdown-better-implementation-that-handles-generics" name="better-implementation-that-handles-generics"></a>

Here's an example of what a simple `Generics` object looks like when generated from
`struct Point<T> { ... }`.

1. The `Generics.params[0]` is a `TypeParam`, which is our `T`.
2. It contains a an `ident` which is the `T` identifier in our `struct Point<T> { ... }`.

```rust
Generics {
    lt_token: Some(
        Lt,
    ),
    params: [
        Type(
            TypeParam {
                attrs: [],
                ident: Ident {
                    ident: "T",
                    span: #0 bytes(706..707),
                },
                colon_token: None,
                bounds: [],
                eq_token: None,
                default: None,
            },
        ),
    ],
    gt_token: Some(
        Gt,
    ),
    where_clause: None,
}
```

Here's a function that we can use to parse this `Generics` object.

```rust
fn parse_generics(generics: &Generics) -> Option<Ident> {
  if let Some(generic_param) = generics.params.first() {
    // https://docs.rs/syn/latest/syn/enum.GenericParam.html
    match generic_param {
      syn::GenericParam::Type(ref param) => Some(param.ident.clone()),
      syn::GenericParam::Lifetime(_) => unimplemented!(),
      syn::GenericParam::Const(_) => unimplemented!(),
    }
  } else {
    None
  }
}
```

And then we could use this in our procedural macro, like so:

```rust
let parsed_generics = parse_generics(&generics);
match parsed_generics {
  Some(ref _generic_ident) => {
    quote! {
      impl <#parsed_generics> #ident <#parsed_generics> {
        fn describe(&self) -> String {
          let mut string = String::from(stringify!(#ident));
          string.push_str(" is ");
          string.push_str(#description);
          string
        }
      }
    }
    .into() // Convert from proc_macro2::TokenStream to TokenStream.
  }
  None => {
    quote! {
      impl #ident  {
        fn describe(&self) -> String {
          let mut string = String::from(stringify!(#ident));
          string.push_str(" is ");
          string.push_str(#description);
          string
        }
      }
    }
    .into() // Convert from proc_macro2::TokenStream to TokenStream.
  }
}
```

This might provide some insight into how the `Generics` object itself is structured, but there is no
need to do any of this, since `quote!()` is awesome 🤯.

### Using quote!
<a id="markdown-using-quote!" name="using-quote!"></a>

Here's a mental model for using `quote!()`:

1. If you don't include the "thing" that you want to see in generated code, then it will be left
   out.
2. Conversely, if you want to see it in the generated code, then include it explicitly!

So, to handle generics, where you can have multiple types and where clauses, here's the simple code
🎉.

```rust
pub fn derive_proc_macro_impl(input: TokenStream) -> TokenStream {
  let DeriveInput {
    ident,
    data,
    generics,
    ..
  } = parse_macro_input!(input as DeriveInput);

  let where_clause = &generics.where_clause;

  let description_str = match data {
    Struct(my_struct) => gen_description_str_for_struct(my_struct),
    Enum(my_enum) => gen_description_str_for_enum(my_enum),
    Union(my_union) => gen_description_str_for_union(my_union),
  };

  quote! {
    impl #generics #ident #generics #where_clause {
      fn describe(&self) -> String {
        let mut string = String::from(stringify!(#ident));
        string.push_str(" is ");
        string.push_str(#description_str);
        string
      }
    }
  }
  .into()
}
```

> 📜 Here's the source code for `describe.rs` from its
> [repo](https://github.com/nazmulidris/rust_scratch/blob/main/macros/my_proc_macros_lib/src/describe.rs).

Here are some tips and tricks for using `quote!()`:

1. Sometimes it is easier to start w/ a `String` or `Vec<String>` (which you can `join()` into a
   `String`), then parse that into a `TokenStream` using `syn::parse_str()`. Then pass that to
   `quote!()`. And example is if you wanted to add an arbitrary number of trait bounds to an
   existing `where` clause. It is just easier to manipulate the new trait bounds as a `String`,
   parse it into a `TokenStream`, and then use `quote!()` to add that to the existing `where`
   clause. Here's an example from
   [`builder.rs`](https://github.com/nazmulidris/rust_scratch/blob/main/macros/my_proc_macros_lib/src/builder.rs#L169).

   ```rust
   let traits: Vec<&str> = vec!["std::default::Default", "std::fmt::Debug"];
   syn::parse_str::<syn::Type>(&traits.join(" + ")).unwrap();
   ```

2. You can also use [`syn::parse_quote!()`](https://docs.rs/syn/latest/syn/macro.parse_quote.html)
   to get a `TokenStream` from a `quote!()` expression, if it is just easier to generate a
   `quote!()` expression instead of using `String`, etc.
3. Repeating patterns in `quote!()` can be tricky to reason about. The best way to get a feel for
   how it works is to try various things and as soon as you run into some road blocks, think about
   generating `TokenStream`s manually, and then passing them to `quote!()`.

## Eg 4 - Derive macro that generates a builder
<a id="markdown-eg-4---derive-macro-that-generates-a-builder" name="eg-4---derive-macro-that-generates-a-builder"></a>

Now that we have seen a relatively simple derive procedural macro, let's look at a more complex one
that implements the builder pattern and supports generics. There are two things this macro has to
do:

1. Generate the `<Foo>Builder` struct that simply copies all the fields of the annotated struct.
2. Generate the impl block for the `<Foo>Builder` struct. It needs the following:
   1. Setter methods for each named field of the `<Foo>` struct.
   2. A `new()` method that returns a `<Foo>Builder` struct.
   3. A `build()` method that returns a `<Foo>` struct.

> 📜 You can get the source code for this example from its repo
> [here](https://github.com/nazmulidris/rust_scratch/blob/main/macros/my_proc_macros_lib/src/builder.rs).
> And you can get the source for the test
> [here](https://github.com/nazmulidris/rust_scratch/blob/main/macros/tests/test_derive_macro_builder.rs).

### Stub out the implementation
<a id="markdown-stub-out-the-implementation" name="stub-out-the-implementation"></a>

We need to make an entry in `lib.rs` for it, like so:

```rust
#[proc_macro_derive(Builder)]
pub fn
derive_macro_builder(input: TokenStream) -> TokenStream {
  builder::derive_proc_macro_impl(input)
}
```

Then we need to make a `builder.rs` file which contains the implementation of the derive macro.

```rust
pub fn derive_proc_macro_impl(input: proc_macro::TokenStream) -> proc_macro::TokenStream {
  let DeriveInput {
    ident: struct_name_ident,
    data,
    generics,
    ..
  }: DeriveInput = parse_macro_input!(input as DeriveInput);

  let required_trait_bounds: Vec<&str> = vec!["std::default::Default", "std::fmt::Debug"];

  // Only generate code for struct.
  if data.is_struct() {
    with_data_struct_make_ts(&data, &|data_struct| {
      let builder_name_ident = struct_name_ident.from_string("{}Builder");

      let gen_props_setter_fns_ts =
        transform_named_fields_into_setter_fns_ts(data_struct);

      let gen_props_ts = transform_named_fields_to_props_ts(data_struct);

      let doc_struct_str = format!(
        " Implements the [builder pattern] for [`{}`].\n [builder pattern]: {}",
        &struct_name_ident, BUILDER_DOC_URL
      );

      let gen_props_with_defaults_ts =
        transform_named_fields_to_props_with_defaults_ts(data_struct);

      let new_or_modified_where_clause_ts =
        if does_where_clause_exist(&generics.where_clause) {
          add_trait_bounds_to_existing_where_clause_ts(
            &generics.where_clause,
            &required_trait_bounds,
          )
        } else {
          make_new_where_clause_with_default_trait_bounds_for_named_fields(data_struct)
        };

      let build_set_named_fields_ts = build_fn_set_named_fields_ts(data_struct);

      quote! {
        #[doc = #doc_struct_str]
        impl #generics #builder_name_ident #generics #new_or_modified_where_clause_ts {
          pub fn new() -> Self {
            Self {
              #gen_props_with_defaults_ts
            }
          }

          pub fn build(mut self) -> #struct_name_ident #generics {
            #struct_name_ident {
              #build_set_named_fields_ts
            }
          }

          #gen_props_setter_fns_ts
        }

        struct #builder_name_ident #generics #new_or_modified_where_clause_ts {
          #gen_props_ts
        }
      }
    })
  } else {
    quote! {}
  }
  .into()
}
```

### Testing the macro
<a id="markdown-testing-the-macro" name="testing-the-macro"></a>

Here's the test for the derive macro, `test_derive_macro_builder.rs`. They have to cover all the
different kinds of structs that we might encounter, some that have generics, some that don't.

```rust
#[test]
fn test_proc_macro_struct_and_enum() {
  #[derive(Builder)]
  struct MyStruct {
    my_string: String,
    my_enum: MyEnum,
    my_number: i32,
  }

  enum MyEnum {
    MyVariant1,
  }

  impl Default for MyEnum {
    fn default() -> Self { MyEnum::MyVariant1 }
  }
}

#[test]
fn test_proc_macro_no_where_clause() {
  #[derive(Builder)]
  struct Point<X, Y> {
    x: X,
    y: Y,
  }

  let my_pt: Point<i32, i32> = PointBuilder::new()
    .set_x(1 as i32)
    .set_y(2 as i32)
    .build();

  assert_eq!(my_pt.x, 1);
  assert_eq!(my_pt.y, 2);
}

#[test]
fn test_proc_macro_generics() {
  #[derive(Builder)]
  struct Point<X, Y>
  where
    X: std::fmt::Display + Clone,
    Y: std::fmt::Display + Clone,
  {
    x: X,
    y: Y,
  }

  let my_pt: Point<i32, i32> = PointBuilder::new()
    .set_x(1 as i32)
    .set_y(2 as i32)
    .build();

  assert_eq!(my_pt.x, 1);
  assert_eq!(my_pt.y, 2);
}
```

### Implementation details
<a id="markdown-implementation-details" name="implementation-details"></a>

Now that we have the skeleton of the entire thing, let's look at some details of how this is
implemented. It's worth taking a closer look at the
[`utils` module](https://github.com/nazmulidris/rust_scratch/blob/main/macros/my_proc_macros_lib/src/utils/mod.rs#),
since these contain re-usable functions that are leveraged to construct the final macro.

One pattern used here is extending some syn and proc_macro2 types with a new method.

1. The `syn::Data` type is extended w/ a method `is_struct` that can be used to check whether it
   contains a `struct` or not.
2. `proc_macro2::Ident` type is extended w/ a method `from_string` that can be used to create a
   `proc_macro2::Ident` from a string.

And there are some nice functions in `syn_parser_helpers.rs` that make it easier for us to create
lambdas that operate on named fields in the struct. We can use these to easily create a
`proc_macro2::TokenStream` that will do various things like:

1. Create a props for the `<Foo>Builder` `struct`.
2. Generate setter functions for the impl block of the `<Foo>Builder` `struct`.
3. Generate `where` clauses that add trait bounds to the existing or new `where` clause.

Please review the sources in detail to get a better understanding of how this is implemented. One of
the interesting things that this builder macro does is that it adds trait bounds to the existing
`where` clause. This is done to make sure that the `<Foo>Builder` `struct` implements the `Default`
trait for the `Foo` struct. It also adds a trait bound for `Debug`. Here's a snippet of that.

> 🔮 There is no need to handle properties or fields that have `Option` type. Creating the
> requirement that the `<Foo>Builder` `struct` implements `Default` for the `Foo` struct ensures
> that if a field has an `Option<T>` type, then the default will be `None`. In other words, if you
> don't specify a value for an `Option<T>` field type then the default will be `None`!.

```rust
let required_trait_bounds: Vec<&str> = vec!["std::default::Default", "std::fmt::Debug"];

fn add_trait_bounds_to_existing_where_clause_ts(
  where_clause: &Option<syn::WhereClause>,
  traits: &Vec<&str>,
) -> proc_macro2::TokenStream {
  // Must parse the `traits.join("+")` string into a [syn::Type].
  let joined_traits: syn::Type =
    syn::parse_str::<syn::Type>(&traits.join(" + ")).unwrap();

  let where_clause_ts = match where_clause {
    Some(where_clause) => {
      let where_predicate_punctuated_list = &where_clause.predicates;

      let modified_where_predicates_ts = where_predicate_punctuated_list
        .iter()
        .map(
          |where_predicate| match where_predicate {
            syn::WherePredicate::Type(_) => {
              quote! { #where_predicate + #joined_traits }
            }
            _ => quote! {},
          },
        )
        .collect::<Vec<_>>();

      quote! { where #(#modified_where_predicates_ts),* }
    }
    None => {
      quote! {}
    }
  };

  return where_clause_ts;
}
```

> 👀 Here are the scripts you can run to watch the macro expansion and test results as you make
> changes.
>
> - We can watch this test run using this script:
>   `./cargo-watch-one-test.fish test_derive_macro_builder`
> - We can watch the macros generated by this test expanded using this script:
>   `./cargo-watch-macro-expand-one-test.fish test_derive_macro_builder`

## Eg 5 - Attribute macro that adds logging to a function
<a id="markdown-eg-5---attribute-macro-that-adds-logging-to-a-function" name="eg-5---attribute-macro-that-adds-logging-to-a-function"></a>

[Attribute procedural macros](https://doc.rust-lang.org/reference/procedural-macros.html#attribute-macros)
are very similar to derive procedural macros, with a few key differences.

1. Instead of just `enum` and `struct` an attribute procedural macro can be used to annotate any
   [`Item`](https://doc.rust-lang.org/reference/items.html). For example, functions, traits, impl
   blocks, etc.
2. Unlike a derive macro, attribute macros will replace the entire item that is annotated. Derive
   macros can only add code below the annotated `struct` or `enum`.
3. There's an extra input argument that attribute macros get passed which holds the arguments used
   to annotate the item. This is optional. These attributes can take 3 forms as defined in the
   `syn::Meta` enum, which can be matched as follows:
   1. `Path(path)` -> `path: syn::Path` is a meta path is like the `test` in `#[test]`.
   2. `List(meta_list)` -> `meta_list: syn::MetaList` is a structured list within an attribute, like
      `derive(Copy, Clone)`.
   3. `NameValue(meta_name_value)` -> `meta_name_value: syn::MetaNameValue` is name-value pair
      within an attribute, like `feature = "nightly"`.

We aren't sure yet what the attributes for this macro might look like. Here are two variants that we
might try out. So let's just make 2 macros.

1. Variant 1 - passing an argument that looks like a key value pair to the macro. This is the
   `NameValue` variant of the `syn::Meta` enum.

   ```rust
   #[attrib_macro_logger_1(key = "value")]
   pub fn some_annotated_function() {
       /* ... */
   }
   ```

2. Variant 2 - passing an argument that looks like a list of identifiers to the macro. This is not
   any of the variants of `syn::Meta` enum and is a something custom. However it is very similar to
   the `List` variant of `syn::Meta` enum.

   ```rust
   #[attrib_macro_logger_2(a, b, c)]
   pub fn some_annotated_function() {
       /* ... */
   }
   ```

### Create entry in lib.rs
<a id="markdown-create-entry-in-lib.rs" name="create-entry-in-lib.rs"></a>

Let's start by creating an entry in `lib.rs` for these attribute macros.

```rust
#[proc_macro_attribute]
pub fn attrib_macro_logger_1(
  args: TokenStream,
  item: TokenStream,
) -> TokenStream {
  logger::attrib_proc_macro_impl(args, item)
}

#[proc_macro_attribute]
pub fn attrib_macro_logger_2(
  args: TokenStream,
  item: TokenStream,
) -> TokenStream {
  logger::attrib_proc_macro_impl(args, item)
}
```

Now let's write the implementations of the attribute macros, named `logger.rs`. As you can see in
addition to the `item` parameter, we have an extra parameter `args` that holds the arguments that
were passed into this attribute macro.

```rust
use quote::quote;

/// The args take a key value pair like `#[attrib_macro_logger(key = "value")]`.
pub fn attrib_proc_macro_impl_1(
  args: proc_macro::TokenStream,
  item: proc_macro::TokenStream,
) -> proc_macro::TokenStream {
  quote! {}.into()
}

/// The args take a set of identifiers like `#[attrib_macro_logger(a, b, c)]`.
pub fn attrib_proc_macro_impl_2(
  args: proc_macro::TokenStream,
  item: proc_macro::TokenStream,
) -> proc_macro::TokenStream {
  quote! {}.into()
}
```

> 📜 You can get the source code for this example in its repo
> [here](https://github.com/nazmulidris/rust_scratch/blob/main/macros/my_proc_macros_lib/src/logger.rs).
>
> 👀 Watch macro expansion
>
> To watch for changes run this script:
> `./cargo-watch-macro-expand-one-test.fish test_attribute_macro_logger`
>
> 👀 Watch test output
>
> To watch for test output run this script:
> `./cargo-watch-one-test.fish test_attribute_macro_logger`

### How to parse item?
<a id="markdown-how-to-parse-item%3F" name="how-to-parse-item%3F"></a>

How do we parse the `item` parameter? We can use `syn::ItemFn` and `parse_macro_input!()` to parse
it into something usable. Here's an example.

```rust
#[proc_macro_attribute]
pub fn attrib_proc_macro_impl_1(args: TokenStream, item: TokenStream) -> TokenStream {
    let item = parse_macro_input!(item as ItemFn);
    quote! {}.into()
}

#[proc_macro_attribute]
pub fn attrib_proc_macro_impl_2(args: TokenStream, item: TokenStream) -> TokenStream {
    let item = parse_macro_input!(item as ItemFn);
    quote! {}.into()
}
```

### How to parse args containing attributes for variant 1?
<a id="markdown-how-to-parse-args-containing-attributes-for-variant-1%3F" name="how-to-parse-args-containing-attributes-for-variant-1%3F"></a>

How do we parse `args` parameter into something we can use? We can use
[`syn::AttributeArgs`](https://docs.rs/syn/latest/syn/type.AttributeArgs.html) along w/
`parse_macro_input!()` to parse it into something usable.

```rust
#[proc_macro_attribute]
pub fn attrib_proc_macro_impl_1(args: TokenStream, item: TokenStream) -> TokenStream {
  let args = parse_macro_input!(args as AttributeArgs);
  let item = parse_macro_input!(item as ItemFn);
  quote! {}.into()
}
```

Here's a snippet of how we might use this attribute macro.

```rust
#[attrib_macro_logger_1(key = "value")]
pub fn some_annotated_function() {
  /* ... */
}
```

What we really want out of the
[`AttributeArgs`](https://docs.rs/syn/latest/syn/type.AttributeArgs.html) is the key and value pair.
We will write an extension trait to parse the key and value pair. And this is how we can use it.

```rust
pub fn attrib_proc_macro_impl_1(args: TokenStream, item: TokenStream) -> TokenStream {
  let args = parse_macro_input!(args as AttributeArgs);
  // Parse args (which contain key & value).
  let (key, value) = args.get_key_value_pair();
  println!(
    "key: {}, value: {}",
    style_prompt(&key),
    style_prompt(&value),
  );
  ...
}
```

You can get the implementation of the extension traits in the links below.

1. [`AttributeArgsExt`](https://github.com/nazmulidris/rust_scratch/blob/main/macros/my_proc_macros_lib/src/utils/attribute_args_ext.rs)
2. [`MetaExt`](https://github.com/nazmulidris/rust_scratch/blob/main/macros/my_proc_macros_lib/src/utils/meta_ext.rs)
3. [`NestedMetaExt`](https://github.com/nazmulidris/rust_scratch/blob/main/macros/my_proc_macros_lib/src/utils/nested_meta_ext.rs)

These traits are implemented on the types that are provided by syn and all work in a similar
fashion. They all look for specific patterns and panic if they're not found. This is the desired
behavior because we want the compiler to give error messages when the it can't generate code for the
macro.

And finally we have the complete macro.

```rust
pub fn attrib_proc_macro_impl_1(
  args: proc_macro::TokenStream,
  item: proc_macro::TokenStream,
) -> proc_macro::TokenStream {
  let args = parse_macro_input!(args as AttributeArgs);
  let item = parse_macro_input!(item as ItemFn);

  // Parse args (which contain key & value).
  let (key, value) = args.get_key_value_pair();
  println!(
    "key: {}, value: {}",
    style_prompt(&key),
    style_prompt(&value),
  );

  let fn_ident = item.sig.ident.from_string(&key);

  quote! {
    fn #fn_ident() -> &'static str {
      #value
    }
  }
  .into()
}
```

When we use the macro like so:

```rust
#[attrib_macro_logger_1(key = "value")]
fn this_fn_will_be_consumed_and_replaced() -> i32 { 42 }
```

Here's the code that is generated:

```rust
fn key() -> &'static str {
  "value"
}
```

### How to parse args containing set of identifiers for variant 2?
<a id="markdown-how-to-parse-args-containing-set-of-identifiers-for-variant-2%3F" name="how-to-parse-args-containing-set-of-identifiers-for-variant-2%3F"></a>

We can also provide our own custom implementation of the `Parse` trait if we want to. Here's an
example of this based on syn's
[`trace-var`](https://github.com/dtolnay/syn/blob/master/examples/trace-var/trace-var/src/lib.rs)
example.

```rust
use std::collections::HashSet as Set;
use syn::{parse_macro_input, Token, Ident};
use syn::parse::{Parse, ParseStream, Result};

/// Parses a list of variable names separated by `+`.
///
///     a + b + c
///
/// This is how the compiler passes in arguments to our attribute -- it is
/// everything inside the delimiters after the attribute name.
///
///     #[attrib_macro_logger(a+ b+ c)]
///                           ^^^^^^^
struct ArgsHoldingIdents {
  idents: Set<Ident>,
}

impl Parse for ArgsHoldingIdents {
  fn parse(args: ParseStream) -> Result<Self> {
    let vars = Punctuated::<Ident, Token![+]>::parse_terminated(args)?;
    Ok(ArgsHoldingIdents {
      idents: vars.into_iter().collect(),
    })
  }
}
```

1. The `parse()` function receives a `ParseStream` and returns a `Result`. In this case:
   1. `args::ParseStream` is the `TokenStream` of the optional arguments that are passed into the
      attribute macro. In other words `(a+ b+ c)`.
   2. `Result` holds the struct `ArgsHoldingIdents`. In other words a `Set` of `Ident` containing
      `a`, `b`, `c`.
2. The actual work is done by
   [`Punctuated::parse_terminated()`](https://docs.rs/syn/latest/syn/punctuated/struct.Punctuated.html#method.parse_terminated)
   function. There are a few of these helper functions provided by syn.
3. `parse_terminated()` parses a bunch of `T` separated by `P` and it has to be told two things:
   1. _What type `T` it is parsing?_ In this case, `Ident`.
   2. _What the separator `P`?_ In this case,
      [`Token![+]`](https://docs.rs/syn/latest/syn/macro.Token.html) which is the Rust
      representation of the `+` token (provided by the `Token!` macro).
   3. We provide it w/ this information using the turbofish syntax: `::<Ident, Token![+]>::`.
4. Finally after the `ParseStream` is parsed, it returns an iterator, which must be used to generate
   the result. We simply iterate over the iterator and collect the `Ident`s and move them into an
   instance of a new struct `ArgsHoldingIdents` and return that wrapped in a `Result::Ok`.

And we might implement the macro like this:

```rust
/// The args take a set of identifiers like `#[attrib_macro_logger(a, b, c)]`.
pub fn attrib_proc_macro_impl_2(
  args: proc_macro::TokenStream,
  item: proc_macro::TokenStream,
) -> proc_macro::TokenStream {
  let args = parse_macro_input!(args as ArgsHoldingIdents);
  let item = parse_macro_input!(item as ItemFn);

  let fn_name_ident = item.sig.ident;

  let args_to_string = args
    .idents
    .iter()
    .map(|ident| ident.to_string())
    .collect::<Vec<_>>()
    .join(", ");

  quote! {
    pub fn #fn_name_ident() -> &'static str { #args_to_string }
  }
  .into()
}
```

And use it like so:

```rust
#[attrib_macro_logger_2(a + b + c)]
fn foo() -> i32 { 42 }
```

This generates the following code (very minor note - the ordering of the output is actually not
stable):

```rust
pub fn foo() -> &'static str {
  "c, a, b"
}
```

> 📜 You can find another example of a attribute procedural macro from the syn docs called
> [`trace-var`](https://github.com/dtolnay/syn/tree/master/examples/trace-var).

## Learning resources
<a id="markdown-learning-resources" name="learning-resources"></a>

- Overview
  - [Excellent overview video](https://youtu.be/g4SYTOc8fL0)

- Books / articles
  - [Macro how to](https://doc.rust-lang.org/reference/procedural-macros.html#function-like-procedural-macros)
  - [Macro how to](https://doc.rust-lang.org/book/ch19-06-macros.html#procedural-macros-for-generating-code-from-attributes)

- Workshop
  - [Proc macro workshop](https://github.com/dtolnay/proc-macro-workshop/blob/master/README.md)
  - [Proc macro workshop solutions](https://github.com/jonhoo/proc-macro-workshop)

- Technical guides to getting things working
  - [Tutorial - Add lib crate for macros](https://dev.to/dandyvica/rust-procedural-macros-step-by-step-tutorial-36n8)
  - [`lib.rs` restriction](https://users.rust-lang.org/t/how-to-import-procedural-macros-that-is-not-in-lib-rs/58323/9)
  - [Quote](https://docs.rs/quote)
  - [Syn](https://docs.rs/syn)

- Procedural macros workshop
  - [Workshop derive builder problem](https://github.com/dtolnay/proc-macro-workshop/blob/master/README.md#derive-macro-derivebuilder)
  - [Solution hints for builder problem](https://github.com/dtolnay/proc-macro-workshop/blob/master/builder/tests/01-parse.rs)

- Source code examples
  1. You can find "real world" examples of both declarative and procedural macros in the
    `r3bl-open-core` [repo](https://github.com/r3bl-org/r3bl-open-core).
    - [proc macros](https://github.com/r3bl-org/r3bl-open-core/tree/main/macro)
    - [decl macros](https://github.com/r3bl-org/r3bl-open-core/search?q=macro_rules)
  2. You can find all the pedagogical examples of macros shown in this article in this
    [repo](https://github.com/nazmulidris/rust_scratch/blob/main/macros/).

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
