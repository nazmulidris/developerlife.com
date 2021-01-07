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

# More info to find if a package is installed: https://askubuntu.com/a/823630/872482
if test (uname) = "Linux"

  echo "🐒isPackageInstalled does-not-exist:" (isPackageInstalled does-not-exist)

  if string match -q "false" (isPackageInstalled ruby-dev) ;
    or string match -q "false" (isPackageInstalled ruby-bundler)
    # Install ruby
    echo "ruby-bundler or ruby-dev are not installed; installing now..."
    echo sudo apt install -y ruby-bundler ruby-dev
  end

  bundle install
  bundle update
  bundle exec jekyll serve

end

# Old stuff.
# Jekyll install instructions: http://tinyurl.com/y2vbgyqz
# jekyll serve --config _config_dev.yml
# More info: http://tinyurl.com/yytw8hus
# gem install bundler
# bundle update --bundler
