---
author: Nazmul Idris
date: 2008-07-29 21:11:53+00:00
excerpt: |
  This tutorial will show you how to use the TableLayout container, which is
  like an HTML table. The UI layout code is done in Java, not XML. A class 
  (LayoutUtils) is provided to make it easier to attach layout params to View objects.
layout: post
title: "Android TableLayout Tutorial"
categories:
  - Android
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [What does stretchable, shrinkable, and collapsible even mean?](#what-does-stretchable-shrinkable-and-collapsible-even-mean)
- [Behavior of rows and columns](#behavior-of-rows-and-columns)
- [What can I do with a TableLayout?](#what-can-i-do-with-a-tablelayout)
- [Example with source code](#example-with-source-code)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

This tutorial covers the
[TableLayout](http://code.google.com/android/reference/android/widget/TableLayout.html) container,
which is like an HTML table. A table can have multiple rows, and each row is a subclass of a
[LinearLayout](http://developerlife.com/tutorials/?p=312). Rows can span columns, just like HTML.
Each cell may contain only 1 View object. The width of a column by default is the width of the
widest component in that column. Note that you aren't able to select any rows/columns/cells in the
TableLayout view; in order to do this you have to use a ListView.

## What does stretchable, shrinkable, and collapsible even mean?

In the API docs you will find the terms "shrinkable", 'stretchable", and "collapsible". I scratched
my head for a long time before coming to understand what the API designers were trying to express.
In my mind, "stretchable" means that something can be collapsed and/or expanded, but they they have
"collapsible" columns, so that doesn't make sense. So here goes:

- Stretchable column means that a column can be expanded to fill extra space left by other columns.
  So stretchable = EXPANDABLE.

- Shrinkable column means that a column can be wrapped to take up less space, so that other columns
  can be displayed in a TableLayout. So shrinkable = WRAPPABLE.

- Collapsed column means that a column is hidden or invisible. So collapsible = INVISIBILITY.

After you translate these strange terms to something that's more Sun Java API friendly, it all
starts to make more sense. The Android SDK is replete with examples of such bizarre naming schemes
(eg, Intent is Event). If Android is a Java API, then why not leverage the API naming conventions
that we are used to from various Java desktop, graphics, and server APIs? Why create new
nomenclatures when there's no need to do so? Similarly, the Android API designers went off the deep
end creating their UI toolkit, which is alien if you're used to any contemporary Java UI toolkits.

## Behavior of rows and columns

Columns can shrink or stretch to accommodate the width of the TableLayout. Shrinkable means that if
a cell in the column takes up a lot of space, then it can be wrapped to make it fit, so that the
other columns show. Stretchable means that if a cell is really narrow, then it can be expanded to
take up enough column width to make it fill the entire table that it's in.

Please note that the children of a TableLayout cannot specify their width - which is always
FILL_PARENT. However, the height can be defined by a child, which defaults to WRAP_CONTENT. If the
child is a [TableRow](http://code.google.com/android/reference/android/widget/TableRow.html), then
the height is always WRAP_CONTENT. So if you use TableLayout with TableRows you can't really can't
set the width/height (width=FILL_PARENT, and height=WRAP_CONTENT). By the way, a TableRow is just a
subclass of LinearLayout. What you can do is specify the behavior of the column to shrink and/or
stretch or not. You can also hide a column by calling setColumnCollapsed on a TableLayout, and
passing it the column index. All column indices start at 0, and you can have empty columns.

Here's the
[API docs on TableLayout](http://code.google.com/android/reference/android/widget/TableLayout.html)
from the Android SDK.

## What can I do with a TableLayout?

Here's a list of things that you can do:

1. You can insert a View object into a TableLayout (not a TableRow) and set it's bgcolor and height,
   and it acts as a spacer that spans the row. The attributes are layout_height and background.

2. You can insert a TextView object into a TableLayout (not a TableRow) and it will span the row.

3. To make a column expandable (to fill up any existing empty space from other columns), use
   setColumnStretchable to mark it stretchable.

4. To make a column wrappable (to reduce it's width and wrap it's content if other columns in the
   table are taking too much space and pushing some columns off the screen), use setColumnShrinkable
   to mark it shrinkable.

5. To put a View in a specific cell, use
   [TableRow.LayoutParams](http://code.google.com/android/reference/android/widget/TableRow.LayoutParams.html)
   and specify a column id (they start at 0).

6. To span a View across a bunch of columns, there's is no programmatic way to do this! Google left
   out a public constructor for
   [TableRow.LayoutParams](http://code.google.com/android/reference/android/widget/TableRow.LayoutParams.html)
   that allows you to specify the column span attribute
   ([layout_span](http://code.google.com/android/reference/android/widget/TableRow.LayoutParams.html#attr_android:layout_span)).
   It might be possible to directly set the span field (which is a public int) in the layout object.
   Just specify the number of columns that you want this View object to span.

7. To hide a column, you can collapse it any time. You can also make some columns start up as
   collapsed.

8. Since a TableRow is essentially a LinearLayout, you can set it's gravity attribute with
   setGravity(Gravity.\*). You can also set the gravity of the Views objects inside the row.

## Example with source code

In the following example, I will show you how to create a table with 2 columns (1 of which is
expandable). I will add a spacer row after each row that has content. These spacers will span the 2
columns. Finally, I will add a button that spans 2 columns at the very end. I will then wrap all of
this into a scroll pane (ScrollView) so that you can scroll up/down if the table is longer than the
displayable screen.

Here's the code for an Activity that simply creates a TableLayout, adds it to a ScrollView and
displays it:

```java
@Override protected void onCreate(Bundle bundle) {
  super.onCreate(bundle);

  setTheme(R.style.Theme_Translucent);

  // wrap the table in a scrollpane
  scrollPane = new ScrollView(this);
  LayoutUtils.Layout.WidthFill_HeightWrap.applyViewGroupParams(scrollPane);

  scrollPane.addView(PanelBuilder.createWidgetPanel(this));
  setContentView(scrollPane);
}
```

One thing you should note in all the code is that any time you create a View, you have to add layout
params to it, to let it's container know how to lay it out. So you have to know which container you
are adding View objects to, and create the layout params appropriately. This can be a little
confusing at first, but think about Java SE layout managers, and defining constraints to layout a
JComponent, in line in the method call used to add that JComponent to the Container. If the API
allowed the constraint to be passed as a parameter to the method used to add the View to the
ViewGroup, then it would be easier to keep everything straight. More criticism of the Android API
from me :) .

I got so sick and tired of typing out the code to attach layout parameters to each View, that I
created a class to make it simple to do this. It's called LayoutoUtils, and it has an enum (Layout)
that represent width and height layout constraints - there are a total of 4 combinations of
height/width settings that are listed. Methods are provided that attach layout params for
TableLayout, LinearLayout, and ViewGroup. Here's a listing of this class (you can see how to use it
above):

```java
public class LayoutUtils {

public enum Layout {
  WidthFill_HeightFill,
  WidthWrap_HeightWrap,
  WidthWrap_HeightFill,
  WidthFill_HeightWrap;

  public void applyViewGroupParams(View component) {
    applyViewGroupLayoutParamsTo(this, component);
  }

  public void applyLinearLayoutParams(View linearlayout) {
    applyLinearLayoutParamsTo(this, linearlayout);
  }

  public void applyTableRowParams(View cell) {
    applyTableRowLayoutParamsTo(this, cell);
  }

  public void applyTableLayoutParams(View row) {
    applyTableLayoutParamsTo(this, row);
  }

}

private static void applyLinearLayoutParamsTo(
        Layout layout, View view) {

  switch (layout) {
    case WidthFill_HeightFill:
      view.setLayoutParams(new LinearLayout.LayoutParams(
          LinearLayout.LayoutParams.FILL_PARENT,
          LinearLayout.LayoutParams.FILL_PARENT
      ));
      break;
    case WidthFill_HeightWrap:
      view.setLayoutParams(new LinearLayout.LayoutParams(
          LinearLayout.LayoutParams.FILL_PARENT,
          LinearLayout.LayoutParams.WRAP_CONTENT
      ));
      break;
    case WidthWrap_HeightFill:
      view.setLayoutParams(new LinearLayout.LayoutParams(
          LinearLayout.LayoutParams.WRAP_CONTENT,
          LinearLayout.LayoutParams.FILL_PARENT
      ));
      break;
    case WidthWrap_HeightWrap:
      view.setLayoutParams(new LinearLayout.LayoutParams(
          LinearLayout.LayoutParams.WRAP_CONTENT,
          LinearLayout.LayoutParams.WRAP_CONTENT
      ));
      break;
  }

}

private static void applyViewGroupLayoutParamsTo(
        Layout layout, View view) {

  switch (layout) {
    case WidthFill_HeightFill:
      view.setLayoutParams(new ViewGroup.LayoutParams(
          ViewGroup.LayoutParams.FILL_PARENT,
          ViewGroup.LayoutParams.FILL_PARENT
      ));
      break;
    case WidthFill_HeightWrap:
      view.setLayoutParams(new ViewGroup.LayoutParams(
          ViewGroup.LayoutParams.FILL_PARENT,
          ViewGroup.LayoutParams.WRAP_CONTENT
      ));
      break;
    case WidthWrap_HeightFill:
      view.setLayoutParams(new ViewGroup.LayoutParams(
          ViewGroup.LayoutParams.WRAP_CONTENT,
          ViewGroup.LayoutParams.FILL_PARENT
      ));
      break;
    case WidthWrap_HeightWrap:
      view.setLayoutParams(new ViewGroup.LayoutParams(
          ViewGroup.LayoutParams.WRAP_CONTENT,
          ViewGroup.LayoutParams.WRAP_CONTENT
      ));
      break;
  }

}

private static void applyTableRowLayoutParamsTo(
        Layout layout, View view) {

  switch (layout) {
    case WidthFill_HeightFill:
      view.setLayoutParams(new TableRow.LayoutParams(
          TableRow.LayoutParams.FILL_PARENT,
          TableRow.LayoutParams.FILL_PARENT
      ));
      break;
    case WidthFill_HeightWrap:
      view.setLayoutParams(new TableRow.LayoutParams(
          TableRow.LayoutParams.FILL_PARENT,
          TableRow.LayoutParams.WRAP_CONTENT
      ));
      break;
    case WidthWrap_HeightFill:
      view.setLayoutParams(new TableRow.LayoutParams(
          TableRow.LayoutParams.WRAP_CONTENT,
          TableRow.LayoutParams.FILL_PARENT
      ));
      break;
    case WidthWrap_HeightWrap:
      view.setLayoutParams(new TableRow.LayoutParams(
          TableRow.LayoutParams.WRAP_CONTENT,
          TableRow.LayoutParams.WRAP_CONTENT
      ));
      break;
  }

}

private static void applyTableLayoutParamsTo(
        Layout layout, View view) {

  switch (layout) {
    case WidthFill_HeightFill:
      view.setLayoutParams(new TableLayout.LayoutParams(
          TableLayout.LayoutParams.FILL_PARENT,
          TableLayout.LayoutParams.FILL_PARENT
      ));
      break;
    case WidthFill_HeightWrap:
      view.setLayoutParams(new TableLayout.LayoutParams(
          TableLayout.LayoutParams.FILL_PARENT,
          TableLayout.LayoutParams.WRAP_CONTENT
      ));
      break;
    case WidthWrap_HeightFill:
      view.setLayoutParams(new TableLayout.LayoutParams(
          TableLayout.LayoutParams.WRAP_CONTENT,
          TableLayout.LayoutParams.FILL_PARENT
      ));
      break;
    case WidthWrap_HeightWrap:
      view.setLayoutParams(new TableLayout.LayoutParams(
          TableLayout.LayoutParams.WRAP_CONTENT,
          TableLayout.LayoutParams.WRAP_CONTENT
      ));
      break;
  }

}

}//end class LayoutUtils
```

You can use the LayoutUtils class in any project where you have to attach layout params to a View
object.

Here's the code that creates the TableLayout object:

```java
public static View createWidgetPanel(TableActivity activity) {

  TableLayout table = new TableLayout(activity);
  LayoutUtils.Layout.WidthFill_HeightFill.applyViewGroupParams(table);

  // set which column is expandable/can grow
  table.setColumnStretchable(1, true);

  // apply layout animation
  AnimUtils.setLayoutAnim_slideupfrombottom(table, activity);

  ArrayList<View> rowList = new ArrayList<View>();

  // create a row with icon/text
  rowList.add(
          createRow(com.sonar.R.drawable.tagflag1,
                    "Row 1, some text",
                    activity));

  // create a spacer
  rowList.add(createSpacer(activity));

  // create a row with icon/text
  rowList.add(
          createRow(com.sonar.R.drawable.tagflag2,
                    "Row 2, some more text",
                    activity));

  // create a spacer
  rowList.add(createSpacer(activity));

  // create a row with icon/text
  rowList.add(
          createRow(com.sonar.R.drawable.tagflagbutton,
                    "Row 3, even more text",
                    activity));

  // create a spacer
  rowList.add(createSpacer(activity));

  // create a buttom on the bottom
  rowList.add(createButton(activity));

  // add all the rows to the table
  {
    for (View row : rowList) {
      LayoutUtils.Layout.WidthWrap_HeightWrap
            .applyTableLayoutParams(row);
      row.setPadding(RowPadding, RowPadding, RowPadding, RowPadding);
//      row.setBackgroundColor(Color.argb(200, 51, 51, 51));
      table.addView(row);
    }
  }

  return table;

}
```

The R.drawable.\* items are just PNG files that I put in my /res/drawable/ folder of my Android
project.

Finally, here are the methods that are used to create the spacer, a button, and table rows (with 2
cells, an image and some text):

```java
private static View createButton(final TableActivity activity) {

//  Button b = new Button(activity);

//  this code doesnt use the id to load the button
//  (since there's only one)
//  Button b = (Button) activity.getViewInflate().inflate(
//          R.layout.buttons, null, null);

  // this code uses the id to find the button
  View v = activity.getViewInflate().inflate(
          R.layout.buttons, null, null);
  Button b = (Button) v.findViewById(R.id.button_small_left);

//  the following doesnt work since the layout wasnt
//  loaded in onCreate by setContentView(id)
//  Button b = (Button) activity.findViewById(
//          R.id.button_small_left);

//  b.setText("Press to close");

  b.setOnClickListener(new View.OnClickListener() {
    public void onClick(View view) {
      activity.runFadeOutAnimationAndFinish();
    }
  });

  return b;
}

private static View createSpacer(Context activity) {
  View spacer = new View(activity);

  spacer.setPreferredHeight(5);
  spacer.setBackgroundColor(Color.argb(200, 226, 226, 226));

  return spacer;
}

public static TableRow createRow(int image,
                                 String txt,
                                 Context activity) {
  TableRow row = new TableRow(activity);

  ImageView icon = new ImageView(activity);
  icon.setAdjustViewBounds(true);
  icon.setScaleType(ImageView.ScaleType.FIT_CENTER);
  icon.setMaxHeight(IconSize);
  icon.setMaxWidth(IconSize);
  icon.setImageResource(image);
  icon.setPadding(
          RowPadding, RowPadding, RowPadding, RowPadding);
  LayoutUtils.Layout.WidthWrap_HeightWrap
          .applyTableRowParams(icon);

  TextView text = new TextView(activity);
  text.setText(txt);
  text.setPadding(
          RowPadding, RowPadding, RowPadding, RowPadding);
  LayoutUtils.Layout.WidthWrap_HeightWrap
          .applyTableRowParams(text);

  row.addView(icon);
  row.addView(text);

  return row;
}
```

You can download LayoutUtils and other helpful classes from
[AndroidUtils]({{'assets/androidutils.zip' | relative_url}}).
