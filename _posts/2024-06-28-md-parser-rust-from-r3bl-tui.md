---
title: "Build with Naz : Markdown parser in Rust and nom from r3bl_tui"
author: Nazmul Idris
date: 2024-06-28 15:00:00+00:00
excerpt: |
    This tutorial and video are a deep dive in a real Markdown parser written using nom in Rust.
    This MD Parser is part of the r3bl_tui crate, which is part of the r3bl-open-core
    repo. It goes over the architecture of thinking about building complex parsers
    and the nitty gritty details the runtime nature and behavior when combining
    nom parsers.
layout: post
categories:
  - Rust
  - CLI
  - Server
  - TUI
---

<img class="post-hero-image" src="{{ 'assets/rust-tui-md-parser.svg' | relative_url }}"/>

<!-- TOC -->

- [Introduction](#introduction)
- [nom crate review](#nom-crate-review)
- [A real production grade Markdown parser example](#a-real-production-grade-markdown-parser-example)
- [Related video](#related-video)
- [Architecture and parsing order](#architecture-and-parsing-order)
- [References](#references)

<!-- /TOC -->

## Introduction
<a id="markdown-introduction" name="introduction"></a>

This tutorial, and video are a deep dive in a real Markdown parser written using nom in
Rust. This MD Parser is part of the [`r3bl_tui`](https://crates.io/crates/r3bl_tui) crate,
which is part of the `r3bl-open-core` repo. It goes over the architecture of thinking
about building complex parsers and the nitty gritty details the runtime nature and
behavior when combining nom parsers.

The [`r3bl_tui`](https://crates.io/crates/r3bl_tui) crate is a Text User Interface (TUI)
crate that is used in the [R3BL](https://r3bl.com) suite of products. It is a very
powerful and flexible TUI crate that is used to build a variety of different applications.
It comes with a full featured Markdown editor component, and the parser that's the focus
on this tutorial is used by that editor component to parse an input string slice into a
Markdown document model (AST representation in memory).

## nom crate review
<a id="markdown-nom-crate-review" name="nom-crate-review"></a>

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

> We have a video and article on developerlife where you can learn more about `nom` and how to use it.
> - [Video on nom fundamentals](https://youtu.be/v3tMwr_ysPg).
> - [Article on nom fundamentals](https://developerlife.com/2023/02/20/guide-to-nom-parsing/).

## A real production grade Markdown parser example
<a id="markdown-a-real-production-grade-markdown-parser-example" name="a-real-production-grade-markdown-parser-example"></a>

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

## Related video
<a id="markdown-related-video" name="related-video"></a>

If you like to consume content via video, then you can watch this video that covers the same content
as this article, but in a live coding format.

<!-- video on nom -->
<iframe
    src="https://www.youtube.com/embed/SbwvSHZRb1E?si=8UFyEKyF8sHnam-K"
    title="YouTube video player" frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    referrerpolicy="strict-origin-when-cross-origin"
    allowfullscreen
    >
</iframe>

> 💡 You can get the source code for the production Markdown parser used in `r3bl_tui` from the
> [`r3bl-open-core`](https://github.com/r3bl-org/r3bl-open-core/tree/main/tui/src/tui/md_parser)
> repo.

## Architecture and parsing order
<a id="markdown-architecture-and-parsing-order" name="architecture-and-parsing-order"></a>

This diagram showcases the order in which the parsers are called and how they are
composed together to parse a Markdown document.

<!--
diagram:
https://asciiflow.com/#/share/eJzdlL9qwzAQxl%2Fl0JRChhLo0Gz9M3Rop2YUCNUWsYgsGfkcxxhD6dyhQwh9ltKnyZNUtus0hAYrJaXQQyAZf%2F6d7rN0JdE8FmSsM6WGRPFCWDImJSULSsbnZ6MhJYVbjZoVigW6B0oSK42VWMB6%2BbxePv7T8UKpBojkNAJwlT5Bwm0qWMztLDS5HpxACTsR8wTQAEYCAmOtCHBX0aIacgvdTDHXxengG3331U8LWb0B3IWXygQzmHMrucZ9e4DPGlGiEmzOVSZcmb0xqeV99W3YfJoyJVP0ITu2k%2Fd617F5hpGx3viLVu7HDjkeYAlcO7n3vh%2Fqn8MiwUOpp8wkyIRR%2B9PctMJD2Kk7tujjy30tvHU6f3ZgQj9PrpywPYfe7O62sbr5sFxixIxtZpMh0yJ3Nek6%2B8S9%2F8q0h%2B114vpii71679jVMcgde6u%2FLv%2B6C%2F7eeG1cVCY%2FjnVdUFKR6gNnN4sV)
-->

```text
priority ┌────────────────────────────────────────────────────────────────────┐
  high   │ parse_markdown() {           map to the correct                    │
    │    │   many0(                     ───────────────────►  MdBlock variant │
    │    │     parse_title_value()                              Title         │
    │    │     parse_tags_list()                                Tags          │
    │    │     parse_authors_list()                             Authors       │
    │    │     parse_date_value()                               Date          │
    │    │     parse_block_heading_opt_eol()                    Heading       │
    │    │     parse_block_smart_list()                         SmartList     │
    │    │     parse_block_code()                               CodeBlock     │
    │    │     parse_block_m..n_text_with_or_without_new_line() Text          │
    │    │   )                                                                │
    ▼    │ }                                                                  │
priority └────────────────────────────────────────────────────────────────────┘
  low
```

The parsing strategy in most cases is to parse the most specific thing first and then
parse the more general thing later. We often use the existence of `\n` (or `eol`) to
decide how far forwards we need to go into the input. And sometimes `\n` doesn't exist
and we simply use the entire input (or end of input or `eoi`). You might see functions
that have these suffixes in their names. Another term you might see is
`with_or_without_new_line` which makes the parsing strategy explicit in the name.

The nature of `nom` parsers is to simply error out when they don't match. And leave
the `input` untouched, so that another parser have a go at it again. The nature of
these parsing functions is kind of recursive in nature. So it's important identify
edge and exit cases up front before diving into the parsing logic. You will see this
used in parsers which look for something more specific, if its not found, they error
out, and allow less specific parsers to have a go at it, and so on.

## The priority of parsers

As we drill down into the implementation further, we see that the parsers are
prioritized in the order of their specificity. The most specific parsers are called
first and the least specific parsers are called last. This is done to ensure that the
most specific parsers get a chance to parse the input first. And if they fail, then
the less specific parsers get a chance to parse the input.

<!--
diagram:
https://asciiflow.com/#/share/eJytlFFuwjAMhq8S5QkkHtD2MjhLJCsNBqK6CUpTUYaQpp2h4iB7RDtNT7I0sK1ABYNhVapdJ1%2F%2F2G7X3MgM%2BdgURANOcoWOj%2Fla8FLw8ejleSD4KnhPo2HwPJY%2BBIIvpMsRErIqhUy6dGKXBposLLWfg3XxbgsPBpdA2mCvz9bs3IQwjGXSrIa9juxtFlmM7bVp07wVpk7OMjQ%2Bh8J4TYCWGnVodRB0nRWsWVZX7%2F9VtvmNHkBrRXVV1dVbvd0xSf7OIh4TI3X7cSjkdwUh99KFOsYGF2aCLlfWIaBzYE27zx20cOILtMbv4LS05QtUWpJ%2BxclVWiJV6nUYzC5ipMXNLmdN3X6u7e4Kl3DqQWdy9pAzR1rY3CnzZpqao0oTW4ax9zZkXHu6u7r7%2BSfaMTaxlnr9SFPSq3kYODop4Sl1QVIffgzGnvf2ROO%2BL4cnFz%2FPiyb4hm%2B%2BAFpUbMk%3D)
-->

```text
parse_block_markdown_text_with_or_without_new_line() {
  many0(
    parse_inline_fragments_until_eol_or_eoi()
       )   │
}          │                                           ──map to the correct──►
           └─► alt(                                     MdLineFragment variant

             ▲ p..e_f..t_s..s_with_underscore_err_on_new_line()  Italic
             │ p..e_f..t_s..s_with_star_err_on_new_line()        Bold
specialized  │ p..e_f..t_s..s_with_backtick_err_on_new_line()    InlineCode
parsers ────►│ p..e_f..t_s..s_with_left_image_err_on_new_line()  Image
             │ p..e_f..t_s..s_with_left_link_err_on_new_line()   Link
             │ p..e_f..t_s..s_with_checkbox_into_str()           Plain
             ▼ p..e_f..t_s..s_with_checkbox_checkbox_into_bool() Checkbox
catch all────► p..e_f..t_plain_text_no_new_line()                Plain
parser
               )
```

The last one on the list in the diagram above is
[`parse_block_markdown_text_with_or_without_new_line()`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/block/parse_block_markdown_text_until_eol_or_eoi.rs).
Let's zoom into this function and see how it is composed.

## The "catch all" parser, which is the most complicated, and the lowest priority

The most complicated parser is the "catch all" parser or the "plain text" parser. This
parser is the last one in the chain and it simply consumes the rest of the input and
turns it into a `MdBlock::Text`. This parser is the most complicated because it has to
deal with all the edge cases and exit cases that other parsers have not dealt with.
Such as special characters like `` ` ``, `*`, `_`, etc. They are all listed here:

- If the input does not start with a special char in this
  [`get_sp_char_set_2()`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/fragment/plain_parser_catch_all.rs),
  then this is the "Normal case". In this case the input is split at the first occurrence
  of a special char in
  [`get_sp_char_set_3()`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/fragment/plain_parser_catch_all.rs).
  The "before" part is `MdLineFragment::Plain` and the "after" part is parsed again by a
  more specific parser.
- If the input starts with a special char in this [`get_sp_char_set_2()`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/fragment/plain_parser_catch_all.rs) and it is not
  in the `get_sp_char_set_1()` with only 1 occurrence, then the behavior is different
  "Edge case -> Normal case". Otherwise the behavior is "Edge case -> Special case".
  - "Edge case -> Normal case" takes all the characters until `\n` or end of input and
    turns it into a `MdLineFragment::Plain`.
  - "Edge case -> Special case" splits the `input` before and after the special char.
    The "before" part is turned into a `MdLineFragment::Plain` and the "after" part is
    parsed again by a more specific parser.

The reason this parser gets called repeatedly is because it is the last one in the chain.
Its the lowest priority parser called by
[`parse_inline_fragments_until_eol_or_eoi()`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/fragment/parse_fragments_in_a_line.rs),
which itself is called:
1. Repeatedly in a loop by
   [`parse_block_markdown_text_with_or_without_new_line()`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/block/parse_block_markdown_text_until_eol_or_eoi.rs).
2. And by
   [`parse_block_markdown_text_with_checkbox_policy_with_or_without_new_line()`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/block/parse_block_markdown_text_until_eol_or_eoi.rs#L80).

## Visualize the parsers running on real input

Let's run some tests from the `md_parser` module with the
[`DEBUG_MD_PARSER_STDOUT`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/mod.rs#L34)
flag set to `true`.

This will allow us to see the output of the parsers as they run on
real input. This is a great way to understand how the parsers are working and what they
are doing. This helps build an intuition around what happens at runtime which might not
match what you think is happening when you read the code.

1. The test we will run are in this file:
   [`tui/src/tui/md_parser/block/parse_block_markdown_text_until_eol_or_eoi.rs`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/block/parse_block_markdown_text_until_eol_or_eoi.rs#L81).
2. The test suite itself is called
   `tests_parse_block_markdown_text_with_or_without_new_line`.
3. And the function under test is
   [`parse_block_markdown_text_with_or_without_new_line()`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/block/parse_block_markdown_text_until_eol_or_eoi.rs#L24).

For convenience, here's a copy of the test that we will run (in this
[file](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/md_parser/block/parse_block_markdown_text_until_eol_or_eoi.rs#L101)):

```rust
#[test]
fn test_parse_hyperlink_markdown_text_1() {
    let input = "This is a _hyperlink: [foo](http://google.com).";
    let it = parse_block_markdown_text_with_or_without_new_line(input);
    assert_eq2!(
        it,
        Ok((
            "",
            list![
                MdLineFragment::Plain("This is a ",),
                MdLineFragment::Plain("_",),
                MdLineFragment::Plain("hyperlink: ",),
                MdLineFragment::Link(HyperlinkData {
                    text: "foo",
                    url: "http://google.com",
                },),
                MdLineFragment::Plain(".",),
            ],
        ))
    );
}
```

You can see from the `assert_eq2!()` statements that the input `"This is a _hyperlink:
[foo](http://google.com)."` is turned into a abstract syntax tree (AST) which looks like
this:

```rust
[
    MdLineFragment::Plain("This is a ",),
    MdLineFragment::Plain("_",),
    MdLineFragment::Plain("hyperlink: ",),
    MdLineFragment::Link(HyperlinkData {
        text: "foo",
        url: "http://google.com",
    },),
    MdLineFragment::Plain(".",),
]
```

Note the "strange" way in which `"_"` is handled. Instead of what we might expect `Plain("This is a _ hyperlink: ")`.
But we get 3 fragments instead of one. This is because of the lowest priority parser handles special characters
so that more specific parsers (higher priority) can have a go at it. So it doesn't prematurely mark them as `Plain`.

Here are the commands to run one of the tests (make sure to run this in the `tui` subfolder):

<pre class="pre-manual-highlight">
<span style="color:#F8F8F2">cargo</span> <span style="color:#FF79C6">test</span> <span style="color:#FF79C6">--</span> <span style="color:#FF79C6">--nocapture</span> <span style="color:#FF79C6">test_parse_hyperlink_markdown_text_1</span>
</pre>

Here's the output, which you can walk through to see the parsing algorithms in action:

<pre class="pre-manual-highlight">
<span style="color:#A3BE8C">■■</span> specialized parser _:
input: &quot;This is a _hyperlink: [foo](http://google.com).&quot;, delim: &quot;_&quot;
count: 1, starts_w: false, input=delim: false
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;This is a _hyperlink: [foo](http://google.com).&quot;

<span style="color:#A3BE8C">■■</span> specialized parser *:
input: &quot;This is a _hyperlink: [foo](http://google.com).&quot;, delim: &quot;*&quot;
count: 0, starts_w: false, input=delim: false
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;This is a _hyperlink: [foo](http://google.com).&quot;

<span style="color:#A3BE8C">■■</span> specialized parser `:
input: &quot;This is a _hyperlink: [foo](http://google.com).&quot;, delim: &quot;`&quot;
count: 0, starts_w: false, input=delim: false
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;This is a _hyperlink: [foo](http://google.com).&quot;

<span style="color:#A3BE8C">■■</span> specialized parser take text between delims err on new line:
input: &quot;This is a _hyperlink: [foo](http://google.com).&quot;, start_delim: &quot;![&quot;, end_delim: &quot;]&quot;
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;This is a _hyperlink: [foo](http://google.com).&quot;

<span style="color:#BF616A">⬢⬢</span> specialized parser error out with image:
input: &quot;This is a _hyperlink: [foo](http://google.com).&quot;, delim: &quot;![&quot;

<span style="color:#A3BE8C">■■</span> specialized parser take text between delims err on new line:
input: &quot;This is a _hyperlink: [foo](http://google.com).&quot;, start_delim: &quot;[&quot;, end_delim: &quot;]&quot;
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;This is a _hyperlink: [foo](http://google.com).&quot;

<span style="color:#BF616A">⬢⬢</span> specialized parser error out with link:
input: &quot;This is a _hyperlink: [foo](http://google.com).&quot;, delim: &quot;[&quot;
<span style="color:#BF616A">⬢⬢</span> specialized parser for checkbox: Err(Error(Error { input: &quot;This is a _hyperlink: [foo](http://google.com).&quot;, code: Tag }))

<span style="color:#B48EAD">██</span> plain parser, input: &quot;This is a _hyperlink: [foo](http://google.com).&quot;
<span style="color:#81A1C1">▲▲</span> normal case :: Ok((&quot;_hyperlink: [foo](http://google.com).&quot;, &quot;This is a &quot;))

<span style="color:#A3BE8C">■■</span> specialized parser _:
input: &quot;_hyperlink: [foo](http://google.com).&quot;, delim: &quot;_&quot;
count: 1, starts_w: true, input=delim: false
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;_hyperlink: [foo](http://google.com).&quot;

<span style="color:#A3BE8C">■■</span> specialized parser *:
input: &quot;_hyperlink: [foo](http://google.com).&quot;, delim: &quot;*&quot;
count: 0, starts_w: false, input=delim: false
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;_hyperlink: [foo](http://google.com).&quot;

<span style="color:#A3BE8C">■■</span> specialized parser `:
input: &quot;_hyperlink: [foo](http://google.com).&quot;, delim: &quot;`&quot;
count: 0, starts_w: false, input=delim: false
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;_hyperlink: [foo](http://google.com).&quot;

<span style="color:#A3BE8C">■■</span> specialized parser take text between delims err on new line:
input: &quot;_hyperlink: [foo](http://google.com).&quot;, start_delim: &quot;![&quot;, end_delim: &quot;]&quot;
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;_hyperlink: [foo](http://google.com).&quot;

<span style="color:#BF616A">⬢⬢</span> specialized parser error out with image:
input: &quot;_hyperlink: [foo](http://google.com).&quot;, delim: &quot;![&quot;

<span style="color:#A3BE8C">■■</span> specialized parser take text between delims err on new line:
input: &quot;_hyperlink: [foo](http://google.com).&quot;, start_delim: &quot;[&quot;, end_delim: &quot;]&quot;
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;_hyperlink: [foo](http://google.com).&quot;

<span style="color:#BF616A">⬢⬢</span> specialized parser error out with link:
input: &quot;_hyperlink: [foo](http://google.com).&quot;, delim: &quot;[&quot;
<span style="color:#BF616A">⬢⬢</span> specialized parser for checkbox: Err(Error(Error { input: &quot;_hyperlink: [foo](http://google.com).&quot;, code: Tag }))

<span style="color:#B48EAD">██</span> plain parser, input: &quot;_hyperlink: [foo](http://google.com).&quot;
<span style="color:#81A1C1">▲▲</span> edge case -&gt; special case :: rem: &quot;hyperlink: [foo](http://google.com).&quot;, output: &quot;_&quot;

<span style="color:#A3BE8C">■■</span> specialized parser _:
input: &quot;hyperlink: [foo](http://google.com).&quot;, delim: &quot;_&quot;
count: 0, starts_w: false, input=delim: false
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;hyperlink: [foo](http://google.com).&quot;

<span style="color:#A3BE8C">■■</span> specialized parser *:
input: &quot;hyperlink: [foo](http://google.com).&quot;, delim: &quot;*&quot;
count: 0, starts_w: false, input=delim: false
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;hyperlink: [foo](http://google.com).&quot;

<span style="color:#A3BE8C">■■</span> specialized parser `:
input: &quot;hyperlink: [foo](http://google.com).&quot;, delim: &quot;`&quot;
count: 0, starts_w: false, input=delim: false
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;hyperlink: [foo](http://google.com).&quot;

<span style="color:#A3BE8C">■■</span> specialized parser take text between delims err on new line:
input: &quot;hyperlink: [foo](http://google.com).&quot;, start_delim: &quot;![&quot;, end_delim: &quot;]&quot;
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;hyperlink: [foo](http://google.com).&quot;

<span style="color:#BF616A">⬢⬢</span> specialized parser error out with image:
input: &quot;hyperlink: [foo](http://google.com).&quot;, delim: &quot;![&quot;

<span style="color:#A3BE8C">■■</span> specialized parser take text between delims err on new line:
input: &quot;hyperlink: [foo](http://google.com).&quot;, start_delim: &quot;[&quot;, end_delim: &quot;]&quot;
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;hyperlink: [foo](http://google.com).&quot;

<span style="color:#BF616A">⬢⬢</span> specialized parser error out with link:
input: &quot;hyperlink: [foo](http://google.com).&quot;, delim: &quot;[&quot;
<span style="color:#BF616A">⬢⬢</span> specialized parser for checkbox: Err(Error(Error { input: &quot;hyperlink: [foo](http://google.com).&quot;, code: Tag }))

<span style="color:#B48EAD">██</span> plain parser, input: &quot;hyperlink: [foo](http://google.com).&quot;
<span style="color:#81A1C1">▲▲</span> normal case :: Ok((&quot;[foo](http://google.com).&quot;, &quot;hyperlink: &quot;))

<span style="color:#A3BE8C">■■</span> specialized parser _:
input: &quot;[foo](http://google.com).&quot;, delim: &quot;_&quot;
count: 0, starts_w: false, input=delim: false
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;[foo](http://google.com).&quot;

<span style="color:#A3BE8C">■■</span> specialized parser *:
input: &quot;[foo](http://google.com).&quot;, delim: &quot;*&quot;
count: 0, starts_w: false, input=delim: false
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;[foo](http://google.com).&quot;

<span style="color:#A3BE8C">■■</span> specialized parser `:
input: &quot;[foo](http://google.com).&quot;, delim: &quot;`&quot;
count: 0, starts_w: false, input=delim: false
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;[foo](http://google.com).&quot;

<span style="color:#A3BE8C">■■</span> specialized parser take text between delims err on new line:
input: &quot;[foo](http://google.com).&quot;, start_delim: &quot;![&quot;, end_delim: &quot;]&quot;
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;[foo](http://google.com).&quot;

<span style="color:#BF616A">⬢⬢</span> specialized parser error out with image:
input: &quot;[foo](http://google.com).&quot;, delim: &quot;![&quot;

<span style="color:#A3BE8C">■■</span> specialized parser take text between delims err on new line:
input: &quot;[foo](http://google.com).&quot;, start_delim: &quot;[&quot;, end_delim: &quot;]&quot;

<span style="color:#A3BE8C">■■</span> specialized parser take text between delims err on new line:
input: &quot;(http://google.com).&quot;, start_delim: &quot;(&quot;, end_delim: &quot;)&quot;
<span style="color:#81A1C1">▲▲</span> specialized parser for link: Ok((&quot;.&quot;, HyperlinkData { text: &quot;foo&quot;, url: &quot;http://google.com&quot; }))

<span style="color:#A3BE8C">■■</span> specialized parser _:
input: &quot;.&quot;, delim: &quot;_&quot;
count: 0, starts_w: false, input=delim: false
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;.&quot;

<span style="color:#A3BE8C">■■</span> specialized parser *:
input: &quot;.&quot;, delim: &quot;*&quot;
count: 0, starts_w: false, input=delim: false
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;.&quot;

<span style="color:#A3BE8C">■■</span> specialized parser `:
input: &quot;.&quot;, delim: &quot;`&quot;
count: 0, starts_w: false, input=delim: false
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;.&quot;

<span style="color:#A3BE8C">■■</span> specialized parser take text between delims err on new line:
input: &quot;.&quot;, start_delim: &quot;![&quot;, end_delim: &quot;]&quot;
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;.&quot;

<span style="color:#BF616A">⬢⬢</span> specialized parser error out with image:
input: &quot;.&quot;, delim: &quot;![&quot;

<span style="color:#A3BE8C">■■</span> specialized parser take text between delims err on new line:
input: &quot;.&quot;, start_delim: &quot;[&quot;, end_delim: &quot;]&quot;
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;.&quot;

<span style="color:#BF616A">⬢⬢</span> specialized parser error out with link:
input: &quot;.&quot;, delim: &quot;[&quot;
<span style="color:#BF616A">⬢⬢</span> specialized parser for checkbox: Err(Error(Error { input: &quot;.&quot;, code: Tag }))

<span style="color:#B48EAD">██</span> plain parser, input: &quot;.&quot;
<span style="color:#81A1C1">▲▲</span> normal case :: Ok((&quot;&quot;, &quot;.&quot;))

<span style="color:#A3BE8C">■■</span> specialized parser _:
input: &quot;&quot;, delim: &quot;_&quot;
count: 0, starts_w: false, input=delim: false
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;&quot;

<span style="color:#A3BE8C">■■</span> specialized parser *:
input: &quot;&quot;, delim: &quot;*&quot;
count: 0, starts_w: false, input=delim: false
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;&quot;

<span style="color:#A3BE8C">■■</span> specialized parser `:
input: &quot;&quot;, delim: &quot;`&quot;
count: 0, starts_w: false, input=delim: false
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;&quot;

<span style="color:#A3BE8C">■■</span> specialized parser take text between delims err on new line:
input: &quot;&quot;, start_delim: &quot;![&quot;, end_delim: &quot;]&quot;
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;&quot;

<span style="color:#BF616A">⬢⬢</span> specialized parser error out with image:
input: &quot;&quot;, delim: &quot;![&quot;

<span style="color:#A3BE8C">■■</span> specialized parser take text between delims err on new line:
input: &quot;&quot;, start_delim: &quot;[&quot;, end_delim: &quot;]&quot;
<span style="color:#BF616A">⬢⬢</span> parser error out for input: &quot;&quot;

<span style="color:#BF616A">⬢⬢</span> specialized parser error out with link:
input: &quot;&quot;, delim: &quot;[&quot;
<span style="color:#BF616A">⬢⬢</span> specialized parser for checkbox: Err(Error(Error { input: &quot;&quot;, code: Tag }))

<span style="color:#B48EAD">██</span> plain parser, input: &quot;&quot;
<span style="color:#BF616A">⬢⬢</span> normal case :: Err(Error(Error { input: &quot;&quot;, code: Eof }))
</pre>

## See this in action in r3bl-cmdr

If you want to use a TUI app that uses this Markdown Parser, run the following commands:

```sh
cargo install r3bl-cmdr
edi --help
```

This will install the `r3bl-cmdr` binary and run `edi`, which is a TUI Markdown editor
that you can use on any OS (Mac, Windows, Linux).

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
