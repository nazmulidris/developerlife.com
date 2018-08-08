---
author: Nazmul Idris
date: 2008-04-21 21:51:14+00:00
excerpt: |
  Given an IP address, this tutorial will show you how to get a Google Static
  Map from it.
layout: post
title: "Geocoding tutorial - Accessing Google Static Maps from Java"
categories: 
- Server
---
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [License key](#license-key)
- [Background Information](#background-information)
- [Source code](#source-code)
- [Graphical test harness](#graphical-test-harness)
  - [Using the harness](#using-the-harness)
- [Advanced API usage](#advanced-api-usage)
- [Example of integrating this into an app](#example-of-integrating-this-into-an-app)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

Google just released a new API that allows access to 'static' maps. Static maps are GIF images that are generated based on a longitude/latitude that's passed to the Google Static Map API. In this tutorial, you will see how to use this API from Java applications. I've created a Java adapter to the API that will allow you to quickly access all the Static Map API features. I've also provide a graphical application that you can use as a test harness to the see the API in action.

You need a latitude and longitude in order to start using the API. You can get this lat/lon pair from a GeoIP database, or a GPS receiver, or just type it in manually.

Also, the 'normal' Google Maps API is geared for use in JavaScript, and the Static API doesn't involve any JavaScript.

## License key

You will need to sign up for a license key in order to use this API. You can learn more about it [here](http://code.google.com/apis/maps/documentation/staticmaps/). You can sign up for a key [here](http://code.google.com/apis/maps/signup.html). A license key will allow 1000 accesses in a 24 hour period. I've designed the Java API to access the Static Maps API in a way that you can easily cache maps that the Static Maps API generates.

## Background Information

Locations on earth can be specified by a combination of longitude, latitude, and elevation. You can read all about it [here on wikipedia](http://en.wikipedia.org/wiki/Geographic_coordinates). The following code is enough to identify a geographic location:

```java
double latitude;
double longitude;
```

This is the bare minimum information that you will need, but you will be able to get by and interface with many location based services just with this data. How do you get this long/lat data? If your app has access to a [GPS](http://en.wikipedia.org/wiki/Gps) device, then it can read the GPS coordinates from it ([NMEA](http://en.wikipedia.org/wiki/NMEA) standard) - the GPS receiver sends lat/long information every few seconds via a serial port, USB, or Bluetooth connection to your laptop or mobile device, and you can then use that data. Alternatively, if you know the IP address where your desktop, mobile, or web based app is running, then you might be able to get geographic information out of it. There are issues with this and it’s not always reliable, and these [issues are explained here](http://www.maxmind.com/app/ip-location-explained).


## Source code

The following code is the main() method implementation of the MapLookup class, and you can run it to get a feel for how to use the API:

```java
public static void main(String[] args) {

  // make sure to set a valid license key
  setLicenseKey("");

  double lat = 38.931099;
  double lon = -77.3489;

  double lat1 = 40.742100;
  double lon1 = -74.001801;

  String u1 = getMap(lat, lon);
  System.out.println(u1);

  String u2 = getMap(lat, lon, 256, 256);
  System.out.println(u2);

  String u3 = getMap(lat, lon, 
        new MapMarker(lat, lon, MapMarker.MarkerColor.blue, 'a'));
  System.out.println(u3);

  String u4 = 
    getMap(lat, lon,
           250, 500,
           new MapMarker(lat, lon, MapMarker.MarkerColor.green, 'v'),
           new MapMarker(lat1, lon1, MapMarker.MarkerColor.red, 'n')
    );
  System.out.println(u4);

}
```

There are many different ways to use the API as you can see from this code. The methods getMap(...) return a String URI that can be resolved to get the map image from Google. All the parameters that you give the MapLookup class are used to generate this URI that is compliant with what Google expects. The MapLookup class also performs range validation checking for input parameters. The following is a list of methods you can call:

```java
// set the license key
public static void setLicenseKey(String lic) {
  GmapLicense = lic;
}

// methods
public static String getMap(double lat, double lon) {
  return getMap(lat, lon, SizeMax, SizeMax);
}

public static String getMap(double lat, double lon, int sizeW, int sizeH) {
  return getMap(lat, lon, sizeW, sizeH, ZoomDefault);
}

public static String getMap(double lat, 
                            double lon, 
                            int sizeW, 
                            int sizeH, 
                            int zoom) {
  return _map.getURI(lat, lon, sizeW, sizeH, zoom);
}

public static String getMap(double lat, 
                            double lon, 
                            int sizeW, 
                            int sizeH, 
                            MapMarker... markers) {
  return _map.getURI(lat, lon, sizeW, sizeH, markers);
}

public static String getMap(double lat, 
                            double lon, 
                            MapMarker... markers) {
  return getMap(lat, lon, SizeMax, SizeMax, markers);
}
```

All the getMap(...) methods return a String URI that can be resolved to get a map image from Google. Most of the methods are pretty straightforward. The class validates your input params to make sure that they are in range. Here's a list of restrictions:

  1. size width and height - max of 512 pixels

  2. zoom - zoom level between 0 and 19.

Make sure to call setLicenseKey() to set the license key supplied to you by Google, when you sign up.

To turn the URI into a GIF use the getDataFromURI(String) method:

```java
/** use httpclient to get the data */
public static ByteBuffer getDataFromURI(String uri) throws IOException {

  GetMethod get = new GetMethod(uri);

  try {
    new HttpClient().executeMethod(get);
    return new ByteBuffer(get.getResponseBodyAsStream());
  }
  finally {
    get.releaseConnection();
  }

}
```

## Graphical test harness

A full blown graphical test harness is provided so that you can get familiar with the API. Here's a screenshot of this app in action:

![]({{'assets/geocoding-1.png' | relative_url}})

![]({{'assets/geocoding-2.png' | relative_url}})

To run the harness, run the SampleApp class in the Provider.GoogleMapsStatic.TestUI package. If you have IDEA, then a GeoIPLookup.ipr project file is provided with a run configuration for this graphical test harness. Make sure that you have a license key pasted into the License Key field, otherwise you will get an error.

### Using the harness

The graphical app can be used to access simple API functions. You have to provide a width and height for the map size that you're expecting. The max size is 512 pixels for each. Also you have to provide a latitude and longitude, these are just Java double values. When you click on "Get Map", the app generates a URI, which is then resolved into a GIF image that's displayed. The Task API is used to load this map in the background. For more information on the Task API, [start here](https://developerlife.com/2008/04/06/task-api-quick-start-guide/).

## Advanced API usage

Simple usage of the API is covered by the test harness. Advanced usage constitutes using "markers". My API makes it really easy to work with markers! There's a getMap(...) variant that takes any number of MapMarker objects. These objects represent "pushpins" that you want to show up on the map itself. You can pass any number of these to the API. Here's the MapMarker class:

```java
/**
 * {latitude} (required) specifies a latitudinal value with precision to 
 * 6 decimal places.
 * {longitude} (required) specifies a longitudinal value with precision 
 * to 6 decimal places.
 * {color} (optional) specifies a color from the set {red,blue,green}.
 * {alpha-character} (optional) specifies a single lowercase alphabetic
 * character from the set {a-z}.
 * <p/>
 * An example marker declaration is of the form {latitude},{longitude},
 * {color}{alpha-character}. Note in particular that the color and
 * alpha-character values of the string are not separated by a comma.
 * A sample marker declaration is shown below.
 * <p/>
 * markers=40.702147,-74.015794,
 *         blues|40.711614,-74.012318,
 *         greeng&key=MAPS_API_KEY
 */
public class MapMarker implements Serializable {
static final long serialVersionUID = 5805831996822361347L;

// enum for marker colors
enum MarkerColor {
  red, green, blue
}// enum MarkerColor

// data
private char _alpha = '1';
private MarkerColor _color = null;
private double _lat = -1;
private double _lon = -1;

// constructor
public MapMarker(double lat, double lon, MarkerColor color, char alpha) {
  _lat = lat;
  _lon = lon;
  _color = color;
  _alpha = alpha;

  StringBuffer buf = new StringBuffer();
  buf.append(alpha);
  if (!Pattern.matches("[a-zA-Z]", buf))
    throw new IllegalArgumentException(
            "marker alpha is not a char between a-z");

  if (color == null) throw new IllegalArgumentException(
          "marker color can not be null");
}

public MapMarker(double lat, double lon) {
  _lat = lat;
  _lon = lon;
}

// generate Google Maps uri
public String toString() {
  StringBuilder sb = new StringBuilder();

  sb.append(_lat).append(",").append(_lon);

  if (_color != null && _alpha != '1') {
    sb.
        append(",").
        append(_color.toString()).
        append(_alpha);
  }

  return sb.toString();
}

}// class Marker

```
You can create a MapMarker just by providing a lat/lon pair. You can also provide a color and alphabet designation along with the lat/lon. The API takes care of translating this into URL parameters that the Google Static Maps API will understand. Here's are some examples:

```java
String u3 = getMap(
      lat, 
      lon, 
      new MapMarker(lat, lon, MapMarker.MarkerColor.blue, 'a'));
System.out.println(u3);

String u4 = getMap(
        lat, lon,
        250, 500,
        new MapMarker(lat, lon, MapMarker.MarkerColor.green, 'v'),
        new MapMarker(lat1, lon1, MapMarker.MarkerColor.red, 'n')
);
System.out.println(u4);
```

In the code above (part of the main()), you can see how to create MapMarker objects really easily!

## Example of integrating this into an app

When you put the Static Maps API together with the GeoIP APIs, then you can create some really useful and compelling functionality in your applications - be they mobile, web, or desktop based. In the ScreamingToaster Platform, I've created functionality that embeds geocode information into every aspect of the user experience. Here's an example of this in action:

![]({{'assets/geocoding-3.png' | relative_url}})