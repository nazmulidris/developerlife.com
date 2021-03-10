---
author: Nazmul Idris
date: 2018-10-21 5:00:00+00:00
excerpt: |
  This tutorial is an exploration of extension functions and higher order functions in Kotlin by
  example
layout: post
title: "Kotlin Extension Function Expressions"
categories:
  - KT
---

<img class="post-hero-image" src="{{ 'assets/kotlin-awesomeness-hero.svg' | relative_url }}"/>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Lambdas and higher order functions](#lambdas-and-higher-order-functions)
- [Extension Functions and Lambdas](#extension-functions-and-lambdas)
  - [Example 1](#example-1)
  - [Example 2](#example-2)
  - [Example 3](#example-3)
  - [Example 4](#example-4)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Lambdas and higher order functions

[Chapter 5 of the Kotlin in Action book](https://livebook.manning.com#!/book/kotlin-in-action/chapter-5/) has a
fantastic deep dive into lambdas.

[Chapter 8 of the Kotlin in Action book](https://livebook.manning.com/#!/book/kotlin-in-action/chapter-8/) has a great
deep dive into higher order functions.

The following is an overly complex example of a calculator function that has 2 plugins (to add and subtract), built
using higher order functions.

```kotlin
run {
    val plusPlugin: (Int, Int) -> Int = { x, y -> x + y }
    val minusPlugin: (Int, Int) -> Int = { x, y -> x - y }
    val calc: (Int, Int, (Int, Int) -> Int) -> Int =
            { x, y, plugin ->
                val value = plugin(x, y)
                println(value)
                value
            }
    calc(1, 2, plusPlugin)
    calc(10, 5, minusPlugin)
    "complex-calculator-example"
}
```

## Extension Functions and Lambdas

Here's an example of passing a context object to a lambda:

```kotlin
// You can choose what object to bind `this` to in the `call` function.
call { println("${this} ${it}") }

// String.        : context
// (String)->Unit : lambda
fun call (functor: String.(String)->Unit) {
  functor("Context", "Jane")
  "Context".functor("Jane")
}
```

One of the key concepts is passing a context object to bind `this` to (in the lambda), very much like JavaScript's
[`call(thisObject, lambda)`](https://developer.mozilla.org
/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/call) method. Watch
[this video](https://www.youtube.com/watch?v=JzTeAM8N1-o&t=1535s) by Venkat Subramaniam on creating internal DSLs in
Kotlin.

Also,

- Watch [this video](https://youtu.be/A2LukgT2mKc?t=1020) by Jake Wharton explaining what this is.
- Great [stackoverflow discussion](https://stackoverflow.com/q/47329716/2085356) on this as well.

Here are more examples of this:

```kotlin
import java.time.*

fun main() {
    ex1()
    ex2()
    ex3()
    ex4()
}

fun ex1(){
    // String.        : context
    // (String)->Unit : lambda
    fun call (functor: String.(String)->Unit) {
        functor("Context", "Jane")
        "Context".functor("Jane")
    }

    // Similar to JS function.call(context, args), where context is this:
    // MDN docs for call: https://tinyurl.com/o8eh6te
    call { println("${this} ${it}") }
}

fun ex2(){
    val ago = "ago"
    val from_now = "from_now"
    infix fun Int.days(tense:String){
        val now = LocalDateTime.now();
        val delta = this.toLong();
        when(tense){
            ago -> println(now.minusDays(delta))
            from_now -> println(now.plusDays(delta))
            else -> println("?")
        }
    }

    // Simple internal DSL syntax.
    2 days ago
    2 days from_now
}

fun ex3(){
    class Meeting(val name: String){
      val start = this
      infix fun at(time:IntRange) {
          println("$name meeting starts at $time")
      }
    }

    infix fun String.meeting(block: Meeting.()->Unit){
        val meeting = Meeting(this)
        block(meeting)
        meeting.block()
    }

    // Simple internal DSL syntax.
    "planning" meeting {
        start at 3..15
    }
}

fun ex4(){
    class Robot{
        val left="left"
        val right="right"
        val fast="fast"

        infix fun turns(direction:String) { println("turns $direction") }
        infix fun runs(speed: String) { println("runs $speed") }
    }

    fun operate(block: Robot.(Robot)->Unit){
        val robot = Robot()
        block(robot, robot)
        robot.block(robot)
    }

    // Simple internal DSL syntax.
    operate{
     	it turns left
        it turns right
        it runs fast
    }
}
```

Extension Function Expressions combine:

1. **Extension functions** - Functions added to a type w/out modifying the original
1. **Function expressions** - Undeclared function bodies used as an expression (data)
1. **High order functions** - A function that takes a function or returns a function

Here's an unsophisticated example of using the 3 things above. This is a simple extension function that allows a List of
Strings to be filtered
[Run the code in the Kotlin playground](https://play.kotlinlang.org/#eyJ2ZXJzaW9uIjoiMS4zLVJDIiwicGxhdGZvcm0iOiJqYXZhIiwiYXJncyI6IiIsIm5vbmVNYXJrZXJzIjp0cnVlLCJ0aGVtZSI6ImlkZWEiLCJmb2xkZWRCdXR0b24iOnRydWUsInJlYWRPbmx5IjpmYWxzZSwiY29kZSI6ImZ1biBtYWluKCkge1xuICAgIHZhbCBkYXRhID0gbGlzdE9mKFwibW9ua2V5XCIsIFwiZG9ua2V5XCIsIFwiYmFuYW5hXCIsIFwiYXBwbGVcIilcbiAgICBwcmludGxuKGRhdGEuZmlsdGVyeyBpdC5zdGFydHNXaXRoKFwiYlwiKX0pXG59XG5cbmZ1biA8VD4gTGlzdDxUPi5maWx0ZXIoYWxsb3c6IChUKSAtPiBCb29sZWFuKTogTGlzdDxUPntcbiAgICB2YWwgbmV3TGlzdCA9IEFycmF5TGlzdDxUPigpXG4gICAgZm9yKCBpdGVtIGluIHRoaXMgKXtcbiAgICAgICAgaWYgKGFsbG93KGl0ZW0pKSB7IG5ld0xpc3QuYWRkKGl0ZW0pIH1cbiAgICB9XG4gICAgcmV0dXJuIG5ld0xpc3Q7XG59In0=).

```kotlin
fun main() {
    val data = listOf("monkey", "donkey", "banana", "apple")
    println( data.filter{ it.startsWith("b") } )
}

fun <T> List<T>.filter(allow: (T) -> Boolean): List<T>{
    val newList = ArrayList<T>()
    for( item in this ){
        if (allow(item)) { newList.add(item) }
    }
    return newList
}
```

### Example 1

Here's the sophisticated version of this leveraging Extension Function Expressions!
[Run the code in the Kotlin playground](https://play.kotlinlang.org/#eyJ2ZXJzaW9uIjoiMS4zLVJDIiwicGxhdGZvcm0iOiJqYXZhIiwiYXJncyI6IiIsIm5vbmVNYXJrZXJzIjp0cnVlLCJ0aGVtZSI6ImlkZWEiLCJmb2xkZWRCdXR0b24iOnRydWUsInJlYWRPbmx5IjpmYWxzZSwiY29kZSI6ImZ1biBtYWluKCkge1xuICAgIHZhbCBkYXRhID0gbGlzdE9mKFwibW9ua2V5XCIsIFwiZG9ua2V5XCIsIFwiYmFuYW5hXCIsIFwiYXBwbGVcIilcbiAgICBwcmludGxuKGRhdGEuZmlsdGVyeyBzdGFydHNXaXRoKFwibVwiKX0gKVxufVxuXG5mdW4gPFQ+IExpc3Q8VD4uZmlsdGVyKGFsbG93OiBULigpIC0+IEJvb2xlYW4pOiBMaXN0PFQ+e1xuICAgIHZhbCBuZXdMaXN0ID0gQXJyYXlMaXN0PFQ+KClcbiAgICBmb3IoIGl0ZW0gaW4gdGhpcyApe1xuICAgICAgICBpZiAoaXRlbS5hbGxvdygpKSB7IG5ld0xpc3QuYWRkKGl0ZW0pIH1cbiAgICB9XG4gICAgcmV0dXJuIG5ld0xpc3Q7XG59In0=).

```kotlin
fun main() {
    val data = listOf("monkey", "donkey", "banana", "apple")
    println( data.filter{ startsWith("m") } )
}

fun <T> List<T>.filter(allow: T.() -> Boolean): List<T>{
    val newList = ArrayList<T>()
    for( item in this ){
        if (item.allow()) { newList.add(item) }
    }
    return newList
}
```

Notes:

1. `allow: T.() -> Boolean` is used instead of `allow: (T) -> Boolean` (from the unsophisticated example). The `T.`
   means that the function expression is an extension function of `T` itself!

1. This means that `allow()` is an extension function of `T`!

1. Since `allow()` is an extension function of `T`, `this` is passed to it, which in this case is a `String`.

1. Given the change above, the `if (item.allow()) { newList.add(item) }` statement is used instead of
   `if (allow(item)) { newList.add(item) }` (from the unsophisticated example).

### Example 2

The following example shows a toast, and allows the creation of a simple DSL syntax for creating the toast. And there's
no way to forget calling `show()` once it's created!

```kotlin
inline fun toast(context: Context,
                 text: String = "",
                 duration: Int = Toast.LENGTH_SHORT,
                 functor: Toast.() -> Unit) {
    val toast: Toast = Toast.makeText(context, text, duration)
    toast.functor()
    toast.show()
}
```

Example of using the function above (with simple DSL syntax for making the toast).

```kotlin
toast(fragment.getParentActivity()) {
    setText(R.string.message_cant_make_autocomplete_request_if_location_is_null)
    duration = Toast.LENGTH_LONG
}
```

Note that the `toast()` function has 1 required parameter (`context`) and the other parameters are optional (and have
default values). This means that you can call this function w/ just the 1st argument. In the DSL syntax, the middle 2
arguments aren't passed, and only the 1st argument (`fragment.getParentActivity()`) and the last argument (the lambda
expression) is passed.

### Example 3

Very similar to Example 2, but this is for showing a Snackbar. Again, there's no way to forget calling `show()` after
the Snackbar has been created.

```kotlin
inline fun snack(view: View,
                 text: String = "",
                 duration: Int = Snackbar.LENGTH_SHORT,
                 functor: Snackbar.() -> Unit) {
    val snackbar: Snackbar = Snackbar.make(view, text, duration)
    snackbar.functor()
    snackbar.show()
}
```

How the function above might be used.

```kotlin
snack(fragmentContainer) {
    setText(R.string.message_making_api_call_getCurrentPlace)
    duration = Snackbar.LENGTH_SHORT
}
```

### Example 4

This is an example of a
[non local return, Kotlin in Action, Ch 8](https://livebook.manning.com#!/book/kotlin-in-action/chapter-8/point-3290-152-152-0)
for an extension function w/ lambdas.

```kotlin
public inline fun <T : AutoCloseable?, R> T.use(block: (T) -> R): R {
    var exception: Throwable? = null
    try {
        return block(this)
    } catch (e: Throwable) {
        exception = e
        throw e
    } finally {
        try { this.close() }
        catch(closeException: Throwable){exception?.addSuppressed(closeException)}
    }
}
```

Example of using this is shown below.

```kotlin
fun readFirstLineFromFile(path: String): String {
    BufferedReader(FileReader(path)).use { br ->
        return br.readLine()
    }
}
```

Notes:

- When the return executes in the lambda, it returns from the function in which the lambda was called from (not just the
  lambda block itself).

- The return from the outer function is possible only if the function that takes the lambda as an argument is inlined.

- More information on when to inline extension functions in
  [Kotlin in Action, Ch 8](https://livebook.manning.com/#!/book/kotlin-in-action/chapter-8/132). Basically its best to
  include a function extension that accepts lambdas (IntelliJ IDEA has hints that help with this).

You can write a local return from a lambda expression as well. A local return in a lambda is similar to a break
expression in a for loop. It stops the execution of the lambda and continues execution of the code from which the lambda
was invoked. To distinguish a local return from a non-local one, you use labels. You can label a lambda expression from
which you want to return, and then refer to this label after the return keyword.

```kotlin
data class Person(val name: String, val age: Int)
val people = listOf(Person("Alice", 29), Person("Bob", 31))
fun lookForAlice(people: List<Person>) {
    people.forEach label@{
        if (it.name == "Alice") return@label
    }
    println("Alice might be somewhere")
}
```
