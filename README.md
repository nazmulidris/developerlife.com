<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [I don't have Jekyll and Ruby installed](#i-dont-have-jekyll-and-ruby-installed)
  - [Installing Ruby, Jekyll, and running this project](#installing-ruby-jekyll-and-running-this-project)
  - [Creating a new project using Jekyll](#creating-a-new-project-using-jekyll)
- [I have Jekyll and Ruby installed, and want to run this project](#i-have-jekyll-and-ruby-installed-and-want-to-run-this-project)
  - [Running the site (if you already have ruby installed)](#running-the-site-if-you-already-have-ruby-installed)
- [RSS Readers and hero-image handling](#rss-readers-and-hero-image-handling)
- [Customize minima theme](#customize-minima-theme)
  - [Overriding files in the base theme](#overriding-files-in-the-base-theme)
  - [How to customize syntax highlighting](#how-to-customize-syntax-highlighting)
  - [Documentation and references on Jekyll styling, minima customization, and SASS](#documentation-and-references-on-jekyll-styling-minima-customization-and-sass)
- [References](#references)
  - [Running github pages locally](#running-github-pages-locally)
  - [More info on Jekyll and Liquid](#more-info-on-jekyll-and-liquid)
- [Change master to main](#change-master-to-main)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# I don't have Jekyll and Ruby installed

## Installing Ruby, Jekyll, and running this project

To use Rails on macOS, you’ll need Ruby (an interpreter for the Ruby programming language) plus gems
(software libraries) containing the Rails web application development framework. Run the following
commands in your terminal app.

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

# RSS Readers and hero-image handling

Using the `hero-image` property in the YAML header of each MD file in `_posts` folder doesn't work
with RSS readers (feedly and Fluent RSS reader). Here is the new (preferred) way of adding hero
images so they work w/ RSS readers.

Instead of using this YAML "hero-image" property (key) it is better to remove it and just add the
image directly using an img tag like so:

```
``<img class="post-hero-image" src="{{ 'assets/<HERO_IMAGE_HERE>' | relative_url }}"/>
```

I successfully tested this using Fluent RSS reader on `http://127.0.0.1:4000/feed.xml`.

# Customize minima theme

Jekyll is configured to use minima theme. This means that there are some files that are pulled from
this dependency by Jekyll when it builds the static site. This dependency is located on your
computer in `echo (bundle info --path minima)`. Save the path to an environment variable called
`$MINIMA_HOME` using `set MINIMA_HOME (bundle info --path minima)`.

Here is an example of the files in the `$MINIMA_HOME` folder.

```text
/home/nazmul/.ruby/gems/minima-2.5.1
├── assets
│   ├── main.scss
│   └── minima-social-icons.svg
├── _includes
│   ├── disqus_comments.html
│   └── ...
├── _layouts
│   ├── default.html
│   └── ...
└── _sass
    ├── minima
    │   ├── _base.scss
    │   ├── _layout.scss
    │   └── _syntax-highlighting.scss
    └── minima.scss
```

As you can imagine, in order to customize this theme you can simply provide a file that is your repo
that is located on a similar path to the path that is in `$MINIMIA_HOME`,
[more info here](https://ouyi.github.io/post/2017/12/23/jekyll-customization.html)

> If you edit these minima files by accident (you will need `sudo` access to edit them), you can
> simply regenerate them by running `bundle install --force`.

## Overriding files in the base theme

The interesting files are `./_sass/minima.scss` and `./_sass/styles.scss` (which is imported by the
former).

- If we provide our own copy of these files in a similar path in this repo, then they will simply be
  considered overrides by Jekyll when it builds the static site.
- Think of this as operator overloading but for files. So if this file `./_sass/minima.scss` is
  found in this repo, then it overrides the equivalent one in the "base" theme located in
  `$MINIMA_HOME`.
- Look at the bottom of the `./_sass/minima.scss` file and you will see imports that pull in
  `styles.scss` and `syntax.scss`. The latter is used for syntax highlighting.

I've created a file `./_sass/minima.scss` which overrides the corresponding file in the base theme.
This is where I do a lot of big customizations, like creating variables, and using `@import` to
bring in other `.scss` files. Here are some examples of this.

```scss
@font-face {
  font-family: "JetBrains Mono";
  src: url("/assets/jetbrainsmono/JetBrainsMono-Regular.woff2") format("woff2");
}

...

$brand-color: #2f9ece !default;
$text-color: #e6e6e6 !default;

...

// Import other SCSS files.
// "minima/base" - override the minima theme files.
// "minima/layout" - override the minima theme files.
// "syntax" - Custom syntax highlighting (not using minima defaults).
// "styles" - Custom styles (not using minima defaults).
@import "minima/base", "minima/layout", "syntax", "styles";
```

These `@import` statements bring in lots of other `scss` files. One of them handles syntax
highlighting, [more on this below](#how-to-customize-syntax-highlighting).

Here's a `./_site/assets/main.css.map` file that is generated as part of the build process (which
are driven by some key-value pairs in the `_config.yml` file) which has a list of all the `scss`
files that are actually imported to give a clear picture of what files are actually used to generate
the single `./_site/assets/main.css` file everytime Jekyll generates the static site.

```css
{
    "version": 3,
    "file": "main.css",
    "sources": [
        "main.scss",
        "_sass/minima.scss",
        "_sass/minima/_base.scss",
        "_sass/minima/_layout.scss",
        "_sass/syntax.scss",
        "_sass/styles.scss"
    ],
    "sourcesContent": [
        "@import \"minima\";\n",
        "@charset \"utf-8\";\n\n@font-face {\n  font-family: \"JetBrains Mono\";\n ..."
    ],
    "names": [],
    "mappings": "ACEA,UAAU,..."
}
```

## How to customize syntax highlighting

The file `./_sass/syntax.scss` actually contains all the syntax highlighting SCSS. This overrides
whatever comes w/ minima (it does come w/ some defaults in
`$MINIMA_HOME/_sass/minima/_syntax-hihglihting.scss`). There's a repo called
[`pygments-css`](https://github.com/richleland/pygments-css) which I simply copy from. In this repo,
find the styling that you like, and just copy/paste the contents of that file into the `syntax.scss`
file as described in the comments in this file, and it will be applied when Jekyll builds the static
site.

## Documentation and references on Jekyll styling, minima customization, and SASS

- [Jekyll docs on styling](https://jekyllrb.com/docs/step-by-step/07-assets/)
- [Minima docs](https://github.com/jekyll/minima)
- [Tutorial on customization](https://ouyi.github.io/post/2017/12/23/jekyll-customization.html)
- [SASS basics](https://sass-lang.com/guide)

# References

## Running github pages locally

- [Setting GitHub Pages site locally with Jekyll](http://tinyurl.com/yytw8hus)

## More info on Jekyll and Liquid

- [Printing debug variables](http://tinyurl.com/y763y5lx)
- [True and false in](http://tinyurl.com/ya793347)
- [Control flow](http://tinyurl.com/yd9ls9ut)

# Change master to main

The
[Internet Engineering Task Force (IETF) points out](https://tools.ietf.org/id/draft-knodel-terminology-00.html#rfc.section.1.1.1)
that "Master-slave is an oppressive metaphor that will and should never become fully detached from
history" as well as "In addition to being inappropriate and arcane, the
[master-slave metaphor](https://github.com/bitkeeper-scm/bitkeeper/blob/master/doc/HOWTO.ask?WT.mc_id=-blog-scottha#L231-L232)
is both technically and historically inaccurate." There's lots of more accurate options depending on
context and it costs me nothing to change my vocabulary, especially if it is one less little speed
bump to getting a new person excited about tech.

You might say, "I'm all for not using master in master-slave technical relationships, but this is
clearly an instance of master-copy, not master-slave"
[but that may not be the case](https://mail.gnome.org/archives/desktop-devel-list/2019-May/msg00066.html).
Turns out the original usage of master in Git very likely came from another version control system
(BitKeeper) that explicitly had a notion of slave branches.

- https://dev.to/lukeocodes/change-git-s-default-branch-from-master-19le
- https://www.hanselman.com/blog/EasilyRenameYourGitDefaultBranchFromMasterToMain.aspx

[#blacklivesmatter](https://blacklivesmatter.com/)
