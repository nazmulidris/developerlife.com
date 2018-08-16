---
author: Nazmul Idris
date: 2018-08-15 5:00:00+00:00
excerpt: |
  Vue is a competitor to React. This tutorial serves as a brief introduction
  to Vue, and getting started with it without using Webpack or Babel.
layout: post
hero-image: assets/vue-hero.svg
title: "Getting started with Vue.js"
categories:
- Web
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [Introduction](#introduction)
- [Getting started quickly (single HTML file)](#getting-started-quickly-single-html-file)
  - [Basic usage](#basic-usage)
  - [v-for directive](#v-for-directive)
  - [v-on directive](#v-on-directive)
  - [v-model directive](#v-model-directive)
- [Getting started without Webpack](#getting-started-without-webpack)
  - [Single origin policy](#single-origin-policy)
  - [Structure of the project](#structure-of-the-project)
  - [Run it](#run-it)
  - [Vue components](#vue-components)
    - [Import the ES6 module](#import-the-es6-module)
    - [Create the ES6 module](#create-the-es6-module)
    - [Notes on the code](#notes-on-the-code)
- [Get the code](#get-the-code)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

Vue.js is a reactive progressive framework that allows the creation of Javascript apps. It
is very similar to React, which I've written about on developerlife.com before. I 
wanted to try Vue out to see how it felt. And I really like it 😃.

Unlike React, it doesn't require you to invest a lot of upfront effort in learning 
it's ways. And it can scale up or down depending on your needs, which makes it easy
to get started with, but can also handle demanding use cases when you get there. Also
it's published under the MIT license ([which is React is too now](https://medium.freecodecamp.org/facebook-just-changed-the-license-on-react-heres-a-2-minute-explanation-why-5878478913b2)).

## Getting started quickly (single HTML file)

The simplest way to get started with Vue is to grab the development version script for
it and add it to the `head` tag of your HTML file.

```html
<script src="https://cdn.jsdelivr.net/npm/vue/dist/vue.js"></script>
```

Then you can start Vue code inside the HTML file inside of `script` tags. 

```html
<script>
    new Vue(
        {
            el: '#app_basic',
            data: {
                message: '🐵 Hello World 🔮',
                timestamp: `Timestamp ${new Date().toLocaleString()}`,
            }
        });
</script>
```

And have the Vue code connect up with an existing element on your HTML page.

{% raw %}
```html
<div id="app_basic" v-bind:title="timestamp" class="experiment-block">
    {{ message }}
</div>
```
{% endraw %}

And that's all there is to it, in order to get going in your browser without
messing with Webpack or Babel, or anything else!

### Basic usage 

Here's the full HTML file w/ this basic example of using Vue. 
- In order to swap out the `div` with id `#app_basic` with the Vue code, you have
to tell the `Vue` object you create what this element id is, eg: `el: '#app_basic'`.
- When you change the `data.message` object, then Vue will update the DOM with 
its new value. This is what makes it 'reactive'.

{% raw %}
```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Vue Test</title>

    <!-- This is a development version of Vue.js! -->
    <script src="https://cdn.jsdelivr.net/npm/vue/dist/vue.js"></script>

    <!-- import stylesheet -->
    <link rel="stylesheet" href="styles.css">

    <!-- Google fonts -->
    <link href="https://fonts.googleapis.com/css?family=Open+Sans" rel="stylesheet">

</head>

<body>

<!-- Basic usage -->

<div id="app_basic" v-bind:title="timestamp" class="experiment-block">
    {{ message }}
</div>

<script>
    new Vue(
        {
            el: '#app_basic',
            data: {
                message: '🐵 Hello World 🔮',
                timestamp: `Timestamp ${new Date().toLocaleString()}`,
            }
        });
</script>

</body>

</html>
```
{% endraw %}

### v-for directive

Here are some more code snippets of basic Vue usage (the `v-for` directive).

{% raw %}
```html
<!-- Loops -->
<div id="app_loops" class="experiment-block">
    <ol>
        <li v-for="todo in todos"> {{ todo.text }} </li>
    </ol>
</div>

<script>
    new Vue(
        {
            el: '#app_loops',
            data: {
                todos: [
                    {text: 'Learn JavaScript'},
                    {text: 'Learn Vue'},
                    {text: 'Build something awesome'},
                ],
            }
        });
</script>
```
{% endraw %}

### v-on directive

Here are some more code snippets of basic Vue usage (the `v-on` directive).

{% raw %}
```html
<!-- OnClick -->
<div id="app_onclick" class="experiment-block">
    <span>{{ message }}</span>
    <button v-on:click="randomGenerate">Click me</button>
</div>

<script>
    new Vue(
        {
            el: '#app_onclick',
            data: {
                message: "Click me (random number generate)",
            },
            methods: {
                randomGenerate() {
                    this.message = Math.random();
                },
            }
        });
</script>
```
{% endraw %}

### v-model directive

Here are some more code snippets of basic Vue usage (the `v-model` directive). With
data binding support, Vue keeps the the underlying data (`data.value`) in sync
with the UI element (`input`).

{% raw %}
```html
<!-- Data binding -->
<div id="app_model" class="experiment-block">
    <p>{{ value }}</p>
    <input v-model="value">
</div>

<script>
    new Vue(
        {
            el: '#app_model',
            data: {
                value: "Some string data"
            }
        });
</script>
```
{% endraw %}

To learn more about Vue, check out their excellent documentation.
- [Vue.js Guide](https://vuejs.org/v2/guide/)
- [Events](https://vuejs.org/v2/guide/events.html#Event-Modifiers)
- [Forms](https://vuejs.org/v2/guide/forms.html)
- [Components](https://vuejs.org/v2/guide/components.html)

## Getting started without Webpack

So far, all the work we have done has been self contained in a single HTML file. What
if you wanted to modularize your code and create ES6 modules, etc? Well, we would
normally have to use something like Webpack at this point, and use it to combine all
the JS files, transpile, and minify them. However, for the purposes of getting started
quickly, I wanted to do without Webpack for now. 

Vue has a [CLI npm module](https://cli.vuejs.org/) that makes
it easy to generate project stubs w/ Webpack already configured and ready to go.

However, we are going to be able to make do without Webpack for a slightly more
sophisticated example that uses Vue components.

### Single origin policy

To enhance security, ES6 modules are subject to
[same-origin policy](http://tinyurl.com/jwag3hy)
which means we have to run a local server in order to being able to run
JavaScript applications using this technology. Unfortunately, that means we
have to install a npm dependency `browsersync`. There's more
[info on stackoverflow](https://stackoverflow.com/a/46992592/2085356)
on this CORS (cross origin resource sharing) policy.

### Structure of the project

This is the folder and file structure of the project.

```text
+-- package.json
+-- src
    +-- TodoComponents.js
    +-- index.html
    +-- styles.css
```

And here's the `package.json` script that's needed to launch the local web
server that will serve up all the JS files from the same origin.

```json
{
  "scripts": {
    "start": "browser-sync start --server 'src' --files 'src' --single"
  }
}
```

### Run it

Type the following commands:

- `npm install`
- `npm start`

### Vue components

To recap, to add a Vue component, I've chosen not to dump everything in a single HTML
file, but not use Webpack either. Instead, I'm useing something called `browsersync`
to setup a simple web server that I can use to host and test my HTML, JS, and CSS
files.

#### Import the ES6 module

The index.html changes a little bit, since I need to import a `TodoComponents.js` file.

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Vue Test</title>

    <!-- This is a development version of Vue.js! -->
    <script src="https://cdn.jsdelivr.net/npm/vue/dist/vue.js"></script>
    
    <!-- import es6 module in main.js -->
    <script src="TodoComponents.js" type="module"></script>
    
    <!-- import stylesheet -->
    <link rel="stylesheet" href="styles.css">
    
    <!-- Google fonts -->
    <link href="https://fonts.googleapis.com/css?family=Open+Sans" rel="stylesheet">

</head>

<!-- Components -->
<div id="app_component" class="experiment-block">
    <todo_list v-bind:todo_list_prop="todoList"/>
</div>

</body>

</html>
``` 

#### Create the ES6 module

{% raw %}
```javascript
// List of to do items (accepts an array as props)
Vue.component(
    'todo_list',
    {
        props: ['todo_list_prop'],
        template:
            `<ol>
                 <todo_item v-for="item in todo_list_prop"
                            v-bind:todo_item_prop="item"
                            v-bind:key="item.id"/>
             </ol>`
    },
);

// Renderer for each to do item (accepts one item as props)
Vue.component(
    'todo_item',
    {
        props: ['todo_item_prop'],
        template:
            `<li v-bind:class="{ strike: todo_item_prop.done }">
              {{ todo_item_prop.text }}
            </li>`
    },
);

// Setup the data for the to do list (and and attach to index.html)
new Vue(
    {
        el: '#app_component',
        data: {
            todoList: [
                {id: 0, text: 'Brush teeth', done: true},
                {id: 1, text: 'Buy chocolate', done: false},
                {id: 2, text: 'Sell laptop', done: false},
            ],
        },
    });

```
{% endraw %}

#### Notes on the code
- There are 2 components that are created `todo_list` and `todo_item`. And these
can be used as tag names in the HTML.
- The `Vue` object that's created has a `data` property that contains an
array of to do items (each of which has an `id`, `text`, and `done` properties).
- The `todo_list` item is passed the `todoList` as a `prop`. It then
iterates thru each object and passes it to the `todo_item` as a `prop`.
- If you're familiar w/ Android, you can think of it this way
    - Adapter 👉 `Vue` object's `data`. 
    - List View 👉 `todo_list`. 
    - List Row Renderer 👉 `todo_item`.
- In the `todo_list` template, you will find this directive 
`v-bind:class="{ strike: todo_item_prop.done }"`. It means that if `done` is `true`
then to apply the `strike` CSS class (which simply strikes thru the item, marking
it done).

## Get the code

You can get the code used in this tutorial in the 
[vue_intro](https://github.com/nazmulidris/vue_intro) GiHub repo.
