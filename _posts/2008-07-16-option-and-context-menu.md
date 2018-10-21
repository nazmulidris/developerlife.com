---
author: Nazmul Idris
date: 2008-07-16 22:13:08+00:00
excerpt: |
  This tutorial will show you how to create options menu (hooks into the MENU
  button) and context menu (press and hold a component).
layout: post
title: "Android Option and Context menu Tutorial"
categories:
- Android
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [Menu item creation code](#menu-item-creation-code)
- [Option Menu - MENU button](#option-menu---menu-button)
- [Context Menu - Press and hold](#context-menu---press-and-hold)
- [Responding to menu selection](#responding-to-menu-selection)
- [Using images in menus](#using-images-in-menus)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

This tutorial will show you how to create options menu (hooks into the MENU button) and context menu (press and hold a component). You can add pictures and text to menu items that get added to both context and options menus. What's the difference between these 2 types of menus?

  1. Think of the option menu as a global menu, that's activated when the MENU button is pressed in an Activity.

  2. Think of the context menu as a right-click-menu on a component; just press and hold (with the enter key on the emulator D-Pad) and this context menu will get activated.

In the example I will build in this tutorial, I will create a set of Menu.Items that are the same for Option and Context menu. The code to create these menu items and respond to user selection of these items is the same in my example.

## Menu item creation code

Here's the code to create some menu items, given a Menu. Whether you are using context or option menu items, this code is the same:

```java
// menu item constants
public static final int Menu1 = Menu.FIRST + 1;
public static final int Menu2 = Menu.FIRST + 2;
public static final int Menu3 = Menu.FIRST + 3;
public static final int Menu4 = Menu.FIRST + 4;

/** create the menu items */
public void populateMenu(Menu menu) {

  // enable keyb shortcuts, qwerty mode = true means 
  // only show keyb shortcuts (not numeric) and vice versa
  // these only show up in context menu, not options menu
  menu.setQwertyMode(true);

  Menu.Item item1 = menu.add(0, Menu1, "MenuOption1");
  {
    item1.setAlphabeticShortcut('a');
    item1.setIcon(AppUtils.resizeImage(
            this, R.drawable.tagfavorite1, 32, 32));
  }

  Menu.Item item2 = menu.add(0, Menu2, "MenuOption2");
  {
    item2.setAlphabeticShortcut('b');
    item2.setIcon(AppUtils.resizeImage(
            this, R.drawable.tagfavorite2, 32, 32));
  }

  Menu.Item item3 = menu.add(0, Menu3, "MenuOption3");
  {
    item3.setNumericShortcut('1');
    item3.setIcon(AppUtils.resizeImage(
            this, R.drawable.tagfavorite3, 32, 32));
  }

  Menu.Item item4 = menu.add(0, Menu4, "MenuOption4");
  {
    item4.setNumericShortcut('2');
    item4.setIcon(AppUtils.resizeImage(
            this, R.drawable.tagnote3, 32, 32));
  }

}
```

Here are some notes on the code:

  1. The menu is created by Android and passed to you; you have to add whatever menu items you want to this object, you don't actually create the Menu.

  2. You can have keyboard accelerators/shortcuts bound to menu items; you have to pick whether you want alpha or numeric accelerators, you can't have both. The code to set alpha accelerators is Menu.setQwertyMode(true). Just set it to false, if you only want numeric accelerators.

  3. You can pass an image and/or some text to create a menu item. By default, if you use a preloaded Drawable image, then it will be shown in it's full size. In the code above, I'm actually resizing the image so that it will be 32x32 pixels in size. The code for can be found at the end of this tutorial.

  4. You must have a correlation Id bound to each menu item. This Id will be used by the handler (that you will bind to in the next sections) that will respond to these menu items being selected. The correlation Ids I'm using are int constants called: Menu1, Menu2, Menu3, and Menu4. Instead of picking random integers, it's a good idea to add an offset value to Menu.FIRST so that these correlation Ids don't conflict with default Android menu items.

  5. There is something called a group id that you can assign a menu item as well - these are only relevant if you want to group together certain menu items. In this example, I've used "0" as the group Id.
\
Once the menu has been populated with menu items, they have to be added to an Activity. This is where the code for hooking up the menu items to a Context menu differs from hooking them up to an Option menu.

## Option Menu - MENU button

The first step in hooking up your menus to an Activity is to create them (which is already shown above). The 2nd step is to hook into the Activity's menu creation methods to call your code, which creates these menu items:

```java
// Menu button - option menu

/** hook into menu button for activity */
@Override public boolean onCreateOptionsMenu(Menu menu) {
  populateMenu(menu);
  return super.onCreateOptionsMenu(menu);
}

/** when menu button option selected */
@Override public boolean onOptionsItemSelected(Menu.Item item) {
  return applyMenuChoice(item) || super.onOptionsItemSelected(item);
}
```

Here are some notes on this code:

  1. The menu is created by Android and passed to you; you have to add whatever menu items you want to this object, you don't actually create the Menu. This allows Android to populate the Menu with system defined menu items (in case you call super.onCreateOptionsMenu(menu) for the Option menu).

  2. If you add more than 5 menu items to the given menu, then the 6th option won't not be displayed in the grid (like they are in the screenshot above). A "More" button will be shown and when you select this a list view will be shown with all your menu items. In the grid view, the accelerators are not shown. The grid view only takes up the bottom portion of the Activity/screen. The list view takes up the full screen and shows the keyboard accelerators.

  3. The code to respond to menu item selection is shown below (this is common to the Option and Context menu).

## Context Menu - Press and hold

The first step in hooking up your menus to an Activity is to create them (which is already shown above). The 2nd step is to hook into the Activity's menu creation methods to call your code, which creates these menu items.

Here's the code to bind the menu items to a ListView component, so when you press-and-hold this component, it will pop up a context menu:

```java
@Override protected void onCreate(Bundle bundle) {

  // wire up the listview to have a press-hold/context menu
  View listview = ...
  listview.setOnPopulateContextMenuListener(this);

}

/** press-hold/context menu */
public void onPopulateContextMenu(ContextMenu menu, 
                                  View view, 
                                  Object o) {
  populateMenu(menu);
}

/** when press-hold option selected */
@Override public boolean onContextItemSelected(Menu.Item item) {
  return applyMenuChoice(item) || super.onContextItemSelected(item);
}
```

Here are some notes on this code:

  1. Just like with the Option menu, the Menu object is pre-created for you and passed to you.

  2. Unlike the Context menu example, you don't override a method in your Activity class, you have to call setOnPopulateContextMenuListener(...) on the component you want to bind the context menu with.

  3. This onPopulateContextMenu(...) method is called every time the user performs a press-and-hold operation on the ListView. This isn't just created once (like the Option menu).

## Responding to menu selection

Here's the code to respond to the Menu item selection. Whether you are using a Context or Option menu, this code is the same:

```java
/** respond to menu item selection */
public boolean applyMenuChoice(Menu.Item item) {
  switch (item.getId()) {
    case Menu1:
      AppUtils.showToastShort(this, "MenuOption1 is selected");
      return true;
    case Menu2:
      AppUtils.showToastShort(this, "MenuOption2 is selected");
      return true;
    case Menu3:
      AppUtils.showToastShort(this, "MenuOption3 is selected");
      return true;
    case Menu4:
      AppUtils.showToastShort(this, "MenuOption4 is selected");
      return true;
  }
  return false;
}
```

Here are some notes on the code:

  1. The code to respond to menu selection can be shared between Context and Option menu items, as in this example.

  2. The correlation Id used to identify which Menu.Item was selected are constant integers: Menu1, Menu2, Menu3, and Menu4, which are declared in previous sections.

  3. AppUtils.showToastShort() simply calls Toast.makeText() to display a short text message on the screen.

## Using images in menus

You can use drawable resources to create a menu item with. However, if these images are too big, they might not look right in a small Option or Context menu display. Here's code that you can use to resize Drawable resources/images to whatever size you want before assigning them to a menu item:

```java
public static Drawable resizeImage(Context ctx, 
                                   int resId, 
                                   int w, 
                                   int h) {

  // load the origial Bitmap
  Bitmap BitmapOrg = BitmapFactory
        .decodeResource(ctx.getResources(), resId);

  int width = BitmapOrg.width();
  int height = BitmapOrg.height();
  int newWidth = w;
  int newHeight = h;

  // calculate the scale
  float scaleWidth = ((float) newWidth) / width;
  float scaleHeight = ((float) newHeight) / height;

  // create a matrix for the manipulation
  Matrix matrix = new Matrix();
  // resize the Bitmap
  matrix.postScale(scaleWidth, scaleHeight);
  // if you want to rotate the Bitmap
  // matrix.postRotate(45);

  // recreate the new Bitmap
  Bitmap resizedBitmap = Bitmap.createBitmap(
          BitmapOrg, 0, 0, width, height, matrix, true);

  // make a Drawable from Bitmap to allow to set the Bitmap
  // to the ImageView, ImageButton or what ever
  return new BitmapDrawable(resizedBitmap);

}
```