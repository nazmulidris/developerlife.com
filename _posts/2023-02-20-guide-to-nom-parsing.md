---
title: "Guide to parsing with nom"
author: Nazmul Idris
date: 2023-02-20 15:00:00+00:00
excerpt: |
  This tutorial is a guide to parsing with nom. It covers the basics of parsing and how to use nom
  to parse a string into a data structure. We will cover a variety of different examples ranging
  from parsing simple CSS like syntax to a full blown Markdown parser.
layout: post
categories:
  - Rust
---

<img class="post-hero-image" src="{{ 'assets/nom-parser.svg' | relative_url }}"/>

<!-- TOC -->

- [Introduction](#introduction)
- [Documentation](#documentation)
- [Getting to know nom using a simple example](#getting-to-know-nom-using-a-simple-example)
  - [Parsing hex color codes](#parsing-hex-color-codes)
  - [What does this code do, how does it work?](#what-does-this-code-do-how-does-it-work)
  - [Generalized workflow](#generalized-workflow)
- [Build a Markdown parser](#build-a-markdown-parser)

<!-- /TOC -->

## Introduction
<a id="markdown-introduction" name="introduction"></a>

This tutorial is a guide to parsing with nom. It covers the basics of parsing and how to use nom to
parse a string into a data structure. We will cover a variety of different examples ranging from
parsing simple CSS like syntax to a full blown Markdown parser.

This tutorial has 2 examples in it:

1. [CSS style syntax](#getting-to-know-nom-using-a-simple-example)
2. [Markdown parser](#build-a-markdown-parser)

{%- include featured.html -%}

> For more information on general Rust type system design (functional approach rather than
> object oriented), please take a look at this [paper](https://arxiv.org/pdf/2307.07069.pdf)
> by Will Crichton demonstrating Typed Design Patterns with Rust.

## Documentation
<a id="markdown-documentation" name="documentation"></a>

nom is a huge topic. This tutorial takes a hands on approach to learning nom. However, the resources
listed below are very useful for learning nom. Think of them as a reference guide and deep dive into
how the nom library works.

- Useful:
  - Source code examples (fantastic way to learn nom):
    - [export-logseq-notes repo](https://github.com/dimfeld/export-logseq-notes/tree/master/src)
  - Videos:
    - [Intro from the author 7yrs old](https://youtu.be/EXEMm5173SM)
    - Nom 7 deep dive videos:
      - [Parsing name, age, and preference from natural language input](https://youtu.be/Igajh2Vliog)
      - [Parsing number ranges](https://youtu.be/Xm4jrjohDN8)
      - [Parsing lines of text](https://youtu.be/6b2ymQWldoE)
    - Nom 6 videos (deep dive into how nom combinators themselves are constructed):
      - [Deep dive, Part 1](https://youtu.be/zHF6j1LvngA)
      - [Deep dive, Part 2](https://youtu.be/9GLFJcSO08Y)
  - Tutorials:
    - [Build a JSON parser using nom7](https://codeandbitters.com/lets-build-a-parser/)
    - [Excellent beginner to advanced](https://github.com/benkay86/nom-tutorial)
    - [Write a parser from scratch](https://github.com/rust-bakery/nom/blob/main/doc/making_a_new_parser_from_scratch.md)
  - Reference docs:
    - [nominomicon](https://tfpk.github.io/nominomicon/introduction.html)
    - [What combinator or parser to use?](https://github.com/rust-bakery/nom/blob/main/doc/choosing_a_combinator.md)
    - [docs.rs](https://docs.rs/nom/7.1.3/nom/)
    - [Upgrading to nom 5.0](https://github.com/rust-bakery/nom/blob/main/doc/upgrading_to_nom_5.md)
- Less useful:
  - [README](https://github.com/rust-bakery/nom)
  - [nom crate](https://crates.io/crates/nom)

## Getting to know nom using a simple example
<a id="markdown-getting-to-know-nom-using-a-simple-example" name="getting-to-know-nom-using-a-simple-example"></a>


[nom](https://crates.io/crates/nom) is a parser combinator library for Rust. You can write small
functions that parse a specific part of your input, and then combine them to build a parser that
parses the whole input. nom is very efficient and fast, it does not allocate memory when parsing if
it doesn't have to, and it makes it very easy for you to do the same. nom uses streaming mode or
complete mode, and in this tutorial & code examples provided we will be using complete mode.

Roughly the way it works is that you tell nom how to parse a bunch of bytes in a way that matches
some pattern that is valid for your data. It will try to parse as much as it can from the input, and
the rest of the input will be returned to you.

You express the pattern that you're looking for by combining parsers. nom has a whole bunch of these
that come out of the box. And a huge part of learning nom is figuring out what these built in
parsers are and how to combine them to build a parser that does what you want.

Errors are a key part of it being able to apply a variety of different parsers to the same input. If
a parser fails, nom will return an error, and the rest of the input will be returned to you. This
allows you to combine parsers in a way that you can try to parse a bunch of different things, and if
one of them fails, you can try the next one. This is very useful when you are trying to parse a
bunch of different things, and you don't know which one you are going to get.

### Parsing hex color codes
<a id="markdown-parsing-hex-color-codes" name="parsing-hex-color-codes"></a>


Let's dive into nom using a simple example of parsing
[hex color codes](https://developer.mozilla.org/en-US/docs/Web/CSS/color).

```rust
//! This module contains a parser that parses a hex color string into a [Color] struct.
//! The hex color string can be in the following format `#RRGGBB`.
//! For example, `#FF0000` is red.

use std::num::ParseIntError;
use nom::{bytes::complete::*, combinator::*, error::*, sequence::*, IResult, Parser};

#[derive(Debug, PartialEq)]
pub struct Color {
    pub red: u8,
    pub green: u8,
    pub blue: u8,
}

impl Color {
    pub fn new(red: u8, green: u8, blue: u8) -> Self {
        Self { red, green, blue }
    }
}

/// Helper functions to match and parse hex digits. These are not [Parser]
/// implementations.
mod helper_fns {
    use super::*;

    /// This function is used by [map_res] and it returns a [Result], not [IResult].
    pub fn parse_str_to_hex_num(input: &str) -> Result<u8, std::num::ParseIntError> {
        u8::from_str_radix(input, 16)
    }

    /// This function is used by [take_while_m_n] and as long as it returns `true`
    /// items will be taken from the input.
    pub fn match_is_hex_digit(c: char) -> bool {
        c.is_ascii_hexdigit()
    }

    pub fn parse_hex_seg(input: &str) -> IResult<&str, u8> {
        map_res(
            take_while_m_n(2, 2, match_is_hex_digit),
            parse_str_to_hex_num,
        )(input)
    }
}

/// These are [Parser] implementations that are used by [hex_color_no_alpha].
mod intermediate_parsers {
    use super::*;

    /// Call this to return function that implements the [Parser] trait.
    pub fn gen_hex_seg_parser_fn<'input, E>() -> impl Parser<&'input str, u8, E>
    where
        E: FromExternalError<&'input str, ParseIntError> + ParseError<&'input str>,
    {
        map_res(
            take_while_m_n(2, 2, helper_fns::match_is_hex_digit),
            helper_fns::parse_str_to_hex_num,
        )
    }
}

/// This is the "main" function that is called by the tests.
fn hex_color_no_alpha(input: &str) -> IResult<&str, Color> {
    // This tuple contains 3 ways to do the same thing.
    let it = (
        helper_fns::parse_hex_seg,
        intermediate_parsers::gen_hex_seg_parser_fn(),
        map_res(
            take_while_m_n(2, 2, helper_fns::match_is_hex_digit),
            helper_fns::parse_str_to_hex_num,
        ),
    );
    let (input, _) = tag("#")(input)?;
    let (input, (red, green, blue)) = tuple(it)(input)?; // same as `it.parse(input)?`
    Ok((input, Color { red, green, blue }))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_valid_color() {
        let mut input = String::new();
        input.push_str("#2F14DF");
        input.push('🔅');

        let result = dbg!(hex_color_no_alpha(&input));

        let Ok((remainder, color)) = result else { panic!(); };
        assert_eq!(remainder, "🔅");
        assert_eq!(color, Color::new(47, 20, 223));
    }

    #[test]
    fn parse_invalid_color() {
        let result = dbg!(hex_color_no_alpha("🔅#2F14DF"));
        assert!(result.is_err());
    }
}
```

### What does this code do, how does it work?
<a id="markdown-what-does-this-code-do%2C-how-does-it-work%3F" name="what-does-this-code-do%2C-how-does-it-work%3F"></a>


Please note that:

- This string can be parsed: `#2F14DF🔅`.
- However, this string can't `🔅#2F14DF`.

So what is going on in the source code above?

1. The `intermediate_parsers::hex_color_no_alpha()` function is the main function that orchestrates
   all the other functions to parse an `input: &str` and turn it into a `(&str, Color)`.

   - The `tag` combinator function is used to match the `#` character. This means that if the input
     doesn't start with `#`, the parser will fail (which is why `🔅#2F14DF` fails). It returns the
     remaining input after `#`. And the output is `#` which we throw away.
   - A `tuple` is created that takes 3 parsers, which all do the same exact thing, but are written
     in 3 different ways just to demonstrate how these can be written.
     1. The `helper_fns::parse_hex_seg()` function is added to a tuple.
     2. The higher order function `intermediate_parsers::gen_hex_seg_parser_fn()` is added to the
        tuple.
     3. Finally, the `map_res` combinator is directly added to the tuple.
   - An extension function on this tuple called `parse()` is called w/ the `input` (thus far). This
     is used to parse the input hex number.
     - It returns the remaining input after the hex number which is why `#2F14DF🔅` returns `🔅` as
       the first item in the tuple.
     - The second item in the tuple is the parsed color string turned into a `Color` struct.

2. Let's look at the `helper_fns::parse_hex_seg` (the other 2 ways shown above do the same exact
   thing). The signature of this function tells nom that you can call the function w/ `input`
   argument and it will return `IResult<Input, Output, Error>`. This signature is the pattern that
   we will end up using to figure out how to chain combinators together. Here's how the `map_res`
   combinator is used by `parse_hex_seg()` to actually do the parsing:

   1. `take_while_m_n`: This combinator takes a range of characters (`2, 2`) and applies the
      function `match_is_hex_digit` to determine whether the `char` is a hex digit (using
      `is_ascii_hexdigit()` on the `char`). This is used to match a valid hex digit. It returns a
      `&str` slice of the matched characters. Which is then passed to the next combinator.
   2. `parse_str_to_hex_num`: This parser is used on the string slice returned from above. It simply
      takes string slice and turns it into a `Result<u8>, std::num::ParseIntError>`. The error is
      important, since if the string slice is not a valid hex digit, then we want to return this
      error.

3. The key concept in nom is the `Parser` trait which is implemented for any `FnMut` that accepts an
   input and returns an `IResult<Input, Output, Error>`.
   - If you write a simple function w/ the signature
     `fn(input: Input) -> IResult<Input, Output, Error>` then you are good to go! You just need to
     call `parse()` on the `Input` type and this will kick off the parsing.
   - Alternatively, you can just call the nom `tuple` function directly via
     `nom::sequence::tuple(...)(input)?`. Or you can just call the `parse()` method on the tuple
     since this is an extension function on tuples provided by nom.
   - `IResult` is a very important type alias. It encapsulates 3 key types that are related to
     parsing:
     1. The `Input` type is the type of the input that is being parsed. For example, if you are
        parsing a string, then the `Input` type is `&str`.
     2. The `Output` type is the type of the output that is returned by the parser. For example, if
        you are parsing a string and you want to return a `Color` struct, then the `Output` type is
        `Color`.
     3. The `Error` type is the type of the error that is returned by the parser. For example, if
        you are parsing a string and you want to return a `nom::Err::Error` error, then the `Error`
        type is `nom::Err::Error`. This is very useful when you are developing your parser
        combinators and you run into errors and have to debug them.

### Generalized workflow
<a id="markdown-generalized-workflow" name="generalized-workflow"></a>


After the really complicated walk through above, we could have just written the entire thing
concisely like so:

```rust
pub fn parse_hex_seg(input: &str) -> IResult<&str, u8> {
  map_res(
    take_while_m_n(2, 2, |it: char| it.is_ascii_hexdigit()),
    |it: &str| u8::from_str_radix(it, 16),
  )(input)
}

fn hex_color_no_alpha(input: &str) -> IResult<&str, Color> {
  let (input, _) = tag("#")(input)?;
  let (input, (red, green, blue)) = tuple((
    helper_fns::parse_hex_seg,
    helper_fns::parse_hex_seg,
    helper_fns::parse_hex_seg,
  ))(input)?;
  Ok((input, Color { red, green, blue }))
}
```

This is a very simple example, but it shows how you can combine parsers together to create more
complex parsers. You start w/ the simplest one first, and then build up from there.

- In this case the simplest one is `parse_hex_seg()` which is used to parse a single hex segment.
  Inside this function we call `map_res()` w/ the supplied `input` and simply return the result.
  This is also a very common thing to do, is to wrap calls to other parsers in functions and then
  re-use them in other parsers.
- Finally, the `hex_color_no_alpha()` function is used to parse a hex color w/o an alpha channel.
  - The `tag()` combinator is used to match the `#` character.
  - The `tuple()` combinator is used to match the 3 hex segments.
  - The `?` operator is used to return the error if there is one.
  - The `Ok()` is used to return the parsed `Color` struct and the remaining input.

## Build a Markdown parser
<a id="markdown-build-a-markdown-parser" name="build-a-markdown-parser"></a>

> 💡 You can get the source code for the Markdown parser shown in this article from the
> [`r3bl-open-core`](https://github.com/r3bl-org/r3bl-open-core/tree/main/tui/src/tui/md_parser)
> repo.
>
> 🌟 Please star this repo on github if you like it 🙏.

The [`md_parser`](https://github.com/r3bl-org/r3bl-open-core/tree/main/tui/src/tui/md_parser) module
in the `r3bl-open-core` repo contains a fully functional Markdown parser (and isn't written as a test
but a real module that you can use in your projects that need a Markdown parser). This parser
supports standard Markdown syntax as well as some extensions that are added to make it work w/ R3BL
products. It makes a great starting point to study how a relatively complex parser is written. There
are lots of tests that you can follow along to understand what the code is doing.

Here are some entry points into the codebase.

1. The main function
   [`parse_markdown()`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/parser.rs)
   that does the parsing of a string slice into a
   [`Document`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/types.rs).
   The tests are provided alongside the code itself. And you can follow along to see how other
   smaller parsers are used to build up this big one that parses the whole of the Markdown document.

   1. All the parsers related to parsing metadata specific for R3BL applications which are not
      standard Markdown can be found in
      [`parser_impl_metadata`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/parser_impl_metadata.rs).
   2. All the parsers that are related to parsing the main "blocks" of Markdown, such as order
      lists, unordered lists, code blocks, text blocks, heading blocks, can be found
      [`parser_impl_block`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/parser_impl_block.rs)
   3. All the parsers that are related to parsing a single line of Markdown text, such as links,
      bold, italic, etc. can be found
      [`parser_impl_element`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/parser_impl_element.rs)

2. The [types](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/types.rs)
   that are used to represent the Markdown document model
   ([`Document`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/types.rs))
   and all the other intermediate types (`Fragment`, `Block`, etc) & enums required for parsing.
