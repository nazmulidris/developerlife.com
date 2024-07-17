---
title:
  "Build with Naz : Rust typestate pattern"
author: Nazmul Idris
date: 2024-05-28 15:00:00+00:00
excerpt: |
  The Typestate Pattern in Rust is a way to manage objects that go through different states
  in their lifecycle. It leverages Rust's powerful type system to enforce these states and
  transitions between them, making your code safer and more predictable. Learn all about it
  in this article, its video, and repo.
layout: post
categories:
  - Rust
  - CLI
  - Server
---

<img class="post-hero-image" src="{{ 'assets/rust-typestate-pattern.svg' | relative_url }}"/>

<!-- TOC -->

- [What is the typestate pattern?](#what-is-the-typestate-pattern)
- [More resources on typestate pattern and others in Rust](#more-resources-on-typestate-pattern-and-others-in-rust)
- [YouTube video for this article](#youtube-video-for-this-article)
- [Examples of typestate pattern in Rust](#examples-of-typestate-pattern-in-rust)
  - [Example 1: Simple version of this is using enums to encapsulate states as variants](#example-1-simple-version-of-this-is-using-enums-to-encapsulate-states-as-variants)
  - [Example 2: Slightly more complex versions are where one type + data = another type](#example-2-slightly-more-complex-versions-are-where-one-type--data--another-type)
  - [Example 3: Best of both worlds, using generics and struct / enum with a marker trait](#example-3-best-of-both-worlds-using-generics-and-struct--enum-with-a-marker-trait)
  - [Example 3.1: Using enum and PhantomData instead of struct](#example-31-using-enum-and-phantomdata-instead-of-struct)
  - [Parting thoughts](#parting-thoughts)
- [Build with Naz video series on developerlife.com YouTube channel](#build-with-naz-video-series-on-developerlifecom-youtube-channel)

<!-- /TOC -->

## What is the typestate pattern?
<a id="markdown-what-is-the-typestate-pattern%3F" name="what-is-the-typestate-pattern%3F"></a>

The Typestate Pattern in Rust is a way to manage objects that go through different states
in their lifecycle. It leverages Rust's powerful type system to enforce these states and
transitions between them, making your code safer and more predictable. Learn all about it
in this article, its video, and repo.

Here are the key ideas behind the Typestate Pattern:

- *States as structs*: Each possible state of the object is represented by a separate
  struct. This lets you associate specific methods and data with each state.
- *Transitions with ownership*: Methods that transition the object to a new state consume
  the old state and return a value representing the new state. Rust's ownership system
  ensures you can't accidentally use the object in an invalid state.
- *Encapsulated functionality*: Methods are only available on the structs representing the
  valid states. This prevents you from trying to perform actions that aren't allowed in
  the current state.

Benefits of using the Typestate Pattern:

- *Safer code*: By statically checking types at compile time, the compiler prevents you from
  accidentally using the object in an invalid state. This leads to fewer runtime errors
  and more robust code.
- *Improved readability*: The code becomes more self-documenting because the valid state
  transitions are encoded in the types themselves.
- *Clearer APIs*: By separating functionality based on state, APIs become more intuitive and
  easier to understand.

## More resources on typestate pattern and others in Rust
<a id="markdown-more-resources-on-typestate-pattern-and-others-in-rust" name="more-resources-on-typestate-pattern-and-others-in-rust"></a>

- [Functional typed design patterns](https://arxiv.org/pdf/2307.07069).
- [Enums and typestate (and limitations)](https://gemini.google.com/app/5bd7fed51858cb4d).
- [Type-Driven API Design in Rust](https://willcrichton.net/rust-api-type-patterns/typestate.html).
- [Rust typestate notes](https://ruk.si/notes/rust/typestate/).
- [Rusty Typestates - Starting Out](https://rustype.github.io/notes/notes/rust-typestate-series/rust-typestate-part-1).
- [The Embedded Rust Book - Typestate programming](https://docs.rust-embedded.org/book/static-guarantees/typestate-programming.html).
- [Typestates in Rust](https://yoric.github.io/post/rust-typestate/).

## YouTube video for this article
<a id="markdown-youtube-video-for-this-article" name="youtube-video-for-this-article"></a>

This blog post has short examples on how to use the typestate pattern in Rust. If you like
to learn via video, please watch the companion video on the [developerlife.com YouTube
channel](https://www.youtube.com/@developerlifecom).

<!-- rust typestate pattern -->
<iframe
    src="https://www.youtube.com/embed/FTSb0dyDOCA?si=ZdUYIxxGTsaAC1B3"
    title="YouTube video player"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    referrerpolicy="strict-origin-when-cross-origin"
    allowfullscreen>
</iframe>

<br/>

## Examples of typestate pattern in Rust
<a id="markdown-examples-of-typestate-pattern-in-rust" name="examples-of-typestate-pattern-in-rust"></a>

Let's create some examples to illustrate how to use the typestate pattern in Rust. You can run
`cargo new --bin typestate-pattern` to create a new binary crate.

> The code in the video and this tutorial are all in [this GitHub
> repo](https://github.com/nazmulidris/rust-scratch/blob/main/typestate-pattern/).

Then add the following to the `Cargo.toml` file that's generated. These pull in all the
dependencies that we need for these examples.

```toml
[package]
name = "typestate-pattern"
version = "0.1.0"
edition = "2021"

[[bin]]
name = "ex1"
path = "src/ex1.rs"

[[bin]]
name = "ex2"
path = "src/ex2.rs"

[[bin]]
name = "ex3"
path = "src/ex3.rs"

[[bin]]
name = "ex3_1"
path = "src/ex3_1.rs"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
crossterm = { version = "0.27.0", features = ["event-stream"] }
```

### Example 1: Simple version of this is using enums to encapsulate states as variants
<a id="markdown-example-1%3A-simple-version-of-this-is-using-enums-to-encapsulate-states-as-variants" name="example-1%3A-simple-version-of-this-is-using-enums-to-encapsulate-states-as-variants"></a>

Then you can add the following code to the `src/ex1.rs` file.

```rust
#[derive(Debug)]
pub enum InputEvent {
    Keyboard((KeyPress, Option<Vec<Modifier>>)),
    Resize(Size),
    Mouse(MouseEvent),
}

#[derive(Debug)]
pub enum Modifier {
    Shift,
    Control,
    Alt,
}

#[derive(Debug)]
pub enum KeyPress {
    Char(char),
    Enter,
    Backspace,
    Delete,
    Left,
    Right,
    Up,
    Down,
    Home,
    End,
    PageUp,
    PageDown,
    Tab,
    F(u8),
}

#[derive(Debug)]
pub enum Size {
    Height(u16),
    Width(u16),
}

#[derive(Debug)]
pub enum MouseEvent {
    Press(MouseButton, u16, u16),
    Release(u16, u16),
    Hold(u16, u16),
}

#[derive(Debug)]
pub enum MouseButton {
    Left,
    Right,
    Middle,
}

impl InputEvent {
    pub fn pretty_print(&self) {
        let it = match self {
            InputEvent::Keyboard((keypress, modifiers)) => {
                let mut result = format!("{:?}", keypress);
                if let Some(modifiers) = modifiers {
                    result.push_str(&format!("{:?}", modifiers));
                }
                result
            }
            InputEvent::Resize(size) => format!("{:?}", size),
            InputEvent::Mouse(mouse_event) => format!("{:?}", mouse_event),
        };
        println!("{}", it);
    }
}

fn main() {
    let a_pressed = InputEvent::Keyboard((KeyPress::Char('a'), None));
    println!("{:?}", a_pressed);

    let ctrl_c_pressed = InputEvent::Keyboard(
        (KeyPress::Char('c'), Some(vec![Modifier::Control]))
    );
    println!("{:?}", ctrl_c_pressed);

    let enter_pressed = InputEvent::Keyboard((KeyPress::Enter, None));
    enter_pressed.pretty_print();

    let mouse_pressed = InputEvent::Mouse(
        MouseEvent::Press(MouseButton::Left, 10, 20)
    );
    mouse_pressed.pretty_print();
}
```

> The code for this example is
> [here](https://github.com/nazmulidris/rust-scratch/blob/main/typestate-pattern/src/ex1.rs).
> Here's the code for the real
> [`InputEvent`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/terminal_lib_backends/input_event.rs).

The main things to note about this code.

- We have a bunch of enums that represent different types of input events.
- We have a method on the `InputEvent` enum that pretty prints the event for all variants.
  We don't have a way to restrict methods on a specific variant using this approach.

When you run this code (using `cargo run --bin ex1`), it should produce the following
output:

<pre class="pre-manual-highlight">$ cargo run --bin ex1
Keyboard((Char('a'), None))
Keyboard((Char('c'), Some([Control])))
Enter
Press(Left, 10, 20)
</pre>

### Example 2: Slightly more complex versions are where one type + data = another type
<a id="markdown-example-2%3A-slightly-more-complex-versions-are-where-one-type-%2B-data-%3D-another-type" name="example-2%3A-slightly-more-complex-versions-are-where-one-type-%2B-data-%3D-another-type"></a>

For this example, let's add the following code to the `src/ex2.rs` file.

```rust
mod ex1;
use ex1::InputEvent;

#[derive(Debug)]
pub enum EditorEvent {
    InsertChar(char),
    InsertNewLine,
    Delete,
    Backspace,
    MoveCursorLeft,
    MoveCursorRight,
    MoveCursorUp,
    MoveCursorDown,
    Copy,
    Paste,
    Cut,
    Undo,
    Redo,
}

impl TryFrom<InputEvent> for EditorEvent {
    type Error = String;

    fn try_from(input_event: InputEvent) -> Result<Self, Self::Error> {
        match input_event {
            InputEvent::Keyboard((keypress, modifiers)) =>
                match (keypress, modifiers)
            {
                (ex1::KeyPress::Char(ch), None) => Ok(Self::InsertChar(ch)),
                (ex1::KeyPress::Char(_), Some(_)) => todo!(),
                (ex1::KeyPress::Enter, None) => Ok(Self::InsertNewLine),
                (ex1::KeyPress::Enter, Some(_)) => todo!(),
                (ex1::KeyPress::Backspace, None) => todo!(),
                (ex1::KeyPress::Backspace, Some(_)) => todo!(),
                (ex1::KeyPress::Delete, None) => todo!(),
                (ex1::KeyPress::Delete, Some(_)) => todo!(),
                (ex1::KeyPress::Left, None) => todo!(),
                (ex1::KeyPress::Left, Some(_)) => todo!(),
                (ex1::KeyPress::Right, None) => todo!(),
                (ex1::KeyPress::Right, Some(_)) => todo!(),
                (ex1::KeyPress::Up, None) => todo!(),
                (ex1::KeyPress::Up, Some(_)) => todo!(),
                (ex1::KeyPress::Down, None) => todo!(),
                (ex1::KeyPress::Down, Some(_)) => todo!(),
                (ex1::KeyPress::Home, None) => todo!(),
                (ex1::KeyPress::Home, Some(_)) => todo!(),
                (ex1::KeyPress::End, None) => todo!(),
                (ex1::KeyPress::End, Some(_)) => todo!(),
                (ex1::KeyPress::PageUp, None) => todo!(),
                (ex1::KeyPress::PageUp, Some(_)) => todo!(),
                (ex1::KeyPress::PageDown, None) => todo!(),
                (ex1::KeyPress::PageDown, Some(_)) => todo!(),
                (ex1::KeyPress::Tab, None) => todo!(),
                (ex1::KeyPress::Tab, Some(_)) => todo!(),
                (ex1::KeyPress::F(_), None) => todo!(),
                (ex1::KeyPress::F(_), Some(_)) => todo!(),
            },
            InputEvent::Resize(_) => todo!(),
            InputEvent::Mouse(_) => todo!(),
        }
    }
}

fn main() {
    let a_pressed = InputEvent::Keyboard((ex1::KeyPress::Char('a'), None));
    println!("{:?}", EditorEvent::try_from(a_pressed));

    let enter_pressed = InputEvent::Keyboard((ex1::KeyPress::Enter, None));
    println!("{:?}", EditorEvent::try_from(enter_pressed));
}

```

> You can get the source code for this example
> [here](https://github.com/nazmulidris/rust-scratch/blob/main/typestate-pattern/src/ex2.rs).
> Here's the code for the real
> [`EditorEvent`](https://github.com/r3bl-org/r3bl-open-core/blob/main/tui/src/tui/editor/editor_component/editor_event.rs#L74).

Here are some notes on this code:

- We have a new enum called `EditorEvent` that represents different types of events that
  can happen in an editor.
- We have a `TryFrom` implementation for `InputEvent` that converts an `InputEvent` into
  an `EditorEvent`. This is a way to restrict methods to specific variants of an enum by
  converting it into a totally different type.
- We still don't have a way to restrict methods to specific variants of the enum.

When you run this code (using `cargo run --bin ex2`), it should produce the following:

<pre class="pre-manual-highlight">$ cargo run --bin ex2
Ok(InsertChar('a'))
Ok(InsertNewLine)
</pre>

### Example 3: Best of both worlds, using generics and struct / enum with a marker trait
<a id="markdown-example-3%3A-best-of-both-worlds%2C-using-generics-and-struct-%2F-enum-with-a-marker-trait" name="example-3%3A-best-of-both-worlds%2C-using-generics-and-struct-%2F-enum-with-a-marker-trait"></a>

Finally we have arrived at the typestate pattern in Rust. With this example:
- You can now group all the states under a marker.
- You can have methods that are specific to a variant.
- You can specify methods that are common to all.
- It's like a very sophisticated builder pattern if you're already familiar with that.

Add the following code to the `src/ex3.rs` file.

```rust
use self::type_state_builder::HttpResponse;
use crossterm::style::Stylize;

pub fn main() -> Result<(), String> {
    let response = HttpResponse::<()>::new();
    println!("{}", "Start state".red().bold().underlined());
    println!("response: {:#?}", response);
    println!(
        "response size: {}",
        response.get_size().to_string().blue().bold()
    );

    // Transition to HeaderAndBody state by calling `set_status_line`.
    let mut response = response.set_status_line(200, "OK");
    println!("response: {:#?}", response);

    // Status line is required.
    println!("{}", "HeaderAndBody state".red().bold().underlined());
    println!("response_code: {}", response.get_response_code());
    println!("response body: {:#?}", response.get_body());
    println!("response: {:#?}", response);
    println!(
        "response size: {}",
        response.get_size().to_string().blue().bold()
    );

    // Body and headers are optional.
    println!("{}", "HeaderAndBody state # 2".red().bold().underlined());
    response.add_header("Content-Type", "text/html");
    response.set_body("<html><body>Hello World!</body></html>");
    println!("response: {:#?}", response);
    println!(
        "response size: {}",
        response.get_size().to_string().blue().bold()
    );

    // Final state.
    println!("{}", "Final state".red().bold().underlined());
    let response = response.finish();
    println!("response_code: {}", response.get_response_code());
    println!("status_line: {}", response.get_status_line());
    println!("headers: {:#?}", response.get_headers());
    println!("body: {}", response.get_body());
    println!("response: {:#?}", response);
    println!(
        "response size: {}",
        response.get_size().to_string().blue().bold()
    );

    Ok(())
}
```

Note the API that we have built here:
- You can't call `get_response_code` or `get_body` until you've called `set_status_line`.
- You can't call `add_header` or `set_body` until you've called `set_status_line`.
- You can't call `finish` until you've called `set_status_line`.
- We have 3 states: `Start`, `HeaderAndBody`, and `Final`. These are meant to be used as
  markers to restrict methods to specific states. Each is a struct with a marker trait.
  And it may or may not contain data / fields.
- We have a `HttpResponse` struct that uses a generic type `T: Marker` to represent the
  state. This is a way to restrict methods to specific states.
- We can transition between states by calling methods that consume the current state and
  return a new state. These methods are specific to the state they transition from. And
  they can be implemented via `impl HttpResponse<T: Marker> { ... }` blocks, where `T` is
  the `Start`, `HeaderAndBody`, or `Final` state.
- We can even implement methods that are valid for a non-existent state using `impl
  HttpResponse<()> { ... }`. This is the constructor.
- In the `Final` state, the data becomes immutable.

Add the following code to desribe the different state structs.

```rust
pub mod state {
    #[derive(Debug, Clone, Default)]
    pub struct Start {}

    #[derive(Debug, Clone, Default)]
    pub struct HeaderAndBody {
        pub response_code: u8,
        pub status_line: String,
        pub headers: Option<Vec<(String, String)>>,
        pub body: Option<String>,
    }

    #[derive(Debug, Clone, Default)]
    pub struct Final {
        pub response_code: u8,
        pub status_line: String,
        pub headers: Vec<(String, String)>,
        pub body: String,
    }

    // The following marker trait is used to restrict the operations
    // that are available in each state. This isn't strictly necessary,
    // but it's a nice thing to use in a where clause to restrict types.
    pub trait Marker {}
    impl Marker for () {}
    impl Marker for Start {}
    impl Marker for HeaderAndBody {}
    impl Marker for Final {}
}
```

Here is the code for the `HttpResponse` struct.

```rust
pub mod type_state_builder {
    use super::state::{Final, HeaderAndBody, Marker, Start};

    #[derive(Debug, Clone, Default)]
    pub struct HttpResponse<S: Marker> {
        pub state: S,
    }

    // Operations that are available in all states.
    impl<S> HttpResponse<S>
    where
        S: Marker,
    {
        pub fn get_size(&self) -> String {
            let len = std::mem::size_of_val(self);
            format!("{} bytes", len)
        }
    }

    // Operations that are only valid in `()`.
    impl HttpResponse<()> {
        pub fn new() -> HttpResponse<Start> {
            HttpResponse { state: Start {} }
        }
    }

    // Operations that are only valid in `Start`.
    impl HttpResponse<Start> {
        pub fn set_status_line(
            self,
            response_code: u8,
            message: &str,
        ) -> HttpResponse<HeaderAndBody> {
            HttpResponse {
                state: HeaderAndBody {
                    response_code,
                    status_line: format!(
                        "HTTP/1.1 {} {}", response_code, message
                    ),
                    ..Default::default()
                },
            }
        }
    }

    // Operations that are only valid in `HeaderAndBodyState`.
    impl HttpResponse<HeaderAndBody> {
        // setter.
        pub fn add_header(&mut self, key: &str, value: &str) {
            if self.state.headers.is_none() {
                self.state.headers.replace(Vec::new());
            }
            if let Some(v) = self.state.headers.as_mut() {
                v.push((key.to_string(), value.to_string()))
            }
        }

        // getter.
        pub fn get_response_code(&self) -> u8 {
            self.state.response_code
        }

        // setter.
        pub fn set_body(&mut self, body: &str) {
            self.state.body.replace(body.to_string());
        }

        // getter.
        pub fn get_body(&self) -> Option<&str> {
            self.state.body.as_deref()
        }

        // transition to Final state.
        pub fn finish(mut self) -> HttpResponse<Final> {
            HttpResponse {
                state: Final {
                    response_code: self.state.response_code,
                    status_line: self.state.status_line.clone(),
                    headers: self.state.headers.take().unwrap_or_default(),
                    body: self.state.body.take().unwrap_or_default(),
                },
            }
        }
    }

    // Operations that are only valid in `Final`.
    impl HttpResponse<Final> {
        // getter.
        pub fn get_headers(&self) -> &Vec<(String, String)> {
            &self.state.headers
        }

        // getter.
        pub fn get_body(&self) -> &str {
            &self.state.body
        }

        // getter.
        pub fn get_response_code(&self) -> u8 {
            self.state.response_code
        }

        // getter.
        pub fn get_status_line(&self) -> &str {
            &self.state.status_line
        }
    }
}
```

When you run the code using `cargo run --bin ex3`, it should produce the following output.

<pre class="pre-manual-highlight">$ cargo run --bin ex3
<span style="color:#BF616A"><u style="text-decoration-style:single"><b>Start state</b></u></span>
response: HttpResponse {
    state: Start,
}
response size: <span style="color:#81A1C1"><b>0 bytes</b></span>
response: HttpResponse {
    state: HeaderAndBody {
        response_code: 200,
        status_line: &quot;HTTP/1.1 200 OK&quot;,
        headers: None,
        body: None,
    },
}
<span style="color:#BF616A"><u style="text-decoration-style:single"><b>HeaderAndBody state</b></u></span>
response_code: 200
response body: None
response: HttpResponse {
    state: HeaderAndBody {
        response_code: 200,
        status_line: &quot;HTTP/1.1 200 OK&quot;,
        headers: None,
        body: None,
    },
}
response size: <span style="color:#81A1C1"><b>80 bytes</b></span>
<span style="color:#BF616A"><u style="text-decoration-style:single"><b>HeaderAndBody state # 2</b></u></span>
response: HttpResponse {
    state: HeaderAndBody {
        response_code: 200,
        status_line: &quot;HTTP/1.1 200 OK&quot;,
        headers: Some(
            [
                (
                    &quot;Content-Type&quot;,
                    &quot;text/html&quot;,
                ),
            ],
        ),
        body: Some(
            &quot;&lt;html&gt;&lt;body&gt;Hello World!&lt;/body&gt;&lt;/html&gt;&quot;,
        ),
    },
}
response size: <span style="color:#81A1C1"><b>80 bytes</b></span>
<span style="color:#BF616A"><u style="text-decoration-style:single"><b>Final state</b></u></span>
response_code: 200
status_line: HTTP/1.1 200 OK
headers: [
    (
        &quot;Content-Type&quot;,
        &quot;text/html&quot;,
    ),
]
body: &lt;html&gt;&lt;body&gt;Hello World!&lt;/body&gt;&lt;/html&gt;
response: HttpResponse {
    state: Final {
        response_code: 200,
        status_line: &quot;HTTP/1.1 200 OK&quot;,
        headers: [
            (
                &quot;Content-Type&quot;,
                &quot;text/html&quot;,
            ),
        ],
        body: &quot;&lt;html&gt;&lt;body&gt;Hello World!&lt;/body&gt;&lt;/html&gt;&quot;,
    },
}
response size: <span style="color:#81A1C1"><b>80 bytes</b></span>
</pre>

### Example 3.1: Using enum and PhantomData instead of struct
<a id="markdown-example-3.1%3A-using-enum-and-phantomdata-instead-of-struct" name="example-3.1%3A-using-enum-and-phantomdata-instead-of-struct"></a>

- You can use enums instead of structs if you have shared data (inner) that you move with
  state transitions.
- And you have to use `PhantomData` here.

Add the following code to the `src/ex3_1.rs` file.

```rust
use self::type_state_builder::HttpResponse;
use crossterm::style::Stylize;

pub fn main() -> Result<(), String> {
    let response = HttpResponse::<()>::new();
    println!("{}", "Start state".red().bold().underlined());
    println!("response: {:#?}", response);
    println!(
        "response size: {}",
        response.get_size().to_string().blue().bold()
    );

    // Status line is required.
    println!("{}", "HeaderAndBody state".red().bold().underlined());
    let mut response = response.set_status_line(200, "OK");
    println!("response_code: {}", response.get_response_code());
    println!("response body: {:#?}", response.get_body());
    println!("response: {:#?}", response);
    println!(
        "response size: {}",
        response.get_size().to_string().blue().bold()
    );

    // Body and headers are optional.
    println!("{}", "HeaderAndBody state # 2".red().bold().underlined());
    response.add_header("Content-Type", "text/html");
    response.set_body("<html><body>Hello World!</body></html>");
    println!("response: {:#?}", response);
    println!(
        "response size: {}",
        response.get_size().to_string().blue().bold()
    );

    // Final state.
    println!("{}", "Final state".red().bold().underlined());
    let response = response.finish();
    println!("response_code: {}", response.get_response_code());
    println!("status_line: {}", response.get_status_line());
    println!("headers: {:#?}", response.get_headers());
    println!("body: {:#?}", response.get_body());
    println!("response: {:#?}", response);
    println!(
        "response size: {}",
        response.get_size().to_string().blue().bold()
    );

    Ok(())
}
```

Note that this `main` function is the same as the one in the previous example.

The following code will be different. We are adding a new `data` module.

```rust
pub mod data {
    #[derive(Debug, Clone, Default)]
    pub struct HttpResponseData {
        pub response_code: u8,
        pub status_line: String,
        pub headers: Option<Vec<(String, String)>>,
        pub body: Option<String>,
    }
}
```

Here's the new `state` module. Note the use of enums and `PhantomData` instead of structs.

```rust
pub mod state {
    #[derive(Debug, Clone)]
    pub enum Start {}

    #[derive(Debug, Clone)]
    pub enum HeaderAndBody {}

    #[derive(Debug, Clone)]
    pub struct Final {}

    // The following marker trait is used to restrict the operations
    // that are available in each state. This isn't strictly necessary,
    // but it's a nice thing to use in a where clause to restrict types.
    pub trait Marker {}
    impl Marker for () {}
    impl Marker for Start {}
    impl Marker for HeaderAndBody {}
    impl Marker for Final {}
}
```

Here is the changed code for the `HttpResponse` struct.

```rust
pub mod type_state_builder {
    use super::{
        data::HttpResponseData,
        state::{Final, HeaderAndBody, Marker, Start},
    };
    use std::marker::PhantomData;

    #[derive(Debug, Clone)]
    pub struct HttpResponse<S: Marker> {
        pub data: HttpResponseData,
        pub state: PhantomData<S>,
    }

    // Operations that are only valid in ().
    impl HttpResponse<()> {
        pub fn new() -> HttpResponse<Start> {
            HttpResponse {
                data: HttpResponseData::default(),
                state: PhantomData::<Start>,
            }
        }
    }

    // Operations that are only valid in Start.
    impl HttpResponse<Start> {
        // setter.
        pub fn set_status_line(
            self,
            response_code: u8,
            message: &str,
        ) -> HttpResponse<HeaderAndBody> {
            HttpResponse {
                data: {
                    let mut data = self.data;
                    data.response_code = response_code;
                    data.status_line = format!(
                        "HTTP/1.1 {} {}", response_code, message
                    );
                    data
                },
                state: PhantomData::<HeaderAndBody>,
            }
        }
    }

    // Operations that are only valid in HeaderAndBodyState.
    impl HttpResponse<HeaderAndBody> {
        // setter.
        pub fn add_header(&mut self, key: &str, value: &str) {
            let mut_data = &mut self.data;
            if mut_data.headers.is_none() {
                mut_data.headers.replace(Vec::new());
            }
            if let Some(headers) = mut_data.headers.as_mut() {
                headers.push((key.to_string(), value.to_string()))
            }
        }

        // getter.
        pub fn get_response_code(&self) -> u8 {
            self.data.response_code
        }

        // setter.
        pub fn set_body(&mut self, body: &str) {
            self.data.body.replace(body.to_string());
        }

        // getter.
        pub fn get_body(&self) -> Option<&str> {
            self.data.body.as_deref()
        }

        // transition to Final state.
        pub fn finish(self) -> HttpResponse<Final> {
            let mut data = self.data;
            HttpResponse {
                data: HttpResponseData {
                    response_code: data.response_code,
                    status_line: data.status_line.clone(),
                    headers: Some(data.headers.take().unwrap_or_default()),
                    body: Some(data.body.take().unwrap_or_default()),
                },
                state: PhantomData::<Final>,
            }
        }
    }

    // Operations that are only valid in FinalState.
    impl HttpResponse<Final> {
        pub fn get_headers(&self) -> &Option<Vec<(String, String)>> {
            &self.data.headers
        }

        pub fn get_body(&self) -> &Option<String> {
            &self.data.body
        }

        pub fn get_response_code(&self) -> u8 {
            self.data.response_code
        }

        pub fn get_status_line(&self) -> &str {
            &self.data.status_line
        }
    }

    // Operations that are available in all states.
    impl<S> HttpResponse<S>
    where
        S: Marker,
    {
        pub fn get_size(&self) -> String {
            let len = std::mem::size_of_val(self);
            format!("{} bytes", len)
        }
    }
}
```

Here's the output when you run the code using `cargo run --bin ex3_1`.

<pre class="pre-manual-highlight">$ cargo run --bin ex3_1
<span style="color:#BF616A"><u style="text-decoration-style:single"><b>Start state</b></u></span>
response: HttpResponse {
    data: HttpResponseData {
        response_code: 0,
        status_line: &quot;&quot;,
        headers: None,
        body: None,
    },
    state: PhantomData&lt;ex3_1::state::Start&gt;,
}
response size: <span style="color:#81A1C1"><b>80 bytes</b></span>
<span style="color:#BF616A"><u style="text-decoration-style:single"><b>HeaderAndBody state</b></u></span>
response_code: 200
response body: None
response: HttpResponse {
    data: HttpResponseData {
        response_code: 200,
        status_line: &quot;HTTP/1.1 200 OK&quot;,
        headers: None,
        body: None,
    },
    state: PhantomData&lt;ex3_1::state::HeaderAndBody&gt;,
}
response size: <span style="color:#81A1C1"><b>80 bytes</b></span>
<span style="color:#BF616A"><u style="text-decoration-style:single"><b>HeaderAndBody state # 2</b></u></span>
response: HttpResponse {
    data: HttpResponseData {
        response_code: 200,
        status_line: &quot;HTTP/1.1 200 OK&quot;,
        headers: Some(
            [
                (
                    &quot;Content-Type&quot;,
                    &quot;text/html&quot;,
                ),
            ],
        ),
        body: Some(
            &quot;&lt;html&gt;&lt;body&gt;Hello World!&lt;/body&gt;&lt;/html&gt;&quot;,
        ),
    },
    state: PhantomData&lt;ex3_1::state::HeaderAndBody&gt;,
}
response size: <span style="color:#81A1C1"><b>80 bytes</b></span>
<span style="color:#BF616A"><u style="text-decoration-style:single"><b>Final state</b></u></span>
response_code: 200
status_line: HTTP/1.1 200 OK
headers: Some(
    [
        (
            &quot;Content-Type&quot;,
            &quot;text/html&quot;,
        ),
    ],
)
body: Some(
    &quot;&lt;html&gt;&lt;body&gt;Hello World!&lt;/body&gt;&lt;/html&gt;&quot;,
)
response: HttpResponse {
    data: HttpResponseData {
        response_code: 200,
        status_line: &quot;HTTP/1.1 200 OK&quot;,
        headers: Some(
            [
                (
                    &quot;Content-Type&quot;,
                    &quot;text/html&quot;,
                ),
            ],
        ),
        body: Some(
            &quot;&lt;html&gt;&lt;body&gt;Hello World!&lt;/body&gt;&lt;/html&gt;&quot;,
        ),
    },
    state: PhantomData&lt;ex3_1::state::Final&gt;,
}
response size: <span style="color:#81A1C1"><b>80 bytes</b></span>
</pre>

### Parting thoughts
<a id="markdown-parting-thoughts" name="parting-thoughts"></a>

To get an experiential understanding of the typestate pattern, you should try to build
something using it. It's a powerful pattern that can help you write more robust and
predictable code. And it's a great way to leverage Rust's type system to enforce state
transitions in your code. I encourage you to clone the repo and run the code to see how it
works. And make changes to it to see if you can make it behave differently and use it in
your own projects.

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
