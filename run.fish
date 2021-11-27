#!/usr/bin/env fish

# Return "true" if $packageName is installed, and "false" otherwise. Use it in an if statement like this:
#
#   if string match -q "false" (isPackageInstalled my-package-name)
#     echo "my-package-name is not installed"
#   else
#     echo "my-package-name is installed"
#   end
#
function isPackageInstalled -a packageName
  set packageIsInstalled (dpkg -l "$packageName")
  if test -z "$packageIsInstalled"
    set packageIsInstalled false
  else
    set packageIsInstalled true
  end
  echo $packageIsInstalled
end

if test -e Gemfile.lock
  rm Gemfile.lock
end

# More info to find if a package is installed: https://askubuntu.com/a/823630/872482
if test (uname) = "Linux"

  if string match -q "false" (isPackageInstalled ruby-dev) ;
    or string match -q "false" (isPackageInstalled ruby-bundler)
    echo "Install ruby"
    echo "ruby-bundler or ruby-dev are not installed; installing now..."
    sudo apt install -y ruby-bundler ruby-dev
  end

  echo "Run the server"
  bundle install
  bundle update
  bundle exec jekyll serve --incremental

end

# Old stuff.
# Jekyll install instructions: http://tinyurl.com/y2vbgyqz
# jekyll serve --config _config_dev.yml
# More info: http://tinyurl.com/yytw8hus
# gem install bundler
# bundle update --bundler
