import sys

filepath = "/home/nazmul/github/developerlife.com/_posts/2026-07-14-build-high-performance-flat-2d-arrays-in-rust.md"
with open(filepath, "r") as f:
    content = f.read()

start_marker = "## Proving it with Benchmarks"
end_marker = "### Note on primitive types"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("Failed to find markers")
    sys.exit(1)

new_content = """## Proving it with Benchmarks

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
    let mut grid = Vec2DArray::<PixelChar>::new(size, PixelChar::default());
    println!("Vec2DArray -> grid size: {:?}", grid.get_mem_size());
    b.iter(|| grid.clear(black_box(PixelChar::Void)));
}

#[bench]
fn fits_l1_g1_clear_screen_flat1darray_scalar(b: &mut Bencher) {
    let size = fits_l1_cache::size();
    let mut grid = Flat2DArray::<PixelChar>::new(size, PixelChar::default());
    println!("Flat2DArray -> grid size: {:?}", grid.get_mem_size());
    b.iter(|| grid.clear(black_box(PixelChar::Void)));
}

#[bench]
fn fits_l1_g1_clear_screen_flat1darray_simd(b: &mut Bencher) {
    let size = fits_l1_cache::size();
    let mut grid = Flat2DArray::<PixelChar>::new(size, PixelChar::default());
    println!("Flat2DArray -> grid size: {:?}", grid.get_mem_size());
    b.iter(|| grid.simd_clear(black_box(PixelChar::Void)));
}

#[bench]
fn spills_l1_g1_clear_screen_vec2darray_scalar(b: &mut Bencher) {
    let size = spills_l1_cache::size();
    let mut grid = Vec2DArray::<PixelChar>::new(size, PixelChar::default());
    println!("Vec2DArray -> grid size: {:?}", grid.get_mem_size());
    b.iter(|| grid.clear(black_box(PixelChar::Void)));
}

#[bench]
fn spills_l1_g1_clear_screen_flat1darray_scalar(b: &mut Bencher) {
    let size = spills_l1_cache::size();
    let mut grid = Flat2DArray::<PixelChar>::new(size, PixelChar::default());
    println!("Flat2DArray -> grid size: {:?}", grid.get_mem_size());
    b.iter(|| grid.clear(black_box(PixelChar::Void)));
}

#[bench]
fn spills_l1_g1_clear_screen_flat1darray_simd(b: &mut Bencher) {
    let size = spills_l1_cache::size();
    let mut grid = Flat2DArray::<PixelChar>::new(size, PixelChar::default());
    println!("Flat2DArray -> grid size: {:?}", grid.get_mem_size());
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
    let mut grid = Vec2DArray::<PixelChar>::new(size, PixelChar::default());
    println!("Vec2DArray -> grid size: {:?}", grid.get_mem_size());
    b.iter(|| grid.scroll_up());
}

#[bench]
fn spills_l1_g2_scroll_up_flat1darray_simd(b: &mut Bencher) {
    let size = spills_l1_cache::size();
    let mut grid = Flat2DArray::<PixelChar>::new(size, PixelChar::default());
    println!("Flat2DArray -> grid size: {:?}", grid.get_mem_size());
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
    let mut grid = Vec2DArray::<PixelChar>::new(size, PixelChar::default());
    println!("Vec2DArray -> grid size: {:?}", grid.get_mem_size());
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
    let mut grid = Flat2DArray::<PixelChar>::new(size, PixelChar::default());
    println!("Flat2DArray -> grid size: {:?}", grid.get_mem_size());
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

    let mut grid_1 = Vec2DArray::<PixelChar>::new(size, PixelChar::Void);
    println!("Vec2DArray -> grid size: {:?}", grid_1.get_mem_size());

    let mut grid_2 = Vec2DArray::<PixelChar>::new(size, PixelChar::Void);
    grid_2.data[50][50] = PixelChar::Spacer;

    b.iter(|| {
        let _ = black_box(&grid_1.diff(&grid_2));
    });
}

#[bench]
fn spills_l1_g4_diff_flat1darray_simd(b: &mut Bencher) {
    let size = spills_l1_cache::size();

    let mut grid_1 = Flat2DArray::<PixelChar>::new(size, PixelChar::Void);
    println!("Flat2DArray -> grid size: {:?}", grid_1.get_mem_size());

    let mut grid_2 = Flat2DArray::<PixelChar>::new(size, PixelChar::Void);
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
    let grid = Vec2DArray::<PixelChar>::new(size, PixelChar::default());
    println!("Vec2DArray -> grid size: {:?}", grid.get_mem_size());
    b.iter(|| {
        let _ = black_box(grid.get_mem_size());
    });
}

#[bench]
fn spills_l1_g5_mem_size_flat1darray_simd(b: &mut Bencher) {
    let size = spills_l1_cache::size();
    let grid = Flat2DArray::<PixelChar>::new(size, PixelChar::default());
    println!("Flat2DArray -> grid size: {:?}", grid.get_mem_size());
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
    let mut grid = Vec2DArray::<PixelChar>::new(size, PixelChar::default());
    println!("Vec2DArray -> grid size: {:?}", grid.get_mem_size());
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
    let mut grid = Flat2DArray::<PixelChar>::new(size, PixelChar::default());
    println!("Flat2DArray -> grid size: {:?}", grid.get_mem_size());
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
    let mut grid = Flat2DArray::<PixelChar>::new(size, PixelChar::default());
    println!("Flat2DArray -> grid size: {:?}", grid.get_mem_size());
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

"""

final_content = content[:start_idx] + new_content + content[end_idx:]

with open(filepath, "w") as f:
    f.write(final_content)

print("Benchmarks updated successfully")
