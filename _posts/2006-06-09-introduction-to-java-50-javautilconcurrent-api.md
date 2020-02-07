---
author: Nazmul Idris
date: 2006-06-09 19:02:16+00:00
excerpt: |
  Introduction to the Java5 Concurrency API. Java 50 introduces the
  java.util.concurrency API, which leverages hardware level constructs
  to allow Java programs to use lock-free, and wait-free thread-safety
  mechanisms, without having to use native code.
layout: post
title: "Introduction to Java 5 java.util.concurrent API"
categories:
  - CC
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [Why should I use this?](#why-should-i-use-this)
- [How did they do it?](#how-did-they-do-it)
- [How do I code using this new API (comparison with synchronized)?](#how-do-i-code-using-this-new-api-comparison-with-synchronized)
- [What is the volatile keyword?](#what-is-the-volatile-keyword)
- [Code example](#code-example)
  - [Notes on the code:](#notes-on-the-code)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

### Introduction

Java 50 introduces the java.util.concurrency API, which leverages hardware level
constructs to allow Java programs to use lock-free, and wait-free thread-safety
mechanisms, without having to use native code. The performance of these lock and
wait free algorithms used to implement thread-safety makes them more efficient
than using Object level monitors (using the synchronized keyword). In addition
to introducing lock and wait free concurrency algorithms, a slew of other
classes and interfaces have been introduced for locks and queues, and much more.

### Why should I use this?

If you are comfortable with using Object level monitors and synchronization
mechanisms of prior Java versions, then it makes sense to continue using those
techniques. However, there are some advantages of using the new atomic
concurrency APIs:

- There is considerable overhead to using Object level monitors and the
  synchronization mechanism. In contrast to this, using the atomic concurrency
  API has very little runtime overhead, when compared to the use of Object level
  monitors/synchronization.

- It's not easy to create really fine grained object-level synchronization or
  locking. Along with less overhead, it's possible to create really fine grained
  critical sections with the use of this atomic concurrency API.

- When lots of threads are running through your code that uses these atomic
  concurrency API, they will scale much better than code which uses Object level
  monitors/synchronization. Since, Java's synchronization mechanisms makes code
  wait, when there are lots of threads running through your critical sections, a
  substantial amount of CPU time is spent in managing the synchronization
  mechanism itself (waiting, notifying, etc). Since the new API uses hardware
  level constructs (atomic variables) and wait and lock free algorithms to
  implement thread-safety, a lot more of CPU time is spent "doing stuff" rather
  than in managing synchronization.

- These new APIs not only offer better throughput, but they also provide greater
  resistance to liveness problems such as deadlock and priority inversion.

There are some clear advantages of using the new Java 50 atomic concurrency API.
However there are a few caveats:

- Make sure that you understand the new API before using it. If you are an
  expert using the synchronized keyword, then don't just rewrite all your code
  before understanding the new stuff, just to the runtime advantages. It's
  better to have slower safer code, than faster less stable code :).

- Make sure that there's no requirement for backward compatibility with older
  VMs in the code that you generate. These new APIs only run on Java 50 and
  beyond.

If you are not bound by any of the constraints above, then the new APIs are a
joy to use! They are fast at runtime, and easy to program with. There is also a
tremendous amount of new and useful constructs to make your life easy when
solving concurrency problems in your code! It's a great addition to Java, and
makes it an even more useful platform!

### How did they do it?

I will just provide a simple overview of how the new concurrency APIs provide
thread-safety without using the Object-level synchronization mechanism of Java,
but for a more in-depth discussion of this topic, read the book:
[Java Concurrency in Practice](http://www.amazon.com/gp/product/0321349601/sr=8-1/qid=1152479794/ref=pd_bbs_1/102-1201016-2359362?ie=UTF8).

Modern CPUs support multiprocessing, and they provide provide support for
multiple processes to share memory, attached peripherals, etc. This
[CAS](https://en.wikipedia.org/wiki/Compare-and-swap) instruction allows
processes to update shared variables in a way that they can detect or prevent
concurrent access from other processes (running on the same processor, or on
multiple processors).

Essentially, CAS instructions allow an algorithm to execute a read-modify-write
sequence on a variable, without fear of another thread modifying the variable in
the meantime, because if another thread did modify the variable, the CAS would
detect it (and fail) and the algorithm could retry the operation. CAS operations
are very lightweight, so they don't have a big performance penalty. These
algorithms leverage the CAS hardware construct to provide wait, and lock free
synchronization functionality to your Java code.

A CAS operation includes three operands -- a memory location (V), the expected
old value (A), and a new value (B). The processor will atomically update the
location to the new value if the value that is there matches the expected old
value, otherwise it will do nothing. In either case, it returns the value that
was at that location prior to the CAS instruction. (Some flavors of CAS will
instead simply return whether or not the CAS succeeded, rather than fetching the
current value.) CAS effectively says "I think location V should have the value
A; if it does, put B in it, otherwise, don't change it but tell me what value is
there now."

The natural way to use CAS for synchronization is to read a value A from an
address V, perform a multi step computation to derive a new value B, and then
use CAS to change the value of V from A to B. The CAS succeeds if the value at V
has not been changed in the meantime.

Instructions like CAS allow an algorithm to execute a read-modify-write sequence
without fear of another thread modifying the variable in the meantime, because
if another thread did modify the variable, the CAS would detect it (and fail)
and the algorithm could retry the operation.

Also, for a quick overview of how wait and lock free algorithms are implemented,
you can find more information about the Compare and Swap (CAS) hardware
instruction and atomic variables
[here](https://en.wikipedia.org/wiki/Compare-and-swap).

### How do I code using this new API (comparison with synchronized)?

So how do you use this new API in practice. If you are familiar with Java's
synchronized keyword, and object level monitors, how do you leverage that
knowledge to quickly get up to speed with these new APIs? Fortunately, the Java
creators made the new APIs very natural for people who are familiar with the
existing object level monitor knowledge. Here are some rules to guide you in
writing code that uses the new API:

<table style="width:100%;text-align:left;" border="1" >

<tbody >

<tr >

<td colspan="2" >Rule 1: Instead of using <code>synchronized</code> keyword, use <code>Lock.lock
()</code> and <code>Lock.unlock()</code>

</td>

</tr>

<tr >

<td width="50%" style="font-weight:bold;vertical-align:top;" >Existing API

</td>

<td width="50%" style="font-weight:bold;vertical-align:top;" >New API

</td>

</tr>

<tr >

<td width="50%" style="vertical-align:top;" >
<pre>
Object monitorObject;
synchronized(monitorObject){
  <span style="color:#008000;">//critical section</span>
}
</pre>
</td>

<td width="50%" style="vertical-align:top;" >
<pre>
Lock lockObject;
<span style="color:#0000ff;">try</span>{
  lockObject.<span style="color:#0000ff;">lock</span>();
  <span style="color:#008000;">//critical section</span>
}
<span style="color:#0000ff;">finally</span>{
  lockObject.unlock();
}
</pre>
</td>

</tr>

</tbody></table>

Instead of using Java's object level monitors, via the synchronized keyword, you
have to now surround your critical sections of code (the parts that need
thread-safety) with calls to Lock.lock() and Lock.unlock(). So, instead of
relying on acquiring an object level monitor, the new API relies on acquiring a
lock to a java.util.concurrent.locks.Lock object.
[Lock](http://java.sun.com/j2se/1.5.0/docs/api/java/util/concurrent/locks/Lock.html)
is an interface, and a few implementations are provided - ReentrantLock,
ReentrantReadWriteLock.ReadLock, ReentrantReadWriteLock.WriteLock. In your code,
for every call you make to Lock.lock(), you must remember to make a
corresponding call to Lock.unlock(). This is why the call to Lock.unlock() is
made in the finally block of the try-catch block. The code that would go in your
critical section, protected by synchronized, now goes inside the
try-catch-finally block.

<table style="width:100%;text-align:left;" border="1" >

<tbody >

<tr >

<td colspan="2" >Rule 2: Instead of using `wait()` and `notify()` in the critical section use `await()` and `signal()` on condition variables

</td>

</tr>

<tr >

<td width="50%" style="font-weight:bold;vertical-align:top;" >Existing API

</td>

<td width="50%" style="font-weight:bold;vertical-align:top;" >New API

</td>

</tr>

<tr >

<td width="50%" style="vertical-align: top;" >
<pre>
<span style="color:#008000;">/////////////////////////////////</span>
<span style="color:#008000;">//Inside your critical section://</span>
<span style="color:#008000;">/////////////////////////////////</span>
<span style="color:#008000;">//evaluate your wait criteria</span>
boolean somecondition;
<span style="color:#0000ff;">while</span>(somecondition){
  wait();
  <span style="color:#008000;">//re-evaluate somecondition</span>
}
</pre>
</td>

<td width="50%" style="vertical-align: top;" >
<pre>
<span style="color:#008000;">//////////////////////////////////</span>
<span style="color:#008000;">//Outside your critical section://</span>
<span style="color:#008000;">//////////////////////////////////</span>
Condition conditionVariable =
  lockObject.newCondition();
<span style="color:#008000;">/////////////////////////////////</span>
<span style="color:#008000;">//Inside your critical section://</span>
<span style="color:#008000;">/////////////////////////////////</span>
<span style="color:#008000;">//evaluate your wait criteria</span>
boolean somecondition;
<span style="color:#0000ff;">while</span>(somecondition){
  conditionVariable.await();
  <span style="color:#008000;">//re-evaluate somecondition</span>
}
</pre>
</td>

</tr>

<tr >

<td width="50%" style="vertical-align: top;">
<pre>
<span style="color:#008000;">////////////////////////////////////</span>
<span style="color:#008000;">//Inside of your critical section://</span>
<span style="color:#008000;">////////////////////////////////////</span>
<span style="color:#008000;">//evaluate your notify criteria</span>
boolean someothercondition;
<span style="color:#0000ff;">if</span>(someothercondition) {
  notify();
}
</pre>
</td>

<td width="50%" style="vertical-align: top;">
<pre>
<span style="color:#008000;">/////////////////////////////////</span>
<span style="color:#008000;">//Inside your critical section://</span>
<span style="color:#008000;">/////////////////////////////////</span>
<span style="color:#008000;">//evaluate your signal criteria</span>
boolean someothercondition;
<span style="color:#0000ff;">if</span>(someothercondition) {
  conditionVariable.signal();
}
</pre>
</td>

</tr>

</tbody></table>

In sections of your code which require use of wait() and notify()/notifyAll(),
you have to use condition variables. Using object level monitors, threads are
able to wait() in queues, until they are signaled by notify()/notifyAll(). Since
you are no longer using object level monitors, you have to use a condition
variable (of type
[java.util.concurrent.locks.Condition](http://java.sun.com/j2se/1.5.0/docs/api/java/util/concurrent/locks/Condition.html)).
Condition is an interface, and before you can use a condition variable, you have
to request one from the Lock object that you've acquired to enter the critical
section. You can generate as many condition variables as you wish from a Lock
object. Once you have the desired condition variable, you can call await() on
it, and get the same functionality as Object.wait(). Typically, you would
evaluate a condition in a while loop, and depending on the outcome of this
evaluation, you would wait(). Similarly, with Condition.await(), you have to
evaluate this condition in a while loop, and if it's necessary to wait, then you
can call Condition.await(). Similarly, if you want to call notify()/notifyAll()
on a thread that's wait()ing on a monitor, you can use signal()/signalAll()
instead.

If you want to interrupt() your threads to terminate them gracefully, the
behavior is the same as it was before. The concurrency API doesn't affect this
behavior of Java threads - you can't really preempt the execution of a thread,
you can only cooperatively signal it that things are interrupted (and it an
InterruptedException is thrown, that can be caught by the thread that's
waiting). The only issue with using interrupt() to stop threads is when threads
are waiting on blocking I/O. In these cases, you have to close the Input or
OutputStream that the thread is blocking in, and catch the IOException and use
it to terminate the thread that was blocked in an IO operation.

The code example provided below will use the concurrency API to demonstrate the
classic
[Producer-Consumer synchronization problem](http://cs.gmu.edu/cne/modules/ipc/aqua/producer.html),
using Rule 1 and 2, and it will show you how terminate threads gracefully using
interrupt().

### What is the volatile keyword?

In the Java VM, when multiple threads are running through sections of your code,
each one of these threads may not have the same copy of the value of a variable
in this critical section. There's the value of the variable that's in "main
memory" vs. the "thread copy" of the value of the same variable. To avoid this
kind of confusion, when you have multiple threads running through a section of
your code, and you want them to have the same value for a particular variable,
you must declare that variable as "volatile". In the code example below, a
volatile boolean variable is used to act as a flag to shutdown threads. For more
details on the volatile keyword, "main memory" and "thread copy of a variable",
please visit this
[link](http://www.javaperformancetuning.com/news/qotm030.shtml).

### Code example

The ReentrantLockTest.java class file provided below illustrates the use of the
new concurrency API to implement a bounded buffer for use by multiple producer
and consumer threads. Please note that classes are provided in the new
concurrency API which implement this functionality already, but the purpose of
the tutorial is to show what you can do with Locks and Condition variables.
Parts 2 and 3 of the tutorial will show more examples of classes that are
already provided for your convenience, to make you really productive when
writing code to tackle common concurrency issues.

The ReentrantLockTest class creates a set of Producer threads and Consumer
threads. The Producer threads add objects to a bounded buffer, that Consumer
threads consume. Since Producer threads produce at a different rate than
Consumer threads, and since there are different numbers of each, threads have to
wait before they can put objects in the bounded buffer, or remove objects from
the bounded buffer. Also, to illustrate interrupt(), the ReentrantLockTest class
tries to terminate all the threads after it runs them for a while (all these
parameters are configurable in the code).

Here's a listing of `ReentrantLockTest.java`:

```java
package concurrency;
import java.util.ArrayList;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.ReentrantLock;
/*
 * ReentrantLockTest uses non blocking, wait free ReentrantLock instead
 * of the synchronized keyword.
 *
 * Use the lock to implement a bounded buffer that 2 types of threads
 * work on:
 * 1. ones that write to it
 * 2. ones that read from it
 *
 * You can tweak all kinds of parameters in this program to determine
 * how many threads run, and how quickly they process things, etc.
 * You can also see how to cleanly shut these threads down, and you
 * can see parts of the JDK that do not work - ThreadGroup.
 *
 * Originally, I didn't use the volatile keyword on variables that
 * were going to be shared amongst different threads - this is a big
 * NO NO. Here's why -
 * http://www.javaperformancetuning.com/news/qotm030.shtml
 *
 * Also, for threads that just go on executing for a long time, in
 * addition to checking for a shutdown flag, it's necessary to check
 * if the thread was interrupted. If the thread is not sleeping,
 * or waiting, then there's no way for it to know that it
 * was interrupted, except for it to check
 * Thread.currentThread.isInterrupted() method. The code has been
 * updated to reflect this. The only real use for interruption in
 * Java is to signal a thread to exit. When you are doing blocking
 * IO, you have to close the socket, which throws an IOException
 * and breaks the blocking operation, but in this IOException
 * handler you then have to check for the shutdown flag.
 *
 * It's complicated 😃. There is no thread preemption in java.
 * Only cooperation. So in order to effectively shut down threads
 * you have to do the following:
 * 1.    use a volatile shutdown Boolean flag
 * 2.    make sure to check isInterrupted() to ensure that
 *       the thread wasn't interrupted while it wasn't waiting or
 *       sleeping
 * 3.    make sure to use InputStream.close() in order to preempt
 *       blocking IO operations, and then check the status
 *       of the shutdown flag or the isInterrupted() status.
 *
 * By the way, if you call interrupted() on a Thread, it CLEARS
 * the interrupt flag, and the thread goes about it's business
 * merrily. This is a NO NO as well. And you wonder why the hell
 * this method even exists, and why it's called interrupted()
 * and not clearInterruptedFlag()?!?!?!?
 *
 * @author Nazmul Idris
 * @since Jun 22, 2006, 1:53:09 PM
 */
public class ReentrantLockTest {
  //
  // shared data members
  //
  int maxSize = 10;
  ArrayList boundedBuffer = new ArrayList( maxSize );
  /*
    size:   1  2  3  4  5
    array: [ ][ ][ ][ ][ ]
    index:  0  1  2  3  4
  */
  int currentIndex = -1;
  ReentrantLock lock = new ReentrantLock(false);
  Condition waiting_on_full_buffer = lock.newCondition(),
            waiting_on_empty_buffer = lock.newCondition();
  /*
    http://www.javaperformancetuning.com/news/qotm030.shtml
    it's important that this boolean be volatile, as it's used by
    many threads
  */
  volatile boolean shutdown = false;
  int totalInserts = 0, totalDeletes = 0;
  int producerSleepTime = 1;
  int consumerSleepTime = 2;
  int mainDriverWaitTime = 100;
  int totalConsumerThreads = 4, totalProduerThreads = 4;
  int criticalSectionDelay = 0;
  //
  // methods
  //
  /**
   * Constructor that starts the ReentrantLockTest program off...
   *
   */
  public ReentrantLockTest () {
    System.out.println("::::::::::::::::::::::::::::::::");
    System.out.println(":: Starting ReentrantLockTest ::");
    System.out.println("::::::::::::::::::::::::::::::::");
    ArrayList threads = new ArrayList();
    ThreadGroup tg = new ThreadGroup("ReentrantLockTest Thread Group");
    //create the producer thread(s)
    for (int i = 1; i<=totalConsumerThreads; i++){
      threads.add( new Thread( tg ,  new Producer() ,
                   "producer_thread_"+i) );
    }
    //create the consumer thread(s)
    for (int i = 1; i<=totalProduerThreads; i++){
      threads.add( new Thread( tg , new Consumer() ,
                   "consumer_thread_"+i) );
    }
    //start the threads
    for (Thread t : threads) t.start();
    //wait for 1 minute and then shutdown
    try {
      Thread.currentThread().sleep(mainDriverWaitTime);
    } catch (InterruptedException e) {
      e.printStackTrace();
    }
    finally{
      shutdown = true;
      System.out.println(
              ":: ReentrantLockTest - setting shutdown to false ::");
    }
    System.out.println(
            ":: ReentrantLockTest - signalling interrupt and waiting "
            + "for "+tg.activeCount()+" threads to die ::");
    for (Thread t : threads){
      System.out.println(":: Interrupting "+t.getName()+" ::");
      try {
        t.interrupt();
      }
      catch (Exception e) {
        e.printStackTrace();
      }
    }
    for (Thread t : threads){
      try {
        StringBuilder sb = new StringBuilder( t.getName() );
        System.out.println(":: Waiting for "+sb+" to die ::");
        t.join();
        System.out.println(":: "+sb+" is dead ::" );
      }
      catch (InterruptedException e) {
        e.printStackTrace();
      }
    }
    System.out.println(":::::::::::::::::::::::::::::");
    System.out.println(":: ReentrantLockTest Ended ::");
    System.out.println(":::::::::::::::::::::::::::::");
  }
  //ProducerTask class
  public class Producer implements Runnable{
    public void run() {
      System.out.println(":: "+Thread.currentThread().getName()+
            " has been started ::");
      //its important to check to see if the thread was interrupted
      //while sleeping... if it was then its the same as a shutdown
      main_while_loop: while( shutdown == false &&
                              !Thread.currentThread().isInterrupted() ){
        //acquire the lock and then put something in the buffer
        try{
          lock.lock();
          System.out.println(":: "+Thread.currentThread().getName()+
                " acquired the lock ::");
          //
          //check to see if the buffer is full - wait if it is.
          //
          while(currentIndex == maxSize-1){
              System.out.println(":: buffer is full - "+
                  Thread.currentThread().getName()+
                  " is going to wait ::");
              waiting_on_full_buffer.await();
          }//while condition waiting_on_full_buffer
          //arbitrary delay - while holding the lock
          Thread.currentThread().sleep(criticalSectionDelay);
          //
          //buffer is not full - add something to the array
          //
          boundedBuffer.add( Integer.toString(++totalInserts) );
          currentIndex++;
          System.out.println(
                  ":: "+Thread.currentThread().getName()+
                  " just added item, totalInserts = "+totalInserts+" ::");
          //
          //signal threads who may be waiting due to the buffer
          //being empty (it no longer is as I just added something)
          //
          waiting_on_empty_buffer.signal();
          System.out.println(":: "+Thread.currentThread().getName()+
                " signalling waiting_on_empty_buffer ::");
        }
        catch (InterruptedException e){
          e.printStackTrace();
          System.out.println(":: "+Thread.currentThread().getName()+
                " was interrupted ::");
          //continue main_while_loop;
          Thread.currentThread().interrupt();//restores the interrupt
                                             // flag of this thread
                                             // (in case shutdown is
                                             // not set, this will
                                             // cause the main loop
                                             // to stop)
          break main_while_loop;
        }
        finally{
          lock.unlock();
          System.out.println(":: "+Thread.currentThread().getName()+
                " released the lock ::");
        }
        //dont need the lock to sleep, so this code is outside
        //critical section above sleep before producing again...
        try {
          System.out.println(":: "+Thread.currentThread().getName()+
                " is sleeping for "+producerSleepTime+" ms ::");
          Thread.currentThread().sleep(producerSleepTime);
        } catch (InterruptedException e) {
          e.printStackTrace();
          System.out.println(":: "+Thread.currentThread().getName()+
                " was interrupted ::");
          //continue main_while_loop;
          Thread.currentThread().interrupt();//restores the interrupt
                                             // flag of this thread
                                             // (in case shutdown is
                                             // not set, this will
                                             // cause the main loop
                                             // to stop)
          break main_while_loop;
        }
      }//end while: main_while_loop
      System.out.println(":: "+Thread.currentThread().getName()+
            " has been shutdown ::");
    }
  }
  //ConsumerTask class
  public class Consumer implements Runnable{
    public void run() {
      System.out.println(":: "+Thread.currentThread().getName()+
        " has been started ::");
      //its important to check to see if the thread was
      //interrupted while sleeping... if it was then its
      //the same as a shutdown
      main_while_loop: while( shutdown == false &&
                              !Thread.currentThread().isInterrupted() ){
        //acquire the lock and then gets omething from the buffer
        try {
          lock.lock();
          System.out.println(":: "+Thread.currentThread().getName()+
                " acquired the lock ::");
          //arbitrary delay - while holding the lock
          Thread.currentThread().sleep(criticalSectionDelay);
          //
          //check to see if the buffer is empty - wait if it is.
          //
          while(currentIndex == -1){
            System.out.println(":: buffer is empty - "+
                Thread.currentThread().getName()+" is going to wait ::");
            waiting_on_empty_buffer.await();
          }//while condition waiting_on_empty_buffer
          //
          //buffer is not empty - consume something from the array
          //
          boundedBuffer.remove(currentIndex);
          currentIndex--;
          totalDeletes++;
          System.out.println(
              ":: "+Thread.currentThread().getName()+
              " just removed item, totalDeletes = "+totalDeletes+" ::");
          //
          //signal threads that may have been waiting on the
          //buffer being full (it no longer is as I just
          //removed something)
          //
          waiting_on_full_buffer.signal();
          System.out.println(":: "+Thread.currentThread().getName()+
                " signalling waiting_on_full_buffer ::");
        }
        catch (InterruptedException e) {
          e.printStackTrace();
          System.out.println(":: "+Thread.currentThread().getName()+
                " was interrupted ::");
          //continue main_while_loop;
          Thread.currentThread().interrupt();//restores the interrupt
                                             // flag of this thread
                                             // (in case shutdown is
                                             // not set, this will
                                             // cause the main loop
                                             // to stop)
          break main_while_loop;
        }
        finally {
          lock.unlock();
          System.out.println(":: "+Thread.currentThread().getName()+
                " released the lock ::");
        }
        //don't need the lock to sleep, so this code is outside
        //critical section above sleep before consuming again...
        try {
          System.out.println(":: "+Thread.currentThread().getName()+
                " is sleeping for "+consumerSleepTime+" ms ::");
          Thread.currentThread().sleep(consumerSleepTime);
        } catch (InterruptedException e) {
          e.printStackTrace();
          System.out.println(":: "+Thread.currentThread().getName()+
                " was interrupted ::");
          //continue main_while_loop;
          Thread.currentThread().interrupt();//restores the interrupt
                                             // flag of this thread
                                             // (in case shutdown is
                                             // not set, this will cause
                                             // the main loop to stop)
          break main_while_loop;
        }
      }//end while: main_while_loop
      System.out.println(":: "+Thread.currentThread().getName()+
            " has been shutdown ::");
    }//end run
  }
}//end class
```

The following class `Test.java` runs the class above.

```java
/**
 * Simple driver class to run examples.
 *
 * @author Nazmul Idris
 * @since Jun 22, 2006, 1:44:20 PM
 */
public class Test {
  public static void main(String[] args) {
    new ReentrantLockTest();
  }
}
```

#### Notes on the code:

ReentrantLockTest constructor:

1. The constructor of this class is responsible for creating many consumer and
   producer threads and starting them off. It's also responsible for terminating
   these threads gracefully after a certain period of time. The interesting
   section of code is where the threads are shutdown by setting the volatile
   boolean variable "shutdown" to true. This volatile boolean variable is shared
   amongst all the treads that are running, and they check to see if this flag
   is set to true in order to terminate gracefully (and cooperatively, not
   preemptively). However, at the time when the shutdown flag is set to true,
   some of the producer or consumer threads may be waiting or sleeping, and they
   will not check the status of the shutdown flag. Since you can't preempt
   threads in Java, the interrupt() method is very useful. The main thread (of
   the ReentrantLockTest) calls interrupt() on every single consumer and
   producer thread. If any of these threads are wait()ing or sleep()ing, then
   they are woken up, and the InterruptedException is thrown, which they have to
   catch. In the catch() block for InterruptedException, these threads check to
   see if the shutdown flag is set to true.

2. Another thing to note is the use of the join() method. Once the main thread
   interrupt()s all the producer and consumer threads, it then join()s each of
   those threads to ensure that all those threads die before the main thread
   moves forwards past the join() method. This is important to do if you want to
   wait until all your threads have cleanly terminated before proceeding with
   the remainder of the shutdown sequence.

ProducerTask, ConsumerTask inner classes: (the two condition variables are
shared between ProducerTask and ConsumerTask threads, since there is only one
shared buffer)

1. Condition variable `waiting_on_full_buffer`: The ProducerTask thread creates
   objects that it puts in a shared bounded buffer. So, when this bounded buffer
   is full, it has to wait until another thread removes an object from the
   shared buffer, before it can produce again. This condition variable is used
   to wait on this "buffer is full" condition. The await() method is used on the
   waiting_on_full_buffer when the buffer is full. There is some complementary
   code in the ConsumerTask inner class that calls signal() on this condition
   variable, when a consumer thread has removed an object from the shared
   bounded buffer (and the producer can create another object to put in this
   bounded buffer).

2. Condition variable `waiting_on_empty_buffer`: The ConsumerTask thread removes
   objects from the shared bounded buffer. So, when this bounded buffer is
   empty, it has to wait until another thread puts an object into the shared
   buffer, before it can consume again. This condition variable is used to wait
   on this "buffer is empty" condition. The await() method is used on the
   waiting_on_empty_buffer when the buffer is empty. There is some complementary
   code in the ProducerTask inner class that calls signal() on this condition
   variable, when a producer thread has added an object to the shared bounded
   buffer (and the consumer can remove another object from the bounded buffer).
