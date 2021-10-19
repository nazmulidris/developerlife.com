---
author: Nazmul Idris
date: 2021-10-19 14:00:00+00:00
excerpt: |
  This handbook is a reference guide on how to understand and use CSS to build web applications that
  incorporate responsive design using Grid, Flexbox, and media queries. IDEA Ultimate / Webstorm
  project files are provided. This handbook is written as a reference. You can easily jump to the
  section that is relevant to you or read them in any order that you like.
layout: post
title: "CSS responsive design using Grid, Flexbox, and media queries handbook"
categories:
  - TypeScript
  - React
  - Web
---

<img class="post-hero-image" src="{{ 'assets/css-handbook.svg' | relative_url }}"/>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [Great CSS references](#great-css-references)
- [Use CSS Reset](#use-css-reset)
- [Use normalize.css](#use-normalizecss)
- [Difference between body and html (:root)](#difference-between-body-and-html-root)
- [Local vs global scope CSS variables (custom properties)](#local-vs-global-scope-css-variables-custom-properties)
- [Using CSS class pseudo selectors to style child elements of a parent](#using-css-class-pseudo-selectors-to-style-child-elements-of-a-parent)
- [CSS background-image vs img tag](#css-background-image-vs-img-tag)
- [SVG and CSS](#svg-and-css)
- [CSS layouts](#css-layouts)
  - [Box model and CSS sizing](#box-model-and-css-sizing)
  - [Hiding things](#hiding-things)
  - [Flow layout - display: inline, block, inline-block](#flow-layout---display-inline-block-inline-block)
  - [CSS Positioning](#css-positioning)
    - [Absolute and relative positioning](#absolute-and-relative-positioning)
    - [Fixed positioning](#fixed-positioning)
    - [Sticky positioning](#sticky-positioning)
  - [CSS floats](#css-floats)
  - [Flex layout - display: flex](#flex-layout---display-flex)
  - [Grid layout - display: grid](#grid-layout---display-grid)
- [Media queries & responsive design](#media-queries--responsive-design)
- [Modal dialog using CSS](#modal-dialog-using-css)
- [How to add emoji to website in HTML, CSS, or JavaScript](#how-to-add-emoji-to-website-in-html-css-or-javascript)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

This handbook and its accompanying [code][gh-repo] is a reference guide on how to understand and use
CSS to build web applications that incorporate responsive design using Grid, Flexbox, and media
queries.

You can jump directly to any topic in the table of contents that you are curious about in this
handbook, you don't have to read it from start to finish.

> ⚡ The source code for this handbook can be found in this [github repo][gh-repo].

[gh-repo]: https://github.com/nazmulidris/ts-scratch/tree/main/css

## Great CSS references

The following references are really useful when working w/ CSS.

- [Codrops](https://tympanus.net/codrops/css_reference/)
- [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference)
- [webgradients.com](https://webgradients.com)
- [colorhunt.com](https://www.colorhunt.co/)
- [freesvg.org](https://freesvg.org)

## Use CSS Reset

Browsers have defaults (the user agent stylesheet) and you can reset them using CSS Reset. Here's
how you can use it in your React app.

1. Copy the contents of this [CSS file](https://meyerweb.com/eric/tools/css/reset/reset.css) into a
   file named `reset.css`. Feel free to modify this file to suit your needs.
2. Then add `@import "reset.css";` to your app's main CSS file.
3. You can also add entries for elements like `button` and `input` which are not explicitly set by
   the default Reset CSS stylesheet (and thus end up using user agent stylesheet, which is the
   default behavior that we don't want and why we are using Reset CSS in the first place).

## Use normalize.css

Instead of CSS Reset you can also use Normalize.css. Here's the
[github repo](https://github.com/necolas/normalize.css/) for Normalize.css. You can either:

1. Download the CSS file and import it.
2. Import the CDN URLs (from the repo's README) which can be found
   [here](https://classic.yarnpkg.com/en/package/normalize.css). Using the
   [`unpkg`](https://unpkg.com/) CDN as an example,

- Here's the link to v8.0.1: `https://unpkg.com/normalize.css@8.0.1/normalize.css`
- Removing the `@8.0.1` ends up in the latest version of this file, so I am using
  `https://unpkg.com/normalize.css/normalize.css`

3. Or just get the latest version from the github repo itself:
   `https://necolas.github.io/normalize.css/latest/normalize.css`.

Code example

- [HTML](https://github.com/nazmulidris/ts-scratch/tree/main/css/src/project-1/index.html)
- [CSS](https://github.com/nazmulidris/ts-scratch/tree/main/css/src/project-1/index.css)

## Difference between body and html (:root)

In CSS `html` and `:root` are the same. But, there are subtle differences between them and `body`.
One manifests when we try to use `line-height` in `:root` / `html`. It simply does not work. But it
does work when applied to `body`. Here's some
[vague indication](https://css-tricks.com/html-vs-body-in-css/) as to why this might be happening.

So the following doesn't work.

```css
:root {
  line-height: 1.5;
}

html {
  line-height: 1.5;
}
```

And the following does.

```css
body {
  line-height: 1.5;
}
```

Code example

- [HTML](https://github.com/nazmulidris/ts-scratch/tree/main/css/src/project-1/index.html)
- [CSS](https://github.com/nazmulidris/ts-scratch/tree/main/css/src/project-1/index.css)

## Local vs global scope CSS variables (custom properties)

CSS variables are actually called
[`custom properties`](https://tympanus.net/codrops/css_reference/custom-properties/). Usually they
are defined globally in `:root`. However, it possible to define them
[locally](https://css-tricks.com/breaking-css-custom-properties-out-of-root-might-be-a-good-idea). I
don't know if this is necessarily a good idea though. Here's an example.

```css
/* Use local variable, instead of declaring in :root. */
a {
  --my-link-color: lightgray;
  color: var(--my-link-color);
}

yy a:link {
  --my-link-color: teal;
}

a:hover {
  --my-link-color: aquamarine;
}
```

> Please refer to the [responsive design](#media-queries--responsive-design) section to read about
> best practices for using variables and CSS (flexbox, grid, etc).

Code example

- [HTML](https://github.com/nazmulidris/ts-scratch/tree/main/css/src/project-1/index.html)
- [CSS](https://github.com/nazmulidris/ts-scratch/tree/main/css/src/project-1/index.css)

## Using CSS class pseudo selectors to style child elements of a parent

Using CSS class pseudo selectors in order to style child elements of a parent (which has this style
applied) w/out having to manually assign classes to each of these children. Let's say that the
parent element has a class `DottedBox`, which will do this, here's the CSS. Here's a
[video](https://youtu.be/9e-lWQdO-DA) by Kevin Powell where he uses this pattern for flexbox.

1. `.DottedBox { padding: 8pt; border: 4pt dotted cornflowerblue; }`
2. `.DottedBox > * { /* this gets applied to all the children */ }`

## CSS background-image vs img tag

Here's a great
[SO thread](https://stackoverflow.com/questions/492809/when-to-use-img-vs-css-background-image) on
when to use CSS `background-image` vs using the `img` tag. To summarize:

- Use `img` tag when the image is part of the content (foreground).
- Use CSS `background-image` when:
  1. The image simply goes in the background of the content.
  2. The image should not be printed, if printing the "page" is a use case that needs to be
     considered.
  3. You need to overlay multiple images, gradients, other images, and apply transparency in layers
     to the background image, using
     [`background`](https://developer.mozilla.org/en-US/docs/Web/CSS/background) shorthand (here's
     an example
     [index.css](https://github.com/nazmulidris/ts-scratch/tree/main/css/src/project-2/index.css)).

Code example

- [HTML](https://github.com/nazmulidris/ts-scratch/tree/main/css/src/project-3/index.html)
- [CSS](https://github.com/nazmulidris/ts-scratch/tree/main/css/src/project-3/index.css)

## SVG and CSS

It is possible to style SVG w/ CSS, just as you would HTML w/ CSS. However, there are some browser
support issues. Not all the ways are supported by Chrome. There are various ways of importing the
CSS file into the SVG file which is where the browser support issues show up.

So the most reliable way might be to use embedded SVG and then style it inline. Or use JS to set the
style of SVG elements in the DOM.

## CSS layouts

### Box model and CSS sizing

There are 2 box sizing models. The `box-sizing` rule determines whether padding and margin are
included when calculating the width and height of a "box" / element.

1. By default it is set to `box-sizing: content-box;` which does not account for padding and margin.
2. You can set it to `box-sizing: border-box;` which "includes" the padding and margins.

### Hiding things

There are two approaches, here are [more details](https://stackoverflow.com/a/133064/2085356).

1. `display:none` - This simply removes the element from the page, you can only access it via the
   DOM.
2. `visibility:hidden` - The element is rendered and space is allocated on the page, but it is not
   shown.

### Flow layout - display: inline, block, inline-block

The `display` rule determines whether an element is displayed in line or with a line break in a
[`CSS flow layout`](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Flow_Layout). By default
some elements are displayed inline (such as `button`). To change this you can specify.

1. `display: block;` - box takes up entire width of content whether it fills it or not, and adds
   line break. Eg: `h1`, `div`, `p`.
2. `display: inline;` - box takes up min amount of width for content and does not add a line break.
   Eg: `img`, `strong`, `em`.
3. `display: inline-block;` - mash up of the two above, can set the width and height of each
   element, and they can be positioned next to each other.
   > ⚠ Instead of using this, try Grid and Flexbox which are much better!

The `display` rule can also be used to switch to `flex` and `grid` layouts, which also affect the
positioning and sizing of their children elements.

### CSS Positioning

> 💡 Use Grid and Flexbox instead of absolute positioning whenever possible.

- [MDN guide](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Positioning)

#### Absolute and relative positioning

References and notes

- [MDN docs on position](/home/nazmul/files/idea-backgrounds/blurred_unsplash-2020-12-22-61010.jpg)
- The `top`, `right`, `bottom`, and `left` properties determine the final location of positioned
  elements.
- `position: absolute` takes the element out of the flow of the normal page and puts it in its own
  layer. This can be useful for popups and other UI that needs to be in a fixed position on the
  page.
  - This element should be placed in a parent which is also positioned, usually using
    `position: relative`.
  - Normal elements are positioned relative to the viewport.
- You can also use the `z-index` property in order to how the element "stacks up" when changing the
  default positioning of elements.

#### Fixed positioning

- This works in exactly the same way as absolute positioning, with one key difference:
  - whereas absolute positioning fixes an element in place relative to its nearest positioned
    ancestor (the initial containing block if there isn't one),
  - fixed positioning usually fixes an element in place relative to the visible portion of the
    viewport.

#### Sticky positioning

- This is a hybrid between fixed and relative. It allows a positioned element to act like it's
  relatively positioned until it's scrolled to a certain threshold (e.g., 10px from the top of the
  viewport), after which it becomes fixed. This can be used, for example, to cause a navigation bar
  to scroll with the page until a certain point and then stick to the top of the page.

### CSS floats

> ⚠ Use Grid and Flexbox instead of this.

- [MDN Guide](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Floats)

### Flex layout - display: flex

Code example

- [HTML](https://github.com/nazmulidris/ts-scratch/tree/main/css/src/project-4/index.html)
- [CSS](https://github.com/nazmulidris/ts-scratch/tree/main/css/src/project-4/index.css)

References and notes

- [flex-direction: row or column](https://developer.mozilla.org/en-US/docs/Web/CSS/flex-direction).
- The most important thing to note about Flexbox is that in order for Flexbox layout to be activated
  in a hierarchy of DOM nodes, at least one parent must have `display: flex` declared. This is
  called the flex container.
- A DOM element can have Flexbox directives that apply to itself and others that apply only to its
  immediate children. This is called a flex item. Since a DOM element can be a child of another
  Flexbox parent, and itself be a parent for other Flexbox nodes.

Here's the Flexbox parent style called `flexCardsContainer`. This contains flex items which are the
cards themselves. Each `card` itself is a flex parent which contains flex items.

```css
.flexCardsContainer {
  --alpha: 0.3;

  /* Flexbox - for children (cards). */
  display: flex;
  flex-wrap: nowrap;
  align-items: stretch;

  counter-reset: cardCounter;

  padding: var(--defaultPadding);
  color: yellow;
}
```

Here's `.card` an example of a CSS class that is both a parent and child.

```css
.card {
  /* Flexbox - for children (card contents). */
  display: flex;
  flex-direction: column;

  width: fit-content;
  margin: var(--defaultPadding);
  padding: var(--defaultPadding);
  background: rgba(0, 0, 0, var(--alpha));
  border-radius: var(--defaultBorderRadius);

  /* Flexbox - for self. */
  align-items: center;
  justify-content: flex-start;
}
```

Here are some interesting things to note.

- `align-self` overrides default alignment that is set for a flex item on the cross axis.
  - [Docs](https://developer.mozilla.org/en-US/docs/Web/CSS/align-self).
- `flex-basis` is the initial size of a flex item that will be added to if `flex-grow` is specified.
  - [Docs](https://developer.mozilla.org/en-US/docs/Web/CSS/flex-basis).
  - You can also just use the `flex` shorthand and supply `flex-grow`, `flex-shrink`, and
    `flex-basis` values in one go.
    - [Tutorial](https://css-tricks.com/understanding-flex-grow-flex-shrink-and-flex-basis/)

### Grid layout - display: grid

Code example

- [HTML](https://github.com/nazmulidris/ts-scratch/tree/main/css/src/project-5/index.html)
- [CSS](https://github.com/nazmulidris/ts-scratch/tree/main/css/src/project-5/index.css)

References & notes

- [MDN: Basic concepts of Grid layout](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout/Basic_Concepts_of_Grid_Layout)
- [MDN: Difference between grid and flexbox](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout/Relationship_of_Grid_Layout)
- [MDN: Grids](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Grids)
- The main difference between Flexbox and Grid is that the former is designed for 1D layout (either
  main or cross axis) and the latter is for 2D layout (across rows AND columns).
  - It is best to start learning Flexbox first prior to getting into Grid.
  - If you need to control layout by row and column use Grid. It works from the "layout in".
  - If you need to control layout by row or column use Flexbox. It works from the "content out".
- Meaning of [`1fr`](https://stackoverflow.com/a/52861514/2085356)
  - You can specify `minmax(0, 1fr)` in order to change the default behavior of `1f` which is
    `minmax(auto, 1fr)`.
  - [`minmax()`][minmax]
- You can easily mix grid and flexbox. You can have a node that is both a flex item and a grid item.
  Here's an example.

  ```css
  .card {
    /* Grid. */
    align-self: start;

    /* Flexbox - for children (card contents). */
    display: flex;
    flex-direction: column;

    /* Flexbox - for self. */
    align-items: center;
    justify-content: flex-start;
  }
  ```

- [Line positioning shorthands](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout/Basic_Concepts_of_Grid_Layout#line-positioning_shorthands)
  - [`grid-column` shorthand for spanning columns](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-column)
  - [`grid-row` shorthand for spanning rows](https://developer.mozilla.org/en-US/docs/Web/CSS/grid-row)
- [Overlapping cells using z-index](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout/Basic_Concepts_of_Grid_Layout#controlling_the_order)
- [Masonry layout](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout/Masonry_Layout)

[minmax]: https://developer.mozilla.org/en-US/docs/Web/CSS/minmax()

## Media queries & responsive design

- [MDN guide](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Media_queries)
- Make sure the HTML has a
  [`viewport` `meta` tag](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Media_queries#the_viewport_meta_tag)
  . that sets it up to work on mobile browsers.
- CSS variables [don't work here](https://stackoverflow.com/a/40723269/2085356) unless you use a CSS
  preprocessor.
- Usually the directives are something like, something should be applied if:
  - _Greater_ than a certain width: `min-width` or `min-device-width`
    - Eg: if screen is less than `70ch` wide => `@media screen and (max-width: 70ch)`
  - _Less_ than a certain width: `max-width` or `max-width`
    - Eg: if screen is greater than `70ch` wide => `@media screen and (min-width: 70ch)`
- You can match for things like
  - `width`
  - `height`
  - `device-height`
  - `device-width`
  - `orientation`
- For responsive design, the idea is to start w/out any media queries for a mobile first design.
  Then add `min-width` (aka greater than this breakpoint) overrides at breakpoints to handle larger
  screens.
  - You can add a few of these larger and larger breakpoints - perhaps a mobile, mid size, and large
    layout.
  - Each of these "larger screen overrides" simply describes the differences between it and the
    previous size, and they're all based on the mobile first styles.
  - There are no hard and fast rules for these breakpoints. You just have to eyeball it for your app
    / content and make choices for what these exact breakpoint values should be.
- You can use CSS variables in your responsive design. Defining and using these variables in styles
  makes it relatively simple to override them when various breakpoints are hit. Things like changing
  the number of CSS grid columns, choosing which Flexbox direction to use, and even margin, padding,
  and block visibility can be done using them. Here's an example.

  ```css
  .gridCardsContainer {
    --gridNumCols: 1;
    display: grid;
    grid-template-columns: repeat(var(--gridNumCols), 1fr);
  }

  /* If the screen is < 70ch wide. */
  @media screen and (max-width: 70ch) {
    .gridCardsContainer {
      --gridNumCols: 1;
    }
  }

  /* If the screen is > 70ch wide. */
  @media screen and (min-width: 70ch) {
    .gridCardsContainer {
      --gridNumCols: 2;
    }
  }
  ```

## Modal dialog using CSS

Code example

- [HTML](https://github.com/nazmulidris/ts-scratch/tree/main/css/src/project-4/index.html)
- [CSS](https://github.com/nazmulidris/ts-scratch/tree/main/css/src/project-4/index.css)

No JS (only CSS)

- [Tutorial using `dialog` and no JS](https://alligator.io/html/dialog-element/)
- [`dialog` in Chrome 92](https://alligator.io/html/dialog-element/)
- [Advanced animations using `dialog` open and hide](https://codepen.io/geckotang/post/dialog-with-animation)

Keyboard focus and mouse click detection

- [JS detect all clicks on document and use `closest`](https://techstacker.com/close-modal-click-outside-vanilla-javascript/)
  - [`Element.closest()`](https://developer.mozilla.org/en-US/docs/Web/API/Element/closest)
- [SO answer for how to detect click outside element](https://stackoverflow.com/a/38317768/2085356)

Notes

- When a modal dialog is shown it takes up the entire viewport. So if you were to call
  `document.elementFromPoint(x,y)` with any `x` and `y` coordinate in the viewport, the same element
  would be returned (which is the modal dialog)
  > [`elementFromPoint` API docs](https://developer.mozilla.org/en-US/docs/Web/API/Document/elementFromPoint).
- In order to close the dialog if a click occurs outside the dialog is very difficult to do, since
  technically the entire dialog is visible, so all clicks are simply being generated by the dialog.
  So if a click listener was added to document, then then on every click, the `event.target` would
  always be the same modal dialog element.
- By default, pressing the `Esc` key will close the dialog.
- Adding a `focusout` listener on the modal dialog doesn't really do much. In the code example used
  here the focus is actually on the "Ok" button, and as soon as any click or keypress is made the
  focus is taken away from it, and this button is what `event.target` references in the listener. It
  is possible to simply close the dialog when _any_ click or key press occurs, but that seems janky,
  given `Esc` is already hooked up by default to do this.

## How to add emoji to website in HTML, CSS, or JavaScript

Let's say you want to add [this emoji 🔥](https://emojipedia.org/fire/) to your HTML and CSS, with
codepoint `U+1F525`, here are the steps.

> 💡
> [Tutorial - How to add Emoji's in your website, using HTML, CSS or JavaScript](https://dev.to/beumsk/how-to-add-emoji-s-in-your-website-using-html-css-or-javascript-4g6g)

- CSS

  You must replace the `U+` with `\0` in the codepoint. So instead of `U+XXYYZZ` you use `\0XXYYZZ`

  ```css
  .card h3:before {
    counter-increment: cardCounter;
    content: "\01F525 \01F5C3 \01F4C7 Card #"counter(cardCounter) " - ";
  }
  ```

- HTML

  You must replace the `U+` with `&#x`. So instead of `U+<code>` you use `&#x<code>`.

  ```html
  <h3>This is a modal dialog &#x1F44B</h3>
  ```
