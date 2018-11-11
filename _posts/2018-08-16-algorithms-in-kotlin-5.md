---
author: Nazmul Idris
date: 2018-08-16 15:00:00+00:00
excerpt: |
  This tutorial is part of a collection of tutorials on basic data
  structures and algorithms that are created using Kotlin.
  This project is useful if you are trying to get more fluency
  in Kotlin or need a refresher to do interview prep for software
  engineering roles.
layout: post
hero-image: assets/algo-hero.svg
title: "Algorithms in Kotlin, Graphs, Part 5/7"
categories:
- CS
- KT
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
  - [How to run this project](#how-to-run-this-project)
    - [Importing this project into Jetbrains IntelliJ IDEA](#importing-this-project-into-jetbrains-intellij-idea)
- [Undirected graphs](#undirected-graphs)
  - [BFS](#bfs)
  - [DFS](#dfs)
- [BFS and DFS traversal for binary trees](#bfs-and-dfs-traversal-for-binary-trees)
- [Stacks and Queues](#stacks-and-queues)
- [Resources](#resources)
  - [CS Fundamentals](#cs-fundamentals)
  - [Data Structures](#data-structures)
  - [Math](#math)
  - [Big-O Notation](#big-o-notation)
  - [Kotlin](#kotlin)
  - [Markdown utilities](#markdown-utilities)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

This tutorial is part of a collection tutorials on basic data
structures and algorithms that are created using Kotlin. This
project is useful if you are trying to get more fluency in
Kotlin or need a refresher to do interview prep for software
engineering roles.

### How to run this project

You can get the code for this and all the other tutorials in
this collection from [this github repo](
https://github.com/nazmulidris/algo). Here's a screen capture of
project in this repo in action.

![]({{'assets/algo-app-anim.gif' | relative_url}})

Once you've cloned the repo, type `gradle run` in order to build
and run this project on the command line.

#### Importing this project into Jetbrains IntelliJ IDEA

- This project was created using Jetbrains Idea as a Gradle and Kotlin project
([more info](https://www.jetbrains.com/help/idea/getting-started-with-gradle.html)).
    - When you import this project into Idea as a Gradle project,
    make sure not to check "Offline work" (which if checked, won't
    allow the gradle dependencies to be downloaded).
    - As of Jun 24 2018, [Java 10 doesn't work w/ this gradle distribution](
    https://github.com/gradle/gradle/issues/4503) (v4.4.x), so you can use Java 9 or 8,
    or upgrade to a newer version of gradle (4.8+).

## Undirected graphs

Here's code in Kotlin that describes undirected graphs with an adjacency list
to represent the edges. For more info, checkout this
[website](https://www.geeksforgeeks.org/graph-and-its-representations/). The
adjacency list is stored in a `MutableMap`, which holds a `LinkedList` of nodes.
A node / vertex in this graph can be of any class (`T`).

Here's an image of an undirected graph.

![]({{'assets/algo-4.svg' | relative_url}})

```kotlin
/**
 * [More info](https://www.geeksforgeeks.org/graph-and-its-representations/).
 */
class Graph<T> {
    val adjacencyMap: MutableMap<T, MutableSet<T>> = mutableMapOf()

    fun addEdge(sourceVertex: T, destinationVertex: T) {
        // Add edge to source vertex.
        adjacencyMap.computeIfAbsent(sourceVertex) { mutableSetOf() }
            .add(destinationVertex)
        // Add edge to destination vertex.
        adjacencyMap.computeIfAbsent(destinationVertex) { mutableSetOf() }
            .add(sourceVertex)
    }

    override fun toString(): String = StringBuffer().apply {
        for (key in adjacencyMap.keys) {
            append("$key -> ")
            append(adjacencyMap[key]?.joinToString(", ", "[", "]\n"))
        }
    }.toString()
}
```

### BFS

To do a breadth first traversal of the graph, here's some code that uses a Queue (FIFO). The
following implementation doesn't use recursion, and also keeps track of the depth as it's
traversing the graph. We also have to keep track of which nodes are visited and unvisited, so
that we don't backtrack and revisit node that have already been visited.

```kotlin
/**
 * Breadth first traversal leverages a [Queue] (FIFO).
 */
fun <T> breadthFirstTraversal(graph: Graph<T>, startNode: T, maxDepth: Int): String {
    //
    // Setup.
    //

    // Mark all the vertices / nodes as not visited. And keep track of sequence  in which nodes are
    // visited, for return value.
    class VisitedMap {
        val traversalList = mutableListOf<T>()

        val visitedMap = mutableMapOf<T, Boolean>().apply {
            for (node in graph.adjacencyMap.keys) this[node] = false
        }

        fun isNotVisited(node: T): Boolean = !visitedMap[node]!!

        fun markVisitedAndAddToTraversalList(node: T) {
            visitedMap[node] = true
            traversalList.add(node)
        }
    }

    val visitedMap = VisitedMap()

    // Keep track of the depth of each node, so that more than maxDepth nodes aren't visited.
    val depthMap = mutableMapOf<T, Int>().apply {
        for (node in graph.adjacencyMap.keys) this[node] = Int.MAX_VALUE
    }

    // Create a queue for BFS.
    class Queue {
        val deck: Deque<T> = ArrayDeque<T>()
        fun add(node: T, depth: Int) {
            // Add to the tail of the queue.
            deck.add(node)
            // Record the depth of this node.
            depthMap[node] = depth
        }

        fun add(set: Set<T>?, depth: Int) {
            if (set != null) {
                for (node in set) {
                    add(node, depth)
                }
            }
        }

        fun isNotEmpty() = deck.isNotEmpty()
        fun remove() = deck.remove()
    }

    val queue = Queue()

    //
    // Algorithm implementation.
    //

    // Initial step -> add the startNode to the queue.
    queue.add(startNode, /* depth= */0)

    // Traverse the graph
    while (queue.isNotEmpty()) {
        // Remove the item at the head of the queue.
        val currentNode = queue.remove()
        val currentDepth = depthMap[currentNode]!!

        if (currentDepth <= maxDepth) {
            if (visitedMap.isNotVisited(currentNode)) {
                // Mark the current node visited and add to traversal list.
                visitedMap.markVisitedAndAddToTraversalList(currentNode)
                // Add nodes in the adjacency map.
                queue.add(graph.adjacencyMap[currentNode], /* depth= */currentDepth + 1)
            }
        }

    }

    return visitedMap.traversalList.toString()
}
```

### DFS

To do a depth first traversal of the graph, here's some code that uses a Stack (LIFO).

```kotlin
/**
 * Depth first traversal leverages a [Stack] (LIFO).
 *
 * It's possible to use recursion instead of using this iterative
 * implementation using a [Stack]. Also, this algorithm is almost
 * the same above, except for [Stack] is LIFO and [Queue] is FIFO.
 *
 * [More info](https://stackoverflow.com/a/35031174/2085356).
 */
fun <T> depthFirstTraversal(graph: Graph<T>, startNode: T): String {
    // Mark all the vertices / nodes as not visited
    val visitedMap = mutableMapOf<T, Boolean>().apply {
        graph.adjacencyMap.keys.forEach { node -> put(node, false) }
    }

    // Create a stack for DFS
    val stack: Deque<T> = LinkedList()

    // Initial step -> add the startNode to the stack
    startNode.also { node ->
        stack.push(node)
    }

    // Store the sequence in which nodes are visited, for return value
    val traversalList = mutableListOf<T>()

    // Traverse the graph
    while (stack.isNotEmpty()) {
        // Pop the node off the top of the stack
        val currentNode = stack.pop()

        if (!visitedMap[currentNode]!!) {

            // Store this for the result
            traversalList.add(currentNode)

            // Mark the current node visited and add to the traversal list
            visitedMap[currentNode] = true

            // Add nodes in the adjacency map
            graph.adjacencyMap[currentNode]?.forEach { node ->
                stack.push(node)
            }

        }

    }

    return traversalList.joinToString()
}
```

## BFS and DFS traversal for binary trees
To see a similar implementation of BFS and DFS traversal for binary trees, please refer to
the [Binary-Trees]({{'/2018/08/16/algorithms-in-kotlin-6/' | relative_url}}) tutorial.

## Stacks and Queues

![]({{'assets/algo-3.svg' | relative_url}})

To learn more about stacks and queues, please refer to the
[Queues]({{'/2018/08/16/algorithms-in-kotlin-3/' | relative_url}})
tutorial.

## Resources

### CS Fundamentals
- [Brilliant.org CS Foundations](https://brilliant.org/courses/#computer-science-foundational)
- [Radix sort](https://brilliant.org/wiki/radix-sort/)
- [Hash tables](https://brilliant.org/wiki/hash-tables/)
- [Hash functions](https://algs4.cs.princeton.edu/34hash/)
- [Counting sort](https://brilliant.org/wiki/counting-sort/)
- [Radix and Counting sort MIT](https://courses.csail.mit.edu/6.006/spring11/rec/rec11.pdf)

### Data Structures
- [Graphs, DFS, BFS in Java](https://www.geeksforgeeks.org/graph-and-its-representations/)
- [Graphs - DFS in Java](https://www.geeksforgeeks.org/iterative-depth-first-traversal/)
- [Graphs - BFS in Java](https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/)
- [Stack vs Queue visualized](https://stackoverflow.com/a/35031174/2085356)

### Math
- [Khan Academy Recursive functions](https://www.khanacademy.org/computing/computer-science/algorithms/recursive-algorithms/a/the-factorial-function)
- [Logarithmic calculator](https://www.rapidtables.com/calc/math/Log_Calculator.html)
- [Logarithm wikipedia](https://en.wikipedia.org/wiki/Logarithm)
- [Fibonacci number algorithm optimizations](https://www.geeksforgeeks.org/program-for-nth-fibonacci-number/)
- [Modulo function](https://en.wikipedia.org/wiki/Modulo_operation)

### Big-O Notation
- [Asymptotic complexity / Big O Notation](https://brilliant.org/wiki/big-o-notation/)
- [Big O notation overview](https://rob-bell.net/2009/06/a-beginners-guide-to-big-o-notation/)
- [Big O cheat sheet for data structures and algorithms](http://bigocheatsheet.com/)

### Kotlin
- [Using Jetbrains Idea to create Kotlin and gradle projects, such as this one](https://www.jetbrains.com/help/idea/getting-started-with-gradle.html)
- [How to run Kotlin class in Gradle task](https://stackoverflow.com/questions/39576170/proper-way-to-run-kotlin-application-from-gradle-task)
- [Kotlin `until` vs `..`](https://kotlinlang.org/docs/reference/ranges.html)
- [CharArray and String](https://stackoverflow.com/questions/44772937/how-can-i-convert-chararray-arraychar-to-a-string)

### Markdown utilities
- [Generate TOCs for MD docs easily](https://github.com/thlorenz/doctoc/blob/master/README.md)
