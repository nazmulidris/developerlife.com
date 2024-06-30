---
author: Nazmul Idris
date: 2021-02-06 10:00:00+00:00
excerpt: |
  Learn how to publish a Kotlin library as a gradle dependency to JitPack or GitHub Package Registry
layout: post
title: "Publishing a Kotlin library as a Gradle dependency to JitPack or GitHub Package Repository"
categories:
  - KT
---

<img class="post-hero-image" src="{{ 'assets/gradle-dep.svg' | relative_url }}"/>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [Using JitPack 👍](#using-jitpack-)
  - [Publish a dependency to JitPack](#publish-a-dependency-to-jitpack)
  - [maven-publish plugin](#maven-publish-plugin)
  - [publishing, groupId, artifactId, version](#publishing-groupid-artifactid-version)
  - [Build & publish locally first](#build--publish-locally-first)
  - [Prepare a release & publish](#prepare-a-release--publish)
  - [Import and use it](#import-and-use-it)
- [Using GitHub Package Registry (GPR) 👎](#using-github-package-registry-gpr-)
  - [Create a new GitHub repo for the actual code of the library](#create-a-new-github-repo-for-the-actual-code-of-the-library)
  - [Generate the personal access tokens that will be needed to publish and import](#generate-the-personal-access-tokens-that-will-be-needed-to-publish-and-import)
  - [Add GitHub Package Registry support to the build script so that the package can be published](#add-github-package-registry-support-to-the-build-script-so-that-the-package-can-be-published)
  - [Import this dependency into another gradle project](#import-this-dependency-into-another-gradle-project)
  - [References](#references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

I'm used to importing libraries that I need in gradle by simply adding them as a dependency for
implementation or testing in `build.gradle` or `build.gradle.kts`.

However, I've always been curious about how to publish my own dependency that can easily be used by
other projects.

This tutorial shows how to take a Kotlin library and publish it to the
[GitHub Package Registry](https://docs.github.com/en/packages/guides/configuring-gradle-for-use-with-github-packages)
and JitPack, as a dependency that can be used in gradle projects. I used to use JFrog Bintray but
both
[Bintray and JCenter are going to be shut down](https://www.infoq.com/news/2021/02/jfrog-jcenter-bintray-closure/)
in May 2021.

In this tutorial I will create the `color-console` library that allows console messages to be
colorized using ANSI color codes. Here is the end result snippet that we are looking to enable for
our `color-console` library.

## Using JitPack 👍

> ✨ This is much simpler than [GPR](#using-github-package-registry-gpr-) and the way to go for
> public dependencies.

This could not be any easier. It's really a 2 step process, once you have your library built with
gradle and its git repo pushed into GitHub. Let's use the following Kotlin library that's published
via JitPack as an example for this article:
[`color-console`](https://github.com/nazmulidris/color-console/).

### Publish a dependency to JitPack

### maven-publish plugin

Ensure that the `maven-publish` plugin is imported in `build.gradle.kts`.

```kotlin
plugins {
  java
  kotlin("jvm") version "1.6.0"
  `maven-publish`
}

repositories {
  mavenCentral()
}

dependencies {
  implementation(kotlin("stdlib-jdk8"))
  testImplementation("junit", "junit", "4.12")
}

tasks {
  compileKotlin {
    kotlinOptions.jvmTarget = "1.8"
  }
  compileTestKotlin {
    kotlinOptions.jvmTarget = "1.8"
  }
}

publishing {
  publications {
    create<MavenPublication>("maven") {
      groupId = "com.developerlife"
      artifactId = "color-console"
      version = "1.0.1"

      from(components["java"])
    }
  }
}
```

### publishing, groupId, artifactId, version

Without the `publishing` rule of `build.gradle.kts` you will get an error from JitPack even though
the `./gradlew build publishToMavenLocal` will work. This error will say
`ERROR: No build artifacts found`. Check out [this tutorial][2021-11-30.jp] for more info on this.

Even though the `groupId`, `artifactId`, `version` are specified inside the `publishing` rule above
it doesn't really get applied to the final artifact served up by JitPack. JitPack renames these
artifacts to something that reflects that they originated from `github.com` and the user
`nazmulidris`.

So the `dependencies` statement you find in a project's Gradle build file that depends on this
library doesn't match the identifiers specified in this rule:
`dependencies { implementation 'com.github.nazmulidris:color-console:Tag' }`. The following is
sanitized snippet from the [build log][2021-11-30.log] that JitPack generates that shows this
happening.

<!-- prettier-ignore-start -->

[2021-11-30.jp]: https://sami.eljabali.org/how-to-publish-a-kotlin-library-to-jitpack/#:~:text=without%20the%20above%2C%20jitpack%20will%20down%20the%20line%20show%20in%20your%20build%20log%20error%3A%20no%20build%20artifacts%20found%2C%20while%20building%20fine
[2021-11-30.log]: https://jitpack.io/com/github/nazmulidris/color-console/1.0.1/build.log

<!-- prettier-ignore-end -->

```text
------------------------------------------------------------
Gradle 7.0
------------------------------------------------------------
Build time:   2021-04-09 22:27:31 UTC
Revision:     d5661e3f0e07a8caff705f1badf79fb5df8022c4

Kotlin:       1.4.31
Groovy:       3.0.7
Ant:          Apache Ant(TM) version 1.10.9 compiled on September 27 2020
JVM:          1.8.0_252 (Private Build 25.252-b09)
OS:           Linux 4.18.0-25-generic amd64

Getting tasks: ./gradlew tasks --all
> Task :clean UP-TO-DATE
> Task :compileKotlin
> Task :compileJava NO-SOURCE
> Task :processResources NO-SOURCE
> Task :classes UP-TO-DATE
> Task :inspectClassesForKotlinIC
> Task :jar
> Task :assemble
> Task :check
> Task :build
> Task :generateMetadataFileForMavenPublication
> Task :generatePomFileForMavenPublication
> Task :publishMavenPublicationToMavenLocal
> Task :publishToMavenLocal

BUILD SUCCESSFUL in 7s
7 actionable tasks: 6 executed, 1 up-to-date
Looking for artifacts...
Looking for pom.xml in build directory and ~/.m2
Found artifact: com.developerlife:color-console:1.0.1

Build artifacts:
com.github.nazmulidris:color-console:1.0.1

Files:
com/github/nazmulidris/color-console/1.0.1
com/github/nazmulidris/color-console/1.0.1/build.log
com/github/nazmulidris/color-console/1.0.1/color-console-1.0.1-sources.jar
com/github/nazmulidris/color-console/1.0.1/color-console-1.0.1.jar
com/github/nazmulidris/color-console/1.0.1/color-console-1.0.1.module
com/github/nazmulidris/color-console/1.0.1/color-console-1.0.1.pom
com/github/nazmulidris/color-console/1.0.1/color-console-1.0.1.pom.md5
com/github/nazmulidris/color-console/1.0.1/color-console-1.0.1.pom.sha1
```

### Build & publish locally first

Before you can publish this library, make sure that you can run the following commands, that ensure
that JitPack can build this repo using gradle.

```shell
./gradlew clean
./gradlew build
./gradlew build publishToMavenLocal
```

### Prepare a release & publish

In order to publish this repo to JitPack you have to do the following things.

1. Make the changes that you want the repo, and commit and push it. Also, make sure that the library
   can be built by JitPack using the command shown above.
2. Update the `version` value in `build.gradle.kts`, this affects the JAR file that is built by
   JitPack. For consistency, the value here should match the release and tag value as well.
3. Get all the tags for this repo from GitHub using `git pull origin`. Then you can list the
   available tags using `git tag -l`.
4. Create a new tag. To create a new tag run this command `git tag <TAG_NAME>`, where `<TAG_NAME>`
   could be something like `1.0.1`. Just make sure not to clobber any existing tag name.
5. Publish the tag to GitHub using the following command `git push --tags`.
6. Finally create a new Release for this tag using
   [GitHub web interface](https://github.com/nazmulidris/color-console/releases).

> ⚡ Note, to delete a tag from GitHub you can run this command
> `git push --delete origin <TAG_NAME> ; git pull origin`. You can delete a tag from your local repo
> using `git tag -d <TAG_NAME>; git push origin --tags`. You can't manage releases though, which
> require the use of the GitHub web UI. Here's
> [more info](https://git-scm.com/book/en/v2/Git-Basics-Tagging) on git tagging.

### Import and use it

Then, in the project where you want to add this library as a dependency, eg:
[`idea-plugin-example`](https://github.com/nazmulidris/idea-plugin-example) you have to do the
following. You can import this dependency into your gradle projects by making the following changes
to your `build.gradle` or `build.gradle.kts` file.

1. Add this at the end of your `repositories` section.

   For `build.gradle`:

   ```groovy
   repositories {
     repositories {maven { url 'https://jitpack.io' }}
   }
   ```

   For `build.gradle.kts`:

   ```kotlin
   repositories {
     maven{
       url = uri("https://jitpack.io")
     }
   }
   ```

2. Add the dependency.

   For `build.gradle`:

   ```groovy
   dependencies { implementation 'com.github.nazmulidris:color-console:1.0.0' }
   ```

   For `build.gradle.kts`:

   ```kotlin
   dependencies { implementation ("com.github.nazmulidris:color-console:1.0.0") }
   ```

Information about this dependency on JitPack:

- You can find this dependency on JitPack
  [here](https://jitpack.io/#nazmulidris/color-console/1.0.0)
- You can find the JitPack build logs
  [here](https://jitpack.io/com/github/nazmulidris/color-console/1.0.0/build.log)

## Using GitHub Package Registry (GPR) 👎

> ⚠ GPR is complex and has authentication issues for public dependencies. People are [really
> unhappy][2021-11-30.gpr] about this.

<!-- prettier-ignore-start -->

[2021-11-30.gpr]: https://github.community/t/download-from-github-package-registry-without-authentication/14407

<!-- prettier-ignore-end -->

Desired snippet for `build.gradle.kts` (using Kotlin DSL):

```kotlin
repositories {
  maven {
    name = "GitHubPackages"
    url = uri("https://maven.pkg.github.com/nazmulidris/color-console")
    credentials {
      username = System.getenv("GITHUB_PACKAGES_USERID") ?: "nazmulidris"
      // Safe to share the password since it is a `read:package` scoped token.
      password = System.getenv("GITHUB_PACKAGES_IMPORT_TOKEN") ?: "22e9ba0d47c3e9116a2f1023867a1985beebfb60"
    }
  }
}

dependencies {
  implementation("com.developerlife:color-console:1.0")
}
```

Desired snippet for `build.gradle` (using Groovy):

```groovy
repositories {
  maven {
    name = "GitHubPackages"
    url = uri("https://maven.pkg.github.com/OWNER/REPOSITORY")
    credentials {
      username = System.getenv("GITHUB_PACKAGES_USERID") ?: "nazmulidris"
      // Safe to share the password since it is a `read:package` scoped token.
      password = System.getenv("GITHUB_PACKAGES_IMPORT_TOKEN") ?: "22e9ba0d47c3e9116a2f1023867a1985beebfb60"
    }
  }
}

dependencies {
  implementation 'com.developerlife:color-console:1.0'
}
```

### Create a new GitHub repo for the actual code of the library

The code that comprises the library, that will be built is in this
[GitHub repo](http://github.com/nazmulidris/color-console) for `color-console`.

Using IDEA create a Gradle + Java + Kotlin (JVM) project. Make sure it uses Kotlin and not Groovy
for the Gradle build script (I only got this working w/ the Kotlin DSL and not Groovy). It's a very
simple Kotlin and Gradle that has a single source file. Add the source code there and the following
steps are where things get interesting.

### Generate the personal access tokens that will be needed to publish and import

The first step is to create some [GitHub personal access tokens](https://github.com/settings/tokens)
that will do 2 things. You might consider saving them to global environment variables using whatever
shell you use.

1. `GITHUB_PACKAGES_PUBLISH_TOKEN` - this token has `repo, write:packages` scope. Do **NOT** share
   this!
2. `GITHUB_PACKAGES_IMPORT_TOKEN` - this token has `read:packages` scope. This is ok to share.

You might also consider saving the following environment variable too.

3. `GITHUB_PACKAGES_USERID` - this is the GitHub username for the token. This is ok to share.

### Add GitHub Package Registry support to the build script so that the package can be published

Edit the `build.gradle.kts` file to allow this library to be published to
[GitHub Packages](https://docs.github.com/en/packages/guides/configuring-gradle-for-use-with-github-packages).
Here are the high level steps.

1. Add some plugins so that we can publish this project to GitHub Packages.
2. Configure the maven publishing plugin.
   [More info](https://docs.gradle.org/current/userguide/publishing_maven.html).
3. To publish, you have to run the gradle task named `publish`. This will generate a release package
   for `color-console`.
4. Before publishing you might want to test that this works locally by using the
   `publishToMavenLocal` task which will generate the artifacts locally and save them to the
   `$HOME/.m2/repository/com/developerlife/color-console/` folder.

Here is what you need to add to your `build.gradle.kts`:

```kotlin
publishing {
  repositories {
    maven {
      name = "GitHubPackages"
      url = uri("https://maven.pkg.github.com/${myGithubUsername}/${myArtifactId}")
      credentials {
        username = System.getenv("GITHUB_PACKAGES_USERID")
        password = System.getenv("GITHUB_PACKAGES_PUBLISH_TOKEN")
      }
    }
  }
}

publishing {
  publications {
    register("gprRelease", MavenPublication::class) {
      groupId = myArtifactGroup
      artifactId = myArtifactId
      version = myArtifactVersion

      from(components["java"])

      artifact(sourcesJar)
      artifact(dokkaJavadocJar)

      pom {
        packaging = "jar"
        name.set(myArtifactId)
        description.set(myGithubDescription)
        url.set(myGithubHttpUrl)
        scm {
          url.set(myGithubHttpUrl)
        }
        issueManagement {
          url.set(myGithubIssueTrackerUrl)
        }
        licenses {
          license {
            name.set(myLicense)
            url.set(myLicenseUrl)
          }
        }
        developers {
          developer {
            id.set(myGithubUsername)
            name.set(myDeveloperName)
          }
        }
      }

    }
  }
}
```

Here is a
[link to the entire source file](https://github.com/nazmulidris/color-console/blob/main/build.gradle.kts)
so that you can see where these variables are defined and what the other functions are that generate
the docs and the JAR files using the `pom` function.

### Import this dependency into another gradle project

In order to load the package for the library from GitHub Packages Registry, the
[official docs](https://docs.github.com/en/packages/guides/configuring-gradle-for-use-with-github-packages)
provide some detailed examples of the provider side of things. And you can extrapolate what the
consumer side of things might look like. The biggest thing to keep in mind is that a `read:packages`
scoped GitHub personal access token will be required by the consumer of the package (and has to be
accessible their `build.gradle` or `build.gradle.kts` file).

Make sure to provide the following environment variables before you import this package.

1. `GITHUB_PACKAGES_IMPORT_TOKEN` - this token has `read:packages` scope. This is ok to share.
2. `GITHUB_PACKAGES_USERID` - this is the GitHub username for the token. This is ok to share.

Here is more information on
[how to declare your own maven repositories](https://docs.gradle.org/current/userguide/declaring_repositories.html)
using gradle.

To import this library into your Gradle project, please add the following lines in your
`build.gradle` file in order to use this library (in Groovy).

```groovy
repositories {
  maven {
    name = "GitHubPackages"
    url = uri("https://maven.pkg.github.com/nazmulidris/color-console")
    credentials {
      username = System.getenv("GITHUB_PACKAGES_USERID") ?: "nazmulidris"
      // Safe to share the password since it is a `read:package` scoped token.
      password = System.getenv("GITHUB_PACKAGES_IMPORT_TOKEN") ?: "22e9ba0d47c3e9116a2f1023867a1985beebfb60"
    }
  }
}

dependencies {
    implementation 'com.developerlife:color-console:1.0'
}
```

Here's the Kotlin DSL version for `build.gradle.kts`:

```kotlin
repositories {
  maven {
    name = "GitHubPackages"
    url = uri("https://maven.pkg.github.com/nazmulidris/color-console")
    credentials {
      username = System.getenv("GITHUB_PACKAGES_USERID") ?: "nazmulidris"
      // Safe to share the password since it is a `read:package` scoped token.
      password = System.getenv("GITHUB_PACKAGES_IMPORT_TOKEN") ?: "22e9ba0d47c3e9116a2f1023867a1985beebfb60"
    }
  }
}

dependencies {
  implementation("com.developerlife:color-console:1.0")
}
```

### References

- [Tutorial on using GitHub Package Registry to publish and import Android Kotlin library](https://medium.com/@stpatrck/publish-an-android-library-to-github-packages-8dfff3ececcb)
- [Tutorial on using GitHub Package Registry to import something from GitHub Package Registry](https://ppulikal.medium.com/publishing-android-libraries-to-the-github-package-registry-part-2-3c5aab31f477)
- [Full `build.gradle.kts` example for tutorial above](https://gist.github.com/prasad79/523cfea10a3748992c8d1cb3fc04eda5)
- [Discussion about why it is bad to need a token to import packages](https://github.community/t/download-from-github-package-registry-without-authentication/14407/44)
- [Discussion about Kotlin versions and the DSL to publish
  packages](https://github.community/t/how-to-configure-gradle-github-package-registry-maven/14247/9
