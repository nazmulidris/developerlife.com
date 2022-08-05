---
title: "Create a simple DSL for CSS like syntax for TUIs"
author: Nazmul Idris
date: 2022-08-04 15:00:00+00:00
excerpt: |
  Procedural macros are a way for you to extend the Rust complier and provide plugins
  that you can use to extend the language. They allow to create your own DSL (domain
  specific language). This article goes into the details of creating a simple DSL to 
  mimic CSS syntax but in Rust, for a TUI app framework.
layout: post
categories:
  - Rust
  - MP
  - CLI
  - TUI
---

<img class="post-hero-image" src="{{ 'assets/rust-dsl.svg' | relative_url }}"/>

<!-- TOC -->

- [Create a DSL for CSS like syntax for TUIs](#create-a-dsl-for-css-like-syntax-for-tuis)
  - [What is a style, and how is it used?](#what-is-a-style-and-how-is-it-used)
  - [Life of a style](#life-of-a-style)
  - [Going from imperative to declarative style declaration](#going-from-imperative-to-declarative-style-declaration)
- [What are procedural macros](#what-are-procedural-macros)
- [Define the syntax](#define-the-syntax)
- [Parse the syntax](#parse-the-syntax)
- [Generate the code](#generate-the-code)
- [Putting it together](#putting-it-together)
- [Learning resources](#learning-resources)
- [Wrapping up](#wrapping-up)

<!-- /TOC -->

## Create a DSL for CSS like syntax for TUIs
<a id="markdown-create-a-dsl-for-css-like-syntax-for-tuis" name="create-a-dsl-for-css-like-syntax-for-tuis"></a>


1. TK: provide an intro to what we are going to achieve in this article (simple CSS syntax)
2. TK: provide context (the tui library) for this work (why is it important to build this?)
3. TK: provide some hint about what greater ambitions we have (stylesheet syntax, JSX like syntax)

In this article, we will create a simple DSL
([domain specific language](https://docs.microsoft.com/en-us/visualstudio/modeling/about-domain-specific-languages?view=vs-2022))
for CSS like syntax to declaratively create styling for TUI apps. You might be thinking, but why? 🤔

The motivation for doing this comes from having built a TUI library in the
[`r3bl_rs_utils`](https://crates.io/crates/r3bl_rs_utils/) crate and wanting to make it more
ergonomic for developers, so that it is easier to use and familiar to declarative styling from CSS,
etc.

> 🦜 What is a TUI? The best way to grok it is to see one in action.
>
> 1. Clone [this repo](https://github.com/r3bl-org/r3bl-cmdr) (for the
>    [`r3bl-cmdr` crate](https://crates.io/crates/r3bl-cmdr)) to your local or remote machine.
> 2. Run `cargo run` (in `r3bl-cmdr` folder) to see it doing its thing. Works great over
>    [SSH](https://en.wikipedia.org/wiki/Secure_Shell) too!
> 3. Check out the source code in this repo, to get a handle on how to use the `r3bl_rs_utils::tui`
>    module.

This TUI library allows developers to build "rich" text user interface apps in Rust, which are fully
async, and leverages ideas from CSS, React, and Redux. Once we built the library, we wanted to make
it easier for developer to declaratively create styling and even layouts, rather than having to do
it imperatively.

> 💭 In frontend web development, we take it for granted that we can describe things
> [declaratively rather than imperatively](https://www.educative.io/blog/declarative-vs-imperative-programming).
> Anytime we use CSS, JSX, or HTML we are doing this. We are used to telling the computer **what**
> we would like it to produce, and it figures out **how** to go about making this happen. There are
> similar declarative technologies in desktop and mobile GUI toolkits as well.

### What is a style, and how is it used?
<a id="markdown-what-is-a-style%2C-and-how-is-it-used%3F" name="what-is-a-style%2C-and-how-is-it-used%3F"></a>


What exactly is a style? It is used to format some text that is painted to the terminal. This is
done by specifying the text's color, background color, and other attributes (bold, underline, etc).

In this article, we will create a simple DSL just to describe a single style. But this next section
gives you context around where this style is used in the `r3bl_rs_utils::tui` library.

### Life of a style
<a id="markdown-life-of-a-style" name="life-of-a-style"></a>


As an aside, before getting into making the syntax declarative, let's look at how a style is
actually used in the `r3bl_rs_utils::tui` library. The following is a whirlwind overview of how the
`r3bl_rs_utils::tui` engine itself works. It is not meant to be an in depth examination or
explanation, so hold on for the blast of information that is about to follow 💨.

First we have to make a stylesheet. This is currently done imperatively, but will be converted to
declarative in the near future 😃. More articles about DSLs are on the horizon.

```rust
fn create_stylesheet(&mut self) -> CommonResult<Stylesheet> {
  // Turquoise:  Color::Rgb { r: 51, g: 255, b: 255 }
  // Pink:       Color::Rgb { r: 252, g: 157, b: 248 }
  // Blue:       Color::Rgb { r: 55, g: 55, b: 248 }
  // Faded blue: Color::Rgb { r: 85, g: 85, b: 255 }
  throws_with_return!({
    let mut stylesheet = Stylesheet::new();

    stylesheet.add_styles(vec![
      style! {
        id: style1
        margin: 1
        color_bg: Color::Rgb { r: 55, g: 55, b: 248 }
      },
      style! {
        id: style2
        margin: 1
        color_bg: Color::Rgb { r: 85, g: 85, b: 255 }
      },
    ])?;

    stylesheet
  })
}
```

Then we have to use this style in a few different places. Let's first use in to create a (flexbox
like) layout. This is currently done imperatively. We intend to create a JSX like declarative syntax
for this layout engine in the near future 😃. Even more articles about DSLs are on the horizon.

The following snippet is a layout being created (imperatively right now). And the stylesheet is
attached into the layout engine, which is a thing called `TWSurface` or terminal window surface. It
stores some information about the terminal "window" (like available rows and columns, and it is
manages when window resize events happen, and even manages user input events); it also has the
stylesheet attached to it.

And then `create_main_container()` is called. This seems important too, so let's look at that next.

```rust
let mut tw_surface = TWSurface {
  stylesheet: self.create_stylesheet()?,
  ..TWSurface::default()
};
tw_surface.surface_start(TWSurfaceProps {
  pos: (0, 0).into(),
  size: window_size,
})?;
self
  .create_main_container(&mut tw_surface, state, shared_store)
  .await?;
tw_surface.surface_end()?;
```

You can think of layouts as flexbox containers (or boxes). You first create the surface that holds
all the boxes. This surface takes up the full width and height of the terminal's window.

Then inside of this surface, you can add a "main container" box which takes up the full space of the
terminal window. You can then add two other boxes which will be columns that are 50% width each. And
they will be arranged from left to right (horizontal direction). And then inside of each column box,
you can provide a `Component` to actually paint the content & even handle user input events. All of
this happening asynchronously.

So here's the snippet that creates this "main container" box.

```rust
async fn create_main_container<'a>(
  &mut self, tw_surface: &mut TWSurface, state: &'a AppWithLayoutState,
  shared_store: &'a SharedStore<AppWithLayoutState, AppWithLayoutAction>,
) -> CommonResult<()> {
  throws!({
    tw_surface.box_start(TWBoxProps {
      id: CONTAINER_ID.into(),
      dir: Direction::Horizontal,
      req_size: (100, 100).try_into()?,
      ..Default::default()
    })?;
    self
      .create_left_col(tw_surface, state, shared_store)
      .await?;
    self
      .create_right_col(tw_surface, state, shared_store)
      .await?;
    tw_surface.box_end()?;
  });
}
```

We will just look at one of the columns for now. After all this article is about DSL for style and
not about how to build TUIs. Here's the snippet to create this column, and it does use a style from
the stylesheet that we made earlier.

```rust
async fn create_left_col<'a>(
  &mut self, tw_surface: &mut TWSurface, state: &'a AppWithLayoutState,
  shared_state: &'a SharedStore<AppWithLayoutState, AppWithLayoutAction>,
) -> CommonResult<()> {
  throws!({
    tw_surface.box_start(TWBoxProps {
      styles: tw_surface.stylesheet.find_styles_by_ids(vec!["style1"]),
      id: COL_1_ID.into(),
      dir: Direction::Vertical,
      req_size: (50, 100).try_into()?,
    })?;

    if let Some(shared_component) = self.component_registry.get(COL_1_ID) {
      let current_box = tw_surface.current_box()?;
      let queue = shared_component
        .write()
        .await
        .render(&self.has_focus, current_box, state, shared_state)
        .await?;
      tw_surface.render_buffer += queue;
    }

    tw_surface.box_end()?;
  });
}
```

### Going from imperative to declarative style declaration
<a id="markdown-going-from-imperative-to-declarative-style-declaration" name="going-from-imperative-to-declarative-style-declaration"></a>


Now that we have that context out of the way, let's look at a real example of a single style.

This is how one can imperatively create a style using the
[`r3bl_rs_utils::tui` module](https://docs.rs/r3bl_rs_utils/latest/r3bl_rs_utils/tui/index.html).
Once created in this manner, it can be applied to things.

```rust
use crossterm::style::*;
use r3bl_rs_utils::*;

fn make_a_style_imperatively(id: &str) -> Style {
  let black = Color::Rgb { r: 0, g: 0, b: 0 };
  Style {
    id: id.to_string(),
    dim: true,
    bold: true,
    color_fg: Some(black.into()),
    color_bg: Some(black.into()),
    ..Style::default()
  }
}
```

We would like to express the declaratively, like so.

```rust
use crossterm::style::*;
use r3bl_rs_utils::*;

fn make_a_style_declaratively(id: &str) -> Style {
  style! {
    id: style2
    attrib: [dim, bold]
    margin: 1
    color_fg: Color::Red
    color_bg: Color::Rgb { r: 0, g: 0, b: 0 }
  }
}
```

The rest of this article will be devoted to making this happen using procedural macros (function
like).

## What are procedural macros
<a id="markdown-what-are-procedural-macros" name="what-are-procedural-macros"></a>


For an introduction to procedural macros, please read our article on
[Procedural Macros](https://developerlife.com/2022/03/30/rust-proc-macro/). Here are some snippets
from that article.

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
>   [DSL (domain spe <a id="markdown-define-the-syntax" name="define-the-syntax"></a>cific language)](https://developerlife.com/2020/04/04/kotlin-dsl-intro/)
>   like in Kotlin and babel and JavaScript.

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

## Define the syntax
<a id="markdown-define-the-syntax" name="define-the-syntax"></a>


> 📜 Here's the final version of the procedural macro we are going to write:
> [`make_style()`](https://github.com/r3bl-org/r3bl-rs-utils/blob/main/macro/src/make_style).

The fun part of creating a DSL is coming up w/ whatever syntax you want to allow developers to use.
This is a very liberating, empowering, and creative exercise. You don't have to accept the language
keywords as they are. You are free to make your own! Rust is awesome!

To meet the goal of being an ergonomic API, the `tui` library leverages the mental model that people
already possess coming from web, or Android, etc. of declaratively creating styling. And then
specifying that some component uses that style. We will do the same while taking the unique
constraints of a text user interface (that only renders to the terminal) into account. Fun times!

A style can have the following things, and is intended to style text that is going to be painted to
the terminal.

```rust
style! {
  id:       style2                   // (req) unique id of the style
  attrib:   [dim, bold]              // (opt) array of attributes for styling text
  margin:   1
  color_fg: Color::Red               // (opt) Foreground color (specified via `Color` enum)
  color_bg: Color::Rgb {r:0,g:0,b:0} // (opt) Background color (specified via `Rgb` struct)
}
```

Let's break this down into more specifics, so that we can build parse the syntax next.

1. The `id` is requir <a id="markdown-learning-resources" name="learning-resources"></a>ed. The
   value is going to be turned into a string. So the value is a literal which can be anything that
   can be turned into a string.
2. The `attrib` field is optional. When you do provide a value for it, this looks like an array of
   attributes. Here's the full list of these attributes:
   `dim, bold, <a id="markdown-wrapping-up" name="wrapping-up"></a> underline, reverse, hidden, strikethrough`.
3. The `margin` field is optional. When you do provide a value for it, this looks like an integer.
   The value is the number of spaces to add to the top, down, left, and right of the text.

## Parse the syntax
<a id="markdown-parse-the-syntax" name="parse-the-syntax"></a>


## Generate the code
<a id="markdown-generate-the-code" name="generate-the-code"></a>


## Putting it together
<a id="markdown-putting-it-together" name="putting-it-together"></a>


## Learning resources
<a id="markdown-learning-resources" name="learning-resources"></a>


## Wrapping up
<a id="markdown-wrapping-up" name="wrapping-up"></a>


In the future we will expand this DSL to include more features like generating the entire stylesheet
declaratively. And then move on to creating JSX like syntax in Rust for the TUI library.

> 📜 You can find all the examples of procedural macros shown in this article in the
> `r3bl_rs_utils_macro` [repo](https://github.com/r3bl-org/r3bl_rs_utils/tree/main/macro/). This is
> just part of the `r3bl_rs_utils` [crate](https://crates.io/crates/r3bl_rs_utils).
