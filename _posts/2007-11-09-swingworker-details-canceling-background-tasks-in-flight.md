---
author: Nazmul Idris
date: 2007-11-09 18:29:38+00:00
excerpt: |
  This tutorial outlines some of the interesting behaviors exhibited by SwingWorker
  when running background tasks are canceled in flight
layout: post
title: "SwingWorker details - canceling background tasks in flight"
categories:
  - UXE
  - CC
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [The setup](#the-setup)
- [The tale of two threads](#the-tale-of-two-threads)
- [Closing thoughts](#closing-thoughts)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

If you use the SwingWorker class to run background tasks that don't freeze up the EDT (Event Dispatch Thread) in your
Swing apps, this may be of interest. What happens when you cancel a long running operation that's running the
background? For eg, a user might generate an event that causes a SwingWorker to be created that starts running some code
in the background. What happens when the user wants to cancel this long running background operation? This is what we
will delve into in this tutorial and get the answer to this question.

## The setup

Let's say you have some code that you want to run in the background (on a thread that is not the EDT). So this is what
you would do. You would subclass SwingWorker and put your code in the doInBackground() method. Here's an example:

```java
SwingWorker<String, Void> myWorker = new SwingWorker<String, Void>() {
   protected String doInBackground() throws Exception {
     while (!isCancelled()) {
       //run some code in the background...
     }
     return "something";
   }
   @Override protected void done() {
     try {
      String value = get();
    }
    catch (InterruptedException e) {}
    catch (ExecutionException e) {}
    catch (CancellationException e) {}
  }
};
```

1. The first type parameter for our SwingWorker subclass is String, and this defines the type of object that is returned
   when done() is called... which happens when the background thread completes it's execution.

1. The second parameter is just Void, since I'm not going to use this SwingWorker to post intermediate results to the
   EDT for processing (while the background thread is running).

1. Note the use of isCancelled() in the while loop... we will cover this in more detail in the sections that follow. The
   results of this background processing are retrieved on the EDT in the done() method - also note the exceptions, we
   will cover this in the next sections as well.

[Click here](http://java.sun.com/javase/6/docs/api/javax/swing/SwingWorker.html) for more details on this. Sun's
[Java Tutorial](http://java.sun.com/docs/books/tutorial/uiswing/misc/threads.html) has more information on SwingWorker
if you need more background information.

To run this snippet, all you have to do is:

```java
myWorker.execute()
```

To cancel it, all you have to do is:

```java
myWorker.cancel()
```

## The tale of two threads

When you call execute() on myWorker, from the EDT or whatever thread the execute() call is running in, two things
happen:

1. a thread is created that runs the SwingWorker (let's call this Thread1).

1. another thread is created by this SwingWorker instance which runs your code in the background (let's call this
   Thread2).

Let's say that you want to cancel the background task because it is taking too long. You would then call cancel() on
myWorker. When you call cancel() on the SwingWorker instance myWorker, the following things happen concurrently:

1. CancellationException gets raised on Thread1 (the SwingWorker thread). So the SwingWorker thread itself jumps out of
   waiting for doInBackground() method to end, and goes straight into done(). When the get() method is called, this
   causes a CancellationException to be thrown on the SwingWorker thread itself, and you can catch this in the
   CancellationException handler. So the SwingWorker thread ends its lifecyle at this point.

1. InterruptedException gets raised on Thread 2 (the thread that's actually running your code in the background). If
   your code is not interruptible, or if you catch the InterruptedException and just keep going, then this thread will
   not die, and will continue doing it's background processing! This is why it's necessary to check to see if
   isCancelled() is true. This is the only way (outside of responding to an InterruptedException) that can cause the
   background thread to stop running your code. Also, when your background task completes execution and it returns the
   String, nothing will happen, since the SwingWorker (Thread1) that was supposed to respond to this (in it's done()
   method) is already dead. If you use call sleep() or wait(), then these methods will respond to an
   InterruptedException being raised, otherwise, the only way to tell is by checking isCancelled(). So it's pretty easy,
   if you're not careful, for the underlying thread executing your background code and the SwingWorker thread itself to
   get out of "sync". Also, if you have code that's doing some network IO, you have to use an InputStream or
   OutputStream that can check the isCancelled() method to break the IO operation. If you can't do this, then you can
   try closing the underlying IO streams and causing an IOException to occur when isCancelled() is detected.

## Closing thoughts

In your Swing apps that use SwingWorker to perform lengthy background tasks, it's necessary to keep in mind that just
because you called cancel() on the SwingWorker doing your task in the background that it's been "canceled". Java does
[not allow you to stop() a Thread](https://docs.oracle.com/javase/1.5.0/docs/guide/misc/threadPrimitiveDeprecation.html),
even though
[Java supports preemptive mutithreading](https://medium.com/traveloka-engineering/cooperative-vs-preemptive-a-quest-to-maximize-concurrency-power-3b10c5a920fe).
So it's your onus to check the isCancelled() method in your doInBackground() code, and do the proper exception handling
in the done() method of the SwingWoker to make sure that you don't have a thread leak. Also, it's important to process
results from your background operation in the done() method - this will ensure that the 2 threads won't go out of
"sync". Since the SwingWorker thread can be canceled without the underlying execution thread knowing, it's important to
perform any changes to your system in the done() method - if the SwingWorker get's canceled, then these changes won't
show up in your system.
