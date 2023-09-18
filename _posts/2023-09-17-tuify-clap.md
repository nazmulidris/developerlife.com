---
title: "tuify your clap CLI apps and make them more interactive"
author: Nazmul Idris
date: 2023-09-17 15:00:00+00:00
excerpt: |
  A guide on how to add minimal interactivity to your clap CLI apps using tuify.
  It doesn't have to be an all or nothing approach w/ going full TUI or CLI.
layout: post
categories:
  - Rust
  - CLI
---

<img class="post-hero-image" src="{{ 'assets/tuify-clap-hero.svg' | relative_url }}"/>

<!-- TOC -->

- [Introduction](#introduction)
- [CLI design concepts](#cli-design-concepts)
- [Show me](#show-me)
- [The r3bl_tuify crate and clap](#the-r3bl_tuify-crate-and-clap)
  - [Example 1: Add interactivity using a list selection component](#example-1-add-interactivity-using-a-list-selection-component)
  - [Example 2: Adding interactivity using a text input field](#example-2-adding-interactivity-using-a-text-input-field)
- [Next steps](#next-steps)

<!-- /TOC -->

## Introduction
<a id="markdown-introduction" name="introduction"></a>

As developers we tend to spend a lot of time in the terminal. It is a great place to exercise
precise control over our computers. And it is a great place to automate tasks. However, there are
some rough edges to this experience. For example, even though the interaction metaphor w/ CLI apps
is a conversation, we have to be very precise in the language we use in this conversation. Lots of
trial and error, patience and resilience are required to make it work. And it does not have to be
this way.

To use a racing analogy, terminals are like race cars. They are fast and powerful, and you can
exercise direct and precise control over them. But if you get things wrong, there can be
consequences. Porsche is a car company that
[wins endurance races](https://en.wikipedia.org/wiki/List_of_24_Hours_of_Le_Mans_winners#By_manufacturer),
and a very long time ago, they decided to make a race car that was friendly to the ergonomics of
their drivers.

The thinking was that if the driver is comfortable, they will perform better, and the 24 hour race
wins will be just a little bit closer within reach. Similarly, we can add some interactivity to our
CLI apps to make them more ergonomic to use. And we can do this without going full TUI. We can do
this in a way that is additive to the existing CLI experience. We can "tuify" our CLI apps that are
built using `clap`.

> 🚀 Please star and fork / clone the
> [r3bl_tuify repo](https://github.com/r3bl-org/r3bl_rs_utils/tree/main/tuify) 🌟. We will use this
> repo as an example to learn how to add minimal interactivity to your clap CLI apps
>
> If you would like to get involved in an open source project and like Rust crates, please feel free
> to contribute to the [r3bl_tuify repo](https://github.com/r3bl-org/r3bl_rs_utils/contribute).
> There are a lot of small features that need to be added. And they can be a nice stepping stone
> into the world of open source contribution 🎉.

## CLI design concepts
<a id="markdown-cli-design-concepts" name="cli-design-concepts"></a>

Here are some great resources to learn more about good CLI design concepts. The Rust crate `clap` is
used by a lot of Rust apps to implement this CLI. And in this tutorial we will take a look at how to
add some interactivity to these `clap` CLI apps using the `r3bl_tuify` crate.

> Note that these resources are all about CLI and not TUI. There isn't very much information out
> there about TUIs. It is a new and evolving space.

1. [Command Line Interface Guidelines](https://clig.dev/#foreword)
1. [`clap` docs](https://docs.rs/clap/latest/clap/_derive/#overview)
1. [`clap` command and subcommand structure guidelines](https://rust-cli-recommendations.sunshowers.io/handling-arguments.html)
1. [Hierarchy of configuration](https://rust-cli-recommendations.sunshowers.io/hierarchical-config.html)

The CLI guidelines above do a great job of explaining how to create a good CLI experience. However
they do not cover how to add interactivity to your CLI apps. Why would we want to do this? Let's
take a real example to illustrate the benefits of this next.

## Show me
<a id="markdown-show-me" name="show-me"></a>

This example is a little "meta". The `r3bl_tuify` crate, that allows interactivity to be added to
`clap` CLI apps, is available as a binary and library. The binary which can be used from the command
line (and uses `clap`) uses the library to provide an interactive experience when certain arguments
aren't provided on the command line.

The idea with the binary target is that you might want to quickly incorporate some interactivity
into your shell scripts without getting into the Rust library. In this case, you can use the `rt`
binary target to do that. This binary takes quite a few arguments as you might imagine. However, you
don't have to supply all of them at the start.

So instead of typing this massive command at the start (where `cargo run --` simply runs the binary
called `rt`):

```shell
cat TODO.todo | cargo run -- select-from-list \
    --selection-mode single \
    --command-to-run-with-each-selection "echo %"
```

You can simply type the following shorter command and have the app prompt you for the rest of the
information that it needs:

```shell
cat TODO.todo | cargo run -- select-from-list
```

Here's a video of this in action, where the app is prompting the user for two items:

1. the `selection-mode` and
1. `command-to-run-with-each-selection` interactively 🎉:

<!-- tuify-interactive-happy-path -->
<video width="100%" controls>
  <source src="https://github.com/r3bl-org/r3bl_rs_utils/assets/2966499/51de8867-513b-429f-aff2-63dd25d71c82" type="video/mp4"/>
</video>

## The r3bl_tuify crate and clap
<a id="markdown-the-r3bl_tuify-crate-and-clap" name="the-r3bl_tuify-crate-and-clap"></a>

The `r3bl_tuify` app itself uses `clap` to parse the command line arguments. Here's an overview of
what that looks like (all of it using the `derive` macro approach). Here's a link to the
[`main.rs::AppArgs`](https://github.com/r3bl-org/r3bl_rs_utils/blob/main/tuify/src/main.rs#L30).

```rust
#[derive(Debug, Parser)]
#[command(bin_name = "rt")]
#[command(about = "Easily add lightweight TUI capabilities to any CLI apps using pipes", long_about = None)]
#[command(version)]
#[command(next_line_help = true)]
#[command(arg_required_else_help(true))]
pub struct AppArgs {
    #[clap(subcommand)]
    command: CLICommand,

    #[clap(flatten)]
    global_opts: GlobalOpts,
}

#[derive(Debug, Args)]
struct GlobalOpts {
    /// Print debug output to log file (log.txt)
    #[arg(long, short = 'l')]
    enable_logging: bool,

    /// Optional maximum height of the TUI (rows)
    #[arg(value_name = "height", long, short = 'r')]
    tui_height: Option<usize>,

    /// Optional maximum width of the TUI (columns)
    #[arg(value_name = "width", long, short = 'c')]
    tui_width: Option<usize>,
}

#[derive(Debug, Subcommand)]
enum CLICommand {
    /// Show TUI to allow you to select one or more options from a list, piped in via stdin 👉
    SelectFromList {
        /// Would you like to select one or more items?
        #[arg(value_name = "mode", long, short = 's')]
        selection_mode: Option<SelectionMode>,

        /// Each selected item is passed to this command as `%` and executed in your shell.
        /// For eg: "echo %". Please wrap the command in quotes 💡
        #[arg(value_name = "command", long, short = 'c')]
        command_to_run_with_each_selection: Option<String>,
    },
}
```

The things to note are that the `selection_mode` and `command_to_run_with_each_selection` fields of
the `CliCommand::SelectFromList` enum are optional. This is where the `r3bl_tuify` crate comes in.
It will prompt the user for these two fields if they are not supplied on the command line.

You can add this programmatically using the library to your existing CLI apps.

> The piping option using the binary is severely limited, so the library option is strongly
> recommended. The binary is more of a convenience for shell scripts only on Linux.

You can see how to use the library to perform this interactivity in
[`main.rs::show_tui()`](https://github.com/r3bl-org/r3bl_rs_utils/blob/main/tuify/src/main.rs#L179).

Here are two examples of adding interactivity.

### Example 1: Add interactivity using a list selection component
<a id="markdown-example-1%3A-add-interactivity-using-a-list-selection-component" name="example-1%3A-add-interactivity-using-a-list-selection-component"></a>

Here's an example of adding interactivity using a list selection component. This is useful
when the values that a field can take are known in advance. In this example, they are
since `selection-mode` is a `clap` `EnumValue` that can only take one of the following
values: `single`, or `multiple`.

In this scenario, `--selection-mode` is *not* passed in the command line. So it only
interactively prompts the user for this piece of information. Similarly, if the user does
not provide this information, the app exits and provides a help message.

```shell
cat TODO.todo | cargo run -- select-from-list --command-to-run-with-each-selection "echo %"
```

<!-- tuify-interactive-selection-mode-not-provided -->
<video width="800" controls>
  <source src="https://github.com/r3bl-org/r3bl_rs_utils/assets/2966499/be65d9b2-575b-47c0-8291-110340bd2fe7" type="video/mp4"/>
</video>

```rust
// Handle `selection-mode` is not passed in.
let selection_mode = if let Some(selection_mode) = maybe_selection_mode {
    selection_mode
} else {
    let possible_values_for_selection_mode =
        get_possible_values_for_subcommand_and_option(
            "select-from-list",
            "selection-mode",
        );
    print_help_for_subcommand_and_option("select-from-list", "selection-mode").ok();

    let user_selection = select_from_list(
        "Choose selection-mode".to_string(),
        possible_values_for_selection_mode,
        max_height_row_count,
        max_width_col_count,
        SelectionMode::Single,
    );

    let it = if let Some(user_selection) = user_selection {
        if let Some(it) = user_selection.first() {
            println!("selection-mode: {}", it);
            SelectionMode::from_str(it, true).unwrap_or(SelectionMode::Single)
        } else {
            print_help_for("select-from-list").ok();
            return;
        }
    } else {
        print_help_for("select-from-list").ok();
        return;
    };

    it
};
```

### Example 2: Adding interactivity using a text input field
<a id="markdown-example-2%3A-adding-interactivity-using-a-text-input-field" name="example-2%3A-adding-interactivity-using-a-text-input-field"></a>

Here's an example of adding interactivity using a text input field. This is useful when the values
that a field can take are not known in advance. The `r3bl_tuify` crate uses the `reedline` crate to
do this.

> Fun fact: [`reedline`](https://docs.rs/reedline/) is the text input field (line editor)
> that is used in [`nushell`](https://github.com/nushell/nushell).

In this scenario, `--command-to-run-with-each-selection` is *not* passed in the command
line. So it only interactively prompts the user for this piece of information. Similarly,
if the user does not provide this information, the app exits and provides a help message.

```shell
cat TODO.todo | cargo run -- select-from-list --selection-mode single
```

<!-- tuify-interactive-command-to-run-with-selection-not-provided -->
<video width="800" controls>
  <source src="https://github.com/r3bl-org/r3bl_rs_utils/assets/2966499/d8d7d419-c85e-4c10-bea5-345aa31a92a3" type="video/mp4"/>
</video>

```rust
// Handle `command-to-run-with-each-selection` is not passed in.
let command_to_run_with_each_selection =
    match maybe_command_to_run_with_each_selection {
        Some(it) => it,
        None => {
            print_help_for_subcommand_and_option(
                "select-from-list",
                "command-to-run-with-each-selection",
            )
            .ok();
            let mut line_editor = Reedline::create();
            let prompt = DefaultPrompt {
                left_prompt: DefaultPromptSegment::Basic(
                    "Enter command to run w/ each selection `%`: ".to_string(),
                ),
                right_prompt: DefaultPromptSegment::Empty,
            };

            let sig = line_editor.read_line(&prompt);
            match sig {
                Ok(Signal::Success(buffer)) => {
                    if buffer.is_empty() {
                        print_help_for("select-from-list").ok();
                        return;
                    }
                    println!("Command to run w/ each selection: {}", buffer);
                    buffer
                }
                _ => {
                    print_help_for("select-from-list").ok();
                    return;
                }
            }
        }
    };

// Actually get input from the user.
let selected_items = {
    let it = select_from_list(
        "Select one line".to_string(),
        lines,
        max_height_row_count,
        max_width_col_count,
        selection_mode,
    );
    convert_user_input_into_vec_of_strings(it)
};
```

## Next steps
<a id="markdown-next-steps" name="next-steps"></a>

There are many more components that need to be added to make it easier to "tuify" lots of
existing CLI experiences. Things like multi line editor component w/ syntax highlighting,
scroll view, form input fields, and more. If you would like to contribute to this effort,
it would be great to have your help.

> 🚀 Please star and fork / clone the
> [r3bl_tuify repo](https://github.com/r3bl-org/r3bl_rs_utils/tree/main/tuify) 🌟. We will use this
> repo as an example to learn how to add minimal interactivity to your clap CLI apps
>
> If you would like to get involved in an open source project and like Rust crates, please feel free
> to contribute to the [r3bl_tuify repo](https://github.com/r3bl-org/r3bl_rs_utils/contribute).
> There are a lot of small features that need to be added. And they can be a nice stepping stone
> into the world of open source contribution 🎉.
