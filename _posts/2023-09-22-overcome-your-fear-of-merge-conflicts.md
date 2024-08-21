---
title: "How to overcome your fear of git merge conflicts"
author: Nazmul Idris
date: 2023-09-22
excerpt: |
  A visual guide on how to understand git merge conflict messages
  and resolve them with confidence.
layout: post
categories:
  - CLI
---

<img class="post-hero-image" src="{{ 'assets/git-merge-conflict-hero.svg' | relative_url }}"/>

<!-- TOC -->

- [Introduction](#introduction)
- [Setting the stage for a merge conflict](#setting-the-stage-for-a-merge-conflict)
- [Picture 1: How we got here](#picture-1-how-we-got-here)
- [Picture 2: The conflict when develop is applied to main](#picture-2-the-conflict-when-develop-is-applied-to-main)
- [Picture 3: How to understand the diff](#picture-3-how-to-understand-the-diff)
- [Picture 4: How to resolve the conflict](#picture-4-how-to-resolve-the-conflict)
- [Build with Naz video series on developerlife.com YouTube channel](#build-with-naz-video-series-on-developerlifecom-youtube-channel)

<!-- /TOC -->

## Introduction
<a id="markdown-introduction" name="introduction"></a>

There are few things that generate as much fear and anxiety in developers as `git` merge
conflicts. `git` is very popular and very powerful, and it is a low level command line
tool. And it is not very user friendly. It is meant to be orchestrate-able and automated
using scripts and CI/CD tools, and build systems; it is extremely flexible. It is not
meant to be used in an interactive manner w/ a human user at the keyboard.

This just creates an opportunity for others to come along and craft user experiences on
top of `git` that are more use case driven. And these UXes can come in the form or GUIs,
TUIs, or even conversational interfaces.

But that's not the focus of this article which is all about the CLI experience of inducing
and resolving merge conflicts. So let's get started.

## Setting the stage for a merge conflict
<a id="markdown-setting-the-stage-for-a-merge-conflict" name="setting-the-stage-for-a-merge-conflict"></a>

Let's create a local repo from scratch and set things up so that we can predictably
generate a merge conflict. Here's what we will do at a high level:
1. Create a local repo.
1. Create a `main` branch.
1. Create a file in the `main` branch and add some content to it.
1. Create a `feature` branch based on the `main` branch.
1. Modify the file in the `feature` branch.
1. Modify the same file in the `main` branch with a change that is going to conflict w/ a change in `feature` branch.
1. Merge the `feature` branch into the `main` branch.

Here's a script to get you started:

```bash
#!/usr/bin/env bash

# Create a local repo.
export TMP_REPO_DIR="~/Downloads/tmp/git-merge-conflict-demo"
if [ -d $TMP_REPO_DIR ]; then
  echo "Folder exists, recreating $TMP_REPO_DIR"
  rm -rf $TMP_REPO_DIR
  mkdir -p $TMP_REPO_DIR
else
  echo "Folder does not exist, creating $TMP_REPO_DIR"
  mkdir -p $TMP_REPO_DIR
fi
cd $TMP_REPO_DIR
git init
git checkout -b main

# Create a file in the main branch and add some content to it.
# This is the "OG change".
echo -e "This is a new feature.\n## 3. Example 3" > file.txt
git add file.txt
git commit -m "Add myexample3"

# Create a develop branch based on the main branch.
git checkout -b develop main

# Person A comes along and changes this line w/ a plus in the develop branch.
echo -e "This is a new feature.\n## 3. Example 3+" > file.txt
git add file.txt
git commit -m "Fix typo w/ plus in develop branch"

# Person B comes along and change this line w/ a minus in the main branch.
# This is going to conflict with the change in the develop branch.
git checkout main
echo -e "This is a new feature.\n## 3. Example 3-" > file.txt
git add file.txt
git commit -m "Fix typo w/ minus in main branch"

# Merge (using rebase, so no extra commit) the develop branch into the main branch.
git rebase develop
```

This results in a merge conflict. And when you run `git diff` it looks like this:

```diff
diff --cc file.txt
index 89da142,ef43c8f..0000000
--- a/file.txt
+++ b/file.txt
@@@ -1,2 -1,2 +1,8 @@@
  This is a new feature.
++<<<<<<< HEAD
 +## 3. Example 3+
++||||||| parent of 7c0f0e4 (Fix typo w/ - in main branch)
++## 3. Example 3
++=======
+ ## 3. Example 3-
++>>>>>>> 7c0f0e4 (Fix typo w/ - in main branch)
```

Let's use some pictures to understand the story of how we got here. And how to resolve this.

## Picture 1: How we got here
<a id="markdown-picture-1%3A-how-we-got-here" name="picture-1%3A-how-we-got-here"></a>

![]({{'assets/git-merge-conflicts/act1.svg' | relative_url}})

## Picture 2: The conflict when develop is applied to main
<a id="markdown-picture-2%3A-the-conflict-when-develop-is-applied-to-main" name="picture-2%3A-the-conflict-when-develop-is-applied-to-main"></a>

![]({{'assets/git-merge-conflicts/act2.svg' | relative_url}})

## Picture 3: How to understand the diff
<a id="markdown-picture-3%3A-how-to-understand-the-diff" name="picture-3%3A-how-to-understand-the-diff"></a>

![]({{'assets/git-merge-conflicts/act3.svg' | relative_url}})

## Picture 4: How to resolve the conflict
<a id="markdown-picture-4%3A-how-to-resolve-the-conflict" name="picture-4%3A-how-to-resolve-the-conflict"></a>

![]({{'assets/git-merge-conflicts/act4.svg' | relative_url}})

## Build with Naz video series on developerlife.com YouTube channel
<a id="markdown-build-with-naz-video-series-on-developerlife.com-youtube-channel" name="build-with-naz-video-series-on-developerlife.com-youtube-channel"></a>

> If you have comments and feedback on this content, or would like to request new content
> (articles & videos) on developerlife.com, please join our [discord
> server](https://discord.gg/8M2ePAevaMi).

You can watch a video series on building this crate with Naz on the
[developerlife.com YouTube channel](https://www.youtube.com/@developerlifecom).

- [YT channel](https://www.youtube.com/@developerlifecom)
- Playlists
    - [Build with Naz, Linux TTY, process, signals, commands in async Rust](https://www.youtube.com/watch?v=bolScvh4x7I&list=PLofhE49PEwmw3MKOU1Kn3xbP4FRQR4Mb3)
    - [Build with Naz, fundamental effective Rust](https://www.youtube.com/playlist?list=PLofhE49PEwmza94sS7UmJnN9gSCHTVTfz)
    - [Build with Naz, effective async Rust and tokio](https://www.youtube.com/playlist?list=PLofhE49PEwmwO69E7eiQ-ewnMME8ydgQ5)
    - [Build with Naz, async readline and spinner for CLI in Rust](https://www.youtube.com/watch?v=3vQJguti02I&list=PLofhE49PEwmwelPkhfiqdFQ9IXnmGdnSE)
    - [Build with Naz, testing in Rust](https://www.youtube.com/watch?v=Xt495QLrFFk&list=PLofhE49PEwmwLR_4Noa0dFOSPmSpIg_l8)
