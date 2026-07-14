---
title: "Build High-Performance Flat 2D Arrays in Rust (SIMD, L1 Cache)"
author: Nazmul Idris
date: 2026-07-14
excerpt: |
    Explore how to build high-performance 2D data structures in Rust. Learn about the
    differences between a simple Vec of Vecs approach and a flat 1D array leveraging
    contiguous memory, CPU L1 Cache, and SIMD optimization to prevent CPU pipeline stalls.
layout: post
categories:
    - Rust
    - CS
    - CLI
---

<!-- cspell:words Vecs mktoc flatline Amdahl's bitshift bitshifts memmoves memset -->
<!-- cspell:words memmove getconf DCACHE LINESIZE memcmp mispredictions mktemp darray -->
<!-- cspell:words prefetcher Superscalar ilog VPCMPEQB -->

<!-- BEGIN mktoc -->

- [Overview](#overview)
- [Quick Summary for Developers](#quick-summary-for-developers)
- [Project Setup](#project-setup)
- [The Simple Approach](#the-simple-approach)
- [The 1D Solution](#the-1d-solution)
    - [Ergonomic Array Access (`Index` and `IndexMut`)](#ergonomic-array-access-index-and-indexmut)
- [The 2D Iteration Trap](#the-2d-iteration-trap)
- [Unlocking SIMD & Raw Memory Operations](#unlocking-simd--raw-memory-operations)
- [Proving it with Benchmarks](#proving-it-with-benchmarks)
    - [1. Clear Screen](#1-clear-screen)
    - [2. Scroll Screen](#2-scroll-screen)
    - [3. Read Screen / Compositing](#3-read-screen--compositing)
    - [4. Memory Overhead](#4-memory-overhead)
    - [5. The 3-Step Performance Staircase](#5-the-3-step-performance-staircase)
    - [Note on primitive types](#note-on-primitive-types)
- [The CPU Cache & Hardware Prefetching](#the-cpu-cache--hardware-prefetching)
    - [How [SIMD] Vectorization Works](#how-simd-vectorization-works)
    - [Rule of Thumb for 1D vs 2D Memory Iteration](#rule-of-thumb-for-1d-vs-2d-memory-iteration)

<!-- END mktoc -->

## Overview

If you are building a Terminal UI, an image processor in Rust, or some other program where
you are going to need a 2D data structure to represent the screen or grid, this tutorial
will walk you through using a 2D array vs a 1D flat version of the same structure using
SIMD and leveraging the CPU's L1 cache. We will explore the performance implications of
how you structure this 2D data in memory by comparing these approaches.

Here are some useful links for context:

1. [Rust standard library: Vec](https://doc.rust-lang.org/std/vec/struct.Vec.html)
2. [Data-Oriented Design](https://en.wikipedia.org/wiki/Data-oriented_design)
3. [SIMD in Rust](https://doc.rust-lang.org/core/simd/index.html)

## Quick Summary for Developers

1. **Goal:**
    - Build a high-performance 2D array data structure in Rust suitable for tasks like UI
      compositing.
2. **Key Challenge:**
    - The immediate approach of using `Vec<Vec<T>>` introduces multiple heap allocations
      scattered randomly in memory. This leads to terrible CPU cache locality and massive
      pipeline stalls during iteration.
    - While using a flat 1D array (`Box<[T]>`) solves the cache locality problem, simple
      mathematical coordinate transformations (modulo and division) can still stall the
      CPU pipeline when iterating over the grid.
3. **Solution:**
    - Use a flat 1D array to guarantee contiguous memory layout and perfect L1 cache
      utilization.
    - Unlock SIMD auto-vectorization and raw pointer operations using `.fill()` for
      clearing, `.copy_within()` for scrolling, and `.chunks_exact(cols)` for rendering,
      completely avoiding slow division operations.
4. **What You'll Get:**
    - A highly performant 2D array implementation with flatline consistent frame times,
      offering significant speedups (e.g., 2.3x for reading/rendering, and up to 39.0x for
      memory size calculations).

## Project Setup

In this tutorial, we are going to build a high-performance 2D array in Rust. Before we
dive into the code, let's scaffold our project and enable the nightly toolchain so we can
run micro-benchmarks later to prove all our hypotheses and theory. It is important to
measure performance impact rather than rely on intuition.

As [Amdahl's Law](https://en.wikipedia.org/wiki/Amdahl%27s_law) teaches us, the overall
speedup of our program is strictly limited by the fraction of time spent in the code we
are optimizing. We use micro-benchmarks to ensure that iterating our 2D array is actually
the bottleneck worth attacking, rather than "optimizing" based on intuition.

```bash
# Create a temp folder for this, or choose where you would like to create your project.
cd (mktemp -d)
cargo new --lib flat2darray
cd flat2darray
rustup override set nightly
cargo add r3bl_tui
```

We don't need any external dependencies, so `Cargo.toml` is good to go. We just need to
configure our `lib.rs` to enable the benchmarking features and expose our modules.

```rust
pub mod vec_2d_array;
```

## The Simple Approach

The immediate, simple approach almost everyone takes is a "Vec of Vecs", creating a
`Vec2DArray` struct.

```rust
use r3bl_tui::{ColWidth, RowHeight};

pub struct Vec2DArray<T: Clone> {
    pub data: Vec<Vec<T>>,
    pub rows: RowHeight,
    pub cols: ColWidth,
}
```

To manipulate this grid, we need a few standard methods. Let's ground them in a real-world
Terminal UI use case:

1. **Iterate**: We need to traverse the grid cell-by-cell to render it to the terminal.
2. **Diffing**: We need to compare the old frame buffer with the new frame buffer to only
   redraw pixels that changed.
3. **Clearing**: We need to wipe all cells in the grid to handle a "clear screen" command.
4. **Scrolling**: We need to shift terminal history up by moving rows when a new line is
   printed at the bottom.

Here's how we might implement these scalar methods, along with a `.get_mem_size()` method
to calculate heap allocation size, and some unit tests:

````rust
impl<T: Copy + PartialEq + std::fmt::Debug> Vec2DArray<T> {
    pub fn new(rows: RowHeight, cols: ColWidth, default_val: T) -> Self {
        Self {
            data: vec![vec![default_val; cols.as_usize()]; rows.as_usize()],
            rows,
            cols,
        }
    }

    pub fn get(&self, row: usize, col: usize) -> &T {
        &self.data[row][col]
    }

    pub fn clear(&mut self, default_val: T) {
        let rows_usize = self.rows.as_usize();
        let cols_usize = self.cols.as_usize();
        for row in 0..rows_usize {
            for col in 0..cols_usize {
                self.data[row][col] = default_val.clone();
            }
        }
    }

    /// Scrolls the grid up by one row.
    ///
    /// # Logic
    /// Because `self.data` is a `Vec<Vec<T>>`, we don't actually need
    /// to copy the underlying elements. We can simply rotate the `Vec`
    /// of row pointers! `rotate_left(1)` moves the first row to the
    /// end, and shifts all other row pointers up by 1. This is extremely
    /// fast because it only moves memory pointers, not the actual items
    /// in the rows.
    ///
    /// # ASCII Diagram
    /// ```text
    /// Before:         After:
    /// [ Row 0 ]       [ Row 1 ]  <-- Shifted up
    /// [ Row 1 ]  ==>  [ Row 2 ]
    /// [ Row 2 ]       [ Row 2 ]  <-- Duplicated from above
    /// ```
    pub fn scroll_up(&mut self) {
        if !self.data.is_empty() {
            self.data.rotate_left(1);
            let len = self.data.len();
            if len > 1 {
                // After rotation, the old top row is now at the bottom.
                // To mimic `copy_within` (where the last row is left
                // untouched and thus duplicated), we overwrite this new
                // bottom row with a clone of the row just above it.
                self.data[len - 1] = self.data[len - 2].clone();
            }
        }
    }

    pub fn diff(&self, other: &Self) -> Vec<(usize, usize)> {
        let mut changes = Vec::new();
        let rows_usize = self.rows.as_usize();
        let cols_usize = self.cols.as_usize();
        for row in 0..rows_usize {
            for col in 0..cols_usize {
                if self.data[row][col] != other.data[row][col] {
                    changes.push((row, col));
                }
            }
        }
        changes
    }

    pub fn get_mem_size(&self) -> usize {
        // Struct.
        let mut total = std::mem::size_of::<Self>();

        // Vec<_>.
        let num_of_rows = self.data.capacity();
        total += num_of_rows * {
            let size_of_a_row = std::mem::size_of::<Vec<T>>();
            size_of_a_row
        };

        // Vec<T> for each row (containing the columns / cells).
        for row in &self.data {
            total += row.capacity() * std::mem::size_of::<T>();
        }

        total
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_vec_2d_array() {
        let mut grid = Vec2DArray::new(
            RowHeight::from(5), ColWidth::from(10), 0);

        // 1. Test clear & get
        grid.clear(1);
        assert_eq!(*grid.get(0, 0), 1);

        // 2. Test diff
        let mut other = Vec2DArray::new(
            RowHeight::from(5), ColWidth::from(10), 1);
        other.data[0][0] = 5;
        let changes = grid.diff(&other);
        assert_eq!(changes.len(), 1);
        assert_eq!(changes[0], (0, 0));

        // 3. Test scroll_up
        grid.data[0][0] = 9; // Top row, col 0
        grid.data[1][0] = 8; // Second row, col 0
        grid.scroll_up();
        // Second row should now be shifted to the top
        assert_eq!(*grid.get(0, 0), 8);

        // 4. Test memory size calculation
        assert!(grid.get_mem_size() > 0);
    }
}
````

But there is a major performance catch here. A `Vec<Vec<T>>` is terrible for iteration
because it requires multiple heap allocations scattered randomly in memory. This destroys
CPU cache locality. Because the CPU's Hardware Prefetcher can't predict where the next row
is, the pipeline suffers massive stalls—wasting up to 300 clock cycles fetching from slow
RAM instead of the 1 to 4 cycles it takes to read from the L1 Cache. By the end of this
post, we'll see exactly how much performance is lost with real benchmarks.

But don't throw away `Vec<Vec<T>>` entirely! I'll also show you one surprisingly elegant
trick where `Vec2DArray` actually wins: scrolling. Because it's an array of pointers, we
can use `rotate_left(1)` to scroll the screen by just shifting pointers, which is
lightning fast compared to moving contiguous bytes.

> For more info, read the production code on which this tutorial is based in the
> [`r3bl-open-core` repo](https://github.com/r3bl-org/r3bl-open-core/tree/main/tui/src/core/common/flat_2d_array/core.rs).

## The 1D Solution

First, let's expose our new module in `src/lib.rs`:

```rust
pub mod flat_2d_array;
```

The solution is to flatten our 2D grid into a single, contiguous 1D array using
`Box<[T]>`.

Why does this matter? Let's look at the memory layout.

```text
# Vec<Vec<T>> (Scattered Heap Memory):

[Ptr] -> [Ptr, Ptr, Ptr]
        |    |    |
        v    v    v
    [Row1] [Row2] [Row3]  <-- Cache Misses!

Box<[T]> (Contiguous Memory):
[Ptr] -> [Row1 | Row2 | Row3] <-- Perfect L1/L2 Cache Hits!
```

By guaranteeing a single contiguous memory allocation, the CPU's Hardware Prefetcher can
effortlessly pull data from RAM into the L1 Cache in perfect 64-byte chunks, known as
Cache Lines. To access any coordinate, we just use simple math:
`(row, col) -> index = row * cols + col`.

```text
# 2D to 1D Mapping

The grid is stored row-by-row in a flat 1D slice.

To find the element at `(row, col)`, we skip `row` full rows of size `width`,
and then step forward by `col`.

        col 0   col 1   col 2
      ┌───────┬───────┬───────┐
row 0 │ idx 0 │ idx 1 │ idx 2 │  ← row_offset = 0 * 3 = 0
      ├───────┼───────┼───────┤
row 1 │ idx 3 │ idx 4 │ idx 5 │  ← row_offset = 1 * 3 = 3
      ├───────┼───────┼───────┤
row 2 │ idx 6 │ idx 7 │ idx 8 │  ← row_offset = 2 * 3 = 6
      └───────┴───────┴───────┘

Example: `(row 1, col 2)`
- `row_offset = 1 * 3 = 3`
- `final_index = 3 + 2 = 5`
```

Conversely, we also need to be able to map a flat 1D index back to its 2D coordinates.
Here is a diagram illustrating the math behind that reverse mapping:

````text
# 1D to 2D Mapping

This is the exact inverse of the above. It is primarily used
during SIMD fast-path diffing, where the algorithm iterates linearly over the
1D slice, finds a difference at a specific 1D `index`, and needs to know the
corresponding `(row, col)` coordinate to issue a terminal cursor movement
command.

```text
        col 0   col 1   col 2
      ┌───────┬───────┬───────┐
row 0 │ idx 0 │ idx 1 │ idx 2 │
      ├───────┼───────┼───────┤
row 1 │ idx 3 │ idx 4 │ idx 5 │  ← index_to_pos(5)
      ├───────┼───────┼───────┤    = Pos { row: 1, col: 2 }
row 2 │ idx 6 │ idx 7 │ idx 8 │
      └───────┴───────┴───────┘
```

Example: `index 5` with `width 3`
- `row = index / width = 5 / 3 = 1`
- `col = index % width = 5 % 3 = 2`
````

Here's the implementation for the `Flat2DArray` struct, along with scalar methods and
tests:

```rust
use r3bl_tui::{ColWidth, RowHeight};

pub struct Flat2DArray<T: Clone> {
    pub data: Box<[T]>,
    pub rows: RowHeight,
    pub cols: ColWidth,
}

impl<T: Copy + PartialEq + std::fmt::Debug> Flat2DArray<T> {
    pub fn new(rows: RowHeight, cols: ColWidth, default_val: T) -> Self {
        let size = rows.as_usize() * cols.as_usize();
        Self {
            data: vec![default_val; size].into_boxed_slice(),
            rows,
            cols,
        }
    }

    pub fn get(&self, row: usize, col: usize) -> &T {
        &self.data[row * self.cols.as_usize() + col]
    }

    pub fn clear(&mut self, default_val: T) {
        let cols_usize = self.cols.as_usize();
        let rows_usize = self.rows.as_usize();
        for row in 0..rows_usize {
            for col in 0..cols_usize {
                self.data[row * cols_usize + col] = default_val.clone();
            }
        }
    }

    pub fn scroll_up(&mut self) {
        let cols_usize = self.cols.as_usize();
        let rows_usize = self.rows.as_usize();
        for row in 0..rows_usize - 1 {
            for col in 0..cols_usize {
                let src_idx = (row + 1) * cols_usize + col;
                let dest_idx = row * cols_usize + col;
                self.data[dest_idx] = self.data[src_idx].clone();
            }
        }
    }

    pub fn diff(&self, other: &Self) -> Vec<(usize, usize)> {
        let mut changes = Vec::new();
        let cols_usize = self.cols.as_usize();
        let rows_usize = self.rows.as_usize();
        for row in 0..rows_usize {
            for col in 0..cols_usize {
                let idx = row * cols_usize + col;
                if self.data[idx] != other.data[idx] {
                    changes.push((row, col));
                }
            }
        }
        changes
    }

    pub fn print_screen(&self) -> String {
        let mut buffer = String::new();

        let cols = self.cols.as_usize();
        for (index, item) in self.data.iter().enumerate() {
            // 2d -> 1d mapping (SLOW!)
            let row = index / cols;
            let col = index % cols;
            buffer.push_str(&format!("({row}, {col}): {item:?} | "));
        }

        buffer
    }

    pub fn get_mem_size(&self) -> usize {
        let mut total = std::mem::size_of::<Self>();
        total += self.data.len() * std::mem::size_of::<T>();
        total
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use r3bl_tui::{col, row};

    #[test]
    fn test_new() {
        let w = width(10);
        let h = height(10);
        let s = w + h;
        println!("s: {:?}", s);

        let grid = Flat2DArray::new(s, 0usize);
        let grid: Box<[usize]> = grid.data;
        println!("grid: {:?}", grid);

        let other = vec![
            /*default value*/ 0usize;
            /*size*/100
        ];

        let other: Box<[usize]> = other.into_boxed_slice();
        println!("other: {:?}", other);

        assert_eq!(/*100*/ grid.len(), /*100*/ other.len());
        assert_eq!(grid, other);
    }

    #[test]
    fn test_clear() {
        let w = width(10);
        let h = height(10);
        let s = w + h;
        let mut grid = Flat2DArray::new(s, 0usize);
        grid.clear(1usize);
        let other = vec![
            /*default value*/ 1usize;
            /*size*/100
        ]
        .into_boxed_slice();
        assert_eq!(grid.data, other);
    }

    #[test]
    fn test_get_mem_size() {
        let w = width(10);
        let h = height(10);
        let s = w + h;
        let grid = Flat2DArray::new(s, 0usize);
        let mem_size = grid.get_mem_size();
        assert_eq!(
            mem_size,
            std::mem::size_of::<Flat2DArray<usize>>()
                + 100 * std::mem::size_of::<usize>()
        );
    }

    #[test]
    fn test_print_screen() {
        let w = width(3);
        let h = height(3);
        let s = w + h;
        let grid = Flat2DArray::new(s, 0usize);
        let screen_output = grid.print_screen();
        println!("screen_output: {:?}", screen_output);
        let expected_output = "(0, 0): 0 | (0, 1): 0 | (0, 2): 0 |
            (1, 0): 0 | (1, 1): 0 | (1, 2): 0 |
            (2, 0): 0 | (2, 1): 0 | (2, 2): 0 | ";
        assert_eq!(screen_output, expected_output);
    }

    #[test]
    fn test_diff() {
        let w = width(2);
        let h = height(2);
        let s = w + h;
        let array1 = Flat2DArray::new(s, 0usize);

        // Modify some elements in array2 to create differences.
        let mut array2 = array1.clone();
        array2.data[1] /* 1d */ = 1; /* Change (0, 1) */
        array2.data[2] /* 1d */ = 1; /* Change (1, 0) */

        let changes = array1.diff(&array2);
        assert_eq!(changes.len(), 2);
        assert!(changes.contains(&(row(0) + col(1))));
        assert!(changes.contains(&(row(1) + col(0))));
    }

    #[test]
    fn test_scroll_up() {
        let cols = width(2);
        let rows = height(3);
        let s = cols + rows;
        let mut array = Flat2DArray::new(s, 0usize);

        // Fill the array with distinct values for testing.
        for row in 0..rows.as_usize() {
            for col in 0..cols.as_usize() {
                // 2d -> 1d mapping.
                let index = row * cols.as_usize() + col;
                // Fill with distinct value.
                array.data[index] = row * cols.as_usize() + col;
            }
        }

        // Scroll up and check the values.
        array.scroll_up();
        assert_eq!(array.data[0], 2); // Row 1 becomes Row 0
        assert_eq!(array.data[1], 3); // Row 1 becomes Row 0
        assert_eq!(array.data[2], 4); // Row 2 becomes Row 1
        assert_eq!(array.data[3], 5); // Row 2 becomes Row 1
        assert_eq!(array.data[4], 4); // Last row duplicates the new last row
        assert_eq!(array.data[5], 5); // Last row duplicates the new last row
    }
}
```

### Ergonomic Array Access (`Index` and `IndexMut`)

To make `Flat2DArray` feel just like `Vec2DArray`, we can implement the `Index` and
`IndexMut` traits for both `usize` (row index) and `Pos` (row + col coordinates):

```rust
use std::ops::{Index, IndexMut};
use r3bl_tui::Pos;

impl<T: Copy + PartialEq> Index<usize> for Flat2DArray<T> {
    type Output = [T];

    fn index(&self, row_index: usize) -> &Self::Output {
        let cols = self.cols.as_usize();
        let range_start = row_index * cols;
        let range_end = range_start + cols;
        &self.data[range_start..range_end]
    }
}

impl<T: Copy + PartialEq> IndexMut<usize> for Flat2DArray<T> {
    fn index_mut(&mut self, row_index: usize) -> &mut Self::Output {
        let cols = self.cols.as_usize();
        let range_start = row_index * cols;
        let range_end = range_start + cols;
        &mut self.data[range_start..range_end]
    }
}

impl<T: Copy + PartialEq> Index<Pos> for Flat2DArray<T> {
    type Output = [T];

    fn index(&self, pos: Pos) -> &Self::Output {
        let row = pos.row_index.as_usize();
        let col = pos.col_index.as_usize();
        let cols = self.cols.as_usize();
        let range_start = row * cols + col;
        let range_end = range_start + 1;
        &self.data[range_start..range_end]
    }
}

impl<T: Copy + PartialEq> IndexMut<Pos> for Flat2DArray<T> {
    fn index_mut(&mut self, pos: Pos) -> &mut Self::Output {
        let row = pos.row_index.as_usize();
        let col = pos.col_index.as_usize();
        let cols = self.cols.as_usize();
        let range_start = row * cols + col;
        let range_end = range_start + 1;
        &mut self.data[range_start..range_end]
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn array_access_syntax() {
        use r3bl_tui::{col, row};
        let w = width(10);
        let h = height(10);
        let s = w + h;

        // Index by usize.
        {
            let grid = Flat2DArray::new(s, 0usize);
            let row_slice: &[usize] = &grid[0];
            let cell = row_slice[0];
            assert_eq!(cell, 0);
            assert_eq!(grid[0][0], cell);
        }

        // IndexMut by usize.
        {
            let mut grid_mut = Flat2DArray::new(s, 0usize);
            grid_mut[0][0] = 42;
            assert_eq!(grid_mut[0][0], 42);
        }

        // Index by Pos.
        {
            let grid = Flat2DArray::new(s, 0usize);
            let pos = row(0) + col(0);
            let row_slice = &grid[pos];
            let cell = row_slice[0];
            assert_eq!(cell, 0);
        }

        // IndexMut by Pos.
        {
            let mut grid_mut = Flat2DArray::new(s, 0usize);
            let pos = row(0) + col(0);
            grid_mut[pos][0] = 42;
            assert_eq!(grid_mut[pos][0], 42);
        }
    }
}
```

## The 2D Iteration Trap

But wait, there is a trap here: **The Math Pipeline Stall Problem**. What if we need to
iterate over the whole grid, but we _still need_ to know our `(row, col)` coordinates to
know where to draw them? This is a common scenario in a Terminal UI, where we need to
render each pixel at its correct position (row and col) on the terminal emulator screen by
writing an ANSI escape sequence to `stdout`.

The simple way to iterate our flat array looks like what we see in `print_screen` above.

The trap is that division (`/`) and modulo (`%`) are extremely slow for the CPU. Now, if
our grid `cols` was a guaranteed compile-time constant _and_ a perfect power of two—like
128—the compiler is smart. It optimizes the math into lightning-fast bitshifts:

```rust
// Compiler optimization if cols is a hardcoded 128 (2^7):
let row = index >> 7;
let col = index & 127;
```

But here is the catch: In a Terminal UI, the columns count is almost never a power of two,
and it's a **runtime variable** because the user can resize their window at any time (for
example, to 113 columns). Because the compiler doesn't know this number at compile time,
it cannot use the bitshift trick. It is forced to emit actual, slow division instructions
to the CPU for every single pixel, causing significant pipeline stalls.

Here is a quick unit test demonstrating how this bitshift optimization works for these specific corner cases where the width is an exact power of 2:

```rust
#[cfg(test)]
mod corner_cases {
    #[test]
    fn slow_division_corner_case_speedup_using_bit_ops() {
        const COLS: usize = 128; // 2^7
        const SHIFT_AMT: u32 = COLS.ilog2(); // 7
        const MASK_AMT: usize = COLS - 1; // 127

        // 1d index to 2d mapping NOT using division
        // (bitshift) and modulo (bitwise AND).
        let index: usize = 5;
        let row = index >> SHIFT_AMT; // index / COLS
        let col = index & MASK_AMT; // index % COLS

        println!("index: {index}, row: {row}, col: {col}");
    }
}
```

## 5. Unlocking SIMD & Raw Memory Operations

So how do we fix it? We follow two simple rules of thumb for 1D memory access to replace
those slow scalar loops.

**Rule 1: If you DO care about 2D coordinates.** Let's say you're rendering or diffing
rows. The silver bullet here is `.chunks_exact(cols)`.

```rust
pub fn simd_print_screen(&self) -> String {
    let mut buffer = String::new();

    let cols /* chunk size / num cols / width */ = self.cols.as_usize();

    let rows_iter = self.data.chunks_exact(cols);
    debug_assert!(
        rows_iter.remainder().is_empty(),
        "The data length should be a multiple of the number of columns."
    );

    let rows_iter = rows_iter.enumerate();
    for (row_idx, row_chunk) in rows_iter {
        let cols_iter = row_chunk.iter().enumerate();
        for (col_idx, item) in cols_iter {
            buffer.push_str(
                &format!("({row_idx}, {col_idx}): {item:?} | "));
        }
    }

    buffer
}

pub fn simd_diff(&self, other: &Self) -> Vec<Pos> {
    let mut changes = Vec::new();

    let cols /* chunk size / num cols / width */ = self.cols.as_usize();

    let self_rows_iter = self.data.chunks_exact(cols);
    debug_assert!(
        self_rows_iter.remainder().is_empty(),
        "The data length should be a multiple of the number of columns."
    );

    let other_rows_iter = other.data.chunks_exact(cols);
    debug_assert!(
        other_rows_iter.remainder().is_empty(),
        "The data length should be a multiple of the number of columns."
    );

    let zipped_rows_iter = self_rows_iter.zip(other_rows_iter).enumerate();
    for (row_idx, (self_row_chunk, other_row_chunk)) in zipped_rows_iter {
        if self_row_chunk != other_row_chunk {
            let cols_iter = self_row_chunk.iter()
                .zip(other_row_chunk.iter())
                .enumerate();
            for (col_idx, (s, o)) in cols_iter {
                if s != o {
                    let row: RowIndex = row_idx.into();
                    let col: ColIndex = col_idx.into();
                    changes.push(row + col);
                }
            }
        }
    }

    changes
}
```

The performance wins here are massive, happening at multiple layers of the CPU:

1. **Bypassing the Math Pipeline:** Under the hood, this doesn't use division (`/`) or
   modulo (`%`). It uses pure **pointer addition**, just adding `cols` to the memory
   pointer for each row.
2. **Eliding Bounds Checks:** By `zip()`ing `chunks_exact` together, we prove to the
   compiler at compile-time that both iterators have the exact same length. LLVM
   completely removes bounds checks from the inner loops, preventing branch
   mispredictions.

Here is the magic behind how that works for comparing two separate chunks of RAM (`self`
and `other`):

### Multi-Stream Hardware Prefetching

The CPU's hardware prefetcher isn't limited to tracking just one stream of memory. Modern
CPUs (like Intel, AMD, and Apple Silicon) can track multiple independent, sequential
memory streams simultaneously (often up to 16 or 32 streams at a time).

Because `simd_diff` iterates linearly through `self.data` and linearly through
`other.data`, the prefetcher quickly recognizes two distinct linear access patterns. It
fires off requests to RAM for both streams concurrently, pulling the next 64-byte Cache
Lines for both `self` and `other` into the L1 Cache ahead of time.

### Dual-Ported L1 Cache

L1 Caches on modern CPUs are usually "multi-ported." This means the CPU doesn't have to
wait to read `self` on cycle 1 and `other` on cycle 2. It can literally fetch data from
two completely different memory addresses in the L1 cache in the exact same clock cycle.

### SIMD Registers and Superscalar Execution

Once the data is sitting in the L1 cache, the CPU executes the equality check
(`if self_row_chunk != other_row_chunk`):

1. It issues two SIMD load instructions (e.g., pulling 32 bytes of `self` into register
   `YMM0` and 32 bytes of `other` into register `YMM1`).
2. Because CPUs are "superscalar" (meaning they can execute multiple instructions per
   cycle), it loads both registers at nearly the exact same time.
3. It then issues a single SIMD compare instruction (like `VPCMPEQB` in x86 AVX2).

While the latency of the entire pipeline (fetch, decode, load, compare) takes several
cycles, the CPU overlaps these operations in an assembly line (pipelining). The result is
a throughput of one massive 32-byte or 64-byte comparison retiring every single clock
cycle.

So, because the memory access is perfectly linear for both arrays, the hardware prefetcher
and L1 Cache perfectly spoon-feed the SIMD registers without ever starving the CPU!

**Rule 2: If you DON'T care about 2D coordinates.** Let's say you just need to clear the
screen or scroll memory. You don't need chunks. Just blast through the entire raw 1D slice
using `.fill()` for instant clearing.

```rust
pub fn simd_clear(&mut self, default_val: T) {
    self.data.fill(default_val);
}
```

Because it's an uninterrupted memory block, LLVM aggressively auto-vectorizes this into
SIMD instructions. But here's the kicker: `.fill()` doesn't _read_ data, it _writes_ data.
LLVM translates this into ultra-wide SIMD Store instructions (acting like a massive `memset`).
Instead of writing one character at a time, the CPU blasts 32 or 64 bytes of the
`default_val` directly into the L1 Cache in a single clock cycle!

If your array is larger than a SIMD register, LLVM handles the magic: it creates a highly
optimized loop, unrolls it to keep the CPU pipeline saturated, and generates a 'scalar
tail' to perfectly clean up any leftover bytes at the end of the array.

For scrolling, we use `.copy_within()`. This is incredibly fast because it maps directly
to `std::ptr::copy` (which acts as a highly optimized SIMD `memmove`). It shifts huge
contiguous blocks of memory in bulk rather than moving elements one by one. However, as
we'll see in the benchmarks, this is actually one scenario where `Vec2DArray` beats the
Flat Array, simply because shifting memory pointers is faster than copying actual
contiguous bytes!

```rust
/// Scrolls the grid up by one row.
///
/// # Logic
/// Because `self.data` is a flat 1D array, we shift the entire contiguous
/// block of memory left by `cols` elements. The `copy_within` method maps
/// directly to a highly optimized `memmove` operation, safely copying
/// overlapping memory regions in bulk.
///
/// # ASCII Diagram
/// ```text
/// Before:                           | After:
/// [ Row 0 | Row 1 | Row 2 | Row 3 ] | [ Row 1 | Row 2 | Row 3 | Row 3 ]
///           ^^^^^^^^^^^^^^^^^^^^^   |   ^^^^^^^^^^^^^^^^^^^^^   ^^^
///             Copied and shifted    |   Pasted at index 0       Duplicated
/// ```
pub fn simd_scroll_up(&mut self) {
    let src_range = self.cols.as_usize()..;
    self.data.copy_within(src_range, /*starting index*/ 0);
}
```


```rust
#[cfg(test)]
mod tests {
    use super::*;
    use r3bl_tui::{col, row};

    #[test]
    fn test_simd_print_screen() {
        let w = width(3);
        let h = height(3);
        let s = w + h;
        let grid = Flat2DArray::new(s, 0usize);

        // SIMD/Vectorized version.
        let screen_output = grid.simd_print_screen();
        println!("screen_output: {:?}", screen_output);
        let expected_output_vectorized =
           "(0, 0): 0 | (0, 1): 0 | (0, 2): 0 |
            (1, 0): 0 | (1, 1): 0 | (1, 2): 0 |
            (2, 0): 0 | (2, 1): 0 | (2, 2): 0 | ";
        assert_eq!(screen_output, expected_output_vectorized);

        // Scalar version.
        let expected_output_scalar = grid.print_screen();
        assert_eq!(expected_output_vectorized, expected_output_scalar);
    }

    #[test]
    fn test_simd_diff() {
        let w = width(2);
        let h = height(2);
        let s = w + h;
        let self_array = Flat2DArray::new(s, 0usize);

        // Modify some elements in array2 to create differences.
        let mut other_array = self_array.clone();
        other_array.data[1] /* 1d */ = 1; /* Change (0, 1) */
        other_array.data[2] /* 1d */ = 1; /* Change (1, 0) */

        let simd_changes = self_array.simd_diff(&other_array);
        assert_eq!(simd_changes.len(), 2);
        assert!(simd_changes.contains(&(row(0) + col(1))));
        assert!(simd_changes.contains(&(row(1) + col(0))));

        // Compare to scalar diff to ensure they produce the same results.
        let scalar_changes = self_array.diff(&other_array);
        assert_eq!(simd_changes, scalar_changes);
    }

    #[test]
    fn test_simd_clear() {
        let w = width(10);
        let h = height(10);
        let s = w + h;

        let mut self_grid = Flat2DArray::new(s, 0usize);
        self_grid.simd_clear(1usize);

        let other_grid = vec![
            /*default value*/ 1usize;
            /*size*/100
        ]
        .into_boxed_slice();

        assert_eq!(self_grid.data, other_grid);
    }

    #[test]
    fn test_simd_scroll() {
        let cols = width(2);
        let rows = height(3);
        let s = cols + rows;
        let mut og_array = Flat2DArray::new(s, 0usize);
        for row in 0..rows.as_usize() {
            for col in 0..cols.as_usize() {
                // 2d -> 1d mapping.
                let index = row * cols.as_usize() + col;
                // Fill with distinct value.
                og_array.data[index] = row * cols.as_usize() + col;
            }
        }

        let array_1_simd_scroll = {
            let mut array = og_array.clone();
            // Scroll up and check the values.
            array.simd_scroll_up();
            assert_eq!(array.data[0], 2); // Row 1 becomes Row 0
            assert_eq!(array.data[1], 3); // Row 1 becomes Row 0
            assert_eq!(array.data[2], 4); // Row 2 becomes Row 1
            assert_eq!(array.data[3], 5); // Row 2 becomes Row 1}
            array
        };

        let array_2_scalar_scroll = {
            let mut array = og_array.clone();
            // Scroll up and check the values.
            array.scroll_up();
            assert_eq!(array.data[0], 2); // Row 1 becomes Row 0
            assert_eq!(array.data[1], 3); // Row 1 becomes Row 0
            assert_eq!(array.data[2], 4); // Row 2 becomes Row 1
            assert_eq!(array.data[3], 5); // Row 2 becomes Row 1}
            array
        };

        assert_eq!(array_1_simd_scroll.data, array_2_scalar_scroll.data);
    }
}
```

## Proving it with Benchmarks

We've implemented both `Vec2DArray` and `Flat2DArray`. Let's look at the benchmarks. To
run `cargo bench`, we first need to configure `lib.rs`:

```rust
// We need this for cargo bench to work.
#![cfg_attr(test, feature(test))]

#[cfg(test)]
mod benches;
```

And then we setup `src/benches.rs`. We define two sizes to test: one that easily fits into the CPU's L1 cache, and a realistic terminal size that spills out of it:

```rust
// Copyright (c) 2026 Nazmul Idris. Licensed under Apache License, Version 2.0.

#![allow(
    dead_code,
    unused_variables,
    unused_mut,
    unused_imports,
    clippy::wildcard_imports
)]

extern crate test;

use crate::flat_2d_array::Flat2DArray;
use crate::vec_2d_array::Vec2DArray;
use r3bl_tui::{ColWidth, PixelChar, RowHeight, Size, height, width};
use test::{Bencher, black_box};

// Intel CPU:
// p core - 48K L1 cache
// e core - 32K L1 cache

mod fits_l1_cache {
    use super::*;

    const WIDTH: usize = 30;
    const HEIGHT: usize = 30;

    pub fn size() -> Size {
        width(WIDTH) + height(HEIGHT)
    }
}

mod spills_l1_cache {
    use super::*;

    const WIDTH: usize = 200;
    const HEIGHT: usize = 100;

    pub fn size() -> Size {
        width(WIDTH) + height(HEIGHT)
    }
}
```

**Crucial Point:** First, before we even look at average speed, look at the **Margin of
Error**. `Vec2DArray` suffers from massive variance—sometimes swinging by ±98%—because its
performance relies entirely on lucky CPU cache placement for scattered heap allocations.
`Flat2DArray` guarantees perfectly consistent, flatline frame times. In a UI, eliminating
those micro-stutters is just as important as raw speed!

Let's validate our theories across 6 groups of operations.

### 1. Clear Screen

```rust
#[bench]
fn fits_l1_g1_clear_screen_vec2darray_scalar(b: &mut Bencher) {
    let size = fits_l1_cache::size();
    let mut grid = Vec2DArray::<PixelChar>::new(
        size, PixelChar::default());
    println!("Vec2DArray -> grid size: {:?}",
        grid.get_mem_size());
    b.iter(|| grid.clear(black_box(PixelChar::Void)));
}

#[bench]
fn fits_l1_g1_clear_screen_flat1darray_scalar(b: &mut Bencher) {
    let size = fits_l1_cache::size();
    let mut grid = Flat2DArray::<PixelChar>::new(
        size, PixelChar::default());
    println!("Flat2DArray -> grid size: {:?}",
        grid.get_mem_size());
    b.iter(|| grid.clear(black_box(PixelChar::Void)));
}

#[bench]
fn fits_l1_g1_clear_screen_flat1darray_simd(b: &mut Bencher) {
    let size = fits_l1_cache::size();
    let mut grid = Flat2DArray::<PixelChar>::new(
        size, PixelChar::default());
    println!("Flat2DArray -> grid size: {:?}", grid
        .get_mem_size());
    b.iter(|| grid.simd_clear(black_box(PixelChar::Void)));
}

#[bench]
fn spills_l1_g1_clear_screen_vec2darray_scalar(b: &mut Bencher) {
    let size = spills_l1_cache::size();
    let mut grid = Vec2DArray::<PixelChar>::new(
        size, PixelChar::default());
    println!("Vec2DArray -> grid size: {:?}",
        grid.get_mem_size());
    b.iter(|| grid.clear(black_box(PixelChar::Void)));
}

#[bench]
fn spills_l1_g1_clear_screen_flat1darray_scalar(b: &mut Bencher) {
    let size = spills_l1_cache::size();
    let mut grid = Flat2DArray::<PixelChar>::new(
        size, PixelChar::default());
    println!("Flat2DArray -> grid size: {:?}",
        grid.get_mem_size());
    b.iter(|| grid.clear(black_box(PixelChar::Void)));
}

#[bench]
fn spills_l1_g1_clear_screen_flat1darray_simd(b: &mut Bencher) {
    let size = spills_l1_cache::size();
    let mut grid = Flat2DArray::<PixelChar>::new(
        size, PixelChar::default());
    println!("Flat2DArray -> grid size: {:?}",
        grid.get_mem_size());
    b.iter(|| grid.simd_clear(black_box(PixelChar::Void)));
}
```

A pure 1D `.fill()` is consistently faster than a scalar row-by-row clear loop, giving us
a **1.4x speedup**.

### 2. Scroll Screen

```rust
#[bench]
fn spills_l1_g2_scroll_up_vec2darray_scalar(b: &mut Bencher) {
    let size = spills_l1_cache::size();
    let mut grid = Vec2DArray::<PixelChar>::new(
        size, PixelChar::default());
    println!("Vec2DArray -> grid size: {:?}",
        grid.get_mem_size());
    b.iter(|| grid.scroll_up());
}

#[bench]
fn spills_l1_g2_scroll_up_flat1darray_simd(b: &mut Bencher) {
    let size = spills_l1_cache::size();
    let mut grid = Flat2DArray::<PixelChar>::new(
        size, PixelChar::default());
    println!("Flat2DArray -> grid size: {:?}",
        grid.get_mem_size());
    b.iter(|| grid.simd_scroll_up());
}
```

This is the one rare case where the simple `Vec2DArray` might actually win! Because the
simple approach uses `rotate_left(1)` to just shift pointer addresses instead of copying
actual contiguous bytes, it is extremely fast. That's a very neat tradeoff: the simple 2D
`Vec` is great for row-swapping pointer operations, but it suffers cache misses on
traversal. The Flat 1D Array (`.copy_within()`) has to move the actual memory bytes, but
it rules at rendering and cache-locality!

### 3. Read Screen / Compositing

```rust
#[bench]
fn spills_l1_g3_print_screen_vec2darray_scalar(b: &mut Bencher) {
    let size = spills_l1_cache::size();
    let mut grid = Vec2DArray::<PixelChar>::new(
        size, PixelChar::default());
    println!("Vec2DArray -> grid size: {:?}",
        grid.get_mem_size());
    b.iter(|| {
        for row in 0..grid.rows.as_usize() {
            for col in 0..grid.cols.as_usize() {
                let _ = black_box(grid.data[row][col]);
            }
        }
    });
}

#[bench]
fn spills_l1_g3_print_screen_flat1darray_simd(b: &mut Bencher) {
    let size = spills_l1_cache::size();
    let mut grid = Flat2DArray::<PixelChar>::new(
        size, PixelChar::default());
    println!("Flat2DArray -> grid size: {:?}",
        grid.get_mem_size());
    b.iter(|| {
        for item in grid.data.iter() {
            let _ = black_box(item);
        }
    });
}
```

Here is **The Rendering Problem**. The first two tests were for _writing_ memory. But when
the compositor tries to _read_ the screen, linearly streaming flat memory into the L1
cache completely destroys nested vector heap-chasing, which constantly causes cache
misses. We see a massive **2.3x speedup**.

### 4. Diff Benchmarks

```rust
#[bench]
fn spills_l1_g4_diff_vec2darray_scalar(b: &mut Bencher) {
    let size = spills_l1_cache::size();

    let mut grid_1 = Vec2DArray::<PixelChar>::new(
        size, PixelChar::Void);
    println!("Vec2DArray -> grid size: {:?}",
        grid_1.get_mem_size());

    let mut grid_2 = Vec2DArray::<PixelChar>::new(
        size, PixelChar::Void);
    grid_2.data[50][50] = PixelChar::Spacer;

    b.iter(|| {
        let _ = black_box(&grid_1.diff(&grid_2));
    });
}

#[bench]
fn spills_l1_g4_diff_flat1darray_simd(b: &mut Bencher) {
    let size = spills_l1_cache::size();

    let mut grid_1 = Flat2DArray::<PixelChar>::new(
        size, PixelChar::Void);
    println!("Flat2DArray -> grid size: {:?}",
        grid_1.get_mem_size());

    let mut grid_2 = Flat2DArray::<PixelChar>::new(
        size, PixelChar::Void);
    grid_2[50][50] = PixelChar::Spacer;

    b.iter(|| {
        let _ = black_box(&grid_1.diff(&grid_2));
    });
}
```

The SIMD approach yields much tighter variance and faster diff execution when rendering frames!

### 5. Memory Overhead

```rust
#[bench]
fn spills_l1_g5_mem_size_vec2darray_scalar(b: &mut Bencher) {
    let size = spills_l1_cache::size();
    let grid = Vec2DArray::<PixelChar>::new(size,
        PixelChar::default());
    println!("Vec2DArray -> grid size: {:?}",
        grid.get_mem_size());
    b.iter(|| {
        let _ = black_box(grid.get_mem_size());
    });
}

#[bench]
fn spills_l1_g5_mem_size_flat1darray_simd(b: &mut Bencher) {
    let size = spills_l1_cache::size();
    let grid = Flat2DArray::<PixelChar>::new(
        size, PixelChar::default());
    println!("Flat2DArray -> grid size: {:?}",
        grid.get_mem_size());
    b.iter(|| {
        let _ = black_box(grid.get_mem_size());
    });
}
```

Calculating the size of `Vec<Vec<T>>` has massive pointer-chasing overhead, while
`Box<[T]>` is near-instantaneous. A whopping **39.0x speedup**!

### 6. The 3-Step Performance Staircase

```rust
#[bench]
fn spills_l1_g6_traversal_by_row_col_vec2darray_scalar(b: &mut Bencher) {
    let size = spills_l1_cache::size();
    let mut grid = Vec2DArray::<PixelChar>::new(
        size, PixelChar::default());
    println!("Vec2DArray -> grid size: {:?}",
        grid.get_mem_size());
    b.iter(|| {
        for row in 0..grid.rows.as_usize() {
            for col in 0..grid.cols.as_usize() {
                let _ = black_box((row, col, grid.data[row][col]));
            }
        }
    });
}

#[bench]
fn spills_l1_g6_traversal_by_row_col_flat1darray_simd_mod_and_div(b: &mut Bencher) {
    let size = spills_l1_cache::size();
    let mut grid = Flat2DArray::<PixelChar>::new(
        size, PixelChar::default());
    println!("Flat2DArray -> grid size: {:?}",
        grid.get_mem_size());
    b.iter(|| {
        for (idx, item) in grid.data.iter().enumerate() {
            let row = idx / grid.cols.as_usize();
            let col = idx % grid.cols.as_usize();
            let _ = black_box((row, col, item));
        }
    });
}

#[bench]
fn spills_l1_g6_traversal_by_row_col_flat1darray_simd(b: &mut Bencher) {
    let size = spills_l1_cache::size();
    let mut grid = Flat2DArray::<PixelChar>::new(
        size, PixelChar::default());
    println!("Flat2DArray -> grid size: {:?}",
        grid.get_mem_size());
    b.iter(|| {
        grid.data
            .chunks_exact(grid.cols.as_usize())
            .enumerate()
            .for_each(|(row, chunk)| {
                chunk.iter().enumerate().for_each(|(col, item)| {
                    let _ = black_box((row, col, item));
                });
            });
    });
}
```

This proves the Math Pipeline Stall theory. We benchmarked 3 traversal methods head-to-head to prove the **1.8x speedup**.

```text
1. Vec2DArray  (Scalar) - Slowest (Cache Misses & Modulo Math)
2. Flat2DArray (Scalar) - Fast (Cache Hits! But Modulo Math stalls)
3. Flat2DArray (SIMD)   - Fastest (Cache Hits & pure pointer addition!)
```

### Note on primitive types

The benchmarks above were executed using a multi-byte struct representing a colored
terminal pixel. When the grid relies on simple primitive integers (such as a `usize`),
LLVM can optimize the SIMD operations more aggressively. In our tests, clearing the screen
with primitive types resulted in up to a 60,000x speedup.

By flattening the 2D array, leveraging SIMD, and ensuring contiguous memory allocation, we
can significantly reduce CPU pipeline stalls and improve overall traversal performance.

## The CPU Cache & Hardware Prefetching

To understand why [`Flat2DArray`] is so fast, you must understand how data travels from
your RAM to the CPU. Data does not travel 1 byte at a time; it is transferred in exact
64-byte blocks (on modern x86 CPUs) called **[Cache Line]s** (you can verify this on x86
CPUs by running `getconf LEVEL1_DCACHE_LINESIZE` on Linux).

When your code asks for a memory address, the memory controller fetches a 64-byte [Cache
Line] from [RAM] and places it into the CPU's **[L1 Cache]**. The CPU Registers (where the
actual math happens) are fed exclusively from this [L1 Cache].

**The [Hardware Prefetcher] (The Conveyor Belt):** Modern CPUs have a dedicated circuit
called the [Hardware Prefetcher]. When you iterate over a contiguous slice of memory (like
[`Flat2DArray`]), the [Hardware Prefetcher] detects that you are moving forward in a
straight line. Before your code even asks for the next block of memory, the [Hardware
Prefetcher] secretly reaches out to [RAM], grabs the _next_ 64-byte [Cache Line], and
places it into the [L1 Cache]. This turns the [L1 Cache] into a high-speed conveyor belt,
ensuring the CPU never has to wait for data (zero Cache Misses).

**The Fragmentation Penalty:** If we had used nested vectors (`Vec<Vec<T>>`) we would
incur a hardware penalty. Because vectors are allocated randomly on the [heap], Row 0 and
Row 1 were not physically next to each other in [RAM]. The [Hardware Prefetcher] could not
predict where the next row would be, causing it to guess wrong. The CPU would suffer a
massive Cache Miss for every single row.

To quantify this penalty (using an Intel i7-14700 as an example):

- **L1 Cache Hit** (~32 KB size): ~1-4 clock cycles
- **L2 Cache Hit** (~4 MB size): ~10-15 clock cycles
- **L3 Cache Hit** (~33 MB size): ~40-70 clock cycles
- **Main RAM Fetch (Cache Miss)**: ~200-300+ clock cycles

The CPU pipeline would suffer a stall, wasting ~300 clock cycles per row while it waited
for the memory controller to fetch data from slow [RAM].

### How [SIMD] Vectorization Works

[SIMD] (Single Instruction, Multiple Data) is a CPU feature that allows the processor to
perform the same mathematical operation on multiple data points simultaneously. [SIMD]
acts as the engine that consumes the [L1 Cache] conveyor belt.

We do not have to write raw [Assembly] or use [`std::simd`] to trigger this. Instead, we
rely on **[LLVM] Auto-vectorization**. Because our 2D vector is now a flat, contiguous 1D
array, we can use built-in Rust [`slice`] operations. [LLVM] recognizes these operations
and automatically injects [AVX/NEON] [SIMD] instructions. These SIMD instructions operate
on specialized, ultra-wide CPU registers that are 256-bit (32 bytes) or 512-bit (64 bytes)
wide. Because these registers are perfectly aligned with the 64-byte Cache Lines sitting
in the [L1 Cache], they can consume and process massive blocks of data in a single clock
cycle.

If the array is larger than the [SIMD] register (which it almost always is), [LLVM]
automatically generates a highly optimized loop. It chunks the array into 32-byte or
64-byte blocks, unrolls the loop to keep the CPU pipeline saturated, and generates a
"scalar tail" to clean up any leftover bytes at the end that don't divide perfectly into
the register size.

Here are the exact triggers we use to unlock [SIMD]:

1. **[`slice::fill`] ([SIMD] [`memset`])**: Used when clearing the screen (e.g.,
   [`Flat2DArray::new_empty`]) to instantly blast empty spacer characters across memory.
2. **[`slice::copy_within`] ([SIMD] [`memmove`])**: Used when scrolling by the [virtual
   terminal tab], e.g., [`Flat1DSimdMut::copy_within_rows`], or when shifting characters
   left/right during text insertion.
3. **[`Iterator::zip`] ([SIMD] [`memcmp`])**: During the diffing phase, [LLVM] vectorizes
   the equality checks of two contiguous slices, allowing it to rapidly jump over massive
   blocks of identical characters.

### Rule of Thumb for 1D vs 2D Memory Iteration

1. **If you DON'T care about 2D coordinates** (e.g., just clearing the whole screen, or
   finding the first occurrence of a character): You don't even need chunks. Just blast
   through the entire raw 1D slice ([`.iter()`], [`.fill()`], etc.). [LLVM] will
   aggressively vectorize this into [SIMD] instructions because it's just one massive,
   uninterrupted block of memory.

2. **If you DO care about 2D coordinates** (e.g., diffing rows, tracking `col_index`, or
   knowing when a line ends): [`.chunks_exact(width)`] is the key.

    - **The Math Pipeline Stall Problem (The Slow Way)**. The simple approach uses
      division (`/`) and modulo (`%`) to calculate coordinates from a 1D index (e.g.,
      `row = index / width`, `col = index % width`). In the computer world, division and
      modulo are extremely slow mathematical operations. If your width was a fixed number
      like 8 or 16 (powers of 2), the compiler could use a lightning-fast bitshift. But
      because terminal widths vary at runtime (e.g., 113 columns), the compiler cannot
      optimize this. The CPU is forced to stop and wait for the math to finish for every
      single character on the screen, causing massive CPU pipeline stalls.

    - **The Chunks Exact Solution (The Fast Way)**. By slicing the array into rows via
      [`.chunks_exact(width)`], you walk down the chunks and their items (e.g.,
      `for (row_idx, chunk)` and `for (col_idx, item)`). Under the hood,
      [`.chunks_exact(width)`] doesn't calculate 2D coordinates from a 1D index using
      division. Instead, it uses simple **pointer addition**. For example, if the terminal
      is 113 columns wide, the outer loop just adds 113 to the memory pointer for each
      row. The inner loop adds 1 to the pointer for each column. Because addition takes 1
      clock cycle (unlike division, which takes many), 113 becomes just as fast for the
      CPU to process as a power of 2 like 128. You get logical 2D row boundaries to write
      easy-to-understand code, while the [LLVM] compiler sees a predictable contiguous
      memory layout. It will happily unroll that double loop and vectorize the inner slice
      comparisons into [SIMD] instructions—all while completely bypassing the slow CPU
      pipeline stalls.

<!-- prettier-ignore-start -->
[`Flat1DSimdMut::copy_within_rows`]: https://github.com/r3bl-org/r3bl-open-core/tree/main/tui/src/core/common/flat_2d_array/array_1d_simd_access.rs
[`Flat2DArray::new_empty`]: https://github.com/r3bl-org/r3bl-open-core/tree/main/tui/src/core/common/flat_2d_array/core.rs
[`Flat2DArray`]: https://github.com/r3bl-org/r3bl-open-core/tree/main/tui/src/core/common/flat_2d_array/core.rs
[virtual terminal tab]: https://docs.rs/r3bl_tui/latest/r3bl_tui/pty_mux/index.html#virtual-terminal-architecture-the-virtual-tab-mental-model
[`.as_raw_mut_slice().fill()`]: https://doc.rust-lang.org/std/primitive.slice.html#method.fill
[`.chunks_exact(width).zip(other.chunks_exact(width))`]: https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.zip
[`.chunks_exact(width)`]: https://doc.rust-lang.org/std/primitive.slice.html#method.chunks_exact
[`.fill()`]: https://doc.rust-lang.org/std/primitive.slice.html#method.fill
[`.iter()`]: https://doc.rust-lang.org/std/primitive.slice.html#method.iter
[`Canvas::clear_canvas`]: https://docs.rs/r3bl_tui/latest/r3bl_tui/core/ansi/vt_100_pty_output_parser/struct.Canvas.html#method.clear_canvas
[`Canvas`]: https://docs.rs/r3bl_tui/latest/r3bl_tui/core/ansi/vt_100_pty_output_parser/struct.Canvas.html
[`Iterator::zip`]: https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.zip
[`memcmp`]: https://doc.rust-lang.org/std/primitive.slice.html
[`memmove`]: https://doc.rust-lang.org/std/ptr/fn.copy.html
[`memset`]: https://doc.rust-lang.org/std/primitive.slice.html#method.fill
[`OfsBuf::diff`]: https://docs.rs/r3bl_tui/latest/r3bl_tui/struct.OfsBuf.html#method.diff
[`OfsBuf`]: https://docs.rs/r3bl_tui/latest/r3bl_tui/struct.OfsBuf.html
[`slice::copy_within`]: https://doc.rust-lang.org/std/primitive.slice.html#method.copy_within
[`slice::fill`]: https://doc.rust-lang.org/std/primitive.slice.html#method.fill
[`slice`]: https://doc.rust-lang.org/std/primitive.slice.html
[`std::simd`]: https://doc.rust-lang.org/std/simd/index.html
[`VT-100` output parser]: https://docs.rs/r3bl_tui/latest/r3bl_tui/core/ansi/vt_100_pty_output_parser/index.html
[`VT-100`]: https://vt100.net/docs/vt100-ug/chapter3.html
[Assembly]: https://en.wikipedia.org/wiki/Assembly_language
[AVX/NEON]: https://en.wikipedia.org/wiki/Advanced_Vector_Extensions
[Cache Line]: https://en.wikipedia.org/wiki/CPU_cache#Cache_lines
[Cache Lines]: https://en.wikipedia.org/wiki/CPU_cache#Cache_lines
[Hardware Prefetcher]: https://en.wikipedia.org/wiki/CPU_cache#Hardware_prefetching
[heap]: https://en.wikipedia.org/wiki/Heap_(data_structure)
[L1 cache]: https://en.wikipedia.org/wiki/CPU_cache#Levels_of_hierarchy
[L1]: https://en.wikipedia.org/wiki/CPU_cache#Levels_of_hierarchy
[L2]: https://en.wikipedia.org/wiki/CPU_cache#Levels_of_hierarchy
[LLVM]: https://llvm.org/
[RAM]: https://en.wikipedia.org/wiki/Random-access_memory
[SIMD]: https://en.wikipedia.org/wiki/SIMD
<!-- prettier-ignore-end -->
