---
author: Maret Idris
date: 2019-08-25 05:19:43+00:00
layout: post
excerpt: |
  This article a pragmatic guide for developers and designers who want to learn how to build responsive web applications.
layout: post
hero-image: assets/flexbox-hero-image.jpg
title: "A pragmatic guide to designing and building responsive web applications"
categories:
- UXE
- Web
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [Sample project](#sample-project)
- [Implementing a responsive design](#implementing-a-responsive-design)
- [Get the source code](#get-the-source-code)
- [CSS details](#css-details)
  - [Screen width smaller than 600px](#screen-width-smaller-than-600px)
    - [Notes on the code](#notes-on-the-code)
  - [Screen width larger than 600px](#screen-width-larger-than-600px)
  - [Things to note](#things-to-note)
  - [<i class="fas fa-exclamation-circle"></i> Add this for Chrome](#i-classfas-fa-exclamation-circlei-add-this-for-chrome)
- [CSS Grid](#css-grid)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

This is a second article on 2 part series. In this article you will learn how to build a simple example responsive navigation design using Flexbox and media queries.

The first article called [Flexbox: Getting Started (Part 1/2)]({{
'/2017/11/15/flexbox-getting-started-part-1-2/' | relative_url }}) shares fun places to learn Flexbox from.

## Sample project

This is the webpage I created and I have used Flexbox on the header. I have also used CSS Grid on the watch gallery. If you read further I explain why I chose to use CSS Grid in addition to Flexbox (instead of relying on Flexbox alone).

![]({{ 'assets/flexbox-navbar-1.png' | relative_url }})

Let’s look at the CSS Box model and HTML first.

- I have a main container called `header-container,` which I surrounded in a
  yellow border in the images below (so you can see what it contains).
- It includes 2 containers (both of which have blue borders below):
  1. `logo`
  2. `nav`. Inside of the `nav`, there is the common unordered list with the navigation
     page names.

This is what the code looks like.

```html
<header class="header-container">
  <div class="logo">
    <a href="index.html" title="Henne home page">
      <img src="images/logo.png" width="180"
    /></a>
  </div>
  <nav>
    <ul>
      <li><a title="Home">Home</a></li>
      <li><a class="active" title="Watches">Watches</a></li>
      <li><a title="Our Story">Our Story</a></li>
      <li><a title="Contact">Contact</a></li>
    </ul>
  </nav>
</header>
```

I have changed the `flex-direction` to `row`. Which means that the main-axis is
now horizontal.

If you look at the CSS styles (they are all on [Github](https://github.com/MaretIdris/website-flexbox)), you will see that the `display` is set to `grid` and that tells the browser that it’s dealing with a grid. You will also find new property names like `grid-template-columns` and `grid-template-rows`.

```css
.watch-grid {
  display: grid;
  grid-template-columns: 50% 50%;
  grid-template-rows: auto;
  margin-top: 30px;
  justify-content: center;
}
```

CSS Grid shares some of the same property names with Flexbox, like `justify-content` for example, so it’s pretty simple to get started with the CSS Grid. I learnt it from [“CSS Grid First Look"](https://www.lynda.com/CSS-tutorials/CSS-Grid-First-Look/422835-2.html) from Lynda.com. If you are interested in, check out this [awesome video by Morten Rand-Hendriksen](https://youtu.be/txZq7Laz7_4) first.

- About CSS Grid and Chrome. I used percentages (`%`) instead of fractions (`fr`) because Chrome doesn’t display them correctly with fractions. I am not sure why, but if you know why, please let me know.

- If you want to see how all of the CSS Grid code looks like, check it out at [Github](https://github.com/MaretIdris/website-flexbox).
