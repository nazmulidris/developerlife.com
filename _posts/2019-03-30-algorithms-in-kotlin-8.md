---
author: Nazmul Idris
date: 2019-03-30 11:00:00+00:00
excerpt: |
  This tutorial shows how one might schedule ordered tasks that need to be
  executed when a particular state is reached. However, these states 
  might be reached in any order.
layout: post
hero-image: assets/algo-hero.svg
title: "Algorithms in Kotlin, Schedule ordered tasks"
categories:
- CS
- KT
- State
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Problem Definition](#problem-definition)
- [Solution in Kotlin using a state machine](#solution-in-kotlin-using-a-state-machine)
- [Source code](#source-code)
  - [How to run this project](#how-to-run-this-project)
    - [Importing this project into JetBrains IntelliJ IDEA](#importing-this-project-into-jetbrains-intellij-idea)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Problem Definition

This tutorial showcases the use of a state management algorithm in Kotlin that
can be used to schedule ordered tasks. 

The idea is that there are a set of tasks that must be executed when a specific
state is reached. Eg: in a camera app, certain tasks might be executed when
certain hardware components become ready, but these might become ready in an
arbitrary sequence. And tasks can only be executed in the expected ordered
sequence.

Using a concrete example, let's say there is an ordered sequence of 3 states:
`[A, B, C]`. There are some tasks that execute when state `A` transition occurs.
Others execute when `B` transition occurs, etc. However, these transitions don't
occur in order. They might happen like this: `B -> A -> C` or `C -> B -> A`,
etc. Regardless of the order in which these transitions occur, tasks (associated
w/ a state) can only execute when that that state transition has occurred.

If some out of order state transitions have already occurred, eg: `B` has
happened, and `C` has happened, but not `A`, then when `A` happens, all the 
tasks for `A`, `B`, and `C` need to be executed.

## Solution in Kotlin using a state machine

The solution involves creating a state machine that can be used to keep track of
which transitions have already occurred. And also keep track of the expected
sequence of state transitions. Tasks that are schedule can also be attached to
this state machine, which only run when the appropriate state transitions have
occurred that allow these to be run.

The key is remembering the out of sequence state transitions that have occurred,
*w/out acting on them*. And when a state transition occurs, checking if all the
subsequent states have already been reached. In the code below this is achieved
using a high order function called `condition` which is run in a while loop (in
the `StateMachine.checkOverflow()` function).

Here's a listing of the code.

```kotlin
fun main(args: Array<String>) {
    println("Order enforcer to schedule ordered tasks".heading())
    val enforcer = StateMachine<Stage>(Stage.A, Stage.B, Stage.C)

    enforcer.runWhen(Stage.A, Runnable { println("A1") })
    enforcer.runWhen(Stage.B, Runnable { println("B1") })
    enforcer.runWhen(Stage.C, Runnable { println("C1") })
    enforcer.runWhen(Stage.C, Runnable { println("C2") })

    enforcer.transition(Stage.A)
    enforcer.transition(Stage.C)
    enforcer.transition(Stage.B)

    enforcer.shutdown()
}

enum class Stage {
    A, B, C
}

class StateMachine<State>(vararg states: State) {
    private val pattern: Array<out State> = states
    private val runnableMap = HashMap<State, ArrayList<Runnable>>()
    private val executorService = Executors.newSingleThreadExecutor()
    fun runWhen(state: State, runnable: Runnable) =
            runnableMap.computeIfAbsent(state) { ArrayList() }.add(runnable)

    private fun runAllFor(state: State) =
            runnableMap[state]?.forEach { executorService.submit(it) }

    fun shutdown() = executorService.shutdown()

    // Record state transition.
    private var cursor = -1
    private var overflowTransitions = HashSet<State>()
    fun transition(newState: State) {
        if (pattern[cursor + 1] == newState) {
            // Successfully transitioned to the next sequential state.
            cursor++
            runAllFor(newState)
            // See if sequential states exist in overflowTransitions,
            // and if so run tasks UNTIL that state.
            checkOverflow()
        } else {
            // Skip a state (non sequential).
            overflowTransitions.add(newState)
        }
    }

    private fun checkOverflow() {
        val condition: () -> Boolean = {
            if (cursor + 1 >= pattern.size) false
            else overflowTransitions.contains(pattern[cursor + 1])
        }
        while (condition()) {
            val nextState = pattern[cursor + 1]
            overflowTransitions.remove(nextState)
            runAllFor(nextState)
            cursor++
        }
    }

}
```

## Source code

The source code for this project is available here on
[github](https://github.com/nazmulidris/algorithms-in-kotlin/blob/master/src/main/kotlin/orderenforcer.kt).

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
