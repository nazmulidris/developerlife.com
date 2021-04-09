---
author: Nazmul Idris
date: 2000-09-20 18:00:57+00:00
excerpt: Introduction to multithreading in Java
layout: post
title: "Introduction to Threads"
categories:
  - CC
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [What is a thread?](#what-is-a-thread)
- [Java threads](#java-threads)
- [Implementing Runnable vs. extending Thread](#implementing-runnable-vs-extending-thread)
  - [Choosing to implement Runnable](#choosing-to-implement-runnable)
  - [Choosing to extend Thread](#choosing-to-extend-thread)
  - [Source code examples](#source-code-examples)
- [Servlets and RMI potential hazard](#servlets-and-rmi-potential-hazard)
- [The synchronized keyword](#the-synchronized-keyword)
- [Thread-safe vs. threaded classes](#thread-safe-vs-threaded-classes)
- [Example Problem](#example-problem)
- [Solution (design)](#solution-design)
- [Code](#code)
- [Why?](#why)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## What is a thread?

A thread is a path of execution through code; in other words, a thread is a single sequential flow
of control within a program. What does that mean? In Java, objects are not "alive", rather threads
are "alive". Threads run through your code (ie, the methods in your objects). When you invoke the
main() method in your class, the Java Virtual Machine (JVM) creates a thread for you that actually
runs the code in this method. Another thread that is always running in the JVM is the garbage
collector thread (which makes sure to reclaim memory for objects that are no longer referenced by
any other objects).

For example, let's say you have a class, called MyClass.java, that has a main() and print() method,
shown in Figure 1. When you run this class, by typing java MyClass at the command prompt, the JVM
creates a thread to run through the main() method. At the same time during which the thread is
running through your object, the JVM has a garbage collection thread running, ie, they are running
concurrently.

![]({{'assets/threads-1.jpg' | relative_url}})

## Java threads

Java allows you to create your own threads that can be run through any class that you write. Threads
are lightweight processes (if you're familiar with UNIX processes). By allowing you to spawn any
number of threads in a single (JVM) process, you can have your objects perform concurrent tasks.
This is very important for network programming, in a distributed environment, where your objects
might be waiting for data from objects on other hosts (ie, remote objects). By being multithreaded,
your objects can do something else while they wait; for example, they can service a large number of
requests from other remote objects. Threads are used heavily in the Servlet API, EJB, RMI and just
about any server framework.

There is more than one way to use threads. Sometimes you have to create "threaded" classes (ie,
classes that create and manage their own threads to perform concurrent tasks), but most of the time
you have to make sure that your classes will handle multiple threads trampling through them (for
example, Servlet classes).

In the advanced thread tutorial you will see how to make complex "threaded" classes. In this
tutorial you will learn how to:

1. make simple "threaded" classes (classes that create and manage their own threads)

2. create classes that can handle multiple threads trampling through them (for example, Servlet
   classes).

## Implementing Runnable vs. extending Thread

There are two ways of creating your own "threaded" classes, you can:

1. implement the java.lang.Runnable interface

2. extend the java.lang.Thread class.

These two ways of creating threads have slightly different semantics, in the way in which a thread
runs through your objects. However, there are similarities in using either of the two ways, you must
have a run() method. Your thread will execute this run() method, once the thread has been
instantiated and started.

### Choosing to implement Runnable

In fact, the Runnable interface only has one method, which is public void run(). The way to use
Runnable is as follows:

1. Create a class that implements Runnable and be sure to implement the run() method

2. In order to make this run() method come "alive", you have to create a Thread object and pass it
   the Runnable implementation class as a parameter (to the constructor).

3. Then you have to invoke the start() method on this Thread object.

Your Runnable object (the threaded class) is not a thread itself. However, you can use the Thread
class (in Java everything is represented as a class, even threads) to run your Runnable object
(concurrently). So you have separate Thread objects, potentially all running through the same
instance of your Runnable object. You can choose not to do this, but you can do this if you want to,
since you have to give the Thread constructor a reference to the Runnable object in order to
instantiate the Thread object. Don't forget to start() the Thread object, in order to make your
Runnable object come "alive".

The Servlet API, for example, chooses to have Servlets implement the Runnable interface rather than
extending the Thread class. The end result of this is that there is one instance of the each Servlet
class, and the Servlet container creates a new thread for each HTTP request that comes in (for that
Servlet) and attaches it to the same Servlet object. This is the Singleton pattern, where only the
same (single) instance of a class is used anywhere that an object of that class is required. Now,
you can override this default behaviour of Servlets, by having your Servlet extend
[SingleThreadedModel](http://jserv.javasoft.com/products/java-server/documentation/webserver1.1/apidoc/Package-javax.servlet.html).
This starts to emulate the behavior that you would get by extending Thread. When you extend
SingleThreadedModel, a new Servlet object is created for every thread that is created to service
each HTTP request. This behavior is illustrated in Figure 2. Please refer to the source code example
below on the details of implementing Runnable.

The behavior of RMI objects is very similar to this. When a client looks up a remote reference, they
get a stub to the skeleton of the remote object. Now, there is only one remote object, per remote
reference. However, a multitude of clients can connect to this singular remote object and invoke
methods on it. Sounds like the Singleton pattern at work again. The skeleton creates a new Thread
that runs through the singular remote object (in addition to managing all the protocol translation
between it and the stub). This is very similar to the Servlet mechanism. This kind of design
strategy exists in most server frameworks, from Servlets, to RMI, to CORBA ORBs.

![]({{'assets/threads-2.jpg'| relative_url}})

### Choosing to extend Thread

Another way of creating "threaded classes" is by extending the Thread class directly. This might
seem simpler than implementing the Runnable interface, but its the same amount of work. In fact,
sometimes it is not possible to extend Thread, because your threaded class might have to extend
something else. The only difference between implementing Runnable and extending Thread is that by
extending Thread, each of your threads has a unique object associated with it, whereas with
Runnable, many threads share the same object instance. This behaviour is also illustrated in
Figure 2. Please refer to the source code example for details of extending Thread.

### Source code examples

Two implementations of the ThreadedClass class are shown below, created once by implementing
Runnable, and again by extending Thread. You can correlate the source code to Figure 2.

The code to implement Runnable is shown below:

```java
   1: //Implementing Runnable
   2: public class ThreadedClass
   3: implements Runnable
   4: {
   5:     int data;
   6:
   7:     public ThreadedClass(){
   8:         data = 0;
   9:     }
  10:
  11:     public void run(){
  12:         //this method runs when start() is invoked on the thread
  13:         System.out.println( data );
  14:     }
  15:
  16:     public Thread getNewThread(){
  17:         Thread t = new Thread( this );
  18:         return t;
  19:     }
  20:
  21:     public static void main( String[] args ){
  22:         ThreadedClass threadedClass = new ThreadedClass();
  23:         Thread t1 = threadedClass.getNewThread();
  24:         t1.start();
  25:
  26:         Thread t2 = threadedClass.getNewThread();
  27:         t2.start();
  28:     }
  29: }
```

In the main() method of the code above, only one instance of ThreadedClass is created. This one
instance is used to spawn a multitude of threads (each executing the run() method of the same
object). This is analogous to what happens with RMI or Servlets. This is how you can share instance
variables of a Servlet across multiple threads of the same Servlet running in the Servlet container.
If you wish to create a new instance of a Servlet per thread, then your Servlet has to extend
[SingleThreadModel](http://jserv.javasoft.com/products/java-server/documentation/webserver1.1/apidoc/Package-javax.servlet.html).

The code to extend Thread is shown below:

```java
   1: //Extend Thread
   2: public class ThreadedClass
   3: extends Thread
   4: {
   5:     int data;
   6:
   7:     public ThreadedClass(){
   8:         data = 0;
   9:     }
  10:
  11:     public void run(){
  12:         //this method runs when start() is invoked on the thread
  13:         System.out.println( data );
  14:     }
  15:
  16:     public static void main( String[] args ){
  17:         ThreadedClass t1 = new ThreadedClass();
  18:         t1.start();
  19:
  20:         ThreadedClass t2 = new ThreadedClass();
  21:         t2.start();
  22:     }
  23: }
```

Notice the difference between the Runnable and Thread versions? In the Runnable version you just
created one ThreadedClass object and then created a bunch of Thread objects based on this Runnable
object. These threads were all running through the same Runnable object (the ThreadedClass object).
In the "extends Thread" version, you actually have to create a new ThreadedClass object per thread
that you want to start.

Depending on the problem you have to solve, you have to choose the appropriate method in your
design. The 2 methods have their differences, and by understanding these differences you can take
advantage of them in your threaded classes.

## Servlets and RMI potential hazard

When you are creating classes that are going to be used by Servlets or RMI objects, you **must**
make these classes "thread-safe". You must made them make them thread-safe because many RMI or
Servlet threads might be trampling through your code concurrently at any given time (by the very
nature of RMI and Servlet architecture). This is where **synchronization **comes in. In the previous
case, where you were creating threaded classes, you are the one spawning the threads, and the
objects that these threads trample through are responsible for being thread-safe. The difference
between making threaded classes vs. making thread-safe classes is very similar to throwing
exceptions vs. catching them.

## The synchronized keyword

In Java, when the synchronized keyword is used in a method, the JVM guarantees that only one thread
will be able to run through that method at any given time, ie, there is no concurrent thread access
to that block of code. These blocks of code are also known as critical sections. You can synchronize
entire methods by using the synchronized keyword in the method declaration, or you can just mark
certain lines of code as synchronized. When you use the latter, approach, you have to use an object
to synchronize "on". I will explain this in detail in the advanced tutorial, but for now, just use
"this" to synchronize code blocks. Here is an example of how to use the synchronize keyword to make
an entire method mutually exclusive, or thread-safe:

```java
public synchronized void someMethod() {..}
```

Now, in order to make just a few lines of code thread-safe, use:

```java
synchronized( this ){
    //critical section
};
```

Why would you want to make only a section of your method thread-safe? Code that is thread-safe (ie,
protected by synchronized) is slower than code that isn't. For better performance, you should only
make those lines of your code thread-safe, that absolutely need to be. In the advanced thread
tutorial, you will see why the code is slower, and what exactly the synchronized keyword does (it
has something to do with object level monitors). However, if this tutorial satisfies your needs,
then you can save time by not going through the advanced tutorial :).

## Thread-safe vs. threaded classes

When you make thread-safe classes, you have to keep in mind that multiple threads could be trampling
through the methods of your class. This requires **special care** in designing and coding these
classes, because there is no way of knowing what thread will invoke what method (and in what
sequence) on an object of this class. You have to take into account all possible scenarios or design
in such a way that the number of possible states that your object can reach is minimized. I prefer
to use the smart solution and design in such a way that the number of states my object can reach is
minimized, that way I don't have to think about too many possibilities of what might happen when
multiple threads are trampling through the same instance of my class.

In order to make thread-safe classes there are a few simple rules to follow:

- Mutator method access to any shared objects must be synchronized.

- Accessor method access to any shared objects need not be synchronized.

  - **There is an exception to this rule however.** When your shared object's value fluctuates very
    frequently (like stock prices), then it is necessary to synchronize the accessor too, in order
    to report the correct value of the object rather than some intermediate (and inaccurate) value
    of the object. There are more advanced techniques to get around making your accessors
    synchronized which I will show you in the advanced thread tutorial. But for now, be sure to
    synchronize everything!

## Example Problem

I will illustrate the problem by using a bank account example. Lets say that I have a bank account
object (this is not thread-safe) which is accessed by a bunch of threads. My bank account object has
a method that adds a given amount of money and removes that same amount and returns (ie, after the
method returns my bank balance is still the same). Then I have another main class that simply spawns
a lot of threads and lets them loose on my bank account object.

Now, you might think that this example shouldn't even have any problems because that method in my
bank account object doesn't do anything. Well, adding money and then removing it from a bank account
are NOT atomic operations; an atomic operation is one that the JVM guarantees will occur without any
interruptions (for example updating a register in a processor). When many threads are trampling
through my (not thread-safe) bank account object, the bank balance does change! This is because
other threads mess with my bank balance before each thread gets done using it; so as one thread adds
money, and is just about to remove it, another thread could go in and remove more money, and my bank
balance is negative for an instant! There are an infinite number of possibilities (most of which are
undesirable) when a lot of threads are let loose on this poor object.

Here is some code (from TestUnsafe.java) for a design that is not thread-safe (and messes up my bank
balance with multiple threads):

```java
   1: //BankAcct - NOT thread safe
   2: class BankAcct{
   3:     int bal;
   4:
   5:     public BankAcct( int i ){
   6:         bal = i;
   7:     }
   8:
   9:      void doNothing(){
  10:         addRemove( 10 );
  11:         addRemove( 20 );
  12:         addRemove( 30 );
  13:     }
  14:
  15:      void addRemove( int m ){
  16:         bal+=m;
  17:         Util.sleepRandom();
  18:         bal-=m;
  19:     }
  20:
  21:      int get(){
  22:         return bal;
  23:     }
  24: }//end BankAcct class
  25:
  26: //TestUnsafe - creates threads and tramples through BankAcct
  27: public class TestUnsafe extends Thread{
  28:     //data members for this thread
  29:     private String name;
  30:     BankAcct ba;
  31:
  32:     //start this method
  33:     public static void main( String[] args ){
  34:         BankAcct ba = new BankAcct( 0 );
  35:         new TestUnsafe( "**      " , ba ).start();
  36:         new TestUnsafe( "  ++    " , ba).start();
  37:         new TestUnsafe( "    ==  " , ba ).start();
  38:         new TestUnsafe( "      //" , ba ).start();
  39:     }
  40:
  41:     //constructor
  42:     public TestUnsafe( String n , BankAcct ba ){
  43:         this.ba = ba;
  44:         name    = n;
  45:     }
  46:
  47:     //extending Thread
  48:     public  void run(){
  49:         doWork();
  50:     }
  51:
  52:     //simply displays the bank balance before and after this thread
  53:     //messes with the bankaccount
  54:     public void doWork(){
  55:         System.out.println(
                    name+" :doWork() - start : account bal = "+ba.get() );
  56:
  57:         ba.doNothing();
  58:
  59:         System.out.println(
                    name+" :doWork() - end   : account bal = "+ba.get() );
  60:     }
  61:
  62:
  63: }//end TestUnsafe class
```

If you compile, and then run TestUnsafe.java at a command prompt/console (by typing java
TestUnsafe), you will notice, from the output, that the bank balance is changing quite a bit. You
will see that the bank balance figure changes as the program runs, however, at the end the bank
balance is zero. Now, the problem is the fluctuations as the program runs; it should be zero,
because the doNothing() method of BankAcct, should not affect the bank balance. However, due to
TestUnsafe threads trampling through the BankAcct, it messes everything up.

## Solution (design)

Obviously the solution to this problem would be to synchronize the method in the BankAcct object
that messes with the bank balance. This would guarantee that only one thread was trampling through
it at any given time.

Also it is necessary to synchronize the accessor method too! Why? Well, the methods to add and
remove money from the account are so fast that when I use get() it sometimes returns the value of my
bank balance in the middle of doNothing(). So one thread is in the middle of executing doNothing()
at which point my bank balance is non-zero. At this same instant, another thread calls get() an gets
a non-zero value of my bank account. Ooops! The way to solve this is to synchronize the get() method
too, in order to ensure that my real bank balance is returned. On the other hand, if you wish to
monitor the state of this object at all times, then you might want to leave the get()
un-synchronized. It all depends on what you want to do.

The code below contains the thread-safe solution for this bank account problem:

## Code

Here is the source code for the solution TestSafe.java:

```java
   1: //BankAcct - thread safe version
   2: class BankAcct{
   3:     int bal;
   4:
   5:     public BankAcct( int i ){
   6:         bal = i;
   7:     }
   8:
   9:      void doNothing(){
  10:         addRemove( 10 );
  11:         addRemove( 20 );
  12:         addRemove( 30 );
  13:     }
  14:
  15:      synchronized void addRemove( int m ){
  16:         bal+=m;
  17:         Util.sleepRandom();
  18:         bal-=m;
  19:     }
  20:
  21:      public synchronized int get(){
  22:         return bal;
  23:     }
  24: }
```

The TestSafe class hasn't changed much from TestUnsafe: only the main() method is different, it
creates TestSafe objects, rather than TestUnsafe ones. When you run this code (by compiling and
running TestSafe.java) you will see that the bank balance is always 0. Don't forget to compile
TestSafe, before running it (due to namespace conflicts with TestUnsafe's BankAcct class). Now if
you make the get() method unsynchronized you will see some fluctuations in the bank balance, but
this is because the get() method might be getting the value of the balance just as its changing. At
the end of each method run, the value is still 0 though. This is a very **interesting** effect.

## Why?

You don't really have a choice, all your code should be thread-safe and re-entrant. Re-entrant means
that once a method is called on your object, it should be possible for someone else to call that
method. For an example of something that's non-re-entrant the IBM XML Parser (version 1.x) comes to
mind. When certain methods are called on the IBM DOM parser, and exceptions are thrown the entire
object becomes frozen and no one can call any more methods on that object. This is an example of
non-reentrant code. The parser code was probably not even tread-safe. I hope they have fixed these
problems in the newer versions.

In the realm of the server (which is NOT the realm of the client) the rules are different. **One of
the rules in this domain is that your code MUST be thread-safe whether you like it or not**.
