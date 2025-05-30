---
author: Nazmul Idris
date: 2020-07-11 5:00:00+00:00
excerpt: |
  Introduction to Kotlin Annotation Processing on Android and how to create a static index of generated classes and
  interfaces (without using reflection or classgraphs)
layout: post
title: "Annotation Processing in Kotlin and Android"
categories:
  - KT
  - Android
  - MP
---

<img class="post-hero-image" src="{{ 'assets/annotation-processing-hero.svg' | relative_url }}"/>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Get the source code](#get-the-source-code)
- [End goals of this project](#end-goals-of-this-project)
  - [Using our annotations](#using-our-annotations)
  - [Using reflection to access the generated classes](#using-reflection-to-access-the-generated-classes)
  - [Generating a static index of all the usages of our annotations in our codebase](#generating-a-static-index-of-all-the-usages-of-our-annotations-in-our-codebase)
- [Annotation processing](#annotation-processing)
- [Project structure](#project-structure)
- [Building an index of annotated classes](#building-an-index-of-annotated-classes)
- [Using reflection to load the adapter classes, given the model classes](#using-reflection-to-load-the-adapter-classes-given-the-model-classes)
- [Converting Groovy scripts to Kotlin DSL](#converting-groovy-scripts-to-kotlin-dsl)
- [Debugging](#debugging)
- [References](#references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Get the source code

You can find the code for this project in
[this GitHub repo](https://github.com/nazmulidris/annotation-processing/tree/main/kotlin-android-project).
This tutorial is meant to give you some context and describe the structure of this repo
and the intended goals. Please clone the repo and play w/ it as you're reading this
tutorial, since most of the code in the repo is simply not provided or repeated in this
tutorial. Also, the code is documented and structured in a readable way, so you can follow
along w/out this tutorial if you like to learn that way.

# End goals of this project

This project shows how to create annotation processors using Kotlin and Android. The main
example is a RecyclerView whose adapter is generated via annotations.

Here's what the annotated code looks like for a "data model" class, which is simply a
class w/ some properties that need to be mapped to each row of a RecyclerView (which is
declared in `row_renderer_simple.xml`).

## Using our annotations

There are only 2 annotations:

1. Class level annotation `@AdapterModel`. This generates a source file w/ the name
   `Adapter` appended at the end of the name of the class annotated w/ this. For the
   example below, the `PersonModelAdapter` class is generated.
2. Property level annotation `@ViewHolderBinding`. These can be added to properties of the
   class that has been annotated w/ `@AdapterModel`.

```kotlin
@AdapterModel(R.layout.row_renderer_simple)
data class PersonModel(
    @ViewHolderBinding(R.id.title) val name: String,
    @ViewHolderBinding(R.id.subtitle) val address: String
)
```

Here's what the code looks like in the simple Activity that loads a bunch of data, which
is then displayed in a RecyclerView. The magic here is that the `PersonModelAdapter` is
generated by the annotation processor! When the data model classes change, the adapter is
regenerated when we rebuild the project!

```kotlin
class MainActivity : AppCompatActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.activity_main)
    recyclerView.apply {
      layoutManager = LinearLayoutManager(this@MainActivity)
      adapter = PersonModelAdapter(listOf(
        Person("John Doe", "123 Street"),
        Person("Jane Doe", "789 Street")
      ))
    }
  }
}
```

## Using reflection to access the generated classes

Note that we are explicitly using `PersonModelAdapter` here, which means we must know of
the existence of this class by memory, which is not optimal.

We can also get this via reflection! Just by knowing that we are looking for the generated
adapter class for the `PersonModel` class (which we have written and know of), we can find
it via reflection, knowing that this adapter must also take a `List` as a parameter to its
constructor. All of this logic is the `AdapterUtils.createBindingForModel()` function.
Here's what the usage of that code looks like.

```kotlin
class MainActivity : AppCompatActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.activity_main)
    recyclerView.apply {
      layoutManager = LinearLayoutManager(this@MainActivity)
    }
    bindPersonModelAdapter()
  }

  private fun bindPersonModelAdapter() {
    val items = listOf(
        PersonModel("Jane Doe", "123 Street"),
        PersonModel("John Doe", "789 Street")
    )
    val adapter = AdapterUtils.createBindingForModel(PersonModel::class.java, items)
    adapter?.apply {
      recyclerView.adapter = this as RecyclerView.Adapter<*>
    }
  }
}
```

## Generating a static index of all the usages of our annotations in our codebase

As a bonus we also get an index of all the classes in our project that use our
annotations! In the `MainActivity` code above, instead of calling the
`bindPersonModelAdapter()` function, we can call the following.

```kotlin
  private fun bindDebugModelAdapter() {
    val items: MutableList<DebugModel> = mutableListOf()
    AdapterIndex().index.map { classAnnotationHolder ->
      val title: String = classAnnotationHolder.name
      val description: String = classAnnotationHolder.list.joinToString(",", "{", "}") { it.name }
      items.add(DebugModel(title, description))
    }
    val adapter = AdapterUtils.createBindingForModel(DebugModel::class.java, items)
    adapter?.apply {
      recyclerView.adapter = this as RecyclerView.Adapter<*>
    }
  }
```

The index is statically generated at compile time, so there's no runtime overhead of using
some kind of expensive
[classgraph](https://github.com/classgraph/classgraph/wiki/Code-examples) or reflection.
The `index.AdapterIndex` file contains the statically generated index of all the places in
our code where our annotation is used. And if you call `bindDebugModelAdapter()` then you
will see all the places where our annotations are used in the code to build the sample app
itself 😲.

# Annotation processing

Here’s a quick breakdown of the core concepts.

- Annotation processing is a tool built into javac for scanning and processing annotations
  at compile time.
- It can create new source files; however, it can’t modify existing ones.
- It’s done in rounds. The first round starts when the compilation reaches the pre-compile
  phase. If this round generates any new files, another round starts with the generated
  files as its input. This continues until the processor processes all the new files.

<img src="{{'assets/ap-diagram.svg' | relative_url}}"/>

# Project structure

This project has 3 modules:

- `app` - contains the Activity and RecyclerView (and uses the annotations defined below).
  The "data model" class is in this module and the annotations are actually used on
  classes here. Eg: `PersonModel` and `DebugModel`.
- `annotations` - contains the custom annotations that we've defined. There are two
  annotations, one at a class level, and the other at a property level (of the properties
  enclosed by the class).
- `processor` - contains the actual processor that generates the source files on compile.
  1. The processor looks for the class level annotation and enclosed property level
     annotations, and gathers the metadata from them in the `metadata.kt` classes.
  2. The metadata is then passed to the `codegen.kt` classes in order to generate the
     RecyclerView adapter corresponding to the data model.
  3. When you build the project, the generated files can be found in the following folder:
     `${buildDir.absolutePath}/generated/source/kotlin`.
     - The actual adapter files that generated here are: `PersonModelAdapter.kt` and
       `DebugModelAdapter.kt`.
     - Also, a static index file is generated in the `index` package/folder, called
       `AdapterIndex.kt`.
  4. `AdapterUtils.kt` is provided in this package as well, which handles providing a way
     to access the index and any generated model adapters via reflection.

There is a bunch of glue that enables annotation processing in the `build.gradle.kts`
files of each of these modules. In summary:

1. The annotations have to be imported in various modules.
2. The processor has to be run as well by the `app` module.

# Building an index of annotated classes

There are times when it would be useful to find all the classes that are annotated w/ a
particular annotation. For a made up example, in our activity, instead of populating the
RecyclerView adapter w/ dummy data, we could have found all the classes and methods where
our annotations appear in the code, and then display that in the list.

Sadly, in Android due to the way in which DEX files work, it's not as easy as it would be
in a normal JVM. Libraries like [classgraph](https://github.com/classgraph/classgraph)
fail to work on Android. And there are hacks to scan DEX files to find annotated classes,
but those
[are slow and dangerous to use](https://bravenewgeek.com/implementing-spring-like-classpath-scanning-in-android/).

Currently we have `AdapterIndexGeneratorBuidler.kt` which actually does just this, but at
compile time. Here's what the output of this class looks like for this project (in the
generated `index.AdapterIndex.kt` file).

```kotlin
package index

class AdapterIndex {
  val index: MutableList<ClassAnnotationHolder> = mutableListOf()

  init {
    index.add(ClassAnnotationHolder("DebugModelAdapter", mutableListOf()).apply {
      list.add(PropertyAnnotationHolder("title"))
      list.add(PropertyAnnotationHolder("description"))
    })
    index.add(ClassAnnotationHolder("PersonModelAdapter", mutableListOf()).apply {
      list.add(PropertyAnnotationHolder("name"))
      list.add(PropertyAnnotationHolder("address"))
    })

  }

  data class PropertyAnnotationHolder(
      val name: String
  )

  data class ClassAnnotationHolder(
      val name: String,
      val list: MutableList<PropertyAnnotationHolder>
  )
}
```

# Using reflection to load the adapter classes, given the model classes

ButterKnife is the inspiration of this feature, where you have to set it in motion by
calling `bind(this)`. Even when classes are generated, they won't "activate" until they
are referenced from someplace.

So at some point, the code using the generated code has to make a call to load the
generated class. In our activity, this happens when `PersonModelAdapter` is directly
referenced. But this is not optimal.

Perhaps a better way would be one by ButterKnife used in this
[nice example here](https://emo-pass.com/2017/11/26/builing-things-with-java-reflection-and-annotation-processing/).
It uses reflection and annotation processing in order to work. Here's the
[code for the `bind()` method](https://github.com/quangctkm9207/prefpin/blob/master/prefpin/src/main/java/prefpin/PrefPin.java#L42).

We can achieve this type of behavior in this project, and the code for this is in
`codegen.AdapterUtils.kt`. If you look at how the following methods
`bindPersonModelAdapter` and `bindDebugModelAdapter` are used in the sections above you
can get a sense for the ergonomics of this approach vs knowing the generated class name
ahead of time.

There's a reflective way to load the `AdapterIndex` shown above as well. Here's the code.

```kotlin
  private fun bindDebugModelAdapter() {
    val items: MutableList<DebugModel> = mutableListOf()
    AdapterUtils.getAdapterIndex()?.apply {
      (this as AdapterIndex).index.map { classAnnotationHolder ->
        val title: String = classAnnotationHolder.name
        val description: String = classAnnotationHolder.list.joinToString(",", "{", "}") { it.name }
        items.add(DebugModel(title, description))
      }
      val adapter = AdapterUtils.createBindingForModel(DebugModel::class.java, items)
      adapter?.apply {
        recyclerView.adapter = this as RecyclerView.Adapter<*>
      }
    }
  }
```

# Converting Groovy scripts to Kotlin DSL

The Groovy gradle files have been converted to Kotlin DSL. Also, note that there are very
few files in `buildSrc` that contain variables about dependencies and version numbers.
These are updated by Android Studio, and putting them in variables defeats Studio's
efforts to automatically upgrade these for you, so it's best to keep it really simple for
simple projects like this one.

1. You can learn more about how to migrate from Groovy to Kotlin DSL
   [here](https://proandroiddev.com/the-new-way-of-writing-build-gradle-with-kotlin-dsl-script-8523710c9670).
2. Here's a KTS script to automate the Groovy file to Kotlin DSL
   [here](https://github.com/bernaferrari/GradleKotlinConverter).

# Debugging

To learn more about debugging your annotation process, check out this
[link](https://medium.com/@cafonsomota/debug-annotation-processor-in-kotlin-6eb462e965f8).

# References

- [Android & Kotlin annotation processing tutorial](https://www.raywenderlich.com/8574679-annotation-processing-supercharge-your-development)
- [Another tutorial like above](https://medium.com/@jintin/annotation-processing-in-java-3621cb05343a)
- [Java annotation processing tutorial](http://hannesdorfmann.com/annotation-processing/annotationprocessing101)
- [Runtime annotations and reflection](https://gist.github.com/championswimmer/d7b9be0c26ac88de2455a80117137ec6)
- [Kotlin in Action book](https://livebook.manning.com/book/kotlin-in-action/chapter-10/55)
