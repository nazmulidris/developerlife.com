---
author: Nazmul Idris
date: 2008-07-31 19:08:09+00:00
excerpt: |
  This tutorial will show you how to use Android's theme-ing capabilities.
  You can set background color, image, etc. on widgets, dialogs, and activities.
layout: post
title: "Android UI Themes Tutorial"
categories:
- Android
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [Defining themes in XML](#defining-themes-in-xml)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

This tutorial will familiarize you with the theme-ing capabilities of Android API. You can set background color, image, etc. on widgets. However, there are some customizations that can only be performed by using the theme-ing facility. Examples of this include change the colors/images of a top-level window like an Activity or Dialog.

## Defining themes in XML

Here's an example of defining a theme in XML, this goes in the styles.xml file in the `<your project>/res/values/styles.xml` file; you can define colors, drawables, and lots of other resources here that get referenced in your theme:

```xml
<resources>
  <!-- Base application theme is the default theme. -->
  <style name="Theme" parent="android:Theme">
  </style>

  <!-- Variation on our application theme that has a translucent
 background. -->
  <style name="Theme.Translucent">
    <item name="android:windowBackground">@drawable/translucent_background</item>
    <item name="android:windowNoTitle">true</item>
    <item name="android:colorForeground">#fff</item>
  </style>

  <!-- Variation on our application theme that has a transparent
background; this example completely removes the background,
allowing the activity to decide how to composite. -->
  <style name="Theme.Transparent">
    <item name="android:windowBackground">@drawable/transparent_background</item>
    <item name="android:windowNoTitle">true</item>
    <item name="android:colorForeground">#fff</item>
  </style>
  <style name="TextAppearance.Theme.PlainText" 
         parent="android:TextAppearance.Theme">
    <item name="android:textStyle">normal</item>
  </style>

</resources>
```

This is how you reference this theme in an Activity:

```java
public class WidgetActivity extends Activity {

@Override protected void onCreate(Bundle bundle) {
  super.onCreate(bundle);

  Log.i(Global.TAG2, 
        "sub-Activity WidgetActivity being creation: start");

  setTheme(R.style.Theme_Translucent);

  setContentView(Panel2Builder.createWidgetPanel(this));

  Log.i(Global.TAG2, 
        "sub-Activity WidgetActivity being creation: end");

}

}//end class WidgetActivity
```

The Android SDK Manual has a lot [more information on styles and themes](http://code.google.com/android/reference/available-resources.html#stylesandthemes) and how [assets and content](http://code.google.com/android/reference/android/content/package-descr.html) are used and created.
