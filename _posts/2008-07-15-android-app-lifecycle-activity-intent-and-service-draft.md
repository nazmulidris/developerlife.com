---
author: Nazmul Idris
date: 2008-07-15 01:07:57+00:00
excerpt: |
  This tutorial will show you how to create a sub-Activity from a calling-Activity,
  and process the results produced by the sub-Activity, if you want to do so. Also,
  the various ways of launching a sub-Activity are covered, along with the Android
  Activity history stack. A subclass of Activity is also provided that makes 
  it trivial to launch sub-Activities and respond to results from them.
layout: post
title: "Android Activity and sub-Activity Tutorial"
categories:
  - Android
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [What’s an activity?](#whats-an-activity)
  - [Service](#service)
- [sub-Activity](#sub-activity)
  - [Activity history stack](#activity-history-stack)
  - [1. Fire and forget](#1-fire-and-forget)
  - [2. Async callback, and correlationId](#2-async-callback-and-correlationid)
- [Intent and sub-Activity details](#intent-and-sub-activity-details)
  - [Processing the result from the sub-Activity in the calling-Activity (cancel or ok)](#processing-the-result-from-the-sub-activity-in-the-calling-activity-cancel-or-ok)
- [Summary - Return to sender... err... caller?](#summary---return-to-sender-err-caller)
- [Is there a better way? Yes, there is!](#is-there-a-better-way-yes-there-is)
- [Source code download](#source-code-download)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

This tutorial will show you how to create a sub-Activity from a calling-Activity, and process the results produced by
the sub-Activity, if you want to do so. Also, the various ways of launching a sub-Activity are covered, along with the
Android Activity history stack. A subclass of Activity is also provided that makes it trivial to launch sub-Activities
and respond to results from them.

## What’s an activity?

An activity is the equivalent of a Frame/Window in GUI toolkits. It takes up the entire drawable area of the screen
(minus the status and title bars on top). An activity is what gets bound to the AndroidManifest.xml as the main entry
point into an application. For long running tasks, it’s best to use a service that talks to this activity.

### Service

Activities are meant to display the UI and get input from the user. However, long running tasks are not meant to be
spawned in a activity, since they can be frozen when the focus is switched away from them (by the user or incoming phone
call or system event). Services on the other hand keep running for the duration of the user’s ‘session’ on the device.

## sub-Activity

An Activity (calling-Activity) can spawn another Activity (sub-Activity) in 2 ways:

1. Fire and forget – create an event (Intent) and fire it

2. Async callback – create an event (Intent), fire it, and wait for it’s response in a callback method (of the
   calling-Activity).

[Here](http://code.google.com/android/kb/commontasks.html#opennewscreen) are more details on spawning new “screens” or
Activities from the Android SDK documentation.

Here's some sample code of an Intent being created and a sub-Activity (called WidgetActivity) being launched in response
to a button being pressed (a detailed analysis of this is provided in the sections below) in the MainActivity class:

```java
    b4.setOnClickListener(new View.OnClickListener() {
      public void onClick(View view) {
        Intent i = new Intent(ctx, WidgetActivity.class);

        Log.i(Global.TAG, "b4 pressed - about to launch sub-activity");

        // the results are called on widgetActivityCallback
        ctx.startSubActivity(i, Global.WIDGET_REQ_CODE);

        Log.i(Global.TAG, "b4 pressed - sucessfully launched sub-activity (startSubActivity called)");
      }
    });
```

### Activity history stack

Please note that Android maintains a history stack of all the Activities that have been spawned in an application's
Linux process. In the sample code above, the calling-Activity simply provides the class name of the sub-Activity. When
the sub-Activity finishes, it puts it's result code and any data back on the stack and finishes itself. Since Android
maintains the stack, it knows which calling Activity to pass the result back to. The calling-Activity has an
onActivityResult method that handles all the callbacks from the sub-Activities. This is pretty confusing at first, since
to keep it all straight we have to use CorrelationIds (more on that below).

### 1. Fire and forget

An Intent is just an event. It can have a target of an Activity class along with some data that’s passed in via a Bundle
(which is like a Hashtable). Fire/forget is easy. Just create an Intent (with a reference to the sub-Activity class),
and call startActivity(intent, correlationId) and this will launch the sub-Activity. This correlationId (requestCode) is
used to identify which sub-Activity called the callback method (which happens when doing the async callback). So it’s
not really needed in the fire-forget scenario.

### 2. Async callback, and correlationId

The calling-Activity has to provide a correlationId/request code to the Intent/event, before firing/raising it. This is
then used by the sub-Activity to report it’s results back to the calling-Activity when it’s ready. The calling-Activity
does not stop when it spawns the sub-Activity (it does not wait for the callback to happen to become unblocked). Please
note that this sub-Activity is not "modal", that is, the calling Activity does not block, when startSubActivity() is
called. So if you're thinking that this is like a modal dialog box, where the calling-Activity will wait for the
sub-Activity to produce a result, then you have to think of it differently.

The sub-Activity is an Activity. It has to have an onCreate() method to build the UI. The only difference is that once
it’s complete, it has to report it’s results to the caller by doing the following:

1. setResult(resultCode, strdata, bundledata) – this is how results are sent to the caller. The resultCode is either
   RESULT_CANCELED or RESULT_OK. Note that you don't have to identify which calling-Activity this result goes to, and
   you don't have to identify what correlation ID/requestCode to use; these are inferred by Android since it keeps a
   history stack of Activity objects around. Also note that you have to provide the correlationID when you created the
   Activity that launches the sub-Activity... so this is how Android knows how to pass the results to the
   calling-Activity with the correct correlationID. Whew! :)

2. finish() – equivalent of calling return... it sends control back to the caller. Note that the calling-Activity never
   blocked, this is not "modal" behavior. finish() just reclaims the resources allocated for the sub-Activity, and
   removes it from the Activity history stack (for this application process).

On the calling-Activity side, the method that gets called when the sub-Activity completes (with result or error, with or
without data) is onActivityResult(...). This method contains the result code, and any data that’s set by the
sub-Activity. If there are any errors, these get reported there as well. There’s a special result code that is passed if
there are any problems – RESULT_CANCELED. If the sub-Activity is launched, and then you press the "Back button" on the
emulator then RESULT_CANCELED is passed on your behalf, and finish() is automatically called. Note that you can pass
parameters back to the calling-Activity (via a Bundle) when you cancel the sub-Activity. Here's some sample code that
does this when a button is pressed:

```java
b2.setOnClickListener(new View.OnClickListener() {
  public void onClick(View view) {
    Bundle map = new Bundle();

    map.putString("de", "nied");
    activity.returnErrorToCaller(map);

    Log.i(Global.TAG,
          "cancel button pressed, calling returnToCaller with bundle" + map.toString());
  }
});

/** call this to return control to the calling activity - {@link MainActivity#onActivityResult} */
public void returnErrorToCaller(Bundle bundle) {
  // sets the result for the calling activity
  setResult(RESULT_CANCELED, null, bundle);

  // equivalent of 'return'
  finish();
}
```

Note that when you press the "Back button" on the emulator, the RESULT_CANCELED is sent back to the calling-Activity,
but no parameters are passed, they are null.

## Intent and sub-Activity details

When creating an Intent (event) that will be used to create a new sub-Activity, you can pass the class of this Activity
as a parameter to the Intent. Here's the code to create an Intent:

```java
Intent i = new Intent(ctx, WidgetActivity.class);

Log.i(Global.TAG, "b4 pressed - about to launch sub-activity");

// the results are called on widgetActivityCallback
ctx.startSubActivity(i, Global.WIDGET_REQ_CODE);
```

When you create this new sub-Activity, you have to register it in the AndroidManifest.xml file. Here's an example:

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.devlife">
    <application android:icon="@drawable/stlogo">
        <activity android:name=".mainactivity.MainActivity"
                  android:label="@string/app_name">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
      <activity android:name=".subactivity.WidgetActivity"
                android:label="@string/widgetactivity_name"/>
    </application>
</manifest>
```

Here are a few notes on this AndroidManifest.xml file:

1. The name of the sub-Activity defined by the "android:name" attribute, has to be the name of the class (in this case
   "com.devlife.subactivity.WidgetActivity").

2. If you've specified a root package attribute for the manifest tag, then you have to precede this class name with a
   "."; if you don't have a root package attribute defined, then just insert the fully qualified name of the class.

3. In the example above, I have a package attribute defined as: package="com.devlife". Android uses this name field to
   do a class lookup when you create an Intent and point it to a .class object.

#### Processing the result from the sub-Activity in the calling-Activity (cancel or ok)

When creating the Intent, to launch this sub-Activity, you have to pass it a correlation ID, which will be used by the
calling-Activity to determine what code is run in the onActivityResult() method. This correlation ID is called a request
code, and it's necessary due to the fact that one Activity might spawn more than one sub-Activity, and if these
sub-Activities send a result code (and some data) back to the calling-Activity, then there has to be a way to sort out
who sent what. This callback mechanism is pretty clunky, and a bit confusing. The implementation of the
onActivityResult() method has to have a switch statement with case statements for each correlation ID. It makes sense to
create a global static class that holds these correlation IDs, that are implicitly mapped to each of your sub-Activity
classes. Here's an example of the callback implementation in the calling-Activity MainActivity:

```java
@Override protected void onActivityResult(int requestCode,
                                          int resultCode,
                                          String strdata,
                                          Bundle bundle)
{

  Log.i(Global.TAG, "MainDriver main-activity got result from sub-activity");

  if (resultCode == Activity.RESULT_CANCELED) {
    Log.i(Global.TAG2,
          "WidgetActivity was cancelled or encountered an "
          + "error. resultcode == result_cancelled");
    Log.i(Global.TAG2,
          "WidgetActivity was cancelled - data =" + bundle);
  }
  else
    switch (requestCode) {
      case Global.WIDGET_REQ_CODE:
        widgetActivityCallback(resultCode, bundle);
        break;
    }

  Log.i(Global.TAG, "MainDriver main-activity got result "
                    + "from sub-activity");

}
```

In addition the correlation ID, a result code is passed from the sub-Activity to calling-Activity. It's strange that the
sub-Activity has to "kill itself" in order for this result to pass back to the caller. This exchange is very clunky as
well. Here's an example of a sub-Activity passing data, result code, and correlation ID back to the calling-Activity
when a button is pressed; please note that the calling Activity is implicitly determined (not explicitly, since Android
maintains a history stack of Activities in the application's process:

```java
b.setOnClickListener(new View.OnClickListener() {
  public void onClick(View view) {
    Bundle map = new Bundle();

    map.putString("monkey", "donkey");
    activity.returnToCaller(map);

    Log.i(Global.TAG,
          "button pressed, calling returnToCaller with bundle" +
          map.toString());
  }
});

/** call this to return control to the calling activity - {@link MainActivity#onActivityResult} */
public void returnToCaller(Bundle bundle) {
  // sets the result for the calling activity
  setResult(RESULT_OK, null, bundle);

  // equivalent of 'return'
  finish();
}
```

Keep in mind that if the "Back button" is pressed, while the sub-Activity is visible, then a RESULT_CANCELED resultCode
is passed to the onActivityResult() method of the calling-Activity. Also, the bundle parameter is null in this case. So
there are 3 ways to return control back to the calling-Activity:

1. Pass RESULT_OK, with or without some return value (passed as a Bundle or String) - in this example a Bundle is used
   ({"monkey"="donkey"}).

2. Pass RESULT_CANCELED, with or without some return value; in this example a Bundle is passed back to the
   calling-Activity ({"de"="nied]").

3. Press the "Back button" which will pass RESULT_CANCELED, with null bundle and string parameter to the
   calling-Activity.

## Summary - Return to sender... err... caller?

As you have probably inferred by now, the sub-Activity doesn't need to know anything about it's caller. The
calling-Activity has to provide a correlationId and a class name to the Intent that launches the sub-Activity. This
correlationId is then used by the calling-Activity to figure out what to do with the result (and which sub-Activity
produced these results).

In the code example above, you don't really need to know what the calling Activity's class is... since it just fires an
Intent to launch the sub-Activity. When the sub-Activity finishes, the results are sent back to the calling-Activity
implicitly by Android itself. This is why I only showed the calling-Activity (in my example MainActivity) fire the
Intent and process the callback with results.

## Is there a better way? Yes, there is!

Instead of dealing with the clunky requestCode/correlationId, I decided to create a subclass of Activity that would make
launching sub-Activities, and dealing with their result (OK or CANCELED) trivial. Here's the class that makes it all
very simple, it's called SimpleActivity:

```java
/**
 * SimpleActivity is a subclass of Activity that makes it
 * trivial to create a sub-Activity, and handle it's
 * results (ok or cancel). No need to deal with requestCodes,
 * since this class handles creating correlationIds
 * automatically.
 *
 * @author Nazmul Idris
 * @version 1.0
 * @since Jul 3, 2008, 12:08:46 PM
 */
public class SimpleActivity extends Activity {

/** holds the map of callbacks */
protected HashMap<Integer, ResultCallbackIF>
    _callbackMap = new HashMap<Integer, ResultCallbackIF>();

/** use this method to launch the sub-Activity, and provide a
* functor to handle the result - ok or cancel */
public void launchSubActivity(Class subActivityClass,
                              ResultCallbackIF callback) {

  Intent i = new Intent(this, subActivityClass);

  Random rand = new Random();
  int correlationId = rand.nextInt();

  _callbackMap.put(correlationId, callback);

  startSubActivity(i, correlationId);

}

/**
 * this is the underlying implementation of the onActivityResult
 * method that handles auto generation of correlationIds and
 * adding/removing callback functors to handle the result
 */
@Override protected void onActivityResult(int correlationId,
                                          int resultCode,
                                          String paramStr,
                                          Bundle paramMap) {

  try {
    ResultCallbackIF callback = _callbackMap.get(correlationId);

    switch (resultCode) {
      case Activity.RESULT_CANCELED:
        callback.resultCancel(paramStr, paramMap);
        _callbackMap.remove(correlationId);
        break;
      case Activity.RESULT_OK:
        callback.resultOk(paramStr, paramMap);
        _callbackMap.remove(correlationId);
        break;
      default:
        Log.e(Global.TAG3,
            "Couldn't find callback handler for correlationId");
    }
  }
  catch (Exception e) {
    Log.e(Global.TAG3,
            "Problem processing result from sub-activity", e);
  }

}

/**
 * ResultCallbackIF is a simple interface that you have to
 * implement to handle results - ok or cancel from a sub-Activity.
 *
 * @author Nazmul Idris
 * @version 1.0
 * @since Jul 3, 2008, 12:11:31 PM
 */
public static interface ResultCallbackIF {

  public void resultOk(String resultString, Bundle resultMap);
  public void resultCancel(String resultString, Bundle resultMap);

}//end interface ResultCallbackIF

}//end class SimpleActivity
```

Here's some sample code to show you how clean it is to use SimpleActivity, instead of the default stuff; this code (it's
a subclass of SimpleActivity) spawns a new sub-Activity in response to a button press, and the callback to handle the
results is passed in-line, with the call to spawn the sub-Activity:

```java
// setup b2 to spawn a subactivity - TableActivity
b2.setOnClickListener(new View.OnClickListener() {
  public void onClick(View view) {
    Log.i(Global.TAG3, "b2 pressed - about to launch sub-activity");

    ctx.launchSubActivity(TableActivity.class,
                          new SimpleActivity.ResultCallbackIF() {
                            public void resultOk(String str, Bundle result) {
                              Log.i(Global.TAG3,
                                    "subactivity completed successfully, "
                                    + "result=" + result);
                            }
                            public void resultCancel(String str, Bundle result) {
                              Log.i(Global.TAG3,
                                    "subactivity was cancelled, result=" + result);
                            }
                          });

    Log.i(Global.TAG3, "b2 pressed - sucessfully launched sub-activity " +
                       "(startSubActivity called)");
  }
});
```

No need to mess with correlationIds, or overriding onActivityResult in the calling-Activity. Simple, elegant, and it
works :) .

## Source code download

Download all of this from [AndroidUtils]({{'assets/androidutils.zip' | relative_url}}).
