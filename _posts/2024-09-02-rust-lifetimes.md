---
title:
  "Build with Naz : Rust lifetimes"
author: Nazmul Idris
date: 2024-09-02
excerpt: |
  Rust lifetimes are key part of the type system which allows the Rust
  compiler to make its memory safety guarantees. We will explore
  subtyping, variance, references, memory aliasing, splitting borrows,
  and clone on write in this article, its video, and repo.
layout: post
categories:
  - Rust
  - CLI
  - Server
---

<img class="post-hero-image" src="{{ 'assets/lifetimes.svg' | relative_url }}"/>

<!-- TOC -->

- [What is subtyping and variance?](#what-is-subtyping-and-variance)
  - [Subtyping](#subtyping)
  - [Variance](#variance)
- [More resources on Rust lifetimes](#more-resources-on-rust-lifetimes)
- [YouTube videos for this article](#youtube-videos-for-this-article)
- [Learn Rust lifetimes by example](#learn-rust-lifetimes-by-example)
  - [Example 1: References](#example-1-references)
  - [Example 2: Aliasing](#example-2-aliasing)
  - [Example 3: Lifetimes](#example-3-lifetimes)
  - [Example 4: Input slices](#example-4-input-slices)
  - [Example 5: Splitting borrows on structs](#example-5-splitting-borrows-on-structs)
  - [Example 6: Clone on write Cow](#example-6-clone-on-write-cow)
  - [Example 7: Subtyping and variance](#example-7-subtyping-and-variance)
- [Build with Naz video series on developerlife.com YouTube channel](#build-with-naz-video-series-on-developerlifecom-youtube-channel)

<!-- /TOC -->

## What is subtyping and variance?
<a id="markdown-what-is-subtyping-and-variance%3F" name="what-is-subtyping-and-variance%3F"></a>

Subtyping and variance are important concepts in Rust's algebraic type system. They allow
us to express relationships between types, and equivalence without using inheritance. Rust
also includes lifetimes in the type definitions themselves! So they become an integral
part of the a type.

### Subtyping
<a id="markdown-subtyping" name="subtyping"></a>

In Rust, subtyping refers to the relationship between two types where one type can be used
in place of the other.

1. This means that if a type `Sub` is a subtype of type `Super`, then any code that
   expects a `Super` can also accept an `Sub`. They are equivalent.
2. Just like inheritance, the opposite is not true. Any code expecting a `Sub` cannot
   accept a `Super`. They are not equivalent.

Consider the following code snippet:

```rust
use std::fmt::Display;

struct Cat {
    name: String,
    breed: String,
}

impl Display for Cat {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>)
    -> std::fmt::Result
    {
        write!(f, "Cat: {} ({})", self.name, self.breed)
    }
}

struct Dog {
    name: String,
    breed: String,
}

impl Display for Dog {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>)
    -> std::fmt::Result
    {
        write!(f, "Dog: {} ({})", self.name, self.breed)
    }
}

/// Since Display is a trait bound in the print_animal function,
/// both &Cat and &Dog can be used as arguments because they are
/// both subtypes of &dyn Display.
fn print_animal<T: Display>(animal: &T) {
    println!("{}", animal);
}

fn main() {
    let cat = Cat {
        name: "Sparky".to_string(),
        breed: "Siamese".to_string() };
    let dog = Dog {
        name: "Buddy".to_string(),
        breed: "Golden Retriever".to_string() };

    print_animal(&cat); // Prints "Cat: Sparky (Siamese)"
    print_animal(&dog); // Prints "Dog: Buddy (Golden Retriever)"

    let animals: Vec<&dyn Display> = vec![&cat, &dog];
    for animal in animals {
        println!("{}", animal);
    }
}
```

In this example:

- In the function `print_animal<T>(animal: &T)`, the super type of `T` is `Display`. This
  means that this function accepts any type that implements the `Display` trait.
- So, we can pass both `&Cat` and `&Dog` to the `print_animal()` function. Since both
  `Cat` and `Dog` implement the `Display` trait.
- The `animals` vector can hold references to any type that implements the `Display`
  trait, so we can store both `Cat` and `Dog` instances in it.
  - We use `&dyn Display` as the type since we want to use [trait
    objects](https://doc.rust-lang.org/stable/book/ch17-02-trait-objects.html#using-trait-objects-that-allow-for-values-of-different-types).
  - And we can't use `&impl Animal` since [this
    syntax](https://doc.rust-lang.org/stable/book/ch10-02-traits.html#clearer-trait-bounds-with-where-clauses)
    expects only a single type.

A real world example of this is the `Copy` and `Clone` traits:

- <https://doc.rust-lang.org/1.80.1/src/core/marker.rs.html#403>
- A type that is `Copy` is also `Clone`.
- But a type that is `Clone` is not necessarily `Copy`.

### Variance
<a id="markdown-variance" name="variance"></a>

In Rust, variance describes how subtyping relationships are preserved when dealing with
**generic** types. Lifetime annotations are part of the generics system. There are three
types of variance:

- `Covariance`: A generic type `T` is covariant if, when `Sub` is a subtype of `Super`,
  `T<Sub>` is also a subtype of `T<Super>`.
- `Invariance`: A generic type `T` is invariant if there is **no** subtyping relationship
   between `T<Sub>` and `T<Super>` when `Sub` is a subtype of `Super`.
- `Contravariance`: A generic type `T` is contravariant if, when `Sub` is a subtype of `Super`,
  `T<Super>` is a subtype of `T<Sub>`.

Here are some examples:

- **Covariance:** The `&T` type is covariant. This means that if `Sub` is a subtype of
  `Super`, then `&Sub` is a subtype of `&Super`. This is useful for references. In the
  code, `Cat` and `Dog` both implement the `Display` trait. Since `Display` is a trait
  bound in the `print_animal` function, both `&Cat` and `&Dog` can be used as arguments
  because they are both subtypes of `&dyn Display`.
- **Invariance:** The `&mut T` type is invariant. This means that if `Sub` is a subtype of
  `Super`, there is no subtyping relationship between `&mut Sub` and `&mut Super`. Also,
  the `UnsafeCell<T>` type is invariant. This means that there is no subtyping
  relationship between `UnsafeCell<Sub>` and `UnsafeCell<Super>` when `Sub` is a subtype
  of `Super`. This is because `UnsafeCell` is used to bypass Rust's safety checks, so it
  must be invariant. Both `&mut T` and `UnsafeCell<T>` are invariant in Rust because they
  are related to unsafe operations or mutable references, which require stricter type
  constraints to ensure safety.
- **Contravariance:** The `Fn(T)` type is contravariant. This means that if `Sub` is a
  subtype of `Super`, then `Fn(Super)` is a subtype of `Fn(Sub)`. This is useful for
  functions that take a callback as an argument.

Here is a table of some other generic types and their variances:

|                 |     'a    |         T         |     U     |
|-----------------|:---------:|:-----------------:|:---------:|
| `&'a T `        | covariant | covariant         |           |
| `&'a mut T`     | covariant | invariant         |           |
| `Box<T>`        |           | covariant         |           |
| `Vec<T>`        |           | covariant         |           |
| `UnsafeCell<T>` |           | invariant         |           |
| `Cell<T>`       |           | invariant         |           |
| `fn(T) -> U`    |           | **contra**variant | covariant |
| `*const T`      |           | covariant         |           |
| `*mut T`        |           | invariant         |           |

> This table is from [Rustonomicon -
> Variance](https://doc.rust-lang.org/nomicon/subtyping.html#variance).

## More resources on Rust lifetimes
<a id="markdown-more-resources-on-rust-lifetimes" name="more-resources-on-rust-lifetimes"></a>

- [Rustonomicon - Subtyping and variance with lifetimes](https://doc.rust-lang.org/nomicon/subtyping.html).
- [Rust compiler - Subtyping and variance implementation in the compiler](https://rustc-dev-guide.rust-lang.org/variance.html).
- [Rustonomicon - Ownership](https://doc.rust-lang.org/nomicon/ownership.html).

## YouTube videos for this article
<a id="markdown-youtube-videos-for-this-article" name="youtube-videos-for-this-article"></a>

This article has short examples on how to get to know Rust lifetimes deeply. If you like
to learn via video, please watch the companion video on the [developerlife.com YouTube
channel](https://www.youtube.com/@developerlifecom).

<!-- rust subtyping and variance -->
<iframe
    src="https://www.youtube.com/embed/HRlpYXi4E-M?si=cSc_Ew5RHQ-ffFWJ"
    title="YouTube video player"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    referrerpolicy="strict-origin-when-cross-origin"
    allowfullscreen>
</iframe>

<!-- rust lifetimes -->
<iframe
    src="https://www.youtube.com/embed/eIJxAEcle7E?si=4Wn3X2mT7Pd8uvGx"
    title="YouTube video player"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    referrerpolicy="strict-origin-when-cross-origin"
    allowfullscreen>
</iframe>

<br/>

## Learn Rust lifetimes by example
<a id="markdown-learn-rust-lifetimes-by-example" name="learn-rust-lifetimes-by-example"></a>

Let's create some examples to illustrate how to use Rust lifetimes. You can run
`cargo new --bin lifetimes` to create a new binary crate.

> The code in the video and this tutorial are all in [this GitHub
> repo](https://github.com/nazmulidris/rust-scratch/blob/main/lifetimes/).

### Example 1: References
<a id="markdown-example-1%3A-references" name="example-1%3A-references"></a>

First add `mod ex_1_references;` to `lib.rs`. Then you can add the following code to the
`src/ex_1_references.rs` file.

> The code for this example is
> [here](https://github.com/nazmulidris/rust-scratch/blob/main/lifetimes/src/ex_1_references.rs).

```rust
#[test]
fn ex_1_references() {
    fn try_to_use_after_free(arg: usize) -> &'static str {
        let s = format!("{} is a number", arg);
        // return &s; /* 🧨 won't compile! */
        unreachable!()
    }

    fn try_to_modify_referent() {
        let mut data = vec![1, 2, 3]; /* referent */
        let ref_to_first_item = &data[0]; /* reference */
        // data.push(4); /* 🧨 won't compile */
        println!("first_item: {}", ref_to_first_item);
        /* ref_to_first_item reference still in scope */
        // drop(ref_to_first_item);
    }
}
```

The main things to note about this code:

- Rust requires any _references_ to freeze:
    - the referent and its owners.
- While a _reference_ is **in scope**, Rust will not allow you to:
    - change the referent and its owners.
- [More info](https://doc.rust-lang.org/nomicon/ownership.html).

### Example 2: Aliasing
<a id="markdown-example-2%3A-aliasing" name="example-2%3A-aliasing"></a>


Let's review some background info on references. There are two kinds of reference:

1. Shared reference: `&`
2. Mutable reference: `&mut`

Here are the rules of references:

1. A reference cannot outlive its referent.
2. A **mutable reference** cannot be aliased.

Aliasing:

1. Variables and pointers alias if they refer to overlapping regions of memory.
2. The definition of "alias" that Rust will use likely involves some notion of
    **liveness** and **mutation**: we don't actually care if aliasing occurs if there
    aren't any actual writes to memory happening.

Here's more info:
- <https://doc.rust-lang.org/nomicon/references.html>
- <https://doc.rust-lang.org/nomicon/aliasing.html>

> The code for this example is
> [here](https://github.com/nazmulidris/rust-scratch/blob/main/lifetimes/src/ex_2_aliasing.rs).

Add `mod ex_2_aliasing;` to `lib.rs`. Then you can add the following code to the
`src/ex_2_aliasing.rs` file.

```rust
#[test]
fn ex_2_aliasing() {
    /// `input_ref` and `output_ref` can't overlap or alias, and thus
    /// can't clobber each other.
    fn compute(input_ref: &usize, output_ref: &mut usize) {
        if *input_ref > 10 {
            *output_ref = 1;
        }
        if *input_ref > 5 {
            *output_ref *= 2;
        }
    }

    // This is safe to do because `input` and `output` don't overlap.
    {
        let input = 10usize;
        let mut output = 1usize;

        let input_address = &input as *const usize;
        let output_address = &output as *const usize;

        compute(&input, &mut output);

        assert_eq!(output, 2);
        assert_ne!(input_address, output_address);
    }

    // Try and clobber `input` with `output`.
    // - Rust won't allow `input` and `output` to overlap aka alias.
    // - Rust won't allow the `&mut output` to be aliased!
    {
        let mut output = 1usize;
        // compute(&output, &mut output); /* 🧨 won't compile! */
    }
}
```

### Example 3: Lifetimes
<a id="markdown-example-3%3A-lifetimes" name="example-3%3A-lifetimes"></a>

Rust enforces a set of rules that govern how references are used via **lifetimes**.

Lifetimes are named regions of code that a reference must be valid for.
- For simple programs, lifetimes coincide with lexical scope.
- Those regions may be fairly complex, as they correspond to paths of execution in the
    program.
- There may even be holes in these paths of execution, as it's possible to invalidate
    a reference as long as it's reinitialized before it's used again.
- Types which contain references (or pretend to) may also be tagged with lifetimes so
    that Rust can prevent them from being invalidated as well.

Inside a function, Rust doesn't let you explicitly name lifetimes. And each let
statement implicitly introduces a scope. However, once you cross the function
boundary, you need to start talking about lifetimes.

More info:
- <https://doc.rust-lang.org/nomicon/lifetimes.html#the-area-covered-by-a-lifetime>
- <https://doc.rust-lang.org/nomicon/lifetime-mismatch.html>

> The code for this example is
> [here](https://github.com/nazmulidris/rust-scratch/blob/main/lifetimes/src/ex_3_lifetimes.rs).

Add `mod ex_3_lifetimes;` to `lib.rs`. Then you can add the following code to the
`src/ex_3_lifetimes.rs` file.

```rust
#[rustfmt::skip]
#[test]
fn ex_3_lifetimes_1() {
    /// 'fn is          <  'input.
    /// 'fn needs to be >= 'input.
    ///
    /// - 'fn is the lifetime of the referent. It is short.
    /// - 'input is the lifetime of the reference. It is long.
    fn try_to_make_reference_outlive_referent<'input>(
        param: &'input usize
    ) -> &'input str {
        // 'fn: {
            let referent = format!("{}", param);
            let reference = &/*'fn*/referent;
            // return reference; /* 🧨 does not compile! */
            unreachable!()
        // }
    }

    fn fix_try_to_make_reference_outlive_referent<'input>(
        param: &'input usize
    ) -> &'input str {
        match param {
            0 => /* &'static */ "zero",
            1 => /* &'static */ "one",
            _ => /* &'static */ "many",
        }
    }

    assert_eq!(
        fix_try_to_make_reference_outlive_referent(&0), "zero");
}
```

Notes on the code above:

- The string literals "zero", "one", and "many" are stored in a special section of memory
  that is accessible throughout the entire program execution. This means that these string
  literals are available for the entire duration of the program, hence they have the
  `'static` lifetime.

Add the following code to the `ex_3_lifetimes.rs` file.

```rust
#[rustfmt::skip]
#[test]
fn ex_3_lifetimes_2() {
    fn try_to_modify_referent() {
        let mut data = vec![1, 2, 3]; /* referent */
        // 'first: {
            /* reference */
            let ref_to_first_item = &/*'first*/data[0];
            //   'second: {
            //        /* 🧨 won't compile */
            //        Vec::push(&/*'second*/mut data, 4);
            //    }
            println!("first_item: {}", ref_to_first_item);
            /* reference still in scope */
        // }
        // drop(ref_to_first_item);
    }
}
```

Notes on the code above:

- Rust doesn't understand that `ref_to_first_item` is a reference to a subpath of
  `data`. It doesn't understand [`Vec`] at all. 🤯

- Here's what it sees:
    - `ref_to_first_item` which is `&'first data` has to live for `'first` in order to
      be printed.
    - When we try to call push, it then sees us try to make an `&'second mut data`.
    - It knows that `'second` is contained within `'first`, and rejects our program
      because the `&'first data` must still be alive! And we can't alias a **mutable
      reference**.

- The lifetime system is much more coarse than the reference semantics we're
  actually interested in preserving.

### Example 4: Input slices
<a id="markdown-example-4%3A-input-slices" name="example-4%3A-input-slices"></a>

We can use lifetimes and slices to work with data without modifying it. This pattern shows
up a lot when working with parsers (eg: `nom`) and general string manipulation.

Real world examples:
- <https://github.com/r3bl-org/r3bl-open-core/tree/main/core/src/tui_core/graphemes>
- <https://github.com/r3bl-org/r3bl-open-core/blob/main/core/src/tui_core/graphemes/access.rs#L173>

> The code for this example is
> [here](https://github.com/nazmulidris/rust-scratch/blob/main/lifetimes/src/ex_4_input_slices.rs).

First add `mod ex_4_input_slices;` to `lib.rs`. Then you can add the following code to the
`src/ex_4_input_slices.rs` file.

```rust
#[rustfmt::skip]
#[test]
fn ex_4_input_slices() {
    // 'fn {
        let data = String::from("foo bar baz");
        let middle_word: & /*'fn*/ str = middle_word(&data);
        assert_eq!(middle_word, "bar");
    // }
}

fn middle_word<'input>(input: &'input str) -> &'input str {
    let iter = input.split_whitespace();

    let (_, middle_word_index) = {
        let iter_clone = iter.clone();
        let word_count = iter_clone.count();
        let middle_word_index = word_count / 2;
        (word_count, middle_word_index)
    };

    let (middle_word_len, len_until_middle_word) = {
        let mut middle_word_len = 0;
        let len_until_middle_word = iter
            .enumerate()
            // Go as far as the middle word.
            .take_while(|(index, _)| *index <= middle_word_index)
            .map(|(index, word)| {
                // At middle word.
                if index == middle_word_index {
                    middle_word_len = word.len();
                    0
                }
                // Before middle word.
                else {
                    word.len()
                }
            })
            .sum::<usize>();

        (middle_word_len, len_until_middle_word)
    };

    let (start_index, end_index) = {
        let start_index = len_until_middle_word + 1;
        let end_index = len_until_middle_word + middle_word_len + 1;
        (start_index, end_index)
    };

    &/*'input*/input[start_index..end_index]
}
```

### Example 5: Splitting borrows on structs
<a id="markdown-example-5%3A-splitting-borrows-on-structs" name="example-5%3A-splitting-borrows-on-structs"></a>

The mutual exclusion property of mutable references can be very limiting when working with
a composite structure.

The borrow checker understand structs sufficiently to know that it's possible to borrow
disjoint fields of a struct simultaneously.

`ex_5_splitting_borrows_on_structs.rs` will demonstrate this.

> The code for this example is
> [here](https://github.com/nazmulidris/rust-scratch/blob/main/lifetimes/src/ex_5_splitting_borrows_on_structs.rs).

First add `mod ex_5_splitting_borrows_on_structs;` to `lib.rs`. Then you can add the
following code to the `src/ex_5_splitting_borrows_on_structs.rs` file.

```rust
#[test]
fn ex_5_splitting_borrows_on_structs() {
    struct Data {
        a: usize,
        b: usize,
    }

    fn change_field_by_ref(field: &mut usize) {
        *field += 1;
    }

    let mut data = Data { a: 1, b: 2 };

    let a_ref = &mut data.a;
    let b_ref = &mut data.b;

    change_field_by_ref(a_ref);
    change_field_by_ref(b_ref);

    assert_eq!(data.a, 2);
    assert_eq!(data.b, 3);
}
```

The next example shows a struct that only contains references. As long as the owned struct
and the references live for the same lifetime, it all works. Add the following code to the
same file:

```rust
#[test]
fn ex_5_splitting_borrows_on_structs_2() {
    struct Data<'a> {
        field_usize: &'a mut usize,
        field_str: &'a str,
    }

    impl Data<'_> {
        fn new<'a>(
            str_param: &'a str, usize_param: &'a mut usize
        ) -> Data<'a>
        {
            Data {
                field_usize: usize_param,
                field_str: str_param,
            }
        }

        fn change_field_usize(&mut self) {
            *self.field_usize += 1;
        }

        fn change_field_str(&mut self) {
            self.field_str = "new value";
        }
    }

    let str_arg = "old value";
    let usize_arg = &mut 1;
    let mut data = Data::new(str_arg, usize_arg);

    data.change_field_usize();
    data.change_field_str();

    assert_eq!(*data.field_usize, 2);
    assert_eq!(data.field_str, "new value");
}
```

### Example 6: Clone on write (Cow)
<a id="markdown-example-6%3A-clone-on-write-cow" name="example-6%3A-clone-on-write-cow"></a>

The [`Cow`](https://doc.rust-lang.org/std/borrow/enum.Cow.html) type is a smart pointer
that can be used to work with both owned and borrowed data.
- It is useful when you want to avoid unnecessary allocations and copying.
- You can also use it in functions where you might need to mutate the argument; in which
  case the data will be **lazily cloned** when mutation or ownership is required.

> The code for this example is
> [here](https://github.com/nazmulidris/rust-scratch/blob/main/lifetimes/src/ex_6_cow.rs).

First add `mod ex_6_cow;` to `lib.rs`. Then you can add the following code to the
`src/ex_6_cow.rs` file.

```rust
#[test]
fn ex_6_cow() {
    use std::borrow::Cow;

    fn capitalize<'a>(input: Cow<'a, str>) -> Cow<'a, str> {
        if input.is_empty() {
            return input;
        }

        if input.chars().all(char::is_uppercase) {
            return input;
        }

        let mut cloned = String::with_capacity(input.len());
        cloned.push_str(&input[..1].to_uppercase());
        cloned.push_str(&input[1..]);
        Cow::Owned(cloned)
    }

    let borrowed_data = Cow::Borrowed("hello");
    let owned_data = Cow::Owned(String::from("world"));

    let capitalized_borrowed_data = capitalize(borrowed_data);
    let capitalized_owned_data = capitalize(owned_data);

    assert_eq!(capitalized_borrowed_data, "Hello");
    assert_eq!(capitalized_owned_data, "World");
}
```

Notes on the code:

- The `capitalize` function takes a `Cow` as an argument. It also returns a `Cow`.
- The `Cow` type is an enum that can hold either a borrowed reference or an owned value.
- The `capitalize` function will return the input unchanged if it is already capitalized.
  Otherwise it allocates a new capitalized string, moves into into a `Cow` and returns it
  as an owned value.

Next, add the following code to the same file:

```rust
#[test]
fn ex_6_cow_2() {
    use std::borrow::Cow;

    fn capitalize_mut<'a>(input: &mut Cow<'a, str>) {
        if input.is_empty() {
            return;
        }

        if input.chars().all(char::is_uppercase) {
            return;
        }

        let mut cloned = String::with_capacity(input.len());
        cloned.push_str(&input[..1].to_uppercase());
        cloned.push_str(&input[1..]);
        *input = Cow::Owned(cloned);
    }

    let mut borrowed_data = Cow::Borrowed("hello");
    let mut owned_data = Cow::Owned(String::from("world"));

    capitalize_mut(&mut borrowed_data);
    capitalize_mut(&mut owned_data);

    assert_eq!(borrowed_data, "Hello");
    assert_eq!(owned_data, "World");
}
```

Notes on the code:

- The `capitalize_mut` function takes a mutable reference to a `Cow` as an argument.
- It will mutate the input in place if it is not already capitalized. This requires
  cloning the input string.

### Example 7: Subtyping and variance
<a id="markdown-example-7%3A-subtyping-and-variance" name="example-7%3A-subtyping-and-variance"></a>

> Please refer to the [Subtyping and variance](#what-is-subtyping-and-variance) section for
> more information, before following this example.

Let's define that `Sub` is a subtype of Super (ie `Sub : Super`).
- What this is suggesting to us is that the set of requirements that `Super` defines
  are completely satisfied by `Sub`.
- `Sub` may then have more requirements.
- That is, `Sub` > `Super`.

Replacing this with lifetimes, `'long : 'short` if and only if
- `'long` defines a region of code that completely contains `'short`.
- `'long` may define a region larger than `'short`, but that still fits our
  definition.
- That is, `'long` > `'short`.

More info:
- <https://doc.rust-lang.org/nomicon/subtyping.html>

> The code for this example is
> [here](https://github.com/nazmulidris/rust-scratch/blob/main/lifetimes/src/ex_7_subtyping_and_variance.rs).

First add `mod ex_7_subtyping_and_variance;` to `lib.rs`. Then you can add the following code to the
`src/ex_7_subtyping_and_variance.rs` file.

```rust
#[rustfmt::skip]
#[test]
fn subtyping() {
    fn debug<'a, T: std::fmt::Display + ?Sized>(a: &'a T, b: &'a T) {
        println!("a: {}, b: {}", a, b);
    }

    let hello: &'static str = "hello";

    // 'short {
    {
        let world = "world".to_string();
        debug(
            /*&'static*/ hello,
            &/*'short*/  world
        );
        // Why does this work?
        // 1) `&'static str` : `&'short str`
        //       ↑                ↑
        //     Subtype          Super type
        // 2) `hello` silently downgrades from `&'static str`
        //    into `&'short str`
    }
    // }
}
```

Notes on the code above:

- `fn debug(a, b)`:
  - Since: `&'a T` is covariant over `'a`, we are allowed to perform subtyping.
  - And: `&'static str` is a subtype of `&'short str`.
  - And since:
  ```text
  'static : 'short
      ↑       ↑
   Sub     Super
  ```
- Here's a short table with the rules:

  ```text
  |                 | `'a`     | `T` |
  |-----------------|----------|-----|
  | `&'a T`         | C        | C   |
  | `&'a mut T`     | C        | I   |
  ```


Now, add the following code to the same file:

```rust
/// More info:
/// - <https://doc.rust-lang.org/nomicon/subtyping.html>
#[rustfmt::skip]
#[test]
fn variance() {
    fn assign<'a, T>(reference: &'a mut T, value: T) {
        *reference = value;
    }

    let mut hello: &'static str = "hello";

    // 'short {
    {
        let world = "world".to_string();
        /* 🧨 does not compile! Due to invariance, the 2 args are
           different types!
        */
        // assign(
        //     &mut/*&'static*/ hello,
        //     &/*'short*/      world
        // );

        // `&mut T` is invariant over `T`, meaning, these are
        // incompatible:
        //
        // 1. 1st arg: `&mut &'static str`, which is `&mut T`
        //    where `T = &'static str`.
        // 2. 2nd arg: `&'short str`, and it is expecting
        //    `T = &'static str`. This `T` does not match!
        //
        // This means that:
        // - `&mut &'static str` cannot be a subtype of `&'short str`
        // - even if `'static` **is** a subtype of `'short`
    }
    // }
}
```

Notes on the code:

1. Take a mutable reference and a value and overwrite the **referent** with it.
2. It clearly says in its signature the referent and the value must be the
    **exact** same type.
- `&mut T` is invariant over `T`, meaning,
- `&mut &'long T` is **NOT** a subtype of `&'short T`,
- Even when:
```text
'long : 'short
↑       ↑
Sub     Super
```
3. Here's a short table with the rules:
```text
|                 | `'a`     | `T` |
|-----------------|----------|-----|
| `&'a T`         | C        | C   |
| `&'a mut T`     | C        | I   |
```

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
