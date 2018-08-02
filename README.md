## Running the site
After you clone the repo, go the `jekyll_test` folder, and
1. Run `bundler` → Takes the `Gemfile` imports and installs them
1. Run `jekyll serve` → Builds the static site and serves it on port 4000
1. Open `http://localhost:4000` in your browser

## Locating minima theme
- Run `open $(bundle show minima)` in Finder
    - Note that if you edit these minima files by accident (you will need sudo access to edit them),
      you can simply regenerate them by running `bundle install --force`.
- [Learn more about `minima` theme customization](https://github.com/jekyll/minima)

## Installing Ruby and running this project
To use Rails on macOS, you’ll need Ruby (an interpreter for the Ruby programming language) plus gems (software libraries) containing the Rails web application development framework. Run the following commands in your terminal app.
1. `xcode-select --install`
1. `brew install ruby`
1. Go to the folder in which you've cloned this repo
    1. run `bundle install`
    1. and run `jekyll serve`

### To create a new project using Jekyll
1. In order to create a new project using Jekyll
    1. Go to a folder that you want to create your new website under, eg `~/github/`
    1. Run `jekyll new jekyll_test`
        1. Your new site will be created in `~/github/jekyll_test` 
        1. Run `jekyll serve` to run it
    1. Point your web browser to `http://localhost:4000`