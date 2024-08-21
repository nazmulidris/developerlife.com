---
title: "Build a non-binary tree that is thread safe using Rust"
author: Nazmul Idris
date: 2022-02-24 14:00:00+00:00
excerpt: |
  This article illustrates how we can build a non-binary tree in Rust using various approaches until
  we end up with a version that is thread safe and supports parallel tree walking as well. Topics
  like interior mutability, sharing ownership, weak and strong references, custom traits for
  polymorphic behavior, are covered in this article.
layout: post
categories:
  - Rust
  - CS
  - CLI
---

<img class="post-hero-image" src="{{ 'assets/rust-non-binary-tree.svg' | relative_url }}"/>

<!-- TOC -->

- [Introduction](#introduction)
- [Naive approach using weak and strong references](#naive-approach-using-weak-and-strong-references)
  - [Thread safety](#thread-safety)
  - [Implementation](#implementation)
- [Sophisticated approach using memory arena](#sophisticated-approach-using-memory-arena)
  - [Traits](#traits)
  - [Arena implementation details](#arena-implementation-details)
  - [Basic usage of the arena tree](#basic-usage-of-the-arena-tree)
  - [Multithreading](#multithreading)
- [Wrapping up](#wrapping-up)
- [Build with Naz video series on developerlife.com YouTube channel](#build-with-naz-video-series-on-developerlifecom-youtube-channel)

<!-- /TOC -->

## Introduction
<a id="markdown-introduction" name="introduction"></a>

This article illustrates how we can build a non-binary tree in Rust using various approaches until
we end up with a version that is thread safe and supports parallel tree walking as well. Topics like
interior mutability, sharing ownership, weak and strong references, custom traits for polymorphic
behavior, are covered in this article.

> For more information on general Rust type system design (functional approach rather than
> object oriented), please take a look at this [paper](https://arxiv.org/pdf/2307.07069.pdf)
> by Will Crichton demonstrating Typed Design Patterns with Rust.

A non-binary tree is a data structure that can be used to represent a tree of nodes similar to DOM,
or Virtual DOM (React). Each node in the tree has a value and a list of children. It also has a
parent. The first implementation that we will do is going to be a naive approach, that will get us
into shared ownership, interior mutability, and weak and strong references. Subsequent approaches
will be allow us to make the tree thread safe and parallel friendly (we will name them `Arena` and
`Node` and you can use the via the [`r3bl_rs_utils` crate](https://crates.io/crates/r3bl_rs_utils).

> 📦 The tree (`Arena` & `Node`) is available for you to use in your projects via the
> [`r3bl_rs_utils`](https://crates.io/crates/r3bl_rs_utils) crate.

> 📜 You can take a look the source code of this thread safe non-binary tree data structure named
> `Arena` in its github [repo](https://github.com/r3bl-org/r3bl-open-core/tree/main/utils).

## Naive approach using weak and strong references
<a id="markdown-naive-approach-using-weak-and-strong-references" name="naive-approach-using-weak-and-strong-references"></a>

Our first attempt at implementing this data structure will involve using a struct that can hold
references to children that it owns. And also a reference to a parent that it does not own, but has
a weak reference to. Also this opens up this data structure to 2 things:

1. Shared ownership - While the children are owned by the struct, it is necessary to provide access
   to these children node to other code that use this tree data structure. Moving these references
   out of the tree isn't desirable. And cloning the entire node before moving it out of the tree
   isn't optimal either. This is where shared onwnership comes into play. In order to do that, we
   wrap the underlying node in a `Rc`. This is a reference counted pointer. However, that isn't
   enough, since once we pass a (shared) reference to other code (that is using this tree), we need
   to provide the ability to mutate what is inside the node itself, which leads us to interior
   mutability.
2. Interior mutability - Once a reference (that allows for shared ownership) of a node is passed to
   code using the tree, it becomes necessary to allow modifications to the underlying node itself.
   This requires us to use interior mutability by wrapping the node in a `RefCell`. Which is then
   wrapped in the `Rc` that we use to share ownership. Combining these two together gets us to where
   we need to be.

> 🧸 Here is a much simpler snippet of code for you to play with
> [in the Rust playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=f8db9ee621dc064051dab005a273e86c)
> before we get into our naive implementation. It will get you warmed up with the concepts of shared
> ownership, interior mutability, weak, and strong references.

### Thread safety
<a id="markdown-thread-safety" name="thread-safety"></a>

While this is a good start, we haven't dealt with thread safety. Rust makes it very easy to handle
this paralellism, we simply do the following:

1. Replace `Rc` with `Arc`.
2. Replace `RefCell` with `RwLock` (note that we could have also used `Mutex` but we are using
   `RwLock` for better performance in use cases where more nodes will be accessed in the tree,
   rather than new nodes added to the tree).

### Implementation
<a id="markdown-implementation" name="implementation"></a>

Here's some code that we will use to implement this data structure. Let's start w/ describing the
struct that holds the value or payload, the children, and parent references.

````rust
/// This struct holds underlying data. It shouldn't be created directly, instead use:
/// [`Node`](struct@Node).
///
/// ```text
/// NodeData
///  | | |
///  | | +- value: T ---------------------------------------+
///  | |                                                    |
///  | |                                        Simple onwership of value
///  | |
///  | +-- parent: RwLock<WeakNodeNodeRef<T>> --------+
///  |                                            |
///  |                 This describes a non-ownership relationship.
///  |                 When a node is dropped, its parent will not be dropped.
///  |
///  +---- children: RwLock<Vec<Child<T>>> ---+
///                                           |
///                 This describes an ownership relationship.
///                 When a node is dropped its children will be dropped as well.
/// ```
pub struct NodeData<T>
where
  T: Display,
{
  value: T,
  parent: Parent<T>,
  children: Children<T>,
}
````

Here are the type aliases used for readability.

```rust
type NodeDataRef<T> = Arc<NodeData<T>>;
type WeakNodeNodeRef<T> = Weak<NodeData<T>>;

/// Parent relationship is one of non-ownership.
/// This is not a `RwLock<NodeDataRef<T>>` which would cause memory leak.
type Parent<T> = RwLock<WeakNodeNodeRef<T>>;

/// Children relationship is one of ownership.
type Children<T> = RwLock<Vec<Child<T>>>;
type Child<T> = NodeDataRef<T>;
```

Here's a visualization of the relationships between a node, its children, and parent, in terms of
ownership.

<img class="post-hero-image" src="{{ 'assets/rust-weak-ref.svg' | relative_url }}"/>

1. When a node is dropped, its children will be dropped as well (since it owns them). We represent
   this relationship w/ a strong reference.
2. However, the parent should not be dropped (since it does not own them). We represent this
   relationship w/ a weak reference.

So far we don't have any functions or methods that allow us to do anything with the `NodeData`. So
lets add some. First step is adding a `Node` struct itself (which will allow us to manage references
more easily).

````rust
/// This struct is used to own a [`NodeData`] inside an [`Arc`]. The [`Arc`]
/// can be shared, so that it can have multiple owners. It does not have
/// getter methods for [`NodeData`]'s properties, instead it implements the
/// `Deref` trait to allow it to be used as a [`NodeData`].
///
/// # Shared ownership
///
/// After an instance of this struct is created and it's internal reference is
/// cloned (and given to another) dropping this instance will not drop the cloned
/// internal reference.
///
/// ```text
/// Node { arc_ref: Arc<NodeData> }
///    ▲                 ▲
///    │                 │
///    │      This atomic ref owns the
///    │      `NodeData` & is shared
///    │
///    1. Has methods to manipulate nodes and their children.
///
///    2. When it is dropped, if there are other `Arc`s (shared via
///       `get_copy_of_internal_arc()`) pointing to the same underlying
///       `NodeData`, then the `NodeData` will not be dropped.
///
///    3. This struct is necessary in order for `add_child_and_update_its_parent`
///       to work. Some pointers need to be swapped between 2 nodes for this work
///       (and one of these pointers is a weak one). It is not possible to do this
///       using two `NodeData` objects, without wrapping them in `Arc`s.
/// ```

#[derive(Debug)]
pub struct Node<T: Display> {
  arc_ref: NodeDataRef<T>,
}
````

Now it is time to add some methods. First the implementation of the
[`Deref`](https://doc.rust-lang.org/book/ch19-03-advanced-traits.html#using-the-newtype-pattern-to-implement-external-traits-on-external-types)
trait for `Node`.

```rust
impl<T> Deref for Node<T>
where
  T: Display,
{
  type Target = NodeData<T>;

  fn deref(&self) -> &Self::Target {
    &self.arc_ref
  }
}
```

And now the rest of the methods.

```rust
impl<T> Node<T>
where
  T: Display,
{
  pub fn new(value: T) -> Node<T> {
    let new_node = NodeData {
      value,
      parent: RwLock::new(Weak::new()),
      children: RwLock::new(Vec::new()),
    };
    let arc_ref = Arc::new(new_node);
    Node { arc_ref }
  }

  pub fn get_copy_of_internal_arc(self: &Self) -> NodeDataRef<T> {
    Arc::clone(&self.arc_ref)
  }

  pub fn create_and_add_child(
    self: &Self,
    value: T,
  ) -> NodeDataRef<T> {
    let new_child = Node::new(value);
    self.add_child_and_update_its_parent(&new_child);
    new_child.get_copy_of_internal_arc()
  }

  /// 🔏 Write locks used.
  pub fn add_child_and_update_its_parent(
    self: &Self,
    child: &Node<T>,
  ) {
    {
      let mut my_children = self.arc_ref.children.write().unwrap();
      my_children.push(child.get_copy_of_internal_arc());
    } // `my_children` guard dropped.

    {
      let mut childs_parent = child.arc_ref.parent.write().unwrap();
      *childs_parent = Arc::downgrade(&self.get_copy_of_internal_arc());
    } // `my_parent` guard dropped.
  }

  pub fn has_parent(self: &Self) -> bool {
    self.get_parent().is_some()
  }

  /// 🔒 Read lock used.
  pub fn get_parent(self: &Self) -> Option<NodeDataRef<T>> {
    let my_parent_weak = self.arc_ref.parent.read().unwrap();
    if let Some(my_parent_arc_ref) = my_parent_weak.upgrade() {
      Some(my_parent_arc_ref)
    } else {
      None
    }
  }
}
```

> 🧸 Here's the complete code listing of this naive implementation for you to play with
> [in the Rust playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=b194d56e5dcd538d88dc4e490c39862b).

## Sophisticated approach using memory arena
<a id="markdown-sophisticated-approach-using-memory-arena" name="sophisticated-approach-using-memory-arena"></a>

In our naive example, we manage references that are strong (owned, children) and weak (not owned,
parent). And we have to wrap the `NodeData` inside of a `Node` in order to be able to share it. This
is quite cumbersome to use. We will use the idea of a memory arena to simplify this. Here's the
[wikipedia definition of a memory arena](https://en.wikipedia.org/wiki/Region-based_memory_management).

We wil call the node struct `Node`, and the tree struct `Arena`. The fundamental idea is that when
nodes are created we save them in a `HashMap`. Each entry in this map must have an `id` (which can
be anything, in our case we will use `usize`). Now instead of using a vector of strong references to
store children, we can just use a `Vec<usize>`. Similarly, the parent will just be a `<usize>`. This
makes it trivial to add a child to a node, and set the parent. Deletion is very easy as well, since
we just remove the node and it's children from the underlying `HashMap`. We can also pass references
around (both strong and weak) to the underlying nodes w/out worrying about affecting the tree. It
simplifies so many things just by having a level of indirection that is not a smart pointer /
reference, but a simple `id`. The constrains is that each node now must have an `id`. Given that
this is a `usize` that's not an overhead, and makes working with nodes very easy, and memory and CPU
efficient.

Before we begin w/ the memory arena (that we will name `Arena` and `Node`), let's take a look at
traits and how we will be using them to get us polymorphic behavior in Rust. We know that each node
must have an `id`, so the following section goes into quite a bit of detail on how can go about
implementing this.

### Traits
<a id="markdown-traits" name="traits"></a>

Traits are like TypeScript, Java, or Kotlin interfaces. They also act like Kotlin extension
functions. Traits come into play when we want to pass an argument to a function that takes something
that implements a certain trait.

They are meant for 2 things:

1. Extension of existing types - This is done by adding methods to existing types. The section below
   goes into detail about how this is leveraged in our example.
2. Adaptation of existing types - An example of this is a library provide a trait that describes
   some functionality that it needs for us to implement in order for us to use it. In this case, we
   would need to implement that trait on a struct that we create in order for that to be usable w/
   this library. A simple example of this is the `Display` trait or `Iterator` trait.

Here's an example of a trait before getting into the specifics of what is used in `Arena`. We've
defined a trait named `HasId` which has an associated type `Id` and a method `id` that returns an
instance of that associated type (in this case, it's `i32`). The actual implementation in `Arena` is
derived from this.

```rust
trait HasId {
  type Id;
  fn id(&self) -> &Self::Id;
}

struct Node {
  id: i32,
  payload: String,
  children: Vec<i32>,
}

impl HasId for Node {
  type Id = i32;

  fn id(&self) -> &Self::Id {
    &self.id
  }
}

impl HasId for i32 {
  type Id = i32;

  fn id(&self) -> &Self::Id {
    self
  }
}
```

Here are the various forms of using the `HasId` trait as an argument to a function. You can see that
arguments of type `Node` and `i32` are passed interchangably to the functions 🪄. There is event a
variant that takes a `Node` or `i32` wrapped in a `Box`.

```rust
let my_node = Node {
  id: 1,
  payload: "payload".to_string(),
  children: vec![2, 3, 4],
};

let my_i32_id = 1;

fun_0(&my_node);

fun_1(&my_node);
fun_1(&my_i32_id);

fun_2(&my_node);
fun_2(&my_i32_id);

fun_3(&my_i32_id);

fun_4(Box::new(my_node)); // `my_node` is moved into `fun_4`.
fun_4(Box::new(my_i32_id)); // `my_i32_id` is moved into `fun_4`.
```

Finally here are the function definitions for the 4 forms that you see used above. You can see there
are various ways to tell Rust that you would like your function to accept an argument that
implements this trait. Depending on what style looks best to you, you can choose from these forms.

```rust
use r3bl_rs_utils::utils::style_primary;

/// This accepts a borrowed `Node` object.
fn fun_0(node: &Node) {
  println!("{}: {}", style_primary("fun_0:"), node.id());
}

/// This accepts a borrowed object that implements `HasId`.
fn fun_1(node: &dyn HasId<Id = i32>) {
  println!("{}: {}", style_primary("fun_1:"), node.id());
}

/// This takes an object that implements `HasId`.
fn fun_2_own(node: impl HasId<Id = i32>) {
  println!("{}: {}", style_primary("fun_2:"), node.id());
}

fn fun_2(node: &impl HasId<Id = i32>) {
  println!("{}: {}", style_primary("fun_2:"), node.id());
}

/// This takes an `i32` which also implements `HasId`.
fn fun_3_own(node: i32) {
  println!("{}: {}", style_primary("fun_3:"), &node.id());
}

fn fun_3(node: &i32) {
  println!("{}: {}", style_primary("fun_3:"), &node.id());
}

/// This takes a `Node` object that's in a `Box` reference.
fn fun_4(node: Box<dyn HasId<Id = i32>>) {
  println!("{}: {}", style_primary("fun_4:"), node.id());
}
```

> 🧸 You can
> [play with this code](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=8cdf3a53e35d7c2372a2b154bd93d422)
> in Rust playground.

### Arena implementation details
<a id="markdown-arena-implementation-details" name="arena-implementation-details"></a>

> 📦 You can get `Arena`, `Node` and `style_primary` from
> [`r3bl_rs_utils`](https://crates.io/crates/r3bl_rs_utils) crate.

> 🌟 Please star the [`r3bl-open-core` repo](https://github.com/r3bl-org/r3bl-open-core) on github if
> you like it 🙏.

`Arena` provides a trait called `HasId` that represents the `id` of a node in the tree. Both a
`usize` and `Node` can be an instance of this trait.

- While this `id` could also just simply be represented by `usize`, using this trait to describe the
  arguments that the `Arena` struct takes gives us the benefit of using any one of these things as
  an argument: `usize`, `Node`.
- There's another benefit of using this trait; the `Arena::add_new_node()` method takes a 2nd
  argument that holds an `Option` that wraps anything that implements the `HasId` trait. This is
  necessary because Rust doesn't support optional arguments and we need to be able to add a root
  node which requires the 2nd argument to be `None`. However, this makes the API clumsy since we
  have to manually wrap the `&dyn HasId` in an`Option`. By implementing the `HasId` trait on `usize`
  itself, it becomes possible to call `into_some()` method on it and get an `Option` that wraps the
  id itself.
- Since `Node` contains a `usize` field, that implements the `HasId` trait, we can delegate the
  implementation of the `impl HasId for Node` to contained `usize` field itself.
- Also, traits can have associated types, and `HasId` has an associated type called `IdType` which
  is just `usize`. However, it can be set to anything and shows the flexibility of traits.

> Here's a diagram summarizing the journey so far. <br/> <br/> >
> <img class="post-hero-image" src="{{ 'assets/tree-approaches.drawio.svg' | relative_url }}"/>

### Basic usage of the arena (tree)
<a id="markdown-basic-usage-of-the-arena-tree" name="basic-usage-of-the-arena-tree"></a>

The first step to using this tree is adding the dependency for `r3bl_rs_utils` to your `Cargo.toml`.

```toml
[dependencies]
r3bl_rs_utils = "0.4.0"
```

Now you can start using the `Arena` struct. This is the main tree struct that you will be
interacting with. Another struct called `Node` is used to represent a node in the tree.

Here's an example. This is a test that creates a tree with a few nodes, looks them up by `id`, and
then performs a tree walk (which returns a list of `id`'s).

```rust
use r3bl_rs_utils::{
  tree_memory_arena::{Arena, HasId, MTArena, ResultUidList},
  utils::{style_primary, style_prompt},
};

#[test]
fn test_can_add_nodes_to_tree() {
  // Can create an arena.
  let mut arena = Arena::<usize>::new();
  let node_1_value = 42 as usize;
  let node_2_value = 100 as usize;

  // Can insert a node - node_1.
  {
    let node_1_id = arena.add_new_node(node_1_value, None);
    assert_eq!(node_1_id, 0);
  }

  // Can find node_1 by id.
  {
    let node_1_id = 0 as usize;
    assert!(arena.get_node_arc(&node_1_id).is_some());

    let node_1_ref = dbg!(arena.get_node_arc(&node_1_id).unwrap());
    let node_1_ref_weak = arena.get_node_arc_weak(&node_1_id).unwrap();
    assert_eq!(node_1_ref.read().unwrap().payload, node_1_value);
    assert_eq!(
      node_1_ref_weak.upgrade().unwrap().read().unwrap().payload,
      42
    );
  }

  // Can't find node by id that doesn't exist.
  {
    let node_id_dne = 200 as usize;
    assert!(arena.get_node_arc(&node_id_dne).is_none());
  }

  // Can add child to node_1.
  {
    let node_1_id = 0 as usize;
    let node_2_id = arena.add_new_node(node_2_value, node_1_id.into_some());
    let node_2_ref = dbg!(arena.get_node_arc(&node_2_id).unwrap());
    let node_2_ref_weak = arena.get_node_arc_weak(&node_2_id).unwrap();
    assert_eq!(node_2_ref.read().unwrap().payload, node_2_value);
    assert_eq!(
      node_2_ref_weak.upgrade().unwrap().read().unwrap().payload,
      node_2_value
    );
  }

  // Can dfs tree walk.
  {
    let node_1_id = 0 as usize;
    let node_2_id = 1 as usize;

    let node_list = dbg!(arena.tree_walk_dfs(&node_1_id).unwrap());

    assert_eq!(node_list.len(), 2);
    assert_eq!(node_list, vec![node_1_id, node_2_id]);
  }
}
```

> 📜 There are more complex ways of using this `Arena`. Please look at these extensive integration
> tests that put the `Arena` API thru its paces
> [here](https://github.com/r3bl-org/r3bl-rs-utils/blob/main/tests/tree_memory_arena_test.rs).

### Multithreading
<a id="markdown-multithreading" name="multithreading"></a>

`Arena` is thread-safe by design. However, there's another struct called `MTArena` that allow for
parallel tree walking, and even sharing `Arena` instances between threads & shared ownership of the
underlying tree itself across various parts of your code.

Instead of creating a new `Arena` instance, we create a new `MTArena` instance. And we have an extra
method that allows for the creation of a new thread to perform tree walking. We have to supply a
closure that is passed to this function `tree_walk_parallel(<id>, <lambda>);`.

Here's an example from the integration tests.

```rust
#[test]
fn test_mt_arena_insert_and_walk_in_parallel() {
  type ThreadResult = Vec<usize>;
  type Handles = Vec<JoinHandle<ThreadResult>>;

  let mut handles: Handles = Vec::new();
  let arena = MTArena::<String>::new();

  // Thread 1 - add root. Spawn and wait (since the 2 threads below need the root).
  {
    let arena_arc = arena.get_arena_arc();
    let thread = thread::spawn(move || {
      let mut arena_write = arena_arc.write().unwrap();
      let root = arena_write.add_new_node("foo".to_string(), None);
      vec![root]
    });
    thread.join().unwrap();
  }

  // Thread 2 - add child. Just spawn, don't wait to finish.
  {
    let arena_arc = arena.get_arena_arc();
    let thread = thread::spawn(move || {
      let mut arena_write = arena_arc.write().unwrap();
      let parent: Option<Vec<usize>> =
        arena_write.filter_all_nodes_by(&mut move |_id, payload| {
          if payload == "foo" {
            true
          } else {
            false
          }
        });
      let parent_id = parent.unwrap().first().unwrap().clone();
      let child = arena_write.add_new_node("bar".to_string(), parent_id.into_some());
      vec![parent_id, child]
    });

    handles.push(thread);
  }

  // Thread 3 - add another child. Just spawn, don't wait to finish.
  {
    let arena_arc = arena.get_arena_arc();
    let thread = thread::spawn(move || {
      let mut arena_write = arena_arc.write().unwrap();
      let parent: Option<Vec<usize>> =
        arena_write.filter_all_nodes_by(&mut move |_id, payload| {
          if payload == "foo" {
            true
          } else {
            false
          }
        });
      let parent_id = parent.unwrap().first().unwrap().clone();
      let child = arena_write.add_new_node("baz".to_string(), parent_id.into_some());
      vec![parent_id, child]
    });

    handles.push(thread);
  }

  // Wait for all threads to complete.
  handles.into_iter().for_each(move |handle| {
    handle.join().unwrap();
  });
  println!("{:#?}", &arena);

  // Perform tree walking in parallel. Note the lamda does capture many enclosing variable context.
  {
    let arena_arc = arena.get_arena_arc();
    let fn_arc = Arc::new(move |uid, payload| {
      println!(
        "{} {} {} Arena weak_count:{} strong_count:{}",
        style_primary("walker_fn - closure"),
        uid,
        payload,
        Arc::weak_count(&arena_arc),
        Arc::weak_count(&arena_arc)
      );
    });

    // Walk tree w/ a new thread using arc to lambda.
    {
      let thread_handle: JoinHandle<ResultUidList> =
        arena.tree_walk_parallel(&0, fn_arc.clone());

      let result_node_list = thread_handle.join().unwrap();
      println!("{:#?}", result_node_list);
    }

    // Walk tree w/ a new thread using arc to lambda.
    {
      let thread_handle: JoinHandle<ResultUidList> =
        arena.tree_walk_parallel(&1, fn_arc.clone());

      let result_node_list = thread_handle.join().unwrap();
      println!("{:#?}", result_node_list);
    }
  }
}
```

## Wrapping up
<a id="markdown-wrapping-up" name="wrapping-up"></a>

There are lots of other useful library functions that you can check out in `r3bl_rs_utils` crate.
There are functions that make it easy to unwrap things in Rust that are wrapped in an `<Option>`, or
`<Arc<RwLock>>`, etc. There are Kotlin inspired scope functions if you like that type of thing.

> 📦 The tree (`Arena` & `Node`) is available for you to use in your projects via the
> [`r3bl_rs_utils`](https://crates.io/crates/r3bl_rs_utils) crate.

> 📜 You can take a look the source code of this thread safe non-binary tree data structure named
> `Arena` in its github [repo](https://github.com/r3bl-org/r3bl-open-core/tree/main/utils).

## Build with Naz video series on developerlife.com YouTube channel
<a id="markdown-build-with-naz-video-series-on-developerlife.com-youtube-channel" name="build-with-naz-video-series-on-developerlife.com-youtube-channel"></a>

> If you have comments and feedback on this content, or would like to request new content
> (articles & videos) on developerlife.com, please join our [discord
> server](https://discord.gg/8M2ePAevaMi).

You can watch a video series on building this crate with Naz on the
[developerlife.com YouTube channel](https://www.youtube.com/@developerlifecom).

- [YT channel](https://www.youtube.com/@developerlifecom)
- Playlists
    - [Build with Naz, Linux TTY, process, signals, commands in async Rust](https://www.youtube.com/watch?v=bolScvh4x7I&list=PLofhE49PEwmw3MKOU1Kn3xbP4FRQR4Mb3)
    - [Build with Naz, fundamental effective Rust](https://www.youtube.com/playlist?list=PLofhE49PEwmza94sS7UmJnN9gSCHTVTfz)
    - [Build with Naz, effective async Rust and tokio](https://www.youtube.com/playlist?list=PLofhE49PEwmwO69E7eiQ-ewnMME8ydgQ5)
    - [Build with Naz, async readline and spinner for CLI in Rust](https://www.youtube.com/watch?v=3vQJguti02I&list=PLofhE49PEwmwelPkhfiqdFQ9IXnmGdnSE)
    - [Build with Naz, testing in Rust](https://www.youtube.com/watch?v=Xt495QLrFFk&list=PLofhE49PEwmwLR_4Noa0dFOSPmSpIg_l8)
