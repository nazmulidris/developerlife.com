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
title: "Algorithms in Kotlin, Binary Trees, Part 6/7"
categories:
- CS
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
  - [How to run this project](#how-to-run-this-project)
    - [Importing this project into Jetbrains IntelliJ IDEA](#importing-this-project-into-jetbrains-intellij-idea)
- [Binary Trees](#binary-trees)
- [Node data structure](#node-data-structure)
- [Building the tree](#building-the-tree)
- [Pre-order, in-order, and post-order recursive traversal](#pre-order-in-order-and-post-order-recursive-traversal)
- [BFS (breadth first search) using a Queue](#bfs-breadth-first-search-using-a-queue)
  - [Notes on the implementation](#notes-on-the-implementation)
- [BFS (pretty print)](#bfs-pretty-print)
  - [Notes on implementation](#notes-on-implementation)
- [DFS (depth first search) using a Stack](#dfs-depth-first-search-using-a-stack)
  - [Notes on the implementation](#notes-on-the-implementation-1)
- [Console output from running the code](#console-output-from-running-the-code)
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

## Binary Trees
![]({{'assets/algo-5.png' | relative_url}})

## Node data structure
```kotlin
data class Node<T>(val value: T,
                   var leftNode: Node<T>?,
                   var rightNode: Node<T>?,
                   var depth: Int = 0) {
    fun link(left: Node<T>?, right: Node<T>?) = this.apply { 
        linkLeft(left).linkRight(right) 
    }

    fun linkLeft(left: Node<T>?) = this.apply { leftNode = left }

    fun linkRight(right: Node<T>?) = this.apply { rightNode = right }

    fun depth(value: Int) = this.apply { depth = value }

    /**
     * Nodes on the left are in yellow, and those on the right are blue.
     */
    override fun toString(): String {
        return StringBuffer().apply {
            append("{${value.toString().green()}")
            if (leftNode != null)
                append(", ${leftNode.toString().yellow()}")
            if (rightNode != null)
                append(", ${rightNode.toString().blue()}}")
        }.toString()
    }
}
```

## Building the tree
The tree shown in the diagram above is built in code as follows.
```kotlin
/**
 * [Image of the generated tree](http://tinyurl.com/yckmlfkt)
 *        [A]
 *       /   \
 *     [B]    [C]
 *     / \    /  \
 *  [D]  [E] [F] [G]
 *               / \
 *             [H] [I]
 */
fun buildTree(): Node<Char> {
    val a = Node('a', null, null)
    val b = Node('b', null, null)
    val c = Node('c', null, null)
    val d = Node('d', null, null)
    val e = Node('e', null, null)
    val f = Node('f', null, null)
    val g = Node('g', null, null)
    val h = Node('h', null, null)
    val i = Node('i', null, null)

    a.link(b, c)
    b.link(d, e)
    c.link(f, g)
    g.link(h, i)

    return a
}
```

## Pre-order, in-order, and post-order recursive traversal

```kotlin
/**
 * A neat trick for pre-order traversals: starting from the root,
 * go around the tree counterclockwise. Print each node when you
 * pass its left side.
 */
fun <T> traversalPreOrder(node: Node<T>?, list: MutableList<T>) {
    if (node != null) {
        list.add(node.value)
        traversalPreOrder(node.leftNode, list)
        traversalPreOrder(node.rightNode, list)
    }
}

/**
 * A neat trick for in-order traversals: starting from the root,
 * go around the tree counterclockwise. Print each node when you
 * pass its bottom side.
 */
fun <T> traversalInOrder(node: Node<T>?, list: MutableList<T>) {
    if (node != null) {
        traversalInOrder(node.leftNode, list)
        list.add(node.value)
        traversalInOrder(node.rightNode, list)
    }
}

/**
 * A neat trick for post-order traversals: starting from the root,
 * go around the tree counterclockwise. Print each node when you
 * pass its right side.
 */
fun <T> traversalPostOrder(node: Node<T>?, list: MutableList<T>) {
    if (node != null) {
        traversalPostOrder(node.leftNode, list)
        traversalPostOrder(node.rightNode, list)
        list.add(node.value)
    }
}
```

## BFS (breadth first search) using a Queue

```kotlin
/**
 * Traverses the binary tree nodes in a sorted order.
 */
fun <T> breadthFirstTraversal(root: Node<T>): MutableList<Node<T>> {
    val queue = LinkedList<Node<T>>()
    val traversalList = mutableListOf<Node<T>>()

    // Add first node
    queue.add(root)

    // Use stack to create breadth first traversal
    while (queue.isNotEmpty()) {
        val currentNode = queue.poll()
        val depth = currentNode.depth

        // Add left node first
        if (currentNode.leftNode != null)
            queue.add(currentNode.leftNode!!.depth(depth + 1))

        // Add right node next
        if (currentNode.rightNode != null)
            queue.add(currentNode.rightNode!!.depth(depth + 1))

        // Add the node to the traversal list
        traversalList.add(currentNode)
    }

    return traversalList
}
```

### Notes on the implementation
- BFS traversal of a binary tree results in a the nodes being visited in their sorted order.
- The trick in the `while` loop is leveraging the FIFO nature of the queue and allow the traversal
of the tree from left node to right node, which results in a breadth first traversal.
- A `depth` field in the `Node` class is what keeps track of the number of branches from the root
to this `Node`.
- The `Deque` interface supports both Stack and Queue ADTs (abstract data types).

## BFS (pretty print) 
```kotlin
/**
 * Traverses the binary tree nodes in a sorted order.
 */
fun <T> printBFSTraversal(root: Node<T>): String {

    val queue = LinkedList<Node<T>>()
    // Add first node
    queue.add(root)

    val mapVisitedDepth = mutableMapOf<Int, MutableList<T>>()
    // Use stack to create breadth first traversal
    while (queue.isNotEmpty()) {
        val currentNode = queue.poll()
        val depth = currentNode.depth

        // Add left node first
        if (currentNode.leftNode != null)
            queue.add(currentNode.leftNode!!.depth(depth + 1))

        // Add right node next
        if (currentNode.rightNode != null)
            queue.add(currentNode.rightNode!!.depth(depth + 1))

        // Decide whether to print crlf or not
        if (!mapVisitedDepth.containsKey(depth)) {
            mapVisitedDepth[depth] = mutableListOf()
        }
        mapVisitedDepth[depth]!!.add(currentNode.value)
    }

    val outputString = StringBuilder()

    for (entry in mapVisitedDepth) {
        outputString.append(entry.value.joinToString(", ", postfix = "\n"))
    }

    return outputString.toString()
}
```

### Notes on implementation
- This is almost identical to the code above. The main difference here is that a
  `mapVisitedDepth` `Map` is used in order to keep track of the depth of each
  traversed node, which can then be used to pretty print the output where a CRLF
  is added at the start of each new depth.

## DFS (depth first search) using a Stack
```kotlin
fun <T> depthFirstTraversal(root: Node<T>): MutableList<Node<T>> {
    val visitedMap = mutableMapOf<Node<T>, Boolean>()
    val stack = LinkedList<Node<T>>()
    val traversalList = mutableListOf<Node<T>>()

    // Add first node
    stack.push(root)

    // Use stack to create breadth first traversal
    while (stack.isNotEmpty()) {
        val currentNode = stack.pop()
        val depth = currentNode.depth

        // If the currentNode key can't be found in the map, then insert it
        visitedMap[currentNode] = visitedMap[currentNode] ?: false

        if (!visitedMap[currentNode]!!) {
            // Push right child to stack FIRST (so this will be processed LAST)
            if (currentNode.rightNode != null)
                stack.push(currentNode.rightNode!!.depth(depth + 1))

            // Push left child to stack LAST (so this will be processed FIRST)
            if (currentNode.leftNode != null)
                stack.push(currentNode.leftNode!!.depth(depth + 1))

            // Mark the current node visited and add to traversal list
            visitedMap[currentNode] = true
            traversalList.add(currentNode)
        }
    }

    return traversalList
}
```

### Notes on the implementation
- The trick in the `while` loop is to leverage the LIFO nature of stack, in order to push
the children on the right on top of the stack first, before the children on the left. Since the
algorithm pops these items off the top of the stack, whatever was pushed last will get processed
sooner (that what was pushed first). And this is what results in a depth first search.
- A `depth` field in the `Node` class is what keeps track of the number of branches from the root
to this `Node`.
- The `Deque` interface supports both Stack and Queue ADTs (abstract data types).
- A map is needed to keep track of nodes that have already been visited. This is different
than what is required for the BFS algorithm.

## Console output from running the code
![]({{'assets/algo-6.png' | relative_url}})

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
