---
title: "Create a simple DSL for CSS like syntax for TUIs"
author: Nazmul Idris
date: 2022-08-04 15:00:00+00:00
excerpt: |
  Procedural macros are a way for you to extend the Rust compiler and provide plugins
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
  - [A TUI brings GUI features to terminal apps](#a-tui-brings-gui-features-to-terminal-apps)
  - [What is a style, and how is it used?](#what-is-a-style-and-how-is-it-used)
  - [Life of a style](#life-of-a-style)
  - [Going from imperative to declarative style declaration](#going-from-imperative-to-declarative-style-declaration)
- [What are procedural macros](#what-are-procedural-macros)
- [Define the syntax](#define-the-syntax)
- [Parse the syntax](#parse-the-syntax)
- [Generate the code](#generate-the-code)
- [Exporting it](#exporting-it)
- [Wrapping up](#wrapping-up)
- [Build with Naz video series on developerlife.com YouTube channel](#build-with-naz-video-series-on-developerlifecom-youtube-channel)

<!-- /TOC -->

## Create a DSL for CSS like syntax for TUIs
<a id="markdown-create-a-dsl-for-css-like-syntax-for-tuis" name="create-a-dsl-for-css-like-syntax-for-tuis"></a>

In this article, we will create a simple DSL
([domain specific language](https://docs.microsoft.com/en-us/visualstudio/modeling/about-domain-specific-languages?view=vs-2022))
for CSS like syntax to declaratively create styling for TUI apps. You might be thinking, but why? 🤔

The motivation for doing this comes from having built a TUI library in the
[`r3bl_rs_utils`](https://crates.io/crates/r3bl_rs_utils/) crate and wanting to make it more
ergonomic for developers, so that it is easier to use and familiar to declarative styling from CSS,
etc.

### A TUI brings GUI features to terminal apps
<a id="markdown-a-tui-brings-gui-features-to-terminal-apps" name="a-tui-brings-gui-features-to-terminal-apps"></a>

The best way to grok what a TUI is, is to see one in action.

<img src="https://user-images.githubusercontent.com/2966499/234949476-98ad595a-3b72-497f-8056-84b6acda80e2.gif"/>

1. <kbd>TUI library crate</kbd>: Clone [this TUI library
   repo](https://github.com/r3bl-org/r3bl-open-core/) for the [`r3bl_tui`
   crate](https://crates.io/crates/r3bl_tui) to your local or remote machine. You can run
   the examples in the
   [README](https://github.com/r3bl-org/r3bl-open-core/tree/main/tui#examples-to-get-you-started).
2. <kbd>TUI apps crate</kbd>: Clone [this TUI apps
   repo](https://github.com/r3bl-org/r3bl-open-core) for the [`r3bl-cmdr`
   crate](https://crates.io/crates/r3bl-cmdr) to your local or remote machine. Run `cargo
   run` (in `r3bl-cmdr` folder) to see it doing its thing. Works great over
   [SSH](https://en.wikipedia.org/wiki/Secure_Shell) too! Or you can just run `cargo
   install r3bl-cmdr`. And then run `edi` or `giti`.

The TUI library allows developers to build "rich" text user interface apps in Rust, which
are fully async, and loosely leverages architectural ideas from CSS, React, web app
development paradigm, and Elm. Once we built the library, we wanted to make it easier for
developer to declaratively create styling and even layouts, rather than having to do it
imperatively.

> 💭 In frontend web development, we take it for granted that we can describe things
> [declaratively rather than imperatively](https://www.educative.io/blog/declarative-vs-imperative-programming).
> Anytime we use CSS, JSX, or HTML we are doing this. We are used to telling the computer **what**
> we would like it to produce, and it figures out **how** to go about making this happen. There are
> similar declarative technologies in desktop and mobile GUI toolkits as well.

> For more information on general Rust type system design (functional approach rather than
> object oriented), please take a look at this [paper](https://arxiv.org/pdf/2307.07069.pdf)
> by Will Crichton demonstrating Typed Design Patterns with Rust.

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

First we have to make a stylesheet. This stylesheet holds 2 styles `style1` and `style2`. We will
track `style1`'s journey in this section.

We currently have to make the stylesheet imperatively, but will be converted to declarative in the
near future 😃. More articles about DSLs are on the horizon.

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
attached into the layout engine, which is a `struct` called `TWSurface` or terminal window surface.
It stores some information about the terminal "window" (like available rows and columns, and it is
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

You can think of creating a layout using flexbox containers or boxes (`TWBox`).

1. You first create the surface that holds all the boxes. This surface takes up the full width and
   height of the terminal's window (`TerminalWindow`).
2. Then inside of this surface (`TWSurface`), you can add a "main container" box (`TWBox`) which
   takes up the full space of the terminal window.
3. You can then add two other boxes (`TWBox`) which will be columns that are 50% width each.
4. They will be arranged from left to right (horizontal direction, or `Direction::Horizontal`).
5. Inside of each column box, you can provide a `Component` to actually paint the content & even
   handle user input events.
6. And ll of this happening asynchronously.

Here's the snippet that creates this "main container" box. No mention of styles here. But they are
attached to the `tw_surface` which is passed into `create_left_col()` & `create_right_col()`.

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

For now, we will just look at one of the columns - `create_left_col()`. After all this article is
about DSL to build a single style and not about how to build TUIs. Here's the snippet to create this
column, and it does use a style from the stylesheet (`style1`) that we made earlier.

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


Now that we have that context out of the way, let's look at a single style in more detail.

This is how we can imperatively create a style using the
[`r3bl_rs_utils::tui` module](https://docs.rs/r3bl_rs_utils/latest/r3bl_rs_utils/tui/index.html).

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

Once created in this manner, it can be added to a stylesheet, which can then be attached to a
`TWSurface`. And then it can be used to style things in boxes (`TWBox`).

We would like to express this declaratively, like so.

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

> 🔮 **Procedural macros** are a way for you to extend the Rust compiler and provide plugins that
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


The fun part of creating a DSL is coming up w/ whatever syntax you want to allow developers to use.
This is a very liberating, empowering, and creative exercise. You don't have to accept the language
keywords as they are. You are free to make your own! Rust is awesome!

To meet the goal of being an ergonomic API, the `tui` library leverages the mental model that people
already possess coming from web, or Android, etc. of declaratively creating styling. And then
specifying that some component uses that style. We will do the same while taking the unique
constraints of a text user interface (that only renders to the terminal) into account. Fun times!

A style is made up of the following things, and is intended to style text that is going to be
painted to the terminal.

```rust
style! {
  id:       style1                   // (req) unique id of the style
  attrib:   [dim, bold]              // (opt) array of attributes for styling text
  margin:   1                        // (opt) top, bottom, left, right margin
  color_fg: Color::Red               // (opt) Foreground color (specified via enum)
  color_bg: Color::Rgb {r:0,g:0,b:0} // (opt) Background color (specified via struct)
}
```

Let's break this down into more specifics, so that we can build the parser for the syntax next.

1. The `id` is required. The value is going to be turned into a string. So the value is a literal
   which can be anything that can be turned into a string.
2. The `attrib` field is optional. When you do provide a value for it, this looks like an array of
   attributes. Here's the full list of these attributes: `dim`, `bold`, `underline`, `reverse`,
   `hidden`, `strikethrough`.
3. The `margin` field is optional. When you do provide a value for it, this looks like an integer.
   The value is the number of spaces to add to the top, down, left, and right of the text.
4. The foreground color is optional. It can take an enum (`Color::Red`) or a struct
   (`Color::Rgb {r:0,g:0,b:0}`).
5. The background color is optional. It can take an enum (`Color::Red`) or a struct
   (`Color::Rgb {r:0,g:0,b:0}`).

> 📜 Here's the production version of the `style!` procedural macro:
> [`make_style()`](https://github.com/r3bl-org/r3bl-rs-utils/blob/main/macro/src/make_style)

You can play around w/ the syntax that you want to be able to parse. It takes some iterating in
order to be ergonomic. It helps to just write out a lot of different ways to express this
information and see what feels the best.

A lot of what feels the best will be biased by whatever style that you might be used to, based on
your background. This is another reason why the ability to create your own DSLs in Rust is so
awesome! You can just extend the language in ways that you would like code to be expressed
regardless of whatever keywords come "out of the box" w/ Rust.

Even if you change it later, it is good to start w/ something to aim for. If we aim for nothing, we
won't hit anything 🎯.

## Parse the syntax
<a id="markdown-parse-the-syntax" name="parse-the-syntax"></a>


Now that we have an idea of what the thing we want to parse looks like, let's parse it. The rough
approach that we can take to parsing this is just go ahead and try and read things that we expect to
see one after another. If it fails, then the compiler will generate a warning letting us know that
something has gone wrong. In this sense, it is fairly straightforward to parse the syntax. However,
there are a lot of details we need to take care of while we are attempting to read the next token in
the stream, since things can be optional, they can be nested, etc.

Let's start w/ a few things to get us going. First we will need a `struct` in which we can store the
things that we have parsed from the token stream. This struct basically holds all the meta data that
we will need to generate the code (which is just auto generating the imperative code we've already
seen above).

```rust
/// Docs: https://docs.rs/syn/1.0.98/syn/parse/struct.ParseBuffer.html
#[derive(Debug, Clone)]
pub(crate) struct StyleMetadata {
  pub id: Ident,                /* Only required field. */
  pub attrib_vec: Vec<Attrib>,  /* Attributes are optional. */
  pub margin: Option<UnitType>, /* Optional. */
  pub color_fg: Option<Expr>,   /* Optional. */
  pub color_bg: Option<Expr>,   /* Optional. */
}
```

Here's an `enum` that we use to represent the various attributes that we can have.

```rust
#[derive(Debug, Clone, PartialEq, Eq)]
pub(crate) enum Attrib {
  Bold,
  Dim,
  Underline,
  Reverse,
  Hidden,
  Strikethrough,
}
```

So far so good. Now we can implement the `Parse` trait for this `struct` so that we can have `syn`
take the token stream and turn it into a `StyleMetadata` struct.

```rust
impl Parse for StyleMetadata {
  fn parse(input: ParseStream) -> Result<Self> {
    let mut metadata = StyleMetadata {
      id: Ident::new("tbd", Span::call_site()),
      attrib_vec: Vec::new(),
      margin: None,
      color_fg: None,
      color_bg: None,
    };

    // TODO: implement these functions below.
    parse_id(&input, &mut metadata)?;
    parse_optional_attrib(&input, &mut metadata)?;
    parse_optional_margin(&input, &mut metadata)?;
    parse_optional_color_fg(&input, &mut metadata)?;
    parse_optional_color_bg(&input, &mut metadata)?;

    Ok(metadata)
  }
}
```

With this stubbed out, we can have `syn` do something like this in our procedural macro.

```rust
pub fn fn_proc_macro_impl(input: proc_macro::TokenStream) -> proc_macro::TokenStream {
  let style_metadata: StyleMetadata = syn::parse_macro_input!(input);
  // TODO: implement the function below.
  code_gen(style_metadata)
}
```

To implement those `parse_*` methods we saw above, we need to create a set of custom keywords for
our syntax.

```rust
/// [syn custom keywords docs](https://docs.rs/syn/latest/syn/macro.custom_keyword.html)
pub(crate) mod kw {
  syn::custom_keyword!(id);
  syn::custom_keyword!(bold);
  syn::custom_keyword!(attrib);
  syn::custom_keyword!(dim);
  syn::custom_keyword!(underline);
  syn::custom_keyword!(reverse);
  syn::custom_keyword!(hidden);
  syn::custom_keyword!(strikethrough);
  syn::custom_keyword!(margin);
  syn::custom_keyword!(color_fg);
  syn::custom_keyword!(color_bg);
}
```

With that out of the way, we can implement each of the functions. Here's the simplest one. Since the
`id` is required, we can just go for it. If it fails, then the compiler will complain that `id` is
missing.

```rust
// Parse id (required).
fn parse_id(input: &ParseStream, metadata: &mut StyleMetadata) -> Result<()> {
  let lookahead = input.lookahead1();
  if lookahead.peek(kw::id) {
    input.parse::<kw::id>()?;
    input.parse::<Token![:]>()?;
    let id = input.parse::<Ident>()?;
    metadata.id = id;
  }
  call_if_true!(DEBUG, println!("🚀 id: {:?}", metadata.id));
  Ok(())
}
```

The next one is more difficult, since we are dealing w/ optional attributes that can be parsed. Also
the things being parsed come in an array and there can be a bunch of different ones.

```rust
// Parse attrib (optional).
fn parse_optional_attrib(input: &ParseStream, metadata: &mut StyleMetadata) -> Result<()> {
  let lookahead = input.lookahead1();
  if lookahead.peek(kw::attrib) {
    input.parse::<kw::attrib>()?;
    input.parse::<Token![:]>()?;

    let expr_array: ExprArray = input.parse()?;
    for item in expr_array.elems {
      if let Expr::Path(ExprPath {
        attrs: _,
        qself: _,
        path: Path { segments, .. },
      }) = item
      {
        let PathSegment {
          ident,
          arguments: _,
        } = segments.first().unwrap();
        match ident.as_str().as_ref() {
          "bold" => metadata.attrib_vec.push(Attrib::Bold),
          "dim" => metadata.attrib_vec.push(Attrib::Dim),
          "underline" => metadata.attrib_vec.push(Attrib::Underline),
          "reverse" => metadata.attrib_vec.push(Attrib::Reverse),
          "hidden" => metadata.attrib_vec.push(Attrib::Hidden),
          "strikethrough" => metadata.attrib_vec.push(Attrib::Strikethrough),
          _ => panic!("🚀 unknown attrib: {}", ident),
        }
      }
    }

    call_if_true!(DEBUG, println!("🚀 attrib_vec: {:?}", metadata.attrib_vec));
  }
  Ok(())
}
```

Finally, the following are fairly naive implementations of the rest of the required functions. And I
say naive, because we don't really support handling colors that are passed in a variable. We
currently only support `Color` `enum` and `Rgb` `struct`. But it is feasible that a variable can be
passed in which holds either. We will leave this implementation for another article.

```rust
// Parse margin (optional).
fn parse_optional_margin(input: &ParseStream, metadata: &mut StyleMetadata) -> Result<()> {
  let lookahead = input.lookahead1();
  if lookahead.peek(kw::margin) {
    input.parse::<kw::margin>()?;
    input.parse::<Token![:]>()?;
    let lit_int = input.parse::<LitInt>()?;
    let margin_int: UnitType = lit_int.base10_parse().unwrap();
    metadata.margin = Some(margin_int);
    call_if_true!(DEBUG, println!("🚀 margin: {:?}", &metadata.margin));
  }
  Ok(())
}

// Parse color_fg (optional).
fn parse_optional_color_fg(input: &ParseStream, metadata: &mut StyleMetadata) -> Result<()> {
  let lookahead = input.lookahead1();
  if lookahead.peek(kw::color_fg) {
    input.parse::<kw::color_fg>()?;
    input.parse::<Token![:]>()?;
    let color_expr = input.parse::<Expr>()?;
    metadata.color_fg = Some(color_expr);
    call_if_true!(DEBUG, println!("🚀 color_fg: {:#?}", metadata.color_fg));
  }

  Ok(())
}

// Parse color_bg (optional).
fn parse_optional_color_bg(input: &ParseStream, metadata: &mut StyleMetadata) -> Result<()> {
  let lookahead = input.lookahead1();
  if lookahead.peek(kw::color_bg) {
    input.parse::<kw::color_bg>()?;
    input.parse::<Token![:]>()?;
    let color_expr = input.parse::<Expr>()?;
    metadata.color_bg = Some(color_expr);
    call_if_true!(DEBUG, println!("🚀 color_bg: {:#?}", metadata.color_bg));
  }

  Ok(())
}
```

With the parsing out of the way, we can now proceed to the code generation.

## Generate the code
<a id="markdown-generate-the-code" name="generate-the-code"></a>


Revisiting our procedural macro function, we can now generate the code.

```rust
pub fn fn_proc_macro_impl(input: proc_macro::TokenStream) -> proc_macro::TokenStream {
  let style_metadata: StyleMetadata = parse_macro_input!(input);
  code_gen(style_metadata)
}
```

This is much more straightforward than parsing the syntax, thanks to `quote!`.

```rust
pub(crate) fn code_gen(
  StyleMetadata {id, attrib_vec, margin, color_fg, color_bg}: StyleMetadata,
) -> proc_macro::TokenStream {
  let has_attrib_bold = attrib_vec.contains(&Attrib::Bold);
  let has_attrib_dim = attrib_vec.contains(&Attrib::Dim);
  let has_attrib_underline = attrib_vec.contains(&Attrib::Underline);
  let has_attrib_reverse = attrib_vec.contains(&Attrib::Reverse);
  let has_attrib_hidden = attrib_vec.contains(&Attrib::Hidden);
  let has_attrib_strikethrough = attrib_vec.contains(&Attrib::Strikethrough);

  let id_str = format!("{}", id);

  let maybe_margin_expr = match margin {
    Some(margin_int) => {
      quote! {
        margin: Some(#margin_int),
      }
    }
    None => quote! {},
  };

  let maybe_color_fg_expr = match color_fg {
    Some(color_expr) => {
      quote! {
        color_fg: Some(crossterm::style::#color_expr.into()),
      }
    }
    None => quote! {},
  };

  let maybe_color_bg_expr = match color_bg {
    Some(color_expr) => {
      quote! {
        color_bg: Some(crossterm::style::#color_expr.into()),
      }
    }
    None => quote! {},
  };

  quote! {
    r3bl_rs_utils::Style {
      id: #id_str.to_string(),
      bold: #has_attrib_bold,
      dim: #has_attrib_dim,
      underline: #has_attrib_underline,
      reverse: #has_attrib_reverse,
      hidden: #has_attrib_hidden,
      strikethrough: #has_attrib_strikethrough,
      #maybe_margin_expr
      #maybe_color_fg_expr
      #maybe_color_bg_expr
      .. Default::default()
    }
  }
  .into()
}
```

## Exporting it
<a id="markdown-exporting-it" name="exporting-it"></a>


This is the simplest part of our journey. In our procedural macro crate, we have do something like
this.

```rust
extern crate proc_macro;
mod make_style;
use proc_macro::TokenStream;

#[proc_macro]
pub fn style(input: TokenStream) -> TokenStream { make_style::fn_proc_macro_impl(input) }
```

> 📜 Here's the production version of the `style!` procedural macro:
> [`make_style()`](https://github.com/r3bl-org/r3bl-rs-utils/blob/main/macro/src/make_style)

## Wrapping up
<a id="markdown-wrapping-up" name="wrapping-up"></a>


This article just shows how to handle a single style. And it has room for improvement (being able to
handle variables that hold color values in them).

In the future we will expand this DSL to include more features like generating the entire stylesheet
declaratively. And then move on to creating JSX like syntax in Rust for layout stuff in the `tui`
module as well. More articles to follow based on this work.

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
