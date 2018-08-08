---
author: Nazmul Idris
date: 2008-07-16 21:51:14+00:00
excerpt: |
  This tutorial will show you how to instantiate or inflate a View from XML;
  this is  useful for components that don't provide a Java API to tweak with certain
  style attributes. The Button class is used as an example; you can only get certain
  styles to show up via XML that aren't available via the Java API.
layout: post
title: "Android XML View inflation Tutorial"
categories:
- Android
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [Button styles](#button-styles)
- [Inflating the view from compiled XML](#inflating-the-view-from-compiled-xml)
- [Loading the whole layout in your Activity's onCreate() method](#loading-the-whole-layout-in-your-activitys-oncreate-method)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

If you have to create a component, but the layout or style attributes can't be set in Java code, then you can use this approach to bridge that gap. An example of this is button style attributes aren't available in the Java API, only from XML. Alternatively, if you are using layout code that's already created in XML, then you can leverage it; so it's not an all or nothing, I will do everything in Java, or in XML; you can do a bit of both, in situations where they make sense.

## Button styles

A Button can have a few style attributes that can be set on it:

  1. normal button - no style attributes required, this is the default
  2. normal right style - style="?android:attr/buttonStyleRight"
  3. small style - style="?android:attr/buttonStyleSmall"
  4. small right style - style="?android:attr/buttonStyleSmallRight"
  5. etc.

So there are normal size and small size buttons, each of which have 4 more variations of "up", "down", "left", and "right". To get a list of all these style attribute values, look at this class [android.R.attr.button](http://code.google.com/android/reference/android/R.attr.html#button).

## Inflating the view from compiled XML

Here's the code in XML (of buttons.xml in /res/layouts) to create one of these buttons, since you can't set the style in Java code easily:

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- the android:id stuff is optional -->
<!-- the button styles are from here - 
  http://code.google.com/android/samples/ApiDemos/res/layout/buttons_1.html -->

<Button xmlns:android="http://schemas.android.com/apk/res/android"
        android:id="@+id/button_small_left"
        style="?android:attr/buttonStyleSmall"
        android:text="Press to close"
    />
```
Some notes on the XML file:

  1. You can specify the layout parameters in here, or not. It's possible to attach layout parameters in Java code.

  2. The android:id attribute is only needed if you want to reference this object by it's id later on (eg, by using Activity.findViewById() method). If you remove this line, then you won't be able to reference this View using R.id.button_small_left. In the code example below, this isn't really needed, so I could have just left this blank.

  3. The "style" attribute is why this approach is even needed, since there are no Java APIs to get to set this attribute easily!

  4. You can set the text attribute here, or set it in Java code using setText().

Here's the Java code to create one of these buttons:

```java
  Button b = (Button) activity.getViewInflate().inflate(R.layout.buttons,
                                                        null,
                                                        null);
```
Here are some notes on this code:

  1. R.layout.buttons is the complied XML resource (ie, under the res folder, and not assets) that needs to be inflated into a View object.

  2. You have to get an [instance of ViewInflate](http://code.google.com/android/reference/android/view/ViewInflate.html) from the Activity/Context or system service, don't instantiate one yourself.

  3. Once the button is created you can assign layout parameters to it, listeners, etc.

  4. You can choose what to initialize in the XML and what to initialize in the code.

Alternatively, you could use the following code:

```java
  View v = activity.getViewInflate().inflate(R.layout.buttons, null, null);
  Button b = (Button)v.findViewById(R.id.button_small_left);
```

Here are some notes on this code:

  1. In this version, the buttons.xml file (which is the same) is inflated, then it's queried for a specific View with the given id. This id is defined in the XML - android:id="@+id/button_small_left".

  2. You should use this version of the code to inflate a View if you have more than one View defined in the XML layout file. This way the id can be used to uniquely identify one View that you're interested in displaying.

## Loading the whole layout in your Activity's onCreate() method

Alternatively, if you define your entire Activity's layout in XML, you can just use Activity.findViewById(int) to get a reference to these View objects. In this case, the inflation occurs in the onCreate() method of the Activity, when you pointed your layout XML resource to the setContentView() method.
