---
author: Nazmul Idris
date: 2018-10-21 5:00:00+00:00
excerpt: |
  This tutorial is an introduction to Dagger 2 with a simple example of using it in Java.
layout: post
hero-image: assets/di-java-hero.svg
title: "Introduction to Dagger 2"
categories:
- DI
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [About Dagger 2](#about-dagger-2)
- [Annotations](#annotations)
- [Dependency providers](#dependency-providers)
- [Dependency consumers](#dependency-consumers)
- [Connecting consumers and providers](#connecting-consumers-and-providers)
  - [Special treatment of fields](#special-treatment-of-fields)
- [Scope annotations](#scope-annotations)
- [References](#references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## About Dagger 2

Dagger 2 is dependency injection framework. It is based on the Java 
Specification Request (JSR) 330. It uses code generation and is based on
annotations. The generated code is very relatively easy to read and debug.

To learn more about Dagger 2, here are some excellent resources.
1. [Excellent video on Dependency Injection](https://www.youtube.com/watch?v=IKD2-MAkXyQ)
1. [Excellent video on Dagger 2 by Jake Wharton](https://www.youtube.com/watch?v=plK0zyRLIP8)
1. [Excellent tutorial on Dagger 2 and Android tutorial](https://github.com/codepath/android_guides/wiki/Dependency-Injection-with-Dagger-2)
1. [SO - @Named](https://stackoverflow.com/questions/45080227/dagger2-where-inject-named-provides-in-dependent-module)
1. [SO - @Inject constructor params](https://stackoverflow.com/questions/32076244/dagger-2-injecting-parameters-of-constructor)

## Annotations

Dagger 2 uses the following annotations:

- `@Module` and `@Provides`: define classes and methods which provide 
   dependencies.

- `@Inject`: request dependencies. Can be used on a *constructor*, a *field*, 
   or a *method*.

- `@Component`: enable selected modules and used for performing dependency 
   injection.

Dagger 2 uses generated code to access the fields and not reflection. Therefore 
it is not allowed to use private fields for field injection.
   
## Dependency providers
The term *dependency injection context* is typically used to describe the set 
of objects which can be injected. 

- In Dagger 2, *classes* annotated with `@Module` are responsible for providing 
  objects which can be injected. 
- Such classes can define methods annotated with `@Provides`. The returned 
  objects from these methods are available for dependency injection.
- Methods annotated with `@Provides` can also express dependencies via method 
  parameters. These dependencies are fulfilled by Dagger 2, if possible.

## Dependency consumers
You use the `@Inject` annotation to define a dependency. 

Note that if you annotate a constructor with `@Inject`, Dagger 2 can also use 
an instance of this object to fulfill dependencies. This was done to avoid the 
definition of lots of `@Provides` methods for these objects.

## Connecting consumers and providers
The `@Component` is used on an interface. Such an interface is used by Dagger 2 
to generate code. This interface defines the connection between the provider of 
objects (modules) and the objects which express a dependency (consumers).

- The name of the the generated class is `Dagger` + the name of the interface. 
- This generated class has a `create()` method which allows configuring the 
  objects based on the given configuration. Or you can use the `builder()` to
  get more sophisticated about providing modules.
- The methods defined on the interface are available to access the generated 
  objects.

### Special treatment of fields
Dagger 2 does not inject fields automatically. It can also not inject private 
fields. If you want to use field injection you have to define a method in 
your `@Component` interface which takes the instance into which you would like
Dagger 2 to inject an object into this field.

## Scope annotations
You can use the `@Singleton` annotation to indicate that there should be only 
one instance of the object.

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
