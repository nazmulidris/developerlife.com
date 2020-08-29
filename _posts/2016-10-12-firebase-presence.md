---
author: Nazmul Idris
date: 2016-10-12 19:40:50+00:00
excerpt: |
  This tutorial will show you how to use Firebase to to build user presence
  tracking into web apps. The code for this tutorial is in GitHub.
layout: post
title: "Using Firebase for user presence tracking"
hero-image: assets/firebase-presence-hero.png
categories:
- DB
- Web
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [How this is built](#how-this-is-built)
  - [Sensing network connectivity](#sensing-network-connectivity)
  - [Responding to user state changes](#responding-to-user-state-changes)
    - [UI updates](#ui-updates)
- [Getting the code](#getting-the-code)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

Firebase handles so many core infrastructure needs that modern apps have, ranging from persistence to authentication to
offline mode. This tutorial is all about how to leverage Firebase to build a presence system for signed in users. The
idea is for your app to sense when a signed in user is online, idle, away, and offline. So not only do you see which
users are currently online, but also what their detailed state is. Both idle and away are forms of being online. Offline
might mean that the user has closed the app or they don't have network connectivity.

To see this app in action, click [here](https://todolist-redux-r3bl-alliance.herokuapp.com/) and then sign in to the
app.

![]({{'assets/firebase-presence-1.png' | relative_url}})

## How this is built

For details on how this is done, check out `presence.ts` on
[GitHub](https://github.com/nazmulidris/starterproject_todolist_react_redux_firebase_ts_md/blob/main/web/src/client/container/presence.ts).
This is part of a todo list app that is built using
[React, Redux, Firebase, and Typescript](https://developerlife.com/2016/10/07/getting-started-with-react-redux-and-firebase/).

The main thing that drives presence track is Firebase's ability to sense if the client app (on any platform) is
currently online or offline. So it can track network state on the client app or device that the Firebase client is
running on. It can also respond on the server side to network connectivity changes (eg: when the client device loses
network, or the app is closed).

### Sensing network connectivity

There's a special path that you can create a Firebase reference to (in your client app) that listens to changes in
network connectivity on the device that this client is running on (web browser on a laptop, or native app on a mobile
device). Here's the location: `.info/connected`. This is what it looks like to attach a value change listener to this
path.

```javascript
const userListRef = firebase.database().ref("USERS_ONLINE");
const myUserRef = userListRef.push();

// Monitor connection state on browser tab
firebase
  .database()
  .ref(".info/connected")
  .on("value", function(snap) {
    if (snap.val()) {
      // if we lose network then remove this user from the list
      myUserRef.onDisconnect().remove();
      // set user's online status
      setUserStatus("online");
    } else {
      // client has lost network
      setUserStatus("offline");
    }
  });
```

This is what is happening in the code above:

- At the start of code block, a `userListRef` object is created that will be used to store an object for each user that
  is active in the app. `myUserRef` is a pointer to this user object that is returned by `push()`. The idea here is that
  all the users that are online in the system have an entry in this `userListRef` node in Firebase. And as they go
  offline, this entry is removed from Firebase. This is what allows your app to sense which users are online and which
  ones have gone offline (more on this below).

- When Firebase client senses that network connectivity state changes the callback is invoked. The `snap` object
  contains `true` or `false`. This happens in your client app and this callback runs in your client app.

- When you have network connectivity (`snap.val()` is `true`) and your callback is run, it registers a `onDisconnect()`
  handler on the `myUserRef` object. What this does is that it tells Firebase to `remove()` the `myUserRef` on the
  SERVER side when Firebase senses that the client is no longer connected!

  - When `snap.val()` becomes false and your callback is run, it will actually only run this callback in your client app
    (in your browser tab). Since network is lost, Firebase server will not be notified (obviously).

  - However, Firebase server will sense (after a while) that the Firebase client isn't connected to it anymore. And it
    will run the `remove()` function on the SERVER side!

    - When the client comes back online, this object will be removed from the client side (since they will sync).
      However, when `setUserStatus()` runs it will actually re-create this object on the client with the same key that
      it had before. So when you go from `online` -> `offline` -> `online` again, it all works out! However, they work
      out differently on the client side than the server side. Whew! This is pretty intricate and Firebase essentially
      makes it as simple as it can for you to deal with this.

What does setUserStatus() do? It just takes the currently signed in user and the status (online, away, idle, and
offline) and writes it to myUserRef.

```javascript
let presenceObject = { user: myUserObject, status: myStatus };
myUserRef.set(presenceObject);
```

### Responding to user state changes

The code above simply allows you to sense network connectivity changes in your own client app, but what of the other
users who are connected at the same time? There is another half to this `presence.ts` file, which is how to you detect
when other users have come online or when their status is changing or when they go offline entirely.

```javascript
// update the UI to show that a new user is now online
userListRef.on("child_added", function(snap) {
  const presence: PresenceIF = snap.val();
  ctx.emit(GLOBAL_CONSTANTS.LE_PRESENCE_USER_ADDED, presence);
});

// update the UI to show that a user has left (gone offline)
userListRef.on("child_removed", function(snap) {
  const presence: PresenceIF = snap.val();
  ctx.emit(GLOBAL_CONSTANTS.LE_PRESENCE_USER_REMOVED, presence);
});

// update the UI to show that a user's status has changed
userListRef.on("child_changed", function(snap) {
  const presence: PresenceIF = snap.val();
  ctx.emit(GLOBAL_CONSTANTS.LE_PRESENCE_USER_CHANGED, presence);
});
```

- This block of code just adds 3 callbacks to listen to various child event changes to the userListRef reference to
  Firebase (remember that this holds entries for every user that is online and when they go offline this entry is
  removed).

- In each of the callbacks a different event is emitted that notifies the rest of the system that these changes have
  occurred. And in this example, the `groupchat.tsx` file is what responds to these events and paints the UI with these
  changes.

- To learn more about the event emitter (observer / observable) pattern, please read
  [this tutorial](https://developerlife.com/2016/10/02/getting-started-with-react-and-firebase/).

#### UI updates

The `groupchat.tsx` file
([GitHub](https://github.com/nazmulidris/starterproject_todolist_react_redux_firebase_ts_md/blob/main/web/src/client/ui/groupchat.tsx))
simply attaches listeners to the `PRESENCE_USER_ADDED`, `PRESENCE_USER_REMOVED`, and `PRESENCE_USER_CHANGED` events.
This is what that code looks like:

```javascript
// respond to changes in presence
applicationContext.addListener(GLOBAL_CONSTANTS.LE_PRESENCE_USER_ADDED, (presence: PresenceIF) => {
  const msg: ChatMessageIF = {
    message: `${presence.user.displayName} joined`,
    displayName: "The App",
    photoURL: "https://url/image.png",
    timestamp: new Date().getTime()
  };
  this.rcvMsgFromServer(msg);
});

applicationContext.addListener(GLOBAL_CONSTANTS.LE_PRESENCE_USER_REMOVED, (presence: PresenceIF) => {
  const msg: ChatMessageIF = {
    message: `${presence.user.displayName} left`,
    displayName: "The App",
    photoURL: "https://url/image.png",
    timestamp: new Date().getTime()
  };
  this.rcvMsgFromServer(msg);
});

applicationContext.addListener(GLOBAL_CONSTANTS.LE_PRESENCE_USER_CHANGED, (presence: PresenceIF) => {
  const msg: ChatMessageIF = {
    message: `${presence.user.displayName} is ${presence.status}`,
    displayName: "The App",
    photoURL: "https://url/image.png",
    timestamp: new Date().getTime()
  };
  this.rcvMsgFromServer(msg);
});
```

There's an important thing that happens in `rcvMsgFromServer()` that is worth noting, and this has to do with using
`setState()` in React. Make sure NOT to re-use partial state to create new state. Just make a new state object and
`setState()` with it, and let React figure out what needs to be rendered / re-rendered, otherwise, you will confuse
React with what it should mark as dirty and needing re-rendering.

```javascript
rcvMsgFromServer(data: ChatMessageIF) {
  const {chatMessageList} = this.state;
  let copy = lodash.clone(chatMessageList);
  copy.push(data);
  this.setState({chatMessageList: copy});
}
```

## Getting the code

You can get the [code on GitHub](https://github.com/r3bl-alliance/starterproject_todolist_react_redux_firebase_ts_md).
