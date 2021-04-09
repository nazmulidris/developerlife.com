---
author: Nazmul Idris
date: 2018-10-21 5:00:00+00:00
excerpt: |
  This tutorial is an introduction to Dagger 2 with a simple example of using it in Java
layout: post
title: "Introduction to Dagger 2"
categories:
  - DI
---

<img class="post-hero-image" src="{{ 'assets/di-java-hero.svg' | relative_url }}"/>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [About Dagger 2](#about-dagger-2)
  - [Annotations](#annotations)
  - [Dependency providers](#dependency-providers)
  - [Dependency consumers](#dependency-consumers)
  - [Connecting consumers and providers](#connecting-consumers-and-providers)
  - [Special treatment of fields](#special-treatment-of-fields)
  - [Scope annotations](#scope-annotations)
- [Simplest Java Example](#simplest-java-example)
  - [Object that does not require @Module](#object-that-does-not-require-module)
  - [Object that requires @Module](#object-that-requires-module)
  - [@Bind shortcut](#bind-shortcut)
  - [Summary](#summary)
- [References](#references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## About Dagger 2

Dagger 2 is dependency injection framework. It is based on the Java Specification Request (JSR) 330.
It uses code generation and is based on annotations. The generated code is very relatively easy to
read and debug.

To learn more about Dagger 2, here are some excellent resources.

1. [Excellent video on Dependency Injection](https://www.youtube.com/watch?v=IKD2-MAkXyQ)
1. [Excellent video on Dagger 2 by Jake Wharton](https://www.youtube.com/watch?v=plK0zyRLIP8)
1. [Excellent tutorial on Dagger 2 and Android tutorial](https://github.com/codepath/android_guides/wiki/Dependency-Injection-with-Dagger-2)
1. [SO - @Named](https://stackoverflow.com/questions/45080227/dagger2-where-inject-named-provides-in-dependent-module)
1. [SO - @Inject constructor params](https://stackoverflow.com/questions/32076244/dagger-2-injecting-parameters-of-constructor)

### Annotations

Dagger 2 uses the following annotations:

- `@Module` and `@Provides`: define classes and methods which provide dependencies.

- `@Inject`: request dependencies. Can be used on a _constructor_, a _field_, or a _method_.

- `@Component`: enable selected modules and used for performing dependency injection.

Dagger 2 uses generated code to access the fields and not reflection. Therefore it is not allowed to
use private fields for field injection.

### Dependency providers

The term _dependency injection context_ is typically used to describe the set of objects which can
be injected.

- In Dagger 2, _classes_ annotated with `@Module` are responsible for providing objects which can be
  injected.
- Such classes can define methods annotated with `@Provides`. The returned objects from these
  methods are available for dependency injection.
- Methods annotated with `@Provides` can also express dependencies via method parameters. These
  dependencies are fulfilled by Dagger 2, if possible.

### Dependency consumers

You use the `@Inject` annotation to define a dependency.

Note that if you annotate a constructor with `@Inject`, Dagger 2 can also use an instance of this
object to fulfill dependencies. This was done to avoid the definition of lots of `@Provides` methods
for these objects.

### Connecting consumers and providers

The `@Component` is used on an interface. Such an interface is used by Dagger 2 to generate code.
This interface defines the connection between the provider of objects (modules) and the objects
which express a dependency (consumers).

- The name of the the generated class is `Dagger` + the name of the interface.
- This generated class has a `create()` method which allows configuring the objects based on the
  given configuration. Or you can use the `builder()` to get more sophisticated about providing
  modules.
- The methods defined on the interface are available to access the generated objects.

### Special treatment of fields

Dagger 2 does not inject fields automatically. It can also not inject private fields. If you want to
use field injection you have to define a method in your `@Component` interface which takes the
instance into which you would like Dagger 2 to inject an object into this field.

### Scope annotations

You can use the `@Singleton` annotation to indicate that there should be only one instance of the
object.

## Simplest Java Example

This is the most basic example of using Dagger 2 without component dependencies, subcomponents,
complex modules, or custom scopes. The main Dagger 2 features used are:

- `@Component`.
- `@Inject`.
- `@Module` and `@Provider`.

There's a `Log` interface that is that allows a message to be logged. And an implementation of this
interface `ConsoleLogger` that just dumps it to the console. The goal is to leave creation of
objects to Dagger 2 (along w/ providing a concrete implementation of the `Log` interface).

Dagger 2 will be providing this application w/ 2 objects:

1. `Main` object.
1. `Log` object.

Here are the basic classes.

```java
interface Log {
    void log(String msg);
}
```

```java
class ConsoleLogger implements Log {
    @Override
    public void log(String msg) {
        System.out.println(msg);
    }
}
```

> Here's a link to the
> [repo](https://github.com/nazmulidris/dagger2/tree/main/java/src/main/java/example0).

### Object that does not require @Module

Let's look at the simplest case first. We don't want to create a new `Main` object using
`new Main()` in the `main()` method of the `Main` class. We want Dagger 2 to generate this, since
the whole point of dependency injection is not having to use `new`.

There's only one `Main` class, there's no interface that has to be implemented by this class. So it
is pretty straightforward to tell Dagger 2 to create this object and expose it as a dependency.

```java
@Inject
Main() {}
```

The way in which to do this is to annotate the no arg constructor of `Main` with `@Inject`. This
tells Dagger 2 that it should create an instance of this class when it's needed by any of the
objects in the object graph that it generates.

This requires the creation of a `@Component` since that's the entry point for Dagger 2 to start
creating all the objects that are required by the application. This is what the interface looks
like.

```java
@Component
@Singleton
interface LogComponent {
    Main providesMain();
}
```

Please note that it's called in the `main()` method of the `Main` class. So we don't actually create
an instance of `Main`. It's done for us by Dagger 2.

```java
public static void main(String[] args) {
    DaggerLogComponent.builder().build().providesMain().run();
}
```

How did this work? Dagger 2 knows how it can create a `Main` class, since the no-arg constructor
annotated w/ `@Inject` in `Main` is a way to tell Dagger 2 that when it needs to, it can use this
constructor to create an instance. The `@Singleton` annotation on the component also ensures that it
keeps this instance around for the lifetime of this component (once the instance has been created).

By using `@Inject` you can bypass the need to create a `@Module` and have a `@Provide` annotated
method, which is what is usually required. Dagger 2 is smart enough to figure out that for this
simple class (that it doesn't have to worry about mapping to some interface) it can just create a
singleton if needed and pass it around the object graph of dependencies.

The situation will get more complex when we have to deal with generating a `Log` implementation
object and make it available to the object graph.

### Object that requires @Module

The key difference between providing a `Main` object and a `Log` object is that `Log` is an
interface, and many different implementations may be available for this interface, and Dagger 2
doesn't know (without being told) how to provide the desired implementation for this interface.

This is where `@Module` and `@Provides` come into play.

So we add some more complexity to our component.

```java
@Component(modules = {LogModule.class})
@Singleton
interface LogComponent {
    Main providesMain();
}

@Module
class LogModule {
    @Provides
    @Singleton
    Log providesLogger(ConsoleLogger logger) {
        return logger;
    }
}
```

Note that the `providesLogger()` method is declared, but an object is **NOT** created here! We could
simply do the following in this method and it would work.

```java
Log providesLogger() {
    return new ConsoleLogger();
}
```

However, by adding a parameter to this `providesLog()` method, we are telling Dagger 2 to figure out
how to get an **instance** of `ConsoleLogger` on its own, but then return it **as** a `Log`
interface. That's pretty slick!

In order to make this happen, we have to make the `ConsoleLogger` class more complex though.

```java
@Singleton
class ConsoleLogger implements Log {

    @Inject
    ConsoleLogger(){}

    @Override
    public void log(String msg) {
        System.out.println(msg);
    }
}
```

By simply adding a no-arg constructor and marking it w/ `@Inject` we are able to tell Dagger 2 how
to provide an instance of `ConsoleLogger` that it can provide! How awesome is that!

Also note that the `@Singleton` annotation is applied to the class and not the method, since we are
using a `@Inject`. If we were using a provider and module then the `@Singleton` annotation would not
be at the class level; this is only for `@Inject`.

Finally we have to change the `Main` class so that it knows how to work w/ the `LogModule` that we
just added.

```java
class Main {

    public static void main(String[] args) {
        DaggerLogComponent.builder().build().providesMain().run();
    }

    @Inject
    Main() {}

    @Inject
    Log logger;

    public void run() {
        logger.log("Hello world!!! Simple Dagger");
    }

}
```

### @Bind shortcut

Instead of this:

```java
@Provides @Singleton
Log providesLogger(ConsoleLogger logger) { return logger; }
```

We could write:

```java
@Binds @Singleton
abstract Log providesLogger(ConsoleLogger logger);
```

It is possible to have arguments in the constructor that are annotated w/ `@Inject` as long as the
parameters in the constructor are objects that Dagger 2 knows how to create. In order to use this:

1. Simply make the `Module` class abstract
1. Make the non-`@Binds` methods, ie the `@Provides` methods static.

### Summary

There you have it! This is the simplest way in which you can use Dagger 2.

1. It was super easy to make `Main` objects w/ a no arg constructor that's annotated w/ `@Inject`.
   But it was harder when we have an interface that may be implemented by many different classes,
   and so a provider and module was needed to tell Dagger 2 how to bind an implementation to the
   interface.

1. However it was not necessary to tell Dagger 2 how to explicitly create an instance of the class
   implementing the interface (this was achieved w/ `@Inject` annotation again, on the no arg
   constructor of the implementation class).

1. The Module and Provider method simply was a way to Dagger 2 how to make that association or
   binding between the implementation of our choice and the interface.

## References

- [Configuring Idea, Gradle, and Dagger2](https://stackoverflow.com/a/52324748/2085356)
- [Excellent video on Dependency Injection](https://www.youtube.com/watch?v=IKD2-MAkXyQ)
- [Jake Wharton's video on Dagger2](https://www.youtube.com/watch?v=plK0zyRLIP8)
- [Tutorial - Kotlin, Android, Dagger2](https://www.raywenderlich.com/262-dependency-injection-in-android-with-dagger-2-and-kotlin)
- [Tutorial - Vogella](http://www.vogella.com/tutorials/Dagger/article.html)
- [Tutorial - Blood example](https://www.ricston.com/blog/dependency-injection-dagger-2/)
- [Tutorial - Missing Guide](https://medium.com/@Zhuinden/that-missing-guide-how-to-use-dagger2-ef116fbea97)
- [Tutorial - Codepath Dagger2 and Android](https://github.com/codepath/android_guides/wiki/Dependency-Injection-with-Dagger-2)
- [SO - question about @Named](https://stackoverflow.com/questions/45080227/dagger2-where-inject-named-provides-in-dependent-module)
- [SO - question about constructor param](https://stackoverflow.com/questions/32076244/dagger-2-injecting-parameters-of-constructor)
