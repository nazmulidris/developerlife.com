---
author: Nazmul Idris
date: 2011-04-13 23:24:00+00:00
excerpt: |
  Overall, the API is pretty straightforward to use, assuming that you are
  familiar with asynchronous processing in the first place. However, if you are not
  familiar with asynchronous processing, then this business of callbacks can be quite
  confusing and daunting. Additionally Tomcat 7 and Servlet API 3.0 make it easier
  to configure servlets using annotations. There are other cool features in 3.0 that
  I haven’t covered in this tutorial, like loading servlets programmatically.
layout: post
title: "Creating asynchronous servlets with Tomcat 7 (Servlet 3.0 API)"
categories:
- Server
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [Some pseudo code to explain this](#some-pseudo-code-to-explain-this)
- [What if something goes wrong?](#what-if-something-goes-wrong)
- [Sample code](#sample-code)
  - [Simple example](#simple-example)
  - [Here’s the client side code that calls this](#heres-the-client-side-code-that-calls-this)
  - [Complex example](#complex-example)
- [To async or not to async](#to-async-or-not-to-async)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

Prior to Servlet API 3.0, in order to create servlet implementations that are asynchronous you would have to use something like Comet. However, Tomcat 7 and Servlet API 3.0, it is now possible to create servlets that can operate in both asynchronous and synchronous mode (and are portable across any 3.0 compliant app server, like Tomcat 7 or GlassFish 3.x). With synchronous servlets, a thread handling the client HTTP request would be tied up for the entire duration of time it takes to process the request. For long running tasks, where the server primarily waits around for a response (from somewhere else), this leads to thread starvation, under heavy load. This is due to the fact that even though the server isn’t doing anything but waiting around, the threads are being consumed by lots of requests as they come in (and threads are a finite resource).

Asynchronous servlets solve this problem by letting this thread that was engaged to handle the request go back to a pool, while the long running task is executing in some other thread. Once the task has completed and results are ready, then the servlet container has to be notified that the results are ready, and then another thread will be allocated to handle sending this result back to the client. The client is totally oblivious that this is happening on the server, and requires no change at all. To enable this async magic to happen, your new servlet must use a callback mechanism (supplied by the app server itself) by which to notify the app server that the results are ready (to be sent back to the client). Additionally, you have to tell the servlet container/app server when to release the thread that’s handling the request right now (just after you spawn some background task to do the actual work).

## Some pseudo code to explain this

Here’s some pseudo code, from the perspective of the servlet, to explain this:

  1. Client request comes in via HTTP and is dispatched to some servlet.

  2. The servlet’s `service()` method is executed in some thread provided by the app server/servlet container.

  3. The `service()` method must create an `AsyncContext` (by calling `startAsync()`).

  4. The `service()` method must then create a `Runnable` and pass it to an `Executor` for execution on some other thread. This `Runnable` will have a reference to the `AsyncContext` (as it will need this to notify the app server that it’s done in the near future).

  5. The `service()` method must then then return and terminate execution of this method! This might seem counter intuitive, but this is the asynchronous part.

Now, when this happens, the client is still connected to the server and is still waiting. At some later time, the following occurs:

  1. The `Runnable` that is now done processing the request (in some thread provided by an `Executor`), and has the results ready, will notify the `AsyncContext` that the response is ready. It will write the result to the `HttpResponse`, and then call `complete()` on the `AsyncContext`. This signals the app server to send this result back to the client, which has been waiting for this data this entire time.

## What if something goes wrong?

If something unexpected goes wrong before the `Runnable` has been sent off to the `Executor`, then the client application will just get some kind of network exception. However, if something does go wrong in the `Runnable`, there is one way to handle this. When creating an `AsyncContext`, you can specify two things:

  1. maximum amount of time that can pass before the results must be ready, otherwise a timeout error will occur,

  2. attach a listener that can handle this timeout condition occurring in a listener implementation that you provide.

So, if something bad happens inside your `Runnable`, then after the appropriate time, specified by your timeout (in ms), has passed, the listener will be called and told that a timeout condition has occurred. Your timeout handler code will then run, and you can send some error response back to the client that’s been waiting all this time. If your runnable (after all this has occurred) then tries to write to the `HttpResponse` object, then an exception will be raised in the `Runnable` code. Also, if `AsyncContext.complete()` is called, this will also raise an exception in your `Runnable` code. You essentially have to throw away any results at this point that may have been generated.

## Sample code

I have provided two sets of examples of asynchronous servlets: a simple one and a complex one. The simple example just goes through and introduces you to the concept of asynchronous servlets and web.xml fragments (which is another cool addition to Servlet 3.0). The complex example shows what happens when long running tasks timeout and cause errors, so you can see how to handle them.

### Simple example

```java
@javax.servlet.annotation.WebServlet(
    // servlet name
    name = "simple",
    // servlet url pattern
    value = {"/simple"},
    // async support needed
    asyncSupported = true
)
public class SimpleAsyncServlet extends HttpServlet {
 
/**
 * Simply spawn a new thread (from the app server's pool) for every 
 * new async request. Will consume a lot more threads for many 
 * concurrent requests.
 */
public void service(ServletRequest req, final ServletResponse res) 
    throws ServletException, IOException {
 
  // create the async context, otherwise getAsyncContext() will be null
  final AsyncContext ctx = req.startAsync();
 
  // set the timeout
  ctx.setTimeout(30000);
 
  // attach listener to respond to lifecycle events of this AsyncContext
  ctx.addListener(new AsyncListener() {
    public void onComplete(AsyncEvent event) throws IOException {
      log("onComplete called");
    }
    public void onTimeout(AsyncEvent event) throws IOException {
      log("onTimeout called");
    }
    public void onError(AsyncEvent event) throws IOException {
      log("onError called");
    }
    public void onStartAsync(AsyncEvent event) throws IOException {
      log("onStartAsync called");
    }
  });
 
  // spawn some task in a background thread
  ctx.start(new Runnable() {
    public void run() {
 
      try {
        ctx.getResponse().getWriter().write(
            MessageFormat.format(
                    "<h1>Processing task in bgt_id:[{0}]</h1>",
                    Thread.currentThread().getId()));
      }
      catch (IOException e) {
        log("Problem processing task", e);
      }
 
      ctx.complete();
    }
  });
 
 
}
 
}
```

Notes on the code:

  1. You can actually name your servlet and provide it’s url pattern in the code using annotations, without having to mess with `web.xml` entries

  2. You have to pass `asyncSupported=true` to tell the app server that this servlet needs asynchronous mode.

  3. In the `service()` method, the timeout value is set to 30 seconds. So as long as the `Runnable` takes less than this amount of time to call `complete()`, no timeout errors will be generated.

  4. The `Runnable` is actually passed to the app server for execution on a different thread (than the one running the `service()` method).

  5. The `AsyncContext` listener does not really do anything useful in this example, just prints out “`onComplete called`” to the app server log when requests come in.

### Here’s the client side code that calls this

```java
public class LoadTester {
 
public static final AtomicInteger counter = new AtomicInteger(0);
public static final int maxThreadCount = 100;
 
public static void main(String[] args) throws InterruptedException {
  new LoadTester();
}
 
public LoadTester() throws InterruptedException {
  // call simple servlet
  ExecutorService exec1 = Executors.newCachedThreadPool();
  for (int i = 0; i < maxThreadCount; i++) {
    exec1.submit(new UrlReaderTask("http://localhost:8080/test/simple"));
  }
  exec1.shutdown();
  
  Thread.currentThread().sleep(5000);
  System.out.println("....NEXT....");
 
  // call complex servlet
  counter.set(0);
  ExecutorService exec2 = Executors.newCachedThreadPool();
  for (int i = 0; i < maxThreadCount; i++) {
    exec2.submit(new UrlReaderTask("http://localhost:8080/test/complex"));
  }
  exec2.awaitTermination(1, TimeUnit.DAYS);
}
 
public class UrlReaderTask implements Runnable {

  private String endpoint;
  public UrlReaderTask(String s) {
    endpoint = s;
  }
  public void run() {
 
    try {
      actuallyrun();
    }
    catch (Exception e) {
      System.err.println(e.toString());
    }
 
  }
 
  public void actuallyrun() throws Exception {
 
    int count = counter.addAndGet(1);
    BufferedReader in = new BufferedReader(
        new InputStreamReader(
            new URL(endpoint).openStream()));
    String inputLine;
    while ((inputLine = in.readLine()) != null) {
      System.out.println(
              MessageFormat.format("thread[{0}] : {1} : {2}",
                                   count, inputLine, endpoint));
    }
    in.close();
 
  }
 
}
 
}//end class ComplexLoadTester
```

Notes on the code:

  1. This simple console app just spawns 100 threads and makes concurrent `GET` method calls on the URL for the simple and complex asynchronous servlets.

  2. The simple asynchronous servlet runs without any issues and will show all the responses that come back from the app server. You will notice that the thread id of the worker thread on the app server side will vary quite a bit, since these threads are supplied from some pool of threads that Tomcat 7 manages. You will see very few thread ids in the calls to the complex servlet; more on this in the section below.

### Complex example

In the complex asynchronous servlet example, there are some major changes from the simple, notably:

  1. The complex servlet manages it’s own thread pool using a fixed thread pool executor. By passing a servlet config init param, you can specify what this is using an annotation. In the code, this is set to 3.

  2. The first 4 requests that are handled result in unexpected errors, just to show what happens when unhandled exceptions are generated in the `service()`.

  3. The long running task that’s performed takes a random amount of time up to a maximum of 5 seconds. The timeout value assigned to the AsyncContext is 60 seconds. This results in the last 20 or so requests (from the client test console app), all end up causing timeout errors, since there are only 3 server threads that are actually processing the 100 requests that are made concurrently.

  4. The `AsyncContext` listener actually has to call `AsyncContext.complete()`, when a timeout condition is detected by Tomcat 7, and it invokes the listener.

  5. Once a timeout condition does occur, Tomcat 7 will invalidate the `HttpRequest` and `HttpResponse` objects contained in the `AsyncContext`. This is a signal to the long running task that it’s `AsyncContext` has already been invalidated. This is why there is a check to see if it’s null or not, before writing the response via the `AsyncContext` in the long running task. This is something to keep in mind. When a timeout does happen, the long running task will probably be unaware of this, and must check to see if the request and response objects are null. If they are null, this means that the long running task should probably terminate itself, since the response has already been sent to the client via the `AsyncContext` listener (if one was assigned) or Tomcat 7 itself.

```java
@javax.servlet.annotation.WebServlet(
    // servlet name
    name = "complex",
    // servlet url pattern
    value = {"/complex"},
    // async support needed
    asyncSupported = true,
    // servlet init params
    initParams = {
        @WebInitParam(name = "threadpoolsize", value = "3")
    }
)
public class ComplexAsyncServlet extends HttpServlet {
 
public static final AtomicInteger counter = new AtomicInteger(0);
public static final int CALLBACK_TIMEOUT = 60000;
public static final int MAX_SIMULATED_TASK_LENGTH_MS = 5000;
 
/** executor svc */
private ExecutorService exec;
 
/** create the executor */
public void init() throws ServletException {
 
  int size = Integer.parseInt(
      getInitParameter("threadpoolsize"));
  exec = Executors.newFixedThreadPool(size);
 
}
 
/** destroy the executor */
public void destroy() {
 
  exec.shutdown();
 
}
 
/**
 * Spawn the task on the provided {@link #exec} object.
 * This limits the max number of threads in the
 * pool that can be spawned and puts a ceiling on
 * the max number of threads that can be used to
 * the init param "threadpoolsize".
 */
public void service(final ServletRequest req, final ServletResponse res)
    throws ServletException, IOException {
 
  // create the async context, otherwise getAsyncContext() will be null
  final AsyncContext ctx = req.startAsync();
 
  // set the timeout
  ctx.setTimeout(CALLBACK_TIMEOUT);
 
  // attach listener to respond to lifecycle events of this AsyncContext
  ctx.addListener(new AsyncListener() {
    /** 
    * complete() has already been called on the async context, 
    * nothing to do 
    */
    public void onComplete(AsyncEvent event) throws IOException { }
    /** timeout has occured in async task... handle it */
    public void onTimeout(AsyncEvent event) throws IOException {
      log("onTimeout called");
      log(event.toString());
      ctx.getResponse().getWriter().write("TIMEOUT");
      ctx.complete();
    }
    /** 
    * THIS NEVER GETS CALLED - error has occured in async task... 
    * handle it 
    */
    public void onError(AsyncEvent event) throws IOException {
      log("onError called");
      log(event.toString());
      ctx.getResponse().getWriter().write("ERROR");
      ctx.complete();
    }
    /** async context has started, nothing to do */
    public void onStartAsync(AsyncEvent event) throws IOException { }
  });
 
  // simulate error - this does not cause onError - causes network 
  // error on client side
  if (counter.addAndGet(1) < 5) {
    throw new IndexOutOfBoundsException("Simulated error");
  }
  else {
    // spawn some task to be run in executor
    enqueLongRunningTask(ctx);
  }
 
 
}
 
/**
 * if something goes wrong in the task, it simply causes timeout 
 * condition that causes the async context listener to be invoked
 * (after the fact)
 * <p/>
 * if the {@link AsyncContext#getResponse()} is null, that means 
 * this context has already timedout (and context listener has 
 * been invoked).
 */
private void enqueLongRunningTask(final AsyncContext ctx) {
 
  exec.execute(new Runnable() {
    public void run() {
 
      try {
 
        // simulate random delay
        int delay = new Random().nextInt(MAX_SIMULATED_TASK_LENGTH_MS);
        Thread.currentThread().sleep(delay);
 
        // response is null if the context has already timedout
        // (at this point the app server has called the listener already)
        ServletResponse response = ctx.getResponse();
        if (response != null) {
          response.getWriter().write(
              MessageFormat.format(
                  "<h1>Processing task in bgt_id:[{0}], delay:{1}</h1>",
                  Thread.currentThread().getId(), delay)
          );
          ctx.complete();
        }
        else {
          throw new IllegalStateException(
                  "Response object from context is null!");
        }
      }
      catch (Exception e) {
        log("Problem processing task", e);
        e.printStackTrace();
      }
 
    }
  });
}
 
}
```

The client code is the same one used to test the simple servlet. It in fact calls both of these servlets in the same `main()` method and gets responses from each of them.

When you run the client console app, which spawns 100 concurrent requests to the complex servlet, you will notice a few things:

  1. The complex servlet never uses more than 3 threads to process all these 100 requests that come in concurrently.

  2. The time for each response by the complex servlet can take up to 5 seconds, during which time about 20% of the incoming requests timeout (since the timeout period is set to 60 seconds, and all the requests come in at the same time and are queued for processing). Even though a 100 requests come in at once, only 3 are concurrently processed. However, even after the timeout condition is handled by the `AsyncContext` listener (and the client is sent an error message and `complete()` is called), the server `Runnables` continue to execute and error out. This is just something to keep in mind. Even though the timeout has been processed, those background tasks are still being executed and are consuming CPU and memory. You have to do something to detect such conditions in your code if you don’t want this to happen and terminate your execution manually (Java does not have preemptive multithreading, only cooperative).

  3. When the complex servlet errors out for the first 4 requests, these generate network exceptions on the client side.

## To async or not to async

Overall, the API is pretty straightforward to use, assuming that you are familiar with asynchronous processing in the first place. However, if you are not familiar with asynchronous processing, then this business of callbacks can be quite confusing and daunting. Additionally Tomcat 7 and Servlet API 3.0 make it easier to configure servlets using annotations. There are other cool features in 3.0 that I haven’t covered in this tutorial, like loading servlets programmatically.
