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
title: "Algorithms in Kotlin, Strings, Part 2/7"
categories:
- CS
- KT
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
  - [How to run this project](#how-to-run-this-project)
    - [Importing this project into Jetbrains IntelliJ IDEA](#importing-this-project-into-jetbrains-intellij-idea)
- [Substring search](#substring-search)
  - [O(n * m) - Brute force approach](#on--m---brute-force-approach)
  - [O(n + m) - Using a state machine](#on--m---using-a-state-machine)
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

## Substring search
It is a very common problem to search for the presence of a substring inside of a string.
Let's say that:
- the string is called `str` (with length `n`)
- the substring is `substr` (with length `m`).

### O(n * m) - Brute force approach
The brute force approach to string searches is done by simply sliding the pattern along the
string until you find a match. Every time you slide down to the next character in `str`, this
algorithm doesn't really remember what it already knows about the string (since it iterates thru
the entire length of the string at every iteration). It essentially forgets about what it knows 
about the string (already) for every `n-1` attempts that it makes to match the substring.

```kotlin
/**
 * O(m * n), where m = str.size, and n = substr.size.
 *
 * This is an inefficient brute force algorithm which has quadratic complexity O(n^2).
 */
fun substring(str: CharArray, substr: CharArray): Any {
    // substr can't be longer than str.
    if (substr.size > str.size) return "not found"

    // Iterate str using cursor1 and for each index look ahead to see if matches exist 
    // for substr.
    var occurrences = 0
    for (cursor1 in 0 until str.size) {
        var matchCount = 0
        for (cursor2 in 0 until substr.size) {
            if (str[cursor1 + cursor2] == substr[cursor2]) matchCount++
        }
        // Found a match.
        if (matchCount == substr.size) occurrences++
    }

    return object {
        val numberOfMatches = occurrences
        val matchFound = occurrences > 0
        override fun toString(): String = StringBuilder().apply {
            append("{match found = $matchFound")
            append(", # matches = $numberOfMatches}")
        }.toString().brightBlue()
    }
}
```

Please note that if you want to turn a Kotlin `String` into a `CharArray` you can use
something like `"Hello world".toCharArray()`. Here's more info about this on 
[stackoverflow](https://stackoverflow.com/questions/44772937/how-can-i-convert-chararray-arraychar-to-a-string).

### O(n + m) - Using a state machine
By using a state machine that is built from the substring pattern we can come up with a much better
algorithm to match these patterns inside our string. The idea here is not to forget what we have
already seen about the string as we iterate over each character in it. 

This is a streaming algorithm where we pass one character at a time (as we iterate thru the 
entire string) to a state maachine which matches the pattern in the substring. 
For every iteration:
- Each character is compared with the character at a cursor (which represents the state)
in the substring.
- If there's a match, this cursor is incremented, and at the next iteration, the next character
in the pattern will be matched, and so on.
- When there's a mismatch the cursor is reset to 0.
- And we know a match has been found when the cursor equals the length of the substring.

This approach is based on the idea of
[Deterministic Finite Automaton](https://en.wikipedia.org/wiki/Deterministic_finite_automaton).

```kotlin
/**
 * O(m + n), where m = str.size, and n = substr.size
 *
 * This function uses a deterministic finite automation (DFA) method
 * which entails the use of a state machine to keep track of progress
 * in a game.
 */
fun substring_optimized(str: CharArray, substr: CharArray): Any {

    class StateMachine(val pattern: CharArray) {
        var cursor = 0
        fun add(character: Char) {
            if (pattern[cursor] == character) cursor++
            else cursor = 0
        }

        fun isMatch() = cursor == pattern.size
        fun reset() {
            cursor = 0
        }
    }

    val stateMachine = StateMachine(substr)
    var numberOfOccurrences = 0

    for (cursor in 0 until str.size) {
        stateMachine.add(str[cursor])
        if (stateMachine.isMatch()) {
            stateMachine.reset()
            numberOfOccurrences++
        }
    }

    return object {
        val occurrences = numberOfOccurrences
        val matchFound = numberOfOccurrences > 0
        override fun toString(): String = StringBuilder().apply {
            append("{occurrences = $occurrences")
            append(", matchFound = $matchFound}")
        }.toString().brightBlue()
    }

}
```

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
