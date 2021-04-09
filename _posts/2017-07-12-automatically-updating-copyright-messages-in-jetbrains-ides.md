---
author: Nazmul Idris
date: 2017-07-12 18:08:13+00:00
excerpt: |
  Pro Tip on automatically updating copyright strings in your JetBrains based IDEs (including Android Studio)
layout: post
title: "Automatically updating copyright messages in JetBrains IDEs"
categories:
  - Misc
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [How to add copyright to Android Studio](#how-to-add-copyright-to-android-studio)
  - [Step 1 - Create a copyright profile](#step-1---create-a-copyright-profile)
  - [Step 2 - Create a scope to apply the `android` profile to](#step-2---create-a-scope-to-apply-the-android-profile-to)
  - [Step 3 - Tell Studio to apply this to all the files](#step-3---tell-studio-to-apply-this-to-all-the-files)
  - [Step 4 - Quick way to update copyright for commits](#step-4---quick-way-to-update-copyright-for-commits)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

It is a pain to manually update copyright messages in open source code that you're going to release
on GitHub 😩. There is a better way. You can have JetBrains based IDEs (Android Studio, Webstorm,
etc) just do it for you.

I'm going to use Android Studio as an example, but this works on Webstorm, etc.

## How to add copyright to Android Studio

Open Android Studio and follow these setps in order to automagically generate copyright messages for
all your project files.

### Step 1 - Create a copyright profile

![]({{ 'assets/copyright-1.png' | relative_url }})

- Open Preferences, and navigate to `Editor` -> `Copyright` -> `Copyright Profiles`.
- Create a new profile and name it `android`.
- Paste the following text into the dialog box, replacing the default text that's already there.

```text
Copyright $today.year YOURCOMPANY. All rights reserved.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

- Make sure to replace `YOURCOMPANY` with your name or the name of the company that the copyright
  belongs to.
- The `$today.year` snippet is a Velocity template string that just inserts the current year into
  the copyright message when it's updated.
- Click on OK.

### Step 2 - Create a scope to apply the `android` profile to

![]({{ 'assets/copyright-2.png' | relative_url }})

- In Preferences, navigate to `Editor` -> `Copyright`.
- Apply the `android` profile the default for the project.
- Add the `Project Files` scope and apply `android` to it.
- Click on OK.

### Step 3 - Tell Studio to apply this to all the files

![]({{ 'assets/copyright-3.png' | relative_url }})

- Right click on your project's root and select `Update Copyright ...`.
- Make sure to apply this to the `Whole project` and `Update existing copyrights`.
- Click OK.

### Step 4 - Quick way to update copyright for commits

![]({{ 'assets/copyright-4.png' | relative_url }})

- When you commit your changes using Android Studio, you can just check the `Update Copyright` so
  that the changed files will have their copyright messages updated.
