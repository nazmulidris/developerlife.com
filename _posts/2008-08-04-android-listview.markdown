---
author: Nazmul Idris
date: 2008-08-04 19:55:55+00:00
excerpt: |
  This tutorial will show you how to use ListView to display selectable lists
  of non trivial data, using complex cell renderers. The ListView is a selectable
  list. You can attach a variety of data models to it and load different 
  display layouts (cell renderers). You can create your own model and cell renderer. 
  This model-view combo is called an Adapter. In this tutorial, I will 
  show you how to extend create your own Adapter from scratch, and create 
  your own cell renderers from scratch as well.
layout: post
title: "Android ListView and custom adapter Tutorial"
categories:
- Android
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [What is a ListView?](#what-is-a-listview)
- [Be careful of the following](#be-careful-of-the-following)
- [Example with source code](#example-with-source-code)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

This tutorial will show you how to use ListView to display selectable lists of non trivial data, using complex cell renderers. The ListView is a selectable list. You can attach a variety of data models to it and load different display layouts (cell renderers). You can create your own model and cell renderer. This model-view combo is called an Adapter. In this tutorial, I will show you how to extend create your own Adapter from scratch, and create your own cell renderers from scratch as well.

## What is a ListView?

What's the difference between a TableLayout and a ListView? Items in a TableLayout are not 'selectable' (unless they are buttons or text areas that support keyboard focus), however, each row of a ListView can be selected. It's just like a Swing JList. You can attach item selection listeners to a ListView to know when the user focuses in on a particular row of a list. The biggest difference between a Swing JList and a ListView is that the model view controller separation in JList is not there in ListView. A ListView's adapter, holds all the list's underlying data as well as the Views necessary to render each row of the ListView. However, there are many similarities with JList, for example, when your underlying data model changes, you have to fire an event to notify the adapter's listeners that the underlying data has changed, and the views should be refreshed. The ListView does not need to be added to a ScrollView since it automatically supports scrolling.

## Be careful of the following

You have to be careful between touch mode and D-pad mode input into a ListView, [read this for more information](http://developer.android.com/resources/articles/touch-mode.html). This affects the way your ListView will respond to user input by touch or by D-Pad movement, the gist of it is use the [onClickListener](http://developer.android.com/reference/android/widget/AdapterView.html#setOnItemClickListener(android.widget.AdapterView.OnItemClickListener))to respond to user input, which will work for D-Pad as well as touch input events.

You also have to be careful about setting background colors and 9patch images on a ListView, [read this for more information](http://developer.android.com/resources/articles/listview-backgrounds.html).

## Example with source code

In the following example, I will show you how to create a ListView that uses a custom adapter to display weather data. The underlying weather data is stored in a Hashtable of Hashtables. At the top level, the key is a String that represents the zipcode. The Hashtable value for this key (zipcode) contains the current temperature, humidity, and an icon that represents the weather conditions. These are all strings as well. The ListView and adapter work together to display a list of these weather conditions for various zip codes. To render this weather data, the list cell renderer uses a TableLayout to display these weather conditions - each cell is composed of a 2 row table: the first row has 2 cells - icon and temperature, the second row has 1 cell - the humidity.

The following Activity creates a ListView (with this weather data adapter) and displays it:

```java
@Override protected void onCreate(Bundle bundle) {

  super.onCreate(bundle);

  // window features - must be set prior to calling setContentView...
  requestWindowFeature(Window.FEATURE_NO_TITLE);

  setContentView(PanelBuilder.createList(this));

}
```

PanelBuilder is a static class with helper methods to assemble the ListView and it's underlying adapter:

```java
public static View createList(Activity activity) {

  // create the ui components
  LinearLayout mainpanel = new LinearLayout(activity);
  ListView listview = new ListView(activity);

  // setup the mainpanel
  {
    // apply view group params for the activity's root pane
    LayoutUtils.Layout.WidthFill_HeightFill.applyViewGroupParams(mainpanel);
    // set animation layout on the mainpanel
    AnimUtils.setLayoutAnim_slideupfrombottom(mainpanel, activity);
  }

  // setup the listview and add to the mainpanel
  {
    LayoutUtils.Layout.WidthFill_HeightFill.applyLinearLayoutParams(listview);

    bindListViewToAdapter(activity, listview);

    AnimUtils.setLayoutAnim_slidedownfromtop(listview, activity);

    mainpanel.addView(listview);
  }

  // return the mainpanel
  return mainpanel;

}
```

Some notes on the code:

  1. LayoutUtlis is used to quickly attach LayoutParams to the LinearLayout and ListView widgets.

  2. AnimUtils is used to apply layout animation sequences to the ViewGroups - mainpanel and listview.

  3. The ListView is embedded into a LinearLayout and then returned to the caller, to be placed on the Activity.

AnimUtils is a utility class that I’ve written 
([you can get it in AndroidUtils.zip]({{'/assets/androidutils.zip' | relative_url}})) 
to make it easier to assign layout animations on Viewgroup objects/containers (LinearLayout, TableLayout, ListView, etc). It can be used to assign different animation sequences to these ViewGroups very easily. With Android’s animation framework, it’s possible to enable layout animation, without you having to write the code.

Let's look at the implementation of `bindListViewToAdapter()` next:

```java
/** create the list data, and bind a custom adapter to the listview */
private static void bindListViewToAdapter(Activity ctx, ListView listview) {

  final WeatherDataListAdapter listModelView = 
        new WeatherDataListAdapter(ctx, listview);

  // bind a selection listener to the view
  listview.setOnItemSelectedListener(
          new AdapterView.OnItemSelectedListener() {
                public void onItemSelected(AdapterView parentView, 
                                           View childView, 
                                           int position, 
                                           long id) {
            listModelView.setSelected(position);
          }
    public void onNothingSelected(AdapterView parentView) {
      listModelView.setSelected(-1);
    }
  });

}
```

Some notes on the code:

  1. The ListView adapter (model + cell renderer) is called WeatherDataListAdapter, and it's created here with some default data and then attached to the ListView already created above.

  2. A selection listener is attached to the ListView so that when the user traverses through the list, the adapter (model + partial view) can respond by updating the UI. This selection event triggers a model change event that causes the UI to be updated with the new selection. My cell renderer implementation renders a selected sell differently than an unselected cell, which is why this is even necessary. If your renderer doesn't care about selection state to render the current row, then this step is not necessary.

Finally, let's look at the WeatherDataListAdapter class, which extends [BaseAdapter](http://code.google.com/android/reference/android/widget/BaseAdapter.html). The BaseAdapter class is a good skeleton class to extend in order to provide an implementation of your ListView adapter. The BaseAdapter doesn't make any assumptions about what your data looks like, but it provides abstract methods for you to override to allow the ListView to traverse your data model.

```java
public class WeatherDataListAdapter extends BaseAdapter {

// data members
/** holds all the weather data */
private Hashtable<String, Hashtable<String, String>> _data = 
        new Hashtable<String, Hashtable<String, String>>();

/** holds the currently selected position */
private int _selectedIndex;
private Activity _context;

// constructor

/**
 * create the model-view object that will control the listview
 *
 * @param context  activity that creates this thing
 * @param listview bind to this listview
 */
public WeatherDataListAdapter(final Activity context, 
                              ListView listview) {

  // save the activity/context ref
  _context = context;

  // bind this model (and cell renderer) to the listview
  listview.setAdapter(this);

  // load some data into the model
  {
    String zip = "12345";
    Hashtable<String, String> wd = 
            new Hashtable<String, String>();
    wd.put("temperature","30F");
    wd.put("humidity","50%");
    wd.put("icon","12");
    _data.put(zip, weatherdata);
  }

  Log.i(getClass().getSimpleName(), 
        "loading data set, creating list model, and binding to listview");

}

// implement ListAdapter - how big is the underlying list data, 
// and how to iterate it... the underlying data is a Map of Maps, 
// so this really reflects the keyset of the enclosing Map...

/** returns all the items in the {@link #_data} table */
public int getCount() {
  return _data.size();
}

/** 
* returns the key for the table, not the value (which 
* is another table) 
*/
public Object getItem(int i) {
  Object retval = _data.keySet().toArray()[i];
  Log.i(getClass().getSimpleName(), "getItem(" + i + ") = " + retval);
  return retval;
}

/** 
* returns the unique id for the given index, which is 
* just the index 
*/
public long getItemId(int i) {
  return i;
}
```

Notes on the code:

  1. The ListView.setAdapter() gets called to bind it to this weather data list adapter.

  2. In the constructor, some dummy data is created and loaded into the model. If you want to add data once the list has been constructed, you have to get the data from some where, and then call notifyDataSetChanged() on the adapter so that it can notify it's ListView that it's time to refresh the view. Make sure to call this notify method in the UI Thread using UIThreadUtilities.runOnUIThread(..) method. If you're getting this data from a service or another background thread, you want to make sure and put the model update event in the UI thread so that there won't be any UI hiccups.

  3. The getCount(), getItem(int) and getItemId(int) are 3 methods that allow the ListView to get visibility into your underlying data structure. These 3 accessor methods let the ListView know how big your list is, and how to access an Object that represents a row of data from your underlying model, given the selection index. These 3 methods provide a way for an index to be dereferenced into a row of data, which will then be renderered by the cell renderer. Just make sure when you're writing your cell renderer that it matches up with these accessors.

Before we jump into the cell renderer code, let's look at list selection methods that we have:

```java
// handle list selection

/**
 * called when item in listview is selected... 
 * fires a model changed event...
 *
 * @param index index of item selected in listview. 
 *              if -1 then it's unselected.
 */
public void setSelected(int index) {

  if (index == -1) {
    // unselected
  }
  else {
    // selected index...
  }

  _selectedIndex = index;

  // notify the model that the data has changed, 
  // need to update the view
  notifyDataSetChanged();

  Log.i(getClass().getSimpleName(),
        "updating _selectionIndex with index and " 
        + "firing model-change-event: index=" + index);

}
```

Notes on the code:

  1. This list selection code is tied to the selection listener that's attached to the ListView in some of the code from previous paragraphs. The reason to have the selection update the list model is because my cell renderer displays different information depending on whether a cell is currently selected or not.

  2. The notifyDataSetChanged() method is called in the UI thread, in this case, since the setSelected(int) method gets called from a listener that's attached to the ListView.

Finally, here's the cell renderer code:

```java
// custom cell renderer

@Override public View getView(int index,
                              View cellRenderer,
                              ViewGroup parent)
{

  CellRendererView cellRendererView = null;

  if (cellRenderer == null) {
    // create the cell renderer
    Log.i(getClass().getSimpleName(), 
            "creating a CellRendererView object");
    cellRendererView = new CellRendererView();
  }
  else {
    cellRendererView = (CellRendererView) cellRenderer;
  }

  // update the cell renderer, and handle selection state
  cellRendererView.display(index,
                           _selectedIndex == index);

  return cellRendererView;

}
```

Notes on the code:

  1. When you override this method, you are telling the ListView that you want to use your own widget/View to render a row of data in your underlying data model.

  2. If the cellRenderer parameter is null, that just means that it's time to create a new "rubber stamp" object to render each row. This object is then returned at the end of this method (for use in subsequent method calls to display different rows).

Here's the CellRendererView class, which itself is just a TableLayout 
container that renders the weather data Hashtable:

```java
/** 
* this class is responsible for rendering the data in the 
* model, given the selection state 
*/
private class CellRendererView extends TableLayout {

  // ui stuff
  private TextView _lblName;
  private ImageView _lblIcon;
  private TextView _lblDescription;

  public CellRendererView() {

    super(_context);

    _createUI();

  }

  /** create the ui components */
  private void _createUI() {

    // make the 2nd col growable/wrappable
    setColumnShrinkable(1, true);
    setColumnStretchable(1, true);

    // set the padding
    setPadding(10, 10, 10, 10);

    // single row that holds icon/flag & name
    TableRow row = new TableRow(_context);
    LayoutUtils.Layout.WidthFill_HeightWrap
            .applyTableLayoutParams(row);

    // fill the first row with: icon/flag, name
    {
      _lblName = new TextView(_context);
      LayoutUtils.Layout.WidthWrap_HeightWrap
            .applyTableRowParams(_lblName);
      _lblName.setPadding(10, 10, 10, 10);

      _lblIcon = AppUtils.createImageView(_context, -1, -1, -1);
      LayoutUtils.Layout.WidthWrap_HeightWrap
            .applyTableRowParams(_lblIcon);
      _lblIcon.setPadding(10, 10, 10, 10);

      row.addView(_lblIcon);
      row.addView(_lblName);
    }

    // create the 2nd row with: description
    {
      _lblDescription = new TextView(_context);
      LayoutUtils.Layout.WidthFill_HeightWrap
            .applyTableLayoutParams(_lblDescription);
      _lblDescription.setPadding(10, 10, 10, 10);
    }

    // add the rows to the table
    {
      addView(row);
      addView(_lblDescription);
    }

    Log.i(getClass().getSimpleName(), 
          "CellRendererView created");

  }

  /** 
  * update the views with the data corresponding to 
  * selection index 
  */
  public void display(int index, boolean selected) {

    String zip = getItem(index).toString();
    Hashtable<String, String> weatherForZip = _data.get(zip);

    Log.i(getClass().getSimpleName(), 
          "row[" + index + "] = " + weatherForZip.toString());

    String temp = weatherForZip.get("temperature");

    String icon = weatherForZip.get("icon");
    int iconId = ResourceUtils.getResourceIdForDrawable(
            _context, "com.developerlife", "w" + icon);

    String humidity = weatherForZip.get("humidity");

    _lblName.setText("Feels like: " + temp + " F, in: " + zip);
    _lblIcon.setImageResource(iconId);
    _lblDescription.setText("Humidity: " + humidity + " %");

    Log.i(getClass().getSimpleName(), "rendering index:" + index);

    if (selected) {
      _lblDescription.setVisibility(View.VISIBLE);
      Log.i(getClass().getSimpleName(), 
            "hiding descripton for index:" + index);
    }
    else {
      _lblDescription.setVisibility(View.GONE);
      Log.i(getClass().getSimpleName(), 
            "showing description for index:" + index);
    }

  }

}
```

Notes on this code:

  1. If a row/cell in the ListView is selected, then the humidity is displayed in a 2nd row of the TableLayout, otherwise it's not. This is why a selection listener had to be attached, and model update events had to be fired, etc.

  2. Most of this code is just leveraging a TableLayout to display weather data.

  3. The icons are from weather.com, and are in their format... their forecasts have a 2 digit number that represents the icon file name that depicts current conditions... this is loaded using the ResourceUtils class, from R.drawable.*. This class is included in 
  [AndroidUtils.zip]({{'/assets/androidutils.zip' | relative_url}}).

You can download LayoutUtils, AnimUtils and other helpful classes in 
[AndroidUtils.zip]({{'/assets/androidutils.zip' | relative_url}}).