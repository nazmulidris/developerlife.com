---
author: Nazmul Idris
date: 2019-07-06 17:59:00+00:00
excerpt: |
  This tutorial showcases a starter project for people who want to use TypeScript
  w/ a stater project already setup to deploy to browsers using Webpack 4, and 
  w/ testing infrastructure configured (via Jasmine and Karma)
layout: post
title: "TypeScript starter project w/ Webpack 4, Karma, Jasmine"
categories:
  - Web
  - TDD
---

<img class="post-hero-image" src="{{ 'assets/typescript-template-project-hero.svg' | relative_url }}"/>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [Architecture Diagram](#architecture-diagram)
- [The starter project repo](#the-starter-project-repo)
  - [Build, run, and test using npm scripts](#build-run-and-test-using-npm-scripts)
  - [Add source and test files, folder structure and configuration overview](#add-source-and-test-files-folder-structure-and-configuration-overview)
- [References](#references)
  - [TypeScript](#typescript)
  - [Webpack 4](#webpack-4)
  - [Karma, Jasmine](#karma-jasmine)
  - [All together](#all-together)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

If you are starting w/ TypeScript for your next project, and you want have a project that is already setup to deploy to
browsers using Webpack 4, and also has testing infrastructure hooked up to it (via Jasmine and Karma), here's a
[repo on GitHub](https://github.com/nazmulidris/ts-template) that you can clone/fork to get started.

This tutorial will walk you thru the gory details of what is going on in this repo (so that you don't have to go thru
the pain of setting and configuring all of this up yourself) 😁.

This repo is a great starting point for someone who wants to start a new TypeScript project w/ TDD / BDD, and also use
Webpack 4 to take care of packing the web app to browsers. And also take care of hosting the app during local
development using Webpack Dev Server.

## Architecture Diagram

The following diagram describes all the different pieces of the starter project that have already been configured for
you to use. And a depiction of what happens when various `npm` scripts are run.

<img src="{{'assets/ts-template-arch-diagram.svg' | relative_url}}"/>

## The starter project repo

### Build, run, and test using npm scripts

Here are some of the major npm scripts that you will need to run once you clone or fork the repo. Make sure to run
`npm install` after you've cloned or forked the repo to your computer.

1. `npm run build:dev` - This will use Webpack to build your project and will continue watching the `src` directory for
   changes in any '.ts' or `.js` files and will rebuild as they change. The Webpack configuration that this script loads
   is in the `webpack.dev.config.js` file.

1. `npm run start:dev` - This will build your project, and then use Webpack Dev Server to deploy the app to localhost.
   Any changes that you make in the `src` folder will be picked up and
   [hot-reloaded](https://webpack.js.org/configuration/dev-server/#devserverhot) into any open browsers running the app
   as well, which is awesome 🎉.

1. `npm run test` - This will start Karma, which will launch a Chrome browser that it will use to run your tests. Karma
   will keep watch on any changes that occur in your source code and it will re-run these tests when that happens.
   [`karma-spec-reporter`](https://stackoverflow.com/a/17327465/2085356) is used so that you get a nice console output
   of the results of the tests (replete w/ the `describe` and `it` strings from your tests).

### Add source and test files, folder structure and configuration overview

Your TS source code goes in the `src` folder, along w/ any JS files that you might have. Webpack 4 is configured to pick
these up and add them to the bundle that it generates. Don't worry, sourcemaps are generated as well, so that when you
debug the bundle, you will be able to browser and set breakpoints in your TS source code.

All your tests (that use Jasmine) go into the `test` folder. When you run Karma, it will continuously test your code
anytime `src` changes. It will also launch a Chrome browser to run these tests in.

In the root folder of the project there are some configuration files. Here's a list of what they are and what they do.

1. `package.json`

   - You can see all the `devDependencies` that are pulled into this project.

   - There aren't any `dependencies` in this project, but as you add them yourself, you can also use
     [bundlephobia](https://bundlephobia.com/) ([more info](https://www.youtube.com/watch?v=U_gANjtv28g)) to find out
     how much bloat each of these dependencies is adding to your final Webpack bundle.

1. `webpack.dev.config.js`

   - This is the Webpack 4 configuration file. It is used by both `.karma conf.js` to run the tests, and the `npm`
     scripts to build and run the project (using the Webpack Dev Server).

   - `entry` is configured to be `src/index` which can be a `index.js` or `index.ts` file (based on the `resolve`
     configuration). In our case, it is `index.ts`. It is critical to define an entry point for Webpack, so that it
     knows where to build its tree of source files that it will transpile, minify, tree-shake, and bundle.

   - `ts-loader` module is used to grab all the `.ts` files and transpile them to ES6 (this is configured in
     `tsconfig.json` which is used by `ts-loader`).

   - `devServer` is configured here to support hot-reloading.

   - `devtool` is configured to support `inline-source-map` so that you can see your TS code when you're debugging your
     test code or source code.

   - `watch` is enabled so that any changes will be detected during build and run (which are invoked using the `npm`
     scripts).

   - `output` is configured such that the bundle is called `bundle.js` and it is written to the `dist/` folder, which is
     the default for Webpack 4 (if you don't use any `webpack.config.js` file).

1. `.karma.conf.js`

   - This is the config file for Karma and it actually pulls in the `webpack.dev.config.js` file as well, so that your
     Webpack development configuration settings are also applied to the code served by Karma to the browsers that are
     running the tests.

   - A strange thing that happens in this file is how the entry for Webpack is set, so that Karma can run the tests.
     Normally, the Webpack entry is the main file in your application (`src/index.ts`), however, in this case, the main
     entry point are the test files. Karma has to leverage Webpack, in order to generate the bundle that it needs, so
     that it can run the tests. In order to make this work, I copy the `webpack.dev.config.js` object (into
     `webpackConfig` variable) and then only grab the following keys to give to the `webpack`: `webpackConfig.module`,
     `webpackConfig resolve`, and `webpackConfig.mode`. Karma injects the `entry` by itself. If you just pass the
     `webpackConfig` to the `webpack` key, then Karma will not start (and will error out).

1. `tsconfig.json`

   - This is the TypeScript compiler configuration file. It is used by the `ts-loader` (in Webpack) to transpile your TS
     files to JS on their way to the bundle.

   - `compilerOptions.target` is an important value to set (in this case `esnext`) as this tells the TS compiler what
     version of JS to transpile the code into. `sourceMap` is also set to `true` so that the transpiled code can be
     debugged in the browser (when served by the Webpack Dev Server) or the tests (when served by the Karma server).

## References

### TypeScript

TypeScript intro

- [Video: quick intro to TS](https://youtube.com/ahCwqrYpIuM)
- [Video: detailed intro to TS](https://www.youtube.com/watch?v=XShQO3BvOyM)

TypeScript and Webpack 4 intro

- [Video: TS w/ Webpack 4](https://www.youtube.com/watch?v=8TiZdePyduI)
- [ts-loader on github](https://github.com/TypeStrong/ts-loader)

### Webpack 4

Webpack 4 intro

- [Tutorial: what is webpack?](https://wanago.io/2018/07/16/webpack-4-course-part-one-entry-output-and-es6-modules/)

Webpack configuration

- [Docs: webpack `devtool`](https://webpack.js.org/configuration/devtool/)
- [Tutorial: webpack configuration](https://medium.com/@rajaraodv/webpack-the-confusing-parts-58712f8fcad9)

Webpack dev server configuration

- [Webpack configuration gotchas](https://github.com/webpack/webpack-dev-server/issues/720)
- [Docs: webpack `webpack-dev-server`](https://webpack.js.org/guides/development/#using-webpack-dev-server)

### Karma, Jasmine

Karma, Jasmine intro

- [Tutorial: Karma](http://www.bradoncode.com/blog/2015/02/27/karma-tutorial/)
- [Stackoverflow: `karma-spec-reporter`](https://stackoverflow.com/a/17327465/2085356)

### All together

Karma, Jasmine, and Webpack setup

- [Tutorial: Setting up Karma testing on Webpack](https://mike-ward.net/2015/09/07/tips-on-setting-up-karma-testing-with-webpack/)

TypeScript migrate from typings to npm @types

- [Tutorial: Migrate from typings to npm](http://codereform.com/blog/post/migrating-from-typings-to-npm-types/)

TypeScript, Webpack, Jasmine, and Karma

- [Tutorial: setup testing w/ TS, Karma, Webpack, etc](https://templecoding.com/blog/2016/02/02/how-to-setup-testing-using-typescript-mocha-chai-sinon-karma-and-webpack)
- [Repo: for the tutorial above](https://github.com/thitemple/TypescriptMochaWebpackDemo)
