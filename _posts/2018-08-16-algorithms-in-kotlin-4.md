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
title: "Algorithms in Kotlin, Recursion, Part 4/7"
categories:
- CS
- KT
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
  - [How to run this project](#how-to-run-this-project)
    - [Importing this project into Jetbrains IntelliJ IDEA](#importing-this-project-into-jetbrains-intellij-idea)
- [Induction](#induction)
- [Brute force approach](#brute-force-approach)
- [Recursion and breaking down the problem](#recursion-and-breaking-down-the-problem)
- [Other examples of using recursion](#other-examples-of-using-recursion)
  - [Quick Sort](#quick-sort)
  - [Binary Search](#binary-search)
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

## Induction
Let's use an example to illustrate induction. Let's say that you have a bunch of coins of
fixed denominations. And you're tasked with figuring out the fewest coins that you would
need to put together in order to arrive at some total amount. Let's say you have denominations
of 1, 5, 7, 11 and you're asked to see how few coins you can select in order to get a total of
49.

## Brute force approach
Using the brute force approach you could simply see how many 11 denomination coins would
get you close to the total. There would be a remainder (4 x 11 denomination coins = 44). Then
you could see how many 7 denomination coins fit. And so on with 5 and 1 denomination coins.
You could write this up in the following code.

```kotlin
/**
 * Brute force version of the recursive function [numCoins] above.
 *
 * - As you can see, there's a lot more code and complexity to compensate
 *   for very simplistic logic.
 * - The coin denominations are hard coded to be 1, 5, 7, 11.
 */
fun numCoins_nonrecursive(total: Int, coins: Coins) {
    // Exit condition
    if (total == 0) return

    var currencyRemoved = 0

    // Remove all the 11 coins
    val numberOf11s = (total / 11)
    if (numberOf11s > 0) {
        coins.numberOf11s += numberOf11s
        currencyRemoved += numberOf11s * 11
    }

    // Remove all the 7 coins
    val numberOf7s = (total - currencyRemoved) / 7
    if (numberOf7s > 0) {
        coins.numberOf7s += numberOf7s
        currencyRemoved += numberOf7s * 7
    }

    // Remove all the 5 coins
    val numberOf5s = (total - currencyRemoved) / 5
    if (numberOf5s > 0) {
        coins.numberOf5s += numberOf5s
        currencyRemoved += numberOf5s * 5
    }

    // Remove all the 1 coins
    val numberOf1s = (total - currencyRemoved) / 1
    if (numberOf1s > 0) {
        coins.numberOf1s += numberOf1s
        currencyRemoved += numberOf1s * 1
    }

}

data class Coins(var numberOf1s: Int = 0,
                 var numberOf5s: Int = 0,
                 var numberOf7s: Int = 0,
                 var numberOf11s: Int = 0) {
    override fun toString() = StringBuilder().apply {
        val result = mutableListOf<String>()
        arrayOf(::numberOf1s, ::numberOf5s, ::numberOf7s, ::numberOf11s)
            .forEach {
                if (it.get() > 0)
                    result.add("#${it.name} coins = ${it.get()}")
            }
        append(result.joinToString(", ", "{", "}").brightBlue())
    }.toString()
}
```

## Recursion and breaking down the problem
The brute force approach produced a lot of code. And the denominations of the coins that we can
use are hardcoded. This isn't a good solution. Instead if we use induction and implement it with
recursion, then we can do the following.
1. Come up with the simplest case that we can solve for (that will not require recursion).
2. Figure out a way to call the function that you're writing w/ arguments that represent
   a smaller subset of the problem and use the return value from the function to assemble
   the final result (whatever that may be).
   * This usually entails performing some logic and then generating new arguments
     for the same function, that break the problem down into smaller problems.
   * Calls need to be made to the function (recursively) and the result from these calls
     need to be combined into a final result somehow.

Using this approach this is what the code might look like for the minimum number of coins
problem.

```kotlin
/**
 * Use the process of induction to figure the min number of coins it
 * takes to come up with the given [total]. The coin denominations
 * you can used are in [denominations]; this list must be sorted
 * already (in descending order), eg: [11, 7, 5, 1].
 */
fun numCoins(total: Int,
             denominations: List<Int>,
             coinsUsedMap: MutableMap<Int, Int>): Int {
    // Show the function call stack
    println("\tnumCoins($total, $denominations)".brightYellow())

    // Stop recursing when these simple exit conditions are met
    if (total == 0) return 0
    if (denominations.isEmpty()) return 0

    // Breakdown the problem further
    val coinDenomination = denominations[0]
    var coinsUsed = total / coinDenomination

    // Remember how many coins of which denomination are used
    if (coinsUsed > 0) {
        coinsUsedMap[coinsUsed] = coinsUsedMap[coinsUsed] ?: 0
        coinsUsedMap[coinsUsed] = coinsUsedMap[coinsUsed]!! + 1
    }

    // Breakdown the problem into smaller chunk using recursion
    return coinsUsed +
        numCoins(total = total - coinsUsed * coinDenomination,
                 denominations = denominations.subList(1, denominations.size),
                 coinsUsedMap = coinsUsedMap)
}
```

## Other examples of using recursion

### Quick Sort

You can apply the steps above (simplest case, perform logic, split arguments into smaller
subset of the problem) to many other examples, such as quick sort.

```kotlin
/** O(n * log(n)) */
fun quick_sort(list: MutableList<Int>,
               startIndex: Int = 0,
               endIndex: Int = list.size - 1) {
    if (startIndex < endIndex) {
        // Perform some logic to break down the problem
        val pivotIndex = partition(list, startIndex, endIndex)
        
        // Recurse before pivot index
        quick_sort(list, startIndex, pivotIndex - 1) 
        
        // Recurse after pivot index
        quick_sort(list, pivotIndex + 1, endIndex) 
    }
}

/**
 * This function takes last element as pivot, places the pivot
 * element at its correct position in sorted list, and places
 * all smaller (smaller than pivot) to left of pivot and all greater
 * elements to right of pivot 
 */
fun partition(list: MutableList<Int>,
              startIndex: Int = 0,
              endIndex: Int = list.size - 1): Int {
    // Element to be placed at the correct position in the list
    val pivotValue = list[endIndex]

    // Index of smaller element
    var smallerElementIndex = startIndex

    // Make a single pass through the list
    for (index in startIndex until endIndex) {
        // If current element is smaller than equal to pivotValue
        // then swap it w/ the element at smallerElementIndex
        val valueAtIndex = list[index]
        if (valueAtIndex < pivotValue) {
            list.swap(smallerElementIndex, index)
            smallerElementIndex++
        }
    }

    // Finally move the pivotValue into the right place on the list
    list.swap(smallerElementIndex, endIndex)

    // Return the index just after where the pivot value ended up
    return smallerElementIndex
}

fun MutableList<Int>.swap(index1: Int, index2: Int) {
    val tmp = this[index1] // 'this' corresponds to the list
    this[index1] = this[index2]
    this[index2] = tmp
}
```

### Binary Search

```kotlin
fun binarySearch(item: String, list: List<String>): Boolean {
    // Exit conditions (base cases)
    if (list.isEmpty()) {
        return false
    }

    // Setup probe
    val size = list.size
    val probeIndex = size / 2
    val probeItem = list[probeIndex]

    // Does the probe match? If not, split and recurse
    when {
        item == probeItem -> return true
        item < probeItem -> return binarySearch(item, 
                                                list.subList(0, probeIndex), 
                                                stats)
        else -> return binarySearch(item, 
                                    list.subList(probeIndex + 1, size), 
                                    stats)
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
