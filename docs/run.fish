#!/usr/bin/env fish

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
    # Ensure Ruby and Bundler are installed in a distro-agnostic way
    if not command -v ruby >/dev/null
        echo "Ruby is not installed. Please install Ruby to continue."
        exit 1
    end

    if not command -v bundle >/dev/null
        echo "Bundler is not installed. Installing it now..."
        gem install bundler
    end

    # On macOS, ensure homebrew ruby is in path just in case
    if test (uname) = Darwin
        if test -d /opt/homebrew/opt/ruby/bin
            fish_add_path /opt/homebrew/opt/ruby/bin
        end
    end

    echo "Ruby version: "(ruby -v)

    echo "Install Jekyll and dependencies."
    # We no longer delete Gemfile.lock or run bundle update blindly. 
    # This prevents reproducible build issues.
    bundle install

    ./build-site.fish
    if test $status -ne 0
        echo "Build failed! Aborting."
        exit 1
    end

    if _promptUserForConfirmation "Do you want to run the local dev server"
        npm list -g --depth=0 | rg -q 'serve@'
        # if $status is 0 then serve is installed, else install serve
        if test $status -ne 0
            echo (set_color green)"Installing serve..."(set_color normal)
            npm install -g serve
        else
            echo (set_color blue)"serve is already installed."(set_color normal)
        end
        killall -9 node 2>/dev/null # Kill all the node processes (serve runs on node)
        serve docs/ & # Run serve in the background, allows `./watch-build.fish` to run in a loop
    else
        echo "Ok, bye!"
        return
    end
end

# Actually call the main function.
main
