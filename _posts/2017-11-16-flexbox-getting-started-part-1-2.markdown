---
author: Maret Idris
authorlink: https://maretidris.com
date: 2017-11-16 04:53:44+00:00
layout: post
excerpt: |
  The goal of this series of articles is to help you to learn Flexbox in a
  fun interactive way and then help you to build simple real life examples using Flexbox.
layout: post
title: 'Flexbox: Getting started (Part 1/2)'
hero-image: assets/flexbox-hero-image.jpg
categories:
- UX Engineering
- Web Design
---
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [About Flexbox](#about-flexbox)
- [Terminology](#terminology)
- [Practice by Playing](#practice-by%C2%A0playing)
  - [Flexbox Froggy](#flexbox-froggy)
  - [Flexbox Playground](#flexbox-playground)
- [Summary](#summary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction 

The goal of this series of articles is to help you to learn Flexbox in a fun interactive way and then help you to build simple real life examples using Flexbox.

  1. In this first article you will find great resources to get started with Flexbox.

  2. [In the second article]({{ '/2017/11/15/flexbox-building-a-navigation-bar-part-2-2/' | 
  relative_url }}) you will learn how to build a simple example responsive 
  navigation design using Flexbox and media queries.

In order to benefit the most of this content, you need to have a basic understanding of [HTML](https://developer.mozilla.org/en-US/docs/Learn/HTML) and [CSS](https://developer.mozilla.org/en-US/docs/Web/CSS). If you have this, keep reading.

## About Flexbox

Flexbox is a CSS [layout mode](https://developer.mozilla.org/en-US/docs/Web/CSS/Layout_mode) which makes it easier to create responsive websites. It allows us to effortlessly manipulate the child elements (also called flex items) of a flex container. For example, you can:

  * Reorder the flex items.

  * Easily place items in a row beside each other and then by adjusting the browser window, the space between them will also adjust.

  * Make those items wrap to the next line (inside the container) when screen gets smaller etc.

![]({{ 'assets/flexbox-1.png' | relative_url }})

Flexbox is not the solution to everything by itself. It’s like a team player in a great soccer game. Every player is valuable, but they all play a different role. If one player has to play for 2 positions, the team is compromised. The same applies to building. If you try to use Flexbox for everything (and end up nesting it a lot) the page will be compromised, and will be harder to manage. While you can get away with that, there are tools out there that will help you to make this process easier (such as CSS Grid).

## Terminology

I have learnt most of what I know about front-end development from [Lynda.com](https://www.lynda.com/CSS-tutorials/CSS-Flexbox-First-Look/116352-2.html), including Flexbox. Because Flexbox is quite simple to understand, I don’t think it is necessary to take an online course. You will be able to capture it faster by reading and understanding the basics. Then jump straight into the code and learn by practicing.

![]({{ 'assets/flexbox-2.png' | relative_url }})

Image by Joni Bologna

  1. Here’s a [cheat sheet by Joni Bologna aka Joni Trythall](http://jonibologna.com/content/images/flexboxsheet.pdf). She wrote and illustrated children’s books as a hobby and you can see that design in her cheat sheet. It’s fun and simple.

  2. If you want something more sophisticated or just double down on your knowledge, check out [The Ultimate Flexbox Cheat Sheet by Sean Fioritto](http://www.sketchingwithcss.com/samplechapter/cheatsheet.html). You will also find snippets of code which work in all browsers.

  3. To understand Flex items and how they behave, check out [Chris Wright’s Flexbox Adventures](https://chriswrightdesign.com/experiments/flexbox-adventures/#).

## Practice by Playing

### Flexbox Froggy

![]({{ 'assets/flexbox-3.png' | relative_url }})

With[ Flexbox Froggy](http://flexboxfroggy.com/) you can play a game and learn the terminology at the same time.

It was created by [Thomas Park](https://github.com/thomaspark), researcher at Drexel University. He is one of the collaborators of [openHTML](http://openhtml.org/), a collaborative research project aimed at designing better tools and practices for learning web development.

### Flexbox Playground

![]({{ 'assets/flexbox-4.png' | relative_url }})

Have fun on the [Flexbox Playground](https://demos.scotch.io/visual-guide-to-css3-flexbox-flexbox-playground/demos/) to see what will happen when you will play with flex container and flex item properties. It was created by [Dimitar Stojanov](https://twitter.com/justd100), founder of [Invoicebus](https://invoicebus.com/).

## Summary

I hope you will have fun while learning Flexbox.

In the next article, called [Flexbox: Building a navigation bar (Part 2/2)]({{ '/2017/11/15/flexbox-building-a-navigation-bar-part-2-2/' | relative_url }}) you will learn a one way how to build a simple navigation using Flexbox and media queries.