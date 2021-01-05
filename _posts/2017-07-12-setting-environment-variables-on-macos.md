---
author: Nazmul Idris
date: 2017-07-12 17:43:35+00:00
excerpt: |
  Pro Tip on setting environment variables for ANDROID_HOME and JAVA_HOME when
  you setup your development environment on a new machine
layout: post
title: "Setting environment variables on macOS"
categories:
  - Misc
---

Everytime I get a new computer, I install Java on it, and then Android Studio. And everytime I have to remember how to
set `ANDROID_HOME` and `JAVA_HOME`. And I forget, and do the same Google searches 😄. So I've decided to write it down
this time.

In your home directory, create this `.profile` file.

```bash
# more info https://goo.gl/YHmHGp
export JAVA_HOME=$(/usr/libexec/java_home)
export ANDROID_HOME=/Users/nazmul/Library/Android/sdk
export PATH="/Users/nazmul/scripts:$PATH"
launchctl setenv ANDROID_HOME $ANDROID_HOME
launchctl setenv JAVA_HOME $JAVA_HOME
```

Now replace all the `/Users/nazmul` folders with your username!

Then restart Terminal, and you are good to go.

This will work for launching Android Studio from Finder as well. Since if you don't do the `launchctl` stuff, your
environment variables will be set when you're in Terminal, but not when you launch something from Finder.
