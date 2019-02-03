#!/bin/bash
#jekyll serve --config _config_dev.yml
bundle update --bundler
bundle install && bundle exec jekyll serve
