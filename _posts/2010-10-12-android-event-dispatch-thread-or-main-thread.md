---
author: Nazmul Idris
date: 2010-10-12 00:00:00-08:00
excerpt: |
  Android applications run in a native Linux process, in the underlying Linux
  OS. This process houses activities (screens), widgets, and services (non visual
  long running application parts). When working with Android apps, it is important
  to remember to keep long running code running in threads that are not tied to the
  main thread or event dispatch thread, in order to get an “application not responding”
  error. A common mistake that is made is long running tasks are performed in this
  EDT/main thread, and this leads to lots of application failures.
layout: post
title: "Android Event Dispatch Thread or Main Thread"
categories:
  - Android
  - FE
  - CC
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [What is the EDT or main thread?](#what-is-the-edt-or-main-thread)
- [Strategies](#strategies)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

Android applications run in a native Linux process, in the underlying Linux OS. This process houses activities
(screens), widgets, and services (non visual long running application parts). When working with Android apps, it is
important to remember to keep long running code running in threads that are not tied to the main thread or event
dispatch thread, in order to get an “application not responding” error. A common mistake that is made is long running
tasks are performed in this EDT/main thread, and this leads to lots of application failures.

## What is the EDT or main thread?

![]({{'assets/edt-1.png' | relative_url}})

This picture outlines what the role of the EDT or main thread is (I will refer to it as the EDT from now on). All UI
operations are performed in a single thread in the native Linux process. This is pretty much the way all graphics on
desktop and mobile platforms are performed. This single thread of execution is called the EDT, and it is spawned by the
OS when you have a graphical app (as opposed to a command line app or an entirely non visual one). All UI operations,
paints, updates, etc. are done on this thread, and it is important to keep long running, high latency tasks off of this
thread of execution. Eg, it is a bad idea to resolve a URL and load content over HTTP in this thread.

In order to combat the single threaded nature of the EDT, a simple event dispatching model is used. In Android, this is
implemented using [`Handler` and `Looper`](http://developer.android.com/reference/android/os/Looper.html) classes. It
goes something like this, if you want the EDT to do something, create a
[`Runnable`](http://developer.android.com/reference/java/lang/Runnable.html) and inject it into the EDT’s task queue.
The EDT will then process this `Runnable`, when it gets around to it. You can’t mess with this queue, except to “post
Runnables” to it. Alternatively, if you have a long running process that must do something in a non-EDT or background
thread (BGT), you have to post a Runnable that then injects the results of this long running background task to the EDT
at some point. This is encapsulated by the Android
[`AsyncTask`](http://developer.android.com/reference/android/os/AsyncTask.html) class.

## Strategies

Based on this event dispatch model, there are a few patterns that emerge, that are reusable across a large variety of
applications.

1. Perform long running tasks in a BGT. This BGT can be created by you calling `new Thread()`, or more preferably, by
   using the [`Executor`](http://download.oracle.com/javase/1.5.0/docs/api/java/util/concurrent/Executor.html)
   framework. You will find a large variety of executors to meet the needs of many different kinds of requirements. Eg,
   you can replace a Timer with a scheduled executor. You can use a single thread executor instead of spawning new
   threads all the time, or you can use a thread pool executor for that. There are a lot of options at your disposal,
   and you should be able to find something that meets your requirements.

2. Once long running tasks are completed in the BGT, post those results to the EDT in a `Runnable`. Sometimes, your long
   running tasks will not require any UI updates, other times, they will. In those cases, where UI updates are needed,
   you have to create a new Runnable closure/functor/anon inner class implementation that delivers the results of the
   computation to the UI (by updating a model, or creating some widget, etc). In order to this, you will need a
   `Context`, and it’s `Handler` to call
   [`post()`](<http://developer.android.com/reference/android/os/Handler.html#post(java.lang.Runnable)>) or
   [`postDelayed()`](<https://developer.android.com/reference/android/os/Handler#postDelayed(java.lang.Runnable,%20long)>)
   on.

3. Inside of your UI code, there are times when you need some UI operation to happen at a later time. In these cases you
   can `post` or `postDelayed` `Runnables` on a `Context’s` `Handler` just like in the previous case. There are various
   reasons for doing this, eg: showing a popup at a later time, or performing an animation, or even “chunking” long
   running UI operations into smaller chunks.
