---
author: Nazmul Idris
date: 2018-10-21 5:00:00+00:00
excerpt: |
  This tutorial is an exploration of doing test driven development using Kotlin. This tutorial 
  focuses on JUnit, MockK, AssertJ, and Roboelectric for Android.
layout: post
hero-image: assets/kotlin-android-test-hero.svg
title: "Kotlin and Test Driven Development"
categories:
- TDD
- KT
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Test driven development and Kotlin](#test-driven-development-and-kotlin)
- [Using Kotlin DSL for gradle](#using-kotlin-dsl-for-gradle)
- [Loading JUnit5, MockK, AssertJ, and Roboelectric](#loading-junit5-mockk-assertj-and-roboelectric)
- [Defining some unit tests](#defining-some-unit-tests)
  - [Example 1](#example-1)
  - [Example 2](#example-2)
- [References](#references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Test driven development and Kotlin

As of October 2018, test driven development on Android is primarily focused on using JUnit4, and Mockito for unit
testing. These don't work very well w/ Kotlin. By default Kotlin classes are final, and so Mockito has a hard time
mocking them. Additionally, JUnit4 doesn't play well w/ lambdas. For these reasons, JUnit5 and MockK are better when
writing unit tests in Kotlin.

Please use the following resources to dive into more details on the following related topics.

1. [Test driven development on Android](https://developer.android.com/training/testing/fundamentals)
1. [Best practices for unit testing in Kotlin blog post](https://blog.philipphauer.de/best-practices-unit-testing-kotlin/)
1. [Best practices for unit testing in Kotlin video](https://www.youtube.com/watch?v=RX_g65J14H0)

This tutorial is purely focused on unit testing (not end to end, integration, or instrumented testing). There are quite
a few dependencies that need to be accommodated before the first unit test can be written, and for that I will use the
Kotlin DSL for gradle script (and not Groovy) in this tutorial and it's related project on
[github](https://github.com/nazmulidris/places-api-poc/).

## Using Kotlin DSL for gradle

In order to use Kotlin DSL for gradle, rather than Groovy, the first thing to do is use
[`buildSrc`](https://docs.gradle.org/current/userguide/organizing_gradle_projects.html#sec:build_sources) where will
create a Kotlin file that holds all our dependencies.

There's a [Gradle Migration Guide](https://guides.gradle.org/migrating-build-logic-from-groovy-to-kotlin/) that will
provide you with more details on how to get this done.

> In order to be able to load a project into Android Studio, there must be a `build.gradle` file in the root folder of
> the project, which can be empty. The main logic will be in the `build.gradle.kts` file instead.

```kotlin
object TestingDeps {
    data class Versions(val assertj: String = "3.11.1",
                        val junit5: String = "5.2.0",
                        val mockk: String = "1.8.9",
                        val roboelectric: String = "3.8",
                        val junit4: String = "4.12")

    val versions = Versions()

    val junit5_jupiter = "org.junit.jupiter:junit-jupiter-api:${versions.junit5}"
    val junit5_jupiter_runtime = "org.junit.jupiter:junit-jupiter-engine:${versions.junit5}"
    val junit5_jupiter_params = "org.junit.jupiter:junit-jupiter-params:${versions.junit5}"
    val junit4_legacy = "junit:junit:${versions.junit4}"
    val junit5_vintage = "org.junit.vintage:junit-vintage-engine:${versions.junit5}"

    val assertj = "org.assertj:assertj-core:${versions.assertj}"

    val mockk = "io.mockk:mockk:${versions.mockk}"

    val roboelectric = "org.robolectric:robolectric:${versions.roboelectric}"
}
```

> You can see the `buildSrc` folder of the project used in this tutorial
> [here](https://github.com/nazmulidris/places-api-poc/tree/main/buildSrc).

Since I'm using Kotlin for test code, and my source code, the source sets needed to be updated as well. This is done in
the app module's `build.gradle.kts` file (in the `android` section)

```kotlin
android {
    // For JUnit5 tests.
    // More info : https://stackoverflow.com/a/46440810/2085356
    // More info : https://github.com/gradle/kotlin-dsl/issues/443
    sourceSets {
        getByName("main").java.srcDir("src/main/kotlin")
        getByName("test").java.srcDir("src/test/kotlin")
    }
}
```

Here are some links with gradle build scripts used in this project.

1. [buildSrc build.gradle.kts](https://github.com/nazmulidris/places-api-poc/blob/main/buildSrc/build.gradle.kts). This
   loads the Kotlin DSL for gradle, so that Kotlin can be used to declare all the dependencies, in the
   [Dependencies.kt](https://github.com/nazmulidris/places-api-poc/blob/main/buildSrc/src/main/kotlin/Dependencies.kt)
   file.
1. [Top level build.gradle.kts](https://github.com/nazmulidris/places-api-poc/blob/main/build.gradle.kts)
1. [Top level settings.gradle](https://github.com/nazmulidris/places-api-poc/blob/main/settings.gradle)
1. [App module build.gradle.kts](https://github.com/nazmulidris/places-api-poc/blob/main/app/build.gradle.kts)

## Loading JUnit5, MockK, AssertJ, and Roboelectric

In order to get JUnit5 into the project, you can use the
[android-junit5](https://github.com/mannodermaus/android-junit5) gradle plugin. Sadly, there's no easier way to
automatically add support for JUnit5 (as of this Oct 2018).

In order to use Roboelectric 3.8, you will also need JUnit4 via JUnit5 Vintage support. And you will have to ensure that
you app doesn't target API level 28.

These are the entries in the `build.gradle.kts` file for the app module that are required to import all the
dependencies.

```kotlin
plugins {
    id("de.mannodermaus.android-junit5")
}

android {
    lintOptions.isAbortOnError = false

    // For JUnit5 tests.
    // More info : https://stackoverflow.com/a/46440810/2085356
    // More info : https://github.com/gradle/kotlin-dsl/issues/443
    sourceSets {
        getByName("main").java.srcDir("src/main/kotlin")
        getByName("test").java.srcDir("src/test/kotlin")
    }

    // For Roboelectric.
    testOptions.unitTests.setIncludeAndroidResources(true)
}


// Testing w/ JUnit5 & AssertJ.
run {

    dependencies {
        // Add JUnit5 dependencies.
        testImplementation(TestingDeps.junit5_jupiter)
        testRuntimeOnly(TestingDeps.junit5_jupiter_runtime)
        testImplementation(TestingDeps.junit5_jupiter_params)

        // Add JUnit4 legacy dependencies.
        testImplementation(TestingDeps.junit4_legacy)
        testRuntimeOnly(TestingDeps.junit5_vintage)

        // Add AssertJ dependencies.
        testImplementation(TestingDeps.assertj)

        // Add MockK dependencies.
        testImplementation(TestingDeps.mockk)

        // Add Roboelectric dependencies.
        testImplementation(TestingDeps.roboelectric)
    }

    // Need this to use Java8 in order to use certain features of JUnit5 (such as calling static
    // methods on interfaces).

    // More info : https://github.com/mannodermaus/android-junit5/wiki/Getting-Started
    // More info : https://stackoverflow.com/a/45994990/2085356

    // For Kotlin sources.
    tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
        kotlinOptions.jvmTarget = "1.8"
    }

    // For Java sources.
    java {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
}
```

## Defining some unit tests

With the dependencies sorted, and sourceSets created, it is now possible to create unit tests!

- You can use AssertJ, MockK, and JUnit5.
- Or you can use JUnit5 Vintage (JUnit4 support) for tests that require Roboelectric.

### Example 1

Here's an example of a unit test that requires Roboelectric to function. Note how you can have spaces in Kotlin function
names as long as you escape them with backticks. This makes test names easier to read!

```kotlin
/**
 * This class uses Roboelectric to mock [android.net.Uri] and it uses the
 * [org.junit.Test] annotation from JUnit4 (and not JUnit5). Also,
 * @[org.junit.runner.RunWith] is JUnit4 (and not JUnit5).
 *
 * Currently (as of Oct 19 2018) Roboelectric doesn't work w/ JUnit5,
 * and also doesn't work w/ API level 28, which is why these changes
 * have to be made.
 */
@RunWith(RobolectricTestRunner::class)
class PlaceWrapperTest {

    @Test
    fun `Convert valid GMS object into PlaceWrapper`() {

        val place = mockk<Place>().apply {
            every { id } returns "placeId"
            every { placeTypes } returns listOf(Place.TYPE_CAFE, Place.TYPE_CAR_DEALER)
            every { address } returns "address"
            every { locale } returns Locale("en")
            every { name } returns "name"
            every { latLng } returns LatLng(-33.880490, 151.184363)
            every { viewport } returns LatLngBounds(
                    LatLng(-33.880490, 151.184363),
                    LatLng(-33.858754, 151.229596))
            every { websiteUri } returns Uri.parse("http://google.com")
            every { phoneNumber } returns "1231231234"
            every { rating } returns 4.4f
            every { priceLevel } returns -1
            every { attributions } returns "n/a"
            every { freeze() } returns this
        }

        with(PlaceWrapper(place, 1f)) {
            assertThat(id).isEqualTo("placeId")
            assertThat(placeTypes).containsAll(
                    listOf(Place.TYPE_CAFE, Place.TYPE_CAR_DEALER))
            assertThat(address).isEqualTo("address")
            assertThat(locale).isEqualTo(Locale("en"))
            assertThat(name).isEqualTo("name")
            assertThat(latLng).isEqualTo(LatLng(-33.880490, 151.184363))
            assertThat(viewport).isEqualTo(LatLngBounds(
                    LatLng(-33.880490, 151.184363),
                    LatLng(-33.858754, 151.229596)))
            assertThat(websiteUri).isEqualTo(Uri.parse("http://google.com"))
            assertThat(phoneNumber).isEqualTo("1231231234")
            assertThat(rating).isCloseTo(4.4f, Percentage.withPercentage(1.0))
            assertThat(priceLevel).isEqualTo(-1)
            assertThat(attributions).isEqualTo("n/a")
        }

    }

    @Test
    fun `Convert incomplete GMS object into PlaceWrapper`() {

        val place = mockk<Place>().apply {
            every { id } returns null
            every { placeTypes } returns listOf()
            every { address } returns null
            every { locale } returns Locale("en")
            every { name } returns "name"
            every { latLng } returns LatLng(-33.880490, 151.184363)
            every { viewport } returns null
            every { websiteUri } returns Uri.parse("http://google.com")
            every { phoneNumber } returns ""
            every { rating } returns 4.4f
            every { priceLevel } returns -1
            every { attributions } returns "n/a"
            every { freeze() } returns this
        }

        with(PlaceWrapper(place, 1f)) {
            assertThat(id).isNull()
            assertThat(placeTypes).isEmpty()
            assertThat(address).isNull()
            assertThat(locale).isEqualTo(Locale("en"))
            assertThat(name).isEqualTo("name")
            assertThat(latLng).isEqualTo(LatLng(-33.880490, 151.184363))
            assertThat(viewport).isNull()
            assertThat(websiteUri).isEqualTo(Uri.parse("http://google.com"))
            assertThat(phoneNumber).isEmpty()
            assertThat(rating).isCloseTo(4.4f, Percentage.withPercentage(1.0))
            assertThat(priceLevel).isEqualTo(-1)
            assertThat(attributions).isEqualTo("n/a")
        }

    }
}
```

### Example 2

Here's another example of a unit test that requires Roboelectric.

```kotlin
/**
 * This class uses Roboelectric to mock [android.util.Log.i] and it uses the
 * [org.junit.Test] annotation from JUnit4 (and not JUnit5). Also,
 * @[org.junit.runner.RunWith] is JUnit4 (and not JUnit5).
 *
 * Currently (as of Oct 19 2018) Roboelectric doesn't work w/ JUnit5, and
 * also doesn't work w/ API level 28, which is why these changes have
 * to be made.
 */
@RunWith(RobolectricTestRunner::class)
class AutocompletePredictionDataTest {

    @Test
    fun `Parse with non null and non empty fields from GMS object`() {
        val gmsObject: AutocompletePrediction =
                mockk<AutocompletePrediction>().apply {
                    every { getFullText(null) } returns "fullText"
                    every { getPrimaryText(null) } returns "primaryText"
                    every { getSecondaryText(null) } returns "secondaryText"
                    every { placeId } returns "placeId"
                    every { placeTypes } returns listOf()
                }

        with(gmsObject.parse()) {
            assertThat(fullText).isNotBlank()
            assertThat(primaryText).isNotBlank()
            assertThat(secondaryText).isNotBlank()
            assertThat(placeId).isNotBlank()
            assertThat(placeTypes).isNotNull
        }
    }

    @Test
    fun `Parse with some null or empty fields from GMS object`() {
        val gmsObject: AutocompletePrediction =
                mockk<AutocompletePrediction>().apply {
                    every { getFullText(null) } returns "fullText"
                    every { getPrimaryText(null) } returns null
                    every { getSecondaryText(null) } returns ""
                    every { placeId } returns null
                    every { placeTypes } returns null
                }

        with(gmsObject.parse()) {
            assertThat(fullText).isNotBlank()
            assertThat(primaryText).isBlank()
            assertThat(secondaryText).isBlank()
            assertThat(placeId).isBlank()
            assertThat(placeTypes).isEmpty()
        }
    }

}
```

> You can see all the tests for this project on
> [github](https://github.com/nazmulidris/places-api-poc/tree/main/app/src/test/kotlin).

## References

- [AssertJ](http://joel-costigliola.github.io/assertj/assertj-core-quick-start.html)
- [MockK](https://github.com/mockk/mockk)
- [Roboelectric](http://robolectric.org/getting-started/)
- [android-junit5 gradle plugin](https://github.com/mannodermaus/android-junit5)
- [Migrating from JUnit4 to JUnit5](https://www.baeldung.com/junit-5-migration)
- [Tutorial on using JUnit5 for Android w/ Kotlin](https://blog.stylingandroid.com/junit-5-kotlin/)
