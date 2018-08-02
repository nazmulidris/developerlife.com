---
author: Maret Idris
authorlink: https://maretidris.com
date: 2017-11-16 05:19:43+00:00
layout: post
excerpt: |
  This is a second article on 2 part series. In this article you will learn
  how to build a simple example responsive navigation design using Flexbox and media
  queries.
layout: post
hero-image: assets/flexbox-hero-image.jpg
title: 'Flexbox: Building a navigation bar (Part 2/2)'
categories:
- UX Engineering
- Web Design
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Outcome](#outcome)
- [Responsive](#responsive)
- [Get the code](#get-the%C2%A0code)
- [**Code**](#code)
- [Let’s look at the CSS](#lets-look-at-the%C2%A0css)
  - [Screen width smaller than 600px](#screen-width-smaller-than%C2%A0600px)
  - [Screen width bigger than 600px](#screen-width-bigger-than%C2%A0600px)
    - [Things to note](#things-to%C2%A0note)
- [CSS Grid](#css-grid)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

This is a second article on 2 part series. In this article you will learn how to build a simple example responsive navigation design using Flexbox and media queries.

The first article called [Flexbox: Getting Started (Part 1/2)](https://medium.com/@maret.idris/flexbox-getting-started-part-1-2-2e101815d405) shares fun places to learn Flexbox from.

# Outcome

This is the webpage I created and I have used Flexbox on the header. I have also used CSS Grid on the watch gallery. If you read further I explain why I chose to use CSS Grid in addition to Flexbox (instead of relying on Flexbox alone).

![](https://cdn-images-1.medium.com/max/1600/0*wwUCTkAks3-Xni5_.)

# Responsive

This is what the header looks like on a screen width smaller than 600px. The logo is above the navigation.

![](https://developerlifecom.files.wordpress.com/2017/11/03a36-1nmlorgsjils4eytvdwo2ca.png)

The same header looks like this on on a screen width 600px and larger. The logo and navigation are beside each other, centered vertically.

![](https://developerlifecom.files.wordpress.com/2017/11/adf4a-12ulqaq9svj21lptymvnd9w.png)

# Get the code

You can download the source code for the HTML and CSS for this project [here](https://github.com/MaretIdris/website-flexbox).

# **Code**

Let’s look at the CSS Box model and HTML first. I have a one main container called header-container, which I surrounded in a yellow border in the images below (so you can see what it contains). It includes 2 containers, one for the logo and another one for nav, both of which have blue borders below. Also inside of the nav, there is the common unordered list with the navigation page names.

![](https://cdn-images-1.medium.com/max/1600/0*7s450T6A9DJsjSDx.)

![](https://cdn-images-1.medium.com/max/1600/0*Rfet3K-PKkE2eNT0.)

This is what the code looks like.

    <header class=”header-container”>

     <<strong class="markup--strong markup--pre-strong">div</strong> class=”logo”>

       <<strong class="markup--strong markup--pre-strong">a</strong> href=”index.html” title=”Henne home page”>

       <<strong class="markup--strong markup--pre-strong">img</strong> src=”images/logo.png” width=”180"></<strong class="markup--strong markup--pre-strong">a</strong>>

     </<strong class="markup--strong markup--pre-strong">div</strong>>

     <<strong class="markup--strong markup--pre-strong">nav</strong>>

       <<strong class="markup--strong markup--pre-strong">ul</strong>>

         <<strong class="markup--strong markup--pre-strong">li</strong>><<strong class="markup--strong markup--pre-strong">a</strong> title=”Home”>Home</<strong class="markup--strong markup--pre-strong">a</strong>></<strong class="markup--strong markup--pre-strong">li</strong>>

         <<strong class="markup--strong markup--pre-strong">li</strong>><<strong class="markup--strong markup--pre-strong">a</strong> class=”active” title=”Watches”>Watches</<strong class="markup--strong markup--pre-strong">a</strong>></<strong class="markup--strong markup--pre-strong">li</strong>>

         <<strong class="markup--strong markup--pre-strong">li</strong>><<strong class="markup--strong markup--pre-strong">a</strong> title=”Our story”>Our Story</<strong class="markup--strong markup--pre-strong">a</strong>></<strong class="markup--strong markup--pre-strong">li</strong>>

         <<strong class="markup--strong markup--pre-strong">li</strong>><<strong class="markup--strong markup--pre-strong">a</strong> title=”Contact”>Contact</<strong class="markup--strong markup--pre-strong">a</strong>></<strong class="markup--strong markup--pre-strong">li</strong>>

       </<strong class="markup--strong markup--pre-strong">ul</strong>>

     </<strong class="markup--strong markup--pre-strong">nav</strong>>

    </<strong class="markup--strong markup--pre-strong">header</strong>>

# Let’s look at the CSS

Because I have two layouts, I used a media query to create a breakpoint and change the CSS styling.

## Screen width smaller than 600px

If the screen width is between 0px and 599px, the following CSS is applied.

    .header-container {

     display: flex;

     flex-direction: column;

     border-bottom: 1px solid #F2F2F2;

     padding: 2.3em 0;

    }

    .logo {

     margin-left: 5%;

    }

    .logo img {

     display: block;

    }

    nav {

     margin: 1.5em 0 0 5%;

    }

    header ul li {

     display: inline-block;

     padding: 0 1.4em 0 0;

     font-size: 0.9em;

    }

    header ul li a {

     text-decoration: none;

     color: #7D7C7D;

    }

    li a.active {

     color: #000000;

     border-bottom: 2px solid #000000;

     font-weight: 300;

    }

    li a:hover {

     color: #B6B6B6;

    }

There is a `header-container`, which is a **flex container.** The browser knows that it’s a flex container, because it’s display is set to flex. `flex-direction` is set to `column`. This means that the main-axis for this layout is vertical and cross-axis is horizontal. Then there is a bunch of extra styling below, which is not Flexbox.

![](https://cdn-images-1.medium.com/max/1600/0*XxSyTjcaZJDun3Kx.)

## Screen width bigger than 600px

Whenever the screen is 600px or bigger, another media query is applied. You’ll notice that on header-container I haven’t declared display: flex; and that’s because the way I set up the media query. The previous styles still apply and I am overwriting the lines of code that I want changed.

I have changed the `flex-direction` to `row`. Which means that the main-axis is now horizontal.

![](https://cdn-images-1.medium.com/max/1600/0*_gKGJJmESjHQH0gd.)

Also added `justify-content` property with a value of space-between. This makes sure the logo and nav containers are on the opposite ends of the header-container.

I used `align-self` on the nav, which is a **flex item**. `align-self` is a **flex item property** and it centers the cross-axis. Which in my case is the vertical alignment, because my main axis is horizontal (flex-direction: row;).

    @media screen and (min-width : 600px) {

     .header-container {

       flex-direction: row;

       justify-content: space-between;

     }

    .logo {

       margin-left: 2.3em;

     }

     nav {

       align-self: center;

       margin: 0 0.8em 0 0;

     }

    }

### Things to note

  * If you add an image to HTML, it includes a tiny bit of space on the bottom of it. In order to remove it, use `display` property and set its value to `block`. I used it on `logo img` and also on `watch-image`.

  * I could have used Flexbox on the `nav` but I would have ended up with 2 extra lines of code, so I decided not to. If you want to use Flexbox, it will look like this:

    header ul {

     display: flex;

     flex-flow: row wrap;

     list-style-type: none;

    }

    header ul li {

     padding: 0 1.4em 0 0;

     font-size: 0.9em;

    }

Instead I used `display: inline-block`;. inline-block places all the nav titles beside each other, no need to use Flexbox. By default HTML would have placed nav titles below one another.

    header ul li {

     display: inline-block;

     padding: 0 1.4em 0 0;

     font-size: 0.9em;

    }

  * If you want the media queries to show up properly in Chrome, add this meta-data tag to the head element of your HTML document. If you don’t do this, then your HTML will not be responsive on the most popular browser in the world!

    <! — https://css-tricks.com/snippets/html/responsive-meta-tag/-->

    <<strong class="markup--strong markup--pre-strong">meta</strong> name=”viewport” content=”width=device-width”>

# CSS Grid

Originally I wanted to create the image gallery using Flexbox. I struggled with it for a while but I couldn’t get the watches in watch-grid to align left, while having the same amount of space between them. I also went through other people’s examples, but none of them worked for this case without hacks. So I ended up using CSS Grid.

If you look at the CSS styles (they are all on [Github](https://github.com/MaretIdris/website-flexbox)), you will see that the `display` is set to `grid` and that tells the browser that it’s dealing with a grid. You will also find new property names like `grid-template-columns` and `grid-template-rows`.

    .watch-grid {

     display: grid;

     grid-template-columns: 50% 50%;

     grid-template-rows: auto;

     margin-top: 30px;

     justify-content: center;

    }

CSS Grid shares some of the same property names with Flexbox, like `justify-content` for example, so it’s pretty simple to get started with the CSS Grid. I learnt it from [“CSS Grid First Look”](https://www.lynda.com/CSS-tutorials/CSS-Grid-First-Look/422835-2.html) from Lynda.com. If you are interested in, check out this [awesome video by Morten Rand-Hendriksen](https://youtu.be/txZq7Laz7_4) first.

  * About CSS Grid and Chrome. I used percentages (%) instead of fractions (fr) because Chrome doesn’t display them correctly with fractions. I am not sure why, but if you know why, please let me know on the comments below.

  * If you want to see how all of the CSS Grid code looks like, check it out at [Github](https://github.com/MaretIdris/website-flexbox).



