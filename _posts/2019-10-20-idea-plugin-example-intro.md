---
author: Nazmul Idris
date: 2019-08-25 05:19:43+00:00
layout: post
excerpt: |
  This article is a introduction to creating plugins using JetBrains PLugin SDK.
layout: post
hero-image: assets/jetbrains-plugin.svg
title: "Introduction to creating IntelliJ IDEA plugins"
categories:
- KT
- TDD
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [Plugin architecture](#plugin-architecture)
  - [PicoContainer](#picocontainer)
  - [plugin.xml](#pluginxml)
  - [Components](#components)
  - [Extensions and extension points](#extensions-and-extension-points)
  - [Services](#services)
- [Persisting state between IDE restarts](#persisting-state-between-ide-restarts)
  - [PersistentStateComponent and Services](#persistentstatecomponent-and-services)
- [Actions](#actions)
- [Testing](#testing)
  - [AssertJ](#assertj)
  - [Example tests](#example-tests)
    - [Fixtures](#fixtures)
    - [Test data](#test-data)
    - [Mocking actions](#mocking-actions)
- [References](#references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

This article covers the basics of creating a plugin for IntelliJ IDEA using the
Plugin SDK. It covers the basics, like what components and services are, what
extension points and extensions are, along with persistent state components, and
unit testing. Topics like disposables, PSI, VFS, read/write locks, are not
covered in this tutorial. I will write more tutorials in the future to cover
these advanced topics as well.

To get the code for this tutorial, please clone the
[`nazmulidris/idea-plugin-example`](https://github.com/nazmulidris/idea-plugin-example)
repo from github. Please checkout the README for this repo, and clone it to your
computer, and get it running before following along in this tutorial. It's much
easier when you have some real code and examples to play with in the IDE to
understand the concepts in this very long tutorial.

There is quite a lot of information to absorb as you embark on this journey! The
following is a link to the official JetBrains Platform SDK docs to create a
plugin from scratch. In this tutorial we will cover using the gradle based
plugin (and not the old Plugin DevKit based approach).

- [Getting started w/ Gradle based IntelliJ Platform Plugin](http://www.jetbrains.org/intellij/sdk/docs/tutorials/build_system/prerequisites.html).

## Plugin architecture

An IDEA plugin really is an extension of the IDE that you are writing. Most of
IDEA itself is constructed as a set of plugins that are layered on top of the
base platform code.

- Each plugin has a `plugin.xml` file which is a manifest that declares what is
  inside the plugin and how it hooks into IDEA itself. If you're familiar w/
  Android, this is similar to the `AndroidManifest.xml` file.
- Each plugin gets its own classloader, and IDEA itself uses PicoContainer (more
  on this below) to perform dependency injection to handle loading classes via
  reflection.
- In many situations in IDEA, classes are loaded via reflection, and there are
  even situations where classes loaded by a classloader are indexed and
  searched. Here's a github repo for a really fast classpath scanner called
  [classgraph](https://github.com/classgraph/classgraph) to give you an idea of
  how this might work.

### PicoContainer

IDEA uses [PicoContainer](http://picocontainer.com/introduction.html) for
dependency injection (DI).

- PicoContainer is a very simple DI engine that supports both constructor and
  field injection injection and uses Java reflection. Even though it supports
  field injection, IDEA uses it primarily for constructor injection.
- [Here's a github repo](https://github.com/avh4/picocontainer-example) which
  contains some examples of how to use PicoContainer.

When IDEA itself launches, it uses PicoContainer to manage loading all of its
classes, interfaces, and objects. And this is extended to any plugin that you
write (to extend IDEA itself). So you don't really manage the lifecycle of your
plugin, IDEA does. And it does it via PicoContainer components.

When your plugin is loaded into IDEA, PicoContainer is used to instantiate the
classes that your plugin provides to IDEA itself, and this is where things like
project and application components can be injected into the constructors of your
components (more on this below).

### plugin.xml

This is a really important file that really tells IDEA about what is inside of
your component and how IDEA should deal with loading it, and having it interact
w/ other 3rd party components, and IDEA itself. This is very similar to
`AndroidManifest.xml` if you're used to Android development.

In this file you have to declare the `id` of your plugin. This is a really
important piece of information as this will be used as a "namespace" for many of
the things that are listed below.

You also have to list all the components, services, and actions that your plugin
provides to IDEA in this file.

Here's an example of a `plugin.xml` file.

- It provides provides an `extensionPoint` which is actually supported by a
  `component`. This extension point is called `configuratorRunnable`.
- It provides 2 `extensions` each of which implement the `configuratorRunnable`
  extension point (which is simply `Runnable`).
- A `PersistentStateComponent` is also declared which is a `applicationService`.
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

  <!-- Add application component. -->
  <application-components>
    <component>
      <implementation-class>extensionPoints.ConfiguratorComponent
      </implementation-class>
    </component>
  </application-components>

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

### Components

Components are classes that are loaded by IDEA when it starts. You have to
careful about creating too many components in your plugin, since they are
created at IDEA startup and if they take a long time to execute, they will delay
the launch of the IDE.

Also, the code in components is executed on the main thread. JetBrains
recommends that services should be used instead of components wherever possible,
since these are loaded lazily, and are better for IDE performance.

There are 3 kinds of components, a) application components, b) project
components, and c) module components. Here are
[the official docs](https://www.jetbrains.org/intellij/sdk/docs/basics/plugin_structure/plugin_components.html).
This a
[link to older docs](https://confluence.jetbrains.com/pages/viewpage.action?pageId=61215573)
from JetBrains which are a really good reference as well.

**Application Components** - These are created and initialized when the IDE
starts up.

1. You can either declare a constructor in your class which accepts an
   `Application` object, eg:
   `class ConfiguratorComponent(val application : Application ) {}`.
   PicoContainer injects the application object into your constructor.
2. Or call the static method
   `ApplicationManager.getInstance().getComponent(YourComponent.class )`. Where
   `YourComponent.class` is your component class.
3. You also have to register the component class (eg: `YourComponent.class`)
   with `plugin.xml`.

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

**Module Components** - These are created for each module inside of every
project in the IDE.

1. You have to implement the `ModuleComponent` interface.
2. The constructor of a module-level component can have a parameter of the
   `Module` type, if it needs the module instance (this will be injected by
   PicoContainer). It can also specify other application-level, project-level or
   module-level components as parameters, if it needs them (these will also be
   injected).
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

An IDEA extension is a way for a plugin to extend what IDEA can do. For eg, IDEA
doesn't know how to work w/ Bash files. You can install a plugin that gives IDEA
syntax highlighting for Bash. This plugin provides this capability of turning a
Bash filed loaded in the editor, into PSI via an extension that this plugin
provides, which binds to an extension point that is provided by IDEA.

IDEA itself is a set of plugins, and many parts of IDEA define extension points,
that can be implemented by extensions that are provided by various plugins. In
fact, there are some scenarios where multiple extensions are provided as an
implementation of a single extension point. The IDE itself doesn't know what
extensions are available or even extension points, until it loads itself and all
the bundled plugins and 3rd party plugins that are installed.

There are many important extension points that are exposed by IDEA itself that
are listed here:

- [LangExtensionPoints.xml](https://tinyurl.com/yxa99b2s)
- [PlatformExtensionPoints.xml](https://tinyurl.com/y5dlgw59)
- [VcsExtensionPoints.xml](https://tinyurl.com/y4bd8ezy)

Here are the [official docs](https://tinyurl.com/y6a4xafo) on extension and
extension points.

IDEA services are themselves implemented via this extension mechanism (more on
that in the section below). There is a very consistent convention / idiom
exposed by extension points and extensions.

1.  The extension point defines and interface that an extension must implement.
    The _name_ attribute of the extension point becomes the XML _element/tag
    name_ of the extension itself.
1.  Any attributes that are passed in the attributes to this extension are
    declared by the extension point as things it requires to be instantiated.
    Examples of this for services are `serviceInterface`, and
    `serviceImplementation`. By default these can be `implementation` attribute,
    when an `interface` attribute is declared in the extension point.

Here's an example of this convention for a plugin providing its own extension
point.

```xml
<extensionPoints>
  <extensionPoint name="MyExtensionPoint2" interface="MyPlugin.MyInterface"/>
</extensionPoints>

<extensions defaultExtensionNs="MyPluginID">
  <MyExtensionPoint2 implementation="MyTestPackage.MyClassImpl">
  </MyExtensionPoint2>
</extensions>
```

Here's an example of this convention for a plugin providing an extension to IDEA
extension points.

```xml
<extensions defaultExtensionNs="com.intellij">
  <appStarter implementation="MyTestPackage.MyTestExtension1" />
  <applicationConfigurable implementation="MyTestPackage.MyTestExtension2" />
</extensions>
```

There are 2 namespaces that you should be aware of. Here is an example of this
in use:

```xml
<extensions defaultExtensionNs="com.intellij">...</extensions>
<extensions defaultExtensionNs="MyPluginID">...</extensions>
```

1.  `com.intellij` means that you want to extend IDEA extension points itself.
1.  `MyPluginID` (which is really any string that you use for your plugins)
    means that this extension implements the extension point that your plugin
    itself is exposing (and not IDEA directly).

So, how are these extensions and extensions points loaded by IDEA? It seems
magic that you just declare them in `plugin.xml` and then they are automagically
instantiated and hooked up in the right way to do all the right things.

The answer is
[`PluginManagerCore.java`](https://github.com/JetBrains/intellij-community/blob/master/platform/core-impl/src/com/intellij/ide/plugins/PluginManagerCore.java).
It searches the plugins directory for plugins, parses their `plugin.xml` files,
and then uses reflection to instantiate the extensions listed there. And
PicoContainer takes care of injecting the platform dependencies.

Here are some examples of real plugins that use extensions and extension points.
You can use these links to browse the source code for these plugins.

- [OpenInTerminal](https://tinyurl.com/y54c35kk)
- [DateTimeConverter](https://tinyurl.com/y6lj6c5w)
- [max_opened_projects sample](https://tinyurl.com/y3qg48ok)
- [Customizing IDEA settings dialog](https://tinyurl.com/y295zx6t)
- [How to create a Tool Window](https://tinyurl.com/y5c4p4c7)

### Services

JetBrains recommends using services instead of components, since they are
created on demand, and don't slow down startup, or allocate resources even
though they aren't being used.

Services are classes that can be instantiated by IDEA when needed, and these
objects/instances reused, so they are stateful. It's a way to provide any
arbitrary class and interface to anything required by a plugin, such as
components, actions, etc.

Services utilize IDEA extensions. And they are unlike components (which are
pre-loaded when the IDE starts up).

In order to create services, here are the IDEA extension points that can be used
(to create services, which are the extensions):

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

It's a very common pattern to provide a static factory method called
`getInstance()` to get an object for the given service class. Here's an example
that gets an instance of `YourService` class:

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

IDEA allows components and services to persist their state across IDE restarts.
You can specify the storage location, or use the defaults. And you can specify
the data that gets stored as well (public fields of the "state" class that you
pick). Annotations are used to specify all these things (combination of `@State`
and `@Storage`, look at the [details link](https://tinyurl.com/y5ofu6g5) for
more info).

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

It is a very common pattern to combine services and `PersistentStateComponent`.
Zooming out from the implementation details, this is how you can use these types
of services:

- You can call `getInstance()` on the companion object, or singleton instance of
  a service class. And IDEA will already restore its state from persistence (XML
  file in `$IDEA_CONFIG_FOLDER/config/system/` folder).
- You can use the instance and mutate its state.
- IDEA will automatically save the mutated state to persistence (XML) files for
  you in the background.

Here's an
[example](https://github.com/nazmulidris/idea-plugin-example/blob/master/src/main/kotlin/services/LogService.kt).

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

- The `loadState()` method is called by IDEA after the component has been
  created (only if there is some non-default state persisted for the component),
  and after the XML file with the persisted state is changed externally (for
  example, if the project file was updated from the version control system). In
  the latter case, the component is responsible for updating the UI and other
  related components according to the changed state.

- The `getState()` method is called by IDEA every time the settings are saved
  (for example, on frame deactivation or when closing the IDE). If the state
  returned from `getState()` is equal to the default state (obtained by creating
  the state class with a default constructor), nothing is persisted in the XML.
  Otherwise, the returned state is serialized in XML and stored.

In this example, you can use the following instructions to locate the XML files
and log files that are generated.

To find the IDEA log look at the
`$PROJECT_DIR/build/idea-sandbox/system/log/idea.log` file. A simple command to
do this (from the project directory) is:

```bash
find . -name "idea.log" | xargs tail -f | grep MyPlugin
```

To find the `"logServiceData.xml"` take a look at the
`$PROJECT_DIR/build/idea-sandbox/config/options/logServiceData.xml` file. A
simple command to do this (from the project directory) is:

```bash
find . -name "logServiceData.xml" | xargs subl -n
```

## Actions

Actions are one of the simplest ways in which to extend IDE functionality. The
official docs do a great job of going over the action system
[here](http://www.jetbrains.org/intellij/sdk/docs/basics/action_system.html). I
recommend reading that page before continuing with this tutorial (as I'm not
going to repeat that material here).

You can declare actions in XML and you can also register them in code. Some of
the built in actions in IDEA itself are registered in code (eg: `Coverage`
action, which is the "Run with Coverage" icon that shows up in the main toolbar,
and main menu). In fact, all the executors are actually registered in code (and
not declaratively in XML).

Here are some examples of actions declared in XML and implemented in Kotlin from
the sample plugin created for this tutorial.

- [`plugin.xml`](https://github.com/nazmulidris/idea-plugin-example/blob/master/src/main/resources/META-INF/plugin.xml).
- [`Actions implemented in Kotlin`](https://github.com/nazmulidris/idea-plugin-example/tree/master/src/main/kotlin/actions).

## Testing

IDEA provides capabilities to do functional or integration testing of high level
functionality. You can still use JUnit4 and AssertJ for example to create unit
tests for your plugins. Please read
[the official docs on testing](http://www.jetbrains.org/intellij/sdk/docs/basics/testing_plugins.html)
before reading further in the tutorial.

### AssertJ

In order to enable AssertJ in your project you can add the following to your
`build.gradle.kts` file.

```kotlin
// Testing
dependencies {
  testImplementation("org.assertj:assertj-core:3.11.1")
}
```

And when you create tests in IDEA, it will ask you if you want to use JUnit3, 4,
or 5.

### Example tests

You can see the tests that are created for the sample plugin created for this
tutorial
[here](https://github.com/nazmulidris/idea-plugin-example/tree/master/src/test/kotlin).

#### Fixtures

When using fixtures that provide an empty project that you can run your plugin
code on, you must make sure to call `super.setUp()` in the `setUp()` method. If
you don't then the test won't really work. Here's an example.

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

It is very common to load some files into the testing fixtures and then have
your plugin code do some work on those files. Then compare the results, to see
if things worked or failed.

In order to load these test data files, you have to tell the test fixtures which
folder to look for your test data. This is more complex than you think.

Here's an example (from the sample plugin created for this tutorial) that
demonstrates this.

```kotlin
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

Files needed to be loaded from the plugin project's `testdata` directory. By
default, IntelliJ Platform `BasePlatformTestCase` provides a location that is
invalid for use by 3rd party plugins (provided by
`BasePlatformTestCase.myFixture#basePath`). This assumes that the files are in
the classpath of the IntelliJ IDEA codebase itself. The `computeBasePath`
function uses the classpath of this class in order to locate where on disk, this
class is loaded from. And then walks up the path to locate the `testdata`
folder. Also, note that this class uses an annotation (`@file:JvmName()`) in
order to explicitly set its own classname and not use the computed
`TestUtilsKt.class` (which would be the default w/out using this annotation).

#### Mocking actions

By default, when you invoke an action from via the fixture, it will execute the
action, and if this means that it does something to change something in your OS,
then it will do that.

For example in the
[`SearchOnStackOverflowActionTest`](https://github.com/nazmulidris/idea-plugin-example/blob/master/src/test/kotlin/actions/SearchOnStackOverflowActionTest.kt),
I open a browser tab w/ the text that's selected in the test data file
`testFle.md`. And when the test would run, it would open a tab in my Chrome
browser.

In order to prevent this, I ended up mocking the action performed method of the
action itself, by passing a lambda for testing purposes. If no lambda is passed,
then the action does what it is supposed to do. However, if I pass a lambda (for
testing) then I can verify some state information from that lambda to ensure
that my action is doing what its supposed to.

Here's the action code
[`StackOverflowActions`](https://github.com/nazmulidris/idea-plugin-example/blob/master/src/main/kotlin/actions/StackOverflowActions.kt).

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
[test code](https://github.com/nazmulidris/idea-plugin-example/blob/master/src/test/kotlin/actions/SearchOnStackOverflowActionTest.kt).

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

There aren't many publicly available resources outside of JetBrains official
docs (which are sparse) and open source plugins (which can be used as examples
to learn from). Here are a few that I've found. Sources (where and if you can
find them) serve as a good source of learning for how the Platform SDK APIs
work, how they can be used, and even how to write tests for them. Using the
[debugger](https://www.youtube.com/watch?v=rjlhSDhFwzM) to set breakpoints and
analyzing the stack traces are also a valid approach to understanding what this
platform code does (since it is 15+ years old and has gone thru many many
revisions).

- [JetBrains IntelliJ Platform SDK official docs](http://www.jetbrains.org/intellij/sdk/docs/welcome.html).
- [Information about Platform SDK by the author of the BashSupport plugin](https://www.plugin-dev.com/intellij/).
- [Article on ApplicationConfigurable and ProjectConfigurable](http://corochann.com/intellij-plugin-development-introduction-applicationconfigurable-projectconfigurable-873.html).
- [All 3rd party plugins, the source can be used as examples](https://plugins.jetbrains.com/).
- [Browse Code examples for open source plugins (from their github repos)](https://www.programcreek.com/java-api-examples/?Query=intellij+plugin&action=search_project&submit=Search).
