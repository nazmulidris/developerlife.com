<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [I don't have Jekyll and Ruby installed](#i-dont-have-jekyll-and-ruby-installed)
  - [Installing Ruby, Jekyll, and running this project](#installing-ruby-jekyll-and-running-this-project)
  - [Creating a new project using Jekyll](#creating-a-new-project-using-jekyll)
- [I have Jekyll and Ruby installed, and want to run this project](#i-have-jekyll-and-ruby-installed-and-want-to-run-this-project)
  - [Running the site (if you already have ruby installed)](#running-the-site-if-you-already-have-ruby-installed)
- [References](#references)
  - [More info on Jekyll and Liquid](#more-info-on-jekyll-and-liquid)
  - [Locating minima theme](#locating-minima-theme)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# I don't have Jekyll and Ruby installed

## Installing Ruby, Jekyll, and running this project

To use Rails on macOS, you’ll need Ruby (an interpreter for the Ruby
programming language) plus gems (software libraries) containing the Rails
web application development framework. Run the following commands in your
terminal app.

1.  `xcode-select --install`
1.  `brew install ruby`
1.  Go to the folder in which you've cloned this repo
    1.  run `bundle install` ⇢ like `npm install`, and will download deps
    1.  and run `jekyll serve`⇢ like `npm run serve`, will launch server

## Creating a new project using Jekyll

1.  In order to create a new project using Jekyll
    1.  Go to a folder that you want to create your new website under,
        eg `~/github/`
    1.  Run `jekyll new jekyll_test`
        1.  Your new site will be created in `~/github/jekyll_test`
        1.  Run `jekyll serve` to run it
    1.  Point your web browser to `http://localhost:4000`

# I have Jekyll and Ruby installed, and want to run this project

## Running the site (if you already have ruby installed)

After you clone the repo, go the `jekyll_test` folder, and

1.  Run `bundler` → Takes the `Gemfile` imports and installs them
1.  Run `jekyll serve` → Builds the static site and serves it on port 4000
1.  Open `http://localhost:4000` in your browser

# References

## More info on Jekyll and Liquid

- [Printing debug variables](http://tinyurl.com/y763y5lx)
- [True and false in](http://tinyurl.com/ya793347)
- [Control flow](http://tinyurl.com/yd9ls9ut)

## Locating minima theme

- Run `open $(bundle show minima)` in Finder
  - Note that if you edit these minima files by accident (you will need
    sudo access to edit them), you can simply regenerate them by
    running `bundle install --force`.
- Learn more about `minima` theme customization
  [here](https://github.com/jekyll/minima)
