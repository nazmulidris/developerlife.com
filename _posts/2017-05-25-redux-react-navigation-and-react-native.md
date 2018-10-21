---
author: Nazmul Idris
date: 2017-05-25 22:26:34+00:00
excerpt: |
  This tutorial is a deep dive in the use of Redux in React Native projects.
  It will show you how to architect apps that rely on external web services,
  and Firebase. The code for this tutorial is on GitHub.
layout: post
title: "Redux, React Navigation, and React Native"
hero-image: assets/redux-hero.png
categories:
- DB
- UXE
- RN
- State
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [Source code on GitHub](#source-code-on-github)
- [MVVP vs Unidirectional architectures](#mvvp-vs-unidirectional-architectures)
- [Flow](#flow)
- [Material Design Components](#material-design-components)
- [Migrating the weather app to using Redux](#migrating-the-weather-app-to-using-redux)
- [Redux](#redux)
  - [1. State](#1-state)
  - [2. Actions](#2-actions)
  - [3. Reducer functions](#3-reducer-functions)
    - [Deep copy or shallow copy to generate the new state?](#deep-copy-or-shallow-copy-to-generate-the-new-state)
  - [4. Middleware functions](#4-middleware-functions)
  - [5. Store creation](#5-store-creation)
  - [6. Connect](#6-connect)
  - [Here's some more information on Redux](#heres-some-more-information-on-redux)
- [Weather App Architecture](#weather-app-architecture)
- [React Navigation and Redux](#react-navigation-and-redux)
- [React Native resources](#react-native-resources)
- [React, Redux, and native Android resources](#react-redux-and-native-android-resources)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

This tutorial is all about thinking in Redux when building mobile apps. In addition to showcasing an architecture for a simple weather app, I will provide clean examples for middleware and reducers and delve into `@connect` and the `connect` function. I will also show you how to set it up for integration into Firebase realtime database, and show you how to use Flow static type checking in your apps.

There will be many more tutorials on the evolution of this weather app into using Firebase Database, Firebase Auth, precise location lookup, and notifications. My goal for creating this project is to provide really clean and simple (while remaining real-world) reference code and architecture that can be used to build most contemporary mobile apps.

## Source code on GitHub

Here's the [source code on GitHub](https://github.com/r3bl-alliance/react-native-weather/tree/5d51b3c622136bcf0e5e4999cd96112b9d55c77b) with react-navigation NOT wired into Redux. This is primarily what this tutorial will cover. I chose not to wire react-navigation into Redux (even though it supports it). So navigation state is not stored in Redux in this tutorial and this version of the source. At the end of this tutorial, you will find information on a branch of this codebase where I did integrate `react-navigation` with Redux in case you're interested in that.

## MVVP vs Unidirectional architectures

Before we get started with the code, let's consider the high level patterns that Redux embodies for data flow and how they are different than [MVVM](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93viewmodel) or MVP approaches. [This article](http://www.michaelridland.com/xamarin/mvvm-mvc-is-dead-is-unidirectional-a-mvvm-mvc-killer/) does a great job highlighting the differences between these approaches. Google just released [Android Architecture Components](https://developer.android.com/topic/libraries/architecture/index.html) (at Google IO17) which is a MVVM framework for native Android development.

In this tutorial and the example weather app, I use Redux which is a unidirectional framework. Both approaches (MVVM and unidirectional) require boilerplate code, and a lot of forethought before starting coding up a project. I might explore MVVM and Android Architecture Components in a different tutorial. If you want to see unidirectional Redux applied to native Android development, [check out this tutorial](https://developerlife.com/2017/01/27/native-android-redux-and-firebase/).

## Flow

Type safety is a good thing. And Flow is a really seamless way of integrating type safety into your React Native application. In fact, it's enabled by default. All the flow code that you add actually gets stripped out when the JS is executed, which is awesome. To learn more about Flow, here are some resources:

  * [Flow documentation](https://flow.org/en/docs/types/primitives/).
  * [Tutorial on using Flow and Redux](https://blog.callstack.io/typed-redux-2aa8bff926ff).
  * [Try it!](https://flow.org/try/#0PTAEAEDMBsHsHcBQjgCpGgLawE4FNQBLAO0llFmNBgQwFpQALAF2YAcBnALhBvgDpcAc2B5iwACawAxh2DMAnmzxyAhjhyqFc+k1acewPoJwixkmXMXK10Qqo4rgulu2684A4aPFTZ8pScSZjwcSFVpJwwMEI5mUGZGAmlYCQIk-Bd9dyNPExFmHAVnUAwOVUw2aGTUgkTVeIBJUHgcWBCst0MhWFh+IWhgAGZ4AE0ANUgkUFRnFGcQBMCOeeQ8AA82XHjrAgBlZgaCAF5QAG8MUABXRxwuUABVW4AaS7hpBsJKblAAGRlPpQAOoNaSMX6EOKvUCgfBbHDMH5AvANDIAJTw8MRrwAvmtNtslspHrdQKcLjDIQBBYiUe4AI161VUxGhoGIFTw9ziOBIQjZN1ChAk3MKfLZbDakEI1QACoRpMwrvgHjhoKLecR+Yg8YgNliiQR-h9mF9iCDmGCIXEyaAqRotAAeHl8gB8AG58QbdqBkajQhisRxbfbNApHX7EgHMdsPV7CT7I+iYwjbRTQO9AcQNeLLtJlfhiMx7gBhAtiZglygSQim75ssj4D5xe7IvAAa2gCgAYrg8M3mLj46mfWWNBWq8Qa3XiMHyZcQpV7sQrph6aE2YxV8Lawpl6v1zg2fASCL2QeN5crgA3U8bfdry8wjhXYi8xwPw9sl+zvDF8+PkeOrDjsgS+ngHZdr2TYOPE84whIWg-KGToACKqDKPZ9gOrpDnqBIjmB6GYdB-awWmlyIXuoAulqm6EJ+T4ZrAjFAbqIDzBQ9IAFb9oiqyINU8SYAoTyhPcYk4BRlIcDSdIJDgVx4GyHKYFyoAAOQcgAXhpAq3MK9waQAjAATEMemXJKsDSnKCpKiqapGa4bCGIysCWTinqCX+WAKMaWY-AFM4WlakJwaAADaJmmXpmnGRZzzxQALBpAC63lCX5gbbEiKJRjgOUInOlyRZcMLpjCMKZjORlmZZVVVfm45FvclWNQkeBLqAZlsh1TDbtO1EABwAAx9R1J5TvcQwTY1N53us9wAKxzVVP7vupvXlR1P6OP+xnDWtOJrY2ZEtucO2NVRPxlf1jXtfdoBUUZ2DEA1T1VYwDGgAA7ONV33XA9wAGwA59oB4k9aXHTtJ2XBlQA).

In this weather app, I use Flow to type the State objects that are managed by Redux, and in the middleware, reducers, and actions as well. It makes it easy for me to keep track of object shapes in my code. I defined all the types that I would need in one file - [Types.js](https://github.com/r3bl-alliance/react-native-weather/blob/91da767ef1a0964c416cf1cf61f2cb81216a348d/app/Types.js). I then import this into whatever JS file I need and use these types, using `import type * as Types from './Types';`. This keeps all the Flow types neatly in one place, while allowing me to use them or not wherever I chose. I've used [TypeScript before in another tutorial and web app on GitHub](https://developerlife.com/2016/10/07/getting-started-with-react-redux-and-firebase/), and I prefer Flow over it.

Here's an example of a reducer that uses Flow types:

```javascript
export const appReducer = (state: Types.AppState = INIT_STATE,
                           action: Types.Action,
): Types.AppState => {
  switch (action.type) {
    case actions.TYPES.set_watchlist: {
      return setWatchlist(state, action.payload);
    }
    case actions.TYPES.set_weather_data: {
      return setWeatherData(state, action.payload);
    }
    case actions.TYPES.set_user_object: {
      return setUserObject(state, action.payload);
    }
  }
  // in case nothing matched, just return the old state
  return state;
};
```

Here's the `setUserObject` method implementation:

```javascript
function setUserObject(state: Types.AppState, user: User) {
  ToastAndroid.show("USER OBJECT SET", ToastAndroid.SHORT);
  return {
    ...state, // syntax : http://es6-features.org/#SpreadOperator
    user, // syntax : http://es6-features.org/#PropertyShorthand
  };
}
```

Here's an example of some of the types defined in `Types.js`:

```javascript
export type Action = {
  type: number,
  payload: any,
}
 
export type State = {
  app: AppState,
}
 
export type AppState = {
  user: User,
  locations: LocationWatchList,
  reports: WeatherReports,
}
 
export type User = {
  isAnon: boolean,
  name: string,
  userid: string,
  profilePictureUrl: string,
}
 
export type LocationWatchList = Array<string>;
 
export type WeatherReports = Array<WeatherReport>;
 
export type WeatherReport = {
  location: string,
  current: CurrentConditions,
  forecast: WeeklyForecast,
}
 
export type CurrentConditions = {
  temp: number,
  humidity: number,
  wind: number,
  uvindex: number,
  sunrise: number,
  sunset: number,
}
 
export type WeeklyForecast = {
  days: Array<DailyForecast>,
}
 
export type DailyForecast = {
  day: string,
  hi: number,
  lo: number,
}
```

## Material Design Components

At Google IO17, Google released the new [Material Components project](https://material.io/components/). This just brings to life the Material Design spec in code libraries that you can use in your Web (Javascript), Android (Java, Kotlin), or iOS (Swift, ObjC) apps.

I went looking for a React Native equivalent for these components and I found this [react-native-material-design](https://github.com/xotahal/react-native-material-ui) library. It works with the vector fonts library that this weather app is already using. The only caveat is that it's currently (as of May 2017) not possible to use font icons other than `materialicons` in react-native-material-ui library.

To accommodate this library, I had to make a few changes to the weather app:

  1. Importing the library from npm was easy since the vector icons project was already added.

  2. I had to wrap the root view that contains a material component in a `ThemeProvder` wrapper, 
  which allows `UITheme` to be passed to it (in order to consistently theme all the material components in the hierarchy). 

  3. Adding the floating action button (`ActionButton`) was easy, but it took some time to figure out how the styling works for this library and how to integrate that into react native styles (which I store in [Styles.js](https://github.com/r3bl-alliance/react-native-weather/blob/5d51b3c622136bcf0e5e4999cd96112b9d55c77b/app/Styles.js)) and deal with the material-ui theme object(s). 

Here's the code to add the [`ActionButton`](https://github.com/xotahal/react-native-material-ui/blob/master/docs/ActionButton.md) in `HomeScreen.js`:

```html
return (
  <ThemeProvider uiTheme={uiTheme}>
    <View style={css.home_screen.v_container}>
      <StatusBar
        hidden={false}
        translucent={false}
        animated={true}
        barStyle={'light-content'}
        backgroundColor={css.colors.secondary}
      />
 
      <FlatList
        style={css.home_screen_list.container}
        data={listData}
        renderItem={this.renderRow}
      />
 
      <ActionButton style={css.fab.stylesheet} icon={css.fab.icon}
                    onPress={this.actionButtonPressed}/>
 
    </View>
  </ThemeProvider>
```

Here's the `fab` style from `Styles.js`:

```javascript
export const fab = {
  // key - value pairs needed to decorate the FAB
  icon      : 'library-add', // As of May 16 '17 only MaterialIcons 
                             // can be used in material-uilib
  // StyleSheet needed to style the FAB
  stylesheet: StyleSheet.create(
    {
      container: {
        //COLORS can be used here as well
        backgroundColor: colors.secondary, 
      },
    },
  ),
};
```

Finally, here's the `uiTheme` object (which doesn't really do anything in this form):

```javascript
const uiTheme = {
  palette: {
    primaryColor: COLOR.green500,
  },
};
```

## Migrating the weather app to using Redux

This weather app started life off without having any Redux code in it ([see this tutorial](https://developerlife.com/2017/04/26/flexbox-layouts-and-lists-with-react-native/)). There was a strange issue I ran into related to JSX while I was wiring Redux into this existing codebase.

In order to move the existing code over to Redux, I couldn’t just pass a `Drawer Navigator` to the `AppRegistry` as I was doing in the past. This navigator now needs to be wrapped with a `Provider`. When I went to create a simple `React.Component` class that just returns this navigator, I ran into trouble because I named the variable for the `Drawer Navigator "nav_drawer"` and this does not play nice with JSX! JSX thought it was an HTML element and didn’t know what to do with it. When I renamed it to _U_ppercase `NavDrawer`, it worked as expected. More info [here](https://goo.gl/nGRaAl).

## Redux

With that out of the way, let's talk about the main thing in this tutorial - which is Redux. Redux is a way to create a finite state machine that captures the state of your entire application. This finite state machine's state can be changed when actions are dispatched against it. Each state transition results in an immutable state. So an entirely new state object is created every time an action is successfully dispatched, and it transitions the state to a new one.

Subscribers can attach to the Redux store. These subscribers are invoked whenever the Redux state changes. You can query the Redux store for the state at anytime. There's a `react-redux` library which provides some helper functions to make this efficient. There's a `connect` function that wires up part of a state tree to React Components that are interested in observing it. These React Components are re-rendered only if there are actual changes in parts of the state tree, so re-renders are efficient.

You can choose to wire react-navigation into this state or not. There's a branch on GitHub (link is shared at the top of the tutorial) which covers how you can wire react-navigation into Redux if you like.

The key elements of using Redux are the following:

### 1. State

Hold your entire app's state in a single object. The shape of this object matters, since you can slice the object based on key names, and then tie them to reducer functions which only operate on that slice of the state tree. You can also connect (or bind) slices of the state tree to React Components that will be re-rendered when anything in these state slices change. This is the main promise of Redux - to make state management robust and manageable, and testable.

### 2. Actions

You have to create action functions that contain a name and a payload. These actions are declarative. They don't actually do anything. Instead they describe what you would like to happen to the Redux state, once these actions are dispatched to the Redux store. Think of actions as requests that you are making against the Redux store. Just because you make a request doesn't mean that it will be fulfilled. If it does get fulfilled, then the state will change and your React Component(s) will be re-rendered if necessary.

```javascript
export const TYPES = {
  request_refresh_weather_data: 0,
  request_add_to_watchlist    : 1,
  set_watchlist               : 2,
  set_weather_data            : 3,
  set_user_object             : 4,
};
...
export function set_weather_data_action(
    weatherreports: WeatherReports): Types.Action {
  return {
    type   : TYPES.set_weather_data,
    payload: weatherreports,
  };
}
 
export function set_user_object_action(user: User): Types.Action {
  let retval = {};
  if (_.isNil(user)) {
    retval = {
      type   : TYPES.set_user_object,
      payload: {
        isAnon           : false,
        name             : Math.random().toString(36).substring(7),
        userid           : Math.random().toString(36).substring(7),
        profilePictureUrl: Math.random().toString(36).substring(7),
      },
    };
  }
  else {
    retval = {
      type   : TYPES.set_user_object,
      payload: user,
    };
  }
  return retval;
}
...
```

### 3. Reducer functions

You have to create reducer functions that take the old state object, and an action, and then run some code to change the state to a new state. These functions are pure, and you can't call web services in them. If you need to do anything asynchronously in these reducers, then you have to use middleware (shown next). To make things more manageable, you can create reducer functions that operate on small parts of the state. Let's say that you have a State object that has the following shape:

```javascript
const state = {
  app: {key:'value'},
  nav: {},
  net: {},
};
```

You can now create 3 reducers, one that operates on the `app` leaf of the state, another that works on the `nav` leaf, and yet another that operates on the `net` leaf. Redux provides a simple way to combine these reducers and associate a reducer function with the key that it's supposed to work with.

```javascript
combineReducers({
                  app: appReducer,
                  nav: navReducer,
                  net: netReducer,
                },
),
```

Here's what appReducer might look like:

```javascript
export const appReducer = (state: Types.AppState = INIT_STATE,
                           action: Types.Action,
): Types.AppState => {
  switch (action.type) {
    case actions.TYPES.set_watchlist: {
      return setWatchlist(state, action.payload);
    }
    case actions.TYPES.set_weather_data: {
      return setWeatherData(state, action.payload);
    }
    case actions.TYPES.set_user_object: {
      return setUserObject(state, action.payload);
    }
  }
  // in case nothing matched, just return the old state
  return state;
};
...
function setUserObject(state: Types.AppState, user: User) {
  ToastAndroid.show("USER OBJECT SET", ToastAndroid.SHORT);
  return {
    ...state, // syntax : http://es6-features.org/#SpreadOperator
    user, // syntax : http://es6-features.org/#PropertyShorthand
  };
...
```

#### Deep copy or shallow copy to generate the new state?

There is something that you have to keep in mind when returning the new state. If you zoom out and consider where this state is going, this will give you some insight into how all this fits together. When an action is dispatched, and this generates a new state object, this object will then be passed to some React Component using the `connect` function and it will probably update some UI, e.g. a `FlatList`. If the thing that's being updated (which will need to be re-rendered) does a shallow equality test of it's existing state and the new state, then this has an impact on how we generate this new state.

Let's use a real example. In the code above there's an action called `set_weather_data`. This is an action that takes data (which is probably from a RESTful endpoint containing the latest version of some data) and applies it to the new state. There will be some UI code that renders this data into a [`FlatList`](https://facebook.github.io/react-native/docs/flatlist.html). This `FlatList` is a `PureComponent` and it does a shallow equality test in order to determine if it should re-render itself, when it gets new data. In this case, when we `connect` our Redux store to a `FlatList`, we have to make sure that when we generate the new state that it will be **DIFFERENT** when we do a **shallow-equality-test**.

What this means is that if we use the following code in the reducer function, then the `FlatList` will NOT update even when we dispatch this action and add new data to the state:

```javascript
function setWeatherData(state: Types.AppState, reports: WeatherReports) {
  ToastAndroid.show("REDUCER: SET WEATHER DATA", ToastAndroid.SHORT);
  return {
    ...state,
    reports, // shallow-equality-test will not detect this change!
  };
}
```

In order for the `FlatList` to actually update, we have to do a deep copy of a portion of the old state in order to let it know that the underlying state data has changed, and it should re-render itself.

Here's what that code would look like:

```javascript
function setWeatherData(state: Types.AppState, reports: WeatherReports) {
  ToastAndroid.show("REDUCER: SET WEATHER DATA", ToastAndroid.SHORT);
  return {
    ...state,
    reports: _.cloneDeep(reports), // shallow-equality-test 
                                   // will detect this change!
  };
}
```

Here's more information on this:

  * Here's code that illustrates this for this weather app: [Reducers.js](https://github.com/r3bl-alliance/react-native-weather/blob/dc1f5ea02af4125c443d60da44e5aaa6b4802e97/app/state/Reducers.js) and [HomeScreen](https://github.com/r3bl-alliance/react-native-weather/blob/dc1f5ea02af4125c443d60da44e5aaa6b4802e97/app/HomeScreen.js).
  * [lodash deep copy](https://lodash.com/docs/4.17.4#cloneDeep).
  * [PureComponent and shallow equality test](https://stackoverflow.com/questions/43397803/how-to-re-render-flatlist/43398395).

### 4. Middleware functions

You have to create middleware functions of you want to do asynchronous things, such as make a webservice call, or change something in Firebase, that will cause a Firebase listener to wake up and then dispatch an action against the Redux store. For Firebase, this is a very simple and effective way to integrate with Firebase Database and even Firebase Functions. I won't delve very deeply into middleware functions in this tutorial, but I will cover this very deeply in a future tutorial where I connect this weather app to a backend (that gets live weather data from a weather data provider). This is what middleware functions look like:

```javascript
export const mainMiddleware = function (store) {
  return function (next) {
    return function (action: Types.Action) {
      if (action.type === actions.TYPES.request_refresh_weather_data) {
        requestRefreshWeatherData(action.payload);
      }
      else if (action.type === actions.TYPES.request_add_to_watchlist) {
        requestAddToWatchlist(action.payload);
      }
      else {
        // must return this in order to invoke reducer functions
        return next(action); 
      }
 
    };
  };
};
```

Note that you have to `return next(action);` in order for the reducer to continue executing any other middleware functions you might have, and also, any other reducer functions you might have. If you fail to do this, then the method chaining will be aborted. This is exactly what we are doing when we match an action type in the if statements. Chaining is a really effective way to broadcast this action to be handled by any number of middleware and reducer functions. It is entirely possible for you to have multiple reducer functions respond to the same action type (if you have `return next(action);` at the end of the if statements above for example). You can also have actions processed by multiple middleware and reducer functions.

### 5. Store creation

In order to setup Redux for your app, the first thing that has to happen is the store must be created and initialized with the initial state, and the middleware and reducer functions that you want to use. In addition to this, in order to pass this Redux store to all your React Components, you have to use a `Provider` object that you pass to the root of your React Component view hierarchy.

The store is actually [stuffed in the React Context](http://javascript.tutorialhorizon.com/2016/07/07/passing-the-store-down-implicitly-via-context-in-a-react-redux-app/) by `react-redux` when you use the `Provider`. It's an implementation detail that isn't too important for you to be aware of, but it's a great example of using [React's Context mechanism](https://facebook.github.io/react/docs/context.html).

The Redux store that you create will be a very important object, since:

  * all actions will have to be dispatched against this store, 

  * subscribers attached to this store, and 

  * you will retrieve the current state from this store object.

Here's an example of creating a store:

```javascript
export const store = createStore(
  combineReducers({
                    app: appReducer,
                  },
  ),
  applyMiddleware(mainMiddleware),
);
```

### 6. Connect

The `connect` function (from `react-redux`), or it's annotation/decorator form `@connect` is a really important function for you to grok. When state changes occur, due to actions being dispatched against the Redux store, this will have to be reflected in your React Components. `connect` is the thing that makes this happen for you, and there are 2 ways in which you can use this: as a decorator, or as a function. I prefer using the decorator/annotation form over the function call, it's terse and really easy to use. Here's an example:

```javascript
@connect(
  (state) => {
    return {app: state.app};
  },
)
export class HomeScreen extends Component {
...
```

In this example, `@connect` simply wraps the HomeScreen component with a call to the `connect()` function. This in turn maps a leaf of the state tree (`app`) to cause `render()` calls on HomeScreen whenever anything in the `state.app` object changes. It's incredibly powerful and terse. And if you think about shaping your state object and binding it to reducers, then this will make sense as well. You're doing something similar with the shape of the state object and binding or connecting it to a React Component unidirectionally. Now, changes to the Redux store that are made by dispatching actions against it will cause re-renders in this connected React component, and it will be done in an efficient way for you!

The 2nd parameter for `@connect` is something called `mapDispatchToProps`, and this is something that I'm not really using in this example. But the idea here is that if you want your UI components to make changes in Redux state, they will have to dispatch actions to the store. This is a function where you can take actions and then automatically bind them to the dispatch. The following example of the expanded `connect()` function will show you this in action:

```javascript
  // NOTE - if you don't use @connect ...
  /*
   * mapStateToProps & mapDispatchToProps more info:
   * - http://tinyurl.com/y8scrq5y
   * - https://goo.gl/VNQAOZ
   */
  const mapStateToProps = (state) => {
    return {app: state.app};
  };
 
  const mapDispatchToProps = (dispatch) => {
    return bindActionCreators(actions, dispatch);
  };
 
  // exports HomeScreen as the connected component
  // more info - http://redux.js.org/docs/basics/UsageWithReact.html
  export const ConnectedHomeScreen =
                 connect(mapStateToProps, mapDispatchToProps)
                 (HomeScreen);
```

Again, in this weather app example, I'm not going to be using `mapDispatchToProps` or `bindActionCreators`, since I will have actions in the UI run code that does this manually by creating an action with the needed parameters, and then dispatching them directly against the Redux store.

### Here's some more information on Redux

  * [Redux Optimization](https://reactrocket.com/post/react-redux-optimization/).
  * [Redux documentation](http://redux.js.org/docs/api/createStore.html).
  * [Tutorial on react-redux and @connect](http://www.sohamkamani.com/blog/2017/03/31/react-redux-connect-explained/).
  * [Tutorial on how to enable es2016 decorators in react-native projects](http://moduscreate.com/using-es2016-decorators-in-react-native/).
  * [Tutorial on using Flow and Redux](https://blog.callstack.io/typed-redux-2aa8bff926ff).

## Weather App Architecture

The following diagram represents how the weather app will be constructed with the use of Redux.

![]({{ 'assets/redux-nav-1.png' | relative_url }})

Here are some important things to note:

1. All the actions have been mapped out in advance that represent things that either the user can perform, or things that the app will do (outside of any user interaction). It's really important to map these out at the start, even thought they might change as you start building and iterating on the design and implementation of your app. It will give you a clear roadmap of all the UI things that have to be built as well as the backend things. I've separated the actions into 2 chunks: `REQUEST`* and `SET`*.

    * All the actions starting with `REQUEST` are handled by middleware functions. These are all async things that will result in Firebase getting poked (or some kind of REST endpoint getting poked). I will build out the backend of this app in a future tutorial (to use Node.JS and Firebase Functions, just to show 2 different ways of doing this). These async actions end up causing some data to be changed in Firebase. Which then results in a Firebase listener being run in the app, which then creates a Redux action with some data (from Firebase) and then dispatches it to the Redux store. 

    * All the actions starting with `SET` are handled by reducer functions. These are pure functions that don't make any web service calls or deal with Firebase. They are only concerned with changing the portion of the state that they are passed (since I'm using `combineReducers`).

## React Navigation and Redux

Here's the [source code on GitHub](https://github.com/r3bl-alliance/react-native-weather/tree/55b5ab0ae15a5d0682c340924d2758342e4c5c72) with react-navigation wired into Redux. This branch is an exploration to see how react-navigation can be integrated with Redux (and isn't covered in detail in this tutorial).

The Redux state has 4 high level objects in it: `app`, `nav_tab`, `nav_stack`, and `nav_drawer`. The biggest differences between these 2 source code version are 2 files: [Router.js](https://github.com/r3bl-alliance/react-native-weather/blob/55b5ab0ae15a5d0682c340924d2758342e4c5c72/app/navigation/Router.js) and [Context.js](https://github.com/r3bl-alliance/react-native-weather/blob/55b5ab0ae15a5d0682c340924d2758342e4c5c72/app/state/Context.js). The biggest changes between these 2 versions are:

  1. Android back button has to be handled manually now (this is expected behavior documented in the [react-navigation docs](https://reactnavigation.org/docs/guides/redux)).

  2. Route params are not being passed to screens nested underneath navigators (e.g.: navigate to `DetailsRoute` with params `{…items}` results in ending up on the correct destination screen BUT the params are lost! I’m sure this can be addressed by connecting the `DetailsScreen1` and `DetailsScreen2` to redux and have them observe the state.

## React Native resources

  * This is a [good resource](http://reactnative.cc/) that you can follow for keeping up to date with changes in React Native.
  * This a [great facebook community](https://www.facebook.com/groups/react.native.community/?hc_ref=NEWSFEED) on React Native.

## React, Redux, and native Android resources

  * How to integrate Redux into native Android development. I have tutorials [on native Android and Redux here](https://developerlife.com/2017/01/27/native-android-redux-and-firebase/).