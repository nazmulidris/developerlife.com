---
author: Nazmul Idris
date: 2021-07-02 14:00:00+00:00
excerpt: |
  This handbook will use TypeScript to take you thru using Node.js. IDEA Ultimate / Webstorm project
  files are provided. This handbook is written as a reference. You can easily jump to the section 
  that is relevant to you or read them in any order that you like.
layout: post
title: "Node.js (v16.3.0) Handbook using TypeScript (v4.3.4)"
categories:
  - TypeScript
  - Node.js
  - Web
  - Server
---

<img class="post-hero-image" src="{{ 'assets/nodejs-ts-handbook.svg' | relative_url }}"/>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Node.js (v16.3.0) Handbook using TypeScript (v4.3.4)](#nodejs-v1630-handbook-using-typescript-v434)
- [Node.js installation on Linux (using brew)](#nodejs-installation-on-linux-using-brew)
- [Node.js project setup using IDEA](#nodejs-project-setup-using-idea)
- [Node.js threading model](#nodejs-threading-model)
  - [Overview](#overview)
  - [Event loop](#event-loop)
  - [Worker threads API for JS code](#worker-threads-api-for-js-code)
  - [Streaming and high performance JSON APIs](#streaming-and-high-performance-json-apis)
  - [libuv and worker threads](#libuv-and-worker-threads)
  - [N-API for native addons](#n-api-for-native-addons)
  - [Kotlin Native and C interop](#kotlin-native-and-c-interop)
- [Message Queue and ES6 Job Queue](#message-queue-and-es6-job-queue)
  - [Message Queue and setTimeout(), setImmediate() - execute at next tick](#message-queue-and-settimeout-setimmediate---execute-at-next-tick)
  - [process.nextTick() - execute at the end of this tick](#processnexttick---execute-at-the-end-of-this-tick)
  - [ES6 Job Queue (for Promises)](#es6-job-queue-for-promises)
- [TypeScript and JavaScript language](#typescript-and-javascript-language)
  - [Promises, async, await](#promises-async-await)
  - [Use strict=true in tsconfig.json options](#use-stricttrue-in-tsconfigjson-options)
  - [Use unknown over any](#use-unknown-over-any)
  - [User defined type guards](#user-defined-type-guards)
  - [never "bottom" type](#never-bottom-type)
  - [TypeScript JSDocs](#typescript-jsdocs)
  - [this keyword and Kotlin scoping functions](#this-keyword-and-kotlin-scoping-functions)
  - [Callable interfaces and implementations in TypeScript](#callable-interfaces-and-implementations-in-typescript)
- [Testing with Jest](#testing-with-jest)
  - [Setting up Jest and TypeScript](#setting-up-jest-and-typescript)
    - [Step 1 - Install Jest and types](#step-1---install-jest-and-types)
    - [Step 2 - Create a new jest.config.ts file](#step-2---create-a-new-jestconfigts-file)
    - [Step 3 - Create test files](#step-3---create-test-files)
- [User input and output via stdin, stdout](#user-input-and-output-via-stdin-stdout)
  - [Global console object](#global-console-object)
  - [Console class (and simple logging)](#console-class-and-simple-logging)
  - [readline from (global) console](#readline-from-global-console)
    - [FP example using question (w/out using "line" event)](#fp-example-using-question-wout-using-line-event)
    - [OOP example using "line" event (w/out using question)](#oop-example-using-line-event-wout-using-question)
- [Buffer](#buffer)
- [Events](#events)
- [Files](#files)
- [Modules](#modules)
- [OS, streams, process, network, etc.](#os-streams-process-network-etc)
  - [OS](#os)
  - [Process](#process)
  - [Streams, backpressure, pipes, files](#streams-backpressure-pipes-files)
    - [pipe](#pipe)
    - [pipeline, transform stream, and errors](#pipeline-transform-stream-and-errors)
  - [Child process](#child-process)
    - [Deep dive into spawn()](#deep-dive-into-spawn)
      - [Example 1 - spawn a child process to execute a command](#example-1---spawn-a-child-process-to-execute-a-command)
      - ["stdio" streams for getting input to and output from child process commands](#stdio-streams-for-getting-input-to-and-output-from-child-process-commands)
      - [Example 2 - pipe process.stdin into child process command](#example-2---pipe-processstdin-into-child-process-command)
      - [Example 3 - pipe the output of one child process command into another one](#example-3---pipe-the-output-of-one-child-process-command-into-another-one)
      - [Example 4 - ugly code to redirect the output of one child process command to another one](#example-4---ugly-code-to-redirect-the-output-of-one-child-process-command-to-another-one)
    - [Killing or aborting a child process](#killing-or-aborting-a-child-process)
    - [Brief exploration of exec()](#brief-exploration-of-exec)
    - [Brief exploration of fork()](#brief-exploration-of-fork)
    - [Example of replacing a fish script using spawn](#example-of-replacing-a-fish-script-using-spawn)
- [Publishing npm packages](#publishing-npm-packages)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Node.js (v16.3.0) Handbook using TypeScript (v4.3.4)

This handbook will use TypeScript to take you thru using Node.js. The table of contents has a list
of topics that are covered in this handbook. You can easily jump to the section that is relevant to
you or read them in any order that you like.

Additionally, here are some great resources to use a reference for your journey into Node.js.

- [Node.js: The complete course for beginners][i-1]
- [Tutorials][i-2]
- [Official docs][i-3]

[i-1]: https://www.educative.io/courses/learn-nodejs-complete-course-for-beginners/xV5YWR3DGq3
[i-2]: https://jscomplete.com/learn/node-beyond-basics/child-processes
[i-3]: https://nodejs.org/api
[gh-repo]: https://github.com/nazmulidris/ts-scratch/tree/main/nodejs-beginner-course

## Node.js installation on Linux (using brew)

You can get the latest version of Node.js using [`brew`](https://brew.sh/), which is available on
Linux and MacOS. Once you have `brew` installed, simply run `brew install node`.

> Note that on Linux, when using `apt` instead of `brew`, the package is called `nodejs` and not
> `node`! So the `brew` package name is actually the "right" one.

Here are some differences when using `brew` vs `apt`.

1. Unlike `apt`, the binaries for any global npm packages that you install will end up in
   `/home/linuxbrew/.linuxbrew/bin/`.
2. Also you won't need to use `sudo` anymore to install npm packages globally!

In IDEA / Webstorm if you use Prettier plugin or just to enable Node.js support, you might have to
provide the location of some of the things that you have installed above. The instructions below are
handy when configuring this.

I usually install the following packages globally after installing node using
`npm i -g prettier doctoc typescript ts-node ts-node-dev`, so to follow along, I recommend doing the
same.

I also create a symlink for these binaries in `/usr/local/bin/` for convenience. For a globally
installed npm package `<some-npm-package>`, here's the pattern:

- Symlinked binary is at `cd /usr/local/bin ; sudo ln -s (which <some-npm-package>)`
- Actual binary is at `/home/linuxbrew/.linuxbrew/bin/<some-npm-package>`

As an example, let's use `prettier` package.

1. The `prettier` binary (symlink) is available at `/usr/local/bin/prettier`.
2. The actual binary is located at `/home/linuxbrew/.linuxbrew/bin/prettier`.

If you run into issue w/ IDEA not picking up your `$PATH` variable contents (for `linuxbrew`) in
your File Watchers, you might need to add the following lines to your `~/.profile` file, so that
GNOME session can pick it up when your desktop session starts (vs when this is set in your
terminal/shell initialization script).

```shell
# Set PATH so it includes linuxbrew for all child processes spawned by the Gnome shell.
# - https://superuser.com/a/398881/1102870
# - https://askubuntu.com/a/356973/872482
# - https://help.ubuntu.com/community/EnvironmentVariables
if [ -d "/home/linuxbrew/.linuxbrew" ] ; then
    PATH="/home/linuxbrew/.linuxbrew/bin:$PATH"
fi
```

## Node.js project setup using IDEA

IDEA Ultimate / Webstorm project files are provided in [this github repo][gh-repo]. You can clone
the repo and tell IDEA / Webstorm to open the sub-folder `nodejs-beginner-course` and not the top
level folder `ts-scratch`. You can open the project to try out the code that is shown in this
handbook.

These are the steps that I followed to create this project.

1. Use IDEA (Ultimate or Webstorm) create a new Node.js project.
2. Use the `ts-node-dev` Node.js interpreter (not the default), which is located in
   `/usr/local/bin/ts-node/dev` (via the symlink created in the previous section).
3. In the `package.json` add the following dev dep (`npm i --save-dev @types/node@latest`). Other
   dev deps will be added when you start importing various modules in your code.
4. When creating a `.ts` file, in order to make it executable, you can do the following:
5. Add `#!/usr/bin/env ts-node` to the top of the `.ts` file.
6. Mark the file executable using `chmod +x *.ts`.
7. Add a
   [`tsconfig.json`](https://github.com/nazmulidris/ts-scratch/blob/main/nodejs-beginner-course/tsconfig.json)
   file which enables strict mode, and dumps compiled output to a `build` folder. Also compile
   TypeScript files located in the `src` folder and its sub-folders only.
   ```json5
   {
     exclude: ["node_modules"],
     include: ["./src/**/*"],
     compilerOptions: {
       strict: true,
       module: "CommonJS",
       target: "ES6",
       sourceMap: true,
       outDir: "build", // More info https://stackoverflow.com/a/49687441/2085356
     },
   }
   ```

## Node.js threading model

### Overview

- [Course link](https://www.educative.io/courses/learn-nodejs-complete-course-for-beginners/RMoNJwAKR2q).
- This article describes how the
  [main thread and thread pool (worker pool) of `k` Worker threads](https://nodejs.org/en/docs/guides/dont-block-the-event-loop/)
  works in Node.js.

Node.js has two types of threads: one Event Loop and `k` Workers.

1. The Event Loop is responsible for JavaScript callbacks and non-blocking I/O, and
2. a Worker (out of the pool of `k`) executes tasks corresponding to C++ code that completes an
   asynchronous request, including blocking I/O and CPU-intensive work.

Both types of threads work on no more than one activity at a time. If any callback or task takes a
long time, the thread running it becomes blocked. If your application makes blocking callbacks or
tasks, this can lead to degraded throughput (clients/second) at best, and complete denial of service
at worst.

To write a high-throughput, more DoS-proof web server, you must ensure that on benign and on
malicious input, neither your Event Loop nor your Workers will block.

### Event loop

- [Node.js docs on event loop, workers, and best practices to avoid freezes](https://nodejs.org/en/docs/guides/dont-block-the-event-loop/)

  - Best practices from doc above:

    - Avoid "vulnerable" regex.
    - Avoid synchronous versions of Node.js APIs for encryption, compression, file system, and child
      process.
    - Avoid using JSON parse and stringify for really large objects (these operations are very slow)
      . Libraries [exist](#streaming-and-high-performance-json-apis) to handle these performance
      issues.
    - Avoid variable time complexity callbacks, try and keep them `O(n)`. Here are some strategies
      to accomplish this.

      1. _Partitioning_: You can use `setImmediate` and chunk the long operation into smaller
         pieces.
      2. _Offloading_: The only drawback here is that the main thread is in a different "namespace"
         (JavaScript state of your application) than a worker thread, so you have to serialize &
         deserialize any objects that are passed between them. Also, you must also be careful about
         understanding whether your long running operations are CPU intensive or IO intensive, since
         they both have to be approached differently. However, if your app relies heavily on complex
         calculations, you should think about whether Node.js is really a good fit. Node.js excels
         for I/O-bound work, but for expensive computation it might not be the best option.

      - You have [**two choices**](#worker-threads-api-for-js-code) to run CPU intensive JS code in
        the thread pool without writing a C/C++ addon.
      - You can create a C/C++ addon using [N-API](https://nodejs.org/api/n-api.html).

- [Video on how the event loop works](https://youtu.be/P9csgxBgaZ8)

### Worker threads API for JS code

Without writing a [C/C++ addon using N-API](#n-api-for-native-addons), you can use either of the
following.

- You can even use the **new**
  [`Worker Threads` API in Node.js 15](https://nodejs.org/docs/latest/api/worker_threads.html) to
  run CPU intensive JS code in the thread pool without writing a C/C++ addon.
- You can use the new [WebWorker Threads library](https://www.npmjs.com/package/webworker-threads)
  to run the JS code in the thread pool without writing a C/C++ addon.

### Streaming and high performance JSON APIs

- You can use [stream APIs](https://www.npmjs.com/package/JSONStream) for JSON.
- Or you can use [async versions of JSON parsing APIs](https://www.npmjs.com/package/bfj).

### libuv and worker threads

`libuv` is a multiplatform C library for async IO based on event loops, which exposes a general task
submission API. Node.js uses the thread pool to handle "expensive" tasks.

This includes I/O for which an OS does not provide a non-blocking version
([DNS](https://tinyurl.com/orjpz3t), and [file system](https://tinyurl.com/yz87vob9)), as well as
particularly CPU-intensive tasks ([Zlib](https://tinyurl.com/ye5kqjny) and
[Crypto](https://tinyurl.com/n3moqwk)).

User defined [C/C++ addons](https://nodejs.org/api/addons.html) can also be run in this thread pool.
However you should write these addons using the [`N-API`](#n-api-for-native-addons).

You have [two choices](#worker-threads-api-for-js-code) to run CPU intensive JS code in the thread
pool without writing a C/C++ addon.

- [Wikipedia](https://en.wikipedia.org/wiki/Libuv)
- [Library website](http://docs.libuv.org/en/v1.x/)
- [Design docs](http://docs.libuv.org/en/v1.x/design.html)
- [Threadpool API](http://docs.libuv.org/en/v1.x/threadpool.html)
- [Differences w/ browser which uses `libevent`](https://blog.insiderattack.net/javascript-event-loop-vs-node-js-event-loop-aea2b1b85f5c)

### N-API for native addons

- [Video](https://youtu.be/-Oniup60Afs)
- [GitHub repo](https://github.com/nodejs/node-addon-api)
- [Tutorial on building Node.js native addons in 2020](https://nodejs.medium.com/building-modern-native-add-ons-for-node-js-in-2020-cd3992c68e0)
- [Tutorial on using the N-API to create an addon in C/C++](https://tinyurl.com/yecfnkf9)

### Kotlin Native and C interop

- **Hypothesis** - It may be possible to use Kotlin Native to generate C interoperable code in order
  to write some native addons for Node.js.
- [KT and C interop](https://kotlinlang.org/docs/native-c-interop.html#basic-interop-types)
- [Random repo I found on github that claims to do this](https://github.com/datkt/node-addon-example)

## Message Queue and ES6 Job Queue

### Message Queue and setTimeout(), setImmediate() - execute at next tick

Read the official Node.js docs about
[event loop and message queue](https://nodejs.dev/learn/the-nodejs-event-loop#the-message-queue:~:text=The%20Message%20Queue,-When).

When `setTimeout(()=>{}, 0)` is called, the Browser or Node.js starts the timer. Once the timer
expires, in this case immediately as we put `0` as the timeout, the callback function is put in the
**Message Queue**.

- The Message Queue is also where user-initiated events like click or keyboard events, or fetch
  responses are queued before your code has the opportunity to react to them. Or also DOM events
  like `onLoad`.
- The loop gives priority to the call stack, and it first processes everything it finds in the call
  stack, and once there's nothing in there, it goes to pick up things in the message queue.
- We don't have to wait for functions like `setTimeout`, `fetch` or other things to do their own
  work, because they are provided by the browser, and they live on their own threads. For example,
  if you set the `setTimeout` timeout to 2 seconds, you don't have to wait 2 seconds - the wait
  happens elsewhere (in the worker thread pool).

A `setTimeout()` callback with a `0ms` delay is very similar to `setImmediate()`. The execution
order will depend on various factors, but they will be both run in the next iteration of the event
loop.

### process.nextTick() - execute at the end of this tick

Read the official Node.js docs about
[process.nextTick()](https://nodejs.dev/learn/understanding-process-nexttick#link-nodejs-with-typescript:~:text=When%20we%20pass%20a%20function%20to,the%20next%20event%20loop%20tick%20starts%3A).

Every time the event loop takes a full trip, we call it a `tick`. When we pass a function to
`process.nextTick()`, we instruct the engine to invoke this function at the end of the current
operation, before the next event loop tick starts. Here's an example.

```javascript
process.nextTick(() => {
  /* Do something. */
})
```

- The event loop is busy processing the current function code.
- When this operation ends, the JS engine runs all the functions passed to `nextTick` calls during
  that operation.
- It's the way we can tell the JS engine to process a function asynchronously (after the current
  function), but as soon as possible, not queue it. Calling `setTimeout(() => {}, 0)` will execute
  the function at the end of next tick, **much later** than when using `nextTick()` which
  prioritizes the call and executes it just **before** the beginning of the next tick.

Use `nextTick()` when you want to make sure that in the next event loop iteration that code is
already executed.

### ES6 Job Queue (for Promises)

Read the official Node.js docs about the
[ES6 job queue](https://nodejs.dev/learn/the-nodejs-event-loop#es6-job-queue:~:text=ES6%20Job%20Queue).

ECMAScript 2015 introduced the concept of the Job Queue, which is used by Promises (also introduced
in ES6/ES2015). It's a way to execute the result of an async function as soon as possible, rather
than being put at the end of the call stack.

Promises that resolve before the current function ends will be executed right after the current
function.

Using the analogy of a roller coaster ride at an amusement park:

- The **message queue** puts you at the back of the queue, behind all the other people, where you
  will have to wait for your turn.
- The **job queue** is the "fast pass" ticket that lets you take another ride right after you
  finished the previous one.

Here's an example.

```javascript
const bar = () => console.log("bar")

const baz = () => console.log("baz")

const foo = () => {
  console.log("foo")
  setTimeout(bar, 0)
  new Promise((resolve, reject) => resolve("should be right after baz, before bar")).then(
    (resolve) => console.log(resolve)
  )
  baz()
}

foo()
```

![Call stack for the code above](https://nodejs.dev/907f18a0288ad303ad59c035397a6f7e/call-stack-third-example.svg)

## TypeScript and JavaScript language

### Promises, async, await

It is relatively simple to reason about using promises, as a way to eliminate callback hell. It is
also relatively simple to
["promisify"](https://nodejs.dev/learn/understanding-javascript-promises#creating-a-promise:~:text=A%20more%20common%20example%20you%20may,and%20have%20it%20return%20a%20promise%3A)
existing callback based APIs.

> Here are some good reference links.
>
> - [Official Node.js docs on Promises](https://nodejs.dev/learn/understanding-javascript-promises)
> - [SO thread about when a Promise actually executes](https://stackoverflow.com/a/42118995/2085356)
> - [Top level await in Node.js](https://nodejs.dev/learn/modern-asynchronous-javascript-with-async-and-await)
> - [ECMA promise (executor) official specs](https://262.ecma-international.org/6.0/#sec-promise-executor)

However, on the other side of the coin, when returning a promise, how does it all work? When does
the promise execute? Here's an example to illustrate this.

```typescript
#!/usr/bin/env ts-node

type ResolveFnType<T> = (value: T) => void
type RejectFnType = (reason?: any) => void
type ExecutorFnType<T> = (resolveFn: ResolveFnType<T>, rejectFn?: RejectFnType) => void

// Can also write this as a named function.
// function myExecutorFn(resolveFn: ResolveFnType<string>) {
const myExecutorFn: ExecutorFnType<string> = (resolveFn: ResolveFnType<string>) => {
  resolveFn("hello world!")
}

function createMyPromise(): Promise<string> {
  const promise: Promise<string> = new Promise<string>(myExecutorFn)
  return promise
}

function main() {
  const promise: Promise<string> = createMyPromise()
  promise.then((value: string) => {
    console.log(value)
  })
}

main()
```

After running this code in the debugger w/ breakpoints set on every line in `createMyPromise()` we
learn:

1. The `Promise` takes an `executor`, which is the function that actually does the work of resolving
   or rejecting the promise. In this case, `myExecutorFn()`.
2. This `executor` is run at the moment at which the `Promise` is instantiated using `new`. In this
   simple example, once `new Promise(myExecutorFn)` is called, it then calls the `myExecutorFn`
   function before returning a `promise` object.

Here's a more sophisticated example w/ timings and even using `await`.

```typescript
#!/usr/bin/env ts-node

import * as chalk from "chalk"

type ResolveFnType<T> = (value: T) => void
type RejectFnType = (reason?: any) => void
type ExecutorFnType<T> = (resolveFn: ResolveFnType<T>, rejectFn?: RejectFnType) => void

// https://nodejs.org/api/process.html#process_process_hrtime_time
let startTime: [number, number] = process.hrtime()

function timeDiffMs(): number {
  const NS_PER_MS = 1e6
  return process.hrtime(startTime)[1] / NS_PER_MS
}

function handleImmediateExecutionPromise() {
  // Can also write this as a named function.
  // function myExecutorFn(resolveFn: ResolveFnType<string>) {
  const myExecutorFn: ExecutorFnType<string> = (resolveFn: ResolveFnType<string>) => {
    resolveFn("hello world!")
  }

  new Promise<string>(myExecutorFn).then((value) =>
    console.log(chalk.red(`immediate: ${value}, actual delay ${timeDiffMs()} ms`))
  )
}

function handleDeferredExecutionPromise(delayMs: number) {
  const myExecutorFn: ExecutorFnType<string> = (resolveFn) => {
    setTimeout(() => {
      resolveFn(`hello world! after ${delayMs} ms`)
    }, delayMs)
  }

  new Promise<string>(myExecutorFn).then((value) =>
    console.log(chalk.green(`using then(): ${value}, actual delay ${timeDiffMs()} ms`))
  )
}

async function handleDeferredExecutionPromiseWithAwait(delayMs: number) {
  const myExecutorFn: ExecutorFnType<string> = (resolveFn) =>
    setTimeout(() => resolveFn(`hello world! after ${delayMs} ms`), delayMs)

  const value = await new Promise(myExecutorFn)
  console.log(chalk.blue(`using await: ${value}, actual delay ${timeDiffMs()} ms`))
}

async function main() {
  startTime = process.hrtime()
  console.log(`Set startTime: ${startTime}, actual delay calculated from this timestamp`)

  handleImmediateExecutionPromise()
  handleDeferredExecutionPromise(500)

  console.log(chalk.yellow("before await!"))
  await handleDeferredExecutionPromiseWithAwait(200)

  console.log(chalk.yellow("end!"))
}

main()
```

Here's another example of using top level `await` in a Node.js program, while mixing and matching
the use of `async`, `await`, and promises.

```typescript
class SpawnCProcToRunLinuxCommandAndGetOutput {
  readonly cmd = "find"
  readonly args = [`${process.env.HOME}`, "-type", "f"]

  run = async (): Promise<void> => {
    const child: ChildProcess = spawn(this.cmd, this.args)

    return new Promise<void>((resolveFn, rejectFn) => {
      child.on("exit", function (code, signal) {
        console.log(`Child process exited with code ${code} and signal ${signal}`)
        resolveFn()
      })
      child.stdout?.on("data", (data: Buffer) => {
        console.log(`Output : ${data.length}`)
      })
      child.stderr?.on("data", (data) => {
        rejectFn()
        console.log(`Error: ${data}`)
      })
    })
  }
}

const main = async (): Promise<void> => {
  console.log("start!")
  await new SpawnCProcToRunLinuxCommandAndGetOutput().run()
  console.log("done!")
}

main().catch(console.error)
```

Notes on the code above:

- The call to `main()` at the very bottom of the snippet actually calls an function that returns a
  `Promise`. The `catch()` section actually handles any top level exceptions that are thrown.
- In the `main()`, which is an `async` function, which returns a `Promise`, `await` is used to wait
  for the call to `run()` to actually complete. This is where promises and `async` / `await` are
  used together.
- In `run()` a `Promise` is created (which is returned by this method) which actually is fulfilled
  when the child process actually completes, or is rejected when it encounters an error.

### Use strict=true in tsconfig.json options

Always set [`"strict"=true`](https://www.typescriptlang.org/tsconfig#strict) in your
`tsconfig.json`.

### Use unknown over any

Because it does not propagate:

```javascript
function foo1(bar: any) {
  const a: string = bar // no error
  const b: number = bar // no error
  const c: { name: string } = bar // no error
}

function foo2(bar: unknown) {
  const a: string = bar // 🔴 Type 'unknown' is not assignable to type 'string'.(2322)
  const b: number = bar // 🔴 Type 'unknown' is not assignable to type 'number'.(2322)
  const c: { name: string } = bar // 🔴 Type 'unknown' is not assignable to type '{ name: string; }'.(2322)
}
```

### User defined type guards

A guard is not a type, but a mechanism that narrows types.

Here are some examples of built-in type guards.

1. `typeof` guard - This only works for JS primitive types that are checked at runtime (string,
   number, undefined, null, Boolean, and Symbol). It does not work for interfaces because that
   information is erased at runtime.

   ```typescript
   class Properties {
     width: number = 0

     setWidth(width: number | string) {
       if (typeof width === "number") {
         this.width = width
       } else {
         this.width = parseInt(width)
       }
     }
   }
   ```

2. `instanceof` guard - This works with classes, but not interfaces. Type information for classes is
   retained at runtime by JS, but not interfaces.

   ```typescript
   class Person {
     constructor(public name: string) {}
   }

   function greet(obj: any) {
     if (obj instanceof Person) {
       console.log(obj.name)
     }
   }
   ```

3. A custom type guard is a Boolean-returning function that can additionally assert something about
   the type of its parameter. You can create user defined type guards to test if an object has the
   shape of an interface.

- [Docs](https://www.typescriptlang.org/docs/handbook/advanced-types.html#using-type-predicates)
- [Course](https://www.educative.io/courses/advanced-typescript-masterclass/g77AxgkEQG3#overview)

The following code does **not work**.

```typescript
interface Article {
  title: string
  body: string
}

function doSomething(bar: unknown) {
  const title: string = bar.title // 🔴 Error!
  const body: number = bar.body // 🔴 Error!
  console.log(title, body)
}

doSomething({ title: "t", body: "b" })
doSomething({ foo: "t", bar: "b" })
```

**First** try at using user defined type guards. It doesn't narrow automatically!

```typescript
interface Article {
  title: string
  body: string
}

function isArticle(param: unknown): boolean {
  const myParam = param as Article
  // 👍 One way of writing this without using string literals.
  if (myParam.title != undefined && myParam.body != undefined) {
    // The following works too.
    // if ("title" in myParam && "body" in myParam) {
    return true
  }
  return false
}

function doSomething(bar: unknown) {
  if (isArticle(bar)) {
    // 👎 You have to cast bar to Article as it does not narrow automatically.
    const article = bar as Article
    console.log("Article interface type: ", article.title, article.body)
  } else {
    console.log("unknown type", bar)
  }
}

doSomething({ title: "t", body: "b" })
doSomething({ foo: "t", bar: "b" })
```

**Second** try at writing this. Have to use string literals for the properties!

```typescript
interface Article {
  title: string
  body: string
}

function isArticle(param: any): param is Article {
  // 👎 You lose the ability to autocomplete title and body (as shown above), string literals are
  // needed, which could be a problem with keeping things in sync.
  return "title" in param && "body" in param
}

function doSomething(bar: unknown) {
  if (isArticle(bar)) {
    // 👍 You don't have to cast bar to Article! It is automatically narrowed!
    console.log("Article interface type: ", bar.title, bar.body)
  } else {
    console.log("unknown type", bar)
  }
}

doSomething({ title: "t", body: "b" })
doSomething({ foo: "t", bar: "b" })
```

**Third** and best try, which solves both problems with previous tries.

```typescript
interface Article {
  title: string
  body: string
}

function isArticle(param: any): param is Article {
  const myParam = param as Article
  return (
    myParam.title != undefined &&
    myParam.body != undefined &&
    typeof myParam.title == "string" &&
    typeof myParam.body == "string"
  )
}

function doSomething(bar: unknown) {
  if (isArticle(bar)) {
    console.log("Article interface type: ", bar.title, bar.body)
  } else {
    console.log("unknown type", bar)
  }
}

doSomething({ title: "t", body: "b" })
doSomething({ foo: "t", bar: "b" })
```

### never "bottom" type

1. `never` is a bottom type (which is `Nothing` in Kotlin).
2. The opposite of "top" type like `Object` in Java, and `any` in TypeScript or Kotlin.

Here's an example.

```typescript
function foo(param: boolean) {
  if (param) {
  } else if (!param) {
  } else {
    // WTF?! param is never and this code is unreachable!
    if (param) {
    }
  }
}
```

Another example.

```typescript
/* @throws(Error) */
function getContentFromRoute(parsedUrl: ParsedUrl, routes: Array<Route>): Content {
  const matchingRoute: Optional<Route> = routes.find(
    (it: Route) => it.pathname === parsedUrl.pathname
  )

  this.error("bam! 🎇 🧯 🚒 💣")

  // This line is unreachable.
  return matchingRoute?.generateContentFn(parsedUrl.query) ?? this.error("no route found")
}

function error(message: string): never {
  throw new Error(message)
}
```

### TypeScript JSDocs

Here's more information on
[TypeScript specific JSDocs](https://www.typescriptlang.org/docs/handbook/jsdoc-supported-types.html).

Here are some examples.

```typescript
/**
 * @param contextObject value of `it`
 * @param block lambda that accepts `it`
 * @return contextObject return the contextObject that is passed
 */
export const _also = <T>(contextObject: T, block: Receiver<T>): T => {
  block(contextObject)
  return contextObject
}

/**
 * @param contextObject value of `this`
 * @param lambda lambda that accepts `this`
 * @return contextObject return the result of the lambda
 */
export function _with<T, R>(contextObject: T, lambda: ImplicitReceiverWithReturn<T, R>): R {
  return lambda.blockWithReboundThis.bind(contextObject).call(contextObject)
}
```

### this keyword and Kotlin scoping functions

To understand advanced things about TypeScript, I decided to write the
[Kotlin scoping functions](https://kotlinlang.org/docs/scope-functions.html#function-selection)
(with, apply, let, run, etc) in TypeScript.

- [Sample code - Kotlin Scoping Functions](https://github.com/r3bl-org/r3bl-ts-utils/blob/main/src/kotlin-lang-utils.ts)
- [Sample code - Test for above](https://github.com/r3bl-org/r3bl-ts-utils/tree/main/src/__tests)

Here are some references:

- [Kotlin context and `this` rebinding](https://developerlife.com/2020/04/05/kotlin-dsl-intro/#context-and-rebinding-this)
- [TypeScript handling `this` parameters](https://www.typescriptlang.org/docs/handbook/functions.html#this-parameters)
- [TypeScript utility types for `this`](https://www.typescriptlang.org/docs/handbook/utility-types.html#thistypetype)
- [JavaScript `bind`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/call)
- [JavaScript `call`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/bind)

It is more complicated to handle "implicit" `this` scenario, since in TypeScript, there is no such
thing. So we use `this` explicitly but even so, in a given lambda rebinding `this` poses a
challenge. This is why I created an interface that describes the shape of an object which has a
function. And for this object, `this` can be bound to the `contextObject`. The `this` keyword then
works inside this object that is passed to `_with` and `_apply` shown below.

```typescript
interface ImplicitReceiver<T> {
  blockWithReboundThis: (this: T) => void
}

interface ImplicitReceiverWithReturn<T, R> {
  blockWithReboundThis: (this: T) => R
}

/**
 * @param contextObject value of `this`
 * @param lambda lambda that accepts `this`
 * @return contextObject return the contextObject that is passed
 */
export function _apply<T>(contextObject: T, lambda: ImplicitReceiver<T>): T {
  lambda.blockWithReboundThis.bind(contextObject).call(contextObject)
  return contextObject
}

/**
 * @param contextObject value of `this`
 * @param lambda lambda that accepts `this`
 * @return contextObject return the result of the lambda
 */
export function _with<T, R>(contextObject: T, lambda: ImplicitReceiverWithReturn<T, R>): R {
  return lambda.blockWithReboundThis.bind(contextObject).call(contextObject)
}
```

### Callable interfaces and implementations in TypeScript

More info:

- [Callable interface](https://basarat.gitbook.io/typescript/type-system/callable)
- [Implementing Callable interface in TypeScript](https://stackoverflow.com/questions/12769636/how-to-make-a-class-implement-a-call-signature-in-typescript)
- [Sample code - ColorConsole class and ColorConsoleIF interface in utils](https://github.com/r3bl-org/r3bl-ts-utils/blob/main/src/color-console-utils.ts)

```typescript
interface CallableIF {
  (text: string): string
}

const myCallableFn: CallableIF = (text: string) => "hello" + text

class MyCallableClass {
  // This is the method that actually ends up getting called.
  call(text: string): string {
    return "hello" + foo
  }

  // Factory method is actually what implements the callable interface.
  static create(): CallableIF {
    const instance = new MyClass()
    return Object.assign((text: string) => instance.call(text))
  }
}

const myObj = MyCallableClass.create()
console.log(myObj("foo"))
```

## Testing with Jest

Use Jest framework (made by Facebook). It is not tied to React development.

- [ts-jest](https://github.com/kulshekhar/ts-jest)
- [jest](https://jestjs.io/)
- [Getting started w/ Node.js and jest](https://jestjs.io/docs/getting-started)

1. Jest itself is built on top of Jasmine. Jest is fast, when compared to Karma (which is a test
   runner that uses a real browser and has to be paired w/ something like Jasmine for the actual
   test running).
2. Jest does not use a real DOM (it uses `js-dom`) which makes it much faster compared to Karma.
3. Given the speed of Jest, the huge developer adoption and support it has, along with its
   multiplatform testing capabilities (Vanilla JS, Node.js, React), and it works w/ React (via
   `ts-jest`), it is the testing platform of choice.

### Setting up Jest and TypeScript

It is a little complicated to set this up for TypeScript. The following instructions on the
[Jest getting started with TypeScript](https://jestjs.io/docs/getting-started#using-typescript) are
not complete.

#### Step 1 - Install Jest and types

Run the following to get Jest and its TypeScript bindings installed, along with `ts-test` which is a
plugin that allows Jest to work directly w/ TypeScript files.

```shell
npm i -D jest ts-jest @types/jest
```

#### Step 2 - Create a new jest.config.ts file

This is a very important step, since this `jest.config.ts` file (which can't be a `.js` file) will
tell Jest how to "deal" with TypeScript files. Once this is configured, everything else (running
tests from the command line using `jest` or IDEA "just work"). Remember that you won't actually run
`js-test` but use `jest` instead; `js-test` is just a plugin for `jest` which has be configured
correctly.

```typescript
export default {
  preset: "ts-jest", // Tell Jest to use `ts-jest` plugin.
  testEnvironment: "node", // Execution environment (can't be `ts-node`).
  testMatch: ["<rootDir>/**/*.test.ts"], // Test files must end in `*.test.ts`.
  testPathIgnorePatterns: ["/node_modules/"], // Don't search for tests inside `node_modules`.
}
```

For information on what each of these keys mean, check out
[Configuring Jest](https://jestjs.io/docs/configuration#testmatch-arraystring).

#### Step 3 - Create test files

Finally, you can create a `.test.ts` file. And then IDEA should be able to run it. Here's an
example.

```typescript
describe("my test suite", () => {
  it("a spec with an expectation", () => {
    expect(true).toBe(true)
  })

  it("another spec with a different expectation", () => {
    expect(false).toBe(false)
  })
})
```

To learn how to write tests using Jasmine, check out these links.

- [Jasmine Manual - writing tests using describe, it, spyOn, etc](https://jasmine.github.io/2.1/introduction)
- [Jasmine tutorial](https://howtodoinjava.com/javascript/jasmine-unit-testing-tutorial/)

## User input and output via stdin, stdout

### Global console object

There's a global `console` object that is configured to write to `process.stdout` and
`process.stderr`. The interesting thing is that you can pass an `Error` to `console.error()` in
order to get a stack trace. You can also use the `trace()` method. Here are examples.

```typescript
console.log("Hello World")
console.warn("This is a warning!")
console.error("This is an error")
console.error(new Error("🐛 This captures the stack trace here!"))
console.trace("🐛 This also captures the stack trace here!")
```

Another useful feature of console is `console.time(string)` and `console.timeEnd(string)`. The first
method starts a time (with the given string as key). A call to the second method with the same key
prints the elapsed time.

```typescript
const timerName = "For loop time"
console.time() // Does not print anything. Starts the timer.
for (let i = 0; i < 100; i++) {
  /* ... */
}
console.timeEnd(timerName) // Prints the time that has passed, eg "For loop time:0.123ms".
```

Yet another useful feature is the `console.table()` method which prints an array of objects that is
passed to it. Here's an example.

```typescript
console.table([
  { name: "john", age: 12 },
  { name: "jane", age: 15 },
])
```

Here's the output it produces.

```text
┌─────────┬─────────┬──────────┐
│ (index) │  Name   │ Age      │
├─────────┼─────────┼──────────┤
│    0    │ 'john'  │    12    │
│    1    │ 'jane'  │    15    │
└─────────┴─────────┴──────────┘
```

### Console class (and simple logging)

- [Sample code](src/basics/console-log-to-file.ts)

You can use the `Console` class to write to files, instead of using the global `console` object that
is tied to `process.stderr` and `process.stdout`. Here's an example of a simple logger that writes
errors to files.

```typescript
const fs = require("fs")
const { Console } = require("console")

const output = fs.createWriteStream("./stdout.log")
const errorOutput = fs.createWriteStream("./stderr.log")

const logger = new Console({ stdout: output, stderr: errorOutput })

const number = 5
logger.log("number:", number)
// In stdout.log: number 5
const code = 9
logger.error("error code:", code)
```

### readline from (global) console

- [Course](https://www.educative.io/courses/learn-nodejs-complete-course-for-beginners/gkj79gjxYo9)
- [Sample code](src/basics/cli-fp.ts)

The `readline` module needs an interface to work. This interface can be a file or the console. We
want to get input from the console and output some information on the console, via `readline`.

1. In Node.js, the `process` object has two properties that can help us:

- 👉 `stdout` for output - Prompts to the user are displayed via this.
- 👈 `stdin` for input - User input is captured via this.

2. We use the `createInterface` method to create a new `readline.Interface` instance that we can use
   to:

- First, prompt the user for input as well (via `question`).
- Second, read user input from the console (via callback to `question`).

3. Finally, when it is time to end the CLI, `close` must be called on the `readline.Interface`
   otherwise the Node.js process will be waiting on the console's `stdin` (even w/out being in the
   middle of executing the `question` method). That's just the way the Node.js
   [threading model works](#nodejs-threading-model).

#### FP example using question (w/out using "line" event)

The following are examples of functions to demonstrate the above. Here's a function that kicks off
the CLI Node.js sample.

```typescript
const main = async (argv: Array<string>) => {
  console.log(`Please type "${Messages.closeCommand}" or ${chalk.red("Ctrl+C")} to exit 🐾`)
  promptUserForInputViaConsoleInterface()
}
// https://nodejs.org/en/knowledge/command-line/how-to-parse-command-line-arguments/
main(process.argv.splice(2))
```

Here's a function that creates a `readline` interface connected to the console.

```typescript
function createReadlineConsoleInterface(): readline.Interface {
  const onCloseRequest = () => {
    console.log(chalk.red("Goodbye!"))
    consoleInterface.close()
  }
  const consoleInterface: readline.Interface = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  })
  consoleInterface.on("close", onCloseRequest)
  return consoleInterface
}

const ourConsoleInterface: readline.Interface = createReadlineConsoleInterface()
```

Here's a function that uses the `readline` console interface to prompt the user (via
`process.stdout`) for some input, and process their response (from `process.stdin`).

```typescript
enum Messages {
  closeCommand = "quit",
  userPrompt = "Type something",
}

type ConsoleInterfaceCallbackFn = (whatTheUserTyped: string) => void

function promptUserForInputViaConsoleInterface() {
  const processWhatTheUserTyped: ConsoleInterfaceCallbackFn = (whatTheUserTyped) =>
    userInputHandler(whatTheUserTyped.toLowerCase())
  ourConsoleInterface.question(chalk.green(`${Messages.userPrompt}: `), processWhatTheUserTyped)
}
```

Here's a function that processes what the user typed.

```typescript
function userInputHandler(userInput: string) {
  // closeCommand issued. Stop the program by shutting the waiter down.
  if (userInput === Messages.closeCommand) {
    ourConsoleInterface.close()
    return
  }
  console.log(`🚀 You typed: ${chalk.yellow(userInput)}`)
  promptUserForInputViaConsoleInterface()
}
```

#### OOP example using "line" event (w/out using question)

Instead of using the `question` method, we can simply rely on the `line` event, just like we rely on
the `close` event (which is fired when the user presses `Ctrl+C`).

Here's an OOP version of the code above that uses this pattern (I think the code is much cleaner
w/out using `question`).

```typescript
class UIStrings {
  public static readonly closeCommand = "quit"
  public static readonly userPrompt = `> Please type "${UIStrings.closeCommand}" or ${chalk.red(
    "Ctrl+C"
  )} to exit 🐾`
}

class CommandLineInterface {
  private readonly consoleInterface: readline.Interface

  constructor(message: string) {
    this.consoleInterface = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    })
    this.consoleInterface.on("line", this.onLineEntered)
    this.consoleInterface.on("close", this.onControlCPressed)
    this.setPrompt(message)
  }

  stop = () => {
    this.consoleInterface.close()
  }

  start = () => {
    this.consoleInterface.prompt()
  }

  setPrompt = (message: string) => {
    this.consoleInterface.setPrompt(message)
  }

  private onLineEntered = (line: string) => {
    switch (line) {
      case UIStrings.closeCommand:
        this.stop()
        return
      default:
        console.log(`> 🚀 You typed: ${chalk.yellow(line)}`)
        this.start()
    }
  }

  private onControlCPressed = () => {
    console.log(chalk.red("Goodbye!"))
    this.stop()
  }
}

const main = async (argv: Array<string>) => {
  const cli = new CommandLineInterface(UIStrings.userPrompt)
  cli.start()
}

main(process.argv.splice(2))
```

## Buffer

- [Course](https://www.educative.io/courses/learn-nodejs-complete-course-for-beginners/7nKRnv8Q9lQ#buffer-in-nodejs)
- [Sample code](src/basics/buffer.ts)

Node.js has a `Buffer` class that provides us with the functionality we discussed above. This
`Buffer` class is an array of bytes that is used to represent binary data. Streams, and other file
system operations, are usually carried out with binary data, making buffers the ideal candidates for
them.

The `Buffer` class is based on JavaScript’s `Uint8Array`. To put it simply, we can think of `Buffer`
objects as arrays that only contain integers from `0` to `255`. One distinction is that `Buffer`
objects correspond to fixed-sized blocks of memory, which cannot be changed after they are created.
There is no explicit way of deleting a buffer, but setting it to null will do the job. The memory
will be handled by the garbage collector.

## Events

- [Sample code](src/basics/events.ts)
- [EventEmitter Docs](https://nodejs.org/api/events.html#events_emitter_emit_eventname_args)
- [TypeScript varargs](https://www.damirscorner.com/blog/posts/20180216-VariableNumberOfArgumentsInTypescript.html)

Some interesting things to note:

- There's a default `error` event that you can pass to an `EventEmitter`.
- When you call `emit` you can pass varargs as the last argument. You have to be careful about
  receiving that in the event listener in the correct way.

```typescript
class Events {
  static readonly TimerName = "EventsTimer"
  static readonly Error = "error" /* Special Node.js error name. */
  static readonly Event1 = Symbol()
  static readonly Event2 = Symbol()
}

utils._let(new EventEmitter(), (emitter) => {
  // Start Timer.
  console.time(Events.TimerName)

  // Handle Event1.
  emitter.on(Events.Event1, (...args: any[]) => {
    console.log(chalk.blue(`emitter.on -> Event1, args: ${JSON.stringify(args)}`))
    console.timeLog(Events.TimerName)
  })

  // Handle Error.
  emitter.on("error", (...errorArgs: any[]) => {
    console.error(chalk.red(`emitter.on('error') -> errorArgs: ${JSON.stringify(errorArgs)}`))
    console.timeLog(Events.TimerName)
  })

  // Fire Event1.
  utils._let(Events.Event1, (event) => {
    fireEvent(emitter, event, 100, "🐵", { foo: "bar" })
    fireEvent(emitter, event, 200)
  })

  // Fire Error.
  fireError(emitter)
  fireError(emitter, 200, "💣", { errorCode: 50 })
})

// TypeScript varargs -
// https://www.damirscorner.com/blog/posts/20180216-VariableNumberOfArgumentsInTypescript.html

const fireError = (
  emitter: EventEmitter,
  delayMs: number = 100,
  ...errorArgs: (string | object)[]
) =>
  setTimeout(() => {
    emitter.emit(Events.Error, ...errorArgs)
  }, delayMs)

const fireEvent = (
  emitter: EventEmitter,
  eventType: symbol | string,
  delayMs: number = 100,
  ...args: (string | object)[]
) =>
  setTimeout(() => {
    emitter.emit(eventType, ...args)
  }, delayMs)
```

## Files

- [Course](https://www.educative.io/courses/learn-nodejs-complete-course-for-beginners/YQorL9rDQEW)
- [Sample code](src/basics/files.ts)

There are many `fs` APIs - async, sync, and promises. Use the `fs.promises` API so that it works
well with async / await and promises.

## Modules

- [Course](https://www.educative.io/courses/learn-nodejs-complete-course-for-beginners/m25YKr666wE)

1. Unlike browsers, global in Node.js is scoped to each module. So each module in Node.js has its
   own `global` object. And there is no such thing as the concept of a browser "global".
2. Each TS or JS file is considered a "module" by Node.js.
3. A Node.js `package` is not the same as a `module`. Modules are related to exports and imports.
   Packages are things that are published to npm and added to other packages as deps.

## OS, streams, process, network, etc.

### OS

- [Course](https://www.educative.io/courses/learn-nodejs-complete-course-for-beginners/N8qMPx1ZAzD)
- [Sample code](src/basics/os.ts)

### Process

You can listen to various events fired by the `process` global object (which is also an
`EventEmitter` instance). Here are some common ones: `beforeExit`, `exit`, and `uncaughtException`.
Refer`to the sample code listed below for more details.

- [Course](https://www.educative.io/courses/learn-nodejs-complete-course-for-beginners/xlxR82ozxxE)
- [Sample code](src/basics/process.ts)
- [Node.js docs - Process](https://nodejs.org/api/process.html#process_process_channel)
- [Tutorial - Node.js memory model](https://www.dynatrace.com/news/blog/understanding-garbage-collection-and-hunting-memory-leaks-in-node-js/)

### Streams, backpressure, pipes, files

- [Node.js docs - Stream](https://nodejs.org/api/stream.html)
- [Node.js docs - Backpressure and pipes](https://nodejs.org/en/docs/guides/backpressuring-in-streams/)
- [Node.js docs - pipeline](https://nodejs.org/api/stream.html#stream_stream_pipeline_streams_callback/)
- [Tutorial - Stream](https://jscomplete.com/learn/node-beyond-basics/node-streams)
- [Tutorial - Streams, large file IO, and memory usage](https://medium.com/dev-bits/writing-memory-efficient-software-applications-in-node-js-5575f646b67f)
- [Article - GC and memory leaks in Node.js](https://www.dynatrace.com/news/blog/understanding-garbage-collection-and-hunting-memory-leaks-in-node-js/)
- [Discussion - Difference between pipe and pipeline](https://stackoverflow.com/a/60459320/2085356)
- [Discussion - Get latest version of Node.js TS bindings](https://stackoverflow.com/a/67435044/2085356)
- [Discussion - Latest version of Node.js and stream promises](https://github.com/nodejs/node/issues/35731)
- [Sample code](src/streams/stream.ts)

All streams are instances of [`EventEmitter`][stream-1]. They emit events that can be used to read
and write data. However, we can consume streams data in a simpler way using the [`pipe()`][stream-2]
method (defined in [`Stream`][stream-3]). This method also handles errors, end-of-files, and the
cases when one stream is slower or faster than the other (backpressure).

[stream-1]: https://nodejs.org/api/events.html#events_class_eventemitter
[stream-2]: https://nodejs.org/en/knowledge/advanced/streams/how-to-use-stream-pipe
[stream-3]: https://nodejs.org/api/stream.html#stream_readable_pipe_destination_options

> In other words:
>
> | Paradigm to work with Streams        | How to use                                              |
> | ------------------------------------ | ------------------------------------------------------- |
> | Events (stream is also EventEmitter) | Use EventEmitter and attach listeners for `data` etc    |
> | Pipes (method defined on Stream)     | `pipe()`, which also handles errors, EOFs, backpressure |

#### pipe

Here's some pseudocode to demonstrate how all this fits together.

```javascript
readableSrc.pipe(writableDest)
```

And in more complex cases.

```javascript
readableSrc.pipe(transformStream1).pipe(transformStream2).pipe(finalWrtitableDest)
```

Using a Linux analogy.

```shell
$ a | b | c | d
```

Is equivalent to.

```javascript
a.pipe(b).pipe(c).pipe(d)

// Which is equivalent to:
a.pipe(b)
b.pipe(c)
c.pipe(d)
```

There is a lot to digest in the sample code above. There are some big concepts with streams and
files. The async nature of Node.js really shows itself here. Here are some interesting things to
note.

1. File reads are asynchronous by nature. So when the `pipe()` function is called on a stream that
   happens asynchronously so there's no waiting for it to finish and it returns an `EventEmitter`.
   That's how these calls can be chained together.
2. Without backpressure, the memory load is really high when writing a file "inefficiently". This
   also has the result of making the gc work even harder, and the CPU even harder dealing w/ memory
   management. Piping and backpressure resolve this issue and the results are stark!
3. File writes using a stream are async, but they also buffer in the OS file system. Linux will
   buffer the file and delay write it, even though Node.js will report that the file write is
   complete. This means that running `fs.stat()` immediately after the file write will result in
   incorrect file size being reported, since the size on disk is still growing.
4. There are [multiple ways](https://stackoverflow.com/a/21583831/2085356) of creating your own
   `Writable` and `Readable` streams. You can use the simplified constructor API or use classes
   instead.
5. The `console` global object is just a `Writable` stream! This makes it possible to overwrite the
   output that has already been written w/out generating a new line! This is handy for showing long
   running progress. Take a look at
   [color-console-utils.kt](https://github.com/r3bl-org/r3bl-ts-utils/blob/main/src/color-console-utils.ts)
   `consoleLogInPlace` method.
6. Piping is an incredibly powerful feature for working with streams in a high performance and
   memory efficient way. Read the docs and tutorials above for details.

#### pipeline, transform stream, and errors

`pipe()` does not report errors. `pipeline()` is what you must use when it comes to detecting error
conditions. Here's an example using a transform stream (which performs `gzip` compression).

Here's a snippet that uses a `gzip` transform stream in between a read and write stream, with the
use of backpressure, in other words:

- `Reader(UncompressedFile)` -> `gzip` transform -> `Writer(NewCompressedFile)`

Or:

- `Reader(UncompressedFile)` | `gzip` transform | `Writer(NewCompressedFile)`

Note - The promisified version of `pipline` on only works on Node.JS v15 and higher.

```typescript
export class CompressLargeFileEfficiently {
  performCompression = async (): Promise<void> => {
    await this.actuallyCompress().catch(console.error)

    // Wait for disk flush.
    ColorConsole.create(textStyle1.blue)(
      "Waiting for disk to flush the write to file for 5s..."
    ).consoleLog()
    await sleep(5000)
  }

  private actuallyCompress = async (): Promise<void> => {
    const uncompressedSrcFileReader = fs.createReadStream(Constants.filePath)
    const compressedDestFileWriter = fs.createWriteStream(Constants.compressedFilePath)

    const gzipTransformer = zlib.createGzip()

    ColorConsole.create(textStyle1)(`Using pipeline() to compress file`).consoleLog()
    await pipeline(uncompressedSrcFileReader, gzipTransformer, compressedDestFileWriter)
  }
}

await new CompressLargeFileEfficiently().performCompression().catch(console.error)
```

### Child process

- [Node.js docs - Child process](https://nodejs.org/api/child_process.html)
- [Tutorial - Child process](https://jscomplete.com/learn/node-beyond-basics/child-processes)
- [Sample code](src/cproc/child-process.ts)

Node.js makes it easy to spawn other child processes (OS processes and other instances of itself) in
order to scale or overcome its single threaded nature.

> Only when spawning other instances of itself it does it use IPC to send messages back and forth
> between these instances.

When combined w/ streams and `pipe()` this creates an incredibly powerful way to run processes and
manage process execution on your host OS.

- A child process (`ChildProcess`) is also an `EventEmitter` (`ChildProcess` is a subclass).
- It has 3 streams as well: `stdin`, `stdout`, `stderr`. You can use `pipe()` on them! Every
  `Stream` is also an `EventEmitter`.

There are four different ways to create a child process in Node:

1. `spawn()` - this is what we will look deeply into in this section. It can be used to run any OS
   command via a child process of the Node.js instance that executes this function.
2. `fork()` - this is what spawns another Node.js instance and IPC is used to communicate between
   the instances.
3. `exec()` - this actually spawns a shell in order to execute the command that is passed. It has
   one other major difference. It buffers the command’s generated output and passes the whole output
   value to a callback function (instead of using streams, which is what `spawn` does).
4. `execFile()` - this is like `exec()` except that it does not generate a shell before executing
   the command.

> - There are also sync versions of these functions that block the main thread.
> - There is currently no promisified version, though you can use the
>   [`util.promisify()`](https://nodejs.org/api/util.html#util_util_promisify_original)
>   functionality of Node.js to use promises. Here's a
>   [thread on SO](https://stackoverflow.com/a/67379845/2085356) that shows some samples of how to
>   write the promises yourself using TypeScript.

The examples in this section only look at the situation where you want to spawn a program on your OS
in a child process of the Node.js process that you have started (and the other approaches are just
skimmed).

#### Deep dive into spawn()

The `spawn` function launches a command in a new process and we can use it to pass that command any
arguments. Here's an example.

##### Example 1 - spawn a child process to execute a command

```typescript
class SpawnCProcToRunLinuxCommandAndGetOutput {
  readonly cmd = "find"
  readonly args = [`${process.env.HOME}`, "-type", "f"]

  run = async (): Promise<void> => {
    const child: ChildProcess = spawn(this.cmd, this.args)

    return new Promise<void>((resolve) => {
      child.on("exit", function (code, signal) {
        console.log(`Child process exited with code ${code} and signal ${signal}`)
        resolve()
      })
      child.stdout?.on("data", (data: Buffer) => {
        console.log(`Output : ${data.length}`)
      })
      child.stderr?.on("data", (data) => {
        console.log(`Error: ${data}`)
      })
    })
  }
}

const main = async (): Promise<void> => {
  await new SpawnCProcToRunLinuxCommandAndGetOutput().run()
}

main().catch(console.error)
```

Here are some notes on the code snippet above:

- [`ChildProcess`][cp-eg1-1] is a subclass of [`EventEmitter`][cp-eg1-2].
  - Events that we can register handlers for with the `ChildProcess` instances are:
  - `disconnect`, `error`, `close`, and `message`.
- To get a stream out of it, you can use the `stdin`, `stdout`, and `stderr` properties of the
  `ChildProcess` instance, using:
  - `child.stdin`, `child.stdout`, and `child.stderr`.
  - When those streams get closed, the child process that was using them will emit the `close`
    event. This `close` event is different than the `exit` event because multiple child processes
    might share the same "stdio" streams, so one child process exiting does not mean that the
    streams got closed.

[cp-eg1-1]: https://nodejs.org/api/child_process.html#child_process_class_childprocess
[cp-eg1-2]: https://nodejs.org/api/events.html#events_class_eventemitter

##### "stdio" streams for getting input to and output from child process commands

Child processes (used to execute commands) have streams that are `Readable` and `Writable`. We can
use them to send data to commands and to get the output or error from the commands.

> In a **child process**, this is the **inverse** of those types found in a **main process**.
>
> | Stream                  | R/W      |
> | ----------------------- | -------- |
> | [`process.stdin`][cp-1] | Readable |
> | [`child.stdin`][cp-2]   | Writable |

We can use the event driven approach to get data in and out of these child processes, they are
[event emitters][cp-3]. We can listen to different events (eg: `data`) on those "stdio" streams that
are attached to every child process.

> In other words:
>
> | What you need from command | What to use               | Stream   |
> | -------------------------- | ------------------------- | -------- |
> | Output from command        | `child.stdout.on("data")` | Readable |
> | Error from command         | `child.stderr.on("data")` | Readable |
> | Input to command           | `child.stdin`             | Writable |

[cp-1]: https://nodejs.org/api/process.html#process_process_stdin
[cp-2]: https://nodejs.org/api/child_process.html#child_process_subprocess_stdin
[cp-3]: https://nodejs.org/api/events.html#events_class_eventemitter

However it is easier to use the

- We can use the child process `stdin` which is a `Writable` stream.
- Just like any `Writable` stream, the easiest way to consume it is using `pipe()`.
- We simply pipe a `Readable` stream into a `Writable` stream.

##### Example 2 - pipe process.stdin into child process command

Since the main process `stdin` is a `Readable` stream, we can pipe that into a child process `stdin`
stream. For example:

```typescript
import { ChildProcess, spawn } from "child_process"
import { notNil } from "../core-utils/kotlin-lang-utils"

export class SpawnCProcAndPipeStdinToLinuxCommand {
  run = async (): Promise<void> => {
    console.log(`Type words, then press Ctrl+D to count them...`)

    const wcCommand: ChildProcess = spawn("wc")

    // Send input to command (from process.stdin), ie, process.stdin | wcCommand.stdin.
    notNil(wcCommand.stdin, (wcCommandStdin) => {
      process.stdin.pipe(wcCommandStdin)
    })

    return new Promise<void>((resolveFn, rejectFn) => {
      wcCommand.on("exit", function (code, signal) {
        console.log(`Child process exited with code ${code} and signal ${signal}`)
        resolveFn()
      })
      wcCommand.stdout?.on("data", (data: Buffer) => {
        console.log(`Output: ${data}`)
      })
      wcCommand.stderr?.on("data", (data) => {
        console.log(`Error: ${data}`)
        rejectFn()
      })
    })
  }
}

const main = async (): Promise<void> => {
  await new SpawnCProcAndPipeStdinToLinuxCommand().run()
}

main().catch(console.error)
```

In the example above:

- The child process invokes the `wc` command, which counts lines, words, and characters in Linux.
- We then pipe the main process `stdin` (which is a `Readable` stream) into the child process
  `stdin` (which is a `Writable` stream).
- The result of this combination is that we get a standard input mode where we can type something,
  and when we hit `Ctrl+D` what we typed will be used as the input of the `wc` command.

##### Example 3 - pipe the output of one child process command into another one

We can also pipe the standard input/output of multiple processes on each other, just like we can do
with Linux commands. For example, we can pipe the `stdout` of the `find` command to the `stdin` of
the `wc` command to count all the files in the current directory.

```typescript
import { ChildProcess, spawn } from "child_process"
import { ColorConsole, textStyle1 } from "../core-utils/color-console-utils"
import { notNil } from "../core-utils/kotlin-lang-utils"

export class SpawnCProcToPipeOutputOfOneLinuxCommandIntoAnother {
  run = async (): Promise<void> => {
    const findChildProcess: ChildProcess = spawn("find", [
      `${process.env.HOME}/github/notes/`,
      "-type",
      "f",
    ])

    const wcChildProcess: ChildProcess = spawn("wc", ["-l"])

    notNil(findChildProcess.stdout, (find) =>
      notNil(wcChildProcess.stdin, (wc) => {
        find.pipe(wc)
      })
    )

    return new Promise<void>((resolveFn, rejectFn) => {
      wcChildProcess.on("exit", function (code, signal) {
        console.log(`Child process exited with code ${code} and signal ${signal}`)
        resolveFn()
      })
      wcChildProcess.stdout?.on("data", (data: Buffer) => {
        console.log(`Number of files ${data}`)
      })
      wcChildProcess.stderr?.on("data", (data) => {
        console.log(`Error: ${data}`)
        rejectFn()
      })
    })
  }
}
```

##### Example 4 - ugly code to redirect the output of one child process command to another one

Without using `pipe()` the code would be pretty ugly.

Let's convert the following shell script to Node.js w/out using `pipe()`.

```shell
ps ax | grep ssh
```

Here's the ugly code (using `pipe()` is far superior).

```typescript
const { spawn } = require("child_process")

const ps = spawn("ps", ["ax"])
const grep = spawn("grep", ["ssh"])

ps.stdout.on("data", (data) => {
  grep.stdin.write(data)
})
ps.stderr.on("data", (data) => {
  console.error(`ps stderr: ${data}`)
})
ps.on("close", (code) => {
  if (code !== 0) {
    console.log(`ps process exited with code ${code}`)
  }
  grep.stdin.end()
})

grep.stdout.on("data", (data) => {
  console.log(data.toString())
})
grep.stderr.on("data", (data) => {
  onsole.error(`grep stderr: ${data}`)
})
grep.on("close", (code) => {
  if (code !== 0) {
    console.log(`grep process exited with code ${code}`)
  }
})
```

#### Killing or aborting a child process

To kill a child process, you can call
[`kill()`](https://nodejs.org/api/child_process.html#child_process_subprocess_kill_signal).

If the `signal` option (of type `AbortSignal`) is enabled, calling `.abort()` on the corresponding
`AbortController` is similar to calling `.kill()` on the child process except the error passed to
the callback will be an `AbortError`.
[Node.js docs](https://nodejs.org/api/child_process.html#child_process_child_process_spawn_command_args_options)
. For example:

```typescript
const { spawn } = require("child_process")
const controller = new AbortController()
const { signal } = controller

const grep = spawn("grep", ["ssh"], { signal })
grep.on("error", (err) => {
  // This will be called with err being an AbortError if the controller aborts
})
controller.abort() // Stops the child process
```

#### Brief exploration of exec()

Here's an example.

```typescript
const { exec } = require("child_process")

exec("find . -type f | wc -l", (err, stdout, stderr) => {
  if (err) {
    console.error(`exec error: ${err}`)
    return
  }

  console.log(`Number of files ${stdout}`)
})
```

#### Brief exploration of fork()

`fork()` is a variation of `spawn()` for spawning node processes. The biggest difference between
`spawn` and `fork` is that a communication channel is established to the child process when using
`fork`, so we can use `send()` on the forked process along with the global `process` object itself
to exchange messages between the parent and forked processes.

We do this through the `EventEmitter` module interface. Here’s an example:

The parent file, `parent.js`:

```typescript
const { fork } = require("child_process")

const forked = fork("child.js")

forked.on("message", (msg) => {
  console.log("Message from child", msg)
})

forked.send({ hello: "world" })
```

The child file, `child.js`:

```typescript
process.on("message", (msg) => {
  console.log("Message from parent:", msg)
})

let counter = 0

setInterval(() => {
  process.send({ counter: counter++ })
}, 1000)
```

#### Example of replacing a fish script using spawn

Here's a simple fish script that looks for the path to `linuxbrew` in `$HOME/.profile` so that GNOME
sessions can load it into their path. This is needed for processes that are spawned from GNOME shell
to be able to use Node.js that is installed using Linuxbrew.

```shell
#!/usr/bin/env fish

set searchString "linuxbrew"
set dotProfileFile "$HOME/.profile"

function _writeToDotProfileFile
  echo >> $dotProfileFile '
if [ -d "/home/linuxbrew/.linuxbrew" ] ; then
  PATH="/home/linuxbrew/.linuxbrew/bin:$PATH"
fi
'
end

function addLinuxbrewToGnomeSessionPath
  set -l grepResponse (grep $searchString $dotProfileFile)

  # echo "grepResponse: '$grepResponse'"

  if test -n "$grepResponse"
    echo "$searchString found in $dotProfileFile, nothing to do."
  else
    echo "$searchString not found in $dotProfileFile, make sure to add it."
    _writeToDotProfileFile
  end
end

if test (uname) = "Linux"
  # This is Linux.
  addLinuxbrewToGnomeSessionPath
else
  # This is macOS.
end
```

Now, here's the equivalent script written in Node.js using `spawn()`.

```typescript
import { _also, Optional } from "../core-utils/kotlin-lang-utils"
import * as fs from "fs"

/**
 * Using constant object instead of enum (better choice here since it allows computed values).
 * More info:
 * - https://www.typescriptlang.org/docs/handbook/enums.html#objects-vs-enums
 * - https://blog.logrocket.com/const-assertions-are-the-killer-new-typescript-feature-b73451f35802/
 */
const MyConstants = {
  gnomeDotProfileFile: process.env.HOME + "/.profile",
  linuxbrewSearchTerm: "linuxbrew",
  defaultLinuxbrewPath: "/home/linuxbrew/.linuxbrew",
} as const

export class SpawnCProcToReplaceFunctionalityOfFishScript {
  run = async (): Promise<void> => {
    try {
      const isFound = await this.doesGnomeProfileContainLinuxbrewPath()
      if (isFound) {
        console.log(
          `Nothing to do, ${MyConstants.linuxbrewSearchTerm} is already in ${MyConstants.gnomeDotProfileFile}`
        )
        return
      }
      await this.addPathToGnomeProfileFile()
    } catch (e) {
      console.error(`Error: ${e}`)
    }
  }

  // https://nodesource.com/blog/understanding-streams-in-nodejs/
  doesGnomeProfileContainLinuxbrewPath = async (): Promise<boolean> => {
    return new Promise<boolean>((resolveFn, rejectFn) => {
      let isFound = false
      _also(fs.createReadStream(MyConstants.gnomeDotProfileFile), (it) => {
        it.on("data", (data: Buffer | string) => {
          isFound = data.includes(MyConstants.linuxbrewSearchTerm)
        })
        it.on("end", () => {
          resolveFn(isFound)
        })
        it.on("error", () => {
          rejectFn()
        })
      })
    })
  }

  addPathToGnomeProfileFile = async (): Promise<void> => {
    const overriddenLinuxbrewPath: Optional<string> = process.env.PATH?.split(":")
      .filter((pathElement) => pathElement.includes(MyConstants.linuxbrewSearchTerm))
      .shift()
    const linuxbrewPath: string = overriddenLinuxbrewPath ?? MyConstants.defaultLinuxbrewPath

    console.log(`linuxbrewPath: ${linuxbrewPath}`)

    const snippetToAppend = `if [ -d "${linuxbrewPath}" ] ; then
  PATH="${linuxbrewPath}/bin:$PATH"
fi`

    console.log(`snippet: ${snippetToAppend}`)

    return new Promise<void>((resolveFn, rejectFn) => {
      fs.appendFile(
        MyConstants.gnomeDotProfileFile,
        snippetToAppend,
        (err: NodeJS.ErrnoException | null) => {
          const _onErr = () => {
            rejectFn()
            console.error(`Problem appending file ${MyConstants.gnomeDotProfileFile}`)
          }
          const _onOk = () => {
            resolveFn()
            console.log(`Appended file ${MyConstants.gnomeDotProfileFile}`)
          }
          err ? _onErr() : _onOk()
        }
      )
    })
  }
}

const main = async () => {
  await new SpawnCProcToReplaceFunctionalityOfFishScript().run()
}

main().catch(console.error)
```

## Publishing npm packages

- [r3bl-ts-utils][r-3] - This repo is published on npm (`npm i r3bl-ts-utils`) and used in the code
  here. The README contains instructions on how to publish a package and update it as well.
- [Excellent tutorial on how to publish an npm package][r-1].
- [`.npmignore` and `files` directive in `package.json`][r-2].

[r-1]: https://itnext.io/step-by-step-building-and-publishing-an-npm-typescript-package-44fe7164964c
[r-2]: https://stackoverflow.com/a/41285281/2085356
[r-3]: https://github.com/r3bl-org/r3bl-ts-utils
