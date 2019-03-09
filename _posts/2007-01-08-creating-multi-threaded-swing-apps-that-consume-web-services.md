---
author: Nazmul Idris
date: 2007-01-08 15:00:02+00:00
excerpt: |
  If you've ever want to incorporate web services into your graphical 
  applications/applets/widgets written in Java, then there are some 
  threading issues that you have to be mindful of, and design around. This tutorial will guide 
  you though some of the important threading issues you have to keep in mind when building 
  such applications. The strategies outlined in this tutorial apply to accessing more than 
  just web services from Swing apps; it also applies to loading information from databases, 
  and performing any other kind of time consuming process that has to happen in the desktop 
  app and interact with it, but can't make the user interface unresponsive.
layout: post
title: "Creating multi-threaded Swing apps that consume web services"
categories:
- CC
---
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Overview](#overview)
- [Background](#background)
- [Strategy #1: Leverage Swing provided background threads (SwingWorker tasks) only](#strategy-1-leverage-swing-provided-background-threads-swingworker-tasks-only)
- [Strategy #2: Create your own threads to perform one-shot tasks, and coordinate with SwingWorker tasks](#strategy-2-create-your-own-threads-to-perform-one-shot-tasks-and-coordinate-with-swingworker-tasks)
- [Strategy #3: Create your own threads to perform recurring/long running tasks, and coordinate with SwingWorker tasks](#strategy-3-create-your-own-threads-to-perform-recurringlong-running-tasks-and-coordinate-with-swingworker-tasks)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Overview

If you've ever want to incorporate web services into your graphical applications/applets/widgets written in Java, then there are some threading issues that you have to be mindful of, and design around. This tutorial will guide you though some of the important threading issues you have to keep in mind when building such applications. The strategies outlined in this tutorial apply to accessing more than just web services from Swing apps; it also applies to loading information from databases, and performing any other kind of time consuming process that has to happen in the desktop app and interact with it, but can't make the user interface unresponsive.

## Background

For some more background information on Swing applications and threading, read this article - [Lesson: Concurrency in Swing](http://java.sun.com/docs/books/tutorial/uiswing/concurrency/). The Swing framework is essentially single threaded, as are most GUI toolkits. The main thread which updates the UI is called the Event Dispatch Thread (EDT). All the graphical components are created by this thread, all the action, event, etc. listeners run in this thread. So if your code performs a long running/time consuming or blocking task in the EDT, then the Swing UI will become frozen until your code is done. In order to prevent this situation, there are other threads that your tasks can use:

  * You can leverage some worker threads that Swing itself creates so that background tasks can be performed outside of the EDT for long running/time consuming/blocking operations that your task must perform, or

  * You can use threads that you explicitly create and then coordinate the output from these threads with the EDT, or

  * You can take a blended approach and do both of the things suggested above.

In this tutorial, I will cover all three strategies for making your Swing apps multithreaded, with code examples, and things to keep in mind when designing such systems.

## Strategy #1: Leverage Swing provided background threads (SwingWorker tasks) only

**Use case:**

<blockquote>Perform a one-shot task, started from the user interface, that only needs to update the UI with the final result of the task. Use a Swing threadpool executor to perform this task (not the EDT).</blockquote>

**Diagram:**

![]({{'assets/swing-apps-threaded-1.png' | relative_url}})

**Notes:**

  * You have to create a subclass of SwingWorker and launch it by calling [execute()](http://java.sun.com/javase/6/docs/api/javax/swing/SwingWorker.html#execute()); this will probably happen in an ActionListener in your Swing code. Calling execute() submits this SwingWorker task to the threadpool that Swing keeps for running background tasks. The execute() method returns immediately; so your calling thread (which may be the EDT itself) will continue.

    * Put the code for the background task in [T doInBackground()](http://java.sun.com/javase/6/docs/api/javax/swing/SwingWorker.html#doInBackground()). This is the code that performs the time consuming one-shot task. If exceptions are generated here, they can be caught by a call to [T get()](http://java.sun.com/javase/6/docs/api/javax/swing/SwingWorker.html#get()), so can the return value. Once this method completes (on the background thread), done() will be called **on the EDT**. The return value is of type "" - this is whatever class you decide to make the doInBackground() method return. "" is the result type returned by this SwingWorker's doInBackground and get methods. You can either implement this time consuming task in this method, or you can call an external web service, or other gateway or proxy class to request something.

    * The [done()](http://java.sun.com/javase/6/docs/api/javax/swing/SwingWorker.html#done()) method is called **on the EDT** when your doInBackground() method exits (by returning a value or throwing an exception). In the done() method, you can retrieve the thrown exception or return value by calling get(). In this method, you have to perform whatever GUI updates, or interactions that are necessary with the return value or exceptions generated by the call to get().

  * In this case the thread is started by calling execute() on the SwingWorker task itself. This submits the task to a threadpool of background threads that Swing manages, and the task will be executed in one of these threads.

  * Please make sure that the task is easily interruptible - there is no way to preemptively interrupt/stop a thread in Java, only cooperative cancellation is possible.

    * So, if you are performing any wait operations (waiting on a lock or monitor) make sure to catch the InterruptedException and cancel out of the task.

    * If you are performing blocking IO, make sure to catch IOException, to cancel out of it. The underlying stream that this task is blocking on has to be closed. Presumably, the object calling [cancel(true)](http://java.sun.com/javase/6/docs/api/javax/swing/SwingWorker.html#cancel(boolean)) on your SwingWorker task will also have to call [close()](http://java.sun.com/javase/6/docs/api/java/io/Closeable.html#close()) on the underlying Input/OutputStream in order for this to work. If you are unblocked due to to an IOException, you can always check for isCancelled() on the SwingWorker to see if it's been cancelled.

    * Also, make sure to check [isCancelled()](http://java.sun.com/javase/6/docs/api/javax/swing/SwingWorker.html#isCancelled()) on the SwingWorker thread to see if the task has been cancelled, to end your task.

    * If you don't know what to do with the InterruptedException (if one is thrown), and if you catch it, make sure to call [Thread.currentThread().interrupt()](http://java.sun.com/javase/6/docs/api/java/lang/Thread.html#interrupt()) to maintain the interrupted flag, so that the [executor](http://java.sun.com/docs/books/tutorial/essential/concurrency/executors.html) running this thread will know what to do with the interruption. More on preserving thread interrupted state (if you don't know what to do with the caught InterruptedException is explained [here](http://java.sun.com/docs/books/tutorial/essential/concurrency/interrupt.html)).

## Strategy #2: Create your own threads to perform one-shot tasks, and coordinate with SwingWorker tasks

**Use case:**

<blockquote>Perform a one-shot task, started from the user interface (or not), that only needs to update the UI with the final result of the task. Use your own executor to perform the task (not the EDT, or a Swing threadpool executor).</blockquote>

**Diagram:**

![]({{'assets/swing-apps-threaded-2.png' | relative_url}})

**Notes:**

  * The only differences between Strategy 1 and 2 are the following:

    * In Strategy 2, instead of performing the time consuming task in the doInBackground(), you simply delegate this responsibility to another task being executed in a different executor (which has it's own thread(s)). The reason for doing this is that you may have some multithreaded components/libraries/objects that you've created that are not tied to Swing. You may have a proxy class that acts as a gateway to an external web service. Instead of having to link this code to Swing's SwingWorker, you can use a generic Executor or Callable or Runnable to implement this. Then you have the task of tying this underlying threaded component to a SwingWorker, basically by creating an SwingWorker adapter for your underlying threaded component. All the processing happens in your underlying component, and the results are trasmitted to the SwingWorker task. So how do you pass a return value in case your underlying component implements Runnable? If the underlying component implements Callable, and you have a reference to a Future, it's easy - you can just call get() and wait in the doInBackground method of your adapter. However, if you don't have an reference to a Future, and you are dealing with Runnable implementation, then you will have pass the results back to doInBackground's thread via a BlockingQueue. So your SwingWorker adapter will have to get a reference to this BlockingQueue when it's created, and then in the doInBackground method, it will wait until it gets an object of type from this queue. Your underlying threaded component will have to pass the results of its computation via this BlockingQueue as well. This is a contract that **must **be honored by both your SwingWorker adapter class, and the underlying threaded component, in order for this strategy to work.

    * If your underlying component uses Callable, instead of Runnable, then there's no need to use a BlockingQueue. The doInBackground method of your SwingWorker adapter can simply call the get() method on the Future returned by the execution of the Callable. In this case, the blocking/waiting still happens in the doInBackground method, so that when everything is completed, done() is called on the EDT. In this scenario, Strategy 2 is very similar to Strategy 1, the only difference being that the doInBackground method doesn't really implement anything, it just uses a Future to get a return value back from your underlying component (which is treaded).

  * The similarities between Strategy 1 and 2 are the following:

    * You don't really use publish or process methods (which you will in Strategy 3).

    * The SwingWorker subclass is very similar, you have to declare a subclass in both cases like this: MySwingWorkerTask <T, Void> extends SwingWorker...

## Strategy #3: Create your own threads to perform recurring/long running tasks, and coordinate with SwingWorker tasks

**Use case:**

<blockquote>Perform a long running or recurring task, started from the user interface (or not), that needs to update the UI with intermediate/periodic results from the task. No final result has to be returned by the task (this is optional). Use your own executor to perform this long running/recurring task (not the EDT, or a Swing threadpool executor).</blockquote>

**Diagram:**

![]({{'assets/swing-apps-threaded-3.png' | relative_url}})

**Notes:**

  * The SwingWorker subclass is defined as SwingWorker<Void, V> : The reason the first parameter type is Void, is due to the fact that the final result returned by doInBackground is not important. However, unlike the previous strategies, the 2nd type parameters is - this is the type of the intermediate values that are passed from the background thread to the EDT via publish -> process.

  * Once this SwingWorker task is started, it continually blocks on the BlockingQueue object that the underlying threaded component uses to pass intermediate objects back to the SwingWorker adapter. The done() method isn't used, and neither is get(); instead the publish() and process() methods are used in this strategy. As soon as an object is available on the BlockingQueue, the SwingWorker task simply publishes that object. When objects are published, the EDT is notified of this, and it calls process() to get the objects that were published. Multiple calls to publish() are coalesed into one call to process() which is why the process method takes a List chunks object as a parameter.

  * The EDT actually runs the process method, so this is where you want to update your GUI and return.
