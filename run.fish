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

# More info on prompting a user for confirmation using fish read function: https://stackoverflow.com/a/16673745/2085356
# More info about fish `read` function: https://fishshell.com/docs/current/cmds/read.html
function _promptUserForConfirmation -a message
    if not test -z "$message"
        echo (set_color brmagenta)"🤔 $message?"
    end

    while true
        # read -l -P '🔴 Do you want to continue? [y/N] ' confirm
        read -l -p "set_color brcyan; echo '🔴 Do you want to continue? [y/N] ' ; set_color normal; echo '> '" confirm
        switch $confirm
            case Y y
                return 0
            case '' N n
                return 1
        end
    end
end

function main
    if test -e Gemfile.lock
        rm Gemfile.lock
    end

    # On Linux.
    if test (uname) = Linux
        # More info to find if a package is installed: https://askubuntu.com/a/823630/872482
        if string match -q false (isPackageInstalled ruby-dev);
            or string match -q false (isPackageInstalled ruby-bundler)
            echo "Install ruby"
            echo "ruby-bundler or ruby-dev are not installed; installing now..."
            sudo apt install -y ruby-bundler ruby-dev
        end
    end

    # On macOS.
    if test (uname) = Darwin
        brew install ruby
        fish_add_path /opt/homebrew/opt/ruby/bin
        echo Ruby version: (ruby -v)
    end

    echo "Install Jekyll and dependencies."
    bundle install
    bundle update

    ./build-site.fish

    if _promptUserForConfirmation "Do you want to run the local dev server"
        npm list -g --depth=0 | rg -q 'serve@'
        # if $status is 0 then serve is installed, else install serve
        if test $status -ne 0
            echo (set_color green)"Installing serve..."(set_color normal)
            npm install -g serve
        else
            echo (set_color blue)"serve is already installed."(set_color normal)
        end
        killall -9 node # Kill all the node processes (serve runs on node)
        serve docs/ & # Run serve in the background, allows `./watch-build.fish` to run in a loop
    else
        echo "Ok, bye!"
        return
    end

    # Run the local dev server (this will hardcode all the links to be localhost:4000)
    # bundle exec jekyll serve

    # Old stuff.
    # Jekyll install instructions: http://tinyurl.com/y2vbgyqz
    # jekyll serve --config _config_dev.yml
    # More info: http://tinyurl.com/yytw8hus
    # gem install bundler
    # bundle update --bundler
end

# Actually call the main function.
main
