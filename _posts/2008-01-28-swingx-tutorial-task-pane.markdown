---
author: Nazmul Idris
date: 2008-01-28 18:48:20+00:00
excerpt: |
  This tutorial will walk you through the steps required to use JXTaskPane
  and JXTaskPaneContainer in SwingX. You will learn how to change the default color
  schemes of these components, and add components and actions to task panes.
layout: post
title: "SwingX Tutorial - Task Pane (JXTaskPane, Container)"
categories:
- UXE
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [What is a task pane?](#what-is-a-task-pane)
- [Source code example](#source-code-example)
- [Download project](#download-project)
- [Comments and Feedback](#comments-and-feedback)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

SwingX introduces a lot of new components to Swing, and this tutorial will cover the task pane. You have seen task panes before if you've used Windows, they are used extensively in explorer and control panel. Here's are examples:

![]({{'assets/swingx-1.png' | relative_url}})
![]({{'assets/swingx-2.png' | relative_url}})

## What is a task pane?

The SwingX implementation of the task pane is more like Windows XP rather than Windows Vista, but the idea is the same. In a [task pane](http://swinglabs.org/hudson/job/SwingX%20Continuous%20Build/javadoc/org/jdesktop/swingx/JXTaskPane.html), you can add various actions and components that are displayed in a list, which can be collapsed. You are free to add more than 1 task pane to a [task pane container](http://swinglabs.org/hudson/job/SwingX%20Continuous%20Build/javadoc/org/jdesktop/swingx/JXTaskPaneContainer.html). You can also set an icon and title for your task pane. You can also set formatting options to change the colors used by the task pane and the task pane container.

You don't have to use a task pane container to hold a task pane, you can add the task pane to any swing container. However, if you place the task pane in the task pane container, it will render better (SwingX changes the default colors of the task pane and container to match the OS it's running on). You can override these default color schemes by adding key-value pairs in the UI Defaults yourself. This tutorial will cover all of this functionality.

## Source code example

In the following example, I'm going to create a JXTaskPane, with some components, that I will then place in a JXTaskPaneContainer. Here is what it looks like:

![]({{'assets/swingx-3.png' | relative_url}})

The JXTaskPane called "My Tasks" has an icon and a title. It also contains a JXLabel with a background painter, and an Action object (which has a name, icon, and tooltip). When you click on the action, it simply changes the JXLabel's text. Note that you can collapse the entire JXTaskPane by clicking anywhere on the title, or by pressing "Space" with your keyboard, when it's in focus. You can change keyboard focus between the action and the JXTaskPane title by pressing the "Tab" key on your keyboard.

The first step in coding up this example is creating the JXTaskPane and JXTaskPaneContainers. The JXTaskPane also needs to be populated with an Action and JXLabel. Here's the code to do this:

```java
// create a label
final JXLabel label = new JXLabel();
label.setFont(new Font("Segoe UI", Font.BOLD, 14));
label.setText("task pane item 1 : a label");
label.setIcon(Images.NetworkDisconnected.getIcon(32, 32));
label.setHorizontalAlignment(JXLabel.LEFT);
label.setBackgroundPainter(getPainter());
// tweak with the UI defaults for the taskpane and taskpanecontainer
changeUIdefaults();
// create a taskpanecontainer
JXTaskPaneContainer taskpanecontainer = new JXTaskPaneContainer();
// create a taskpane, and set it's title and icon
JXTaskPane taskpane = new JXTaskPane();
taskpane.setTitle("My Tasks");
taskpane.setIcon(Images.Quit.getIcon(24, 24));
// add various actions and components to the taskpane
taskpane.add(label);
taskpane.add(new AbstractAction() {
 {
 putValue(Action.NAME, "task pane item 2 : an action");
 putValue(Action.SHORT_DESCRIPTION, "perform an action");
 putValue(Action.SMALL_ICON, Images.NetworkConnected.getIcon(32, 32));
 }
 public void actionPerformed(ActionEvent e) {
 label.setText("an action performed");
 }
});
// add the task pane to the taskpanecontainer
taskpanecontainer.add(taskpane);
```

There are a couple of things to note here:

  1. There is an enumeration called Images, which is used to load some images that come with this example. I've added 3 PNG images to the icons.zip file that are included as part of the [project download](http://developerlife.com/tutorials/wp-content/uploads/2008/01/taskpane.zip) (it's in the lib folder of the zip file). The enumeration has code in it which allows me to quickly load the images from PNG format, and then resize them to the width/height that is needed for this example. I use the [GraphicsUtilities](http://swinglabs.org/hudson/job/SwingX%20Continuous%20Build/javadoc/) class that's provided with SwingX, that has lots of useful features that you can use to resize images, etc. I also use the [ImageIO](http://java.sun.com/j2se/1.4.2/docs/api/javax/imageio/ImageIO.html) class to actually read in the PNG file and convert it to a BufferedImage.

```java
public enum Images {
// images
 NetworkConnected("NetworkConnected.png"),
 NetworkDisconnected("NetworkDisconnected.png"),
 Quit("quit.png");
// data
String imagefilename;
// constructor
Images(String name) {
 imagefilename = name;
}
// methods
BufferedImage getImage() {
 try {
 return ImageIO.read(ClassLoader
        .getSystemResourceAsStream(imagefilename));
 }
 catch (IOException e) {
 return null;
 }
}
Icon getIcon() {
 return new ImageIcon(getImage());
}
BufferedImage getImage(int width, int height) {
 return GraphicsUtilities.createThumbnail(
         getImage(), width, height);
}
Icon getIcon(int width, int height) {
 return new ImageIcon(getImage(width, height));
}
}//end enum Images
```

  2. There is a call to getPainter() which sets the background painter for the JXLabel. To learn more about Painters, and the Colors enumeration, [click here](http://developerlife.com/tutorials/?p=140). Here's the code for getPainter():

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

  3. There is a call to changeUIDefaults() which will be explained below.

  4. You can add any component to the JXTaskPane. You can also add Actions. When using Actions, just make sure that the NAME key has a value. If you have a SHORT_DESCRIPTION value, then it will show up as a tooltip. If you have a SMALL_ICON or LARGE_ICON value, then it will show up as an icon in the JXTaskPane entry.

If you want to change the look of the JXTaskPane and JXTaskPane container, then you have to change some UI Defaults that they use to figure out how they should render themselves. There are quite a lot of options that you can set. Here's the implementation of changeUIDefaults():

```java
private void changeUIdefaults() {
 // JXTaskPaneContainer settings (developer defaults)
 /* These are all the properties that can be set 
  * (may change with new version of SwingX)
  * "TaskPaneContainer.useGradient",
  * "TaskPaneContainer.background",
  * "TaskPaneContainer.backgroundGradientStart",
  * "TaskPaneContainer.backgroundGradientEnd",
  * etc.
  */
 // setting taskpanecontainer defaults
 UIManager.put("TaskPaneContainer.useGradient", 
               Boolean.FALSE);
 UIManager.put("TaskPaneContainer.background", 
               Colors.LightGray.color(0.5f));
 // setting taskpane defaults
 UIManager.put("TaskPane.font", 
               new FontUIResource(
                       new Font("Verdana", Font.BOLD, 16)));
 UIManager.put("TaskPane.titleBackgroundGradientStart", 
               Colors.White.color());
 UIManager.put("TaskPane.titleBackgroundGradientEnd", 
               Colors.LightBlue.color());
}
```

As you can see from this code, you can set 2 gradient colors for the JXTaskPane/JXTaskPaneContainer to paint the background. You have to set the "useGradient" value to "Boolean.TRUE". and you have to specify the "backgroundGradientStart" and "backgroundGradientEnd" values, which are both colors. Alternatively, you can set "useGradient" to false, and just use a "background" color. The code example shows you both combinations:

  1. The JXTaskPaneContainer doesn't use a gradient fill, it uses a single background color (LightGray 50% transparent).

  2. The JXTaskPane uses a gradient fill (vertical fill), and it's 2 stops are: White to LightBlue.

Here's the complete listing for the TaskPanelExample1.java:

 
```java
import org.jdesktop.swingx.*;
import org.jdesktop.swingx.painter.*;
import javax.swing.*;
import javax.swing.plaf.*;
import java.awt.*;
import java.awt.event.*;
/**
 * TaskPaneExample1
 *
 * @author Nazmul Idris
 * @version 1.0
 * @since Jan 28, 2008, 12:49:01 PM
 */
public class TaskPaneExample1 {
/** simple main driver for this class */
public static void main(String[] args) {
  SwingUtilities.invokeLater(new Runnable() {
    public void run() {
      new TaskPaneExample1();
    }
  });
}
/** creates a JFrame and calls {@link #doInit} to 
* create a JXPanel and adds the panel to this frame. */
public TaskPaneExample1() {
  JFrame frame = new JFrame("TaskPane Example 1");
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
  // create a label
  final JXLabel label = new JXLabel();
  label.setFont(new Font("Segoe UI", Font.BOLD, 14));
  label.setText("task pane item 1 : a label");
  label.setIcon(
          Images.NetworkDisconnected.getIcon(32, 32));
  label.setHorizontalAlignment(JXLabel.LEFT);
  label.setBackgroundPainter(getPainter());
  // tweak with the UI defaults for the taskpane and 
  // taskpanecontainer
  changeUIdefaults();
  // create a taskpanecontainer
  JXTaskPaneContainer taskpanecontainer = 
        new JXTaskPaneContainer();
  // create a taskpane, and set it's title and icon
  JXTaskPane taskpane = new JXTaskPane();
  taskpane.setTitle("My Tasks");
  taskpane.setIcon(Images.Quit.getIcon(24, 24));
  // add various actions and components to the taskpane
  taskpane.add(label);
  taskpane.add(new AbstractAction() {
    {
      putValue(Action.NAME, 
            "task pane item 2 : an action");
      putValue(Action.SHORT_DESCRIPTION, 
            "perform an action");
      putValue(Action.SMALL_ICON, 
            Images.NetworkConnected.getIcon(32, 32));
    }
    public void actionPerformed(ActionEvent e) {
      label.setText("an action performed");
    }
  });
  // add the task pane to the taskpanecontainer
  taskpanecontainer.add(taskpane);
  // set the transparency of the JXPanel to 
  // 50% transparent
  panel.setAlpha(0.7f);
  panel.add(taskpanecontainer, BorderLayout.CENTER);
  panel.setPreferredSize(new Dimension(250, 200));
  return panel;
}
private void changeUIdefaults() {
  // JXTaskPaneContainer settings (developer defaults)
  /* These are all the properties that can be set 
   * (may change with new version of SwingX)
   * "TaskPaneContainer.useGradient",
   * "TaskPaneContainer.background",
   * "TaskPaneContainer.backgroundGradientStart",
   * "TaskPaneContainer.backgroundGradientEnd",
   * etc.
   */
  // setting taskpanecontainer defaults
  UIManager.put("TaskPaneContainer.useGradient", 
        Boolean.FALSE);
  UIManager.put("TaskPaneContainer.background", 
        Colors.LightGray.color(0.5f));
  // setting taskpane defaults
  UIManager.put("TaskPane.font", 
        new FontUIResource(new Font("Verdana", Font.BOLD, 16)));
  UIManager.put("TaskPane.titleBackgroundGradientStart", 
        Colors.White.color());
  UIManager.put("TaskPane.titleBackgroundGradientEnd", 
        Colors.LightBlue.color());
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
}//end class TaskPaneExample1
```

Please note that I've assembled the JXTaskPaneContainer in a JXPanel and I set it's opacity to 70%, making it 30% transparent. This is another cool feature of using SwingX JXPanel, and it's transparency.

## Download project

To download the IDEA projects for this tutorial's source code example, 
[click here]({{'assets/taskpane.zip' | relative_url}}).