---
author: Nazmul Idris
date: 2008-06-04 12:00:00-08:00
excerpt: |
  I've written 3 tutorials to show you how to create a service enabled Android
  application that performs all of it's network I/O in a background thread (not the
  UI thread). These tutorials are split into three parts. This tutorial shows you
  how to use background threads to perform long running network IO operations, so
  that the main UI thread is not locked up.
layout: post
title: "Android - How to build a service-enabled Android app - Part 3/3 Multithreading"
categories:
- Android
- CC
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [Don't hog the UI Thread](#dont-hog-the-ui-thread)
- [Running tasks in the background thread](#running-tasks-in-the-background-thread)
- [Download source code](#download-source-code)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

I've written 3 tutorials to show you how to create a service enabled Android application that performs all of it's [network I/O](http://hc.apache.org/httpcomponents-core-ga/tutorial/html/) in a background thread (not the UI thread). Please note that by service I mean web-service, not Android Service. These tutorials are split into three parts:

  1. [How to build a simple UI without using XML, by writing Java code to layout the UI.](https://developerlife.com/2008/06/04/how-to-build-a-service-enabled-android-app-part-13-ui/)

  2. [How to use Apache HTTP Client to connect to services over HTTP or HTTPS and exchange serialized Java objects with services.](https://developerlife.com/2008/06/04/how-to-build-a-service-enabled-android-app-part-23-networking/)

  3. How to use background threads to perform long running network IO operations, so that the main UI thread is not locked up.

## Don't hog the UI Thread

Just like with Swing, or any other single threaded GUI toolkit, in Android, [you shouldn't perform long running operations in the UI Thread](https://developerlife.com/2010/10/12/android-event-dispatch-thread-or-main-thread/). Imagine that there's the equivalent of the EDT in Android, and it's called the UI thread. There are also a [UI thread utilities](http://developer.android.com/reference/android/os/AsyncTask.html) class called AsyncTask, much like SwingUtilities for posting events on this UI thread.

## Running tasks in the background thread

The basic structure of creating code that runs in a background thread is in the GetDataFromServlet class. If you've used SwingWorker before, you should see similarities.

Here's what the first screen looks like:

![]({{'assets/and-1.png' | relative_url}})

Here's the code that's executed in the UI thread (called from the first screen) when the Login button is pressed:

```java
public void execute(NetworkActivity activity) {
 
  _activity = activity;
 
  uid = activity.ttfUserid.getText().toString();
  pwd = activity.ttfPassword.getText().toString();
 
  // allows non-"edt" thread to be re-inserted into the "edt" queue
  final Handler uiThreadCallback = new Handler();
 
  // performs rendering in the "edt" thread, after background operation is complete
  final Runnable runInUIThread = new Runnable() {
    public void run() {
      _showInUI();
    }
  };
 
  new Thread() {
    @Override public void run() {
      _doInBackgroundPost();
      uiThreadCallback.post(runInUIThread);
    }
  }.start();
 
  Toast.makeText(_activity,
                 "Getting data from servlet",
                 Toast.LENGTH_LONG).show();
 
}
```

Some notes on this code:

  1. Essentially a callback handler is created, which is activated when the task in the background thread completes. This callback handler is  inserted into the event queue by using Handler.post(Runnable). This is similar to using SwingUtilities.invokeLater(Runnable). This callback handler has a method _showInUI() that will get invoked in the UI thread, when the background task completes.

  2. The long running task is performed in _doInBackgroundPost(). The UI thread just creates a new thread, and this new thread executes this method and calls the callback handler when it's done. Any code in this method will run in the "background thread", and not the UI thread.

  3. Once the background method is complete, the callback handler runs _showInUI() in the UI thread itself; so any code that goes in that method can block the UI. In this example, this code simply updates the 2nd screen with the Hashtable it downloaded, which is what it's supposed to do.

  4. The calls to Toast are to display a simple status message that pops up and disappears on it's own.

Here's the code for _doInBackgroundPost():

```java
/** this method is called in a non-"edt" thread */
private void _doInBackgroundPost() {
  Log.i(getClass().getSimpleName(), "background task - start");
 
  Hashtable<String, String> map = new Hashtable();
  map.put("uid", uid);
  map.put("pwd", pwd);
 
  try {
    HttpParams params = new BasicHttpParams();
 
    // set params for connection...
    HttpConnectionParams.setStaleCheckingEnabled(params, false);
    HttpConnectionParams.setConnectionTimeout(params, NetworkConnectionTimeout_ms);
    HttpConnectionParams.setSoTimeout(params, NetworkConnectionTimeout_ms);
    DefaultHttpClient httpClient = new DefaultHttpClient(params);
 
    // create post method
    HttpPost postMethod = new HttpPost(LoginServiceUri);
 
    // create request entity
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    ObjectOutputStream oos = new ObjectOutputStream(baos);
    oos.writeObject(map);
    ByteArrayEntity req_entity = new ByteArrayEntity(baos.toByteArray());
    req_entity.setContentType(MIMETypeConstantsIF.BINARY_TYPE);
 
    // associating entity with method
    postMethod.setEntity(req_entity);
 
    // RESPONSE
    httpClient.execute(postMethod, new ResponseHandler<Void>() {
      public Void handleResponse(HttpResponse response) 
      throws ClientProtocolException, IOException {
        HttpEntity resp_entity = response.getEntity();
        if (resp_entity != null) {
 
          try {
            byte[] data = EntityUtils.toByteArray(resp_entity);
            ObjectInputStream ois = 
                new ObjectInputStream(new ByteArrayInputStream(data));
            dataFromServlet = (Hashtable<DataKeys, Serializable>) ois.readObject();
            Log.i(getClass().getSimpleName(), 
                "data size from servlet=" + data.toString());
            Log.i(getClass().getSimpleName(), 
                "data hashtable from servlet=" + dataFromServlet.toString());
          }
          catch (Exception e) {
            Log.e(getClass().getSimpleName(), 
                "problem processing post response", e);
          }
 
        }
        else {
          throw new IOException(
              new StringBuffer()
                  .append("HTTP response : ").append(response.getStatusLine())
                  .toString());
        }
        return null;
      }
    });
 
  }
  catch (Exception e) {
    ex = e;
//    Log.e(getClass().getSimpleName(), "problem encountered", e);
    StringWriter sw = new StringWriter();
    PrintWriter pw = new PrintWriter(sw);
    e.printStackTrace(pw);
    Log.e(getClass().getSimpleName(), sw.getBuffer().toString(), e);
  }
 
  Log.i(getClass().getSimpleName(), "background task - end");
}
```

Here's the code for _showInUI():

```java
/** this method is called in the "edt" */
private void _showInUI() {
 
  if (data != null)
    Toast.makeText(_activity,
                   "Got data from service: " + data.toString(),
                   Toast.LENGTH_SHORT).show();
  if (ex != null)
    Toast.makeText(_activity,
                   ex.getMessage() == null ? "Error" : "Error - " + ex.getMessage(),
                   Toast.LENGTH_SHORT).show();
 
//  Toast.makeText(_activity,
//                 "completed background task, rejoining \"edt\"",
//
 
  _activity._displayUserProfile(dataFromServlet);
 
}
```

Here's a screenshot of the 2nd screen:

![]({{'assets/and-2.png' | relative_url}})

## Download source code

To download the source code for this tutorial, 
[click here]({{'assets/android.zip' | relative_url}}). There 
are 3 folders in this zip file:

  1. AndroidTest –  This contains the Android UI and web service client code

  2. ServiceTest – This contains the web service, or servlet code

  3. SharedTest – This contains the code that is shared between the Android code and web service code.



