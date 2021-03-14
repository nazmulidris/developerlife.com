---
author: Nazmul Idris
date: 2021-03-13 14:00:00+00:00
excerpt: |
  Advanced guide to creating JetBrains Platform plugins: VFS, PSI, Kotlin UI DSL, Dialog, Tool window, List,
  Swing UI and layout managers, ConsoleView, LineMarker. This is a companion of the Introduction to creating IntelliJ 
  IDEA plugins tutorial.
layout: post
title: "Advanced guide to creating IntelliJ IDEA plugins"
categories:
  - IJ
  - KT
---

<img class="post-hero-image" src="{{ 'assets/jetbrains-plugin.svg' | relative_url }}"/>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Overview](#overview)
- [IDEA threading model](#idea-threading-model)
- [PSI access and mutation](#psi-access-and-mutation)
- [Dynamic plugins](#dynamic-plugins)
- [VFS and Document](#vfs-and-document)
- [Swing UI](#swing-ui)
- [Kotlin UI DSL](#kotlin-ui-dsl)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Overview

This article is a reference covering a lot of advanced topics related to creating IDEA plugins using the JetBrains
IntelliJ Platform SDK. However there are many advanced topics that are not covered here (such as
[custom language support](https://plugins.jetbrains.com/docs/intellij/custom-language-support.html)).

In order to be successful creating advanced plugins, this is what I suggest:

1. Read thru the [Introduction to creating IntelliJ IDEA
   plugins]({{ '2020/11/20/idea-plugin-example-intro/' | relative_url }}) in detail. Modify the
   [idea-plugin-example](https://github.com/nazmulidris/idea-plugin-example),
   [idea-plugin-example2](https://github.com/nazmulidris/idea-plugin-example2), or
   [shorty-idea-plugin](https://github.com/r3bl-org/shorty-idea-plugin) to get some hands on experience working with the
   plugin APIs.
2. Use the [Official JetBrains IntelliJ Platform SDK docs](https://plugins.jetbrains.com/docs/intellij/welcome.html),
   along with the source code examples (from the list of repos above) to get a better understanding of how to create
   plugins.
3. When you are looking for something not in tutorials here (on developerlife.com) and in the official docsd, then
   search the [`intellij-community`](https://github.com/JetBrains/intellij-community) repo itself to find code examples
   on how to use APIs that might not have any documentation. An effective approach is to find some functionality in IDEA
   that is similar to what you are looking to build, and then locate the source code for that feature in the repo and
   see how JetBrains has done it.

## IDEA threading model

## PSI access and mutation

## Dynamic plugins

## VFS and Document

## Swing UI

## Kotlin UI DSL
