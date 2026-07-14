import sys
import re

filepath = "/home/nazmul/github/developerlife.com/_posts/2026-07-14-build-high-performance-flat-2d-arrays-in-rust.md"
with open(filepath, "r") as f:
    content = f.read()

# 1. Replace the first mod tests block
# It starts after: total += self.data.len() * std::mem::size_of::<T>();\n        total\n    }\n}\n
first_test_marker_start = "    pub fn get_mem_size(&self) -> usize {\n        let mut total = std::mem::size_of::<Self>();\n        total += self.data.len() * std::mem::size_of::<T>();\n        total\n    }\n}\n\n#[cfg(test)]\nmod tests {\n"
idx = content.find(first_test_marker_start)
if idx == -1:
    print("Failed to find first test block")
    sys.exit(1)

# Find the end of this rust block
end_idx = content.find("\n```\n", idx)
if end_idx == -1:
    print("Failed to find end of first test block")
    sys.exit(1)

new_first_block = """    pub fn get_mem_size(&self) -> usize {
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
            std::mem::size_of::<Flat2DArray<usize>>() + 100 * std::mem::size_of::<usize>()
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
        let expected_output = "(0, 0): 0 | (0, 1): 0 | (0, 2): 0 | \
            (1, 0): 0 | (1, 1): 0 | (1, 2): 0 | \
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
}"""
content = content[:idx] + new_first_block + content[end_idx:]


# 2. Replace ergonomic access tests
second_test_marker = "    fn index_mut(&mut self, pos: Pos) -> &mut Self::Output {\n        let row = pos.row_index.as_usize();\n        let col = pos.col_index.as_usize();\n        let cols = self.cols.as_usize();\n        let range_start = row * cols + col;\n        let range_end = range_start + 1;\n        &mut self.data[range_start..range_end]\n    }\n}\n\n#[cfg(test)]\nmod tests {\n"

idx2 = content.find(second_test_marker)
if idx2 == -1:
    print("Failed to find second test block")
    sys.exit(1)

end_idx2 = content.find("\n```\n", idx2)
if end_idx2 == -1:
    print("Failed to find end of second test block")
    sys.exit(1)

new_second_block = """    fn index_mut(&mut self, pos: Pos) -> &mut Self::Output {
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
}"""

content = content[:idx2] + new_second_block + content[end_idx2:]


# 3. Add SIMD tests right before "## Proving it with Benchmarks"
bench_marker = "## Proving it with Benchmarks"
idx3 = content.find(bench_marker)
if idx3 == -1:
    print("Failed to find benchmarks section")
    sys.exit(1)

simd_tests_block = """
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
        let expected_output_vectorized = "(0, 0): 0 | (0, 1): 0 | (0, 2): 0 | \\
            (1, 0): 0 | (1, 1): 0 | (1, 2): 0 | \\
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

"""

content = content[:idx3] + simd_tests_block + content[idx3:]

with open(filepath, "w") as f:
    f.write(content)

print("Tests updated successfully")
