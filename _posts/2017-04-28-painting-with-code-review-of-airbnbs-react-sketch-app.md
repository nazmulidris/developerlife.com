---
author: Nazmul Idris
date: 2017-04-28 23:47:59+00:00
excerpt: |
  Design engineering is becoming a thing. Airbnb has created something amazing
  - react-sketchapp. This library can generate Sketch artifacts using Javascript and
  React as a starting point. This article will show you what it is, who this is for,
  and why it matters.
layout: post
title: "Painting with code - review of Airbnb's React Sketch.app plugin"
hero-image: assets/airbnb-hero.png
categories:
- UXE
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [What is this thing?](#what-is-this-thing)
  - [Using the library](#using-the-library)
  - [Hot reloading goodness](#hot-reloading-goodness)
- [Playing with basic-setup](#playing-with-basic-setup)
- [Playing with styleguide](#playing-with-styleguide)
- [Playing with profile-cards](#playing-with-profile-cards)
- [Playing with foursquare-maps](#playing-with-foursquare-maps)
- [Who is this for?](#who-is-this-for)
- [Why do this?](#why-do-this)
- [Closing thoughts](#closing-thoughts)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

Airbnb [recently released](http://airbnb.design/painting-with-code/) `react-sketchapp` on
[GitHub](http://airbnb.io/react-sketchapp) a few days ago. It wasn't something that I was expecting to find in the
design and engineering world. It has taken 2 things and merged them into one!

The intersection of design and engineering has been near and dear to my heart for a very long time, so I had to give it
a try. I also read a lot of people's reactions to this library online, and a majority of engineers asked: "isn't this
done backwards?"

This is a fair question to ask, given how design and development are done for the most part today. There is a gap
between design and engineering, and there shouldn't be. I've written about this on developerlife.com
([`#design-engineering`](https://developerlife.com/category/design-engineering/)) and have run
[Design for Humans meetups](https://www.meetup.com/UX-Design-for-Developers/events/238604432/) in Silicon Valley, on
this topic as well.

I'm really glad to see that there are other leaders in the design and development community that are changing things for
the better, so we can build better products by fostering more effective communication and workflow in very large teams.

Having said this, let's get started with what this thing is, why it was made, and what it can do!

## What is this thing?

The best way to get a handle on this amazing library is to download it from GitHub and start messing with the examples
to see what it does. I have done just that, and here are some links for this tutorial. These examples are incredibly
well written and are easy to understand and modify.

- [GitHub repo](https://github.com/r3bl-alliance/react-sketchapp-airbnb) that I've cloned and modified some of the
  examples for this tutorial.
- [Sketch file](https://github.com/r3bl-alliance/react-sketchapp-airbnb/tree/master/scratch_files) that I generated
  using `react-sketchapp`.

### Using the library

The way to use this library is to have the Sketch app open (any version > 43 will do). It's important to have a document
open to start!

I would recommend that you create a new document and leave it open in Sketch with the keyboard focus on the Page that
you want `react-sketchapp` to modify!

Here's the basic workflow for running each example. Go to the example sub-folder, eg:
[`basic-setup`](https://github.com/r3bl-alliance/react-sketchapp-airbnb/tree/master/examples/basic-setup) and then run
the following.

    npm install
    npm run render

When you run `npm run render` on the examples, they will dump their output to Sketch and will render to whatever active
page is open in Sketch.

### Hot reloading goodness

You can also do something pretty amazing. You can run multiple examples at once, and `react-sketchapp` has a filewatcher
that will re-render the output to Sketch! This is incredible! It's like hot loading / reloading, but for Sketch as the
head-unit or output device that's being rendered to! Mind blown!

Here you can see that I have 4 examples that I'm modifying in my IDE -
[basic-setup](https://github.com/r3bl-alliance/react-sketchapp-airbnb/tree/master/examples),
[styleguide](https://github.com/r3bl-alliance/react-sketchapp-airbnb/tree/master/examples/styleguide),
[profile-cards](https://github.com/r3bl-alliance/react-sketchapp-airbnb/tree/master/examples/profile-cards), and
[foursquare-maps](https://github.com/r3bl-alliance/react-sketchapp-airbnb/tree/master/examples/foursquare-maps). And as
I would make changes to the source code in each of these examples, and save it, they would immediately re-render into
Sketch.

I just had to have the right page open in Sketch that corresponds to each example. Also, I ended up creating 4 pages in
Sketch before I got started, to hold the rendered output for each of these 4 example projects rendering.

![]({{ 'assets/airbnb-1.png' | relative_url }})

Again, make sure to have the correct page open in Sketch. You can always use the undo function in Sketch to get to your
previous state.

## Playing with basic-setup

This is a very simple project that just displays a set of Swatches in a Sketch page. However, these swatches are not
generted by hand. They are generated by the code running in the file
[`my-command.js`](https://github.com/r3bl-alliance/react-sketchapp-airbnb/blob/master/examples/basic-setup/src/my-command.js)!
Here's what the Sketch output looks like when you start.

![]({{ 'assets/airbnb-2.png' | relative_url }})

I changed a few things in this JS file. I simply created a new color called Blue and replaced Haus with it.

```javascript
export default (context) => {
  const colorList = {
    //Haus: '#F3F4F4',
    Blue: '#2ccce4',
    Night: '#333',
    Sur: '#96DBE4',
    'Sur Dark': '#24828F',
    Peach: '#EFADA0',
    'Peach Dark': '#E37059',
    Pear: '#93DAAB',
    'Pear Dark': '#2E854B',
  };
```

When you make this change and save the file (assuming that you have `npm run render` still running) the Sketch page will
change before your very eyes and will produce the following output.

![]({{ 'assets/airbnb-3.png' | relative_url }})

This is a really simple thing, but the key here is that code changes that are made in Javascript end up generating the
Swatches artboard in Sketch!

The code is eerily familiar as well. It just kind of makes sense, having stared at React and React Native code for a
while :).

## Playing with styleguide

This example generates a styleguide in Sketch from data. I modified 2 files in here to make some minor changes to the
generated styleguide. Here's what it looked like before the changes.

![]({{ 'assets/airbnb-4.png' | relative_url }})

I made the following minor changes to the following files:

[`designSystem.js`](https://github.com/r3bl-alliance/react-sketchapp-airbnb/blob/master/examples/styleguide/src/designSystem.js) -
I simply added swapped out Haus for Blue again in the `colors` object.

```javascript
export const colors = {
  Blue: "#2ccce4",
  //Haus: '#F3F4F4',
  Night: "#333",
  Sur: "#96DBE4",
  "Sur a11y": "#24828F",
  Peach: "#EFADA0",
  "Peach a11y": "#E37059",
  Pear: "#93DAAB",
  "Pear a11y": "#2E854B"
};
```

[`main.js`](https://github.com/r3bl-alliance/react-sketchapp-airbnb/blob/master/examples/styleguide/src/main.js) - I
simply added some text to a `Label` component.

```html
<label>
  This is an example react-sketchapp document, showing how to render a styleguide from a data representation of your
  design system. This is pretty amazing!
</label>
```

And this is what it looked like after these changes were made. `npm run render` was still running on this folder so I
could see these changes happen as soon as I hit save in my IDE and had the right page open in Sketch.

![]({{ 'assets/airbnb-5.png' | relative_url }})

## Playing with profile-cards

This is a much more interesting example of generating the Sketch artboards using data. This example generates a page in
Sketch that holds a set of profile cards. The magic is that these cards are generated from the data that's provided to
the app.

![]({{ 'assets/airbnb-6.png' | relative_url }})

I made changes to the `DATA` object in
[`main.js`](https://github.com/r3bl-alliance/react-sketchapp-airbnb/blob/master/examples/profile-cards/src/main.js).

```javascript
export default (context) => {
  const DATA = [
    {
      screen_name: 'nazmulidris',
      name: 'Nazmul Idris',
      description: 'Developer | Designer | Communicator | Leader | Entrepreneur',
      location: 'Mountain View, CA',
      url: 'nazmulidris.com',
      profile_image_url: 'https://i2.wp.com/developerlifecom.files.wordpress.com/2017/04/nazmul.png?ssl=1&w=450',
    },
    {
      name: 'maret',
      screen_name: 'Maret Eiland',
      description: 'Full Stack Product Designer | Coding ninja',
      location: 'Mountain View, CA',
      url: 'r3bl.com',
      profile_image_url: 'https://lh5.googleusercontent.com/R_tQfrMcNL-ofrq_T-1U-XnCdcg-fP05G-YMOfv61DegG-_74pol_6SNUhKwlRbx4fztabL7=w271',
    },
  ];
```

I've been extolling the virtue of designing with data
[for sometime now](http://developerlife.com/2017/04/26/flexbox-layouts-and-lists-with-react-native/). And it is awesome
to see this approach being applied to generating Sketch artboards for design systems! Things like this reinforce habits
that people, and cultivating a habit of starting from data for designing and prototyping is a really good thing to do!

## Playing with foursquare-maps

This is the most interesting and powerful example that I found in the set of examples and illustrates the power of what
`react-sketchapp` can do that is above and beyond what we might expect today. This is what it looks like after I
modified it.

![]({{ 'assets/airbnb-7.png' | relative_url }})

I changed the following things in the source code.

[`getVenues.js`](https://github.com/r3bl-alliance/react-sketchapp-airbnb/blob/master/examples/foursquare-maps/src/getVenues.js) -
This is where you can specify which location and the search term that is passed to the Foursquare API in order to get
some results which are assembled in the artboard by this awesome example. I changed the latitude and longitude to
Mountain View, CA, and the search term to "`whole foods`" 😃. Here's the code.

```javascript
export default (platformFetch) => {
  const query = 'whole foods';
  const latitude = '37.386051';
  const longitude = '-122.083855';
  ...
}
```

[`App.js`](https://github.com/r3bl-alliance/react-sketchapp-airbnb/blob/master/examples/foursquare-maps/src/App.js) -
This is where the main app is setup using `[react-primitives](https://github.com/lelandrichardson/react-primitives)`. I
swapped out a color that was being used in multiple places, and replaced it with a variable that contains that color.
It's a [good idea](http://developerlife.com/2017/04/15/navigation-and-styling-with-react-native/) to build stylesheets
in this modular way. Here's the code.

```javascript
const myColor = `#697689`;

const styles = StyleSheet.create({
  container: {
    width: 375,
    height: 667,
    backgroundColor: '#fefefe',
    borderWidth: 2,
    borderColor: myColor,
    borderRadius: 4,
    overflowY: 'scroll',
  },
  text: {
    fontFamily: 'Helvetica',
    fontSize: 24,
    lineHeight: 24,
    color: myColor,
    textAlign: 'center',
  },
  rowWrapper: {
    padding: 16,
    backgroundColor: '#FFF',
    borderBottomWidth: 2,
    borderBottomColor: myColor,
  },

```

## Who is this for?

The approach that Airbnb has taken with `react-sketchapp` doesn't apply to small teams of designers and developers. It
is built for teams that are huge, where gains in efficiency can be made when friction is removed in the workflow that
isn't even seen in smaller teams.

## Why do this?

Conventional wisdom will tell you that wireframes are designed by designers in Sketch, and then they are handed off to
developers. Developers then use something like [Zeplin](https://zeplin.io/) and then get redlines which they manually
translate to code (using Flexbox layout or some other type of layout engine that isn't supported in Sketch) with a lot
guesswork.

When code changes, or the design changes in Sketch, iterations have to be made in order to bring the code (for the web
apps, mobile apps, etc) and the design assets (Sketch files, etc) back into sync. These changes can be very costly when
there is a really complex design system and methodology in place, and drawing tools like Sketch are notoriously bad with
version control. Code on the other hand is very well suited for version control.

Prototyping with data is also a big hassle. Getting real data to inject into wireframes in Sketch, rather than
boilerplate content fillers is difficult to do, especially with complex data that comes from multiple sources.

Inject React into this mix. React is an amazing piece of technology from Facebook which allows easy development of
components that are rendered on browsers, and with react-native, on mobile devices. React Native is a fascinating blend
of web and mobile technology, where JS code can manipulate native view hierarchies, and not a DOM tree! All the
optimizations made in React by using a virtual DOM is retained in React Native as an example, and you can even plug into
native code on iOS and Android where needed.

So the genius idea from Airbnb's design engineering team was to create some code and use React to target Sketch as the
output device! Instead of rendering output to DOM (as React does), or native view hierarchies (on Android or iOS) like
React Native does, `react-sketchapp` targets Sketch as the device that things `render()` to! This means that live
reloading works in this context as well. So you can change some code in Javascript that's using `react-sketchapp` and it
will output these changes to currently active and open Sketch page! You have to try it to see how awesome this is!

Here are some use cases that are addressed nicely by this library:

Integration with data. It's really difficult to perform complex queries against multiple data sources in order to get
raw data that will be used as content for Sketch wireframes. And instead of using fake data, the best thing to do is use
real data. And be able to change parameters to feed to API calls to generate this data and then seamlessly integrate
this with drawings in sketch. This is what using Javascript to make RESTful API calls, get the data, process it, and
then generate the UI to render it into Sketch is so powerful!

Using Flexbox to generate Sketch components now becomes a possibility. The process of creating layouts in Sketch has
nothing to do with Flexbox layouts. Once you're done with a drawing in Sketch, the guesswork begins to move it to
Flexbox and code (for React or React Native, or even Android and iOS native layout managers). Using this library, you
can use Flexbox layouts in code to generate the Sketch components themselves. Without this library, you would have to
resize components manually in Sketch and then simulate different target sizes. Now, you can do this in code,
effortlessly, and generate many different components that are sized for different target display sizes.

If you have a sophisticated design system that's driven by data that specifies things like typography, color, spacing,
components that work across multiple platforms, and screen sizes, and human languages, then it is a painful thing to
match your Sketch artifacts to changes in your system. This can lead to the system getting out of sync with the current
truth! This can lead to terrible consequences when your product apps are using different spacing and typography as an
example, than what is specified in your design system. By literally generating the design system assets dynamically from
code and preserving the source of truth in this domain specific language that goes from the data and generates the
design system, then you are well on your way to efficiency gains in large teams. Also using code has the benefit of
being able to use version control systems, which design tools aren't very good with.

Leverage the code that's already written and in production as the basis for generating the Sketch artifacts. The code
that's used to generate the artifacts for Sketch is related to the code that's used in the web, or mobile apps. This
minimizes the sources of truth in the system, so that it's harder for things to go out of sync between production code
and design artifacts. The workflow of creating React components and passing data in as properties is very similar to the
Sketch workflow of using components and putting data into them. By unifying them, it reduces an entire layer of
abstraction that previously existed (in projects that don't use something like this).

## Closing thoughts

Airbnb has done a pretty amazing thing to bring Design Engineering to light. I've spent quite a few years doing advocacy
around why developers need to be engaged in the design narrative, and why designers need to learn some coding in order
to be able to more effectively communicate with developers ([Udacity](http://bit.ly/uxdclass),
[YouTube](http://bit.ly/uxdplaylist), [Meetup](http://bit.ly/uxdmeetup)).

Design is everyone's responsibility, and only by working together more effectively and taking ownership of outcomes that
impact our users, and the business will we be able to create amazing products.
