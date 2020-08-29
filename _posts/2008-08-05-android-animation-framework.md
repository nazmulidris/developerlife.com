---
author: Nazmul Idris
date: 2008-08-05 20:41:26+00:00
excerpt: |
  This tutorial is an introduction to the built in animation frameworks that
  are part of the Android UI library. Without writing any animation/drawing code,
  you can do 2 types of animations - layout transitions that affect ViewGroups, and
  sequences inside a View. You can also do frame by frame animation, but this tutorial
  will not cover that. The basics covered here affect layout transitions, and animation
  of a View itself, using tweening animation, which includes each of the following
  effects (or any combination) - Alpha, Rotate, Scale, and Translate.
layout: post
title: "Android Animation Framework Tutorial"
categories:
- Android
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
    

- [Introduction](#introduction)
- [Tweening and frame-by-frame](#tweening-and-frame-by-frame)
  - [Tweening](#tweening)
  - [One offs - not applicable to all Views, just specific widget classes](#one-offs---not-applicable-to-all-views-just-specific-widget-classes)
- [Creating animation sequences](#creating-animation-sequences)
  - [Defining in XML, and Loading from XML](#defining-in-xml-and-loading-from-xml)
  - [Defining it in Java code](#defining-it-in-java-code)
- [Applying animation sequences](#applying-animation-sequences)
  - [Layout animation](#layout-animation)
    - [Loading layout animation from Java](#loading-layout-animation-from-java)
    - [Loading layout animation from XML](#loading-layout-animation-from-xml)
  - [View animation](#view-animation)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

This tutorial is an introduction to the built in animation frameworks that are part of the Android UI library. Without
writing any animation/drawing code, you can do 2 types of animations - layout transitions that affect ViewGroups, and
sequences inside a View. You can also do frame by frame animation, but this tutorial will not cover that. The basics
covered here affect layout transitions, and animation of a View itself, using tweening animation, which includes each of
the following effects (or any combination) - Alpha, Rotate, Scale, and Translate.

## Tweening and frame-by-frame

You can learn more about the animation framework that comes with Android from the m5 SDK docs
[here](http://code.google.com/android/reference/android/view/animation/package-descr.html). More information on
frame-by-frame animation, not covered in this tutorial, can be found
[here](http://code.google.com/android/reference/android/graphics/drawable/AnimationDrawable.html).

### Tweening

To get started,
[please read this SDK document](http://code.google.com/android/reference/android/view/animation/package-descr.html). It
goes over the details of the default types of animations available, and the basics of how to configure them.

There are 2 types of tweening animations that can be applied to Android apps. They are:

1. layout animation (inter component) – these animations are applied when components are laid out. Eg: when components
   are added or removed from layouts, these animations are triggered. These are different than animations occurring
   inside a component.

2. animation effects on any component/screen (intra component). These animations impact the canvas/drawable area of a
   component itself (not the layout of multiple components). These effects have to be invoked ‘manually’ – unlike layout
   animations, which are triggered when the arrangement/layout of components changes.

### One offs - not applicable to all Views, just specific widget classes

For the [ViewFlipper](http://code.google.com/android/reference/android/widget/ViewFlipper.html) component it’s possible
to define in and out animations:

1. in animation – select an animation effect that’s run when the component is displayed

2. out animation – select an animation effect that’s run when the component is removed/hidden.

## Creating animation sequences

For tweening animations there is a library of built in animations that can be leveraged. And it’s possible to create
your own. In m5 SDK, the pre assembled animations are not well documented, and it’s clear they are still working on this
part of the SDK. However, they do provide access to the classes that are the basis for all their animations (built in):

1. [AlphaAnimation](http://code.google.com/android/reference/android/view/animation/AlphaAnimation.html) - transparency
   changes

2. [RotateAnimation](http://code.google.com/android/reference/android/view/animation/RotateAnimation.html) - rotations

3. [ScaleAnimation](http://code.google.com/android/reference/android/view/animation/ScaleAnimation.html) - growing or
   shrinking

4. [TranslateAnimation](http://code.google.com/android/reference/android/view/animation/TranslateAnimation.html) -
   position changes

These 4 animations
[can be](http://code.google.com/android/samples/ApiDemos/src/com/google/android/samples/view/LayoutAnimation2.html)
composited, nested, and individually configured and applied to any component or group of components, which is very
powerful. In the m5 sdk demos there are some examples of composite animation configurations in
[XML](http://code.google.com/android/samples/ApiDemos/res/anim/).

For all animations, if the animation effects extend beyond the screen region then they are clipped outside those
boundaries… this applies to animations that rotate a screen or scale it for example.

### Defining in XML, and Loading from XML

Just like everything else related to GUIs in Android, it's possible to define animation sequences in XML. Just like
[View inflation from XML](https://developerlife.com/2008/07/16/android-xml-view-inflation/), it's possible to define and
load an animation sequence from XML itself. The following are some example of animation sequences defined in XML.

Here's a fade-in animation (alpha is changed from 0 to 1):

```xml
<?xml version="1.0" encoding="utf-8"?>

<alpha xmlns:android="http://schemas.android.com/apk/res/android"
       android:interpolator="@android:anim/accelerate_interpolator"
       android:fromAlpha="0.0" android:toAlpha="1.0" android:duration="100" />
```

Here's a slide-from-left animation (translate from right to left across the width of the view), named
"/res/anim/slide_right.xml":

```xml
<?xml version="1.0" encoding="utf-8"?>

<set xmlns:android="http://schemas.android.com/apk/res/android"
     android:interpolator="@android:anim/accelerate_interpolator">
    <translate android:fromXDelta="100%p"
               android:toXDelta="0"
               android:duration="150" />
</set>
```

Here's another animation sequence that uses the one above (@anim/slide_right.xml -> "/res/anim/slide_right.xml"):

```xml
<?xml version="1.0" encoding="utf-8"?>

<layoutAnimation xmlns:android="http://schemas.android.com/apk/res/android"
        android:delay="10%"
        android:order="reverse"
        android:animation="@anim/slide_right" />
```

So you can create your sequences in XML and put them in the "/res/anim/some_file.xml" of your Android project resources.
You can get more details on how to create this XML file
[here](http://code.google.com/android/reference/available-resources.html#tweenedanimation).

### Defining it in Java code

Here's an animation sequence that does a layout animation, by sliding a view down from the top:

```java
AnimationSet set = new AnimationSet(true);

Animation animation = new AlphaAnimation(0.0f, 1.0f);
animation.setDuration(100);
set.addAnimation(animation);

animation = new TranslateAnimation(
  Animation.RELATIVE_TO_SELF, 0.0f, Animation.RELATIVE_TO_SELF, 0.0f,
  Animation.RELATIVE_TO_SELF, -1.0f, Animation.RELATIVE_TO_SELF, 0.0f
);
animation.setDuration(500);
set.addAnimation(animation);

LayoutAnimationController controller =
  new LayoutAnimationController(set, 0.25f);
```

Notes on this code:

1. The animation sequence is defined in Java, as an AnimationSet object, to which various
   [Animation subclasses](http://code.google.com/android/reference/android/view/animation/Animation.html) can be added
   (like AlphaAnimation, RotateAnimation, ScaleAnimation, and TranslateAnimation).

2. You have to create a LayoutAnimationController which will actually orchestrate the sequence/AnimationSet that you've
   defined. This controller has to be attached to a ViewGroup in order for this to be run (shown below).

So you can choose to define your animation sequences in XML or define them in Java code. You should do whatever you find
easier.

## Applying animation sequences

Once animation sequences are defined in XML or Java, they can be applied to Views or ViewGroups and run.

### Layout animation

When applying a
[layout animation sequence](http://code.google.com/android/reference/android/view/animation/LayoutAnimationController.html)
to a ViewGroup, you don't have to start or stop the animation sequence. You can't pause it anyway. When you add or
remove a View from your ViewGroup, the animation sequence you have specified will run at that moment. All of this is
automatic. You have to load the animation sequence and then apply it to a ViewGroup.

#### Loading layout animation from Java

Here's an example of how to do this for an animation sequence defined in Java:

```java
public static void setLayoutAnim_slidedownfromtop(ViewGroup panel, Context ctx) {

  AnimationSet set = new AnimationSet(true);

  Animation animation = new AlphaAnimation(0.0f, 1.0f);
  animation.setDuration(100);
  set.addAnimation(animation);

  animation = new TranslateAnimation(
      Animation.RELATIVE_TO_SELF, 0.0f, Animation.RELATIVE_TO_SELF, 0.0f,
      Animation.RELATIVE_TO_SELF, -1.0f, Animation.RELATIVE_TO_SELF, 0.0f
  );
  animation.setDuration(500);
  set.addAnimation(animation);

  LayoutAnimationController controller =
      new LayoutAnimationController(set, 0.25f);
  panel.setLayoutAnimation(controller);

}
```

Notes on this code:

1. The parameters passed to this static method are the ViewGroup that you want to assign this layout animation to, and
   the Activity/Context in which it will be viewed.

2. The animation sequence is defined in Java, as an AnimationSet object, to which various
   [Animation subclasses](http://code.google.com/android/reference/android/view/animation/Animation.html) can be added
   (like AlphaAnimation, RotateAnimation, ScaleAnimation, and TranslateAnimation).

3. The
   [LayoutAnimationController](http://code.google.com/android/reference/android/view/animation/LayoutAnimationController.html)
   is used by the ViewGroup, who's layout is being animated, to determine how your AnimationSet will be orchestrated and
   drawn.

4. Finally, once the layout controller has been created, after the animation set is defined, you have to bind it to a
   ViewGroup that will automatically invoke this animation controller, which will run the set, when the layout is
   changed (Views are added or removed from your ViewGroup or container).

#### Loading layout animation from XML

Here's an example of how to do this for an animation sequence defined in XML:

```java
public static void setLayoutAnimation2(ViewGroup panel, Context ctx) {

  LayoutAnimationController controller =
        AnimationUtils.loadLayoutAnimation(ctx, R.anim.app_enter);

  panel.setLayoutAnimation(controller);

}
```

Notes on this code:

1. The layout animation being used here is defined in R.anim.app_enter (this is default stuff with the m5 SDK).

2. Unlike the Java code, you don't have to create an AnimationSet, that contains Animation subclass objects. Instead,
   you just reference the XML that contains the AnimationSet, etc. by using R.anim.\*.

3. You still have to create the LayoutAnimationController, just like for the Java example above.

4. You still have to bind the layout animation controller to the ViewGroup as in the Java example above.

### View animation

Whether you are doing layout animation for a ViewGroup, or animating just a View, the AnimationSet is the same. You have
to define the animation set in XML or Java code, just like before. The only difference is that there is no
AnimationController. You have to explicitly run or start the animation on the View, in order to see the animation
sequence; it doesn't get automatically triggered as with the ViewGroup layout animation.

Here's an example:

```java
public static Animation runFadeOutAnimationOn(Activity ctx, View target) {
  Animation animation = AnimationUtils.loadAnimation(
          ctx, android.R.anim.fade_out);
  target.startAnimation(animation);
  return animation;
}
```

Notes on the code:

1. This method takes a View and Activity/Context as a parameter. The animation sequence is run on the given View when
   this method is called. The Activity/Context is needed to draw the animations.

2. Just as before, the Animation is loaded from XML (R.anim.fade_out).

3. The View is told to run the animation using startAnimation(...).

You probably have to intercept some event, and then run this animation as a response to that event in your programs.
