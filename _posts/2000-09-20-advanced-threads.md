---
author: Nazmul Idris
date: 2000-09-20 18:32:56+00:00
excerpt: |
   This tutorial is devoted to showing you advanced techniques of using threads to
   perform event driven tasks, without using polling, and usually with the use of
   queues. Along with techniques of managing life cycles of server objects (that are 
   multithreaded) and runtime activation and deactivation of these objects.
layout: post
title: "Advanced Threads"
categories:
- CC
- Server
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Uses for advanced threads](#uses-for-advanced-threads)
- [Example problem](#example-problem)
  - [Producers, consumers and queues](#producers-consumers-and-queues)
  - [Where not to use queues](#where-not-to-use-queues)
- [Solution (design)](#solution-design)
  - [Monitors](#monitors)
  - [Monitors and internal queues](#monitors-and-internal-queues)
  - [wait()](#wait)
  - [notify() and notifyAll()](#notify-and-notifyall)
  - [interrupt(), InterruptedException and other thread exceptions](#interrupt-interruptedexception-and-other-thread-exceptions)
- [Thread management strategies for server-side component threads](#thread-management-strategies-for-server-side-component-threads)
  - [ServiceIF](#serviceif)
  - [ServiceIF implementation in a server framework](#serviceif-implementation-in-a-server-framework)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Uses for advanced threads

There are many uses for threads. Sometimes, you need a thread to spawn a new task, other times you have make sure that your code will not break if many threads are trampling through it, and yet in other times, you need threads to listen to events as they become available and notify some other object. These are just a few ways of using threads in your programs.

This tutorial is devoted to showing you:

  1. advanced techniques of using threads to perform event driven tasks, without using polling, and usually with the use of queues.

  2. techniques of managing life cycles of server objects (that are multithreaded) and runtime activation and deactivation of these objects.

In the real world, there are many practical applications where polling is unacceptable. For example, in event driven GUIs (like Swing, AWT, Win32, Motif, etc.) a threaded architecture is necessary because polling would yield unacceptable performance. In networked programming, there are many instances where threads have to wait for data coming from streams (over sockets), and it would be too resource intensive to poll these streams to see if they have new data. Now, these are all very low level software components, like a GUI toolkit, and networking toolkit, and most programmers won't have to write these toolkits from scratch. However, it is sometimes necessary to create these toolkits from scratch, for experience or for deployment, and the insights and skills that you take away from doing such tasks will only make you a more accomplished programmer, and take you closer to a system architect type role, rather than just being a developer. These skills are also necessary if want to create a server architecture or framework of your own.

## Example problem

Lets say that you have an object that has to perform a task when an event occurs, and this object does not know when this event will occur. In such a case you can use threads (without having a thread poll on this event having occurred all the time). The classical example is that of a producer and consumer that share some kind of buffer or queue.

In the real world, this scenario might pop up if you have to create a server framework, that has to integrate your objects with some kind of pre-existing protocol based server. For example, if you have to use the services of some legacy server that "speaks" a protocol, then you will have to use Sockets and queues to "talk" with the server, and "translate" what it says to your "object-speak".

### Producers, consumers and queues

A producer object is one that produces data (objects), a consumer object uses this data (objects), and a queue is an object that is used to transmit this data. In other words, a queue is a thread safe container of (data) objects that is directly shared between the producer object and the consumer object. The producer object generates data objects and places them in the queue, and the consumer object gets this data (from the queue) and does some work with it. The producer and consumer objects also have different threads running through them, ie, the consumer object has its own thread, and the producer object has its own different thread. The queue object does not have a thread running through it, as it is merely a shared object, rather than one that is "alive".

This queue (or buffer) could be an ArrayList or Vector. Now, the whole idea is that the consumer thread is always consuming, but, it can't consume if the queue is empty. The producer creates objects and puts them in the queue at anytime (ie, the consumer has no idea when the producer will create objects to put in the queue). You can think of the producer as something that generates (or creates) an event, and a consumer as an event dispatcher for all events. The queue where these events are placed (by the producer) is like an event queue. The dispatcher has to route the event to the appropriate handler in order for the handler to do some meaningful task, but the handler is probably some other object. So the the consumer thread usually gets data objects out of the queue, and then runs through some event handler object. The producer thread is concerned with generating data objects (at anytime) and putting them in the shared queue.

If the problem you are trying to solve fits this profile, then you can use threads to avoid polling on the (event) queue to figure out if something just "happened" or if some data objects "just arrived". An example of this is where you need data from a socket to fire an event into your system. You don't know when data is going to be sent from the server, but as soon as it is sent, your system will have to be notified of this (the data from the server can be wrapped in an event object). Another example of this is where you need to write data asynchronously, without having to wait for the write to be completed; you just want to issue a write and pass the data without waiting for the potentially lengthy write operation to complete (for example you could be sending data over a socket, or writing something to a database, or saving a file in the background). In this case, you simply put the data that needs to be written into the right queue object, and another thread will take care of actually performing the write operation. Yet another example of this is a GUI toolkit, where a user input event can occur at anytime, and the GUI has to route the event to its correct event handler.

### Where not to use queues

So this producer, consumer and queue can be used for a variety of tasks, that include, asynchronous reading, writing as well event dispatching and generation. The addition of the queue to disconnect the producer from the consumer is a very powerful thing; it allows these tasks to happen asynchronously. You could even persist the queue to disk and have a fault tolerant queue that resumes operation if your program crashes. However, if you need to block on certain operations (ie, you need synchronous messaging) then there is no need for the queue as it adds unnecessary overhead).

You can also have many different kinds of queues, depending on your needs you can have grow-able ones or fixed length ones.

## Solution (design)

Java has the synchronized keyword to provide mutually exclusive access to a critical section (code that is in a synchronized code block) of code. The JVM performs this magic by using object level monitors.

### Monitors

There are two ways of providing mutually exclusive access to code sections, semaphores and [Hoare's monitors](https://en.wikipedia.org/wiki/Monitor_(synchronization)). The Java Virtual Machine (JVM) uses object level monitors to provide a mutex mechanism in Java, however you can write your own semaphore classes if you wish. This tutorial deals with object level monitors exclusively.

Each object in the VM has a monitor associated with it, and when a thread enters a critical section it has to acquire a lock to this monitor. Once the thread finishes executing the code in the critical section, it releases the lock to this monitor. Now, once the lock for the monitor has been acquired, it can't be acquired by any other thread that is trying to go through the same critical section as the first thread that "got in". Now, the second, third, and all threads after the first are suspended until the first one gets done. This is the essence of mutual exclusion. Now, the JVM assigns one and only one monitor per object. The syntax for declaring a section of code as a critical section is the following: synchronized (object) { .. }. Now, the object in the parentheses has to be a reference to an already instantiated object, of any class. All these behaviors are embedded in the Object superclass (which is a special class which exists in the JVM). Now, the code in the ellipsis is the "critical section", mutual exclusive access (by multiple threads) is guaranteed by the JVM in this code section. Now, you can declare entire methods synchronized; in this case, you are doing the equivalent of the following: void someMethod(){ synchronized( this ){ .. } }. The code in equivalent to: synchronized void someMethod(){ .. }.

However, you don't always have to use the current object's montior, in your classes. You can create dummy objects, whose only purpose is to act as locks for your objects. You can create an object of any class (like String) and then synchronized on that object. For example:

```java
   1: public class SomeClass{
   2:   private String lockObject = new String();
   3:
   4:   public void someMethod(){
   5:     synchronized( lockObject ){ .. }
   6:   }
   7:
   8:   public void someOtherMethod(){
   9:     synchronized( this ){ .. }
  10:   }
  11: }
```

In this example, someMethod() has a critical section that uses the lock of the lockObject. Now, while a thread is running through someMethod(), another thread could concurrently run through someOtherMethod(), since it uses the lock of "this", which is a different object from lockObject. You can make different parts of your code become mutually exclusive based on different object monitors. This is quite powerful and flexible when your object might have to allow certain operations to occur mutually exclusively, while others to happen concurrently.

If you have a completely static class, there is one monitor object associated with that class object. Normally, a monitor is attached (by the JVM) to each instance of a class.

### Monitors and internal queues

Now, what exactly happens to a thread once it tries to acquire a lock and enter a critical section of code, but it finds that the lock has already been acquired by some other thread? Well, the first thread is already executing the code in the critical section, when the second thread tries to enter that same section. The JVM puts this (second) thread in a special queue associated with the monitor object on which the critical section was synchronized. These are properties of the object monitor (supplied by the JVM implementation). These properties are specified in the Java language definition, and a JVM has to implement all this functionality in order to be Java compliant.

Now, while the first thread is still executing code in the critical section, and the second 
thread is waiting (inside the monitor's queue), if a third or fourth thread try to run the code 
in the synchronized block, they will be suspended and placed in this queue as well. Once a thread
 is placed in this queue, it is no longer "alive", its liveness gets taken away by the JVM. These 
 threads are placed in this queue in the order in which they try to acquire the monitor. Now, once the first thread completes execution of the critical section, it release the monitor's lock. At this point, the JVM picks the second thread and restores its "liveness" and makes it run the code in the synchronized block. Once the second one is done, the third one is revived and allowed in, and so on. Let's call this queue the synchronized queue.

This seems pretty automatic, and for most people this is all it takes to make code threadsafe. 
However, in order to do more advanced things, like not polling to be notified of some event, you have to learn how to use wait() and notify() to manipulate this internal monitor queue.

### wait()

When a thread enters a critical section, all other threads trying to get into this block of code are automatically suspended by the JVM. Now, what if you want to control this mechanism, so its no longer automatic. In that case, you have to use the two methods: wait() and notify(). These methods are defined and implemented in the Object class. Let's say, you don't want this first thread to complete its run through the critical section, but you want it to give up its monitor lock. You can "suspend" this thread, and put it in that monitor's waiting queue, by executing the wait(). Once a thread acquires a monitor lock, and it executes the wait() method, it is put in the wait() queue, and the thread relinquishes its monitor lock! At this point, the second or third thread that was waiting to acquire this monitor lock gets its chance to do so, and enters the critical section. Now, the wait() queue is different from the internal monitor queue that was discussed in the previous paragraph. So there are two queues that are in a monitor object:

  1. one queue that holds all the threads that are trying to acquire the monitor lock required to enter a critical section; let's call this queue the synchronized queue

  2. another queue that holds all the threads that have executed the wait() method and are currently suspended; let's call this queue the wait() queue.

Please be careful not to confuse these queues. In order for a thread to even execute the wait() it has to first acquire the monitor lock. So if the thread is waiting to acquire this lock, there is no way it will even get to execute wait(), or be put in the wait() queue.

Here is how you can use the wait() method:

```java
   1: public void someMethod(){
   2:   synchronized(this){
   3:     try{
   4:       wait();
   5:     }
   6:     catch(Exception e){
   7:     }
   8:   }
   9: }
```

I will explain what the exceptions are for in the following sections of this tutorial. For now, just focus on the wait() method suspending the current thread and releasing the monitor lock.

Once a thread is put in this queue, it loses its "liveness", and at some point it has to be "woken up", otherwise, it effectively "dies". You have to be very careful when using wait() on threads, because if you forget to "wake" them, they don't come back to life. How do you wake them up? By using notify() or notifyAll() of course :). Now, in order to use wait() and notify(), you have to use what is traditionally called a "condition variable". This is a pattern that you must use when working with monitors and wait() and notify(); you have to use a different design pattern when working with semaphores.

Here is an illustration of this pattern: a thread evaluates a condition to determine if it should execute wait(). Now, this evaluation must be done in a while( condition ) loop, not an if( condition ) statement. Also, in some other method, there has to be an invocation to notify() or notifyAll() made. In fact, there should be a call to notify() or notifyAll() for each invocation of wait(); this is just a simple check to remind you not to take away liveness from your threads inadvertently.

A source code example to illustrate this condition-variable pattern can be seen in the following Queue class:

```java
   1: import java.lang.reflect.*;         //Array, etc.
   2: import java.util.*;                 //Vectors, etc
   3: import java.io.*;                   //Serializable, etc
   4:
   5: public class Queue {
   6:
   7: protected List list = new ArrayList();
   8:
   9: /**
  10:  * This method returns an object from the front of the queue and
  11:  * suspends the active thread if the queue is empty.
  12:  *
  13:  * Report all exceptions that happen to the wait()ing thread
  14:  * to other objects that have called this method (because it
  15:  * is their thread which is waiting).
  16:  */
  17: public Object get(){
  18:   synchronized( this ){
  19:
  20:     //if the list is empty then freeze the current thread
  21:     while( list.isEmpty() ) {
  22:       try{
  23:         wait();
  24:       }
  25:       catch(InterruptedException e){
  26:         return null;
  27:       }
  28:       catch(Exception e){
  29:         return null;
  30:       }
  31:     }//end while( list.isEmpty() )
  32:
  33:     //return the first element in the list, and remove it from list
  34:     return list.remove( 0 );
  35:   }//end critical section
  36:
  37: }
  38:
  39:
  40: /**
  41:  * This method inserts object into the list. If an Array is
  42:  * passed to this method, then each object in the Array is
  43:  * inserted in the list one at a time (using reflection).
  44:  */
  45: public void put( Object o ){
  46:   synchronized( this ){
  47:
  48:     if(o.getClass().isArray()) {
  49:       //add each object in the array to the list
  50:       for( int i=0; i<Array.getLength(o); i++) {
  51:       list.add( Array.get( o , i ) );
  52:       }
  53:     }
  54:     else{
  55:       //add the object to the list
  56:       list.add( o );
  57:     }
  58:
  59:     //notify any threads waiting for the q to be non-empty
  60:     notify();
  61:   }//end critical section
  62: }
  63:
  64: }
```

The Queue object is a grow-able FIFO queue that holds objects (built on top of a java.util.List).
 It has two methods, get() and put(). The get() method can be used to get objects from the Queue, while the put() method is used to insert objects into the Queue. The way this Queue can be used is that a Consumer thread can get() objects from the Queue, and do some work on it; and concurrently a Producer thread can put objects into the Queue (for the Consumer to work on). Now, the Queue is the shared object (or data channel) between the Producer and Consumer. Because of the way in which the Queue has been designed, there is no need for the Consumer to poll the Queue to see if there are any new objects in it. This makes it very efficient for use at runtime.

The Producer thread inserts objects into the Queue at any time, asynchronously with the Consumer. Now, the Consumer thread can't consume objects if the Queue is empty. In order to avoid polling the Queue to see if it is not empty, wait() is used by the Queue, to suspend the Consumer thread. The Producer thread (that calls put()) causes notify() to be invoked, which ends up reviving the waiting threads.

### notify() and notifyAll()

If you look at the get() method, there is a while loop that determines if the currently executing thread should wait(). This fits the pattern of the condition variable. In this case, the condition is: is the queue empty?. If the queue is empty, then the Consumer thread (which calls get()) can't do anything, so the Queue makes it wait(). Once, a Producer thread put()s an object into the Queue, it notifies this waiting thread that it should reevaluate its waiting condition. Please note that notify() must be called in a synchronized block. As soon as a Producer inserts an object into the Queue, and notify() gets called, one (or all) Consumer thread(s) that are waiting for it to become non-empty get notified to re-evaluate their condition variable. If notify() gets called, only one waiting thread is revived and it immediately re-evaluates its condition variable, to determine whether it should wait() again or do something. Now, if there is more than one thread waiting on this condition, notify() causes one and only one thread to be randomly picked to be notified. However, if notifyAll() is used, all threads that are waiting are notified and asked to re-evaluate their condition variable. In the case of the Queue, there is no need to use notifyAll() as it would just be wasteful, as it would notify a lot of threads for nothing, just wasting CPU cycles. In some applications, it becomes necessary to use notifyAll(). Even when notifyAll() is used, not all wait()ing threads get to trample through the Queue object, the restrictions of synchronization are still in effect, and the JVM notifies all threads at once, but they don't all get to evaluate their condition variable at once, they have to wait to acquire their monitor lock. However, all the wait()ing threads do re-evaluate their condition variable, whereas with notify() only one thread gets to re-evaluate its condition variable.

This condition-variable pattern must be used when using wait() and notify() with object level monitors. The Queue class demonstrates the classic Computer Science Consumer Producer problem.

### interrupt(), InterruptedException and other thread exceptions

If you look at the get() method, there is some exception handling code, due to the wait() method. When a thread is put in the wait() queue, conditions can occur that remove it from this queue. For example, there might be a situation where a thread is wait()ing, and another thread comes along and interrupt()s it. This can happen if a reference to the wait()ing thread is held in an object, and another thread runs through this object. This kind of behavior is useful when creating server side objects whose lifecycles you have to control. I will give examples of this in the next section. Now, the strange thing to remember is that when the wait()ing thread gets interrupt()ed, it resumes execution by throwing an exception in the code block of the wait() method. Once the InterruptedException is dealt with, the wait()ing thread is alive again, and if the exception is dealt with properly, should resume execution as it was intended, rather than just throwing an unhandled exception and freezing the thread. An example of this can be seen in the following example. This might be confusing if you are not that familiar with threads; things can get very confusing in your code, when a thread, which was created in one object, runs through other objects.

Let's say that the Consumer object has its own thread, and the Producer object has its own thread, and that they both share the Queue object. Now, after they are running for sometime, let's say that you want to shut down the Consumer, which might happen in a server side environment, where you might have to replace the Consumer with a different object (for example, if the class gets updated in a Servlet environment, or a new version of an object is deployed). In order to shut and take down this Consumer object at runtime, its thread has to be taken off of the wait()ing queue (if it is currently waiting). The best way to do this, is to have the server thread invoke a shutdown method of some sort on the Consumer object. The shutdown method should then invoke the interrupt() method on the Consumer's thread. Once this happens, an exception gets generated in the Queue's get() method (where the Consumer's thread was waiting). Phew! So, the Consumer's thread was interrupted in the Queue's get() method, and it returns null. The Consumer thread's run() method should have logic in it to determine when this has happened, and it should self terminate. Please note that complicated logic occurs because every thread has to have a run() method in which it all happens. This will be illustrated in the next section.

## Thread management strategies for server-side component threads

A big way in which multithreaded objects differ from single threaded ones, is that threaded 
objects start with the run() method. This means that "liveness" in a threaded object begins in the run() method, and this imposes certain design patterns on threaded class designs. For these threaded objects, life begins in the run() method, but the threads run through many other objects. This is sort of like the main() in self starting classes. However, the JVM takes care of the lifecycle for this class. Once you return from the main(), if there are no daemon threads running, the JVM self terminates, and you can always call System.exit(int) which terminates the JVM. However, for your autonomous, asynchronous, threaded objects, you can't shutdown the JVM just to terminate them. This kind of thinking is unacceptable in the real-world, especially in the server-side environment, where you have to deal with components going online and offline, new versions being deployed, and changes being made to the system (swapping out implementation classes, while keeping interfaces the same, working with the same underlying data). There are many constraints in the real-world (especially in the server-side world), and you have to use a rich framework to make elegant, and efficient use of threads.

When implementing the run() method of these threaded classes, you usually have to have a big while loop which keeps going until the object is signalled to shutdown; its like an infinite loop in which certain sequence of operations keep happening. Now, you might have a threaded class that is used on a one-time basis only, and in this case you don't need to loop. This is necessary when you have to perform some concurrent task that has nothing to do with anything else.

This is especially important if you create your own server side frameworks. EJB only helps in certain types of situations, it is not always the server-side framework of choice, neither is the Servlet framework. They are good frameworks, but by the nature of computing, with new things happening all the time, you might have to come up with the next framework. For example, you might have to create an instant messaging (server side) component framework, or online presence tracking, or GPS location framework, or real time driving directions framework, and so on. In these cases, you have to dig into your system architect toolbox (which is in your head, and experience, success, and ability are the tools) and create extensible, simple, and efficient frameworks to do the job, and do it well.

### ServiceIF

You should make your threads self-terminating, and they should expose lifecycle control and resource management methods. This means that you should be able to start your threaded objects, as well as shut them down. When you start them, they allocate certain resources (like memory, threads, sockets, etc.), so when you shut them down, they should give back these resources, so that these expensive resources are not wasted. If you do this, you can start and shutdown your threads, without any loss of resources. Here is an interface (called ServiceIF) that embodies these ideas:

```java
   1: /**
   2:  * ServiceIF encapsulates a few methods that can be
   3:  * invoked on a threaded object, to control the lifecycle of
   4:  * this object. This includes:
   5:  *   startup
   6:  *   shutdown
   7:  *   check the current liveness state (is it shutdown already?)
   8:  *   a thread accessor method.
   9:  */
  10: public interface ServiceIF
  11: {
  12:     public void start();
  13:     public void shutdown();
  14:     public boolean isShutdownCompleted();
  15:     public Thread[] getThreads();
  16:     public boolean isMultipleThreads();
  17: }
```

A threaded class that properly implements this class can fit into most server side frameworks, where server side components are created (and terminated) by the framework at runtime. The getThreads() method might be useful in the worst case scenario, where the framework can cause the thread to self-terminate, and has to perform some low-level operations on it.

### ServiceIF implementation in a server framework

Here is an implementation of this interface that uses the Queue class. The EventDispatcher processes objects that are placed in the Queue, by event object sources. You can plug in event handlers into this EventDispatcher class, but none are provided. This class can be used in the real world to do threaded queue processing, which is why it is so generic. However, it does have its own thread, which can be started and shutdown, and this is where the ServiceIF comes in. The way the EventDispatcher can be used in the real world, is by plugging some kind of event handler in there, which delegates events to different listeners. This is left as an exercise to the reader.

Here is the EventDispatcher code:

```java
   1: import java.util.*;                 //Vectors, etc
   2: import java.io.*;                   //Serializable, etc
   3:
   4: /**
   5:  * process():
   6:  * This is a threaded class (it implements ServiceIF). Most of the
   7:  * methods in this class are for thread management, except for 
   8:  * the process() method. If you are interested in adding more
   9:  * event processing functionality to this class, you simply need
  10:  * to modify this method alone.
  11:  * 
  12:  * threads:
  13:  * This class has its own thread (t), which simply calls the get()
  14:  * method on the queue, and potentially wait()s for a long time.
  15:  * As soon as it receives something from the queue (ie, the get()
  16:  * method unblocks, and notify() is called) the thread runs the
  17:  * process() method. This method looks at all the information that
  18:  * comes in, and determines what to do (and where to route all this
  19:  * information to). Rules processing basically, done on a thread
  20:  * which is used to block on a get() from the queue. Now, once
  21:  * processing happens, the right objects (possibly shared) in the
  22:  * right places are updated with this new information. For example
  23:  * events can be cast over sockets, and get turned back into 
  24:  * events on the listening side. Its like layering event dispatching 
  25:  * and processing over sockets.
  26:  * 
  27:  */
  28: public class EventDispatcher
  29: implements ServiceIF, Runnable
  30: {
  31: //
  32: // Data Members
  33: //
  34: protected Queue q;
  35:
  36: /** ServiceIF and DebugIF data */
  37: protected Thread t = null;
  38: protected boolean shutdownCompletedFlag = false;
  39: protected boolean shutdownFlag = false;
  40:
  41: /** shutdown synch objects */
  42: private boolean isWaitingToGet = false;
  43: private final Object lock = new StringBuffer();
  44:
  45:
  46: //
  47: // constructor
  48: //
  49: public EventDispatcher( Queue q ){
  50:   this.q = q;
  51: }
  52:
  53:
  54: //
  55: // actual event processing method
  56: //
  57: public void process( Object o ){
  58:   //insert your code here
  59: }
  60:
  61:
  62: //
  63: // Runnable impl
  64: //
  65: public void run(){
  66:   while( shutdownFlag == false ) {
  67:     try{
  68:       //try and get something from the q, this thread will wait()
  69:       //if the queue is empty!
  70:       synchronized( lock ){
  71:         isWaitingToGet = true;
  72:       }
  73:
  74:       Object o = q.get();
  75:
  76:       synchronized( lock ){
  77:         isWaitingToGet = false;
  78:       }
  79:
  80:       if( o == null ) {
  81:         //someone interrupted thread (t) wait()ing on q.get()
  82:         //someone must have asked for a shutdown; 
  83:         //in either case, break out of while loop, as the thread
  84:         //cant continue in any meaningful manner.
  85:         break;
  86:       }
  87:
  88:       //perform some processing task on this object from the queue
  89:       try{
  90:         process( o );
  91:       }
  92:       catch(Exception e){
  93:         System.out.println( e );
  94:         //put the object back into the queue, as it could not be
  95:         //processed
  96:         q.put( o );
  97:       }
  98:     }
  99:     catch(Exception e){
 100:       //something bad happened period, shutdown!
 101:       shutdownFlag = true;
 102:     }
 103:
 104:     }//end while (...)
 105:
 106:
 107:     // 
 108:     //shutdown everything (release all open resources)
 109:     //
 110:
 111:     shutdownCompletedFlag = true;
 112: }
 113:
 114:
 115: //
 116: // ServiceIF impl
 117: //
 118: public void start(){
 119:   if( t == null ) {
 120:     t = new Thread( this );
 121:     t.start();
 122:   }
 123:
 124: }
 125:
 126: public void shutdown(){
 127:
 128:   synchronized( lock ){
 129:     if( isWaitingToGet == true ) {
 130:       //the thread (t) is currently wait()ing in the q.get() method
 131:       //interrupt it!
 132:       //shutdown imminent, InterruptedException handler should take
 133:       //care of everything.
 134:       if( !t.isInterrupted() ) {
 135:         t.interrupt();
 136:       }
 137:     }
 138:   }//end critical section
 139:
 140:   shutdownFlag = true;
 141:
 142: }
 143:
 144: public boolean isShutdownCompleted(){
 145:   return shutdownCompletedFlag;
 146: }
 147:
 148: public Thread[] getThreads(){
 149:   Thread[] tRay = new Thread[ 1 ];
 150:   tRay[0] = t;
 151:   return tRay;
 152: }
 153:
 154: public boolean isMultipleThreads(){
 155:   return false;
 156: }
 157:
 158:
 159: }//end of EventDispatcher class
```

Study the code to see how each of the ServiceIF methods are implemented. There are quite a few flags that are used to determine the state of this object while it's thread does what it needs to. The server framework thread is also understood to exist in this environment and it is the one that invokes all of the ServiceIF methods. The run() method contains all the operations that belong to the ServiceIF implementation's own thread, which really does all the work. The server framework thread just controls the lifecycle.

What are real world examples of a server framework? A really simple and effective one is the Servlet API framework. You can draw parallels in how the Servlet API controls the lifecycle of Servlet objects. Most server frameworks are similar in lifecycle management strategies/techniques. Studying/working with one at a low-level will give you insights on how to work in such an intimate level with these systems.
