---
author: Nazmul Idris
date: 2007-09-24 19:31:10+00:00
excerpt: |
  I needed to perform animations in the app that I'm building for ScreamingToaster
  desktop app framework using Java and Swing. I needed to build animations that show 
  a transition from one screen to another.
  This is slightly different than creating custom, or modified components which perform
  a function and have a set of graphical effects. I needed animations that would transition
  my user interface from one "screen" to the next. The screens themselves could be
  panels or components (part of the whole app, or the entire app itself). While I'd
  been writing much of this code myself, to do these animations, it just got really
  tedious and frustrating to add this level of complexity to my code, when all I needed
  were some simple animations. I've been using the SwingX API and the TimingFramework
  API to perform the animations and leverage the components, however, this last piece
  was missing. And this last piece just got delivered by Chet Haase, as a part of
  the binary deliverables with his (and Romain Guy's) great book - Filthy Rich Clients.
layout: post
title: "How to use the AnimatedTransition API (SwingX and Timingframework)"
categories:
- UXE
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [Background information](#background-information)
- [Getting started](#getting-started)
- [Implementation details](#implementation-details)
  - [Example #1 : hiding a component](#example-1--hiding-a-component)
  - [Example #2 : swapping layouts on a component](#example-2--swapping-layouts-on-a-component)
- [Summary](#summary)
- [Related links](#related-links)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

I needed to perform animations in the desktop app framework (using Java and Swing) that I'm 
building for ScreamingToaster. I needed
 to build animations that show a transition from one screen to another. This is slightly different than creating custom, or modified components which perform a function and have a set of graphical effects. I needed animations that would transition my user interface from one "screen" to the next. The screens themselves could be panels or components (part of the whole app, or the entire app itself). While I'd been writing much of this code myself, to do these animations, it just got really tedious and frustrating to add this level of complexity to my code, when all I needed were some simple animations. I've been using the [SwingX API](http://swinglabs.org) and the [TimingFramework API](https://timingframework.dev.java.net/) to perform the animations and leverage the components, however, this last piece was missing. And this last piece just got delivered by [Chet Haase](http://weblogs.java.net/blog/chet/), as a part of the binary deliverables with his (and Romain Guy's) great book - [Filthy Rich Clients](http://www.amazon.com/gp/product/0132413930?ie=UTF8&tag=developerlife-20&link_code=as3&camp=211189&creative=373489&creativeASIN=0132413930).

At a high level, there are a few things to keep in mind. If you are looking for animations that move things around on an existing screen, eg, when you switch from one screen to another, in a wizard, or when you change the layout of a panel from 3 columns wide to 2 columns wide, or if you want to animate a component showing up and then going away, these are the kinds of things that the AnimatedTransitions API is really good at doing. If you want to do custom animations for popups or a custom component that does interesting stuff in the paint() method, then this API may not be what you are looking for.

Before we get started on the API and how to use it, one last thing to keep in mind is that the Animated Transitions API can be applied to the entire app, or just a part of the app (eg, a panel that's one of many panels in the app). Additionally, the Animated Transitions API works very well with LayoutManagers! If you've used the TimingFramework before and have created property setters which change the size or location of a component, only to have the layout manager yank it back, you know how frustrating it can be to deal with issues like that.

For a more detailed description of the API, [buy the Filthy Rich Clients book](http://www.amazon.com/gp/product/0132413930?ie=UTF8&tag=developerlife-20&link_code=as3&camp=211189&creative=373489&creativeASIN=0132413930), or read more about it on java.net. If you want to start using the API right away and want to see some code examples, read on.

## Background information

For more information on AnimatedTransitions API, refer to these links:

  1. Download the [API here](http://download.java.net/javadesktop/filthyrichclients/AnimatedTransitions.jar).

  2. Download the [Javadocs for the API here](http://download.java.net/javadesktop/filthyrichclients/AnimTransJavadoc.zip).

  3. Get the source code [here](http://animatedtransitions.dev.java.net/).

For more information on SwingX, refer to these links:

  1. SwingLabs – [SwingX toolkit](http://swinglabs.org/)

  2. Download SwingX here – [Hudson Weekly Builds](http://swinglabs.org/hudson/job/SwingX%20Weekly%20Build/)

I'm planning on writing more tutorials on SwingX and how to use painters… check back in a few days/weeks and I should have them uploaded on the site.

For more information on the Timingframework for animation, refer to these lniks:

  1. Timingframework tutorial – [Timing is Everything](http://today.java.net/pub/a/today/2005/02/15/timing.html)

  2. Timingframework homepage – [timingframework.java.net](https://timingframework.dev.java.net/)

  3. Timingframework downloads – [java.net downloads](https://timingframework.dev.java.net/servlets/ProjectDocumentList?folderID=7194&expandFolder=7194&folderID=0)

## Getting started

In order to use the AnimatedTransitions API in the simplest way you have to do two things:

  1. Identify a JComponent (can be a container with a layout manager) that is going to transition from one state to another.

  2. Clearly define these 2 states: the start state and the end state.

  3. Implement a callback from the AnimatedTransitions API to your code that sets up the end state. (The start state is assumed to be whatever state you are in before the animated transition is started).

  4. Define the duration of the transition animation, in ms.

  5. Make sure to use the AnimatedTransitions API to initiate the state change, and don't just make the changes to the UI yourself, bypassing the API :) .

There are more complex ways of using the API. You can define more than just a duration in ms for the length of the animation. You can provide your own Animator object (this will allow you to do non-linear interpolation of the animation itself), this is covered in the examples in this tutorial.

You can also use change the default Effects that are used in the API. These Effect classes control what animations are performed: FadeIn, FadeOut, Scale, etc. There are lots of predefined ones that are pre-configured out of the box, so to speak. You can create your own effects by compositing these exisitng Effect objects, and of course create your own, from scratch or by extending one of the Effects that are provided. Please read the book ([Filthy Rich Clients](http://filthyrichclients.org/)) for more information on Effects.

The thing to keep in mind when using this API is the following: make sure that you know what component is going to be animated from a start (current) state to it's end state. Then register a callback with the API to set up this "end state". If you get this out of sync, then you won't see the desired effect.

## Implementation details

You have to implement 3 things:

  1. Create the ScreenTransiton object. This is the controller that you bind the component you want animated with, along with the duration (or an Animator object), and the callback. Make sure to bind the correct component to this ScreenTransition object - if you don't see any animations, chances are that you've bound the wrong component to the API.

  2. The callback (TransitionTarget) in your code. The method setupNextScreen() is called by the API when the ScreenTransition is started. Also, if you are using components that are acutally containers with layout managers, there is no need to call revalidate() and repaint() at the end of the implementation of this method (the API will take care of this for you).

  3. Be sure to use the ScreenTransition object in your code to start() the transition, so that it can animate it.

You can use a UI builder like JFormDesigner to create the desired layouts for your components. However, when you perform the transition from one state to the next, and this impacts the layout of your components drastically, then this will require some hand coding in the setupNextScreen() implementation in your code. Not to worry, chances are that you can copy/paste most of the layout code from your favorite UI builder. Also, there is nothing stopping you from transitioning between any number of states, as long as your code knows how to multiplex these state changes, the API will run them for you.

The IntelliJ IDEA project and JFormDesigner project, along with all the source code and required 
libraries are available [here - animatedtransitions.zip]({{'assets/animatedtransitions.zip' | 
relative_url}}).

### Example #1 : hiding a component

In this example (SamplePanel.java in hidepaneltest package), I have two components in a panel, which has a layout manager. I want to hide/show one of these components, and I want an animation to occur to transition this hide/show operation graphically.

Here is some sample code to create the ScreenTransition component:

```java
public SamplePanel() {
   initComponents();
   // — create the animator object (set delay and interpolator) 
   Animator anim = new Animator(200);
   // http//javadesktop.org/swinglabs/demos/timingframework/SplineEditor.jnlp 
   anim.setInterpolator(new SplineInterpolator(
           0.97f, 0.03f,
           1.0f, 0.00f));

   // — setup the screen transition object, with TransitionTarget & Animator 
   st = new ScreenTransition(
           tablePanel,
           this,
           anim
   );

}
```
Here is some sample code to implement the callback (TransitionTarget):

```java
public void setupNextScreen() {
   // — show left column
   if (leftPanelIsHidden) {
       tablePanel.removeAll();
       tablePanel.add(
               leftLabel,
               new TableLayoutConstraints(0, 0, 0, 0,
               TableLayoutConstraints.FULL, TableLayoutConstraints.FULL));
       tablePanel.add(
               rightLabel,
               new TableLayoutConstraints(1, 0, 1, 0,
               TableLayoutConstraints.FULL, TableLayoutConstraints.FULL));
       //tablePanel.revalidate();
       //tablePanel.repaint();
       leftPanelIsHidden = false;
   }

   // — hide left column
   else {
       tablePanel.removeAll();
       tablePanel.add(
               rightLabel,
               new TableLayoutConstraints(0, 0, 1, 0,
               TableLayoutConstraints.FULL, TableLayoutConstraints.FULL)
       );

       //tablePanel.revalidate();
       //tablePanel.repaint();
       leftPanelIsHidden = true;
   }
}
```

Here is some code to kick off the transition, when the user presses a button:

```java
private void toggleAction() {
   st.start();
}
```

### Example #2 : swapping layouts on a component

In this example (SamplePanel.java in switchlayouts package), I have three components in a panel, which has a layout manager. I want to change the layout when the user presses a button, from 3 columns wide, to 2 columsn wide. I want an animation to move the new components to the desired locations and I want these locations determined by the layout manager. So I'm actually going to change the layout manager as well from the current state to the end state. In this example, you can see how you can have multiple states that you can animate back and forth between.

Here is some sample code to create the ScreenTransition component:

```java
public SamplePanel() {
   initComponents();

   // — create the animator object (set delay and interpolator)
   Animator anim = new Animator(200);
   // http//javadesktop.org/swinglabs/demos/timingframework/SplineEditor.jnlp
   anim.setInterpolator(new SplineInterpolator(
           0.00f, 1.00f,
           1.00f, 0.98f));

   // — setup the screen transition object, with TransitionTarget & Animator
   st = new ScreenTransition(
           contentPanel,
           this,
           anim
   );
}
```
Here is some sample code to implement the callback (TransitionTarget):

```java
enum Layouts {
  Wide, Tall
}

Layouts currentLayout = Layouts.Wide;
Layouts newLayout = null;

public void setupNextScreen() {
 contentPanel.removeAll();
 switch (newLayout) {
      case Tall // — do Tall layout…
          TableLayout tallLayout = new TableLayout(new double[][]{
                  {0.3, TableLayout.FILL},
                  {0.5, 0.5}});
          tallLayout.setHGap(5);
          tallLayout.setVGap(5);
          contentPanel.setLayout(tallLayout);
          contentPanel.add(leftLabel, new TableLayoutConstraints(0, 0, 0, 1,
          TableLayoutConstraints.FULL, TableLayoutConstraints.FULL));
          contentPanel.add(middleLabel, new TableLayoutConstraints(1, 0, 1, 0,
          TableLayoutConstraints.FULL, TableLayoutConstraints.FULL));
          contentPanel.add(rightLabel, new TableLayoutConstraints(1, 1, 1, 1,
          TableLayoutConstraints.FULL, TableLayoutConstraints.FULL));
          break;

      case Wide // — do Wide layout
          TableLayout wideLayout = new TableLayout(new double[][]{
                  {0.33, 0.33, TableLayout.FILL},
                  {TableLayout.FILL}});
          wideLayout.setHGap(5);
          wideLayout.setVGap(5);
          contentPanel.setLayout(wideLayout);
          contentPanel.add(leftLabel, new TableLayoutConstraints(0, 0, 0, 0,
          TableLayoutConstraints.FULL, TableLayoutConstraints.FULL));
          contentPanel.add(middleLabel, new TableLayoutConstraints(1, 0, 1, 0,
          TableLayoutConstraints.FULL, TableLayoutConstraints.FULL));
          contentPanel.add(rightLabel, new TableLayoutConstraints(2, 0, 2, 0,
          TableLayoutConstraints.FULL, TableLayoutConstraints.FULL));
          break;
  }

  currentLayout = newLayout;
  newLayout = null;
}
```

Here is some code to kick off the transition, when the user presses one of the two buttons:

```java
enum Layouts {
  Wide, Tall
}

Layouts currentLayout = Layouts.Wide;
Layouts newLayout = null;

public void setupNextScreen() {
 contentPanel.removeAll();

 switch (newLayout) {
      case Tall // — do Tall layout…
          TableLayout tallLayout = new TableLayout(new double[][]{
                 {0.3, TableLayout.FILL},
                 {0.5, 0.5}});

          tallLayout.setHGap(5);
          tallLayout.setVGap(5);
          contentPanel.setLayout(tallLayout);
          contentPanel.add(leftLabel, new TableLayoutConstraints(0, 0, 0, 1,
          TableLayoutConstraints.FULL, TableLayoutConstraints.FULL));
          contentPanel.add(middleLabel, new TableLayoutConstraints(1, 0, 1, 0,
          TableLayoutConstraints.FULL, TableLayoutConstraints.FULL));
          contentPanel.add(rightLabel, new TableLayoutConstraints(1, 1, 1, 1,
          TableLayoutConstraints.FULL, TableLayoutConstraints.FULL));
          break;

     case Wide // — do Wide layout
          TableLayout wideLayout = new TableLayout(new double[][]{
                  {0.33, 0.33, TableLayout.FILL},
                  {TableLayout.FILL}});
          wideLayout.setHGap(5);
          wideLayout.setVGap(5);
          contentPanel.setLayout(wideLayout);
          contentPanel.add(leftLabel, new TableLayoutConstraints(0, 0, 0, 0,
          TableLayoutConstraints.FULL, TableLayoutConstraints.FULL));
          contentPanel.add(middleLabel, new TableLayoutConstraints(1, 0, 1, 0,
          TableLayoutConstraints.FULL, TableLayoutConstraints.FULL));
          contentPanel.add(rightLabel, new TableLayoutConstraints(2, 0, 2, 0,
          TableLayoutConstraints.FULL, TableLayoutConstraints.FULL));
          break;
  }

 currentLayout = newLayout;
 newLayout = null;
}
```

## Summary

The strategy outlined here is just a quick way to get transitions implemented in your user 
interface without having to write tons of custom code, and having to debug it and test it. There 
are many more strategies that you can select, depending on your requirements. However, I feel 
that this is one of the simplest and most effective approaches that have worked well for me, and 
I use it all the time in creating the user interface for applications in my desktop app framework
for ScreamingToaster. If you look at some of the animations on the video posted on this website, 
they all use this strategy.

## Related links

  * Timingframework – [http://timingframework.java.net](http://timingframework.java.net)

  * SwingX - [http://swinglabs.org](http://swinglabs.org)

  * Filthy Rich Clients - [http://amazon.com](http://www.amazon.com/gp/product/0132413930?ie=UTF8&tag=developerlife-20&link_code=as3&camp=211189&creative=373489&creativeASIN=0132413930)



