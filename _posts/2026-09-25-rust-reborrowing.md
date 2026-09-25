---
title: "Rust Reborrowing, Aliasing, and Mutable References"
author: Nazmul Idris
date: 2026-09-25 09:00:00+00:00
excerpt: |
    Why can a method that takes `&mut self` call another method that takes `&mut self`? If
    mutable references can't be copied, how is this possible? This article explores Rust's
    core invariant Aliasing XOR Mutability, and dives into reborrowing, Non-Lexical
    Lifetimes (NLL), what "pausing a borrow" actually means in the compiler, and illegal
    concurrent aliasing.
layout: post
categories:
    - Rust
    - CS
---

<!-- BEGIN mktoc -->

- [This example works, but why?](#this-example-works-but-why)
    - [Mental Model: "Variable Shadowing" Analogy](#mental-model-variable-shadowing-analogy)
- [1. How Reborrowing Works Under the Hood](#1-how-reborrowing-works-under-the-hood)
    - [Core Rules: Shared vs. Mutable References](#core-rules-shared-vs-mutable-references)
    - [What If Mutable References Were Strictly Move-Only?](#what-if-mutable-references-were-strictly-move-only)
    - [What Is Reborrowing?](#what-is-reborrowing)
    - [How the Compiler Desugars a Reborrow (`&mut *ref`)](#how-the-compiler-desugars-a-reborrow-mut-ref)
    - [Putting It All Together](#putting-it-all-together)
- [2. How Non-Lexical Lifetimes (NLL) Revolutionized Borrow Checking](#2-how-non-lexical-lifetimes-nll-revolutionized-borrow-checking)
- [3. What "Pausing a Borrow" Actually Means Inside the Compiler](#3-what-pausing-a-borrow-actually-means-inside-the-compiler)
    - [The "Interpreter Trap"](#the-interpreter-trap)
    - [Compile-Time Loan Capabilities & Polonius](#compile-time-loan-capabilities--polonius)
    - [Visualizing Loan Lifecycle vs. Runtime Stack](#visualizing-loan-lifecycle-vs-runtime-stack)
- [4. The Call Stack Does Not Enforce Safety](#4-the-call-stack-does-not-enforce-safety)
- [5. Valid Sequential Delegation vs. Illegal Concurrent Aliasing](#5-valid-sequential-delegation-vs-illegal-concurrent-aliasing)
    - [Example 1: Valid Sequential Delegation](#example-1-valid-sequential-delegation)
    - [Example 2: Illegal Concurrent Aliasing](#example-2-illegal-concurrent-aliasing)
        - [Attempt 1: Creating overlapping mutable references](#attempt-1-creating-overlapping-mutable-references)
        - [Attempt 2: Overlapping Borrows in the Same Scope](#attempt-2-overlapping-borrows-in-the-same-scope)
- [Conclusion & Further Reading](#conclusion--further-reading)
    - [Resources & Links](#resources--links)

<!-- END mktoc -->

## This example works, but why?

This is a pretty common pattern that you may have encountered in your Rust journey.

```rust
#[derive(Debug, Default)]
struct Player {
    score: u8,
}

impl Player {
    pub fn add_score(&mut self, points: u8) {
        self.score += points;

        // 🤔 Calling another &mut self helper method!
        // Doesn't this overlap?
        self.print_score();

        // 🤔 Continuing to use self afterward!
        self.score += 1;
    }

    pub fn print_score(&mut self) {
        println!("Score is now: {:#?}", self.score);
    }
}

fn main() {
    let mut player = Player::default();
    player.add_score(10);
    // ☑️ The &mut borrow ends here when the call to add_score() returns.

    // ☑️ This doesn't overlap with the previous call, so it is valid.
    player.print_score();
}
```

This compiles cleanly and runs. But if you stop and think about Rust's foundational
ownership rules, it seems that this should not compile:

1. **Shared references (`&T`) implement `Copy`.** You can duplicate them as many times as
   you want.
2. **Mutable references (`&mut T`) do NOT implement `Copy`.** They represent strictly
   exclusive, unique access.
3. Under normal move semantics, passing any non-`Copy` type into a function **moves and
   consumes** that value permanently.

Look inside `Player::add_score()`: if `&mut self` were moved into `self.print_score()`,
then `self` would have been consumed and destroyed:

- The subsequent line `self.score += 1` would trigger
  `error[E0382]: use of moved value: self`.
- You would expect to have to return `&mut self` out of every single helper method just to
  thread ownership back to the caller.

Then why does this code compile without compiler errors?

The answer is **reborrowing**. Reborrowing is the compiler mechanism that makes mutable
references practical in Rust. Instead of moving `self`, the compiler automatically inserts
a temporary sub-borrow: `&mut *self`, whose lifetime is shorter than `self`'s borrow. This
isn't aliasing - we are not copying the mutable borrows. Instead we are making a new
mutable borrow that replaces the original one, but with a shorter lifetime. And they can't
both be used at the same time.

### Mental Model: "Variable Shadowing" Analogy

A great way to think about reborrowing is to compare it to block-scoped **variable
shadowing** in Rust. This example demonstrates how we create two variable bindings `x` and
they are **not** aliases.

```rust
// Variable Shadowing:
let x: u8 = 10;
{
    // Shadows outer `x`
    let x: String = "hello".to_string();
    // Prints "hello"
    println!("{x}");
} // Inner `x` (the String) is dropped here
// Outer `x` (the u8) is restored
println!("{x}"); // Prints 10
```

- The second `x` (`String`) completely shadows the first `x`. When the inner scope ends,
  the outer `x` (`u8`) is restored.
- And while the inner `x` (`String`) is in scope, the outer `x` (`u8`) cannot be used.

The same logic applies to reborrowing. Notice how similar the mechanics are:

1. **Lifespan:**
    - **Variable Shadowing:** The inner binding exists only within the inner scope.
    - **Reborrowing:** The child reference lives only for the sub-lifetime (callee or
      [`NLL`] span).
2. **Accessibility:**
    - **Variable Shadowing:** The outer binding cannot be named or accessed while
      shadowed.
    - **Reborrowing:** The parent reference is dormant/suspended while the child borrow is
      live.
3. **Restoration:**
    - **Variable Shadowing:** When the inner scope ends, the outer binding is usable
      again.
    - **Reborrowing:** When the child borrow ends, the parent reference is restored with
      full permissions.
4. ‼️ **Memory Target (The Crucial Difference):**
    - **Variable Shadowing (Different memory):** The inner binding occupies a completely
      separate slot. Modifying it has zero effect on the outer variable.
    - **Reborrowing (Same memory):** The child reference points to the _exact same
      address_. Any mutation made through the child persists and is seen by the parent!

The difference in **memory target** is what makes reborrowing unique: you temporarily
delegate access to the _exact same data_, mutate it through the child, and then resume
control with the parent.

In this article, we will unpack the following:

1. How reborrowing works under the hood
   [[jump to the section](#1-how-reborrowing-works-under-the-hood)].
2. How **Non-Lexical Lifetimes ([`NLL`])** revolutionized borrow checking (in Rust 2018
   Edition)
   [[jump to the section](#2-how-non-lexical-lifetimes-nll-revolutionized-borrow-checking)].
3. What "pausing a borrow" actually means inside the compiler (and how
   [**Polonius**][polonius-book] models it)
   [[jump to the section](#3-what-pausing-a-borrow-actually-means-inside-the-compiler)].
4. Why the call stack is **not** what enforces safety
   [[jump to the section](#4-the-call-stack-does-not-enforce-safety)].
5. The exact boundary where valid sequential delegation ends and illegal concurrent
   aliasing begins
   [[jump to the section](#5-valid-sequential-delegation-vs-illegal-concurrent-aliasing)].

> 💡 All code examples featured in this article are available in the companion repository:
> [**`rust-scratch/reborrow`**][repo-reborrow].

## 1. How Reborrowing Works Under the Hood

### Core Rules: Shared vs. Mutable References

- **`&T` implements `Copy`:** Duplication is trivial and safe because multiple readers
  cannot mutate data or cause data races.
- **`&mut T` does NOT implement `Copy`:** It guarantees exclusive access. If duplicated,
  multiple writers could alias the same memory concurrently, causing data races and
  undefined behavior (UB).

Because `&mut T` is not `Copy`, assigning it performs a **move**:

```rust
let mut x = 42;
let r1 = &mut x;
let r2 = r1; // MOVES r1 into r2!
// println!("{}", r1); // ERROR: borrow of moved value: `r1`
```

### What If Mutable References Were Strictly Move-Only?

If Rust treated `&mut T` strictly like other non-`Copy` types, passing `&mut self` into
any helper function would permanently consume it. You would have to manually thread
ownership back through return types:

```rust
// Tedious ownership threading without reborrowing:
impl Player {
    pub fn add_score(mut self: &mut Self, points: u8) -> &mut Self {
        self.score += points;
        self = self.print_score(); // Manually threading ownership back!
        self.score += 1;
        self
    }
}
```

This would make Rust tedious to write & difficult to read. Fortunately, Rust solves this
problem with **reborrowing**.

### What Is Reborrowing?

In plain English, **reborrowing means borrowing from an existing borrow**. Think of it
like borrowing a physical tool, and then lending it to your friend.

- You borrow (rent) a drill from Home Depot.
- You use it yourself to drill a hole.
- You need a friend to drill another hole for you before you continue.
- Rather than giving away the drill permanently to your friend (and the rental agreement
  from Home Depot), you hand it over to them just for that one hole.
- While they drill the hole, you can't use the drill.
- Once they finish, they hand the drill back, and you resume your work.
- When you are done with the drill, you have to return it to Home Depot.

> 🛑 **Important: This has nothing to do with threads, locks, or atomics!**
>
> When we say the parent reference is "paused" or "waiting", it is easy to think of
> concurrency:
>
> - _No multiple threads (`Send` / `Sync`)_: Reborrowing happens entirely within
>   single-threaded, sequential execution.
> - _No runtime locks or atomics_: There is no `Mutex`, semaphore, or atomic operation
>   involved. At runtime, references are just naked machine pointers.
> - _Purely compile-time_: The CPU thread never blocks or sleeps. The "pause" simply means
>   the compiler statically forbids you from writing code that uses the original reference
>   until the sub-borrow's lifetime expires.

In Rust, a **reborrow** creates a new, temporary reference pointing to the same memory as
an existing reference, without moving or consuming the original reference.

Every reborrow follows a 3-phase lifecycle:

1. **Child Reference Created:** Spawns a child reference with a shorter sub-lifetime
   bounded by the helper function call (or inner scope).
2. **Parent Reference Paused:** While the child borrow is live, the parent reference is
   temporarily suspended. It cannot be read from or written to.
3. **Parent Reference Restored:** Once the child borrow ends, the parent reference awakens
   with its full exclusive permissions restored.

### How the Compiler Desugars a Reborrow (`&mut *ref`)

When you write a helper call like `self.print_score()`, the compiler automatically inserts
an explicit reborrow under the hood instead of moving `self`:

```rust
Player::print_score(&mut *self);
```

Let's break down those two operators:

- `*self`: **Dereferences** the pointer to access the target value in place.
- `&mut (...)`: Takes a fresh, temporary mutable **borrow** of that target value.

```text
       Original Pointer (&mut Player)
                   │
                   ▼ (Dereference: *self)
         [ Target Memory Value ]
                   ▲
                   │ (Borrow again: &mut)
         New Child Reference (&'child mut Player)
```

> 💡 **Connecting the Dots: Why did `let r2 = r1;` move earlier, while method calls
> reborrow?**
>
> Reborrowing is an implicit **[coercion][rust-ref-coercions]** (compiler
> [**`autoreborrow`**][rustc-autoborrow]). The compiler automatically inserts this
> `&mut *r1` desugaring only at **coercion sites** where the expected target type is
> known:
>
> 1. Passing `r1` into a function expecting `&mut T`,
> 2. Calling an `&mut self` method like `self.print_score()`, or
> 3. Assigning with an explicit type annotation (`let r2: &mut _ = r1;`).
>
> In a bare `let r2 = r1;` (as shown in the earlier example), there is no expected target
> type to trigger coercion, so type inference assigns `r2` the exact type of `r1` and
> moves the non-`Copy` value!
>
> Reborrowing also enables **cross-type downgrading**: you can reborrow an `&mut T` as a
> temporary shared reference `&T` (e.g., `let r2: &_ = &*r1;` or calling an `&self` method
> from `&mut self`). This freezes the mutable reference into read-only mode until all
> shared readers finish.

### Putting It All Together

Here is how the Home Depot drill rental analogy maps 1:1 to the introductory `Player`
code, starting with the `main()` function:

| Real-World Step (Home Depot)          | Rust Code (`Player` Example)                               | Compiler Borrow State                                     |
| :------------------------------------ | :--------------------------------------------------------- | :-------------------------------------------------------- |
| **Rent drill from Home Depot**        | `player.add_score(10)` _(borrows `&mut player` as `self`)_ | Outer mutable borrow begins.                              |
| **You use the drill**                 | `self.score += points;`                                    | Parent reference performs mutation.                       |
| **Lend drill to friend for one hole** | `self.print_score()` _(desugars to `&mut *self`)_          | Child reborrow created with shorter lifetime (`'call`).   |
| **You wait while friend drills**      | _(Inside `print_score`)_                                   | Parent reference `self` is dormant / suspended.           |
| **Friend hands drill back**           | `print_score()` returns                                    | Child borrow ends; parent `self` is restored.             |
| **You resume drilling**               | `self.score += 1;`                                         | Parent reference has exclusive access again.              |
| **Return drill to Home Depot**        | `add_score()` returns to `main()`                          | Outer borrow ends; original owner `player` is accessible. |

## 2. How Non-Lexical Lifetimes (NLL) Revolutionized Borrow Checking

Prior to Rust 2018, borrow scopes were strictly **lexical**—tied directly to AST curly
braces (`{ ... }`). A borrow lasted until the closing `}`, even if it was never used
again. Reborrowing across local variable bindings in the same function required artificial
inner scopes:

```rust
// Rust 2015 (Pre-NLL): Artificial blocks were mandatory!
let mut x = 10;
let r1 = &mut x;
{
    let r2 = &mut *r1; // Reborrow r1
    *r2 += 1;
} // r2 dies at '}'. Only now is r1 restored!
*r1 += 1;
```

In the **Rust 2018 Edition** ([RFC 2094][rfc-2094]), the compiler introduced **Non-Lexical
Lifetimes ([`NLL`])**. Lifetimes are now computed from the compiler's [**Control Flow
Graph (CFG)**][cfg-wiki] and end at the **point of last actual use**:

```rust
// Rust 2018+ (NLL): Clean, flat reborrowing!
let mut x = 10;
let r1 = &mut x;

let r2 = &mut *r1; // r1 is suspended here
*r2 += 1;          // <-- LAST USE OF r2! r2 dies right here.

*r1 += 1;          // r1 is AUTOMATICALLY restored! No curly braces needed.
```

## 3. What "Pausing a Borrow" Actually Means Inside the Compiler

Borrow checking is a **100% static compile-time pass**. At runtime, references are just
raw machine pointers; there are no locks or runtime state flags.

### The "Interpreter Trap"

If you read Rust code with the mental model of an interpreter, imagining a runtime engine
tracking active references and overlapping lifespans, that model won't match what the
compiler does. Or if you mentally step into functions to see what they do with their
references, this approach won't match what the compiler does either.

1. **Static Compile Time Checks:** All borrow checks are resolved statically at compile
   time. There is no runtime involvement in the borrow checking process. Once the compiler
   is done, it strips out everything and for the binary, at runtime, references are just
   pointers with zero runtime overhead.
2. **Function Signature Only Analysis:** The compiler never peeks inside a function's body
   when analyzing the call. It treats function calls as opaque black boxes, relying
   strictly on the function signature to determine borrow validity.

### Compile-Time Loan Capabilities & Polonius

Inside `rustc`'s MIR `borrowck` (and formalized in the next-gen
[**Polonius**][polonius-book] borrow checker), references are tracked as abstract
**loans** and **capabilities**:

1. **Origin Tracking:** Declaring `let r1 = &mut c` creates an origin loan `LOAN1`
   granting exclusive capability to access `c`.
2. **Sub-Loan Derivation:** Reborrowing `let r2 = &mut *r1` spawns child loan `LOAN2`
   derived from `LOAN1`.
3. **Capability Suspension:** While `LOAN2` is in the CFG live set, `LOAN1`'s capability
   is marked **suspended (invalidated)**. Any attempt to directly access or use `r1` or
   `c` triggers a compile error (`E0503`), while attempting conflicting reborrows triggers
   `E0499` (mutable) or `E0502` (shared).
4. **Capability Restoration:** As soon as `LOAN2` is no longer live, it expires,
   reactivating `LOAN1`.

### Visualizing Loan Lifecycle vs. Runtime Stack

```text
Compile-Time (MIR Borrowck)                Runtime (CPU & Stack)
───────────────────────────                ─────────────────────

[ add_score: &mut self active (LOAN1) ]
         │
         ├─ Reborrow: &mut *self (LOAN2) ──►  Pushes stack frame: print_score()
         │  (LOAN1 SUSPENDED)                 Executes with raw pointer
         │                                    Pops stack frame (ret)
         ├─ LOAN2 expires (NLL) ───────────►  Caller resumes
         │  (LOAN1 RESTORED)
         ▼
[ add_score: self.score += 1 (LOAN1) ]
```

## 4. The Call Stack Does Not Enforce Safety

Reborrowing is most commonly encountered when calling methods like `self.print_score()`,
so it might seem that reborrowing is tied in some way to function calls and the call
stack. But "reborrowing is safe because the caller's stack frame is suspended while the
callee runs" is the wrong understanding.

The call stack plays no role in enforcing borrow safety. As documented in the
[rustc-dev-guide][rustc-borrowck], borrow checking is verified entirely at compile time on
the [Control Flow Graph (CFG)][cfg-wiki]. At runtime, lifetimes do not exist—references
are compiled directly down to raw machine pointers.

Reborrowing works inside a single function with **no function calls and no new stack
frames**:

```rust
fn flat_reborrow_single_frame() {
    let mut c = Counter::default();
    let r1 = &mut c;

    // --- SAME STACK FRAME
    let r2 = &mut *r1; // r1 is PAUSED right here!
    r2.inc();          // r2 is active; r1 cannot be used.
    // ---------------------
    r1.inc();          // r1 is RESTORED right here!
}
```

The stack is merely the runtime execution mechanism for synchronous code. In fact, in
optimized builds (`--release`), the compiler routinely **inlines** small helper methods
like `self.print_score()`. When inlined, **no stack frame is pushed or popped at runtime
whatsoever**—yet the code remains completely memory-safe. The compiler uses the function
call boundary as a natural lifetime limit (`'call`), but the safety proof is verified
entirely via static graph analysis before LLVM and code generation ever run.

## 5. Valid Sequential Delegation vs. Illegal Concurrent Aliasing

Rust's memory safety guarantees rest on one fundamental invariant: **Aliasing XOR
Mutability**. You can have any number of shared references (`&T`), OR you can have a
single mutable reference (`&mut T`), but you can never have both simultaneously.

Reborrowing does not violate this rule because access is delegated **sequentially** over
time. The parent loan is paused while the child loan is active, ensuring that only one
reference can access the target memory at any given point:

```text
Sequential Reborrowing (Legal):
[ Parent LOAN1 ] ──► [ Child LOAN2 (Parent Paused) ] ──► [ Parent LOAN1 Restored ]

Concurrent Aliasing (Illegal):
┌── [ Active LOAN1: &mut c ] ──┐
└── [ Active LOAN2: &mut c ] ──┴──► 💥 Overlapping mutable access to same memory!
```

To see the exact line where the compiler draws the boundary between legal delegation and
illegal aliasing, let's contrast two concrete examples:

### Example 1: Valid Sequential Delegation

> 🔗 _Companion file: [`valid.rs` in `rust-scratch/reborrow`][repo-valid]_

Calling helper methods sequentially delegates access temporally without ever having two
active mutable references at the same time:

```rust
#[derive(Debug, Default)]
pub struct Player {
    score: u8,
}

impl Player {
    pub fn add_score(&mut self, points: u8) {
        self.score += points;

        /* 1. Child reborrow creation */
        self.print_score();

        /* 2. Parent loan restoration */
        self.score += 1;
    }

    pub fn print_score(&mut self) {
        println!("Score is now: {:#?}", self.score);
    }
}

fn main() {
    let mut player = Player::default();
    player.add_score(10);
    player.print_score();
}
```

Here is what happens in the 2 steps:

1. **Child reborrow creation:** The compiler desugars `self.print_score()` into
   `Player::print_score(&mut *self);`:
    - `*self`: Dereferences the pointer to access the target `Player`.
    - `&mut (...)`: Creates a temporary child reborrow with a shorter lifetime for
      `print_score()`.
    - The parent `self` loan is paused for the duration of the `print_score()` call.
2. **Parent loan restoration:** When `print_score()` returns, its child loan ends. The
   compiler restores the parent `self` loan, granting it back exclusive mutable access so
   mutating `self.score += 1` succeeds.

### Example 2: Illegal Concurrent Aliasing

> 🔗 _Companion file: [`invalid.rs` in `rust-scratch/reborrow`][repo-invalid]_

Here are some examples of invalid accesses to the same memory to contrast with the valid
sequential delegation above.

```rust
#[derive(Default, Debug)]
pub struct Counter {
    count: u8,
}

impl Counter {
    pub fn inc(&mut self) -> u8 {
        self.count += 1;
        self.count
    }
}

pub fn bar(c_mut_1: &mut Counter, c_mut_2: &mut Counter) {
    c_mut_1.inc();
    c_mut_2.inc();
}
```

#### Attempt 1: Creating overlapping mutable references

Passing two mutable references to the same object into a single function call fails at
compile time:

```rust
let mut c = Counter::default();

bar(
    &mut c,
    &mut c // 💥 ERROR[E0499]: cannot borrow `c` as mutable
           //                  more than once at a time
);
```

Both references would be active simultaneously inside `bar(c_mut_1, c_mut_2)`. Unlike
sequential reborrowing where the first loan is paused while the second is active, here
both arguments would have concurrent mutable access to the same memory—directly violating
**Aliasing XOR Mutability**.

#### Attempt 2: Overlapping Borrows in the Same Scope

```rust
let r1 = &mut c; // 1st mutable borrow starts
let r2 = &mut c; // 💥 ERROR[E0499]: cannot borrow `c` as mutable
                 //                  more than once at a time
r2.inc();
r1.inc();        // r1 is used HERE, keeping it alive across r2's creation!
```

Because `r1` is used after `r2`, both mutable borrows to `c` are live at the same time in
the [`CFG`]. Since these are two independent borrows of `c` (rather than a reborrow
`let r2 = &mut *r1` that pauses `r1`), their overlapping live ranges violate **Aliasing
XOR Mutability**.

Note that even if `r2` were a reborrow (`let r2 = &mut *r1`), attempting to interleave
their usage (e.g. calling `r1.inc()` while `r2` is still used later) is equally forbidden
with `E0499`. Reborrowing is strictly hierarchical and sequential: the parent cannot wake
up until the child has completely finished.

## Conclusion & Further Reading

Reborrowing bridges the gap between Rust's strict ownership rules (where mutable
references cannot be copied, and are consumed when moved, aka, [affine
types][affine-types]) and everyday ergonomics. Whenever you delegate a mutable reference:

- The compiler creates a short-lived child loan: `&mut *reference`.
- The parent loan is safely suspended in the compiler's abstract state machine.
- NLL computes the exact point where the child loan expires.
- The parent reference awakens with exclusive access restored.

### Resources & Links

- Companion Repository: [**`rust-scratch/reborrow`**][repo-reborrow]
    - [Valid sequential delegation (`valid.rs`)][repo-valid]
    - [Illegal concurrent aliasing (`invalid.rs`)][repo-invalid]
- RFC 2094: [Non-Lexical Lifetimes (NLL)][rfc-2094]
- Polonius Project:
    - [The Polonius Book][polonius-book]
    - [Polonius Rules & Architecture][polonius-rules]
    - [Polonius WG Repository][polonius-repo]
    - [Polonius Tracking Issue #55078][polonius-tracking]
- rustc-dev-guide:
    - [Borrow Checking Overview][rustc-borrowck]
- Related developerlife.com deep dives:
    - [Build with Naz : Rust lifetimes (Subtyping and Variance)][dl-lifetimes]
    - [Build with Naz : Rust Typestate Pattern][dl-typestate]
    - [Build with Naz : Memory Latency & Cache Locality in Rust][dl-mem-latency]
    - [To Async or Not to Async: Building a Rust MCP Server][dl-mcp-server]

<!-- prettier-ignore-start -->

[affine-types]: https://en.wikipedia.org/wiki/Substructural_type_system#Affine_type_systems
[cfg-wiki]: https://en.wikipedia.org/wiki/Control-flow_graph
[CFG]: https://en.wikipedia.org/wiki/Control-flow_graph
[rustc-borrowck]: https://rustc-dev-guide.rust-lang.org/borrow_check.html
[repo-reborrow]: https://github.com/nazmulidris/rust-scratch/tree/main/reborrow
[repo-valid]: https://github.com/nazmulidris/rust-scratch/blob/main/reborrow/src/valid.rs
[repo-invalid]: https://github.com/nazmulidris/rust-scratch/blob/main/reborrow/src/invalid.rs
[rfc-2094]: https://rust-lang.github.io/rfcs/2094-nll.html
[`NLL`]: https://rust-lang.github.io/rfcs/2094-nll.html
[NLL]: https://rust-lang.github.io/rfcs/2094-nll.html
[polonius-book]: https://rust-lang.github.io/polonius/
[polonius-rules]: https://rust-lang.github.io/polonius/rules.html
[polonius-repo]: https://github.com/rust-lang/polonius
[polonius-tracking]: https://github.com/rust-lang/rust/issues/55078
[rust-ref-coercions]: https://doc.rust-lang.org/reference/type-coercions.html
[rustc-autoborrow]: https://doc.rust-lang.org/nightly/nightly-rustc/rustc_middle/ty/adjustment/enum.AutoBorrow.html
[dl-lifetimes]: https://developerlife.com/2024/09/02/rust-lifetimes/
[dl-typestate]: https://developerlife.com/2024/05/28/typestate-pattern-rust/
[dl-mem-latency]: https://developerlife.com/2025/05/19/rust-mem-latency/
[dl-mcp-server]: https://developerlife.com/2026/08/22/to-async-or-not-to-async-rust-mcp-server/

<!-- prettier-ignore-end -->

<!-- cspell:words reborrow reborrowing reborrows autoreborrow subtyping subloans deref noalias -->
<!-- cspell:words dereferencing callee mktoc Polonius borrowck liveness autoreborrow inlines -->
