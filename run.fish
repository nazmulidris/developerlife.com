#!/usr/bin/env fish

if test (uname) = "Linux"
  # Install ruby
  sudo apt install -y ruby-bundler ruby-dev
end

bundle install
bundle update
bundle exec jekyll serve

# Old stuff.
# Jekyll install instructions: http://tinyurl.com/y2vbgyqz
# jekyll serve --config _config_dev.yml
# More info: http://tinyurl.com/yytw8hus
# gem install bundler
# bundle update --bundler
