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
title: "Algorithms in Kotlin, Caches, Part 7/7"
categories:
- CS
- KT
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
  - [How to run this project](#how-to-run-this-project)
    - [Importing this project into JetBrains IntelliJ IDEA](#importing-this-project-into-jetbrains-intellij-idea)
- [LRU and MRU](#lru-and-mru)
  - [Notes on implementation](#notes-on-implementation)
- [References](#references)
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

Once you've cloned the repo, type `./gradlew run` in order to build
and run this project from the command line.

#### Importing this project into JetBrains IntelliJ IDEA

- This project was created using JetBrains Idea as a Gradle and Kotlin project
([more info](https://www.jetbrains.com/help/idea/getting-started-with-gradle.html)).
    - When you import this project into Idea as a Gradle project, 
    make sure not to check "Offline work" (which if checked, won't
    allow the gradle dependencies to be downloaded).
    - As of Jun 24 2018, [Java 10 doesn't work w/ this gradle distribution](
    https://github.com/gradle/gradle/issues/4503) (v4.4.x), so you can use Java 9 or 8,
    or upgrade to a newer version of gradle (4.8+).

## LRU and MRU
```kotlin
enum class Type { LRU, MRU }

class Cache<T>(val type: Type, val size: Int) {
    val map = mutableMapOf<T, Int>()
    var rank = 0

    fun put(value: T): T? {
        var evictedKey: T? = null

        when {
            map.containsKey(value) -> {
                // Increase rank of existing value.
                map[value] = rank++
            }
            map.size == size -> {
                // Remove the lowest or highest rank item in the map
                // depending on Type.
                evictedKey = findKeyToEvict()
                map.remove(evictedKey)
                map.put(value, rank++)
            }
            else -> {
                // Add the new item.
                map.put(value, rank++)
            }
        }

        return evictedKey
    }

    /**
     * LRU means evict the item in the map w/ the lowest rank.
     * MRU means evict the item in the map w/ the highest rank.
     */
    fun findKeyToEvict(): T {
        var rankToEvict = map.values.first()
        var keyToEvict = map.keys.first()

        when (type) {
            Type.MRU -> {
                // Find the highest rank item.
                for (entry in map) {
                    if (entry.value > rankToEvict) {
                        rankToEvict = entry.value
                        keyToEvict = entry.key
                    }
                }
            }
            Type.LRU -> {
                // Find the lowest rank item.
                for (entry in map) {
                    if (entry.value < rankToEvict) {
                        rankToEvict = entry.value
                        keyToEvict = entry.key
                    }
                }
            }
        }

        return keyToEvict
    }
    
    override fun toString(): String = StringBuilder().apply {
        val list = mutableListOf<String>().apply {
            for (entry in map) 
                add("'${entry.key}'->rank=${entry.value}".yellow())
        }
        append(list.joinToString(", ", "{", "}"))
    }.toString()
}
```

### Notes on implementation
- According to the LRU Algorithm, the lowest rank item will be removed when a new one is inserted
  and there's no space left in the cache. Also, every time an item is inserted into the cache
  it's rank is set to the highest rank.
- According to the MRU Algorithm, the highest rank item will be removed when a new one is inserted
  and there's no space left in the cache. Also, every time an item is inserted into the cache
  it's rank is set to the highest rank.

## References
You can get more information on Cache replacement policies on
[wikipedia](https://en.wikipedia.org/wiki/Cache_replacement_policies).

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
- [Using JetBrains Idea to create Kotlin and gradle projects, such as this one](https://www.jetbrains.com/help/idea/getting-started-with-gradle.html)
- [How to run Kotlin class in Gradle task](https://stackoverflow.com/questions/39576170/proper-way-to-run-kotlin-application-from-gradle-task)
- [Kotlin `until` vs `..`](https://kotlinlang.org/docs/reference/ranges.html)
- [CharArray and String](https://stackoverflow.com/questions/44772937/how-can-i-convert-chararray-arraychar-to-a-string)

### Markdown utilities
- [Generate TOCs for MD docs easily](https://github.com/thlorenz/doctoc/blob/master/README.md)
