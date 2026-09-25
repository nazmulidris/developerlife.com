# Plan: Transform `rust-scratch/reborrow` into a developerlife.com Article

## 1. Objective

Convert the code examples and conceptual documentation from
[`rust-scratch/reborrow`](file:///home/nazmul/github/rust-scratch/reborrow) into a
published article for [`developerlife.com`](file:///home/nazmul/github/developerlife.com).

The article will explore:

- Why `&mut T` cannot be copied and what happens under standard move semantics.
- How **reborrowing** works under the hood (`&mut *ref`) and how the compiler desugars
  helper method calls.
- **Non-Lexical Lifetimes (NLL)** (Rust 2018, RFC 2094): How it transformed borrow
  checking from rigid block scopes to control-flow graph (CFG) liveness, and how it
  enables flat sequential reborrowing.
- **Demystifying "Pausing a Borrow" & Busting the "Call Stack Myth"**:
    - What "pausing" actually means inside the compiler's borrow checker (static loan
      capability tracking, [Polonius](https://rust-lang.github.io/polonius/) origins).
    - Why the hardware/OS call stack does **not** enforce borrow safety, and why
      reborrowing works even within the _exact same stack frame_.
    - How the runtime call stack relates (and doesn't relate) to compile-time lifetime
      analysis.
- The precise boundary between valid sequential reborrowing
  ([`valid.rs`](file:///home/nazmul/github/rust-scratch/reborrow/src/valid.rs)) and
  illegal concurrent aliasing
  ([`invalid.rs`](file:///home/nazmul/github/rust-scratch/reborrow/src/invalid.rs)).
- Real-world nuances: lifetime subtyping, Deref coercions, and downgrading `&mut T` to
  `&T`.

---

## 2. Target File & Frontmatter Specifications

- **Target File**: `_posts/2026-09-25-rust-reborrowing.md` in
  [`/home/nazmul/github/developerlife.com`](file:///home/nazmul/github/developerlife.com)
- **Frontmatter**:
    ```yaml
    ---
    title: "Build with Naz : Rust Reborrowing, Aliasing, and Mutable References"
    author: Nazmul Idris
    date: 2026-09-25 09:00:00+00:00
    excerpt: |
        Why can an &mut self method call another &mut self method if mutable references
        cannot be copied? This article is a deep dive into Rust reborrowing mechanics,
        Non-Lexical Lifetimes (NLL), what "pausing a borrow" actually means in the
        compiler, busting the call stack myth, and the boundary between valid delegation
        and illegal concurrent aliasing.
    layout: post
    categories:
        - Rust
        - CS
    ---
    ```
- **TOC Engine**: Generated using `mktoc` (`<!-- BEGIN mktoc -->` ...
  `<!-- END mktoc -->`).
- **Spellcheck**: Add `<!-- cspell:words ... -->` directives for technical terms
  (`reborrow`, `reborrowing`, `reborrows`, `subtyping`, `dereferencing`, `callee`,
  `mktoc`, `Polonius`, `borrowck`, `liveness`).

---

## 3. Article Structure & Outline

### Section 1: Overview & The Fundamental Mystery

- The paradox: In Rust, `&mut T` does **not** implement `Copy`. Under move semantics,
  passing `self` to a helper method should consume it permanently.
- Why doesn't calling `self.log_score()` inside `add_score(&mut self)` trigger
  `error[E0382]: use of moved value: self`?
- Introducing **Reborrowing** as the invisible engine making idiomatic Rust possible.
- Quick summary / key takeaways for developers.

### Section 2: Core Rules of References & The Single-Use Token Problem

- Rule 1: Shared references (`&T`) implement `Copy`.
- Rule 2: Mutable references (`&mut T`) do **not** implement `Copy` (exclusive access
  guarantee).
- The hypothetical Rust without reborrowing: mutable references as single-use tokens where
  every helper method would have to pass back ownership:
  `fn helper(mut self: &mut Self) -> &mut Self`.

### Section 3: Anatomy of a Reborrow (`&mut *ref`)

- The explicit syntax: `&mut *original_reference`.
- The 3-phase lifecycle:
    1. **Child Borrow Creation**: A short-lived sub-loan is spawned.
    2. **Parent Borrow Suspension**: The parent reference is placed into a dormant/paused
       state.
    3. **Parent Borrow Restoration**: When the child borrow expires, the parent wakes back
       up with full exclusivity.

### Section 4: Non-Lexical Lifetimes (NLL): The 2018 Watershed Moment

- **Before NLL (Rust 2015)**:
    - Lifetimes were strictly lexical, tied to the nearest enclosing curly braces
      `{ ... }`.
    - A mutable borrow lived until the closing `}` of its block, even after its final
      instruction.
    - Reborrowing within the same function required artificial scoping blocks:
        ```rust
        let mut x = 10;
        let r1 = &mut x;
        {
            let r2 = &mut *r1; // artificial block needed in Rust 2015!
            *r2 += 1;
        }
        *r1 += 1;
        ```
- **After NLL (Rust 2018 - RFC 2094)**:
    - Lifetimes are derived from the Control Flow Graph (CFG) and end at the **point of
      last use** (liveness analysis).
    - Allows clean, flat reborrowing without synthetic `{ ... }` blocks.
    - Crucial insight: Why NLL still rejects `invalid.rs` (because `r1` is used _after_
      `r2.inc()`, meaning both borrows are concurrently live in the CFG).

### Section 5: What Does "Pausing a Borrow" Actually Mean? (Busting the "Call Stack Myth")

- **Busting the "Call Stack Myth"**:
    - _The Common Misconception_: "Reborrowing works because the call stack pauses the
      caller function while the callee runs."
    - _The Reality_: The hardware/OS call stack has **zero** role in enforcing borrow
      safety.
        - Borrow checking is a 100% static compile-time pass (MIR borrowck / Polonius).
        - At runtime, references are just naked machine pointers in registers/memory with
          zero runtime locks, flags, or stack introspection.
        - **Proof**: Reborrowing happens _within the exact same stack frame_!
            ```rust
            let mut c = Counter::default();
            let r1 = &mut c;
            let r2 = &mut *r1; // r1 is PAUSED right here, in the same stack frame!
            r2.inc();          // r2 is last used here
            r1.inc();          // r1 is RESTORED right here, in the same stack frame!
            ```
- **What "Pausing" Really Means Inside the Compiler**:
    - The borrow checker models references as abstract **loans** and **capabilities**.
    - When `r2 = &mut *r1` occurs, `r2` is registered as a child loan derived from `r1`.
    - While `r2` is in the CFG "live" set, the capability to access memory via `r1` (or
      root `c`) is marked as **suspended / invalidated**. Any attempt by code to touch
      `r1` triggers a compile error (`E0499` / `E0502`).
    - As soon as `r2` exits the live set (under NLL), the loan expires and `r1`'s
      capabilities are reactivated.
    - In [Polonius](https://rust-lang.github.io/polonius/) (Rust's next-generation borrow
      checker), this is formally represented through origins and loan subsets. Check the
      [Polonius WG](https://github.com/rust-lang/polonius) and the
      [rustc-dev-guide](https://rustc-dev-guide.rust-lang.org/borrow_check/polonius.html).
- **So how DOES the stack factor in, if at all?**:
    - The stack is purely the _runtime execution mechanism_ for synchronous function
      calls.
    - When delegating to a helper method (`self.log_score()`), the call boundary defines a
      convenient sub-lifetime (`'call`) for the child loan.
    - At runtime, single-threaded execution naturally means the caller isn't running while
      the callee runs. But compile-time safety was already proven by the borrow checker's
      CFG analysis, completely independent of the hardware stack.

### Section 6: The Mental Model: "Variable Shadowing" Analogy

- Detailed mapping between block-scoped variable shadowing (`{ let x = ...; }`) and
  reborrowing (`&mut *parent`).
- Comparison Matrix:
    - Lifespan (scope vs CFG liveness).
    - Accessibility (dormant parent vs shadowed outer binding).
    - Restoration (unfreezing parent vs exiting inner scope).
    - Memory Target (**different memory slot** for shadowing vs **exact same memory
      location** for reborrowing).

### Section 7: Visualizing Reborrowing with Mermaid Diagrams

- **Diagram 1: Static CFG Loan Lifecycle vs Runtime Stack**
    - Sequence / flowchart illustrating the difference:
        - What the compiler sees: MIR CFG nodes, Loan `L1` (active) -> Loan `L2` (child
          created, `L1` suspended) -> `L2` dies -> `L1` restored.
        - What the CPU executes: Instruction pointer jumping, naked pointers.
- **Diagram 2: Sequential Reborrowing vs Illegal Concurrent Aliasing**
    - Side-by-side visualization contrasting sequential temporal isolation
      ([`valid.rs`](file:///home/nazmul/github/rust-scratch/reborrow/src/valid.rs)) vs
      overlapping live ranges
      ([`invalid.rs`](file:///home/nazmul/github/rust-scratch/reborrow/src/invalid.rs)).

### Section 8: Deep Dive: Valid Sequential Delegation (`valid.rs`)

- Full code walkthrough of
  [`src/valid.rs`](file:///home/nazmul/github/rust-scratch/reborrow/src/valid.rs):
    - Struct `Player` and method `add_score(&mut self, points: i32)`.
    - What the compiler actually compiles: `Player::log_score(&mut *self)`.
    - Step-by-step trace of borrow states.
    - Demonstrating post-restoration usage (`self.score += 1`).

### Section 9: Deep Dive: Illegal Concurrent Aliasing (`invalid.rs`)

- Full code walkthrough of
  [`src/invalid.rs`](file:///home/nazmul/github/rust-scratch/reborrow/src/invalid.rs):
    - **Attempt 1: Simultaneous Arguments** (`bar(&mut c, &mut c)`):
        - Why passing two mutable references to the same function call is rejected at the
          call site.
        - Detailed breakdown of the rustc error:
          `cannot borrow c as mutable more than once at a time`.
    - **Attempt 2: Overlapping Borrows in the Same Scope**
      (`let r1 = &mut c; let r2 = &mut c; r2.inc(); r1.inc();`):
        - NLL analysis: why `r1`'s live range spans across `r2`'s creation and usage.
        - Why Rust's fundamental invariant **Aliasing XOR Mutability** forbids this.
    - The optimizer rationale: LLVM `noalias` annotations, pointer aliasing assumptions,
      and how allowing this would produce undefined behavior (UB).

### Section 10: Nuances: Shared Borrows, Deref Coercions & Downgrading

- Reborrowing with shared references (`&T`): subtyping, shortening lifetimes, and Deref
  coercion (e.g. `&Vec<T>` to `&[T]`).
- **Cross-Type Reborrowing (Downgrading)**: Reborrowing `&mut T` as temporary `&T`
  (`&*mut_ref`).
    - How this temporarily freezes the mutable reference into read-only mode until all
      shared readers drop.

### Section 11: Summary Cheat Sheet Matrix

- Comprehensive comparison table covering code patterns, compiler verdict, and borrow
  checker mechanics:
    1. Method call reborrow (`self.helper()`).
    2. Same-scope reborrow under NLL (`let r2 = &mut *r1; use(r2); use(r1);`).
    3. Pre-2018 block-scope reborrow (`{ let r2 = &mut *r1; }`).
    4. Simultaneous function arguments (`foo(&mut x, &mut x)`).
    5. Overlapping live ranges (`let r1 = &mut x; let r2 = &mut x; use(r2); use(r1);`).
    6. Downgrading reborrow (`let r_shared = &*r_mut;`).

### Section 12: Companion Repository & Further Reading

- Link to companion repository:
  [`github.com/nazmulidris/rust-scratch/tree/main/reborrow`](https://github.com/nazmulidris/rust-scratch/tree/main/reborrow).
- Links to related developerlife.com articles:
    - [Rust lifetimes: Subtyping and variance](https://developerlife.com/2024/09/02/rust-lifetimes/)
    - [Typestate pattern in Rust](https://developerlife.com/2024/05/28/typestate-pattern-rust/)
    - [Memory latency & CPU cache lines in Rust](https://developerlife.com/2025/05/19/rust-mem-latency/)
- Official Rust documentation:
    - [RFC 2094 (Non-Lexical Lifetimes)](https://rust-lang.github.io/rfcs/2094-nll.html)
    - [The Polonius Book](https://rust-lang.github.io/polonius/) &
      [rust-lang/polonius repo](https://github.com/rust-lang/polonius)
    - [rustc-dev-guide: Polonius](https://rustc-dev-guide.rust-lang.org/borrow_check/polonius.html)
    - [Rustonomicon: Subtyping and Variance](https://doc.rust-lang.org/nomicon/subtyping.html)

---

## 4. Execution Steps & Status

- [x] **Draft Post**: Write `_posts/2026-09-25-rust-reborrowing.md` incorporating the 5 core sections matching the introductory roadmap.
- [x] **Streamline & Be Thrifty**: Ditch all mermaid diagrams in favor of clean, readable ASCII diagrams; eliminate repetitive boilerplate; condense sections for readability.
- [x] **Title & Formatting**: Ensure title is `"Rust Reborrowing, Aliasing, and Mutable References"` (no "Build with Naz : " prefix).
- [x] **Generate TOC**: Run `mktoc _posts/2026-09-25-rust-reborrowing.md`.
- [x] **Synchronize Companion Repository**:
  - `rust-scratch/reborrow/src/valid.rs`: Updated to `u8`, `print_score`, and `{:#?}` format specifier.
  - `rust-scratch/reborrow/src/invalid.rs`: Added `#![allow(dead_code)]`.
  - `rust-scratch/reborrow/src/main.rs`: Invokes `valid::run()`.
  - `rust-scratch/reborrow/README.md`: Updated code snippets and method names.
  - Verified `cargo check` and `cargo run` pass with zero warnings.
- [x] **Verify Site Build**: Run `bundle exec jekyll build` in `/home/nazmul/github/developerlife.com` (0 errors, clean build).
- [x] **Git Check**: Verified repository status.

