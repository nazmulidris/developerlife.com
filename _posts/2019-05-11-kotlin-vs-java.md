---
author: Nazmul Idris
date: 2019-05-11 17:59:00+00:00
excerpt: |
  This tutorial showcases the differences between using Java and Kotlin in
  Android development
layout: post
hero-image: assets/java-vs-kotlin.svg
title: "Java vs Kotlin for Android development"
categories:
  - Android
  - KT
  - TDD
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [Video of the app in action](#video-of-the-app-in-action)
- [Architecture of the Giphy viewer app](#architecture-of-the-giphy-viewer-app)
  - [Overview of the Kotlin codebase](#overview-of-the-kotlin-codebase)
  - [Overview of the Java codebase](#overview-of-the-java-codebase)
- [Differences between Java and Kotlin](#differences-between-java-and-kotlin)
  - [Sealed data classes vs builders](#sealed-data-classes-vs-builders)
  - [typedefs and lambdas vs interfaces](#typedefs-and-lambdas-vs-interfaces)
  - [Coroutines vs AsyncTask](#coroutines-vs-asynctask)
  - [Extension function expressions](#extension-function-expressions)
  - [Constructors](#constructors)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

I've been working w/ Kotlin to write Android apps for about 1 year now, and I've
really love it 😍. I've also been working w/ vanilla ES6 JavaScript a lot in the
past year, which surprisingly has made my Kotlin better (since I'd been a Java
developer for many decades prior to this).

However, I hadn't used both Java and Kotlin on the same app before, so I decided
to write the same exact Android app using Java, and also using Kotlin to
experience what the major differences would be. This tutorial contains a side by
side comparison between Kotlin and Java for the same Android app, which is a
simple endless scrolling Giphy viewer.

## Video of the app in action

<!-- Image resize and flexbox: https://stackoverflow.com/a/37799733/2085356 -->
<div style="display:flex; justify-content:center; flex-flow:row nowrap; align-items:flex-start;">
<img
src="https://raw.githubusercontent.com/nazmulidris/giphy-viewer-kotlin/master/files/giphy.gif"
style="max-width:40%; padding-bottom:24px; padding-right: 16px">
<div>
  The app allows a user to see trending GIFs from the Giphy API. It
  allows the user to search for GIFs. Whether the user is browsing
  trending GIFs or searching for them, infinite scrolling is supported, so
  the more they swipe down on the app, 25 images are loaded at a time.
  Thumbnails of the images are loaded in the RecyclerView, and when the
  user clicks on an item, a high res version of the image is opened in a
  new activity and the URL is shortened and copied to the clipboard.

  <br><br>
  <a href="https://github.com/r3bl-org/giphy-viewer-kotlin">
      GitHub repo for the Kotlin app</a>
  <br><br>
  <a href="https://github.com/nazmulidris/giphy_viewer">
      GitHub repo for the Java app</a>
</div>
</div>

## Architecture of the Giphy viewer app

- The app uses Architecture components (`LiveData` and `ViewModel`) to actually
  get the data from the Giphy API on Android, and then populate a `RecyclerView`
  that uses a `StaggeredGridLayoutManager` to display the images.

- It uses Fresco to load and cache the images.

- It uses Paginate library to handle infinite scrolling of the `RecyclerView`.

- It also uses Kotlin coroutines and `tinyurl.com` in order to generate and copy
  short URLs for the selected GIF.

- The tests (unit and instrumented) are written using Espresso, JUnit4, MockK,
  Roboelectric, and AssertJ. _I really like Karma and Jasmine (from the JavaScript
  world) and in a future project will be using Kotlin testing libraries that allow
  `describe` and `it` blocks in the test code._

<img
src="https://raw.githubusercontent.com/nazmulidris/giphy-viewer-kotlin/master/files/arch-diagram.png"
style="width:100%;">

### Overview of the Kotlin codebase

You can get the GitHub repo for the Kotlin app
[here](https://github.com/r3bl-org/giphy-viewer-kotlin).

<a href="https://github.com/r3bl-org/giphy-viewer-kotlin">
<img
src="https://repository-images.githubusercontent.com/182448002/ce195500-732d-11e9-87fc-425635e0dac5">
</a>

- **MyApplication.kt** is the custom Application class that acts as a
  dependency injection component that provides various objects that are needed
  in various places throughout the app.

- **State.kt** contains sealed classes that represent various events and state
  representations that are used throughout the app.

- **Util.kt** contains a set of extension function expressions and typedefs that
  are used throughout the app. Coroutine functions are included here as well.

- **MyViewModel.kt** contains the AndroidViewModel that holds the data that's
  loaded from the network service, and also exposes the network service end points
  to the rest of the app.

- **NetworkService.kt** contains the integration w/ the Giphy Android SDK. Calls
  from the ViewModel are passed on the methods of GiphyClient, which ends up
  making calls to the Giphy Android API.

- **RecyclerViewManager.kt** contains the RecyclerView data adapter,
  RowViewModel implementation, and configuration w/ the
  StaggeredGridLayoutManager. It also hooks into the ViewModel's observable to
  react to changes in the underlying data (as a result of network service request
  being made from various parts of the app).

- **NetworkServiceTest.kt** contains the classes that connect to web services to
  load data over the network (GiphyClient SDK).

- **Unit tests (test/)** test classes in State.kt and some functions in
  NetworkService (using Roboelectric).

- **Instrumented tests (androidTest/)** test classes in NetworkServiceTest.kt over
  the network.

### Overview of the Java codebase

You can get the GitHub repo for the Java app
[here](https://github.com/nazmulidris/giphy_viewer).

The Java code is setup in a very similar fashion to the Kotlin one. However,
there are no unit or instrumented tests in this repo. Here's the mapping from
the Kotlin codebase to the Java one.

- **State.kt** -> **AppMode.java**, **DataEvent.java**
- **NetworkService.kt** -> **GipyhClient.java**
- **MyViewModel.kt** -> **AppViewModel.java**
- **RecyclerViewManager.kt** -> **RecyclerViewManager.java**
- **MyApplication.kt** -> N/A
- **FullScreenActivity.kt** -> **FullScreenActivity.java**
- **MainActivity.kt** -> **MainActivity.java**, **SearchViewManager.java**

## Differences between Java and Kotlin

If you use Android Studio itself to automatically convert Java code to Kotlin,
then you end up w/ code that isn't very idiomatic in Kotlin. I actually wrote
the Java version of the app first, then took inspiration from that to generate
the Kotlin version. And I tried to be idiomatic in Kotlin wherever I could think
of, and while I'm sure there are things in the app I can do better, I had to
make some major changes for the Kotlin version to be idiomatic in Kotlin.

Also, it really helped that I'm doing a lot of work w/ ES6 (JavaScript) because
I was able to think about high order functions and start writing the code w/
this in mind, rather than thinking in Java terms of interfaces and anonymous
inner classes. The following are some big differences that I was able to spot in
between the Java and Kotlin versions.

### Sealed data classes vs builders

One of the biggest wins in the Kotlin version was being able to use sealed data
classes, which eliminated so much boilerplate code over Java builder pattern
that it was quite shocking.

Here's an example of a builder in the Java version, which expresses an
`AppMode` which is something that can either be `Trending` or `Searching`.

Here's some code that shows `AppMode` being used:

```java
public AppViewModel(@NonNull Application application) {
  super(application);
  Fresco.initialize(application);
  appModeLiveData.setValue(
      AppMode.Builder
        .builder()
        .mode(AppMode.Mode.Trending)
        .build());
}
```

And here's the implementation of `AppMode` itself:

```java
/**
 * Specifies whether the app is in "search" or "trending" mode.
 *
 * <ol>
 * <li>With Search mode enabled, the "search" API endpoint is used.
 * <li>With it disabled, the "trending" API endpoint is used.
 * </ol>
 */
public class AppMode {

public static final class Builder {

  private Mode   mode  = Mode.Trending;
  private String query = null;

  public static Builder builder() {
    return new Builder();
  }

  public Builder mode(Mode mode) {
    this.mode = mode;
    return this;
  }

  public Builder query(String query) {
    this.query = query;
    return this;
  }

  public AppMode build() {
    return new AppMode(mode, query);
  }
}

private AppMode(@NonNull Mode mode, @Nullable String query) {
  this.mode = mode;
  this.query = query;
}

public enum Mode {
  Search,
  Trending
}

private Mode mode;

public boolean isTrendingMode() {
  return mode == Mode.Trending;
}

public boolean isSearchingMode() {
  return mode == mode.Search;
}

private String query;

public String getSearchQuery() {
  return query;
}

public String toString() {
  StringBuilder stringBuilder = new StringBuilder();
  switch (mode) {
    case Search:
      stringBuilder.append(Mode.Search.name()).append(", query:").append(query);
      break;
    case Trending:
      stringBuilder.append(Mode.Trending.name());
      break;
  }
  return stringBuilder.toString();
}
}
```

Whew! That is a lot of boilerplate code to express something that can be done in
Kotlin in the following lines 🙀:

```kotlin
/** User interaction causes a mode to be created and set on the UI. */
sealed class AppMode {
  data class Trending(val timestamp: Date = Date()) : AppMode()
  data class Search(val query: String, val timestamp: Date = Date()) : AppMode()
}
```

Using this is also so much simpler in Kolin (compared to the Java version):

```kotlin
appViewModel.appMode = AppMode.Trending()
appViewModel.appMode = AppMode.Search(query)
```

Also, w/ sealed classes, I can also use the `when` keyword:

```kotlin
fun makeRequest(appMode: AppMode,
              responseHandler: GiphyClientResponseHandler,
              offset: Int? = null
) = when (appMode) {
    is AppMode.Trending -> { /* Do stuff. */ }
    is AppMode.Search   -> { /* Do stuff. */ }
}
```

Similarly, there's a `DataEvent.java` class that gets shrunk in a similar
fashion in Kotlin.

```java
/**
 * Represents changes in underlying data (from the Giphy server). Changes can be
 * either:
 *
 * <ol>
 * <li>Refresh - entirely new data set is available.
 * <li>Update - more data was added to existing set (the amount of new data is
 * specified).
 * </ol>
 */
public class DataEvent {

public static final class Builder {

  private Type type    = Type.Refresh;
  private int  newSize = 0;

  public static Builder builder() {
    return new Builder();
  }

  public Builder type(Type mode) {
    this.type = mode;
    return this;
  }

  public Builder newSize(int newSize) {
    this.newSize = newSize;
    return this;
  }

  public DataEvent build() {
    return new DataEvent(type, newSize);
  }
}

private DataEvent(@NonNull Type mode, int query) {
  this.type = mode;
  this.newSize = query;
}

public enum Type {
  Refresh,
  GetMore,
  Error
}

private Type type;

public Type getType() {
  return type;
}

public boolean isErrorType() {
  return type == Type.Error;
}

public boolean isRefreshType() {
  return type == Type.Refresh;
}

public boolean isGetMoreType() {
  return type == Type.GetMore;
}

private int newSize;

public int getNewSize() {
  return newSize;
}

public String toString() {
  StringBuilder stringBuilder = new StringBuilder();
  switch (type) {
    case GetMore:
      stringBuilder.append(Type.Refresh.name()).append(", newSize:").append(newSize);
      break;
    case Refresh:
      stringBuilder.append(Type.Refresh.name());
      break;
    case Error:
      stringBuilder.append(Type.Error.name());
      break;
  }
  return stringBuilder.toString();
}
}
```

And here's the Kotlin version:

```kotlin
/**
 * GiphyClient responses result in this event being broadcast to various
 * parts of the UI that need to respond to these underlying data model changes.
 */
sealed class NetworkServiceResponse {
  data class Refresh(val timestamp: Date = Date()) : NetworkServiceResponse()
  data class Error(val timestamp: Date = Date()) : NetworkServiceResponse()
  data class More(val newSize: Int, val timestamp: Date = Date()) :
    NetworkServiceResponse()
}
```

Yup, it's incredible how much more terse and 'ergonomic' Kotlin is to use when
compared to Java 🎉.

### typedefs and lambdas vs interfaces

In the Java version, I was passing anonymous inner classes that implement
`Runnable` around to some functions. Here's an example:

```java
private final class ViewHolder {
  /* Snip. */
  void setupSwipeRefreshLayout() {
    onRefreshGestureHandler = () -> appViewModel.requestRefreshData(
        () -> swipeRefreshLayout.setRefreshing(false)
    );
    /* Snip. */
}
```

And in the `AppViewModel.java` class here's the function that takes the
`Runnable` parameter:

```java
public void requestRefreshData(@Nullable Runnable runOnRefreshComplete) {
  /* Snip. */
}
```

In Kotlin, instead of requiring `Runnable` blocks to be passed around, I
created the following `typedef`:

```kotlin
typealias BlockLambda = () -> Unit
```

And here's the `requestRefreshData()` function in Kotlin:

```kotlin
fun requestRefreshData(runOnComplete: BlockLambda? = null) {/* Snip. */}
```

And here's an example of calling this function:

```kotlin
appViewModel.requestRefreshData { swipeRefreshLayout.isRefreshing = false }
```

In the Kotlin version, if still using `Runnable` I could do something like the
following `Runnable {/* Do stuff. */}` but, since I'm writing all of the code in
Kotlin, by ditching `Runnable` and going w/ my `BlockLambda` typedef instead, I
can achieve the same result w/ the following `{/* Do stuff. */`}`. For more info
on single abstract method (SAM) conversions, [click
here](https://kotlinlang.org/docs/reference/java-interop.html#sam-conversions).

There are other places where I ended up using another `typedef` that I
created called `BlockWithSingleArgLambda` to pass lambdas around that simply
accepted a single argument.

```kotlin
typealias BlockWithSingleArgLambda<T> = (T) -> Unit
```

Here's an example of it being used in the `RecyclerView` `DataAdapter`:

```kotlin
dataAdapter = DataAdapter { it:Media ->
  activity.startActivity(FullScreenActivity.getIntent(activity, it))
}
```

In the lamda that I pass to the `DataAdapter` I simply use `it` to reference
the argument that I expect will be passed to my lambda.

Here's an example of this lambda that I'm passing acutally being executed:

```kotlin
private inner class RowViewHolder(
  cellView: View,
  val imageView: SimpleDraweeView = cellView.find(R.id.image_grid_cell)
) : RecyclerView.ViewHolder(cellView) {
fun bindDataToView(data: Media, block: BlockWithSingleArgLambda<Media>) {
  imageView.setOnClickListener { block.invoke(data) }
  /* Snip. */
}
}
```

This is so much cleaner IMO than having to define abstract classes or
interfaces to achieve the same result.

### Coroutines vs AsyncTask

The Kotlin version of the app has a feature that's not present in the Java
version which is that it shortens the URL of the GIF when the user clicks on a
thumbnail in the `RecyclerView` before copying that to the clipboard.

I decided to use coroutines, since I really like ES6 promises and async/await.
And while I've used `AsyncTask` and `Executors` quite extensively in the past, I
really like this new approach to async programming.

Here's an example of a coroutine that shortens the given URL string
(`shortenUrl()` actually does the work of shortening the URL by using a
`HttpURLConnection` that needs to be run in a background thread (and not the
main thread):

```kotlin
suspend fun shorten(longUrl: String): String {
  return suspendCoroutine { promise ->
    try {
      val shortUrl = shortenUrl(longUrl)
      promise.resume(shortUrl)
    }
    catch (e: Exception) {
      promise.resume(longUrl)
    }
  }
}
```

Here's code to call this coroutine from an Android activity:

```kotlin
private fun shortenUriAndCopyToClipboard(imageUri: Uri) {
val longUrl = imageUri.toString()
GlobalScope.launch(Dispatchers.IO) {
  lateinit var shortUrl: String
  try {
    shortUrl = shorten(longUrl)
    info { "coroutine-shortUrl: $shortUrl" }
  }
  catch (e: Exception) {
    shortUrl = longUrl
    info { "coroutine-copyUrlToClipboard exception! $e" }
  }
  copyTextToClipboard(shortUrl)
  toast(this@FullScreenActivity) {
    setText("URL copied to clipboard")
  }
}
}
```

### Extension function expressions

I love using extension function expressions when I can. Here are some examples:

```kotlin
inline fun toast(
    context: Context,
    text: String = "",
    duration: Int = Toast.LENGTH_SHORT,
    crossinline block: Toast.() -> Unit
) {
  runOnUiThread {
    with(Toast.makeText(context, text, duration)) {
      block()
      show()
    }
  }
}

fun runOnUiThread(block: BlockLambda) {
  Handler(Looper.getMainLooper()).post { block.invoke() }
}
```

I am still getting used to the ability to do things like `Toast.() -> Unit` 😁.

### Constructors

Another thing I noticed is that I was able to leverage the terse constructor
syntax of Kotlin to make it much simpler to pass arguments, and also defined
variables that operated on those variables in the constructor argument list
itself, instead of polluting the main function body w/ this code.

Here's an example where I pull out an `imageView` from a `cellView` which is
passed to this function:

```kotlin
private inner class RowViewHolder(
  cellView: View,
  val imageView: SimpleDraweeView = cellView.find(R.id.image_grid_cell)
) : RecyclerView.ViewHolder(cellView) {
fun bindDataToView(data: Media, block: BlockWithSingleArgLambda<Media>)
  {/*Snip. */}}
```

Another thing that I started using is `init` blocks and `apply` blocks in Kotlin
code, to put code to initialize a variable where I declare the variable
itself.

Here's an example of using `apply`:

```kotlin
private val layoutManager: StaggeredGridLayoutManager =
  StaggeredGridLayoutManager(GRID_SPAN_COUNT, VERTICAL)
      .apply {
        gapStrategy = GAP_HANDLING_MOVE_ITEMS_BETWEEN_SPANS
        recyclerView.layoutManager = this
      }
}
```

Here's an example of using `init`:

```kotlin
private var dataAdapter: DataAdapter
init {
  dataAdapter = DataAdapter {
    activity.startActivity(FullScreenActivity.getIntent(activity, it))
  }
  recyclerView.adapter = dataAdapter
}
```
