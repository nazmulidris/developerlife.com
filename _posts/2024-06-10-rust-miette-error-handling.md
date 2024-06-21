---
title: "Build with Naz : Rust error handling with miette"
author: Nazmul Idris
date: 2024-06-10 15:00:00+00:00
excerpt: |
  miette is an excellent crate that can make error handling in Rust powerful, flexible,
  and easy to use. It provides a way to create custom error types, add context to errors,
  and display errors in a user-friendly way. In this article, we'll explore how to use
  miette to improve error handling in your Rust applications.
layout: post
categories:
  - Rust
  - CLI
  - Server
---

<img class="post-hero-image" src="{{ 'assets/rust-miette.svg' | relative_url }}"/>

<!-- TOC -->

- [Rust error handling primer](#rust-error-handling-primer)
- [More resources on Rust error handling](#more-resources-on-rust-error-handling)
- [YouTube video for this article](#youtube-video-for-this-article)
- [Examples of Rust error handling with miette](#examples-of-rust-error-handling-with-miette)
  - [Example 1: Simple miette usage](#example-1-simple-miette-usage)
  - [Example 2: Complex miette usage](#example-2-complex-miette-usage)
  - [Parting thoughts](#parting-thoughts)
- [Build with Naz video series on developerlife.com YouTube channel](#build-with-naz-video-series-on-developerlifecom-youtube-channel)

<!-- /TOC -->

## Rust error handling primer
<a id="markdown-rust-error-handling-primer" name="rust-error-handling-primer"></a>

Rust has a powerful error handling system that is based on the
[`Result`](https://doc.rust-lang.org/std/result/) and `Option` types. For this tutorial we
will focus on the `Result` type, which is an enum that has two variants: `Ok` and `Err`.
The `Ok` variant is used to represent a successful result, while the `Err` variant is used
to represent an error.

The [`Error`](https://doc.rust-lang.org/std/error/trait.Error.html) trait in Rust has to
be implemented for types that can be used as errors. The `Error` trait has a method called
`source` that returns a reference to the underlying cause of the error. This trait has two
supertraits: `Debug` and `Display`. The `Debug` trait is used to format the error for
debugging purposes (for the operator), while the `Display` trait is used to format the
error for displaying to the user.

The `?` operator can be used in order to propagate errors up the call stack. This operator
is used to unwrap the `Result` type and provide the inner value of the `Ok` variant.
Otherwise it returns from the function with the error, if it is the `Err` variant. This
operator can only be used in functions that return a `Result` type. Here's an example:

```rust
/// Fails and produces output:
/// ```text
/// Error: ParseIntError { kind: InvalidDigit }
/// ```
#[test]
fn test() -> Result<(), Box<dyn std::error::Error>> {
    fn return_error_result() -> Result<u32, std::num::ParseIntError> {
        "1.2".parse::<u32>()
    }

    fn run() -> Result<(), Box<dyn std::error::Error>> {
        // It is as if the `?` is turned into the following code.
        // let result = match result {
        //     Ok(value) => value,
        //     Err(err) => return Err(Box::new(err)),
        // }
        let result = return_error_result()?;

        // The following lines will never be executed, since the previous
        // line will return from the function with an error.
        println!("Result: {}", result);
        Ok(())
    }

    run()?;

    Ok(())
}
```

In the rest of the tutorial (and accompanying video), we will build upon this knowledge
and introduce `miette`, a crate that can make error handling in Rust powerful, flexible,
and easy to use. We will also learn more about the `thiserror` crate, which can be used to
easily create custom error types in Rust.

## More resources on Rust error handling
<a id="markdown-more-resources-on-rust-error-handling" name="more-resources-on-rust-error-handling"></a>

- [`thiserror` crate](https://docs.rs/thiserror/latest/thiserror/).
- [`miette` crate](https://docs.rs/miette/latest/miette/).
- [`Error` trait](https://doc.rust-lang.org/std/error/trait.Error.html).
- [`Result` enum](https://doc.rust-lang.org/std/result/).

## YouTube video for this article
<a id="markdown-youtube-video-for-this-article" name="youtube-video-for-this-article"></a>

This blog post has short examples on how to use `miette` to enhance Rust error handling. If
you like to learn via video, please watch the companion video on the [developerlife.com
YouTube channel](https://www.youtube.com/@developerlifecom).

<!-- rust error handling with miette -->
<iframe
    src="https://www.youtube.com/embed/TmLF7vI8lKk?si=Xh5belp5zD-w-J3P"
    title="YouTube video player"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    referrerpolicy="strict-origin-when-cross-origin"
    allowfullscreen>
</iframe>

<br/>

## Examples of Rust error handling with miette
<a id="markdown-examples-of-rust-error-handling-with-miette" name="examples-of-rust-error-handling-with-miette"></a>

Let's create some examples to illustrate how to use `miette` to enhance Rust error
handling. You can run `cargo new --lib error-miette` to create a new library crate.

> The code in the video and this tutorial are all in [this GitHub
> repo](https://github.com/nazmulidris/rust-scratch/blob/main/error-miette/src/lib.rs).

Then add the following to the `Cargo.toml` file that's generated. These pull in all the
dependencies that we need for these examples.

```toml
[package]
name = "error-miette"
version = "0.1.0"
edition = "2021"

[dependencies]

# Pretty terminal output.
crossterm = "0.27.0"

# Error handling.
thiserror = "1.0.61"
miette = { version = "7.2.0", features = ["fancy"] }
pretty_assertions = "1.4.0"
```

### Example 1: Simple miette usage
<a id="markdown-example-1%3A-simple-miette-usage" name="example-1%3A-simple-miette-usage"></a>

Then you can add the following code to the `src/lib.rs` file. You can note the following things
in the code:
- We define a custom error type called `UnderlyingDatabaseError` using the `thiserror` crate.
- We define a function called `return_error_result` that returns a `Result<u32, std::num::ParseIntError>`.
- We write a test called `test_into_diagnostic` that demonstrates how to use `miette` to
  add context to errors and display them in a user-friendly way. The test also
  demonstrates how to use the `wrap_err` and `context` methods to add context to errors.
  And how they are displayed in the error report (in the inverse order in which they were
  added).
- We also demonstrate how to use the `into_diagnostic` method to convert a `Result` into a
  `miette::Result`.

```rust
#[cfg(test)]
pub mod simple_miette_usage {
    use crossterm::style::Stylize;
    use miette::{Context, IntoDiagnostic};

    #[derive(Debug, thiserror::Error)]
    pub enum UnderlyingDatabaseError {
        #[error("database corrupted")]
        DatabaseCorrupted,
    }

    fn return_error_result() -> Result<u32, std::num::ParseIntError> {
        "1.2".parse::<u32>()
    }

    #[test]
    fn test_into_diagnostic() -> miette::Result<()> {
        let error_result: Result<u32, std::num::ParseIntError> =
            return_error_result();
        assert!(error_result.is_err());

        // The following line will return from this test.
        // let it: u32 = error_result.into_diagnostic()?;

        let new_miette_result: miette::Result<u32> = error_result
            .into_diagnostic()
            .context("🍍 foo bar baz")
            .wrap_err(miette::miette!("custom string error"))
            .wrap_err(std::io::ErrorKind::NotFound)
            .wrap_err(UnderlyingDatabaseError::DatabaseCorrupted)
            .wrap_err("🎃 this is additional context about the failure");

        assert!(new_miette_result.is_err());

        println!(
            "{}:\n{:?}\n",
            "debug output".blue().bold(),
            new_miette_result
        );

        if let Err(ref miette_report) = new_miette_result {
            println!(
                "{}:\n{:?}\n",
                "miette report".red().bold(),
                miette_report.to_string()
            );

            let mut iter = miette_report.chain();

            // First.
            pretty_assertions::assert_eq!(
                iter.next().unwrap().to_string(),
                "🎃 this is additional context about the failure"
                    .to_string()
            );

            // Second.
            pretty_assertions::assert_eq!(
                iter.next().unwrap().to_string(),
                "database corrupted".to_string()
            );

            // Third.
            pretty_assertions::assert_eq!(
                iter.next().unwrap().to_string(),
                "entity not found".to_string()
            );

            // Fourth.
            pretty_assertions::assert_eq!(
                iter.next().unwrap().to_string(),
                "custom string error".to_string()
            );

            // Fifth.
            pretty_assertions::assert_eq!(
                iter.next().unwrap().to_string(),
                "🍍 foo bar baz".to_string()
            );

            // Final.
            pretty_assertions::assert_eq!(
                iter.next().unwrap().to_string(),
                "invalid digit found in string".to_string()
            );
        }

        Ok(())
    }

    #[test]
    fn test_convert_report_into_error() ->
        std::result::Result<(), Box<dyn std::error::Error>> {
        let miette_result: miette::Result<u32> =
            return_error_result()
                .into_diagnostic()
                .wrap_err(miette::Report::msg(
                    "wrapper for the source parse int error",
                ));

        // let converted_result: Result<u32, Box<dyn Error>> =
        //     miette_result.map_err(|report| report.into());

        let converted_result:
            std::result::Result<(), Box<dyn std::error::Error>> =
            match miette_result {
                Ok(_) => Ok(()),
                Err(miette_report) => {
                    let boxed_error: Box<dyn std::error::Error> =
                        miette_report.into();
                    Err(boxed_error)
                }
            };

        println!(
            "{}:\n{:?}\n",
            "debug output".blue().bold(),
            converted_result
        );

        assert!(converted_result.is_err());

        Ok(())
    }
}
```

### Example 2: Complex miette usage
<a id="markdown-example-2%3A-complex-miette-usage" name="example-2%3A-complex-miette-usage"></a>

Next, we will add the following code to the `src/lib.rs` file. You can note the following
things in the code:

- We define a custom error type called `KvStoreError` using the `thiserror` crate.
- We define two variants for the `KvStoreError` enum: `CouldNotCreateDbFolder` and
  `CouldNotGetOrCreateEnvOrOpenStore`. The latter variant has a field called `source` that
  is of type `UnderlyingDatabaseError`, which is defined in the previous example.
- We define two functions called `return_flat_err` and `return_nested_err` that return
  `miette::Result<(), KvStoreError>`.
- We write two tests called `fails_with_flat_err` and `fails_with_nested_err` that
  demonstrate how to use `miette` to add context to errors and display them in a
  user-friendly way. The tests also demonstrate how to use the `from` attribute to convert
  an error of one type into an error of another type.
- We also demonstrate how to use the `#[diagnostic]` attribute to add a code and help URL
  to the error type.
- We also demonstrate how to use the `#[from]` attribute to convert an error of one type
  into an error of another type.
- We also demonstrate how to use the `#[error]` attribute to add a custom error message to
  the error type.

```rust
#[cfg(test)]
pub mod complex_miette_usage {
    use std::error::Error;

    use crate::simple_miette_usage::UnderlyingDatabaseError;
    use pretty_assertions::assert_eq;

    #[derive(thiserror::Error, Debug, miette::Diagnostic)]
    pub enum KvStoreError {
        #[diagnostic(
            code(MyErrorCode::FileSystemError),
            help("https://docs.rs/rkv/latest/rkv/enum.StoreError.html"),
            // url(docsrs) /* Works if this code was on crates.io / docs.rs */
        )]
        #[error("📂 Could not create db folder: '{db_folder_path}' on disk")]
        CouldNotCreateDbFolder { db_folder_path: String },

        #[diagnostic(
            code(MyErrorCode::StoreCreateOrAccessError),
            help("https://docs.rs/rkv/latest/rkv/enum.StoreError.html"),
            // url(docsrs) /* Works if this code was on crates.io / docs.rs */
        )]
        #[error("💾 Could not get or create environment, or open store")]
        CouldNotGetOrCreateEnvOrOpenStore {
            #[from]
            source: UnderlyingDatabaseError,
        },
    }

    fn return_flat_err() -> miette::Result<(), KvStoreError> {
        Result::Err(KvStoreError::CouldNotCreateDbFolder {
            db_folder_path: "some/path/to/db".to_string(),
        })
    }

    /// This test will not run! It will fail and demonstrate the default
    /// [report handler](miette::ReportHandler) of the `miette` crate.
    #[test]
    fn fails_with_flat_err() -> miette::Result<()> {
        let result = return_flat_err();

        if let Err(error) = &result {
            assert_eq!(
                format!("{:?}", error),
                "CouldNotCreateDbFolder { db_folder_path: \"some/path/to/db\" }"
            );
        }

        result?;

        Ok(())
    }

    fn return_nested_err() -> miette::Result<(), KvStoreError> {
        // Variant 1 - Very verbose.
        let store_error = UnderlyingDatabaseError::DatabaseCorrupted;
        let rkv_error = KvStoreError::from(store_error);
        Result::Err(rkv_error)

        // Variant 2.
        // Result::Err(KvStoreError::CouldNotGetOrCreateEnvOrOpenStore {
        //     source: UnderlyingDatabaseError::DatabaseCorrupted,
        // })
    }

    /// This test will not run! It will fail and demonstrate the default
    /// [report handler](miette::ReportHandler) of the `miette` crate.
    #[test]
    fn fails_with_nested_err() -> miette::Result<()> {
        let result = return_nested_err();

        if let Err(error) = &result {
            assert_eq!(
                format!("{:?}", error),
                "CouldNotGetOrCreateEnvOrOpenStore { source: DatabaseCorrupted }"
            );
        }

        result?;

        Ok(())
    }
}
```

### Parting thoughts
<a id="markdown-parting-thoughts" name="parting-thoughts"></a>

For more sophisticated error handling examples, please check out the following links:

- [`terminal_async.rs` in `r3bl_terminal_async`
  crate](https://github.com/r3bl-org/r3bl-open-core/blob/main/terminal_async/src/public_api/terminal_async.rs#L57).
- [`kv.rs` in `tcp-api-server`
  crate](https://github.com/nazmulidris/rust-scratch/blob/main/tcp-api-server/src/standalone/kv.rs#L137).
- [Custom global report handler for `miette` in `tcp-api-server`
  crate](https://github.com/nazmulidris/rust-scratch/blob/main/tcp-api-server/src/standalone/miette_setup_global_report_handler.rs).

## Build with Naz video series on developerlife.com YouTube channel
<a id="markdown-build-with-naz-video-series-on-developerlife.com-youtube-channel" name="build-with-naz-video-series-on-developerlife.com-youtube-channel"></a>

You can watch a video series on building this crate with Naz on the
[developerlife.com YouTube channel](https://www.youtube.com/@developerlifecom).

- [YT channel](https://www.youtube.com/@developerlifecom)
- Playlists
    - [Build with Naz, fundamental effective Rust](https://www.youtube.com/playlist?list=PLofhE49PEwmza94sS7UmJnN9gSCHTVTfz)
    - [Build with Naz, effective async Rust and tokio](https://www.youtube.com/playlist?list=PLofhE49PEwmwO69E7eiQ-ewnMME8ydgQ5)
    - [Build with Naz, async readline and spinner for CLI in Rust](https://www.youtube.com/watch?v=3vQJguti02I&list=PLofhE49PEwmwelPkhfiqdFQ9IXnmGdnSE)
    - [Build with Naz, testing in Rust](https://www.youtube.com/watch?v=Xt495QLrFFk&list=PLofhE49PEwmwLR_4Noa0dFOSPmSpIg_l8)
