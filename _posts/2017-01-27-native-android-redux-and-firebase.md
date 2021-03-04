---
author: Nazmul Idris
date: 2017-01-27 10:05:05+00:00
excerpt: |
  Redux and React are things that are normally associated with web development.
  Redux is a beautiful design pattern that can help with any application, even native
  ones! I used Firebase in order to do cross platform data synchronization across
  web and mobile clients. I also used Firebase auth and Material Design to craft a
  real-world app. The code for this tutorial is in GitHub.
layout: post
title: "Android, Redux, Firebase Auth & Database, and Material Design"
hero-image: assets/and-redux-hero.png
categories:
  - Android
  - DB
  - FE
  - State
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [Material Design and Material Components for Android](#material-design-and-material-components-for-android)
- [Architecture](#architecture)
  - [Using Redux and Firebase](#using-redux-and-firebase)
    - [Redux → Store + Middleware + Reducer](#redux-%E2%86%92-store--middleware--reducer)
    - [Firebase Listener(s)](#firebase-listeners)
    - [Android Middleware](#android-middleware)
- [Redux Middleware and Firebase](#redux-middleware-and-firebase)
- [Firebase database and auth](#firebase-database-and-auth)
- [What happens in the reducer and what happens in the middleware and how that relates to Firebase](#what-happens-in-the-reducer-and-what-happens-in-the-middleware-and-how-that-relates-to-firebase)
  - [Actions that are processed by Redux](#actions-that-are-processed-by-redux)
  - [Interaction between Redux and Firebase via Async Action pattern in the Middleware](#interaction-between-redux-and-firebase-via-async-action-pattern-in-the-middleware)
- [App startup time](#app-startup-time)
- [Offline mode](#offline-mode)
- [Anonymous auth vs signed in experience](#anonymous-auth-vs-signed-in-experience)
- [Closing thoughts](#closing-thoughts)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

Redux is normally associated with web development. Redux is a beautiful design pattern that can help with any
application, even native Android ones! This is the approach that I took to integrate the Redux pattern into native
Android development, and leverage the stability and predictability of a finite state machine to native development.

Further, I used Firebase in order to do cross platform data synchronization across web and mobile clients. Firebase has
the benefit of providing offline mode for web and native mobile client apps, which is incredibly powerful.

And I decided to use Firebase authentication for web, and mobile as well, which provides a consolidated way to do cross
platform anonymous authentication and signed in authentication using a variety of social sign in providers (Google,
Facebook, etc.)

Here's a video of the app in action and here's a link to the code that produced this app on
[GitHub](https://github.com/r3bl-alliance/starterproject_todolist_react_redux_firebase_ts_md/tree/978224a82f31f34c84cdaeb91763fcd48a991d5f/mobile_android_native).
It's a pretty sophisticated app, so please pay attention to the video and look thru the code on GitHub. You will find
things like:

- Fast boot time by persisting the redux state to local storage.

- The ability to have anonymous auth (and save the state of the app), then switch to a signed in state and then retain
  the data that was created in the anonymous auth state of the app.

- Proper handling of sign-in and anonymous authentication, and not burdening the user with Login, SignUp, and SignIn.
  Just replace all that with a single button press that takes the app from anonymous-auth mode to signed-in mode.

- Using Redux middleware (and not just reducers) to play nice with Firebase updates, and solve a lot of murky
  synchronization issues that would otherwise present themselves.

- The app also has a sophisticated debug mechanism that exposes the history of redux state transitions and even the
  ability to diff between 2 states in the Android app itself. You can see the app going thru it's state changes from
  startup until present moment. These are incredibly valuable insights that you have on the lifecycle of your
  application that you leverage to build some really compelling apps.

[![Click to play video](https://img.youtube.com/vi/9yhxD2o51ZQ/0.jpg)](https://youtu.be/9yhxD2o51ZQ "Click to play video")

There's a web app that works hand in hand with this mobile app. Here are some links for the web app:

- [Web app code on Github](https://github.com/r3bl-alliance/starterproject_todolist_react_redux_firebase_ts_md/tree/978224a82f31f34c84cdaeb91763fcd48a991d5f/web)
- [Run the web app on heroku](https://todolist-redux-r3bl-alliance.herokuapp.com/)

This is a screenshot of the web app in action:

![]({{ 'assets/and-redux-1.png' | relative_url}})

This is also incredibly powerful because it showcases how the ideas that are used in the Android native app are very
similar to those implemented in the web app, such as:

- Reducers and middleware are very similar on both native Android and web.
- Firebase auth is used in both cases, so that sign-in and anonymous auth work pretty much the same.
- Firebase database is used in a similar way (in addition to the use of middleware) that makes user data synchronization
  between the web and mobile apps seamless, and offline!

## Material Design and Material Components for Android

This entire app is built using Material Components for Android. You can learn more about it
[here](https://material.io/components/android/catalog/).

- It uses both `com.android.support:appcompat-v7` and `com.android.support:design` libraries in the app's
  `build.gradle`.
- It uses AppCompatActivity from the material design support library
  ([MainActivity.java](https://github.com/r3bl-alliance/starterproject_todolist_react_redux_firebase_ts_md/blob/6de82aea9aa38f6dc4f4bd3c7a31887d0093399d/mobile_android_native/app/src/main/java/com/r3bl/todo_app/ui/MainActivity.java)).
- It uses Toolbar, FloatingActionButton, CircleIndicators, ViewPager, BottomSheetDialogFragment, a whole host of other
  Material Design components.
- It uses Material Design
  [themes](https://github.com/r3bl-alliance/starterproject_todolist_react_redux_firebase_ts_md/blob/6de82aea9aa38f6dc4f4bd3c7a31887d0093399d/mobile_android_native/app/src/main/res/values/styles.xml)
  as well.
- It even uses ConstraintLayout in some screens, which was in beta while this was being developed.

Please check out the
[ui package](https://github.com/r3bl-alliance/starterproject_todolist_react_redux_firebase_ts_md/tree/6de82aea9aa38f6dc4f4bd3c7a31887d0093399d/mobile_android_native/app/src/main/java/com/r3bl/todo_app/ui)
of the source code, and the
[res folder](https://github.com/r3bl-alliance/starterproject_todolist_react_redux_firebase_ts_md/tree/6de82aea9aa38f6dc4f4bd3c7a31887d0093399d/mobile_android_native/app/src/main/res/layout)
on GitHub.

## Architecture

For more information on how Redux is used with the native Android app and how it syncs with the web app, check out the
wiki page on [GitHub](https://github.com/r3bl-alliance/starterproject_todolist_react_redux_firebase_ts_md/wiki).

### Using Redux and Firebase

- [More info on Redux Middleware](https://medium.com/@meagle/understanding-87566abcfb7a#.8dlay3nwa)
- [More info on async actions](http://redux.js.org/docs/advanced/AsyncActions.html)
- [More info on JS middleware](https://reactjsnews.com/redux-middleware)

#### Redux → Store + Middleware + Reducer

1. create a middleware for the store
2. in this middleware, when redux actions come in for adding todo items or toggling todo items or deleting todo items,
   then modify what needs to be modified and save it to firebase -> do NOT dispatch these actions!

#### Firebase Listener(s)

1. create a firebase listener that simply takes the snapshot data and creates a redux action (like set_state_data) and
   then applies it to the redux store

#### Android Middleware

```java
private void _initReduxStore() {
  _log = new ReduxDebugLog();
  State state = new State();
  com.brianegan.bansa.Reducer reducer = new Reducer(this);
  _store = new BaseStore<>(state, reducer, new Middleware<State>() {
    @Override
    public void dispatch(Store<State> store, Action action, NextDispatcher next) {
      App.log("Middleware [START]", "");
      App.log("Middleware [state]", store.getState().toString());
      App.log("Middleware [action]", action.toString());
      App.log("Middleware [END]", "");
      next.dispatch(action);
    }
  });
}
```

`next.dispatch(action)` is what allows the middleware to keep processing actions in the chain. If this call was removed,
then the middleware would just stop processing that action (just like java servlet filtering). So it's best to make this
call, and just ignore the actions that don't need to be processed in the reducer. So there are some actions that will be
processed by the middleware and others that will be processed by the reducer.

![]({{'assets/and-redux-2.jpg' | relative_url}})

The Middleware handles the following actions:

1. `AddTodoItemAction` (this writes to Firebase)
1. `ToggleTodoItemAction` (this writes to Firebase)

The Reducer handles the following actions:

1. `ResetStateAction` (no connection to Firebase)
1. `RestoreStateAction` (no connection to Firebase)
1. `SetUserAction` (these are read from Firebase)
1. `SetDataAction` (these are read from Firebase)

## Redux Middleware and Firebase

The Redux library I'm using for this project is the Bansa library on [GitHub](https://github.com/brianegan/bansa). You
can add it to your build.gradle and get started very quickly.

```groovy
// First, add JitPack to your repositories
repositories {
...
maven { url "https://jitpack.io" }
}

// Base package. Everything else is built upon it!
compile 'com.github.brianegan.bansa:bansa:1.0.0-beta'
```

Here are some links that contain some important details about this Redux Middleware and Async Actions pattern (which is
used in the native Android and web app):

- [More info on Redux Middleware](https://medium.com/@meagle/understanding-87566abcfb7a#.8dlay3nwa)
- [More info on async actions](http://redux.js.org/docs/advanced/AsyncActions.html)
- [More info on JS middleware](https://reactjsnews.com/redux-middleware)

The way to get Redux and Firebase to work together is to use Middleware that handles some actions, and have the Reducer
functions handle some other actions (instead of doing it all in the reducers). Now, regardless of whether these actions
are handled by the Middleware or Reducers, they are dispatched to the Redux Store.

The Redux store contains the state of the application, which stores:

1. the currently logged in user data, and
2. the todolist data for this user.

## Firebase database and auth

Both of these things are backed to Firebase. The following video shows what the Firebase database looks like:

[![Click to play video](https://img.youtube.com/vi/Tdnedi6EVxQ/0.jpg)](https://youtu.be/Tdnedi6EVxQ "Click to play video")

## What happens in the reducer and what happens in the middleware and how that relates to Firebase

The following diagrams shows how the various actions are processed by Middleware, or Reducers, and how that interaction
works with Firebase:

![]({{'assets/and-redux-2.jpg' | relative_url}})

### Actions that are processed by Redux

The **Middleware** handles the following actions:

1. `AddTodoItemAction` (this writes to Firebase)
2. `ToggleTodoItemAction` (this writes to Firebase)

```java
@Override
public void dispatch(Store<State> store, Action actionParam, NextDispatcher next) {

  try {

    State newState = store.getState().deepCopy();

    if (actionParam instanceof Actions.AddTodoItem) {

      if (newState.data == null) newState.data = new Data();
      Actions.AddTodoItem action = (Actions.AddTodoItem) actionParam;
      newState.data.todoArray.add(action.getParam());
      _ctx.getDatabase().saveUserDataToFirebase(newState.data);

    } else if (actionParam instanceof Actions.ToggleTodoItem) {

      Actions.ToggleTodoItem action = (Actions.ToggleTodoItem) actionParam;
      int index = action.getParam();
      newState.data.todoArray.get(index).done =
            !newState.data.todoArray.get(index).done;
      _ctx.getDatabase().saveUserDataToFirebase(newState.data);

    }

  } catch (Exception e) {
    App.logErr("StateMiddleware", "problem with dispatch()", e);
  }

  next.dispatch(actionParam);

}
```

The **Reducer** handles the following actions:

1. `ResetStateAction` (no connection to Firebase)
2. `RestoreStateAction` (no connection to Firebase)
3. `SetUserAction` (these are read from Firebase)
4. `SetDataAction` (these are read from Firebase)

```java
@Override
public State reduce(State state, Action actionParam) {

  try {

    State newState = state.deepCopy();

    if (actionParam instanceof Actions.SetUser) {

      Actions.SetUser action = (Actions.SetUser) actionParam;
      newState.user = action.getParam();

    } else if (actionParam instanceof Actions.SetData) {

      Actions.SetData action = (Actions.SetData) actionParam;
      newState.data = action.getParam();

    } else if (actionParam instanceof Actions.RestoreState) {

      Actions.RestoreState action = (Actions.RestoreState) actionParam;
      newState = action.getParam();

    } else if (actionParam instanceof Actions.ResetState) {

      Actions.ResetState action = (Actions.ResetState) actionParam;
      newState = new State();

    }

    ctx.getReduxLog().push(ctx.getTime(), state, actionParam, newState);

    App.log("Reducer", "applying action: " + actionParam.getClass().getSimpleName());

    return newState;

  } catch (Exception e) {
    App.logErr("Reducer", "problem running reduce()", e);
  }
  return state;
}
```

### Interaction between Redux and Firebase via Async Action pattern in the Middleware

The magic that makes the interaction between Firebase and Redux work is the following:

1. In the Redux Middleware, when redux actions come in for adding todo items or toggling todo items or deleting todo
   items, then modify what needs to be modified and save it to firebase -> do NOT dispatch these actions.

2. For Firebase, create a firebase listener that simply takes the snapshot data and creates a redux action (like
   set_state_data) and then applies it to the redux store.

## App startup time

The todo list app has to do a few things before it can be ready for use by the user (after the user has launched the
app). It has to figure out whether its using anonymous auth or signed in auth, and then perform the auth, and then get
the data from Firebase, then update the UI. This can take a few seconds over a slow cellular network. So what might
happen is that the app is launched by the user and it doesn't do anything during this time. Rule of thumb is that if an
app is unresponsive for 3 seconds, users think that it has died. So how can we improve on this?

Redux is a finite state machine. And the entire app's state is represented in a single object. This makes it really
straightforward to persist the entire state object as a JSON string into local storage. In fact, every time any data is
saved to Firebase, it gets dumped into local storage. Here's the code for that (in
[MyDB.java](https://github.com/r3bl-alliance/starterproject_todolist_react_redux_firebase_ts_md/blob/6de82aea9aa38f6dc4f4bd3c7a31887d0093399d/mobile_android_native/app/src/main/java/com/r3bl/todo_app/container/firebase/MyDB.java)):

```java
public static void saveStateToSharedPrefs(App context, State state) {
  SharedPreferences.Editor pref = context.getSharedPreferences(MyDB.class.getSimpleName(),
                                                               Context.MODE_PRIVATE)
                                         .edit();
  pref.putString(Locations.DATA_KEY.name(),
                 state.toString());
  pref.apply();

  App.log("Database.saveStateToSharedPrefs",
          "saving state to SharedPreferences");
}
```

On the flip side, when the Application class
([App.java](https://github.com/r3bl-alliance/starterproject_todolist_react_redux_firebase_ts_md/blob/6de82aea9aa38f6dc4f4bd3c7a31887d0093399d/mobile_android_native/app/src/main/java/com/r3bl/todo_app/container/App.java))
loads, it initializes the Redux store and then loads the Redux state (if there is any) and then applies it to the Redux
store! And voila! The app has restored itself instantly to the previous state that it was left in, the last time it was
run!

```java
@Override
public void onCreate() {
  super.onCreate();
  log("App.onCreate", "[START]");

  _initReduxStore();
  _initFromSharedPrefs();
  _initDatabase();
  _initFirebaseAuth();

  log("App.onCreate", "[END]");
}

//
// Shared Preferences
//
private void _initFromSharedPrefs() {
  State oldState = MyDB.loadStateFromSharedPrefs(this);
  if (oldState != null) {
    getReduxStore().dispatch(new Actions.RestoreState(oldState));
    log("App._initFromSharedPrefs", "loaded saved state from SharedPreferences");
  }
}
```

Here's the code to actually load the data from local storage (in
[MyDB.java](https://github.com/r3bl-alliance/starterproject_todolist_react_redux_firebase_ts_md/blob/6de82aea9aa38f6dc4f4bd3c7a31887d0093399d/mobile_android_native/app/src/main/java/com/r3bl/todo_app/container/firebase/MyDB.java)):

```java
public static State loadStateFromSharedPrefs(App context) {
  SharedPreferences pref = context.getSharedPreferences(MyDB.class.getSimpleName(),
                                                        Context.MODE_PRIVATE);
  String serform = pref.getString(Locations.DATA_KEY.name(), null);
  if (serform == null) return null;
  Gson gson = new GsonBuilder().create();
  State retval = gson.fromJson(serform, State.class);

  App.log("Database.loadStateFromSharedPrefs",
          "loading state from SharedPreferences");

  return retval;
}
```

## Offline mode

The beauty of using Firebase is that offline mode is handled for you out of the box. You have to accommodate the
behavior of Firebase in order for this to work. In Firebase, when you update a JSON object, then the listener is fired
on the node that made this change. The reason for this is to ensure that the Firebase Database can operate in offline
mode. So when you write to the database, it will notify you when this write operation has completed. So you request a
write - you don't force it to happen right now. This is why you have to shift your thinking from the mindset that when
you mutate a data structure in memory, then this change has occurred already (if there were no exceptions). In the
realtime database world of Firebase, we request writes/deletes/changes, and when they happen, we get notified and that
is when we re-act to the data model having been actually modified. This is reflected in this todo list app in the way
async actions are used in the Middleware, and how some actions are handled in the Middleware and others in the Reducer.

So, if you can shift your thinking to this Firebase mindset and adopt Redux Reducers and Middleware, then yes, offline
mode comes for "free".

## Anonymous auth vs signed in experience

A lot of people get authentication wrong. The notion of SignIn, Login, and SignUp being different things is a reflection
of a lack of understanding of signin flow works. I've had the benefit of working on the Google+ team at Google and had a
thorough exposure to the underpinnings of authentication and the UX of authentication. There are 2 critical times in
most mobile apps - when a user is asked to signin and when a user is asked to checkout. These are times of huge
abandonments and uninstalls of an app. So please keep this in mind when designing and building your next mobile app,
whether it's in Android, or iOS, or React Native.

In our todo list app, we have no signed-out state at all! You are either signed in anonymously, or you are signed in
using Google. I'm using Firebase Auth, so you can just keep adding multiple providers (like Facebook, etc). I'm just
sticking with Google to keep things really straightforward on Android.

The Application object (App.java) is where most of this magic is setup to happen. There is a class called
[MyAuth.java](https://github.com/r3bl-alliance/starterproject_todolist_react_redux_firebase_ts_md/blob/6de82aea9aa38f6dc4f4bd3c7a31887d0093399d/mobile_android_native/app/src/main/java/com/r3bl/todo_app/container/firebase/MyAuth.java)
which handles the logic for sign-in (Google and Anonmous) and sign-out. The way Firebase Auth works is that there is a
single method `onAuthStateChanged()` that will determine everything. This keeps things simple. And it makes for a single
point of integration with Firebase Auth. Here's the implementation of that method in MyAuth.java:

```java
/**
 * main firebase auth callback that pretty much takes care of all auth state changes
 */
@Override
public void onAuthStateChanged(@NonNull FirebaseAuth firebaseAuth) {
  FirebaseUser user = firebaseAuth.getCurrentUser();
  App.log("Auth",
          String.format("onAuthStateChanged: %s",
                        user) == null ? "user is null" : "user is NOT null");
  if (user != null) {
    _processUserLogin(user);

  } else {
    // user isn't signed in, so kick off anon auth
    _forceAnonSignIn();
  }
}
```

There is one tricky thing to handle. Since the user is allowed to signin and out at will, and they might be signed into
multiple Google accounts on their phone, this can lead to some interesting situations. The way this todo list app is
designed right now is that any data created in anonymous auth mode will actually be saved when the user signs in (for
the first time). This way, the work isn't lost when they go from anonymous -> signed in. However, to keep things simple,
I don't do a sophisticated merge. I simply detect if the user data exists in Firebase, and if it does NOT then I copy
the anonymous data to the new user account. However, if there's pre-existing data for this user, then I delete the
anonymous data. In the 'real world' you would want to come up with a better data migration policy than this, but this
app is meant to be a teaching tool, and not a full blown production app.

Here's the rest of the code in MyAuth.java:

```java
private void _processUserLogin(@NonNull FirebaseUser firebaseUserObject) {
  if (firebaseUserObject == null) return;

  // new_user is signed in (anon or social)
  User old_user = _ctx.getReduxState().user;
  User new_user = new User(firebaseUserObject);

  boolean performMigration = old_user != null &&
                             old_user.isAnonymous &&
                             !new_user.isAnonymous;

  _ctx.getDatabase().removeUserDataValueListener(); // stop listening to db updates
  _ctx.getDatabase().removeUserInfoValueListener(); // stop listening to db updates

  if (performMigration) {
    // anon -> signedin ... do data migration
    _ctx.getDatabase().performDataMigration(old_user, new_user);
  }

  // process user login
  _ctx.getDatabase().saveUserAndLoadData(new_user);
}

//
// Anon sign in
//

private void _forceAnonSignIn() {
  _auth.signInAnonymously()
       .addOnCompleteListener(
         task -> {
           App.log("Auth", "_forceAnonSignIn: anon auth complete");
           if (!task.isSuccessful()) {
             App.logErr("Auth", String.format(
                    "_forceAnonSignIn: problem with anon auth, %s",
                    task.getException()));
           }
         });
}

//
// Google sign in
//

public void firebaseAuthWithGoogle(GoogleSignInAccount acct,
                                   String googleIdToken,
                                   AuthCredential credential,
                                   MainActivity mainActivity) {
  _auth.signInWithCredential(credential)
       .addOnCompleteListener(mainActivity, new OnCompleteListener<AuthResult>() {
         @Override
         public void onComplete(@NonNull Task<AuthResult> task) {
           App.log("Auth",
                   "firebaseAuthWithGoogle -> signInWithCredential:onComplete:" +
                   task.isSuccessful());
           if (!task.isSuccessful()) {
             App.logErr("Auth", String.format(
                    "firebaseAuthWithGoogle: problem with signin, %s",
                    task.getException()));
           }
         }
       });
}

public void signOut() {
  _auth.signOut();
}
```

## Closing thoughts

You can use the Redux pattern in your native Android apps, and iOS apps as well.

- It's a very powerful way to simplify complex app state changes, and can improve reliability.

- Firebase provides offline mode, and Redux plays nice with it if you use reducers and middleware in the right way.

- It also provides a natural way to interact with any web apps that you have to build on the same backend.
