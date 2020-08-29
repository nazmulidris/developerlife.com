---
author: Nazmul Idris
date: 2008-06-04 12:00:00-08:00
excerpt: |
  I've written 3 tutorials to show you how to create a service enabled Android
  application that performs all of it's network I/O in a background thread (not the
  UI thread). This tutorial shows you how to build a simple UI without using XML,
  by writing Java code to layout the UI.
layout: post
title: "Android - How to build a service-enabled Android app - Part 1/3 UI"
categories:
- Android
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [Building the UI](#building-the-ui)
- [The code - login screen](#the-code---login-screen)
  - [UI builder and emulator performance](#ui-builder-and-emulator-performance)
- [The code - form screen](#the-code---form-screen)
- [Download source code](#download-source-code)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

I've written 3 tutorials to show you how to create a service enabled Android application that performs all of it's
[network I/O](http://hc.apache.org/httpcomponents-core-ga/tutorial/html/) in a background thread
([not the UI thread](https://developerlife.com/2010/10/12/android-event-dispatch-thread-or-main-thread/)). Please note
that by service I mean web-service, not Android Service. These tutorials are split into three parts:

1. How to build a simple UI without using XML, by writing Java code to layout the UI.

2. [How to use Apache HTTP Client to connect to services over HTTP or HTTPS and exchange serialized Java objects with services.](https://developerlife.com/2008/06/04/how-to-build-a-service-enabled-android-app-part-23-networking/)

3. [How to use background threads to perform long running network IO operations, So That The main UI thread is not locked up.](https://developerlife.com/2008/06/04/how-to-build-a-service-enabled-android-app-part-33-multithreading/)

## Building the UI

Most of the information I've read on Google's Android documentation site, as well as other websites, take the approach
of messing with XML to build an Android UI. Personally, I don't like this approach; ideally, I would like a UI builder
like [JFormDesigner](http://www.jformdesigner.com/) for Android, to generate the underlying UI code for me, whether it's
generated in Java or XML. The XML syntax is really cumbersome for me, and I'm really familiar with the Swing, so it's
natural for me to lay components out in Java code, and not XML. Having said that I will show you how to use a simple
layout in Android for the purposes of creating a simple form based UI. It will have 2 screens:

1. a login screen that has a userid and password textfield, along with a button to login

2. a form screen that displays the userid, password, and a picture (that it gets from the service). It also has a button
   to restart the app.

I'm not going to delve into the lifecycle of an Android activity, and the various classes that exist in Android. Rather,
I'm going to take the approach of showing you a sample app so that you can get your hands dirty. In future tutorials, I
will go into greater detail on different parts of the Android API.

## The code - login screen

The main activity class is called NetworkActivity. It has some methods in it to create the UI screen described above. In
this example, I'm using [LinearLayout](http://code.google.com/android/reference/android/widget/LinearLayout.html) to
create a simple form based UI. Here's the code for the
[Activity](http://code.google.com/android/reference/android/app/Activity.html):

```java
public class NetworkActivity extends Activity {
// data

public EditText ttfUserid;
public EditText ttfPassword;

// constructor

/** Called when the activity is first created. */
@Override
public void onCreate(Bundle icicle) {
  super.onCreate(icicle);

  // create the panel to enclose everything
  View mainPanel = _createInputForm();

  // show the panel on the screen
  setContentView(mainPanel);
}

...

}
```

This is what the first screen looks like:

![]({{'assets/and-5.png' | relative_url}})

Here's the code for the first screen (created by `_createInputForm()`):

```java
// input form

/** create the login form */
private ViewGroup _createInputForm() {
  LinearLayout panel = new LinearLayout(this);
  panel.setLayoutParams(
          new LayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT));
  panel.setOrientation(LinearLayout.VERTICAL);

  // Userid : label and text field
  TextView lblUserid = new TextView(this);
  lblUserid.setText("Userid");
  lblUserid.setTextSize(TypedValue.COMPLEX_UNIT_SP, 10f);
  lblUserid.setLayoutParams(
          new LayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT));

  ttfUserid = new EditText(this);
  ttfUserid.setLayoutParams(
          new LayoutParams(LayoutParams.FILL_PARENT, LayoutParams.WRAP_CONTENT));
//  ttfUserid.setText("a");

  // Password : label and text field
  TextView lblPassword = new TextView(this);
  lblPassword.setTextSize(TypedValue.COMPLEX_UNIT_SP, 10f);
  lblPassword.setText("Password");
  lblPassword.setLayoutParams(
          new LayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT));

  ttfPassword = new EditText(this);
  ttfPassword.setLayoutParams(
          new LayoutParams(LayoutParams.FILL_PARENT, LayoutParams.WRAP_CONTENT));
  ttfPassword.setTransformationMethod(new PasswordTransformationMethod());
//  ttfPassword.setText("a");

  // login button
  final Button btnLogin = new Button(this);
  btnLogin.setText("Login");
  btnLogin.setLayoutParams(
          new LayoutParams(LayoutParams.FILL_PARENT, LayoutParams.WRAP_CONTENT));
  btnLogin.setGravity(Gravity.CENTER);
  btnLogin.setOnClickListener(new View.OnClickListener() {
    public void onClick(View view) {
      new GetDataFromServlet().execute(NetworkActivity.this);
      Log.i(getClass().getSimpleName(), "button was pressed");
    }
  });

  // actually adding the views (that have layout set on them) to the panel
  // userid
  panel.addView(lblUserid);
  panel.addView(ttfUserid);
  // password
  panel.addView(lblPassword);
  panel.addView(ttfPassword);
  // loginbutton
  panel.addView(btnLogin);

  return panel;
}
```

If you're familiar with the XML code that would perform this layout, then you will find the layout params very familiar.
Every widget that's added to the LinearLayout has to have it's layout params set. If you're familiar with Swing, then
the Activity is similar to a JFrame. The LinearLayout is like a JPanel with a LayoutManager already set. If you look at
the code from this perspective, then it should start to seem more familiar. If you look at the XML code, it's
disorientating 😃.

### UI builder and emulator performance

One of the coolest Applets/Apps that I stumbled upon to help me make sense of the Android widget toolkit is
[DroidDraw](http://www.droiddraw.org/). Try it out and you won't be disappointed. It's a simple GUI builder for Android
that generates XML layouts; however, it will help you understand all the UI elements, even if you're doing layout in
Java.

I also stumbled upon [this great article](http://jars.de/english/android-emulator-performance), that talks about how to
determine how fast your emulator runs, so that you have some idea how fast your apps might run on a real device.

## The code - form screen

The second screen simply displays data that it gets from a service. More on this in the networking part of the tutorial.

This is what the second screen looks like:

![]({{'assets/and-6.png' | relative_url}})

Here's the code for this screen:

```java
// display user profile data callback

/** create a new panel to display the data and replace the existing content */
public void _displayUserProfile(Hashtable<DataKeys,
                                Serializable> up) {

  String name = _getStringValue(up, DataKeys.str1, "user id");
  String pwd = _getStringValue(up, DataKeys.str2, "password");
  byte[] icon = _getByteRayValue(up, DataKeys.img1, null);

  View infoPanel = _createInfoPanel(name, pwd, icon);

  setContentView(infoPanel);

}

private View _createInfoPanel(String uid,
                              String pwd,
                              byte[] icon) {

  LinearLayout panel = new LinearLayout(this);
  panel.setLayoutParams(
          new LayoutParams(LayoutParams.FILL_PARENT, LayoutParams.FILL_PARENT));
  panel.setOrientation(LinearLayout.VERTICAL);

  // user id
  TextView lblName = new TextView(this);
  lblName.setText(uid);
  lblName.setTextSize(TypedValue.COMPLEX_UNIT_SP, 14f);
  lblName.setLayoutParams(
          new LayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT));

  // password
  TextView lblEmail = new TextView(this);
  lblEmail.setText(pwd);
  lblEmail.setTextSize(TypedValue.COMPLEX_UNIT_SP, 14f);
  lblEmail.setLayoutParams(
          new LayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT));

  // icon
  Bitmap bitmap = BitmapFactory.decodeStream(new ByteBuffer(icon).getInputStream());
  ImageView lblIcon = new ImageView(this);
  lblIcon.setImageBitmap(bitmap);
  lblIcon.setLayoutParams(
          new LayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT));

  // quit button
  final Button btnRestart = new Button(this);
  btnRestart.setText("Restart");
  btnRestart.setLayoutParams(
          new LayoutParams(LayoutParams.FILL_PARENT, LayoutParams.WRAP_CONTENT));
  btnRestart.setGravity(Gravity.CENTER);
  btnRestart.setOnClickListener(new View.OnClickListener() {
    public void onClick(View view) {
      setContentView(_createInputForm());
      Log.i(getClass().getSimpleName(), "restart button was pressed");
    }
  });

  // actually adding the views (that have layout set on them)
  // to the panel name
  panel.addView(lblName);
  panel.addView(lblEmail);
  panel.addView(lblIcon);
  panel.addView(btnRestart);

  ScrollView scrollPanel = new ScrollView(this);
  scrollPanel.setLayoutParams(
          new LayoutParams(LayoutParams.FILL_PARENT, LayoutParams.FILL_PARENT));
  scrollPanel.addView(panel);

  return scrollPanel;

}
```

This screen is very similar to the first one. The only interesting thing going on here is the creation of a Bitmap
widget. A PNG file is actually loaded from a service, serialized as byte[] and sent to the app, which then has to
display it in a widget. The PNG file's bytes can be loaded directly into the Bitmap widget and it will show the image on
screen. The image is actually loaded from a JAR file included in the servlet that's included in the source code. More on
this will be covered in the networking file tutorial.

## Download source code

To download the source code for this tutorial, [click here]({{'assets/android.zip' | relative_url}}). There are 3
folders in this zip file:

1. AndroidTest – This contains the Android UI and web service client code

2. ServiceTest – This contains the web service, or servlet code

3. SharedTest – This contains the code that is shared between the Android code and web service code.
