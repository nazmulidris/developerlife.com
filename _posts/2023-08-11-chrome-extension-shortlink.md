---
title: "Build a Chrome Extension using Manifest V3"
author: Nazmul Idris
date: 2023-08-11 15:00:00+00:00
excerpt: |
  A guide on how to build a Chrome Extension using Manifest V3
  that replaces the use of bookmarks (in a way) allowing you to
  create your own names for a URL or a set of URLs.
layout: post
categories:
  - TS
  - Web
  - React
---

<img class="post-hero-image" src="{{ 'assets/chrome-extension.svg' | relative_url }}"/>

<!-- TOC -->

- [Introduction](#introduction)
- [Step 1: Create a new Chrome Extension](#step-1-create-a-new-chrome-extension)
- [Step 2: Build and load the Chrome Extension](#step-2-build-and-load-the-chrome-extension)
- [Step 3: Add functionality](#step-3-add-functionality)
- [Step 4: Publish it](#step-4-publish-it)
- [Next steps: Contribute to the Shortlink project](#next-steps-contribute-to-the-shortlink-project)

<!-- /TOC -->

## Introduction
<a id="markdown-introduction" name="introduction"></a>


In this tutorial we will create a new Chrome Extension using Manifest V3 that allows us to create
our own names for a URL or a set of URLs. This is useful when you have a set of URLs that you want
to open at once, or you want to create a name for a URL that is hard to remember. Or if you just
don't want to use bookmarks. We will also save these shortlinks to the Chrome Sync key-value pair
store. This extension will also allow the user to type commands when it is activated (in its popped
up state). And we will use Typescript and React to build it.

Before we get started, here are some good references to take a look at:

1. [Official Chrome docs on writing an extension](https://developer.chrome.com/docs/extensions/mv3/intro/)
2. [Template to build a Chrome extension without having to configure Typescript and React](https://github.com/r3bl-org/chrome-extension-typescript-react-template)

> 🚀 Please star and fork / clone the [Shortlink repo](https://github.com/r3bl-org/shortlink) 🌟
> Install the
> [Chrome Extension](https://chrome.google.com/webstore/detail/r3bl-shortlink/ffhfkgcfbjoadmhdmdcmigopbfkddial?hl=en-US&gl=US)
> 🛠️

{%- include featured.html -%}

## Step 1: Create a new Chrome Extension
<a id="markdown-step-1%3A-create-a-new-chrome-extension" name="step-1%3A-create-a-new-chrome-extension"></a>


The first thing to is to create a new repo on GitHub using this
[template repo](https://github.com/r3bl-org/chrome-extension-typescript-react-template).

You can do this in two ways.

1. Using github.com and a web browser. Here are the
   [instructions](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)
   on how to do this.
2. Using the GitHub CLI. You must have the [GitHub CLI](https://cli.github.com/) installed and be
   logged in to github.com (using `gh auth login`).
   ```sh
   # More info: https://cli.github.com/manual/gh_repo_create
   gh repo create shortlink --public --template r3bl-org/chrome-extension-typescript-react-template
   # More info: https://cli.github.com/manual/gh_repo_clone
   gh repo clone shortlink
   ```

## Step 2: Build and load the Chrome Extension
<a id="markdown-step-2%3A-build-and-load-the-chrome-extension" name="step-2%3A-build-and-load-the-chrome-extension"></a>


At this point we have a `shortlink` git repo on our local machine that is setup to build a Chrome
Extension. You can run the following command to build it.

```sh
npm install
npm run build
```

This will generate a `dist/` directory that contains the Chrome Extension. You can load this into
Chrome by:

1. Type `chrome:extensions` in the URL bar.
2. Turn on "Developer Mode".
3. Then click on "Load unpacked" and select the `dist/` directory. Your extension will be loaded
   into Chrome.

## Step 3: Add functionality
<a id="markdown-step-3%3A-add-functionality" name="step-3%3A-add-functionality"></a>


In our extension we will ask for the minimum of
[permissions](https://developer.chrome.com/docs/extensions/reference/permissions/) from the user.
This ensures that our extension doesn't have access to anything more than it needs. All of this is
specified in the `public/manifest.json` file. Here's an example of what this file might look like
when we are done building our extension.

```json
{
  "manifest_version": 3,
  "name": "R3BL Shortlink",
  "description": "Make go links",
  "version": "2.0",
  "icons": {
    "16": "icon16.png",
    "32": "icon32.png",
    "48": "icon48.png",
    "128": "icon128.png"
  },
  "action": {
    "default_title": "Click to make go link for URL",
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icon16.png",
      "32": "icon32.png",
      "48": "icon48.png",
      "128": "icon128.png"
    }
  },
  "omnibox": {
    "keyword": "go"
  },
  "background": {
    "service_worker": "js/background.js"
  },
  "commands": {
    "_execute_action": {
      "suggested_key": {
        "default": "Alt+L",
        "mac": "Alt+L"
      },
      "description": "Make a go link for URL in address bar"
    }
  },
  "permissions": ["activeTab", "tabs", "storage", "clipboardWrite"]
}
```

Now that we have our permissions sorted, we can start by adding functionality to the extension. When
we activate the extension by clicking its icon in the Chrome toolbar or by pressing the shortcut
<kbd>Alt+l</kbd> the `popup.tsx` file will be run which itself is loaded by `popup.html`.

> You can learn more about activating the extension and the popup in the
> [`chrome.browserAction` docs](https://developer.chrome.com/docs/extensions/reference/browserAction/#popups).

This `popup.tsx` file will be the entry point for our extension. It is the main function in a node
program or the `App` top level component in a React app. It sets up the UI and handles the user
input events (key presses).

> This is what the UI looks like on Linux on my machine:
> ![Shortlink Screenshot]({{'assets/shortlink-image.png' | relative_url}})

This is what the file looks like in the real Shortcut extension:
[`popup.tsx`](https://github.com/r3bl-org/shortlink-react-webpack/blob/main/src/popup.tsx). If you
go through this code, these are some of the things you will notice:

1. The `main()` function just sets up the main React component `Popup` and mounts it to the DOM
   (`div` with id `root`).
2. There are some `useEffect()` hooks which ensures that when `chrome.storage` changes, the global
   state is updated and the component is re-rendered. Learn more about `chrome.storage` in the API
   reference [here](https://developer.chrome.com/docs/extensions/reference/storage/). Another hook
   is responsible for painting the badge on the extension icon in the toolbar (when the
   `Shortlink[]` in the state changes).
3. The `Popup` function component returns some JSX that is used to render the global state, which
   are two things: `Shortlink[]` and `string`. The `Shortlink[]` is used to render the list of
   shortcuts and the `string` is used to render the input field.
4. The `handleOnChange()` and `handleEnterKey()` function is where the user input that is typed is
   interpreted into a command and then executed.

There are some other files of note. Please take a look at their linked source code.

1. [`command.ts`](https://github.com/r3bl-org/shortlink-react-webpack/blob/main/src/command.ts): The
   main logic for parsing a `string` into a command is handled by this file. The
   `parseUserInputTextIntoCommand()` function does all the work of converting a given `string` into
   a `Command`, and has a very Rust "vibe". Please check out how this works. It makes it very easy
   to add or change commands in the future.
2. [`storage.ts`](https://github.com/r3bl-org/shortlink-react-webpack/blob/main/src/storage.ts):
   This is where all the functions to manipulate the storage that syncs w/ Chrome accounts is
   located. Functions that handle shortlinks to be deleted, or added, or updated can all be found
   here. The Chrome storage API is async which is why the code in this file is written in the way
   that it is.
3. [`omnibox.ts`](https://github.com/r3bl-org/shortlink-react-webpack/blob/main/src/omnibox.ts):
   This file works w/ `background.ts` to handle the omnibox functionality. The omnibox is the
   [address bar](https://developer.chrome.com/docs/extensions/reference/omnibox/) in Chrome. When
   the user types `go` and then a space, the omnibox will be activated and the user can type in a
   shortcut. When the user presses <kbd>Enter</kbd>, the `background.ts` file will be run and the
   shortcut will be expanded to the full URL.

## Step 4: Publish it
<a id="markdown-step-4%3A-publish-it" name="step-4%3A-publish-it"></a>


Please read this [guide](https://developer.chrome.com/docs/webstore/publish/) on how to publish the
extension. You will have to get a developer account, and then upload the extension binaries. There's
a `make-distro-zip.sh` script provided in this repo that will create a zip file that you can upload
to the Chrome Web Store.

As part of publishing a version you have to provide justification for why
you are requesting the permissions that you are. The fewer the permissions that you use, the better
for the end user, and also for the review process to take less time.

## Next steps: Contribute to the Shortlink project
<a id="markdown-next-steps%3A-contribute-to-the-shortlink-project" name="next-steps%3A-contribute-to-the-shortlink-project"></a>

> 🚀 Please star and fork / clone the [Shortlink repo](https://github.com/r3bl-org/shortlink) 🌟
> Install the
> [Chrome Extension](https://chrome.google.com/webstore/detail/r3bl-shortlink/ffhfkgcfbjoadmhdmdcmigopbfkddial?hl=en-US&gl=US)
> 🛠️

If you would like to get involved in an open source project and like Chrome extensions, please feel
free to contribute to the [Shortlink repo](https://github.com/r3bl-org/shortlink/issues). There are
a lot of small features that need to be added. And they can be a nice stepping stone into the world
of open source contribution 🎉.
