---
author: Nazmul Idris
date: 2016-10-02 05:37:30+00:00
excerpt: |
  The purpose of this tutorial is to serve as a starting point for a real world
  React and Firebase example. The starter project is on GitHub.
layout: post
title: "Building a real world app using React, Firebase, and Typescript"
hero-image: assets/react-firebase-typescript-hero.png
categories:
- Firebase
- UXE
- Web
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
  - [What does this project actually do?](#what-does-this-project-actually-do)
- [Setting up your environment](#setting-up-your-environment)
  - [Install NodeJS](#install-nodejs)
  - [Install all the other things](#install-all-the-other-things)
  - [Get the code from GitHub](#get-the-code-from-github)
  - [Setup Firebase](#setup-firebase)
- [Your map of the code](#your-map-of-the-code)
- [Patterns used in the code](#patterns-used-in-the-code)
  - [Event emitters / Event listeners / Observables](#event-emitters--event-listeners--observables)
    - [Local events](#local-events)
    - [Firebase Database patterns](#firebase-database-patterns)
    - [React UI update patterns](#react-ui-update-patterns)
    - [Socket.IO patterns](#socketio-patterns)
- [Typescript](#typescript)
- [Material Design](#material-design)
- [Firebase Auth](#firebase-auth)
- [Misc](#misc)
- [Getting the code](#getting-the-code)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

I'd been looking for a good starter project to tie together React, Firebase, and Material Design, and I wanted it to be lightweight enough to get started with quickly, but deep enough so that it would be realistic enough to use in actual projects.

With this in mind, I set out to create the starter project that is on [GitHub here](https://github.com/r3bl-alliance/starterproject_todolist_react_firebase_ts_md). The core technologies used in this starter project are:

  * [React](https://facebook.github.io/react/)
  * [Firebase](https://www.firebase.com/)
  * [ES6 ](http://es6-features.org/#Constants)
  * [Typescript](https://www.typescriptlang.org/), [Typescript with NodeJS](https://basarat.gitbooks.io/typescript/content/docs/quick/nodejs.html)
  * [Material UI for React](http://www.material-ui.com/#/)
  * [Flexbox layout](http://flexboxfroggy.com/)
  * [Socket.IO](http://socket.io/)

Please note that is not for beginners, but is more for someone who knows these technologies and wants to put them together into real world applications. If you want to get started with the basics, here are some good resources:

  * React JS Essentials book - [https://goo.gl/UkHggE](https://goo.gl/UkHggE)
  * Udemy React Course - [https://www.udemy.com/react-redux/](https://www.udemy.com/react-redux/)
  * Basic code example for (redux/react/firebase) - [https://github.com/r-park/todo-react-redux](https://github.com/r-park/todo-react-redux)

### What does this project actually do?

To see it in action, see it deployed on [heroku](https://todolist-r3bl-alliance.herokuapp.com/). This project is a simple todo list app that stores its data in Firebase. And it uses Material Design and Flexbox layout for the UI, along with React. Additionally, it supports signed in users, so that all the data is stored on the user's behalf based on their social identity (anonymous auth and Google sign in is supported via Firebase).

When the app first starts up, you will be able to create todo list items. These are saved for the anonymous user that's automatically created when the app launches. This is explained in more detail below in the Firebase Auth section. When you click on the user icon on the top right hand corner of the app, you will be asked to connect the app using your Google profile (via OAuth 2.0), which is handled by Firebase Auth as well. Once you provide your authorization, it will copy the todo data to a new account that is permanent and tied to your social identity. If you then sign in to this app from any number of machines, the same todo data will be available everywhere. As you make changes to this data (in real time) you will see these changes appear everywhere that you have the app running (as long as you are online on those machines).

![]({{'assets/react-firebase-typescript-1.png' | relative_url}})

## Setting up your environment

The project on GitHub uses node and Webpack in order to make sure that everything transpiles and deploys in your development and production environment. This project is ready to be deployed to a Heroku node container as is. I'm not going to go into the specifics of Babel, Webpack, Heroku, or Node in this tutorial.

To get started you will need the following on your development machine:

  * `node`
  * `babel`
  * `webpack` and `webpack-dev-server`
  * `typescript` and `typings`

### Install NodeJS

Make sure to install Node if you havent' already. Here are directions on MacOS using `brew`:

  * `/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`

  * `brew install node`

### Install all the other things

To install all the other things on your machine (these are all installed globally and not specific to this project):

  * `npm install babel webpack webpack-dev-server typescript typings -g`

  * `typings install dt~node --global --save`

### Get the code from GitHub

Then checkout the source code from GitHub and go to the folder where you downloaded this project and run (to install all the project scoped dependencies):

  * `npm install`

### Setup Firebase

Whew! We aren't done yet, with the setup. Now, you have to setup your Firebase console and setup a new project and make sure to setup the project to enable Auth. Here are the details:

  * Create a new project

  * Set Database -> Rules to read/write by public using `{ "rules": { ".read": true, ".write": true } }`

  * Set the Auth -> SignIn Methods to enable `Google` and `Anonymous`

  * Put the config object generated by Firebase in `constants.js`

Now that you have everything setup and runing on your machine, it's time to dig deeper and understand what it is that you just downloaded!

## Your map of the code

You will find the following packages in the `src` folder:

  * `client` - this folder holds all the code related to the web app

    * `container` - this folder holds all the related to the internal state and lifecycles of the web app itself.

    * `ui` - this folder holds all the React UI code.

  * `global` - this folder holds the code that is shared between the web client app and the web server app.

  * `server` - this folder holds all the server code (spawns Websocket, HTTP server, etc).

Let's do a deep dive of the files in the `container` folder which only holds Typescript files (with the .ts extension):

  * Every `.ts` file gets compiled into a `.js` and `.js.map` file. Eg: `firebase.ts`, gets compiled into `firebase.js` and `firebase.js.map`. So the "real" file is just firebase.ts.

  * `firebase.ts` - This Typescript file contains all the functions that connect to Firebase Database and Firebase Auth. This is a central place where all the Firebase I/O happens.

  * `context.ts` - This Typescript file is actually the main container that is the web client app itself. All the connections to Firebase, server sockets, and all other kinds of lifecycle management and clean operations happen in this file and it can be imported and used everywhere. Event emitters and web sockets are also accessed via the ApplicationContext class in this file.

  * `interfaces.ts` - This is where all the interfaces that describe the types that are used in this folder are stored. Things like what does the data look like, what does a user object look like, etc. This helps you keep track of the types of data that flowing between Firebase and various components of your app.

  * `mutatedata.ts` - This Typescript file contains all the functions that deal with the UI making changes to the underlying Firebase data stores & sync it with the UI (using event emitters).

## Patterns used in the code

To understand the design of the code I've emplouyed some core design patterns that keep things very clear (conceptually). The primary pattern is that of the emitter or observable. To start your self guided journey into the code, I recommend starting with `main.js` and go from there.

### Event emitters / Event listeners / Observables

The key concept here, for those who aren't familiar, is to have an interested party respond to changes in an object, without having any knowledge or awareness of who authored this change or where it occured. This decoupling makes it really easy to bind / glue disparate components together using "invisible wiring". This pattern is quite natural to use for Firebase, React, and Socket.IO. This is a very fundamental pattern that shows up in just about any event driven type of system (and not batch systems).

To abstract the pattern, there are 3 key things that have to happen (in no particular order):

  * The thing that you are interested in observing (aka the observable) has to emit or push an event into the event bus. This is done by naming the event and attaching a payload (JSON object) to it.

  * Your code that is interested in responding to changes in the observable (aka the observer) needs to attach a listener to the event name (which will be emitted above). This takes the form of calling an addListener() or on() method and passing 1. the name of the event, 2. the callback that will run when the event is emitted or fired.

  * You might have to unbind these listeners when they are no longer needed in the lifecycle of your application. This is just good hygene to keep listeners from being fired long after certain components have been torn down.

#### Local events

The project uses the Node event emitter to tie observers to observables. It all begins with this import:

```javascript
const events = require("events");
```

The local event emitter is created in `context.ts` using the following code:

```javascript
this.eventEmitter = new events.EventEmitter()
```

To actually emit or fire events that will be dispatched to listeners / observers, here's what happens in the `emit()` method in `context.ts`.

```javascript
emit(eventName, payload) {
  this.eventEmitter.emit(eventName, payload);
}
```

On the observer-side, to actually respond to an event, this is what has to happen:

```javascript
this.eventEmitter.addListener(
  "actual_name_of_event",
  function callback (param) {
    console.log(param);
  }
);
```

You can see an actual example of this in the `componentWillMount()` method in `app.js`. This code actually shows a [Material Design Snackbar](http://www.material-ui.com/#/components/snackbar) in response to the `LE_SHOW_SNACKBAR` event that is emitted (these constants are in the `constants.js` file).

```javascript
this.le_showSnackbarListener = applicationContext.addListener(
  GLOBAL_CONSTANTS.LE_SHOW_SNACKBAR,
  function callback (param) {
    this.showSnackBar(param);
  }
);
```

To emit / fire an event that reaches this listener you would have to do this:

```javascript
applicationContext.emit(GLOBAL_CONSTANTS.LE_SHOW_SNACKBAR,
                        "text to show in snackbar");
```

#### Firebase Database patterns

It turns out that Firebase itself uses this same exact pattern for propagating changes data that's stored in the cloud. Firebase is a realtime object database, that is very different than traditional SQL databases. All Firebase clients maintain a local copy of the data that is written to first, before these changes are propagated to the cloud. When these changes are applied locally, the Firebase client then notifies all interested components of your app that the data has changed.

In the case of Firebase:

  * The observable is just about any Firebase node that you hold a reference to.

  * The observer is any component in your code that has registered a callback to a Firebase reference (the reference is the event name in our analogy). The payload that is passed to the callback you register to the on() or once() methods of Firebase is the JSON object that is at the node that you have the Firebase reference to.

One key thing to remember with Firebase is that when you register an on() listener with it, it will be fired on ALL listeners, even if your component is the one making the change. So it won't just skip sending a notification to your component, since it knows that you're the author of the change, and you don't need to be poked that the thing that you just changed, acutally did change. So keep this in mind when designing for Firebase. You pretty much have to rely on the Firebase callback mechanism to notify your own code that it has made changes to the data, you can't take advantage of the fact that you know this - otherwise you risk breaking Firebase synchrnoization.

Another key thing to remember with Firebase is that if you register for on() events of type `child_added`, `child_removed`, etc. then when you first connect to the Firebase reference, all the events that are stored in the local database will be immediately applied to your listener. This is very unintiutive, since you might want to sense the deltas from this point in time forwards. There is a way to do this, but it requires the use of timestamps on the server side and asking for changes based on timestamps. This is a more advanced topic and I will cover this in another tutorial.

Here are some code examples of Firebase using the observer / observable pattern. The following code example is from the `_loadDataForUserAndAttachListenerToFirebase()` method in the `firebase.ts` file. It registers a listener that is called everytime the JSON object stored in the `userDataRootRef` node changes in Firebase.

```javascript
let userId = ctx.getUserId();
let userDataRootRef = _getUserDataRootRef(ctx, userId);
userDataRootRef.on(
  "value",
  function callback(snap) {
    _processUpdateFromFirebase(snap, ctx);
  }
);
```

Here is the code that saves data to Firebase (which ends up triggering the callback above).

```javascript
// apply the action locally, and this will change the state
ctx.getReduxStore()
   .dispatch(action);
// save to persistence
let root_ref = _getUserDataRootRef(ctx, ctx.getUserId());
let value = ctx.getReduxState().data;
value[DB_CONST.SESSION_ID] = ctx.getSessionId();
value[DB_CONST.TIMESTAMP] = ctx.getFirebaseServerTimestampObject();
root_ref.child(DB_CONST.DATA_KEY)
        .set(value);
```

#### React UI update patterns

The observer - observable pattern works nicely with React. React itself is totally event driven. The idea with React is that it figures out how to pain the DOM tree more efficiently based on changes un underlying state that is explicicly declared in your code. There's a render() method that simply paints the current state to the UI. For native UI developers (on mobile or desktop), this is nothing new, and is a very familiar pattern. For the web, where components and subclassing components is new, this is a new thing.

To tie React to the event emitter pattern is super straightforward:

  * When the component mounts, simply attach a listener to the event name you are interested in. This will ensure that your listener will be poked when this event is fired (when the observable changes).

  * In your listener, make sure to take the payload and apply that to the underlying state object that you are maintaining in React. The state object can simply be set in your constructor.

  * In the render method, make sure to pull things out of the state object and paint them.

  * When the component unmounts, simply detact the listener, so that it will no longer respond to events that are fired by the observable.

#### Socket.IO patterns

Turns out that Socket.IO uses a near identical pattern to do it's thing. In order to fire something off to a socket, you simply emit() an event and payload to it. Similarly, you can attach a listener (using on() or addListener()) and it will invoke your callback when this named event is fired.

On the client, to create the socket:

```javascript
let io = require("socket.io-client");
this.socket = new io.connect(this.getSocketURL());
```

To emit an event to the server, the code is similar to the Node local emitter.

```javascript
this.socket.emit("my_named_event", {key:"value"});
```

On the server, to recieve this event, you have to setup a Socket.IO object.

```javascript
let http = require('http');
let httpServer = http.createServer(
  function handler(req, res) {
    res.writeHead(200, {"Content-Type": "text/html"});
    res.end("<h1>Socket IO Server Running</h1>");
  }
);

let io = require("socket.io");
socketio = io.listen(httpServer);
```

Then you attach a listener to it on the server:

```javascript
socketio.on(
  "connection",
  function callback(socket) {
    socket.on(
      "my_named_event",
      function listen(data) {
        console.log("Received message from client: " + data);
      }
  );
 }
)
```

## Typescript

I chose to use Typescript for parts of this project (the container classes) in order to leverage the power of static type checking to reduce the errors and increase quality of code. Using this event emitter pattern, payloads are flying all over the place. And without having any idea of the interface or type of the object that is expected to be fired or responded it, all hell can break loose.

For more info check out - [https://www.typescriptlang.org/](https://www.typescriptlang.org/)

## Material Design

I used Material Design UI library for React for this project, since I really like Material Design and wanted to provide an example of how to use the UI library. I don't spend too much effort in theming these components, though I do provide examples of how to customize themes and apply local styling.

For more info check out - [http://material-ui.com](http://material-ui.com)

## Firebase Auth

I decided to use Firebase Auth to provide anonymous auth and signedin auth for this app. Anonymous auth is a good idea for a variety of reasons:

  * You can leverage the power of signed in experience and remember things (create state and context) for the user while not burdening them with signing in.

  * Once you do decide to convert the user from anonymous to named or signed in, then you can save all the data (state and context) that they've created and simply make it part of the newly created user's data set.

Here's the main callback that you register with Firebase which is called anytime the auth state changes from signed-out -> signed-in-anonymously -> signed-in-withgoogle. This code is from the `initAuth()` method of the `firebase.ts` file.

```javascript
// setup auth
ctx.getFirebase()
   .auth()
   .onAuthStateChanged(
     function callback(user) {
       if (user) {
         // user is signed in
         _processAuthStateChange(ctx, user);
       } else {
         // user is signed out
         _forceAnonSignIn(ctx);
       }
     }
   );
```

## Misc

Lodash is pretty awesome. It's used in this project, learn more about it [here](http://colintoh.com/blog/lodash-10-javascript-utility-functions-stop-rewriting).

If you use Chrome, the React and Redux Dev Tool extensions are very useful:

  * Install the React DevTools for Chrome [here](https://goo.gl/1XNSjY).

  * Install the Redux DevTools for Chrome [here](https://goo.gl/HTKf5g).

## Getting the code

You can get the [code on GitHub](https://github.com/r3bl-alliance/starterproject_todolist_react_firebase_ts_md).
