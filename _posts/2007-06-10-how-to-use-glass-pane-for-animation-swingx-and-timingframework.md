---
author: Nazmul Idris
date: 2007-06-10 20:02:26+00:00
excerpt: |
  I needed to perform animations in the desktop app framework that I'm building
  for ScreamingToaster. I needed to build animations that move various 
  components around on the screen, and other animations that pop up components 
  on top of existing components, etc. After creating a few of these effects, 
  I realized that I was doing the same thing over and over again, which is why 
  I decided to write this tutorial to encapsulate this pattern, in the hopes 
  that I will help others doing the same thing.
layout: post
title: "How to use glass pane for animation (SwingX and Timingframework)"
categories:
- UXE
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [Background information](#background-information)
- [Getting started](#getting-started)
- [Implementation details](#implementation-details)
  - [#1 implementation of the event listener that will trigger the animator to start](#1-implementation-of-the-event-listener-that-will-trigger-the-animator-to-start)
  - [#2 implementation of the custom component that performs the animation](#2-implementation-of-the-custom-component-that-performs-the-animation)
  - [Extras](#extras)
- [Summary](#summary)
- [Related links](#related-links)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

  I needed to perform animations in the desktop app framework that I'm building
  for ScreamingToaster. I needed to build animations that move various 
  components around on the screen, and other animations that pop up components 
  on top of existing components, etc. After creating a few of these effects, 
  I realized that I was doing the same thing over and over again, which is why 
  I decided to write this tutorial to encapsulate this pattern, in the hopes 
  that I will help others doing the same thing.

The strategy outlined here is just a suggestion on how to perform animation using a glass pane. 
There are many more strategies that you can select, depending on your requirements. However, I 
feel that this is one of the simplest and most effective approaches that have worked well for me,
and I use it all the time in creating the user interface for applications in my desktop app 
container framework for ScreamingToaster. If you look at some of the animations on the video posted
on this website, they all use this strategy.

The following is a list of approaches that you can take to create custom components:

<table class="formattedinnertable" >

<tbody >

<tr >

<td width="40%" ><strong>Strategy</strong>

</td>

<td width="60%" ><strong>Cost</strong>

</td>

</tr>

<tr >

<td >Create your own components that implement paint() methods, or override the paint() method on existing components

</td>

<td >Medium/High level of effort, since you have to generate your own paint method

</td>

</tr>

<tr >

<td >Use SwingX API to install your own custom painters

</td>

<td >Low level of effort, since you can mix and match a variety of painters that are provided for you. It’s easy to write painters as well

</td>

</tr>

<tr >

<td >Use the glass pane to perform custom painting on top of your existing components

</td>

<td >Low level of effort, since you can just paint what you need, instead of re-doing painting code for various components

</td>

</tr>

<tr >

<td >Implement your own look and feel

</td>

<td >High level of effort, unless you just tweak with a few UIDelegates

</td>

</tr>

</tbody>

</table>

The following is a list of approaches that you can take to create animations:

<table class="formattedinnertable" >

<tbody >

<tr >

<td width="40%" ><strong>Strategy</strong>

</td>

<td width="60%" ><strong>Cost</strong>

</td>

</tr>

<tr >

<td >Create your animations in a custom paint() method

</td>

<td >Medium/High level of effort, since you may have to implement the whole thing from scratch. You can speed things up (reduce your coding effort) by drawing over existing components using super.paint()

</td>

</tr>

<tr >

<td valign="top" >Use the glass pane to draw the animation sequences on

</td>

<td valign="top" >Low/Medium level of effort, since you may just have to paint on top of existing components

</td>

</tr>

<tr >

<td valign="top" >Implement your own look and feel

</td>

<td valign="top" >High level of effort

</td>

</tr>

</tbody>

</table>

The easiest approach is to performing animations is using the glass pane. This tutorial will outline a strategy to using the glass pane for performing your own custom animation on components, to add special effects like Spring and Glow, and to even place custom components on top of existing components to show error conditions and such, and have components fly down and move up.

## Background information

For more information on glasspane and RootPaneContainers refer to these links:

  1. The Java Tutorial – [How to use Root Panes](http://java.sun.com/docs/books/tutorial/uiswing/components/rootpane.html)

  2. Java 6 javadocs on [JRootPane](http://java.sun.com/javase/6/docs/api/javax/swing/JRootPane.html)

For more information on SwingX, refer to these links:

  1. SwingLabs – [SwingX toolkit](http://swinglabs.org/)

  2. Download SwingX here – [Hudson Weekly Builds](http://swinglabs.org/hudson/job/SwingX%20Weekly%20Build/)

I'm planning on writing more tutorials on SwingX and how to use painters… check back in a few days/weeks and I should have them uploaded on the site.

For more information on the Timingframework for animation, refer to these lniks:

  1. Timingframework tutorial – [Timing is Everything](http://today.java.net/pub/a/today/2005/02/15/timing.html)

  2. Timingframework homepage – [timingframework.java.net](https://timingframework.dev.java.net/)

  3. Timingframework downloads – [java.net downloads](https://timingframework.dev.java.net/servlets/ProjectDocumentList?folderID=7194&expandFolder=7194&folderID=0)

## Getting started

The basic idea is to have all animation effects delegated to a component that’s placed on the glass pane, on top of your container (dialog, frame, etc). When the appropriate event triggers the animation to being, the custom component has to be installed as the glass pane of your RootPaneContainer and then your animator can be started which runs the animation, and when it’s complete, the glass pane has to be unistalled. The following diagram depicts this sequence of events:

![]({{'assets/glasspane-1.png' | relative_url}})

## Implementation details

You have to implement 2 things:

  1. The event listener that will trigger the animator to start – and the implementation of Animator’s TimingTarget interface. This event listener will be bound to some event source in your container/RootPaneContainer. You can create and initialize your custom component here.

  2. The custom component that will be installed on the RootPaneContainer’s glass pane. This component will be created and initialized by your container/RootPaneContainer.

### #1 implementation of the event listener that will trigger the animator to start

In your event listener, be sure to perform the following in your TimingTarget implementation:

  1. Create the Animator and it’s TimingTarget object.

  2. In the TimingTarget implementation, do the following:

    1. begin() – create your custom component, initialize it, and install it on the RootPaneContainer

    2. timingEvent(float) – delegate to your custom component (which will cause a repaint)

    3. end() – uninstall the custom component from the RootPaneContainer.

  3. Start the Animator after you’ve configured it with the appropriate Interpolator, timing resolution, etc.

Here's is some sample code below of an Animator that you could create in an event handler in your container:

```java
RootPaneContainer container = ...;
AnimCompGlassPane component = new AnimCompGlassPane();
component.init(...);
component.installOnContainer(container);

Animator animator = new Animator(
  ANIMATION_LENGTH, ANIMATION_REPEATS, Animator.RepeatBehavior.REVERSE,
  new TimingTargetAdapter() {
    @Override public void begin() {
   component.startAnimation();
 }



@Override public void timingEvent(float v) {
   component.setAnimationPhase(v);
 }

 @Override public void end() {
   component.endAnimation();
   component.uninstallFromContainer();
 }
 });

animator.setInterpolator(new SplineInterpolator(0.0f, 0.99f, 0.01f, 1.0f));
animator.setResolution(ANIMATION_RESOLUTION);
animator.start();
```
### #2 implementation of the custom component that performs the animation

In your custom component, that actually performs the painting for the animation, be sure to perform the following:

  1. Provide an install(RootPaneContainer) method that installs this component on the glass pane of the RootPaneContainer after saving off the old component that’s in the glass pane. There is only one glass pane per container, so be sure to save off an existing one and restore it once your animation is complete – so be careful not to clobber existing glass panes.

  2. Provide an uninstall() method that removes this component from the RootPaneContainer’s glass pane and restores the original glass pane component.

  3. Provide a method that will be called by timingEvent(float) of the TimingTarget implementation. This method should store the current animation stage (which is a float between 0f and 1f that signifies how much of the animation is complete), and it should call repaint().

  4. Provide an implementation of paint(Graphics) method that performs your custom painting code. It should use the float value received in the method above to determine what stage of the animation to paint.

Here is some sample code, that may be a partial implementation of your animated component that goes on the glass pane:

```java
private RootPaneContainer _rootPaneContainer;
private Component _oldGlasspane;
private float _animPhase;

public void installOnContainer(RootPaneContainer container){
  _rootPaneContainer = container;
  _oldGlasspane = _rootPaneContainer.getGlassPane();
  _rootPaneContainer.setGlassPane(this);
  setVisible(true);
 requestFocusInWindow();
}

public void uninstallFromContainer(){
 setVisible(false);
 _rootPaneContainer.setGlassPane(_oldGlasspane);
 _rootPaneContainer = null;
 _oldGlasspane = null;
}

public void startAnimation(){...}

public void setAnimationPhase(float v){
 _animPhase = v;
 repaint();
}

public void endAnimation(...);

public void paint(Graphics g){
 super.paint(g);
 // do something with _animPhase and paint... 
}
```
### Extras

When the glass pane is installed on your RootPaneContainer, you should request that it gets keyboard focus. This way, you won't see any strange artifacts of keypresses moving things around underneath the component in the glasspane. You can also install a sink that absorbs all key press and mouse events so that these aren’t passed on to components other that what’s on your glass pane. You can also choose to respond to mouse events or key presses by removing the glass pane (kick off the animation which hides the component in the glass pane for example). The same pattern used in the #1 would apply here!

## Summary

The strategy outlined here is just a suggestion on how to perform animation using a glass pane. 
There are many more strategies that you can select, depending on your requirements. However, I 
feel that this is one of the simplest and most effective approaches that have worked well for me,
and I use it all the time in creating the user interface for applications in my desktop app 
framework for ScreamingToaster. If you look at some of the animations on the video posted on this 
website,  they all use this strategy.

## Related links

  * Timingframework – [http://timingframework.java.net](http://timingframework.java.net)
  * SwingX - [http://swinglabs.org](http://swinglabs.org)