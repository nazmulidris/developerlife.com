---
author: Nazmul Idris
date: 2020-11-21 05:19:43+00:00
excerpt: |
  Introduction to creating plugins using JetBrains Plugin SDK covering these topics: PicoContainer,
  Services, plugin.xml, actions, extension points, extensions, testing, and the intellij-plugin-verifier.
  This is a companion of the Advanced guide to creating IntelliJ IDEA plugins.
layout: post
title: "Introduction to creating IntelliJ IDEA plugins"
categories:
  - IJ
  - KT
  - TDD
---

<img class="post-hero-image" src="{{ 'assets/jetbrains-plugin.svg' | relative_url }}"/>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [What are plugins?](#what-are-plugins)
  - [plugin.xml - "entry point" into your plugin](#pluginxml---entry-point-into-your-plugin)
  - [Declarative nature and dependency injection](#declarative-nature-and-dependency-injection)
  - [Actions](#actions)
  - [Dynamic plugins](#dynamic-plugins)
  - [Main thread, performance, and UI freezes](#main-thread-performance-and-ui-freezes)
  - [Extending your plugin or another plugin](#extending-your-plugin-or-another-plugin)
  - [References](#references)
- [Plugin architecture](#plugin-architecture)
  - [PicoContainer](#picocontainer)
  - [plugin.xml](#pluginxml)
  - [Migrating from Components to Dynamic Plugins (2020-07-17)](#migrating-from-components-to-dynamic-plugins-2020-07-17)
  - [Components (deprecated)](#components-deprecated)
  - [Extensions and extension points](#extensions-and-extension-points)
  - [Services](#services)
- [Persisting state between IDE restarts](#persisting-state-between-ide-restarts)
  - [PersistentStateComponent and Services](#persistentstatecomponent-and-services)
- [Actions](#actions-1)
- [IntelliJ platform version, Gradle version, Kotlin version, gradle-intellij-plugin, intellij-plugin-verifier](#intellij-platform-version-gradle-version-kotlin-version-gradle-intellij-plugin-intellij-plugin-verifier)
  - [intellij-plugin-verifier](#intellij-plugin-verifier)
    - [Notes on the build or version codes](#notes-on-the-build-or-version-codes)
  - [Using the latest version of Gradle and gradle-intellij-plugin](#using-the-latest-version-of-gradle-and-gradle-intellij-plugin)
  - [In build.gradle.kts which intellij version should we use?](#in-buildgradlekts-which-intellij-version-should-we-use)
- [Declaring dependencies on other plugins](#declaring-dependencies-on-other-plugins)
- [Misc](#misc)
  - [Analyze startup performance](#analyze-startup-performance)
  - [How to use project specific JDKs](#how-to-use-project-specific-jdks)
  - [Using ResourceBundles for localization](#using-resourcebundles-for-localization)
    - [Imperative approach](#imperative-approach)
    - [Declarative approach](#declarative-approach)
- [Testing](#testing)
  - [AssertJ](#assertj)
  - [Example tests](#example-tests)
    - [Fixtures](#fixtures)
    - [Test data](#test-data)
    - [Mocking actions](#mocking-actions)
- [References](#references-1)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

This tutorial (originally published on 2019-08-25) covers the basics of creating a plugin for
IntelliJ IDEA using the Plugin SDK. It covers the basics, like what components and services are,
what extension points and extensions are, along with persistent state components, and unit testing.
Topics like disposables, PSI, VFS, read/write locks, are not covered in this tutorial. I will write
more tutorials in the future to cover these advanced topics as well.

To get the code for this tutorial, please clone the
[`nazmulidris/idea-plugin-example`](https://github.com/nazmulidris/idea-plugin-example) repo from
github. Please checkout the README for this repo, and clone it to your computer, and get it running
before following along in this tutorial. It's much easier when you have some real code and examples
to play with in the IDE to understand the concepts in this very long tutorial.

There is quite a lot of information to absorb as you embark on this journey! The following is a link
to the official JetBrains Platform SDK docs to create a plugin from scratch. In this tutorial we
will cover using the gradle based plugin (and not the old Plugin DevKit based approach).

- [Getting started w/ Gradle based IntelliJ Platform Plugin](http://www.jetbrains.org/intellij/sdk/docs/tutorials/build_system/prerequisites.html).

Once you are done with the basics, and want to get into more advanced topics, please read the
[Advanced guide to creating IntelliJ IDEA
plugins]({{ '2021/03/13/ij-idea-plugin-advanced/' | relative_url }}).

## What are plugins?

IntelliJ IDEA is a very powerful IDE platform. This platform is used to roll out a variety of IDEs
(eg: IntelliJ Community Edition (FOSS), IntelliJ Ultimate, Android Studio, Webstorm, etc). You can
find the source code for the Community Edition in this repo
[`intellij-community`](https://github.com/JetBrains/intellij-community). The platform SDK is part of
this repo.

JetBrains allows you or anyone to extend their IDE in any way that they choose by writing their own
[plugin](https://plugins.jetbrains.com/docs/intellij/types-of-plugins.html). IDEA itself is
comprised of a very small core set of classes, with a ton of plugins that are supplied by JetBrains.

So if you are thinking of writing a plugin to extend the functionality of IDEA, then you have come
to the right place. Think of your plugin as an application that will live in the container of the
IDEA window in a desktop environment. There are some rules that you have to comply with in order to
be a good citizen of this container. This tutorial will guide you through some of what these
constraints are.

### plugin.xml - "entry point" into your plugin

When creating a plugin, you must let the "IDEA container" know what your plugin actually does, so
that IDEA can load it properly and allow users to interact with it (via keyboard shortcuts, menus,
toolbars). Things like the name of your plugin, associate icons, internationalized string bundles,
etc all have to be provided to IDEA so that it can render your plugin properly. All of this
declarative information about your plugin is stored in a file called
[`plugin.xml`](https://plugins.jetbrains.com/docs/intellij/plugin-configuration-file.html) which is
the most important "entry point" into the code for your plugin.

### Declarative nature and dependency injection

IDEA itself uses [PicoContainer](http://picocontainer.com/) to load all the classes required by your
plugin via very simple dependency injection. This is why all of the things in `plugin.xml` tend to
be declarative. You won't find any calls to constructors and such. IDEA uses something like
[`classgraph`](https://github.com/classgraph/classgraph/wiki) in order to look thru its various
classpaths and figure out which actual classes to load at runtime.
[Here](https://github.com/nazmulidris/algorithms-in-kotlin) is an example of how you can use
`classgraph` in your Kotlin / Java code.

### Actions

One of the main ways in which IDEA users will interact with your plugin is via
[actions](https://plugins.jetbrains.com/docs/intellij/action-system.html). Actions can be invoked by
using Search Anywhere (`Shift + Shift`) and typing the name of the action. Or by pressing the
keyboard shortcut to invoke that action. Or by clicking on a toolbar that has the action, or
selecting a menu that is mapped to this action. All the actions that are exposed by your plugin are
explicitly listed in this `plugin.xml` file.

### Dynamic plugins

All IDEA plugins need to be
[dynamic](https://plugins.jetbrains.com/docs/intellij/dynamic-plugins.html). This means they can be
unloaded and loaded on demand. So if the user uninstalls your plugin it should not require an IDE
restart. Similarly if they install your plugin, or upgrade it, it should not require an IDE restart.
For this reason you can think of your plugin as a set of actions, and a set of
[services](https://plugins.jetbrains.com/docs/intellij/plugin-services.html) that can be provided on
demand. You can learn more about services in
[Services]({{ '2020/11/20/idea-plugin-example-intro/#services' | relative_url }}).

There are tasks that your plugin might need to happen when a project is first opened that requires
the use of this plugin. You can handle this by declaring the use of the
[`backgroundPostStartupActivity`](https://plugins.jetbrains.com/intellij-platform-explorer/?extensions=com.intellij.backgroundPostStartupActivity)
extension point. You may also have tasks that might need to happen when the IDE itself is started in
which can you try using the
[`AppLifecycleListener`](https://github.com/gilday/dark-mode-sync-plugin/pull/24#discussion_r486033893).

### Main thread, performance, and UI freezes

So following is another reason dynamic plugins and the declarative nature of `plugin.xml` go hand in
hand - performance. In order for IDEA itself to load quickly, plugins that are not needed by any
open projects should not be loaded at startup. If the user opens a project, then only the plugins
required by that project should be loaded without making the IDE unresponsive, or at least be
delayed after the UI is responsive. A lot of code in IDEA runs in the UI (main) thread. This is
unfortunate and unavoidable for a lot of reasons (which will become clear when you learn about
[PSI](https://plugins.jetbrains.com/docs/intellij/psi.html) and
[VFS](https://plugins.jetbrains.com/docs/intellij/files.html); more about these in the [advanced
tutorial]({{ '2021/03/13/ij-idea-plugin-advanced/' | relative_url }})). In order to be a "good
citizen" in the IDE container itself, your plugin will need to do things that are unintuitive just
so that it
[does not freeze](https://plugins.jetbrains.com/docs/intellij/performance.html#avoiding-ui-freezes)
the main thread, and make the IDE itself unresponsive to the user.

### Extending your plugin or another plugin

Even your plugin can be built in a way that it can be extended by other plugins! And your plugin can
extend another plugin created by someone else. These are called `extension points` and `extensions`
and you can learn about them in detail in [Extensions and extension
points]({{ '2020/11/20/idea-plugin-example-intro/#extensions-and-extension-points' | relative_url }}).

### References

Docs:

1. [Introduction to creating IntelliJ IDEA
   plugins]({{ '2020/11/20/idea-plugin-example-intro/' | relative_url }})
2. [Official JetBrains IntelliJ Platform SDK docs](https://plugins.jetbrains.com/docs/intellij/welcome.html)
3. [Official JetBrains IntelliJ Platform Explorer (extension point explorer)](https://plugins.jetbrains.com/intellij-platform-explorer/)

Code examples (GitHub repos):

1. [idea-plugin-example](https://github.com/nazmulidris/idea-plugin-example)
2. [idea-plugin-example2](https://github.com/nazmulidris/idea-plugin-example2)
3. [shorty-idea-plugin](https://github.com/r3bl-org/shorty-idea-plugin)
4. [intellij-community](https://github.com/JetBrains/intellij-community)

## Plugin architecture

An IDEA plugin really is an extension of the IDE that you are writing. Most of IDEA itself is
constructed as a set of plugins that are layered on top of the base platform code.

- Each plugin has a `plugin.xml` file which is a manifest that declares what is inside the plugin
  and how it hooks into IDEA itself. If you're familiar w/ Android, this is similar to the
  `AndroidManifest.xml` file.
- Each plugin gets its own classloader, and IDEA itself uses PicoContainer (more on this below) to
  perform dependency injection to handle loading classes via reflection.
- In many situations in IDEA, classes are loaded via reflection, and there are even situations where
  classes loaded by a classloader are indexed and searched. Here's a github repo for a really fast
  classpath scanner called [classgraph](https://github.com/classgraph/classgraph) to give you an
  idea of how this might work.

### PicoContainer

IDEA uses [PicoContainer](http://picocontainer.com/introduction.html) for dependency injection (DI).

- PicoContainer is a very simple DI engine that supports both constructor and field injection
  injection and uses Java reflection. Even though it supports field injection, IDEA uses it
  primarily for constructor injection.
- [Here's a github repo](https://github.com/avh4/picocontainer-example) which contains some examples
  of how to use PicoContainer.

When IDEA itself launches, it uses PicoContainer to manage loading all of its classes, interfaces,
and objects. And this is extended to any plugin that you write (to extend IDEA itself). So you don't
really manage the lifecycle of your plugin, IDEA does. And it does it via PicoContainer components.

When your plugin is loaded into IDEA, PicoContainer is used to instantiate the classes that your
plugin provides to IDEA itself, and this is where things like project and application components can
be injected into the constructors of your components (more on this below).

### plugin.xml

This is a really important file that really tells IDEA about what is inside of your component and
how IDEA should deal with loading it, and having it interact w/ other 3rd party components, and IDEA
itself. This is very similar to `AndroidManifest.xml` if you're used to Android development.

In this file you have to declare the `id` of your plugin. This is a really important piece of
information as this will be used as a "namespace" for many of the things that are listed below.

You also have to list all the components, services, and actions that your plugin provides to IDEA in
this file.

Here's an example of a `plugin.xml` file.

- It provides a custom extension point that allows some extensions (which are simple `Runnable`
  classes that are run at IDE startup).
  - The `extensionPoint` is called `configuratorRunnable`.
  - The `postStartupActivity` implemented by `extensionPoints.ConfiguratorComponent.kt` finds all
    its `extensions` (declared below) after the IDE finishes loading and does "something" with each
    of them.
  - Two `extensions` each of which implement the `configuratorRunnable` extension point (declared
    above) which is simply `Runnable`.
- A `PersistentStateComponent` called `services.LogService` is also declared which is a
  `applicationService`. Services are the preferred way of creating plugin functionality since they
  don't all have to be created until actually needed.
  - Note that if you use
    [light services](https://jetbrains.org/intellij/sdk/docs/basics/plugin_structure/plugin_services.html#light-services)
    then there's no need to have this block in `plugin.xml`.
- It exposes a bunch of actions and specifies where these actions should appear.
- It creates a menu group and adds some actions to it.

More on all of this in the following sections.

```xml
<idea-plugin>
  <!-- Namespace of this plugin. Used in extensions and extension points. -->
  <id>com.developerlife.example.idea-plugin-example</id>
  <name>developerlife example</name>
  <vendor email="support@developerlife.com" url="http://developerlife.com">
    developerlife.com
  </vendor>

  <description><![CDATA[
    This sample plugin does the following things ...
    ]]></description>

  <!-- Add post startup activity to load extensions for our custom extension point. -->
  <extensions defaultExtensionNs="com.intellij">
    <postStartupActivity implementation="extensionPoints.ConfiguratorStartupActivity" />
  </extensions>

  <!-- Extension point for the application component above. -->
  <extensionPoints>
    <extensionPoint name="configuratorRunnable"
        interface="java.lang.Runnable" />
  </extensionPoints>

  <!-- Extensions that run when the application component above is
  initialized. -->
  <extensions
      defaultExtensionNs="com.developerlife.example.idea-plugin-example">
    <configuratorRunnable order="first"
        implementation="extensions.AnInitializer"
        id="MyPlugin.extensions.AnInitializer" />
    <configuratorRunnable order="last"
        implementation="extensions.AnotherInitializer"
        id="MyPlugin.extensions.AnotherInitializer" />
  </extensions>

  <!-- Extension to publish the LogService. -->
  <extensions defaultExtensionNs="com.intellij">
    <applicationService serviceImplementation="services.LogService" />
  </extensions>

  <!-- Add SearchOnStackOverflowAction to both the EditorPopupMenu and
  ConsoleEditorPopupMenu -->
  <actions>
    <action id="MyPlugin.Editor.actions.SearchOnStackOverflowAction"
        class="actions.SearchOnStackOverflowAction"
        text="Search on Stack Overflow"
        description="Search selected text on Stack Overflow"
        icon="/icons/ic_stackoverflow.svg">
      <add-to-group group-id="EditorPopupMenu" anchor="last" />
      <add-to-group group-id="ConsoleEditorPopupMenu" anchor="last" />
    </action>
  </actions>

  <!-- Create a new Greeting menu and add the following to it: HelloAction and
  AskQuestionOnStackOverflowAction. -->
  <actions>
    <!-- Create a new Greeting menu -->
    <group id="MyPlugin.SampleMenu" text="Greeting" description="Greeting menu">
      <add-to-group group-id="MainMenu" anchor="last" />

      <!-- Add HelloAction to the Greeting menu -->
      <action id="MyPlugin.actions.HelloAction" class="actions.HelloAction"
          text="Hello" description="Says hello"
          icon="/icons/ic_check_circle.svg">
        <add-to-group group-id="MainMenu" anchor="first" />
      </action>

      <!-- Add AskQuestionOnStackOverflowAction to the Greeting menu -->
      <action id="MyPlugin.actions.AskQuestionOnStackOverflowAction"
          class="actions.AskQuestionOnStackOverflowAction" text="Ask Question"
          description="Opens a browser" icon="/icons/ic_stackoverflow.svg">
        <add-to-group group-id="MainMenu" anchor="last" />
      </action>
    </group>
  </actions>
</idea-plugin>
```

### Migrating from Components to Dynamic Plugins (2020-07-17)

Components are now deprecated, so just use services instead. To migrate your plugin to be Dynamic,
use the following links to determine how to make the switch. Dynamic Plugins allow IDEA to
load/unload/reload your plugin w/out restarting IDEA and it makes IDEA much faster to startup, and
more memory and CPU efficient as well (when done correctly).

- [Plugin extension points](https://jetbrains.org/intellij/sdk/docs/basics/plugin_structure/plugin_extension_points.html?search=extension)
- [Dynamic plugins](https://jetbrains.org/intellij/sdk/docs/basics/plugin_structure/dynamic_plugins.html)
- [Migrate components to services](https://jetbrains.org/intellij/sdk/docs/basics/plugin_structure/plugin_components.html)
- [Dynamic plugins and choosing a parent disposable](https://jetbrains.org/intellij/sdk/docs/basics/disposers.html#choosing-a-disposable-parent)
- [Initialize plugin on startup](https://www.plugin-dev.com/intellij/general/plugin-initial-load/)

In this plugin, here are
[the changes](https://github.com/nazmulidris/idea-plugin-example/commit/73756ffbef3159928f90f9289b54613bebac2ce3)
that are related to making it dynamic.

1. The component (`ConfiguratorComponent.kt`) that runs the Runnables when the plugin loads after
   the IDE starts, was replaced w/ a `postStartupActivity` called `ConfiguratorStartupActivity.kt`
   that actually does what the old component did. The extensions for our custom extension point are
   instantiated and run here. This is essentially all that the old component actually did. The entry
   for the component in `plugin.xml` was removed and the `postStartupActivity` entry was added.
2. The custom extension point is actually marked as
   [dynamic](https://jetbrains.org/intellij/sdk/docs/basics/plugin_structure/plugin_extension_points.html?search=extension#dynamic-extension-points).
3. The service (`LogService.kt`) is marked w/ an annotation `@Service` making it a
   [light service](https://jetbrains.org/intellij/sdk/docs/basics/plugin_structure/plugin_services.html#light-services).
   This does not require any `plugin.xml` entry, which was removed.

### Components (deprecated)

Components are classes that are loaded by IDEA when it starts. You have to careful about creating
too many components in your plugin, since they are created at IDEA startup and if they take a long
time to execute, they will delay the launch of the IDE.

Also, the code in components is executed on the main thread. JetBrains recommends that services
should be used instead of components wherever possible, since these are loaded lazily, and are
better for IDE performance.

There are 3 kinds of components, a) application components, b) project components, and c) module
components. Here are
[the official docs](https://www.jetbrains.org/intellij/sdk/docs/basics/plugin_structure/plugin_components.html).
This a [link to older docs](https://confluence.jetbrains.com/pages/viewpage.action?pageId=61215573)
from JetBrains which are a really good reference as well.

**Application Components** - These are created and initialized when the IDE starts up.

1. You can either declare a constructor in your class which accepts an `Application` object, eg:
   `class ConfiguratorComponent(val application : Application ) {}`. PicoContainer injects the
   application object into your constructor.
2. Or call the static method `ApplicationManager.getInstance().getComponent(YourComponent.class )`.
   Where `YourComponent.class` is your component class.
3. You also have to register the component class (eg: `YourComponent.class`) with `plugin.xml`.

   ```xml
   <!-- Add application component. -->
   <application-components>
   <component>
     <implementation-class>YourComponent</implementation-class>
   </component>
   </application-components>
   ```

4. Here's an example on github for this tutorial
   [idea-plugin-example ](https://github.com/nazmulidris/idea-plugin-example).

**Project Components** - These are created for each project instance in the IDE.

1.  You have to implement the `ProjectComponent` interface.
2.  You can use constructor injection, that accepts a `Project` object.
3.  You have to register the component class with `plugin.xml`.

    ```xml
    <project-components>
      <component>
        <implementation-class>YourProjectComponent</implementation-class>
      </component>
    </project-components>
    ```

4.  You can get a list of all the open projects by using
    `ProjectManager.getInstance().getOpenProjects()`.
5.  Here's an example project on github called
    [max_opened_projects](https://github.com/JetBrains/intellij-sdk-docs/tree/master/code_samples/max_opened_projects).

**Module Components** - These are created for each module inside of every project in the IDE.

1. You have to implement the `ModuleComponent` interface.
2. The constructor of a module-level component can have a parameter of the `Module` type, if it
   needs the module instance (this will be injected by PicoContainer). It can also specify other
   application-level, project-level or module-level components as parameters, if it needs them
   (these will also be injected).
3. You have to register the component class with `plugin.xml`.

   ```xml
   <!-- Plugin's module components -->
   <module-components>
     <component>
       <interface-class>YourModuleComponent</interface-class>
     </component>
   </module-components>
   ```

### Extensions and extension points

An IDEA extension is a way for a plugin to extend what IDEA can do. For eg, IDEA doesn't know how to
work w/ Bash files. You can install a plugin that gives IDEA syntax highlighting for Bash. This
plugin provides this capability of turning a Bash filed loaded in the editor, into PSI via an
extension that this plugin provides, which binds to an extension point that is provided by IDEA.

IDEA itself is a set of plugins, and many parts of IDEA define extension points, that can be
implemented by extensions that are provided by various plugins. In fact, there are some scenarios
where multiple extensions are provided as an implementation of a single extension point. The IDE
itself doesn't know what extensions are available or even extension points, until it loads itself
and all the bundled plugins and 3rd party plugins that are installed.

There are many important extension points that are exposed by IDEA itself that are listed here:

- [LangExtensionPoints.xml](https://tinyurl.com/yxa99b2s)
- [PlatformExtensionPoints.xml](https://tinyurl.com/y5dlgw59)
- [VcsExtensionPoints.xml](https://tinyurl.com/y4bd8ezy)

Here are the [official docs](https://tinyurl.com/y6a4xafo) on extension and extension points.

IDEA services are themselves implemented via this extension mechanism (more on that in the section
below). There is a very consistent convention / idiom exposed by extension points and extensions.

1.  The extension point defines an interface that an extension must implement. The _name_ attribute
    of the extension point becomes the XML _element/tag name_ of the extension itself.
1.  Any attributes that are passed in to the extension are declared by the extension point as things
    it requires to be instantiated. For any extension point that you create, there are 2 attributes
    to consider: `interface` attribute is declared in the extension point, and the `implementation`
    attribute, which is used by each of the extensions that may be declared. Examples of these
    attributes for services (eg: `applicationService`, `projectService`, or `moduleService`
    extension points) are `serviceInterface`, and `serviceImplementation`.

Here's an example of this convention for a plugin providing its own extension point.

```xml
<extensionPoints>
  <extensionPoint name="MyExtensionPoint2" interface="MyPlugin.MyInterface"/>
</extensionPoints>

<extensions defaultExtensionNs="MyPluginID">
  <MyExtensionPoint2 implementation="MyTestPackage.MyClassImpl">
  </MyExtensionPoint2>
</extensions>
```

Here's an example of this convention for a plugin providing an extension to IDEA extension points:
`appStarter` and `applicationConfigurable`.

```xml
<extensions defaultExtensionNs="com.intellij">
  <appStarter implementation="MyTestPackage.MyTestExtension1" />
  <applicationConfigurable implementation="MyTestPackage.MyTestExtension2" />
</extensions>
```

There are 2 namespaces that you should be aware of. Here is an example of this in use:

```xml
<extensions defaultExtensionNs="com.intellij">...</extensions>
<extensions defaultExtensionNs="MyPluginID">...</extensions>
```

1.  `com.intellij` means that you want to extend IDEA extension points itself.
1.  `MyPluginID` (which is really any string that you use for your plugin id) means that this
    extension implements the extension point that your plugin itself is exposing (and not IDEA
    directly).

So, how are these extensions and extensions points loaded by IDEA? It seems magic that you just
declare them in `plugin.xml` and then they are automagically instantiated and hooked up in the right
way to do all the right things.

The answer is
[`PluginManagerCore.java`](https://github.com/JetBrains/intellij-community/blob/master/platform/core-impl/src/com/intellij/ide/plugins/PluginManagerCore.java).
It searches the plugins directory for plugins, parses their `plugin.xml` files, and then uses
reflection to instantiate the extensions listed there. And PicoContainer takes care of injecting the
platform dependencies.

Here's an example of this in the extension point implementation that is provided in the git repo of
this tutorial
([`extensionPoints/ConfiguratorComponent.kt`](https://github.com/nazmulidris/idea-plugin-example/blob/main/src/main/kotlin/extensionPoints/ConfiguratorComponent.kt)).

```kotlin
package extensionPoints

/**
 * Create an ExtensionPointName given the namespace of the plugin and the
 * name of the extension point itself. Note that the namespace is "com
 * .intellij" if IntelliJ Platform core functionality is extended, otherwise,
 * it is the namespace of the plugin itself.
 */
object EP_NAME {
  private const val nameSpace =
      "com.developerlife.example.idea-plugin-example"
  private const val name = "configuratorRunnable"
  private const val fullyQualifiedName = "$nameSpace.$name"
  operator fun invoke(): ExtensionPointName<Runnable> =
      ExtensionPointName.create<Runnable>(fullyQualifiedName)
}

/**
 * An ApplicationComponent that loads all the extensions that are registered to
 * the extension point. Note that this class does not have to implement any
 * IntelliJ platform interfaces.
 */
class ConfiguratorComponent(val application: Application) {
  init {
    EP_NAME().extensionList.forEach { it.run() }
  }
}
```

Here are some examples of real plugins that use extensions and extension points. You can use these
links to browse the source code for these plugins.

- [OpenInTerminal](https://tinyurl.com/y54c35kk)
- [DateTimeConverter](https://tinyurl.com/y6lj6c5w)
- [max_opened_projects sample](https://tinyurl.com/y3qg48ok)
- [Customizing IDEA settings dialog](https://tinyurl.com/y295zx6t)
- [How to create a Tool Window](https://tinyurl.com/y5c4p4c7)

### Services

JetBrains recommends using services instead of components, since they are created on demand, and
don't slow down startup, or allocate resources even though they aren't being used.

Services are classes that can be instantiated by IDEA when needed, and these objects/instances
reused, so they are stateful. It's a way to provide any arbitrary class and interface to anything
required by a plugin, such as components, actions, etc.

Services utilize IDEA extensions. And they are unlike components (which are pre-loaded when the IDE
starts up).

In order to create services, here are the IDEA extension points that can be used (to create
services, which are the extensions):

- `applicationService` - this is equivalent to application component
- `projectService` - this is equivalent to project component
- `moduleService` - this is equivalent to module component

Here's an example:

```xml
<extensions defaultExtensionNs="com.intellij">
    <applicationService
        serviceImplementation="settings.OpenInTerminalSettings"/>
    <applicationConfigurable
        id="OpenInTerminal.settings"
        instance="settings.OpenInTerminalSettingsConfigurable"/>
</extensions>
```

It's a very common pattern to provide a static factory method called `getInstance()` to get an
object for the given service class. Here's an example that gets an instance of `YourService` class:

```kotlin
/**
 * This is used by IDEA to get a reference to the single instance of this
 * service (used by [ServiceManager]).
 */
val instance: LogService
  get() = ServiceManager.getService(YourService::class.java)
```

Here is more information on this:

- [Docs (jetbrains.org)](https://tinyurl.com/y4n4l4wd)
- [Example (OpenInTerminal plugin)](https://tinyurl.com/y54c35kk)
- [Example (max_open_projects sample plugin)](https://tinyurl.com/y3qg48ok)

## Persisting state between IDE restarts

IDEA allows components and services to persist their state across IDE restarts. You can specify the
storage location, or use the defaults. And you can specify the data that gets stored as well (public
fields of the "state" class that you pick). Annotations are used to specify all these things
(combination of `@State` and `@Storage`, look at the [details link](https://tinyurl.com/y5ofu6g5)
for more info).

There are 2 ways (each saves/loads from a different location):

- Preferred:
  - Simple: `PropertiesComponent` (saves to `workspace.xml`)
  - Complex: `@State`, `@Storage`, `PersistentStateComponent` interface
- Deprecated: `JDOMExternalizable` interface

Settings are persisted across IDEA restarts:

- Application components are in global IDEA configuration.
- Project components are saved in project specific configuration.
- Module components are saved in project specific configuration.

More info on persisting state (and lifecycle):

- [Overview](https://tinyurl.com/y5qh3obf).
- [Details](https://tinyurl.com/y5ofu6g5).

### PersistentStateComponent and Services

It is a very common pattern to combine services and `PersistentStateComponent`. Zooming out from the
implementation details, this is how you can use these types of services:

- You can call `getInstance()` on the companion object, or singleton instance of a service class.
  And IDEA will already restore its state from persistence (XML file in
  `$IDEA_CONFIG_FOLDER/config/system/` folder).
- You can use the instance and mutate its state.
- IDEA will automatically save the mutated state to persistence (XML) files for you in the
  background.

Here's an
[example](https://github.com/nazmulidris/idea-plugin-example/blob/main/src/main/kotlin/services/LogService.kt).

```kotlin
@State(name = "LogServiceData", storages = [Storage("logServiceData.xml")])
object LogService : PersistentStateComponent<LogService.State> {
  /**
   * This is used by IDEA to get a reference to the single instance of this
   * service (used by [ServiceManager]).
   */
  val instance: LogService
    get() = ServiceManager.getService(LogService::class.java)

  fun addMessage(message: String) {
    with(state.messageList) {
      add(message)
      add("LogService: ${whichThread()}")
    }
  }

  override fun toString(): String {
    return with(state.messageList) {
      "messageList.size=$size" + "\n${joinToString(separator = "\n")}"
    }
  }

  private var state = State()

  data class State(
      var messageList: MutableList<String> =
          CopyOnWriteArrayList()
  )

  /**
   * Called by IDEA to get the current state of this service, so that it can
   * be saved to persistence.
   */
  override fun getState(): State {
    "IDEA called getState()".logWithoutHistory()
    return state
  }

  /**
   * Called by IDEA when new component state is loaded. This state object should
   * be used directly, defensive copying is not required.
   */
  override fun loadState(stateLoadedFromPersistence: State) {
    "IDEA called loadState(stateLoadedFromPersistence)".logWithoutHistory()
    stateLoadedFromPersistence.messageList
        .joinToString(separator = ",", prefix = "{", postfix = "}")
        .logWithoutHistory()
    state = stateLoadedFromPersistence
  }

}
```

Notes on `PersistentStateComponent` implementation.

- The `loadState()` method is called by IDEA after the component has been created (only if there is
  some non-default state persisted for the component), and after the XML file with the persisted
  state is changed externally (for example, if the project file was updated from the version control
  system). In the latter case, the component is responsible for updating the UI and other related
  components according to the changed state.

- The `getState()` method is called by IDEA every time the settings are saved (for example, on frame
  deactivation or when closing the IDE). If the state returned from `getState()` is equal to the
  default state (obtained by creating the state class with a default constructor), nothing is
  persisted in the XML. Otherwise, the returned state is serialized in XML and stored.

In this example, you can use the following instructions to locate the XML files and log files that
are generated.

To find the IDEA log look at the `$PROJECT_DIR/build/idea-sandbox/system/log/idea.log` file. A
simple command to do this (from the project directory) is:

```bash
find . -name "idea.log" | xargs tail -f | grep MyPlugin
```

To find the `"logServiceData.xml"` take a look at the
`$PROJECT_DIR/build/idea-sandbox/config/options/logServiceData.xml` file. A simple command to do
this (from the project directory) is:

```bash
find . -name "logServiceData.xml" | xargs subl -n
```

## Actions

Actions are one of the simplest ways in which to extend IDE functionality. The official docs do a
great job of going over the action system
[here](http://www.jetbrains.org/intellij/sdk/docs/basics/action_system.html). I recommend reading
that page before continuing with this tutorial (as I'm not going to repeat that material here).

You can declare actions in XML and you can also register them in code. Some of the built in actions
in IDEA itself are registered in code (eg: `Coverage` action, which is the "Run with Coverage" icon
that shows up in the main toolbar, and main menu). In fact, all the executors are actually
registered in code (and not declaratively in XML).

Here are some examples of actions declared in XML and implemented in Kotlin from the sample plugin
created for this tutorial.

- [`plugin.xml`](https://github.com/nazmulidris/idea-plugin-example/blob/main/src/main/resources/META-INF/plugin.xml).
- [`Actions implemented in Kotlin`](https://github.com/nazmulidris/idea-plugin-example/tree/main/src/main/kotlin/actions).

## IntelliJ platform version, Gradle version, Kotlin version, gradle-intellij-plugin, intellij-plugin-verifier

When creating your plugin, you have to make a decision about which IntelliJ products your plugin
will support (the products inside of which your plugin will run once they're installed). Keep in
mind that these products are rapidly evolving and platform updates (for the IntelliJ platform that
all the IDE products are based on) are released quite often, about 3 releases a year. Oftentimes
breaking changes are released and this requires big architectural or structural changes in your
plugin codebase.

### intellij-plugin-verifier

JetBrains have a plugin verifier
[intellij-plugin-verifier](https://github.com/JetBrains/intellij-plugin-verifier) that makes it easy
for you to know if your plugin is compatible w/ your chosen IntelliJ platform version or build
codes. Instead of running this manually against your plugin, the
[gradle-intellij-plugin](https://github.com/JetBrains/gradle-intellij-plugin#plugin-verifier-dsl)
makes it easy to run this as a gradle task. Note that you are using this gradle plugin to build your
plugin. Here's a snippet in your `build.gradle.kts` that you can add to configure this verification
task.

```kotlin
// See https://github.com/JetBrains/gradle-intellij-plugin#plugin-verifier-dsl
// See https://data.services.jetbrains.com/products?fields=code,name,releases.version,releases.build,releases.type&code=IIC,IIU
tasks {
  runPluginVerifier {
    ideVersions(listOf<String>("2020.1.4", "2020.2.3", "2020.3"))
  }
}
```

You can run this task from IDEA, or from the command line using `./gradlew runPluginVerifier` to
ensure that this the intellij-plugin-verifier runs. It points out any deprecations or any other
mistakes that need to be corrected before publishing this plugin. Also, make sure to choose which
IDEA versions you would like the plugin to be verified against in the `ideVersions` function. More
on this [below](#notes-on-the-build-or-version-codes).

You can learn more about this DSL
[here](https://github.com/JetBrains/gradle-intellij-plugin#plugin-verifier-dsl). There's a detailed
report that is generated in `${project.buildDir}/reports/pluginVerifier` for each `ideVersion` that
this plugin is tested against. Here's an example of the output this task produces on the command
line.

```text
Starting the IntelliJ Plugin Verifier 1.253
2020-11-21T13:25:17 [main] INFO  c.j.p.options.OptionsParser - Delete the verification directory /home/nazmul/github/idea-plugin-example/build/reports/pluginVerifier because it isn't empty
Verification reports directory: /home/nazmul/github/idea-plugin-example/build/reports/pluginVerifier
2020-11-21T13:25:17 [main] INFO  verification - Reading IDE /home/nazmul/.pluginVerifier/ides/IC-2020.1.4
2020-11-21T13:25:19 [main] INFO  verification - Reading IDE /home/nazmul/.pluginVerifier/ides/IC-2020.2.3
2020-11-21T13:25:21 [main] INFO  verification - Reading IDE /home/nazmul/.pluginVerifier/ides/IC-2020.3
2020-11-21T13:25:22 [main] INFO  verification - Reading plugin to check from /home/nazmul/github/idea-plugin-example/build/distributions/idea-plugin-example-1.0.zip
2020-11-21T13:25:33 [main] INFO  verification - Task check-plugin parameters:
Scheduled verifications (3):
com.developerlife.example.idea-plugin-example:1.0 against IC-201.8743.12, com.developerlife.example.idea-plugin-example:1.0 against IC-202.7660.26, com.developerlife.example.idea-plugin-example:1.0 against IC-203.5981.41

2020-11-21T13:25:34 [main] INFO  verification - Finished 1 of 3 verifications (in 0.6 s): IC-201.8743.12 against com.developerlife.example.idea-plugin-example:1.0: Compatible
2020-11-21T13:25:34 [main] INFO  verification - Finished 2 of 3 verifications (in 0.6 s): IC-202.7660.26 against com.developerlife.example.idea-plugin-example:1.0: Compatible. 3 usages of internal API
2020-11-21T13:25:34 [main] INFO  verification - Finished 3 of 3 verifications (in 0.6 s): IC-203.5981.41 against com.developerlife.example.idea-plugin-example:1.0: Compatible. 3 usages of deprecated API. 3 usages of internal API
Plugin com.developerlife.example.idea-plugin-example:1.0 against IC-201.8743.12: Compatible
    Plugin can be loaded/unloaded without IDE restart

Plugin com.developerlife.example.idea-plugin-example:1.0 against IC-202.7660.26: Compatible. 3 usages of internal API
Internal API usages (3):
    #Internal method com.intellij.ide.plugins.PluginManager.getLogger() invocation
        Internal method com.intellij.ide.plugins.PluginManager.getLogger() : com.intellij.openapi.diagnostic.Logger is invoked in UtilsKt.logWithHistory(String) : void. This method is marked with @org.jetbrains.annotations.ApiStatus.Internal annotation and indicates that the method is not supposed to be used in client code.
        Internal method com.intellij.ide.plugins.PluginManager.getLogger() : com.intellij.openapi.diagnostic.Logger is invoked in UtilsKt.log(String) : void. This method is marked with @org.jetbrains.annotations.ApiStatus.Internal annotation and indicates that the method is not supposed to be used in client code.
        Internal method com.intellij.ide.plugins.PluginManager.getLogger() : com.intellij.openapi.diagnostic.Logger is invoked in UtilsKt.logWithoutHistory(String) : void. This method is marked with @org.jetbrains.annotations.ApiStatus.Internal annotation and indicates that the method is not supposed to be used in client code.
    Plugin can be loaded/unloaded without IDE restart

Plugin com.developerlife.example.idea-plugin-example:1.0 against IC-203.5981.41: Compatible. 3 usages of deprecated API. 3 usages of internal API
Deprecated API usages (3):
    #Deprecated method com.intellij.openapi.util.IconLoader.getIcon(String) invocation
        Deprecated method com.intellij.openapi.util.IconLoader.getIcon(java.lang.String path) : javax.swing.Icon is invoked in actions.PluginIcons.DefaultImpls.getHELLO_ACTION(PluginIcons) : Icon
        Deprecated method com.intellij.openapi.util.IconLoader.getIcon(java.lang.String path) : javax.swing.Icon is invoked in actions.PluginIcons.DefaultImpls.getSTACKOVERFLOW_ACTION(PluginIcons) : Icon
    #Deprecated constructor com.intellij.notification.NotificationGroup.<init>(String, NotificationDisplayType, boolean, String, Icon, int, DefaultConstructorMarker) invocation
        Deprecated constructor com.intellij.notification.NotificationGroup.<init>(java.lang.String arg0, com.intellij.notification.NotificationDisplayType arg1, boolean arg2, java.lang.String arg3, javax.swing.Icon arg4, int arg5, kotlin.jvm.internal.DefaultConstructorMarker arg6) is invoked in ui.ShowNotificationSampleAction.anotherNotification(AnActionEvent) : void
Internal API usages (3):
    #Internal method com.intellij.ide.plugins.PluginManager.getLogger() invocation
        Internal method com.intellij.ide.plugins.PluginManager.getLogger() : com.intellij.openapi.diagnostic.Logger is invoked in UtilsKt.logWithHistory(String) : void. This method is marked with @org.jetbrains.annotations.ApiStatus.Internal annotation and indicates that the method is not supposed to be used in client code.
        Internal method com.intellij.ide.plugins.PluginManager.getLogger() : com.intellij.openapi.diagnostic.Logger is invoked in UtilsKt.log(String) : void. This method is marked with @org.jetbrains.annotations.ApiStatus.Internal annotation and indicates that the method is not supposed to be used in client code.
        Internal method com.intellij.ide.plugins.PluginManager.getLogger() : com.intellij.openapi.diagnostic.Logger is invoked in UtilsKt.logWithoutHistory(String) : void. This method is marked with @org.jetbrains.annotations.ApiStatus.Internal annotation and indicates that the method is not supposed to be used in client code.
    Plugin can be loaded/unloaded without IDE restart

2020-11-21T13:25:34 [main] INFO  verification - Total time spent downloading plugins and their dependencies: 0 ms
2020-11-21T13:25:34 [main] INFO  verification - Total amount of plugins and dependencies downloaded: 0 B
2020-11-21T13:25:34 [main] INFO  verification - Total amount of space used for plugins and dependencies: 0 B
```

#### Notes on the build or version codes

The gradle task shown above requires a `ideVersions` array to be passed in. This array contains the
build or version codes for IDEA releases or EAPs that we want our plugin to be tested against. Where
do we find these codes that are required? The following link has a list of build and version codes
for `IIC - IntelliJ IDEA Community Edition`, and `IIU - IntelliJ IDEA Ultimate Edition`. You can
modify the URL to get other product codes that you need to include. To view this link in Chrome,
please use an extension like [JSON Formatter](https://github.com/callumlocke/json-formatter) since
there the JSON blob returned by this URL is quite big.

- [IIC, IIU release version, build, download](https://data.services.jetbrains.com/products?fields=code,name,releases.downloads,releases.version,releases.build,releases.type&code=IIC,IIU)

Once you have decided which versions of IDEA that you want this plugin to be verified against, make
sure that you have declared this plugin to be compatible w/ these IDE build ranges in the following
two places:

1. `build.gradle` - `intellij { version { "<version-or-build-code>" } }`
2. `plugin.xml` -
   `<idea-version since-build="<version-or-build-code>" until-build="<version-or-build-code" />`
   - Note that you can use wildcards here, eg: `2020.*` for the `<version-or-build-code>`

### Using the latest version of Gradle and gradle-intellij-plugin

On a somewhat related note, you might have to upgrade your existing plugin to use the latest Gradle
and gradle-intellij-plugin. You might also have to upgrade the version of Kotlin you support. Most
of these changes can be made in the `build.gradle.kts` file. However, upgrading Gradle itself has to
be done from the command line.

Here's more information on staying up to date w/ the latest version of
[gradle-intellij-plugin](https://github.com/JetBrains/gradle-intellij-plugin). This requires changes
to be made to the `plugin` section of `build.gradle` w/
`id "org.jetbrains.intellij" version "<latest-version-here>"`

Here's more information on staying up to date w/ the latest version of the
[Gradle wrapper](https://docs.gradle.org/current/userguide/userguide.html) that is required. You can
run the following command upgrade the Gradle wrapper
`./gradlew wrapper --gradle-version <latest-version-here>`, where `<latest-version-here>` is the
latest version of Gradle, eg: `6.7`.

To update to the latest version of Kotlin, in `build.gradle.kts`, you have to update
`plugins { kotlin("jvm") version "<new-version>" }` where `<new-version>` is the latest version of
Kotlin, eg: `1.4.10`.

### In build.gradle.kts which intellij version should we use?

Using `version 'LATEST-EAP-SNAPSHOT` can be very unstable, and cause gradle tasks to fail in strange
ways, and cause other issues w/ the gradle plugins (IntelliJ, Kotlin, etc). Instead it is best to
pick a specific stable version from [here](https://www.jetbrains.com/intellij-repository/releases/).

You can get a list of EAP snapshots from
[here](https://www.jetbrains.com/intellij-repository/snapshots/) but these are also most likely
unstable. For our plugin, it is a little bit more complex, since it has a dependency on "java" and
"markdown" plugins. The workflow to update to the latest version of IDEA and Markdown plugin goes
something like this:

1. Find the latest Markdown plugin release from
   [here](https://plugins.jetbrains.com/plugin/7793-markdown/versions), and insert it below
   (replacing whatever version is there now). The webpage will also tell you which version of IDEA
   this is compatible w/.
2. Find the IDEA snapshot that is compatible w/ the Markdown plugin above (which probably won't be
   the latest EAP snapshot). Replace the `intellij.version` in `build.gradle.kts` w/ this supported
   snapshot.

You can read more about this on the
[JB official docs plugin dependencies](https://www.jetbrains.org/intellij/sdk/docs/basics/plugin_structure/plugin_dependencies.html).

## Declaring dependencies on other plugins

It is common for some plugins to have dependencies on portions of the IntelliJ Platform that are
themselves built and distributed as plugins, some of which can be bundled w/ the IDE itself. In the
example used in for this tutorial there are dependencies declared on a few of these plugins: `java`,
`markdown`, and `platform`.

Since the example does PSI manipulation, the `markdown` and `java` plugins are needed. And the
`platform` modules is needed for the following: Messaging, UI Themes, UI Components, Files,
Documents, Actions, Components, Services, Extensions, Editors. You can read more about this in the
[IntelliJ Platform SDK DevGuide](https://www.jetbrains.org/intellij/sdk/docs/basics/getting_started/plugin_compatibility.html).

The confusing thing about these dependencies is that they have to be declared in 2 places. Let's
take a look at the `markdown` plugin dependency. Here are the places where you have to declare this.

1. In `build.gradle.kts` - You have to specify the dependency in
   `intellij { setPlugin("markdown", ...) }`.
2. In `plugin.xml` - You have to specify the dependency in
   `<depends>org.intellij.plugins.markdown</depends>`.

Similarly for the `java` dependency, you have to declare this in 2 places.

1. In `build.gradle.kts` - You have to specify the dependency in
   `intellij { setPlugin("java", ...) }`.
2. In `plugin.xml` - You have to specify the dependency in
   `<depends>com.intellij.modules.java</depends>`.

And finally, for the `platform` you only have to specify this in `plugin.xml`. Hoever, you don't
have to specify this in `build.gradle.kts`, since the code for these plugins are already included in
the version of the platform that you choose in
`intellij { version = "<idea-build-code-or-version-here> }`.

1. In `plugin.xml` - You have to specify the dependency in
   `<depends>com.intellij.modules.platform</depends>`.

## Misc

### Analyze startup performance

IDEA has an action called "Analyze Plugin Startup Performance". It is hidden away in the main menu
"Help -> Diagnostic Tools -> Analyze Plugin Startup Performance". This gem of an action will show
you how much time your plugin is taking, and all the other plugins that you have loaded are taking,
at startup. For those other plugins, it provides a useful feature to disable them from this dialog.

IDEA has yet another hidden gem to analyze the startup performance of an IDE instance. Visit
[ij-perf.jetbrains.com/#/report](https://ij-perf.jetbrains.com/#/report) and it will give you the
ability to connect to an IDE instance running on your machine, or you can upload the logs to get the
startup performance report.

### How to use project specific JDKs

If for some reason you use an embedded JDK in the plugin project that you are working on, then it
can become cumbersome to have to manually change the JDK table settings in IDEA on every single
machine that you have cloned this project on.

There is a plugin called
[EmbeddedProjectJdk plugin](https://plugins.jetbrains.com/plugin/10480-embeddedprojectjdk) that
enables per project JDK settings (that are not loaded from your IDEA user settings).
[This doc contains information of where IDEA stores its configuration files](https://www.jetbrains.com/help/idea/tuning-the-ide.html#default-dirs).

This plugin allows you to put the `jdk.table.xml` file (stored in
`$IDEA_SETTINGS/config/options/jdk.table.xml` in
[IDEA settings directory](https://intellij-support.jetbrains.com/hc/en-us/articles/206544519-Directories-used-by-the-IDE-to-store-settings-caches-plugins-and-logs)),
into the project folder and commit to your VCS. If the JDK defined in the per project
`$PROJECT_DIR/.idea/jdk.table.xml` is not found or invalid, then the plugin will it automatically.
You can also define OS-dependent `$PROJECT_DIR/.idea/jdk.table.*.xml` files like so:

- Windows: `jdk.table.win.xml`
- Linux: `jdk.table.lin.xml`
- MacOS: `jdk.table.mac.xml`

### Using ResourceBundles for localization

In order to use localized strings for use in your plugin, you can use an imperative or declarative
approach.

#### Imperative approach

For the imperative approach, create a `MyStringsBundle.properties` file in your
`$PROJECT_DIR/resources/` folder. You can name this whatever you want. This file can contain
something like this.

```properties
dialog.title=My awesome dialog
```

You can then use this code snippet to get the values of the properties that you have defined in that
file.

```kotlin
fun getStringFromBundle(key: String): String {
  val strings: ResourceBundle = ResourceBundle.getBundle("MyStringsBundle", Locale.getDefault())
  return strings.getString(key)
}
```

#### Declarative approach

`plugin.xml`
[supports getting values out of this properties file declaratively](https://jetbrains.org/intellij/sdk/docs/basics/plugin_structure/plugin_configuration_file.html)
as long as the following is done.

1. Add a `<resource-bundle>` element in the `plugin.xml` for the `MyStringsBundle` resource. For
   example, add `<resource-bundle>MyStringsBundle</resource-bundle>` in the `<idea-plugin>` element.
2. In `MyStringsBundle.properties` file, if you want to provide a `text` value for an action, use
   the following naming pattern: `action.<YOUR_ACTION_ID>.text`. For `description` value, use the
   following pattern: `action.<YOUR_ACTION_ID>.description`.

## Testing

IDEA provides capabilities to do functional or integration testing of high level functionality. You
can still use JUnit4 and AssertJ for example to create unit tests for your plugins. Please read
[the official docs on testing](http://www.jetbrains.org/intellij/sdk/docs/basics/testing_plugins.html)
before reading further in the tutorial.

### AssertJ

In order to enable AssertJ in your project you can add the following to your `build.gradle.kts`
file.

```kotlin
// Testing
dependencies {
  testImplementation("org.assertj:assertj-core:3.11.1")
}
```

And when you create tests in IDEA, it will ask you if you want to use JUnit3, 4, or 5.

### Example tests

You can see the tests that are created for the sample plugin created for this tutorial
[here](https://github.com/nazmulidris/idea-plugin-example/tree/main/src/test/kotlin).

#### Fixtures

When using fixtures that provide an empty project that you can run your plugin code on, you must
make sure to call `super.setUp()` in the `setUp()` method. If you don't then the test won't really
work. Here's an example.

```kotlin
class LogServiceTest : BasePlatformTestCase() {

  @Before
  public override fun setUp() {
    super.setUp()
  }

  // snip
}
```

#### Test data

It is very common to load some files into the testing fixtures and then have your plugin code do
some work on those files. Then compare the results, to see if things worked or failed.

In order to load these test data files, you have to tell the test fixtures which folder to look for
your test data. This is more complex than you think.

Here's an example (from the sample plugin created for this tutorial) that demonstrates this.

```kotlin
@file:JvmName("TestUtils")

class TestUtils {

  companion object {
    val testDataFolder = "testdata"
    /**
     * @throws [IllegalStateException] if the [testDataFolder] folder
     * can't be found somewhere on the classpath.
     */
    fun computeBasePath(): String {
      val urlFromClassloader =
          TestUtils::class.java.classLoader.getResource("TestUtils.class")
      checkNotNull(urlFromClassloader) { "Could not find $testDataFolder" }

      var path: File? = File(urlFromClassloader.toURI())
      while (path != null &&
             path.exists() &&
             !File(path, testDataFolder).isDirectory
      ) {
        path = path.parentFile
      }
      checkNotNull(path) { "Could not find $testDataFolder" }
      return File(path, testDataFolder).absolutePath
    }

  }
}
```

Files needed to be loaded from the plugin project's `testdata` directory. By default, IntelliJ
Platform `BasePlatformTestCase` provides a location that is _invalid_ for use by 3rd party plugins
(provided by `BasePlatformTestCase.myFixture#basePath`) 😳. This assumes that the files are in the
classpath of the IntelliJ IDEA codebase itself.

In contrast, the
[`TestUtils.kt`](https://github.com/nazmulidris/idea-plugin-example/blob/main/src/test/kotlin/TestUtils.kt)
that provides the `computeBasePath` function uses the classpath of its own self (class) in order to
locate where on disk, this class is loaded from. And then walks up the path (tree) to locate the
`testdata` folder (which is a leaf off of one of these parent nodes). Also, note that this class
uses an annotation (`@file:JvmName()`) in order to explicitly set its own classname and not use the
computed `TestUtilsKt.class` (which would be the default w/out using this annotation).

#### Mocking actions

By default, when you invoke an action from via the fixture, it will execute the action, and if this
means that it does something to change something in your OS, then it will do that.

For example in the
[`SearchOnStackOverflowActionTest`](https://github.com/nazmulidris/idea-plugin-example/blob/main/src/test/kotlin/actions/SearchOnStackOverflowActionTest.kt),
I open a browser tab w/ the text that's selected in the test data file `testFle.md`. And when the
test would run, it would open a tab in my Chrome browser.

In order to prevent this, I ended up mocking the action performed method of the action itself, by
passing a lambda for testing purposes. If no lambda is passed, then the action does what it is
supposed to do. However, if I pass a lambda (for testing) then I can verify some state information
from that lambda to ensure that my action is doing what its supposed to.

Here's the action code
[`StackOverflowActions.kt`](https://github.com/nazmulidris/idea-plugin-example/blob/main/src/main/kotlin/actions/StackOverflowActions.kt).

```kotlin
/**
 * [handler] allows this class to be mocked. If nothing is passed, then this
 * action does what it is supposed to. Otherwise, this handler gets passed
 * two things:
 * 1. selectedText: String
 * 2. langTag: String
 */
class SearchOnStackOverflowAction(
    val handler: ((String, String) -> Unit)? = null
) : AnAction() {
  override fun update(event: AnActionEvent) {
    with(event.getRequiredData(CommonDataKeys.EDITOR)) {
      val condition = caretModel.currentCaret.hasSelection()
      event.presentation.isEnabledAndVisible = condition
    }
  }

  override fun actionPerformed(event: AnActionEvent) {
    val langTag: String = with(event.getData(CommonDataKeys.PSI_FILE)) {
      this?.run {
        "+[${language.displayName.toLowerCase()}+]"
      }
    } ?: ""

    val selectedText: String =
        with(event.getRequiredData(CommonDataKeys.EDITOR)) {
          caretModel.currentCaret.selectedText
        } ?: ""

    val myHandler = handler ?: { _, _ ->
      if (selectedText.isEmpty()) {
        Messages.showMessageDialog(
            event.project,
            "Please select something before running this action",
            "Search on Stack Overflow",
            Messages.getWarningIcon())
      }
      else {
        val query = URLEncoder.encode(selectedText, "UTF-8") + langTag
        BrowserUtil.browse("https://stackoverflow.com/search?q=$query")
      }
    }

    myHandler.invoke(selectedText, langTag)

  }
```

Here's the
[test code `SearchOnStackOverflowActionTest.kt`](https://github.com/nazmulidris/idea-plugin-example/blob/main/src/test/kotlin/actions/SearchOnStackOverflowActionTest.kt).

```kotlin
class SearchOnStackOverflowActionTest : BasePlatformTestCase() {

private lateinit var testFolderLocation: String

@Before
public override fun setUp() {
  super.setUp()
  testFolderLocation = computeBasePath()
  assertThat(testFolderLocation).isNotNull()
}

@Test
fun testSelectedTextIsSearchedOnStackOverflow() {
  // Load test file w/ text selected.
  myFixture.configureByFile(
      testFolderLocation + File.separator + "testFile.md")

  // Try and perform the action.
  lateinit var selectedText: String
  lateinit var langTag: String
  val action = SearchOnStackOverflowAction { text, lang ->
    selectedText = text
    langTag = lang
  }

  val presentation = myFixture.testAction(action)
  assertThat(presentation.isEnabledAndVisible).isTrue()

  assertThat(selectedText).isEqualTo("jetbrains sdk plugin testing")
  assertThat(langTag).isEqualTo("+[plain text+]")
  }
}
```

## References

There aren't many publicly available resources outside of JetBrains official docs (which are sparse,
and tend to focus on the "how?" and never the "why?") and open source plugins (which can be used as
examples to learn from).

Here are a few that I've found. Sources (where and if you can find them) serve as a good source of
learning for how the Platform SDK APIs work, how they can be used, and even how to write tests for
them. Using the [debugger](https://www.youtube.com/watch?v=rjlhSDhFwzM) to set breakpoints and
analyzing the stack traces are also a valid approach to understanding what this platform code does
(since it is 15+ years old and has gone through many many revisions).

- [JetBrains IntelliJ Platform SDK official docs](http://www.jetbrains.org/intellij/sdk/docs/welcome.html).
- [Information about Platform SDK by the author of the BashSupport plugin](https://www.plugin-dev.com/intellij/).
- [Article on ApplicationConfigurable and ProjectConfigurable](http://corochann.com/intellij-plugin-development-introduction-applicationconfigurable-projectconfigurable-873.html).
- [All 3rd party plugins, the source can be used as examples](https://plugins.jetbrains.com/).
- [Browse Code examples for open source plugins (from their github repos)](https://www.programcreek.com/java-api-examples/?Query=intellij+plugin&action=search_project&submit=Search).
- [Comparison of plugin development on IDEA, VSCode, etc](https://medium.com/cacher-app/building-code-editor-plugins-a-comparison-83b5c21657fe)
