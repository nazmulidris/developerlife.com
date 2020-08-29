---
author: Nazmul Idris
date: 2009-03-06 19:47:02+00:00
excerpt: |
  I've been working with various object encoding schemes to get information
  transferred over the network between services and mobile apps running on Android
  and BlackBerry. On Android, I figured I would try using Java object serialization,
  and that works some of the time, and not for anything complex. I wish the object
  serialization and deserialization mechanism in GWT would be ported over to all these
  mobile environments, but I digress. This tutorial outlines the use of JSON for this
  purpose.
layout: post
title: "Using JSON for mobile object exchange"
categories:
- Android
- Server
---
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [What is JSON?](#what-is-json)
- [Source code example](#source-code-example)
- [My JSON Code Generator](#my-json-code-generator)
- [JSON API for JavaME and SE](#json-api-for-javame-and-se)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

I've been working with various object encoding schemes to get information transferred over the network between services
and mobile apps running on Android and BlackBerry. On Android, I figured I would try using Java object serialization,
and that works some of the time, and not for anything complex. I wish the object serialization and deserialization
mechanism in GWT would be ported over to all these mobile environments, but I digress.

So I evaluated the following strategies:

1. I tried using binary formats, these are too complicated and the overhead of writing marshalling/unmarshalling code is
   too high. Also this code has to be portable across a variety of platforms, and so it gets complicated. For me, it has
   to work on BlackBerry and Android, and BlackBerry is clearly the lesser platform, only supporting JavaME, while
   Android has pseudo Java5 support with generics.

2. I tried using Google Protocol Buffers. While this sounded like the perfect solution at first, it isn’t. It relies on
   the use of generics and so that rules it out as an option for JavaME, although it’s a good option to have for Android
   and even desktop environments, and other service to service interactions. But this is one more thing to learn, and it
   won't even work for BlackBerry. So that ruled it out.

3. I looked at XML serialization. There is plenty of tooling around this option. They have XMLRPC servers and clients
   (even for JavaME) so that makes it a little easier to deal with. But all transport mechanism aside, the marshalling
   and unmarshalling code still has to be generated painfully. Although the use of Betwixt & Digester or XML Beans might
   make it easier. Again, more APIs to use and learn and all that... so that ruled it out.

So what did I end up choosing? None of the above 😃. I picked this one: [JSON](http://json.org/). Yes, good old
JavaScript Object Serialization 😃. It’s simple. It’s lightweight. The marshalling and unmarshalling has to be done by
hand, but it’s relatively simple (everything is a map, and you can have lists of values). Any binary data you want to
transfer has to be encoded to Base64, so that’s cool. It’s really simple, nothing new to learn. And they have APIs
available for everything (platform, language, whatever). The only thing to keep in mind is that your
marshalling/unmarshalling code has to be available in the codebase of your services as well as mobile apps, and any
other apps that you use this data in. Using HTTP makes it so that you don’t really have to include the transport
mechanism code, since HTTP/S libs are available on just about every platform.

## What is JSON?

Think of JSON as a hashtable. For a key there is a value. The value can be an object. JSON supports some Java objects
right out of the box like Vector, String, Integer, Boolean, and Arrays of Objects. If you want to transfer objects, then
you have to convert them to bytes, and then Base64 encode these bytes to strings. Then you have to reverse this process
to get the Object when you deserialize. The main class for transferring a Hashtable is JSONObject.

You can also pass arrays, which can have objects of any type in them using JSONArray. This class is great when you don’t
have keys for the objects you are trying to pass over the wire. Things like method params are really easy to encode
using this scheme. You can also put JSONArray as a value for a key in a JSONObject object.

Here are some diagrams that depict this:

![]({{'assets/json-1.gif' | relative_url}})

![]({{'assets/json-2.gif' | relative_url}})

There are a couple of things to keep in mind:

1. When passing null as a value, be sure to pass `JSONObject.NULL` instead. This just avoids `JSONExceptions` being
   raised all over the place, and it makes it so that null values are actually passed in a `JSONObject` (which by
   default will not include a key if the value is null). `JSONObject.NULL.equals(null)` is `true`, so you can test for
   your value being null in this way.

2. When passing objects, be sure that what’s contained in them can be serialized. Alternatively, provide serialization
   routines to Base64 encoded string for bytes that are not provided by default.

3. When using JSON, you can use the underlying `Hashtable` has the foundation data structure of your object model, if it
   fits. Otherwise, just design your object model in a way that is natural for it, and just write serialization method
   to convert it to a `Hashtable`/`JSONObject`/`JSONArray`. My code generator is meant as a starting point to do this...
   you can modify it's output by hand to meet your needs.

## Source code example

This example shows using `JSONArray`, `JSONObject`, and `Vectors`. There’s also a visualization of the state of the
`JSONObject` at the end of the code.

```java
public class JSONDemo {

    // main method
    public static void main(String[] args) throws JSONException {
        JSONArray list1 = new JSONArray();
        Vector v = new Vector();
        v.addElement("1");
        v.addElement("2");
        v.addElement("3");
        list1.put(v);

        Vector v1 = new Vector();
        v1.addElement("A");
        v1.addElement("B");
        v1.addElement("C");
        JSONArray list2 = new JSONArray(v1);

        JSONObject jObj = new JSONObject();
        jObj.put("key", "value");
        jObj.put("list1", list1);
        jObj.put("list2", list2);

        System.out.println("JObject: " + jObj.toString(5));
    }
}
```

![]({{'assets/json-3.png' | relative_url}})

## My JSON Code Generator

Here are some code examples to get you started:
[http://code.google.com/p/json-simple/wiki/EncodingExamples](http://code.google.com/p/json-simple/wiki/EncodingExamples)

To automate the process, I've actually created a class that generates JSON code for you 😃 . It's a very useful code
generator that is a good starting point for you to use in your projects. If you improve on it, and are willing to share
the improvements, please email them to me and I will provide it on developerlife.com. Just run this class and provide
the field names you want it to generate code for as command line arguments. The code is output to the console and
automatically copied to the clipboard so you can paste it into your IDE using Ctrl + V.

```java
package rpc.json;

import rpc.json.me.*;

import java.awt.*;
import java.awt.datatransfer.*;

/**
 * JSONCodegen is a simple code generator that takes care of creating
 * getter/setter/ser/deser code for you. You just provide the fields
 * you want, and the code is generated & copied to the clipboard.
 *
 * <p>The getter/setter code deal with "null" objects by using
 * {@link JSONObject#NULL} instead.
 *
 * @author Nazmul Idris
 * @version 1.0
 * @since Feb 11, 2009, 8:55:51 AM
 */
public class JSONCodegen {

    public static final String DefaultPackage = "datamodels";
    public static final String DefaultClass = "MyDataModel";
    public static final String DefaultType = "Object";

    /**
     * provide the properties/fields that you want your json
     * object to have, separated by spaces.
     */
    public static void main(String[] args) {

        StringBuffer buf = new StringBuffer();

        // package and import
        buf.append("package ").append(DefaultPackage);
        _endLine(buf);
        buf.append("import rpc.json.me.*");
        _endLine(buf);

        // class
        buf.append("/** code generated by JSONCodegen */\n");
        buf.append("public class ").append(DefaultClass).append(" {\n");

        _data(args, buf);

        _constructors(args, buf);

        _gettersetter(args, buf);

        _serdeser(args, buf);

        _listutils(args, buf);

        _tostr(args, buf);

        // end class
        buf.append("} //end class ").append(DefaultClass);

        // dump to console & copy to clipboard
        System.out.println(buf);
        _saveToClipboard(buf);
    }

    private static void _tostr(String[] args, StringBuffer buf) {

        buf.append("\n/* toString */\n");

        buf.append(
                "public String toString() {\n"
                        + "  try {\n"
                        + "    return "
                + "BBUtils.compactPrintJSONObject(toJSON()).toString();\n"
                        + "  }\n"
                        + "  catch (JSONException e) {\n"
                        + "    return \""
                        + DefaultClass
                        + " - can not get toString():\" + e.toString();\n"
                        + "  }\n"
                        + "}");
    }

    private static void _listutils(String[] args, StringBuffer buf) {
        buf.append("\n/* list utils */\n");

        // toarray
        buf.append("public static JSONArray toJSONArray(");
        buf.append(DefaultClass);
        buf.append("[] ray) {\n");

        buf.append("JSONArray jray = new JSONArray();\n")
                .append("for (int i = 0; i < ray.length; i++) "
                        + "jray.put(ray[i]);\n")
                .append("return jray;\n")
                .append("}\n");

        // fromarray
        buf.append("public static ");
        buf.append(DefaultClass);
        buf.append("[] fromJSONArray(JSONArray jray) "
                   + "throws JSONException {\n");
        buf.append("int size = jray.length();\n");

        buf.append(DefaultClass);
        buf.append("[] ray = new ");
        buf.append(DefaultClass);
        buf.append("[size];\n");

        buf.append("for (int i = 0; i < size; i++) ray[i] = (");
        buf.append(DefaultClass);
        buf.append(") jray.get(i);\n");

        buf.append("return ray;\n}\n");
    }

    private static void _serdeser(String[] args, StringBuffer buf) {
        buf.append("\n/* ser, deser */\n");

        // tojson
        buf.append("public JSONObject toJSON() throws JSONException {\n");
        buf.append("JSONObject retval = new JSONObject()");
        _endLine(buf);

        for (int i = 0; i < args.length; i++) {
            String arg = args[i];
            buf.append("retval.put(")
                    .append(_quotesAround(arg))
                    .append(", ")
                    .append(arg)
                    .append(")");
            _endLine(buf);
        }

        buf.append("return retval");
        _endLine(buf);
        buf.append("}\n");

        // fromjson
        buf.append("public static ")
                .append(DefaultClass)
                .append(" fromJSON(JSONObject json) "
                        + "throws JSONException {\n");
        buf.append(DefaultClass)
                .append(" retval = new ")
                .append(DefaultClass).append("()");
        _endLine(buf);

        for (int i = 0; i < args.length; i++) {
            String arg = args[i];
            buf.append("retval.set_")
                    .append(arg)
                    .append("(json.get(")
                    .append(_quotesAround(arg))
                    .append("))");
            _endLine(buf);
        }

        buf.append("return retval");
        _endLine(buf);
        buf.append("}\n");
    }

    private static void _gettersetter(String[] args, StringBuffer buf) {
        buf.append("\n/* getter, setter */\n");
        for (int i = 0; i < args.length; i++) {
            String arg = args[i];
            buf.append("/** @param val if this is null, "
                       + "JSONObject.NULL will be inserted.*/\n");
            buf.append("public void ")
                    .append("set_")
                    .append(arg)
                    .append("(")
                    .append(DefaultType)
                    .append(" val){\n");
            buf.append("if (val == null) val = JSONObject.NULL;\n");
            buf.append(arg).append(" = val;\n}\n");
        }

        for (int i = 0; i < args.length; i++) {
            String arg = args[i];
            buf.append(
                    "/** @return JSONObject.NULL will be returned "
                    + "if null was inserted to begin with.*/\n");
            buf.append("public ")
                    .append(DefaultType)
                    .append(" get_")
                    .append(arg)
                    .append("(){");
            buf.append("return ").append(arg).append(";}\n");
        }
    }

    private static void _constructors(String[] args, StringBuffer buf) {
        buf.append("\n/* constructors */\n");

        buf.append("public ").append(DefaultClass).append("(){}\n");

        buf.append("public ").append(DefaultClass).append("(");
        for (int i = 0; i < args.length; i++) {
            String arg = args[i];
            boolean isLastElement = i == (args.length - 1);
            buf.append(DefaultType).append(" ").append(arg).append("_");
            if (!isLastElement) buf.append(", ");
        }
        buf.append("){\n");
        for (int i = 0; i < args.length; i++) {
            String arg = args[i];
            buf.append("set_")
                    .append(arg).append("(").append(arg).append("_)");
            _endLine(buf);
        }
        buf.append("}\n");
    }

    private static void _data(String[] args, StringBuffer buf) {
        buf.append("\n/* data */\n");
        for (int i = 0; i < args.length; i++) {
            String arg = args[i];
            buf.append(DefaultType)
                    .append(" ").append(arg).append(" = JSONObject.NULL");
            _endLine(buf);
        }
    }

    private static void _endLine(StringBuffer buf) {
        buf.append(";\n");
    }

    private static String _quotesAround(String msg) {
        return "\"" + msg + "\"";
    }

    private static void _saveToClipboard(StringBuffer buf) {
        StringSelection stringSelection =
                new StringSelection(buf.toString());
        Clipboard clipboard =
                Toolkit.getDefaultToolkit().getSystemClipboard();
        clipboard.setContents(
                stringSelection,
                new ClipboardOwner() {
                    public void lostOwnership(Clipboard clipboard,
                                              Transferable contents) {}
                });
    }
} // end class JSONCodegen
```

## JSON API for JavaME and SE

I've taken some open source libraries and combined them into one package that I use in all my ScreamingToaster software.
I've packaged a Base64 codec, as well as a JSON parser and generator, along with some utility classes to make it really
easy to use. Let me know if you have any issues with the library, and if you can see areas of improvement. You can
[download it here]( {{'assets/json.zip' | relative_url}}).

Here are some important classes:

1. `rpc.ByteBuffer.java` - this class allows you to perform base64 encoding/decoding pretty easily... check out the
   static methods for the class, and it's use becomes apparent.

2. `rpc.json.JSONCodegen.java` - this is the code generator that's listed above.

3. `rpc.json.me.JSONObject.java` - this is the main `JSONObject` class.

4. `rpc.json.me.JSONArray.java` - this is the main `JSONArray` class.
