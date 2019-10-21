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
    - [Examples](#examples)
  - [Services](#services)
    - [Examples](#examples-1)
  - [Extensions](#extensions)
    - [Examples](#examples-2)
  - [Extension points](#extension-points)
    - [Examples](#examples-3)
- [Persisting state between IDE restarts](#persisting-state-between-ide-restarts)
  - [PersistentStateComponent and Services](#persistentstatecomponent-and-services)
  - [Examples](#examples-4)
- [Actions](#actions)
  - [Examples](#examples-5)
- [Unit testing](#unit-testing)
  - [JUnit4 and AssertJ](#junit4-and-assertj)
  - [Fixtures](#fixtures)
  - [Examples](#examples-6)

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
repo from github.

Here are some references on how to get started. There is quite a lot of
information to absorb as you embark on this journey!

- [Getting started w/ Gradle based IntelliJ Platform Plugin](http://www.jetbrains.org/intellij/sdk/docs/tutorials/build_system/prerequisites.html).
- [Code examples for open source plugins (from their github repos)](https://www.programcreek.com/java-api-examples/?Query=intellij+plugin&action=search_project&submit=Search).
- [Great website for writing plugins](https://www.plugin-dev.com/intellij/).

## Plugin architecture

An IDEA plugin really is an extension of the IDE that you are writing. Most of
IDEA itself is constructed as a set of plugins that are layered on top of the
base platform code. Each plugin has a `plugin.xml` file which is a manifest that
declares what is inside the plugin and how it hooks into IDEA itself. If you're
familiar w/ Android, this is similar to the `AndroidManifest.xml` file.

Each plugin gets its own classloader, and IDEA itself uses PicoContainer (more
on this below) to perform dependency injection to handle loading classes via
reflection. In many situations in IDEA, classes are loaded via reflection, and
there are even situations where classes loaded by a classloader are indexed and
searched. Here's a github repo for a
[really fast classpath scanner](https://github.com/classgraph/classgraph) to
give you an idea of how this might work.

### PicoContainer

IDEA uses [PicoContainer](http://picocontainer.com/introduction.html) for
dependency injection (DI). PicoContainer is a very simple DI engine that uses
constructor injection primarily and uses Java reflection. So when IDEA itself
launches, it uses PicoContainer to manage loading all of its classes,
interfaces, and objects. And this is extended to any plugin that you write (to
extend IDEA itself).
[Here's a github repo](https://github.com/avh4/picocontainer-example) which
contains some examples of how to use PicoContainer.

When your plugin is loaded into IDEA, PicoContainer is used to instantiate the
classes that your plugin provides to IDEA itself, and this is where things like
project and application components can be injected into the constructors of your
components (more on this below).

### plugin.xml

### Components

#### Examples

### Services

#### Examples

### Extensions

#### Examples

### Extension points

#### Examples

## Persisting state between IDE restarts

### PersistentStateComponent and Services

### Examples

## Actions

### Examples

## Unit testing

### JUnit4 and AssertJ

### Fixtures

### Examples
