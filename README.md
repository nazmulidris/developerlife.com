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

To use Rails on macOS, you’ll need Ruby (an interpreter for the Ruby programming language) plus gems (software
libraries) containing the Rails web application development framework. Run the following commands in your terminal app.

1.  `xcode-select --install`
1.  `brew install ruby`
1.  Go to the folder in which you've cloned this repo
    1.  run `bundle install` ⇢ like `npm install`, and will download deps
    1.  and run `jekyll serve`⇢ like `npm run serve`, will launch server

## Creating a new project using Jekyll

1.  In order to create a new project using Jekyll
    1.  Go to a folder that you want to create your new website under, eg `~/github/`
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

## Running github pages locally

- [Setting GitHub Pages site locally with Jekyll](http://tinyurl.com/yytw8hus)

## More info on Jekyll and Liquid

- [Printing debug variables](http://tinyurl.com/y763y5lx)
- [True and false in](http://tinyurl.com/ya793347)
- [Control flow](http://tinyurl.com/yd9ls9ut)

## Locating minima theme

- Run `open $(bundle show minima)` in Finder
  - Note that if you edit these minima files by accident (you will need sudo access to edit them), you can simply
    regenerate them by running `bundle install --force`.
- Learn more about `minima` theme customization [here](https://github.com/jekyll/minima)

# Change master to main

The
[Internet Engineering Task Force (IETF) points out](https://tools.ietf.org/id/draft-knodel-terminology-00.html#rfc.section.1.1.1)
that "Master-slave is an oppressive metaphor that will and should never become fully detached from history" as well as
"In addition to being inappropriate and arcane, the
[master-slave metaphor](https://github.com/bitkeeper-scm/bitkeeper/blob/master/doc/HOWTO.ask?WT.mc_id=-blog-scottha#L231-L232)
is both technically and historically inaccurate." There's lots of more accurate options depending on context and it
costs me nothing to change my vocabulary, especially if it is one less little speed bump to getting a new person excited
about tech.

You might say, "I'm all for not using master in master-slave technical relationships, but this is clearly an instance of
master-copy, not master-slave"
[but that may not be the case](https://mail.gnome.org/archives/desktop-devel-list/2019-May/msg00066.html). Turns out the
original usage of master in Git very likely came from another version control system (BitKeeper) that explicitly had a
notion of slave branches.

- https://dev.to/lukeocodes/change-git-s-default-branch-from-master-19le
- https://www.hanselman.com/blog/EasilyRenameYourGitDefaultBranchFromMasterToMain.aspx

[#blacklivesmatter](https://blacklivesmatter.com/)
