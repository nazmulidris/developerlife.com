---
title: "Build with Naz : Comprehensive guide to nom parsing"
author: Nazmul Idris
date: 2023-02-20 15:00:00+00:00
update: 2024-06-19 15:00:00+00:00
excerpt: |
  This tutorial is a comprehensive guide to parsing with nom. It covers the basics of parsing and
  how to use nom to parse a string into a data structure. It also covers more complex topics like
  human readable error reporting, and building up complex parsers. We will cover a variety of different
  examples ranging from parsing simple CSS like syntax to a full blown Markdown parser.
layout: post
categories:
  - Rust
  - CLI
  - Server
  - TUI
---

<img class="post-hero-image" src="{{ 'assets/rust-nom-comprehensive.svg' | relative_url }}"/>

<!-- TOC -->

- [Introduction](#introduction)
- [Getting to know nom using lots of examples](#getting-to-know-nom-using-lots-of-examples)
- [Related video](#related-video)
- [Hex color code parser](#hex-color-code-parser)
  - [What does this code do, how does it work?](#what-does-this-code-do-how-does-it-work)
    - [The Parser trait and IResult](#the-parser-trait-and-iresult)
    - [Main parser function that calls all the other parsers](#main-parser-function-that-calls-all-the-other-parsers)
    - [The hex segment parser, comprised of nom combinator functions, and IResult](#the-hex-segment-parser-comprised-of-nom-combinator-functions-and-iresult)
  - [Generalized workflow](#generalized-workflow)
  - [Why can't we parse "🔅#2F14DF"?](#why-cant-we-parse-2f14df)
  - [Better error reporting when things go wrong](#better-error-reporting-when-things-go-wrong)
- [Other examples](#other-examples)
  - [Simple CSS syntax parser](#simple-css-syntax-parser)
  - [Simple natural language parser](#simple-natural-language-parser)
- [Markdown parser](#markdown-parser)
- [References](#references)

<!-- /TOC -->

## Introduction
<a id="markdown-introduction" name="introduction"></a>

This tutorial is a comprehensive guide to parsing with nom. It covers the basics of parsing and
how to use nom to parse a string into a data structure. It also covers more complex topics like
human readable error reporting, and building up complex parsers. We will cover a variety of different
examples ranging from parsing simple CSS like syntax to a full blown Markdown parser.

> For more information on general Rust type system design (functional approach rather than
> object oriented), please take a look at this [paper](https://arxiv.org/pdf/2307.07069.pdf)
> by Will Crichton demonstrating Typed Design Patterns with Rust.

## Getting to know nom using lots of examples
<a id="markdown-getting-to-know-nom-using-lots-of-examples" name="getting-to-know-nom-using-lots-of-examples"></a>

[`nom`](https://crates.io/crates/nom) is a parser combinator library for Rust. You can write small
functions that parse a specific part of your input, and then combine them to build a parser that
parses the whole input. `nom` is very efficient and fast, it does not allocate memory when parsing if
it doesn't have to, and it makes it very easy for you to do the same. `nom` uses streaming mode or
complete mode, and in this tutorial & code examples provided we will be using complete mode.

Roughly the way it works is that you tell `nom` how to parse a bunch of bytes in a way that matches
some pattern that is valid for your data. It will try to parse as much as it can from the input, and
the rest of the input will be returned to you.

You express the pattern that you're looking for by combining parsers. `nom` has a whole bunch of these
that come out of the box. And a huge part of learning `nom` is figuring out what these built in
parsers are and how to combine them to build a parser that does what you want.

Errors are a key part of it being able to apply a variety of different parsers to the same input. If
a parser fails, `nom` will return an error, and the rest of the input will be returned to you. This
allows you to combine parsers in a way that you can try to parse a bunch of different things, and if
one of them fails, you can try the next one. This is very useful when you are trying to parse a
bunch of different things, and you don't know which one you are going to get.

## Related video
<a id="markdown-related-video" name="related-video"></a>

If you like to consume content via video, then you can watch this video that covers the same content
as this article, but in a live coding format.

<!-- video on nom -->
<iframe
    src="https://www.youtube.com/embed/v3tMwr_ysPg?si=rDXomVWgE1GBlGm-"
    title="YouTube video player" frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    referrerpolicy="strict-origin-when-cross-origin"
    allowfullscreen
    >
</iframe>

> You can get the source code for the examples in this
> [repo](https://github.com/nazmulidris/rust-scratch/blob/main/nom).

## Hex color code parser
<a id="markdown-hex-color-code-parser" name="hex-color-code-parser"></a>

Let's dive into `nom` using a simple example of parsing
[hex color codes](https://developer.mozilla.org/en-US/docs/Web/CSS/color).

```rust
//! This module contains a parser that parses a hex color
//! string into a [Color] struct.
//! The hex color string can be in the following format `#RRGGBB`.
//! For example, `#FF0000` is red.

use std::num::ParseIntError;
use nom::{
    bytes::complete::*, combinator::*, error::*, sequence::*, IResult, Parser
};

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

/// Helper functions to match and parse hex digits. These are not
/// [Parser] implementations.
mod helper_fns {
    use super::*;

    /// This function is used by [map_res] and it returns a [Result]
    /// not [IResult].
    pub fn parse_str_to_hex_num(input: &str) ->
        Result<u8, std::num::ParseIntError>
    {
        u8::from_str_radix(input, 16)
    }

    /// This function is used by [take_while_m_n] and as long as it
    /// returns `true` items will be taken from the input.
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

/// These are [Parser] implementations that are used by
/// [hex_color_no_alpha].
mod intermediate_parsers {
    use super::*;

    /// Call this to return function that implements the [Parser] trait.
    pub fn gen_hex_seg_parser_fn<'input, E>() ->
        impl Parser<&'input str, u8, E>
    where
        E: FromExternalError<&'input str, ParseIntError> +
           ParseError<&'input str>,
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
    let (input, (red, green, blue)) =
        tuple(it)(input)?; // same as `it.parse(input)?`
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

> You can get the source code for the examples in this
> [repo](https://github.com/nazmulidris/rust-scratch/blob/main/nom).

### What does this code do, how does it work?
<a id="markdown-what-does-this-code-do%2C-how-does-it-work%3F" name="what-does-this-code-do%2C-how-does-it-work%3F"></a>

Please note that:

- This string can be parsed: `#2F14DF🔅` ✅.
- However, this string can't `🔅#2F14DF` 🤔.

So what is going on in the source code above?

#### The Parser trait and IResult
<a id="markdown-the-parser-trait-and-iresult" name="the-parser-trait-and-iresult"></a>

The key concept in `nom` is the `Parser` trait which is implemented for any `FnMut` that accepts an
input and returns an `IResult<Input, Output, Error>`.

- If you write a simple function w/ the signature
  `fn(input: Input) -> IResult<Input, Output, Error>` then you are good to go! You just need to
  call `parse()` on the `Input` type and this will kick off the parsing.
- Alternatively, you can just call the `nom` `tuple` function directly via
  `nom::sequence::tuple(...)(input)?`. Or you can just call the `parse()` method on the tuple
  since this is an extension function on tuples provided by `nom`.
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
  4. Typically we are dealing with complete parsers which are character based. These are reflected
     in the functions that we import from `nom`. It is pretty common to see the `'input` lifetime
     parameter used in functions that are parsers. This way slices of the input can be returned
     from the parser without having to `Clone` or allocate memory.

     Here's an example of this:
     ```rust
     pub fn parse_hex_seg<'input, E /* thread this generic type down */>(
         input: &'input str,
     ) -> IResult<&'input str, u8, E>
     where
         E: ParseError<&'input str> + ContextError<&'input str>
     { /* code */ }
     ```

#### Main parser function that calls all the other parsers
<a id="markdown-main-parser-function-that-calls-all-the-other-parsers" name="main-parser-function-that-calls-all-the-other-parsers"></a>

The `intermediate_parsers::hex_color_no_alpha()` function is the main function that
orchestrates all the other functions to parse an `input: &str` and turn it into a
`(&str, Color)`.

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

#### The hex segment parser, comprised of nom combinator functions, and IResult
<a id="markdown-the-hex-segment-parser%2C-comprised-of-nom-combinator-functions%2C-and-iresult" name="the-hex-segment-parser%2C-comprised-of-nom-combinator-functions%2C-and-iresult"></a>

Let's look at the `helper_fns::parse_hex_seg` (the other 2 ways shown above do the same exact
thing). The signature of this function tells `nom` that you can call the function w/ `input`
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

### Why can't we parse "🔅#2F14DF"?
<a id="markdown-why-can't-we-parse-%22%F0%9F%94%85%232f14df%22%3F" name="why-can't-we-parse-%22%F0%9F%94%85%232f14df%22%3F"></a>

The reason we can't parse `🔅#2F14DF` is because the `tag("#")` combinator is used to
match the `#` character at the very start of our input. Remember that the parser will try
to eat the bytes from the start of the input to the end. This means that if the input
doesn't start with `#`, the parser will fail.

If we have the requirement to parse a hex color code that doesn't start with `#`, then we
can modify the parser to handle this case. Here's one way in which we can do this.

```rust
/// This is the "main" function that is called by the tests.
fn hex_color_no_alpha(
    input: &str,
) -> IResult<
    (
        /* start remainder */ &str,
        /* end remainder */ &str,
    ),
    Color,
> {
    let mut root_fn = preceded(
        /* throw away "#" */
        tag("#"),
        /* return color */
        tuple((
            helper_fns::parse_hex_seg,
            helper_fns::parse_hex_seg,
            helper_fns::parse_hex_seg,
        )),
    );

    // Get chars before "#".
    let pre_root_fn = take_until::<
        /* input after "#" */ &str,
        /* start remainder */ &str,
        /* error type */ nom::error::VerboseError<&str>,
    >("#");

    if let Ok((input_after_hash, start_remainder)) = pre_root_fn(input) {
        if let Ok((end_remainder, (red, green, blue))) =
            root_fn(input_after_hash)
        {
            Ok((
                (start_remainder, end_remainder),
                Color::new(red, green, blue),
            ))
        } else {
            Err(nom::Err::Error(Error::new(
                (input_after_hash, ""),
                ErrorKind::Fail,
            )))
        }
    } else {
        Err(nom::Err::Error(Error::new((input, ""), ErrorKind::Fail)))
    }
}
```

And this is what the tests would look like:

```rust
#[test]
fn parse_valid_color() {
    let input = "\n🌜\n#2F14DF\n🔅\n";
    let result = dbg!(hex_color_no_alpha(input));
    let Ok((remainder, color)) = result else {
        panic!();
    };
    assert_eq!(remainder, ("\n🌜\n", "\n🔅\n"));
    assert_eq!(color, Color::new(47, 20, 223));
}
```

### Better error reporting when things go wrong
<a id="markdown-better-error-reporting-when-things-go-wrong" name="better-error-reporting-when-things-go-wrong"></a>

We can use the `context` combinator to provide better error reporting. This is a very useful
combinator that you can use to provide better error messages when parsing fails. However, when
using it, we need to:

1. Be careful of expressing the `nom` error types as generic arguments to the parser
   functions, by  using the `nom::error::VerboseError` type to get more detailed error
   messages which are used by `nom::error::convert_error`.
2. This type needs to be passed as a generic argument to each parser that uses the
   `context` combinator.
3. In the example below, we call `u8::from_str_radix`. This might throw a
   `core::num::ParseIntError` error. However, this error is never thrown in the code. Even
   if `core::num::ParseIntError` were to be thrown, it would be *consumed*, and a higher
   level `nom` error would be returned for the `map_res` combinator.

Here's an example of this.

```rust
use nom::{
    bytes::complete::{tag, take_while_m_n},
    combinator::map_res,
    error::{context, convert_error},
    sequence::Tuple,
    IResult, Parser,
};

/// `nom` is used to parse the hex digits from string. Then
/// [u8::from_str_radix] is used to convert the hex string into a
/// number. This can't fail, even though in the function signature,
/// that may return a [core::num::ParseIntError], which never
/// happens. Note the use of [nom::error::VerboseError] to get more
/// detailed error  messages that are passed to
/// [nom::error::convert_error].
///
/// Even if [core::num::ParseIntError] were to be thrown, it would
/// be consumed, and a higher level `nom` error would be returned
/// for the `map_res` combinator.
pub fn parse_hex_seg(input: &str) -> IResult<
    &str,
    u8,
    nom::error::VerboseError<&str>
> {
    map_res(
        take_while_m_n(2, 2, |it: char| it.is_ascii_hexdigit()),
        |it| u8::from_str_radix(it, 16),
    )
    .parse(input)
}

/// Note the use of [nom::error::VerboseError] to get more detailed
/// error messages that are passed to [nom::error::convert_error].
pub fn root(input: &str) -> IResult<
    &str,
    (&str, u8, u8, u8),
    nom::error::VerboseError<&str>
> {
    let (remainder, (_, red, green, blue)) = (
        context("start of hex color", tag("#")),
        context("hex seg 1", parse_hex_seg),
        context("hex seg 2", parse_hex_seg),
        context("hex seg 3", parse_hex_seg),
    )
        .parse(input)?;

    Ok((remainder, ("", red, green, blue)))
}
```

This just sets up our code to use `context`, but we still have to format the output of the
error in a human readable way to `stdout`. This is where `convert_error` comes in. Here's
how you can use it.

```rust
#[test]
fn test_root_1() {
    let input = "x#FF0000";
    let result = root(input);
    println!("{:?}", result);
    assert!(result.is_err());

    match result {
        Err(nom::Err::Error(e)) | Err(nom::Err::Failure(e)) => {
            println!(
                "Could not parse because ... {}",
                convert_error(input, e)
            );
        }
        _ => { /* do nothing for nom::Err::Incomplete(_) */ }
    }
}
```

Here's the output of the test.

```text
Err(Error(VerboseError { errors: [("x#FF0000", Nom(Tag)), ("x#FF0000", Context("start of hex color"))] }))
Could not parse because ... 0: at line 1, in Tag:
x#FF0000
^

1: at line 1, in start of hex color:
x#FF0000
^
```

Here's another test to see even more detailed error messages.

```rust
#[test]
fn test_root_2() {
    let input = "#FF_000";
    let result = root(input);
    println!("{:?}", result);
    assert!(result.is_err());

    match result {
        Err(nom::Err::Error(e)) | Err(nom::Err::Failure(e)) => {
            println!(
                "Could not parse because ... {}",
                convert_error(input, e)
            );
        }
        _ => { /* do nothing for nom::Err::Incomplete(_) */ }
    }
}
```

Here's the output of this test.

```text
Err(Error(VerboseError { errors: [("_000", Nom(TakeWhileMN)), ("_000", Context("hex seg 2"))] }))
Could not parse because ... 0: at line 1, in TakeWhileMN:
#FF_000
   ^

1: at line 1, in hex seg 2:
#FF_000
   ^
```

## Other examples
<a id="markdown-other-examples" name="other-examples"></a>

### Simple CSS syntax parser
<a id="markdown-simple-css-syntax-parser" name="simple-css-syntax-parser"></a>

Here's a snippet from the [simple CSS parser
code](https://github.com/nazmulidris/rust-scratch/blob/main/nom/src/parser_simple_css.rs),
that allows `nom` to parse a simple CSS like syntax. The hex color string can be in the
following formats:

1. `#RRGGBB`, eg: `#FF0000` for red.
2. `#RRGGBBAA`, eg: `#FF0000FF` for red with alpha.

Here are some examples of valid input strings:
```text
style = {
    fg_color: #FF0000;
    bg_color: #FF0000FF;
}
```

1. The `fg_color` and `bg_color` are both optional.
2. The `style = {` and `}` are required.

```rust
/// Type alias for [nom::error::VerboseError] to make the code more
/// readable.
type VError<'input> = nom::error::VerboseError<&'input str>;

/// Parser functions for a single hex segment & `#RRGGBB` &
/// `#RRGGBBAA`.
mod hex_color_parser_helper_fns {
    use super::*;

    pub fn parse_single_hex_segment(input: &str) -> IResult<&str, u8, VError> {
        map_res(
            take_while_m_n(2, 2, |it: char| it.is_ascii_hexdigit()),
            |it: &str| u8::from_str_radix(it, 16),
        )(input)
    }

    pub fn parse_hex_color_no_alpha(input: &str) -> IResult<
        &str, Color, VError
    > {
        let (input, _) = tag("#")(input)?;
        let (input, (red, green, blue)) = tuple((
            parse_single_hex_segment,
            parse_single_hex_segment,
            parse_single_hex_segment,
        ))(input)?;

        Ok((input, Color::NoAlpha(ColorNoAlpha::new(red, green, blue))))
    }

    pub fn parse_hex_color_with_alpha(input: &str) -> IResult<
        &str, Color, VError
    > {
        let (input, _) = tag("#")(input)?;
        let (input, (red, green, blue, alpha)) = tuple((
            parse_single_hex_segment,
            parse_single_hex_segment,
            parse_single_hex_segment,
            parse_single_hex_segment,
        ))(input)?;

        Ok((
            input,
            Color::WithAlpha(
                ColorWithAlpha::new(red, green, blue, alpha)
            ),
        ))
    }
}

/// Parser functions for a style multiline string.
mod style_parser_helper_fns {
    use super::*;

    /// Parse `style = { bg_color: .. , fg_color: .. }` parser.
    pub fn parse_style(
        input: &str,
    ) -> IResult<&str, Option<HashMap<ColorKind, Color>>, VError> {
        // Parse `style = {`.
        let (input, _) = tuple((
            tag("style"),
            multispace0,
            nom::character::complete::char('='),
            multispace0,
            tag("{"),
            multispace0,
        ))(input)?;

        // Parse `bg_color: ..` or `fg_color: ..`.
        let (input, output) = many0(parse_color_key_value)(input)?;

        // Parse `}`.
        let (input, _) = tuple((multispace0, tag("}"), multispace0))(input)?;

        let output = {
            let mut it: HashMap<ColorKind, Color> = HashMap::new();
            for (color_kind, color) in output.iter() {
                it.insert(*color_kind, *color);
            }
            it
        };

        Ok((input, Some(output)))
    }

    /// Parse `<key>: #<val>`, where:
    /// 1. `<key>` can be `fg_color` or `bg_color`.
    /// 2. `<val>` can be `#RRGGBB` or `#RRGGBBAA`.
    pub fn parse_color_key_value(input: &str) -> IResult<
        &str, (ColorKind, Color), VError
    > {
        // Parse `fg_color` or `bg_color`.
        let (input, key_str) = alt((tag("fg_color"), tag("bg_color")))(input)?;

        // Parse `: #RRGGBBAA;` or `: #RRGGBB;`.
        let (input, (_, _, _, output, _, _, _)) = tuple((
            multispace0,
            tag(":"),
            multispace0,
            // The order in which these functions are called matters: first,
            // try to parse `#RRGGBBAA` & if it fails then try to parse
            // `#RRGGBB`.
            alt((parse_hex_color_with_alpha, parse_hex_color_no_alpha)),
            multispace0,
            tag(";"),
            multispace0,
        ))(input)?;

        Ok((input, (ColorKind::from(key_str), output)))
    }
}
```

### Simple natural language parser
<a id="markdown-simple-natural-language-parser" name="simple-natural-language-parser"></a>

Here's a snippet from the [Simple natural language parser
code](https://github.com/nazmulidris/rust-scratch/blob/main/nom/src/parse_natural_lang.rs)
that parses natural language sentences.

The sentences are in this form:
```text
Hello, [my name is <name>] and [i am <age> years old] and [i like <language>]
```
The `and` is optional; it can be omitted or replaced w/ a `,`.

Here are examples of valid sentences:
- `"Hello, my name is Tommaso and i am 32 years old and I like Rust"`
- `"Hello, my name is Roberto and i like Python, I am 44 years old"`
- `"Hello, I like JavaScript my name is Luciano i am 35 years old"`

```rust
/// Functions that can be composed to parse the sentence.
mod parse_sentence {
    use super::*;

    /// Sentence starts w/ "hello". Then optional whitespace.
    /// Then optional ",". Then optional whitespace.
    pub fn root(input: &str) -> IResult</* remainder */ &str, Sentence> {
        let (rem, _) = tuple((
            tag_no_case("hello"),
            multispace0,
            opt(tag(",")), /* cut() also works instead of opt() */
            multispace0,
        ))(input)?;

        // Name, age, and language show up next in any order.
        let (rem, (name, age, language)) =
            permutation((name, age, language))(rem)?;

        Ok((
            rem,
            Sentence {
                name,
                age,
                language,
            },
        ))
    }

    /// Optional whitespace. Then optional "and" or optional ",". Then optional
    /// whitespace.
    pub fn optional_prefix(input: &str) -> IResult<&str, ()> {
        let (rem, _spaces) = multispace0(input)?;
        let (rem, _prefix) = opt(
            alt((
                tag_no_case("and"),
                tag(",")
            ))
        )(rem)?;
        let (rem, _spaces) = multispace0(rem)?;
        Ok((rem, ()))
    }

    /// Age starts w/ optional "and" or ",". Then "i am". Then optional
    /// whitespace. Then age (number).
    pub fn age(input: &str) -> IResult<&str, u8> {
        let (rem, _prefix) = optional_prefix(input)?;
        let (rem, _i_am_with_spaces) = tuple((
            tag_no_case("i am"),
            multispace0
        ))(rem)?;
        let (rem, age) = map_res(digit1, |age: &str| age.parse::<u8>())(rem)?;
        let (rem, _suffix) = tag_no_case(" years old")(rem)?;
        Ok((rem, age))
    }

    /// Name starts w/ optional "and" or ",". Then "my name is". Then optional
    /// whitespace. Then name.
    pub fn name(input: &str) -> IResult<&str, &str> {
        let (rem, _prefix) = optional_prefix(input)?;
        let (rem, _my_name_is_with_spaces) = tuple((
            multispace0,
            tag_no_case("my name is"),
            multispace0
        ))(rem)?;
        let (rem, name) = alpha1(rem)?;
        Ok((rem, name))
    }

    /// Language starts w/ optional "and" or ",". Then "i like". Then optional
    /// whitespace. Then language.
    pub fn language(input: &str) -> IResult<&str, &str> {
        let (rem, _prefix) = optional_prefix(input)?;
        let (rem, _i_like_with_spaces) = tuple((
            tag_no_case("i like"),
            multispace0
        ))(rem)?;
        let (rem, language) = alpha1(rem)?;
        Ok((rem, language))
    }
}
```

## Markdown parser
<a id="markdown-markdown-parser" name="markdown-parser"></a>

You can find a simplified version of the Markdown parser in this
[repo](https://github.com/nazmulidris/rust-scratch/blob/main/nom/src/md_parser/parser.rs). This may
be useful to learn the basics of Markdown parsing before delving into the more complex parser that is
used in `r3bl_tui`.

The production
[`md_parser`](https://github.com/r3bl-org/r3bl-open-core/tree/main/tui/src/tui/md_parser)
module in the `r3bl-open-core` repo contains a fully functional Markdown parser (that you
can use in your projects that need a Markdown parser). This parser supports standard
Markdown syntax as well as some extensions that are
added to make it work w/ [R3BL](https://r3bl.com) products. It makes a great starting
point to study how a relatively complex parser is written. There are lots of tests that
you can follow along to understand what the code is doing.

> 💡 You can get the source code for the production Markdown parser used in `r3bl_tui` from the
> [`r3bl-open-core`](https://github.com/r3bl-org/r3bl-open-core/tree/main/tui/src/tui/md_parser)
> repo.
>
> 🌟 Please star this repo on github if you like it 🙏.

The main entry point (function) for this Markdown parsing module is
[`parse_markdown()`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/parse_markdown.rs).
- It takes a string slice.
- And returns a vector of [`MdBlock`s](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/types.rs).

Here are some entry points into the codebase.

1. The main function
   [`parse_markdown()`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/parse_markdown.rs)
   that does the parsing of a string slice into a
   [`MdDocument`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/types.rs).
   The tests are provided alongside the code itself. And you can follow along to see how
   other smaller parsers are used to build up this big one that parses the whole of the
   Markdown document.
2. The
   [`types`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/types.rs) module
   contain all the types that are used to represent the Markdown document model, such as `MdDocument`, `MdBlock`,
   `MdLineFragment` and all the other intermediate types & enums required for parsing.
3. All the parsers related to parsing metadata specific for [R3BL](https://r3bl.com)
   applications which are not standard Markdown can be found in
   [`parse_metadata_kv`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/extended/parse_metadata_kv.rs#L1)
   and
   [`parse_metadata_kcsv`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/extended/parse_metadata_kcsv.rs#L1).
4. All the parsers that are related to parsing the main "blocks" of Markdown, such as
   order lists, unordered lists, code blocks, text blocks, heading blocks, can be
   found [`block`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/block/mod.rs#L3).
5. All the parsers that are related to parsing a single line of Markdown text, such as
   links, bold, italic, etc. can be found
   [`fragment`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/fragment/mod.rs#L1).

## References
<a id="markdown-references" name="references"></a>

`nom` is a huge topic. This tutorial takes a hands on approach to learning `nom`. However, the resources
listed below are very useful for learning `nom`. Think of them as a reference guide and deep dive into
how the `nom` library works.

- Useful:
  - Source code examples (fantastic way to learn `nom`):
    - [export-logseq-notes repo](https://github.com/dimfeld/export-logseq-notes/tree/master/src)
  - Videos:
    - [Intro from the author 7yrs old](https://youtu.be/EXEMm5173SM)
    - `nom` 7 deep dive videos:
      - [Parsing name, age, and preference from natural language input](https://youtu.be/Igajh2Vliog)
      - [Parsing number ranges](https://youtu.be/Xm4jrjohDN8)
      - [Parsing lines of text](https://youtu.be/6b2ymQWldoE)
    - `nom` 6 videos (deep dive into how nom combinators themselves are constructed):
      - [Deep dive, Part 1](https://youtu.be/zHF6j1LvngA)
      - [Deep dive, Part 2](https://youtu.be/9GLFJcSO08Y)
  - Tutorials:
    - [Build a JSON parser using `nom` 7](https://codeandbitters.com/lets-build-a-parser/)
    - [Excellent beginner to advanced](https://github.com/benkay86/nom-tutorial)
    - [Write a parser from scratch](https://github.com/rust-bakery/nom/blob/main/doc/making_a_new_parser_from_scratch.md)
  - Reference docs:
    - [nominomicon](https://tfpk.github.io/nominomicon/introduction.html)
    - [What combinator or parser to use?](https://github.com/rust-bakery/nom/blob/main/doc/choosing_a_combinator.md)
    - [docs.rs](https://docs.rs/nom/7.1.3/nom/)
    - [Upgrading to `nom` 5.0](https://github.com/rust-bakery/nom/blob/main/doc/upgrading_to_nom_5.md)
- Less useful:
  - [README](https://github.com/rust-bakery/nom)
  - [`nom` crate](https://crates.io/crates/nom)
