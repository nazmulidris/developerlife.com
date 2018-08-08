---
author: Nazmul Idris
date: 2007-12-25 00:38:50+00:00
excerpt: |
  This tutorial will introduce you to the SwingX API and the concept of Painters.
  It will give you an idea of the kinds of effects you can create with them as well,
  with code examples.
layout: post
title: "SwingX Tutorial - Painters"
categories:
- UXE
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [JXPanel](#jxpanel)
- [Painters](#painters)
- [The Painters API](#the-painters-api)
- [Source code example 1](#source-code-example-1)
- [Source code example 2](#source-code-example-2)
- [Download the code](#download-the-code)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

SwingX is an extension to the Swing API by the folks who work on the Swing team. The code is released as open source on [Sun SwingLabs](http://swinglabs.org). Parts of the API that are mature are supposed to show up in Java 7. It's a great way to get a sneak peek at new components and technologies that the Swing team is working on, but it's not ready for an official release, which takes time, etc.

One of the biggest changes with the SwingX API is it's use of painters. Typically, if you wanted to create new components in Swing, you would have to mess with the Look and Feel API. Painters give you the ability to use Java2D code to very quickly define the look of your component.

## JXPanel

SwingX comes with it's own custom repaint manager (which replaces the default implementation used by Swing; there can only be one active at any given time). This custom repaint manager respects the transparency of a top level SwingX container - eg, JXPanel. Unlike a JPanel, when you place a JButton on a JXPanel, and set the button's transparency, it will retain it's transparency even when you click on the button. In the case of JPanel, when the JButton first appears, it will be transparent, but as soon as you click on it, it will become opaque. You can do things like change the transparency of all components in a JXPanel for example, and lots of other neat effects. You can tie this into the [TimingFramework](https://timingframework.dev.java.net/) and very quickly create really cool animations in your user interface (like change the transparency of your components by changing the "alpha" property from 0.0f to 1.0f to fade in a panel).

## Painters

The Painters API is refreshingly simple. All the Java2D code that you want to use to paint your component, that would otherwise go in a subclass of a Swing component who's paint() or paintComponent() method you've overridden, is placed in a class which implements the `Painter<T>` interface, which is defined thusly:

```java
public void paint(Graphics2D g, T object, int width, int height);
```

There are lots of Painter implementations provided for you, and you can even composite various 
existing painter implementations to create new ones. You are limited by your imagination and 
proficiency with the Java2D API 😃. All the SwingX components are Painter enabled - they all 
have a `setBackgroundPainter(Painter<T>)` method.

## The Painters API

Out of the box, SwingX comes with a rich set of Painter implementations, some of which are listed here:

  1. [GlossPainter](http://swinglabs.org/hudson/job/SwingX%20Continuous%20Build/javadoc/org/jdesktop/swingx/painter/GlossPainter.html) - this paints a gloss effect on your component, you can pick the gloss [Paint](http://java.sun.com/j2se/1.5.0/docs/api/java/awt/Paint.html) object and gloss position (top/bottom). The gloss effect is painted as a filled arc that highlights the component with whatever color you provided. The [Paint](http://java.sun.com/j2se/1.5.0/docs/api/java/awt/Paint.html)object that's used to paint the gloss effect can be a simple Color, or a gradient or a texture.

  2. [ImagePainter](http://swinglabs.org/hudson/job/SwingX%20Continuous%20Build/javadoc/org/jdesktop/swingx/painter/ImagePainter.html) - this paints a [BufferedImage](http://java.sun.com/j2se/1.5.0/docs/api/java/awt/image/BufferedImage.html)on your component. You have control over how you want the image painted. You can choose to have it scale to the site of the area that needs to be painted, or you can have it tiled, or centered. There are lots of layout options that you can pick.

  3. [MattePainter](http://swinglabs.org/hudson/job/SwingX%20Continuous%20Build/javadoc/org/jdesktop/swingx/painter/MattePainter.html) - this uses a [Paint](http://java.sun.com/j2se/1.5.0/docs/api/java/awt/Paint.html)object to paint your component. This can be used to fill the component area with a color, gradient, or texture.

  4. [PinstripePainter](http://swinglabs.org/hudson/job/SwingX%20Continuous%20Build/javadoc/org/jdesktop/swingx/painter/PinstripePainter.html) - this paints pinstripes on your component, and you can control the angle, width, distance apart, and color ([Paint](http://java.sun.com/j2se/1.5.0/docs/api/java/awt/Paint.html)object) of these stripes. Instead of using a color, you can use a gradient, or texture, etc.

  5. [CompoundPainter](http://swinglabs.org/hudson/job/SwingX%20Continuous%20Build/javadoc/org/jdesktop/swingx/painter/CompoundPainter.html) - this allows you to add multiple painter implementations to a component. The painters will be rendered in the order in which they are added to the [CompoundPainter](http://swinglabs.org/hudson/job/SwingX%20Continuous%20Build/javadoc/org/jdesktop/swingx/painter/CompoundPainter.html). It can be used to quickly create cool effects.

  6. [RectanglePainter](http://swinglabs.org/hudson/job/SwingX%20Continuous%20Build/javadoc/org/jdesktop/swingx/painter/RectanglePainter.html) - this paints a rectangle on your component. You can select a fill Paint object and background Paint object. There are lots of other options like border size, and rounded borders.

There are other painters like ShapePainter, TextPainter, URLPainter, CheckerboardPainter, and BusyPainter. You can extend [AbstractPainter](http://swinglabs.org/hudson/job/SwingX%20Continuous%20Build/javadoc/org/jdesktop/swingx/painter/AbstractPainter.html) to create your own. The code examples below will get you started using Painters; experiment with the API and create your own effects using the provided painters, and composite them using CompoundPainter.

## Source code example 1

In the following example, I'm going to create a JXLabel and set a compound background painter on it. Here's what it looks like:

![]({{'assets/painter-1.png' | relative_url}})

Here's the code which produced this painter:

```java
/**
* this compound painter composites a bunch of different painters.
*/
private Painter getPainter() {
    // set the background painter
    MattePainter mp = new MattePainter(Colors.LightBlue.alpha(0.5f));
    GlossPainter gp = new GlossPainter(Colors.White.alpha(0.3f),
                                       GlossPainter.GlossPosition.TOP);
    PinstripePainter pp = new PinstripePainter(Colors.Gray.alpha(0.2f),
                                               45d);
    return (new CompoundPainter(mp, pp, gp));
}
```

In this example, I create 3 painters and composite them and apply them to the [JXLabel](http://swinglabs.org/hudson/job/SwingX%20Continuous%20Build/javadoc/org/jdesktop/swingx/JXLabel.html) (which is the SwingX label class):

  1. MattePainter - I fill the component with a translucent light blue color (50% transparent).

  2. GlossPainter - I apply a white gloss (30% transparent) to the top of the label.

  3. PinstripePainter - I apply a gray (50% transparent) color to the label.

These painters are applied in the order in which they are added to the CompoundPainter - first MattePainter, then PinstripePainter, and finally GlossPainter. If you look at the screenshot, you will see that the Pinstripes are BEHIND the Gloss effect. Also, notice that the text "Painter Example 1" is in front of the painters, since they are all background painters. If you want to add text behind a painter, then use the TextPainter and make sure to add it in the right order in your CompositePainter.

Here's the full source code listing for this example:

```java
  import org.jdesktop.swingx.*;
  import org.jdesktop.swingx.painter.*;
 
  import javax.swing.*;
  import java.awt.*;
 
  /**
   * PainterExample1
   *
   * @author Nazmul Idris
   * @version 1.0
   * @since Dec 25, 2007, 13 PM
   */
  public class PainterExample1 {
 
  /**
   * simple main driver for this class
   */
  public static void main(String[] args) {
    SwingUtilities.invokeLater(new Runnable() {
      public void run() {
        new PainterExample1();
      }
    });
  }
 
  /**
   * creates a JFrame and calls {@link #doInit} to create a 
   * JXPanel and adds the panel to this frame.
   */
  public PainterExample1(){
    JFrame frame = new JFrame("Painter Example 1");
 
    // add the panel to this frame
    frame.add(doInit());
 
    // when you close the frame, the app exits
    frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
 
    // center the frame and show it
    frame.setLocationRelativeTo(null);
    frame.pack();
    frame.setVisible(true);
  }
 
  /**
   * creates a JXLabel and attaches a painter to it.
   */
  private Component doInit() {
    JXPanel panel = new JXPanel();
    panel.setLayout(new BorderLayout());
 
    JXLabel label = new JXLabel();
    label.setFont(new Font("Segoe UI", Font.BOLD, 14));
    label.setText("Painter Example 1");
    label.setHorizontalAlignment(JXLabel.CENTER);
    label.setBackgroundPainter(getPainter());
 
    panel.add(label, BorderLayout.CENTER);
 
    panel.setPreferredSize(new Dimension(250,100));
 
    return panel;
  }
 
  /**
   * this compound painter composites a bunch of different painters.
   */
  private Painter getPainter() {
    // set the background painter
    MattePainter mp = new MattePainter(Colors.LightBlue.alpha(0.5f));
    GlossPainter gp = new GlossPainter(Colors.White.alpha(0.3f),
                                       GlossPainter.GlossPosition.TOP);
    PinstripePainter pp = new PinstripePainter(Colors.Gray.alpha(0.2f),
                                               45d);
    return (new CompoundPainter(mp, pp, gp));
  }
  }//end class PainterExample1
```

The other interesting class is the Color enumeration, that makes it easy to work with colors. I will write a tutorial on Java5 enumerations and how they make it really easy to create type safe constants, and much more. It allows you to easily work with custom colors that you've created, and you can get translucent colors conveniently, and you can get HEX encoded strings to use in HTML. Here's a listing of the Color enum:

```java
  import java.awt.*;
 
  /**
   * Colors is an enumeration class that makes it easier to work with 
   * colors. Methods are provided for conversion to hex strings, and 
   * for getting alpha channel colors.
   *
   * @author Nazmul Idris
   * @version 1.0
   * @since Apr 21, 2007, 24 PM
   */
  public enum Colors {
 
  // various colors in the pallete
    Pink(255, 175, 175),
    Green(159, 205, 20),
    Orange(213, 113, 13),
    Yellow(Color.yellow),
    Red(189, 67, 67),
    LightBlue(208, 223, 245),
    Blue(Color.blue),
    Black(0, 0, 0),
    White(255, 255, 255),
    Gray(Color.gray.getRed(), Color.gray.getGreen(), Color.gray.getBlue());
 
  // constructors
 
  Colors(Color c) {
    _myColor = c;
  }
 
  Colors(int r, int g, int b) {
    _myColor = new Color(r, g, b);
  }
 
  Colors(int r, int g, int b, int alpha) {
    _myColor = new Color(r, g, b, alpha);
  }
 
  Colors(float r, float g, float b, float alpha) {
    _myColor = new Color(r, g, b, alpha);
  }
 
  // data
 
  private Color _myColor;
 
  // methods
 
  public Color alpha(float t) {
    return new Color(_myColor.getRed(), 
                     _myColor.getGreen(), 
                     _myColor.getBlue(), 
                     (int) (t * 255f));
  }
 
  public static Color alpha(Color c, float t) {
    return new Color(c.getRed(), 
                     c.getGreen(), 
                     c.getBlue(), 
                     (int) (t * 255f));
  }
 
  public Color color() { return _myColor; }
 
  public Color color(float f) {
    return alpha(f);
  }
 
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("r=")
        .append(_myColor.getRed())
        .append(", g=")
        .append(_myColor.getGreen())
        .append(", b=")
        .append(_myColor.getBlue())
        .append("n");
    return sb.toString();
  }
 
  public String toHexString() {
    Color c = _myColor;
    StringBuilder sb = new StringBuilder();
    sb.append("#");
    sb.append(Integer.toHexString(_myColor.getRed()));
    sb.append(Integer.toHexString(_myColor.getGreen()));
    sb.append(Integer.toHexString(_myColor.getBlue()));
    return sb.toString();
  }
 
  }//end enum Colors
```

## Source code example 2

In this second example, I will show you how to use a different painter to draw a gradient fill on a component, and change it's transparency using JXLabel. Here's a screenshot:

![]({{'assets/painter-2.png' | relative_url}})

Here's the code for the painter:

```java
  /** this painter draws a gradient fill */
  public Painter getPainter() {
    int width = 100;
    int height = 100;
    Color color1 = Colors.White.color(0.5f);
    Color color2 = Colors.Gray.color(0.5f);
 
    LinearGradientPaint gradientPaint =
        new LinearGradientPaint(0.0f, 0.0f, width, height,
                                new float[]{0.0f, 1.0f},
                                new Color[]{color1, color2});
    MattePainter mattePainter = new MattePainter(gradientPaint);
    return mattePainter;
  }
```

The MattePainter uses a Paint object, which draws a gradient fill (using LinearGradientPaint class).

The following line of code makes the JXPanel and everything inside it 50% transparent:

```java
  // set the transparency of the JXPanel to 50% transparent
  panel.setAlpha(0.5f);
```

Here's the complete code listing for this example:

```java
  import org.jdesktop.swingx.*;
  import org.jdesktop.swingx.painter.*;
 
  import javax.swing.*;
  import java.awt.*;
 
  /**
   * PainterExample2
   *
   * @author Nazmul Idris
   * @version 1.0
   * @since Dec 25, 2007, 13 PM
   */
  public class PainterExample2 {
 
  /** simple main driver for this class */
  public static void main(String[] args) {
    SwingUtilities.invokeLater(new Runnable() {
      public void run() {
        new PainterExample2();
      }
   });
  }
 
  /** creates a JFrame and calls {@link #doInit} to 
  * create a JXPanel and adds the panel to this frame. */
  public PainterExample2() {
    JFrame frame = new JFrame("Painter Example 2");
 
    // add the panel to this frame
    frame.add(doInit());
 
    // when you close the frame, the app exits
    frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
 
    // center the frame and show it
    frame.setLocationRelativeTo(null);
    frame.pack();
    frame.setVisible(true);
  }
 
  /** creates a JXLabel and attaches a painter to it. */
  private Component doInit() {
    JXPanel panel = new JXPanel();
    panel.setLayout(new BorderLayout());
 
    JXLabel label = new JXLabel();
    label.setFont(new Font("Segoe UI", Font.BOLD, 14));
    label.setText("Painter Example 2");
    label.setHorizontalAlignment(JXLabel.CENTER);
    label.setBackgroundPainter(getPainter());
 
    // set the transparency of the JXPanel to 50% transparent
    panel.setAlpha(0.5f);
 
    panel.add(label, BorderLayout.CENTER);
    panel.setPreferredSize(new Dimension(250, 100));
 
    return panel;
  }
 
  /** this painter draws a gradient fill */
  public Painter getPainter() {
    int width = 100;
    int height = 100;
    Color color1 = Colors.White.color(0.5f);
    Color color2 = Colors.Gray.color(0.5f);
 
    LinearGradientPaint gradientPaint =
       new LinearGradientPaint(0.0f, 0.0f, width, height,
                               new float[]{0.0f, 1.0f},
                               new Color[]{color1, color2});
    MattePainter mattePainter = new MattePainter(gradientPaint);
    return mattePainter;
  }
 
  }//end class PainterExample2
```

## Download the code

You can download the 0.9.1 release of SwingX [here](http://swinglabs.org/downloads.jsp):

  1. Binaries - [https://swingx.dev.java.net/files/documents/2981/76227/swingx-0.9.1.zip](https://swingx.dev.java.net/files/documents/2981/76227/swingx-0.9.1.zip)

  2. Sources - [https://swingx.dev.java.net/files/documents/2981/76229/swingx-0.9.1-src.zip](https://swingx.dev.java.net/files/documents/2981/76229/swingx-0.9.1-src.zip)

  3. JavaDocs - [https://swingx.dev.java.net/files/documents/2981/76228/swingx-0.9.1-javadoc.zip](https://swingx.dev.java.net/files/documents/2981/76228/swingx-0.9.1-javadoc.zip)

You can download the source code for this tutorial, which includes the SwingX libraries, along 
with IDEA projects for the code [here]({{'assets/painters.zip' | relative_url}}).