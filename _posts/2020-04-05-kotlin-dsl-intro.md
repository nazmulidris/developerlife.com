---
author: Nazmul Idris
date: 2020-04-05 5:00:00+00:00
excerpt: |
  This tutorial is an introduction to Kotlin internal DSLs using examples
layout: post
title: "Kotlin DSL Introduction"
categories:
  - KT
---

<img class="post-hero-image" src="{{ 'assets/kotlin-awesomeness-hero.svg' | relative_url }}"/>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Kotlin internal DSLs](#kotlin-internal-dsls)
- [Fluency](#fluency)
- [Context, and rebinding this](#context-and-rebinding-this)
  - [Summary](#summary)
- [Example of a DSL that allows console output to be colored](#example-of-a-dsl-that-allows-console-output-to-be-colored)
- [Example of a DSL that executes a list of lambdas while a condition is met](#example-of-a-dsl-that-executes-a-list-of-lambdas-while-a-condition-is-met)
- [Further reading](#further-reading)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Kotlin internal DSLs

There are many useful DSLs out there that make specific programming tasks easier. CSS and HTML are good examples that
come to mind. They both make it easier to create content for web pages that would otherwise be tedious to create if we
had to use the DOM API to create them. However, they both require the creation of a parser for the DSL.

Kotlin internal DSLs are a way to work within the boundaries of the Kotlin language and leverage the Kotlin compiler
itself to generate DSLs using Kotlin itself. Kotlin does not use VM byte code injection, and instead the DSL syntax is
syntactic sugar that gets compiled down to bytecode by the Kotlin compiler itself.

Please watch this great video -
[KotlinConf 2018 - Creating Internal DSLs in Kotlin by Venkat Subramaniam](https://www.youtube.com/watch?v=JzTeAM8N1-o)
to learn more about Kotlin DSLs before getting started with this tutorial. It's a very easy to follow video and sets up
really important background information for understanding DSLs.

## Fluency

Kotlin allows many things in code to be removed from the syntax, like semicolons, too many parentheses, etc. It also
allows for lambdas that are the last parameter of a function to have a special syntax when calling them. Additionally
operators can be overloaded, and infix functions can be created (which make the `.` unncessary when making a method call
on an object). And there's support for extension functions and implicit recievers which provide a rich set of tools that
we can leverage in order to create DSLs. Keep in mind though that we have to work within the constraints of the Kotlin
language and compiler itself in order to be able to express our DSL.

Here's a simple example of the `infix` keyword which allows us to drop the `.` and parentheses for the argument.

```kotlin
fun main() {
  val car = Car()
  car.drive(10) // Regular method call.
  car drive 10 // Infix method call.
}
class Car {
  infix fun drive(dist: Int){
     println("Driving $dist miles")
  }
}
```

## Context, and rebinding this

If you have JavaScript experience, then you know that you can bind `this` to any object that you would like when you are
calling a function using the
[`call()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/call) function. For
people coming from the Java world, this is a very strange concept indeed. Kotlin allows you to pass different contexts
into function calls (when creating DSLs) which is actually one of the major language capabilities that make internal
DSLs possible.

Here's some JavaScript code that shows how `this` can be bound to any object that you desire.

```javascript
function greet(name) {
  console.log(`${this.toUpperCase()} ${name}!`);
}
greet.call("hello", "Nora"); // The first argument is bound to `this` in the call to `greet()`.
```

Here's a Kotlin equivalent of this code in action.

```kotlin
fun call(block: MutableList<String>.(String) -> Unit) {
  val context = mutableListOf("Hello")
  val argument = "Nora"
  block(/* context aka `this`= */ context, /* argument aka `it`= */ argument)
}

call {
  // `context` argument binds to `this`, so `this: MutableList<String>`.
  // `it` parameter holds the argument passed, so `it: String`.
  println("${this.joinToString { it.toUpperCase() }} $it")
}
```

If you look at the `call` function, the `block` parameter has this signature: `MutableList<String>.(String) -> Unit`.
Let's break this down.

1. Right side `(String) -> Unit` - this simply says that the lambda will accept a single argument of type `String`.
2. Left side `Mutable<String>.` - this is more interesting, this says that the lambda above will have `this` bound to an
   object of type `MutableList<String>`. In other words, the context passed to the lambda will be of type
   `MutableList<String>`.

Now, let's take a look at the code at the call site of this `call` function.

The lambda that is passed to `call` has the following things.

1. `it` is of type `String` and is bound to the argument that is passed to it in the `call` function (`"Nora"`).
2. `this` is of type `MutableList<String>` and is bound to the context argument that is passed in the `call` function
   implementation (`mutableListOf("Hello")`).

### Summary

This takes a little getting used to, but once you get the hang of it, you know that:

1. The thing on the left side of the `.` in the method signature is the context.
2. The thing on the right side is the lambda's function signature. And that you can potentially pass an argument to this
   lambda.

```text
fun call(block: MutableList<String>.(String) -> Unit) {}
                ^                   ^
                1. the context      2. the lambda function signature
                                       (and possible argument)
```

And on the flip side, when you're writing the lambda passed to this `call` function, you can expect:

1. `this` will be of type `MutableList<String>` (the thing on the left).
2. `it` will be of type `(String)` (the parameter to the thing on the right).

## Example of a DSL that allows console output to be colored

Let's say that you want to create console log output with colors, instead of boring old black and white. When we come up
with a DSL, one of the first things we have to do is come up with some idea of what our DSL will look like (assuming it
has already been implemented).

So here's some code I came up with that I would like to generate console log output in color.

```kotlin
fun main() {
  colorConsole {//this: ColorConsoleContext
    printLine {//this: MutableList<String>
      span(Colors.Purple, "word1")
      span("word2")
      span(Colors.Blue, "word3")
    }
    printLine {//this: MutableList<String>
      span(Colors.Green, "word1")
      span(Colors.Purple, "word2")
    }
    println(
        line {//this: MutableList<String>, it: ColorConsoleContext
          add(Colors.Green("word1"))
          add(Colors.Blue("word2"))
        })
  }
}
```

For this DSL, the main enclosing function is `console`, to which we pass a lambda. Inside the lambda, we can use
`printLine` function or `line` function to express what to log exactly. We can pass lambdas to each of these functions,
and note that when using `line`, `it` is available for use in the lambda, and when using `printLine` `it` isn't
available.

Here's the code that makes this DSL possible.

```kotlin
class ColorConsoleContext {
  companion object {
    fun colorConsole(block: ColorConsoleContext.() -> Unit) {
      ColorConsoleContext().apply(block)
    }
  }

  fun printLine(block: MutableList<String>.() -> Unit) {
    println(line {
      block(this)
    })
  }

  fun line(block: MutableList<String>.(ColorConsoleContext) -> Unit): String {
    val messageFragments = mutableListOf<String>()
    block(messageFragments, this)
    val timestamp = SimpleDateFormat("hh:mm:sa").format(Date())
    return messageFragments.joinToString(separator = ", ", prefix = "$timestamp: ")
  }

  /**
   * Appends all arguments to the given [MutableList].
   */
  fun MutableList<String>.span(color: Colors, text: String): MutableList<String> {
    add(color.ansiCode + text + Colors.ANSI_RESET.ansiCode)
    return this
  }

  /**
   * Appends all arguments to the given [MutableList].
   */
  fun MutableList<String>.span(text: String): MutableList<String> {
    add(text + Colors.ANSI_RESET.ansiCode)
    return this
  }
}

enum class Colors(val ansiCode: String) {
  ANSI_RESET("\u001B[0m"),
  Black("\u001B[30m"),
  Red("\u001B[31m"),
  Green("\u001B[32m"),
  Yellow("\u001B[33m"),
  Blue("\u001B[34m"),
  Purple("\u001B[35m"),
  Cyan("\u001B[36m"),
  White("\u001B[37m");

  operator fun invoke(content: String): String {
    return "${ansiCode}$content${ANSI_RESET.ansiCode}"
  }

  operator fun invoke(content: StringBuilder): StringBuilder {
    return StringBuilder("${ansiCode}$content${ANSI_RESET.ansiCode}")
  }
}
```

> I've open sourced this as a gradle dependency named `color-console`. You can get it on
> [GitHub](https://github.com/nazmulidris/color-console).

## Example of a DSL that executes a list of lambdas while a condition is met

Let's say that you have a list of lambdas. And that you want to execute them in sequence, as long as a condition is met
(is true). Here's an example of what DSL for this use case may look like.

```kotlin
import actions.createConditionalRunnerScope
import org.assertj.core.api.Assertions
import org.junit.Test

class ConditionalRunnerDslTest {
  @Test
  fun testCreateConditionalRunnerScope() {
    var count = 1
    var executionCount = 1
    createConditionalRunnerScope {
      condition { count < 4 }
      addLambda { count++; executionCount++ }
      addLambda { count++; executionCount++ }
      addLambda { count++; executionCount++ }
      addLambda { count++; executionCount++ }
      addLambda { count++; executionCount++ }
      addLambda { count++; executionCount++ }
      runEachLambdaUntilConditionNotMet()
    }
    Assertions.assertThat(count).isEqualTo(4)
    Assertions.assertThat(executionCount).isEqualTo(4)
  }
}
```

To implement this DSL, here's the code.

```kotlin
package actions

/**
 * DSL to run a sequence of lambdas as long as the condition is met. As soon as the condition is not met, execution
 * stops.
 */
fun createConditionalRunnerScope(block: FunctionCollector.() -> Unit) {
  val myFunctionCollector = FunctionCollector()
  block(myFunctionCollector)
}

class FunctionCollector() {
  lateinit var conditionBlock: () -> Boolean
  val lambdaList: MutableList<() -> Unit> = mutableListOf()

  fun condition(block: () -> Boolean) {
    conditionBlock = block
  }

  fun addLambda(block: () -> Unit) {
    lambdaList.add(block)
  }

  fun runEachLambdaUntilConditionNotMet() {
    for (function in lambdaList) {
      colorConsole {
        printLine {
          if (conditionBlock()) span(Colors.Green, "Condition == true")
          else span(Colors.Red, "Condition == false")
        }
      }
      if (conditionBlock()) {
        colorConsole {
          printLine {
            span(Colors.Green, "invoking function")
          }
        }
        function()
      }
      else {
        colorConsole {
          printLine {
            span(Colors.Red, "breaking out of runEachUntilConditionNotMet()")
          }
        }
        return
      }
    }
  }
}
```

## Further reading

I've got a GitHub repo [here](https://github.com/nazmulidris/kt-scratch/tree/main/src/main/kotlin/dsl), where you can
find many more examples (including the `console` example shown above).

Please clone the repo, and take a look at the sources, and run the code to try it out for yourself. The best way to get
good with DSLs is to spend a lot of time tinkering with this stuff and making your own.

As Venkat Subramaniam says in his [video](https://www.youtube.com/watch?v=JzTeAM8N1-o), you will need 2 things:

1. Patience,
2. Coffee. 🤣

Enjoy! 😃
