---
author: Nazmul Idris
date: 2008-08-04 15:26:00+00:00
excerpt: |
  This tutorial shows you how to use the LinearLayout container (using Java
  code, not XML markup), which is the simplest layout mechanism available on Android.
  If you're familiar with Swing's BoxLayout then you will have a good idea of what
  this container has to offer. Linear layouts are really simple... you can add 
  components horizontally or vertically to a ‘bag’ or ‘box’.
layout: post
title: "Android LinearLayout Tutorial"
categories:
  - Android
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [What can I do with LinearLayout?](#what-can-i-do-with-linearlayout)
- [Example with source code](#example-with-source-code)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

This tutorial covers the [LinearLayout](http://code.google.com/android/reference/android/widget/LinearLayout.html)
container, which is the simplest layout mechanism available on Android. If you're familiar with
[Swing's BoxLayout](http://java.sun.com/docs/books/tutorial/uiswing/layout/box.html) then you will have a good idea of
what this container has to offer. Linear layouts are really simple... you can add components horizontally or vertically
to a ‘bag’ or ‘box’. This is a pretty simple way of getting components assembled on a screen. Here are it’s limitations:

1. Can’t overlay components (one in front of the other)

2. Can’t control layout in a grid fashion (for that you can use TableLayout).

Also, you can't select items that you've inserted into this container (unless the components themselves are selectable).
If you want to make every item you add in this container selectable, then you should use ListView.

## What can I do with LinearLayout?

Here's a list of things you can do:

1. You can set the orientation of the LinearLayout to LinearLayout.VERTICAL, or LinearLayout.HORIZONTAL. If you select
   VERTICAL, then all your components added to this container will be stacked on top of each other. If you pick
   HORIZONTAL, they will all be stacked beside each other.

2. Before adding a component to this container, you have to set its
   [LinearLayout.LayoutParams](<http://code.google.com/android/reference/android/widget/LinearLayout.LayoutParams.html#LinearLayout.LayoutParams(int,%20int,%20float)>).
   This specifies the height and width constraints you want to assign to your component.

3. You can specify the "weight" (as a float which has to be less than or equal to 1.0f) when you create the LayoutParams
   for a component that you're adding to the container. This weight determines how much empty space the component should
   take up in the final layout. A good way to use this feature is if you want an expandable component in a mix of some
   other components. For example, if you want to layout 3 components, and you want the middle component to take up the
   space left over by the other 2 then you can specify it's width to be 1.0f. Alternatively, you can assign non zero
   weights to many components (as long as they all add up to 1f). Using this approach you can group the spacing of
   various components.

4. You can specify the "gravity" for each component that's in the LinearLayout. This determines whether the component is
   left or right aligned, and top or bottom aligned, or a combination of these.

That's pretty much it. The LinearLayout is simple to use, and is very useful to quickly get components stacked
vertically or horizontally. When creating the LinearLayout itself, don't forget to setLayoutParams() on it by specifying
layout parameter constraints for the view that the LinearLayout itself is going to be added to.

## Example with source code

In the following example, I will show you how to create a vertical box that has 2 other boxes in it; the enclosing
vertical box itself is added to an Activity. The top component in the vertical box has a weight of 1f which allows it to
take up all the screen space (except for what's taken up by the bottom box). The top box has an image, and a bunch of
clocks in it (vertically laid out). The bottom box has a bunch of buttons in it (horizontally laid out).

Here's the code that creates the enclosing LinearLayout and adds it to an Activity:

```java
@Override
public void onCreate(Bundle icicle) {
  super.onCreate(icicle);
  try {

    // create the UI
    setContentView(PanelBuilder.createPanel1(this));

  }
  catch (Exception e) {
    Log.e(Global.TAG, "ui creation problem", e);
  }

}
```

The PanelBuilder class is just a static class that assembles the UI in Java code:

```java
public static final ViewGroup createPanel1(final MainActivity ctx) {

  // main "enclosing" linearlayout container - mainPanel
  final LinearLayout mainPanel = new LinearLayout(ctx);
  {
    mainPanel.setLayoutParams(new LayoutParams(LayoutParams.FILL_PARENT,
                                               LayoutParams.FILL_PARENT));
    mainPanel.setOrientation(LinearLayout.VERTICAL);

    mainPanel.setBackground(SCREEN_BG_IMG);

    AnimUtils.setLayoutAnim_slidedownfromtop(mainPanel, ctx);

    Log.i(Global.TAG, "created main panel");
  }

  // top panel
  LinearLayout topPanel = new LinearLayout(ctx);
  {
  ...
  }

  // bottom panel
  LinearLayout bottomPanel = new LinearLayout(ctx);
  {
  ...
  }

  // add the panels
  mainPanel.addView(topPanel);
  mainPanel.addView(bottomPanel);

  Log.i(Global.TAG, "added topPanel and bottomPanel to mainPanel");

  return mainPanel;

}
```

Here are some notes on this code:

1. This mainPanel is a LinearLayout container that's displayed in the Activity. I set it's LayoutParams to fill the
   parent (ie, full screen on the activity). Alternatively, you can use the LayoutUtils utility class provided in
   [AndroidUtils]({{'assets/androidutils.zip' | relative_url}}) to save yourself the tedium of setting these verbose
   LayoutParams (this is shown in the code example for assembling the bottomPanel below).

2. mainPanel.setOrientation() sets this to be a vertical LinearLayout.

3. You can set a background image to fill the background of the LinearLayout with setBackground(). In this case,
   SCREEN_BG_IMG is simply an image in R.drawable.\* (in my res/drawable/ folder).

4. AnimUtils is a utility class that I've written [AndroidUtils]({{'assets/androidutils.zip' | relative_url}}) to make
   it easier to assign layout animations on Viewgroup objects/containers (LinearLayout, TableLayout, ListView, etc). It
   can be used to assign different animation sequences to these ViewGroups very easily. With Android's animation
   framework, it's possible to enable layout animation, without you having to write the code.

5. There's some code that creates the top and bottom LinearLayout containers (called topPanel and bottomPanel), which
   are then added to the mainPanel LinearLayout object.

The following code shows you how the topPanel is assembled:

```java
  // top panel
  LinearLayout topPanel = new LinearLayout(ctx);
  {

    // WEIGHT = 1f, GRAVITY = center
    topPanel.setLayoutParams(new LayoutParams(LayoutParams.FILL_PARENT,
                                              LayoutParams.WRAP_CONTENT,
                                              1));
    topPanel.setOrientation(LinearLayout.VERTICAL);
    topPanel.setGravity(Gravity.CENTER);

    // an imageview with scaling...
    ImageView topIcon = new ImageView(ctx);
    topIcon.setImageResource(R.drawable.stlogo);
    topIcon.setAdjustViewBounds(true);
    topIcon.setMaxHeight(TopIconMaxHeight);
    topIcon.setMaxWidth(TopIconMaxWidth);
    topIcon.setScaleType(ScaleType.FIT_CENTER);
    topIcon.setAlpha(TopIconAlpha);
    topIcon.setLayoutParams(new LayoutParams(LayoutParams.WRAP_CONTENT,
                                             LayoutParams.WRAP_CONTENT));

    // clocks...
    AnalogClock clock = new AnalogClock(ctx);
    clock.setBackground(topIcon.getDrawable());
    clock.setLayoutParams(new LayoutParams(LayoutParams.WRAP_CONTENT,
                                           LayoutParams.WRAP_CONTENT));
    DigitalClock clock2 = new DigitalClock(ctx);
    clock2.setLayoutParams(new LayoutParams(LayoutParams.WRAP_CONTENT,
                                            LayoutParams.WRAP_CONTENT));

    // adding imageview and clocks to topPanel
    topPanel.addView(clock);
    topPanel.addView(clock2);

    Log.i(Global.TAG, "created topIcon & clock, and added it to topPanel");

  }
```

Here are some notes on this code:

1. The topPanel LinearLayout is created, and LayoutParams are assigned to it. Note that a weight of "1" is passed in as
   a parameter to the LayoutParams constructor. This will ensure that the topPanel will fill the screen with whatever
   space remains after the bottomPanel is drawn.

2. The gravity is set to CENTER. This simply horizontally and vertically centers any components that are placed inside
   the topPanel.

3. A couple of Views are then added to the container... these are all wrapped to content width and height. So the
   topPanel will take up as much space as it can, but the components inside of it will not... they will be centered.

The following code shows how the bottomPanel is assembled:

```java
  // bottom panel
  LinearLayout bottomPanel = new LinearLayout(ctx);
  {
    LayoutUtils.Layout.WidthFill_HeightWrap
               .applyLinearLayoutParams(bottomPanel);
    bottomPanel.setOrientation(LinearLayout.HORIZONTAL);
    bottomPanel.setGravity(Gravity.CENTER_HORIZONTAL);

    bottomPanel.setBackgroundColor(Color.argb(120, 120, 120, 120));

    ImageButton b1 = _newButton(ctx, R.drawable.icon1);
    ImageButton b2 = _newButton(ctx, R.drawable.icon2);
    ImageButton b3 = _newButton(ctx, R.drawable.icon3);

    bottomPanel.addView(b1);
    bottomPanel.addView(b2);
    bottomPanel.addView(b3);

  }
```

Here are some notes on this code:

1. Instead of creating a LayoutParams object by hand, this code uses the LayoutUtils class (part of AndroidUtils). This
   is a shorthand version of the code you have seen in earlier snippets.

2. The bottomPanel is horizontal, and it's gravity is set to center-horizontal, simply meaning that all components will
   be centered left-right on the bottomPanel.

3. A translucent background color is set on the bottomPanel itself.

4. Finally a bunch of buttons are added to the bottomPanel.

You can download LayoutUtils, AnimUtils and other helpful classes in
[AndroidUtils]({{'assets/androidutils.zip' | relative_url}}).
