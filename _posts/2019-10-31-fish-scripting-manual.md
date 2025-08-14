---
author: Nazmul Idris
date: 2021-01-19 17:43:35+00:00
excerpt: |
  Short manual on how to program using fish shell's scripting language using lots of useful examples ranging from simple
  to complex
layout: post
title: "fish shell scripting manual"
categories:
  - Linux
  - Misc
---

<img class="post-hero-image" src="{{ 'assets/fish-shell.svg' | relative_url }}"/>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Shebang line at the top of your scripts](#shebang-line-at-the-top-of-your-scripts)
- [How to set variables](#how-to-set-variables)
  - [Variable scopes: local, global, global-export](#variable-scopes-local-global-global-export)
  - [Lists](#lists)
  - [Storing return values from running a command](#storing-return-values-from-running-a-command)
  - [Ranges](#ranges)
- [How to write for loops](#how-to-write-for-loops)
- [How to write if statements](#how-to-write-if-statements)
  - [Commonly used conditions](#commonly-used-conditions)
  - [Program, script, or function exit code](#program-script-or-function-exit-code)
  - [Difference between set -q and test -z](#difference-between-set--q-and-test--z)
  - [Multiple conditions with operators: and, or](#multiple-conditions-with-operators-and-or)
  - [Another common operator: not](#another-common-operator-not)
  - [References](#references)
- [How to split strings by a delimiter](#how-to-split-strings-by-a-delimiter)
- [How to perform string comparisons](#how-to-perform-string-comparisons)
- [How to write switch statements for strings](#how-to-write-switch-statements-for-strings)
- [How to execute strings](#how-to-execute-strings)
- [How to write functions](#how-to-write-functions)
  - [Pass arguments to a function](#pass-arguments-to-a-function)
  - [Return values from a function](#return-values-from-a-function)
  - [Advanced function features](#advanced-function-features)
    - [Functions with default values](#functions-with-default-values)
    - [Functions with variable arguments (variadic)](#functions-with-variable-arguments-variadic)
    - [Functions with options/flags](#functions-with-optionsflags)
    - [Functions that modify global state](#functions-that-modify-global-state)
    - [Functions with comprehensive error handling](#functions-with-comprehensive-error-handling)
- [How to handle file and folder paths for dependencies](#how-to-handle-file-and-folder-paths-for-dependencies)
- [How to write multi line strings to files](#how-to-write-multi-line-strings-to-files)
- [How to create colorized echo output](#how-to-create-colorized-echo-output)
- [How to get user input](#how-to-get-user-input)
- [How to use fzf for interactive selection](#how-to-use-fzf-for-interactive-selection)
  - [Basic selection example](#basic-selection-example)
  - [Interactive file menu example](#interactive-file-menu-example)
  - [Multiple selection example](#multiple-selection-example)
  - [Common fzf options](#common-fzf-options)
  - [Installation and usage notes](#installation-and-usage-notes)
- [How to use sed](#how-to-use-sed)
- [How to use xargs](#how-to-use-xargs)
- [How to use cut to split strings](#how-to-use-cut-to-split-strings)
- [How to calculate how long the script took to run](#how-to-calculate-how-long-the-script-took-to-run)
- [How to debug fish scripts](#how-to-debug-fish-scripts)
  - [Enable command tracing](#enable-command-tracing)
  - [Conditional debug output](#conditional-debug-output)
  - [Check command success and status codes](#check-command-success-and-status-codes)
  - [Validate function arguments](#validate-function-arguments)
  - [Use verbose output for complex operations](#use-verbose-output-for-complex-operations)
  - [Debug script timing and performance](#debug-script-timing-and-performance)
  - [Environment variable debugging](#environment-variable-debugging)
- [Fish scripting best practices](#fish-scripting-best-practices)
  - [Always quote variables](#always-quote-variables)
  - [Use meaningful variable names](#use-meaningful-variable-names)
  - [Validate inputs and handle errors](#validate-inputs-and-handle-errors)
  - [Use local variables in functions](#use-local-variables-in-functions)
  - [Prefer fish builtins over external commands](#prefer-fish-builtins-over-external-commands)
  - [Use command substitution appropriately](#use-command-substitution-appropriately)
  - [Use functions for reusable code](#use-functions-for-reusable-code)
  - [Handle signals gracefully](#handle-signals-gracefully)
  - [Use consistent exit codes](#use-consistent-exit-codes)
  - [Document your functions](#document-your-functions)
- [Common fish scripting pitfalls](#common-fish-scripting-pitfalls)
  - [Forgetting that all variables are lists](#forgetting-that-all-variables-are-lists)
  - [Using bash syntax in fish](#using-bash-syntax-in-fish)
  - [Mixing up `set -q` (exists) vs `test -z` (empty)](#mixing-up-set--q-exists-vs-test--z-empty)
  - [Not quoting variables with spaces](#not-quoting-variables-with-spaces)
  - [Incorrect variable expansion in loops](#incorrect-variable-expansion-in-loops)
  - [Forgetting command substitution captures stdout only](#forgetting-command-substitution-captures-stdout-only)
  - [Using `!` for negation instead of `not`](#using--for-negation-instead-of-not)
  - [Assuming `$0` contains the script name](#assuming-0-contains-the-script-name)
  - [Not checking command exit status](#not-checking-command-exit-status)
  - [Global variable pollution](#global-variable-pollution)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Shebang line at the top of your scripts

To be able to run fish scripts from your terminal, you have to do two things.

1. Add the following shebang line to the top of your script file: `#!/usr/bin/env fish`.
2. Mark the file as executable using the following command: `chmod +x <YOUR_FISH_SCRIPT_FILENAME>`.

## How to set variables

Keep in mind that all types of values that can be assigned to variables in fish are strings. There
is no such thing as boolean or integer or float, etc. Here's a simple example of assigning a value
to a variable. Here is
[more information on stackoverflow](https://stackoverflow.com/a/47762934/2085356) on this.

```bash
set MY_VAR "some value"
```

One of the most useful things that you can do is save the output of a command that you run in the
shell in a variable. This is useful when you are testing to see if some program or command returned
some values that mean that you should perform some other command (using string comparisons, if
statements, and switch statements). Here's are examples of doing this.

```bash
set CONFIG_FILE_DIFF_OUTPUT (diff ~/Downloads/config.fish ~/.config/fish/config.fish)
set GIT_STATUS_OUTPUT (git status --porcelain)
```

### Variable scopes: local, global, global-export

There are times when you have to export variables to child processes and also times when you have to
export variables to global scope. There are also times when you want this variable to be limited to
local scope of the function you are writing. The fish documentation on the
[`set`](https://fishshell.com/docs/current/cmds/set.html) function has more information on this.

- To limit variables to local scope of the function (even if there is a global variable of the same
  name) use `set -l`. This type of variable is not available to the entire fish shell. An example of
  this is a local variable that is used to hold some value just for the scope of a function, such as
  `set -l fname (realpath .)`
- Export variable using `set -x` (this is only available inside the current fish shell). An example
  of this is setting the `DISPLAY` environment variable for X11 session in a fish function that is
  running in a `crontab` headless environment.
- Export variable globally using `set -gx` (this is available to any programs in your OS, not just
  the currently running fish shell process). An example of this is setting the `JAVA_HOME`
  environment variable for all programs running on the machine.

### Lists

Here's an example of appending values to a variable. By default fish variables are lists.

```bash
set MY_VAR $MY_VAR "another value"
```

This is how you can create lists.

```bash
set MY_LIST "value1" "value2" "value3"
```

### Storing return values from running a command

Here's an example of storing value returned from the execution of a command to a variable.

```bash
set OUR_VAR (math 1+2)
set OUR_VAR (date +%s)
set OUR_VAR (math $OUR_VAR / 60)
```

Since all fish variables are lists, you can access individual elements using `[n]` operator, where
`n=1` for the first element (not 0 index). Here's an example. And negative numbers access elements
from the end.

```bash
set LIST one two three
echo $LIST[1]  # one
echo $LIST[2]  # two
echo $LIST[3]  # three
echo $LIST[-1] # This is the same element as above
```

### Ranges

You can also use ranges from the variable / list, continuing the example above.

```bash
set LIST one two three
echo $LIST[1..2]  # one two
echo $LIST[2..3]  # two three
echo $LIST[-1..2] # three two
```

- [Here's the doc for lists](https://fishshell.com/docs/current/tutorial.html#tut_lists)

## How to write for loops

Since variables contain lists by default, it is very easy to iterate thru them. Here's an example.

```bash
set FOLDERS bin
set FOLDERS $FOLDERS .atom
set FOLDERS $FOLDERS "my foldername"
for FOLDER in $FOLDERS
  echo "item: $FOLDER"
end
```

You can also simplify the code above by putting all the `set` commands in a single line like this.

```bash
set FOLDERS bin .atom "my foldername"
for FOLDER in $FOLDERS
  echo "item: $FOLDER"
end
```

You can also put the entire for statement in a single line like this.

```bash
set FOLDERS bin .atom "my foldername"
for FOLDER in $FOLDERS ; echo "item: $FOLDER" ; end
```

## How to write if statements

The key to writing if statements is using the `test` command to evaluate some expression to a
boolean. This can be string comparisons or even testing the existence of files and folders. Here are
some examples. You can also use the `not` operator to prefix the test to check for the inverse
condition.

### Commonly used conditions

Checking the size of an array. `$argv` contains the list of arguments passed to a script from the
command line.

```bash
if test (count $argv) -lt 2
  echo "Usage: my-script <arg1> <arg2>"
  echo "Eg: <arg1> can be 'foo', <arg2> can be 'bar'"
else
  echo "👋 Do something with $arg1 $arg2"
end
```

String comparison in variable.

```bash
if test $hostname = "mymachine"
  echo "hostname is mymachine"
end
```

Checking for file existence.

```bash
if test -e "somefile"
  echo "somefile exists"
end
```

Checking for folder existence.

```bash
if test -d "somefolder"
  echo "somefolder exists"
end
```

Checking for file wildcard existence is a little different than both file and folder checks. The
reason for this is how fish handles wildcards - they are expanded by fish before it performs
whatever command on them.

```bash
set -l files ~/Downloads/*.mp4 # This wildcard expression is expanded to include the actual files
if test (count $files) -gt 0
  mv ~/Downloads/*.mp4 ~/Videos/
  echo "📹 Moved '$files' to ~/Videos/"
else
  echo "⛔ No mp4 files found in Downloads"
end
```

Here's an example of how to use the `not` operator in the previous example.

```bash
if not test -d "somefolder"
  echo "somefolder does not exist"
end
```

### Program, script, or function exit code

The idea with exit codes is that your function or entire fish script could be used by some other
program that understands exit codes. In other words there could be an if statement that is going to
use the exit code to determine some condition. This is a very common pattern that is used with other
command line programs. Exit codes are different than [return values](#return-values-from-a-function)
from a function.

Here's an example of using the exit code of some `git` command:

```bash
if (git pull -f --rebase)
  echo "git pull with rebase worked without any issues"
else
  echo "Something went wrong that requires manual intervention, like a merge conflict"
end
```

Here's an example of how to test whether a command executed without errors.

```bash
if sudo umount /media/user/mountpoint
  echo "Successfully unmounted /media/user/mountpoint"
end
```

You can also check the value of the `$status` variable. Fish stores the return value in this
variable, just after a command is executed. Here's
[more info](https://fishshell.com/docs/2.3/faq.html) on this.

When you are writing functions you can use the following keyword to exit functions or loops:
`return`. This may be followed by a number. So here's what it means.

1. `return` or `return 0` - This means that the function exited normally.
2. `return 1` or some other number > 0 - This means that the function had some problem.

You can exit the fish shell itself using `exit`. And the integer exit codes have the same meaning as
above.

### Difference between set -q and test -z

There is a subtle difference between using `set -q` and `test -z` in if statements when checking to
see if a variable is empty.

1. In the case of `test -z` make sure to wrap the variable in quotes, since it might just break in
   some edge cases if it isn't wrapped in quotes.
2. However, you can use `set -q` to test if a variable has been set without wrapping it in quotes.

Here's an example.

```bash
set GIT_STATUS (git status --porcelain)
if set -q GIT_STATUS ; echo "No changes in repo" ; end
if test -z "$GIT_STATUS" ; echo "No changes in repo" ; end
```

### Multiple conditions with operators: and, or

If you want to combine multiple conditions into a single statement, then you can use `or` and `and`
operators. Also if you want to check the inverse of a condition, you can use `!`. Here's an example
of a function that checks for 2 arguments to be passed via the command line. Here's the logic we
will describe.

1. If both the arguments are missing, then usage information should be displayed to the CLI, and
   perform an early return.
2. If either one of the arguments is missing, then display a prompt stating that one of the
   arguments is missing, and perform an early return.

```bash
function requires-two-arguments
  # No arguments are passed.
  if set -q "$argv"
    echo "Usage: requires-two-arguments arg1 arg2"
    return 1
  end
  # Only 1 argument is passed.
  if test -z "$argv[1]"; or test -z "$argv[2]"
    echo "arg1 or arg2 can not be empty"
    return 1
  end
  echo "Thank you, got 1) $argv[1] and 2) $argv[2]"
end
```

Here are some notes on the code.

1. What does the [`set -q variable`](https://fishshell.com/docs/current/cmds/set.html) function do?
   It returns true if `variable` exists (is defined), regardless of whether it contains a value.
2. Instead of `set -q`, if you wanted to use
   [`test`](https://fishshell.com/docs/current/cmds/test.html) function in order to determine if a
   variable is empty, you can use:
   - `if test -z "$variable"`.
   - `if test ! -n "$variable"` or `if not test -n "$variable"`.
3. If you wanted to replace the `or` check above w/ `test`, this is what it would look like
   `if test -z "$argv[1]"; or test -z "$argv[2]"`.
4. When you use `or`, `and` operators that you have to terminate the condition expression w/ a `;`.
5. Make sure to wrap the variable in empty quotes. If an empty string is contained inside the
   variable, then without these quotes, the statements will cause errors.

Here's another example of this to test if `$variable` is empty or not.

```bash
if test -z "$variable" ; echo "empty" ; else ; echo "non-empty" ; end
```

Here's another example of this to test if `$variable` contains a string or not.

```bash
if test -n "$variable" ; echo "non-empty" ; else ; echo "empty" ; end
```

### Another common operator: not

Here's an example of using the `not` operator to test whether a string contains a string fragment or
not.

```bash
if not string match -q "*md" $argv[1]
  echo "The argument passed does not end in md"
else
  echo "The argument passed ends in md"
end
```

### References

1. [test command](https://fishshell.com/docs/current/cmds/test.html)
2. [set command](https://fishshell.com/docs/current/cmds/set.html)
3. [if command](https://fishshell.com/docs/current/cmds/if.html)
4. [stackoverflow answer: how to check if fish variable is empty](https://stackoverflow.com/questions/47743015/fish-shell-how-to-check-if-a-variable-is-set-empty)
5. [stackoverflow answer: how to put multiple conditions in fish if statement](https://stackoverflow.com/questions/17900078/in-fish-shell-how-can-i-put-two-conditions-in-an-if-statement)

## How to split strings by a delimiter

There are situations when you want to take the output of a command, which is a string, and then
split it by some delimiter, to use just a portion of the output string. An example of getting the
SHA checksum of a given file. The command `shasum <filename>` produces something like
`df..d8 <filename>`. Let's say that we just wanted the first portion of this string (the SHA),
knowing that the delimiter is two space characters, we can do the following to get just the checksum
portion and store it in `$CHECKSUM`. Here's more info on the
[`string split` command](https://fishshell.com/docs/current/cmds/string-split.html).

```bash
set CHECKSUM_ARRAY_STRING (shasum $FILENAME)
set CHECKSUM_ARRAY (string split "  " $CHECKSUM_ARRAY_STRING)
set CHECKSUM $CHECKSUM_ARRAY[1]
```

## How to perform string comparisons

In order to test substring matches in strings you can use the `string match` command. Here is more
information on the command:

1. [Official docs on string match](https://fishshell.com/docs/current/cmds/string-match.html).
2. [Stackoverflow answer on how to use it](https://unix.stackexchange.com/a/504931/302646).

Here's an example of this in action. Note the use of `-q` or `--quiet` which does not echo the
output of the string if the match condition was met (succeeded).

```bash
if string match -q "*myname*" $hostname
  echo "$hostname contains myname"
else
  echo "$hostname does not contain myname"
end
```

Here's an example of checking for an exact string match.

```bash
if test $hostname = "machine-name"
  echo "Exact match"
else
  echo "Not exact match"
end
```

Here's an example of testing whether a string is empty or not.

```bash
if set -q my_variable
  echo "my_variable is empty"
end
```

Here's a sophisticated example that tests to see if the packages `ruby-dev` and `ruby-bundler` are
installed. If they are then `jekyll` gets run, and if not, then these packages are installed.

```bash
# Return "true" if $packageName is installed, and "false" otherwise.
# Use it in an if statement like this:
#
# if string match -q "false" (isPackageInstalled my-package-name)
#   echo "my-package-name is not installed"
# else
#   echo "my-package-name is installed"
# end
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
  else
    bundle install
    bundle update
    bundle exec jekyll serve
  end

end
```

## How to write switch statements for strings

In order to create switch statements for strings, the `test` command is used here as well (just like
it was for [if statements](#how-to-write-if-statements)). The `case` statements need to match
substrings, which can be expressed using a combination of wildcard chars and the substring you want
to match. Here's an example.

```bash
switch $hostname
case "*substring1*"
  echo "Matches $hostname containing substring1"
case "*substring2*"
  echo "Matches $hostname containing substring2"
end
```

You can combine this w/ if statements as well, and end up w/ something like this.

```bash
if test (uname) = "Darwin"
  echo "Machine is running macOS"
  switch $hostname
  case "*MacBook-Pro*"
    echo "hostname has MacBook-Pro in it"
  case "*MacBook-Air*"
    echo "hostname has MacBook-Air in it"
  end
else
  echo "Machine is not running macOS"
end
```

## How to execute strings

The safest way to execute strings that are generated in the script is to use the following pattern.

```bash
echo "ls \
  -la" | sh
```

This not only makes it easier to debug, but also avoids strange errors when doing multi-line breaks
using `\`.

## How to write functions

A fish function is just a list of commands that may optionally take arguments. These arguments are
just passed in as a list (since all variables in fish are lists).

Here's an example.

```bash
function say_hi
  echo "Hi $argv"
end
say_hi
say_hi everbody!
say_hi you and you and you
```

Once you have written a function you can see what it is by using `type`, eg: `type say_hi` will show
you the function that you just created above.

- [Here's the doc for functions](https://fishshell.com/docs/current/tutorial.html#tut_functions)

### Pass arguments to a function

In addition to using `$argv` to figure out what parameters were passed to a function, you can
provide a list of named parameters that a function expects. Here is more information on this
[from the official docs](https://fishshell.com/docs/current/cmds/function.html).

Some key things to keep in mind:

1. Parameter names can not have `-` characters in them, so use `_` instead.
2. Do not use the `(` and `)` to pass arguments to a function, simply pass the arguments in a single
   line w/ spaces.

Here's an example.

```bash
function testFunction -a param1 param2
  echo "arg1 = $param1"
  echo "arg2 = $param2"
end
testFunction A B
```

Here's another example that tests for the existence of a certain number of arguments that are passed
to a function.

```bash
# Note parameter names can't have dashes in them, only underscores.
function my-function -a extension search_term
  if test (count $argv) -lt 2
    echo "Usage: my-function <extension> <search_term>"
    echo "Eg: <extension> can be 'fish', <search_term> can be 'test'"
  else
    echo "✋ Do something with $extension $search_term"
  end
end
```

### Return values from a function

You might want to return a value from a function (typically just a string). You can also return many
strings delimited by new lines. Regardless, the mechanism for doing this is the same. You simply
have to use `echo` to dump the return value(s) to stdout.

Here's an example.

```bash
function getSHAForFilePath -a filepath
  set NULL_VALUE ""
  # No $filepath provided, or $filepath does not exist -> early return w/ $NULL_VALUE.
  if set -q $filepath; or not test -e $filepath
    echo $NULL_VALUE
    return 0
  else
    set SHASUM_ARRAY_STRING (shasum $filepath)
    set SHASUM_ARRAY (string split "  " $SHASUM_ARRAY_STRING)
    echo $SHASUM_ARRAY[1]
  end
end

function testTheFunction
  echo (getSHAForFilePath ~/local-backup-restore/does-not-exist.fish)
  echo (getSHAForFilePath)
  set mySha (getSHAForFilePath ~/local-backup-restore/test.fish)
  echo $mySha
end

testTheFunction
```

### Advanced function features

#### Functions with default values

You can provide default behavior when arguments are missing:

```bash
#!/usr/bin/env fish

function greet -a name greeting
    # Provide default values
    if test -z "$name"
        set name "World"
    end
    if test -z "$greeting"
        set greeting "Hello"
    end
    
    echo "$greeting, $name!"
end

greet                    # "Hello, World!"
greet Alice              # "Hello, Alice!"
greet Bob "Good morning" # "Good morning, Bob!"
```

#### Functions with variable arguments (variadic)

Handle functions that accept any number of arguments:

```bash
#!/usr/bin/env fish

function sum_numbers
    set -l total 0
    
    if test (count $argv) -eq 0
        echo "Usage: sum_numbers <number1> [number2] [number3] ..." >&2
        return 1
    end
    
    for num in $argv
        if not string match -q -r '^\d+$' "$num"
            echo "Error: '$num' is not a valid number" >&2
            return 1
        end
        set total (math $total + $num)
    end
    
    echo $total
end

sum_numbers 1 2 3 4 5    # Output: 15
sum_numbers 10 20        # Output: 30
```

#### Functions with options/flags

Parse command-line style options in functions:

```bash
#!/usr/bin/env fish

function my_copy
    set -l verbose false
    set -l force false
    set -l source ""
    set -l dest ""
    
    # Parse options
    while test (count $argv) -gt 0
        switch $argv[1]
            case -v --verbose
                set verbose true
                set argv $argv[2..-1]
            case -f --force
                set force true
                set argv $argv[2..-1]
            case -*
                echo "Unknown option: $argv[1]" >&2
                return 1
            case '*'
                if test -z "$source"
                    set source $argv[1]
                else if test -z "$dest"
                    set dest $argv[1]
                else
                    echo "Too many arguments" >&2
                    return 1
                end
                set argv $argv[2..-1]
        end
    end
    
    # Validate required arguments
    if test -z "$source"; or test -z "$dest"
        echo "Usage: my_copy [-v|--verbose] [-f|--force] <source> <dest>" >&2
        return 1
    end
    
    # Build command
    set -l cp_args
    if test "$force" = "true"
        set cp_args $cp_args -f
    end
    if test "$verbose" = "true"
        set cp_args $cp_args -v
        echo "Copying '$source' to '$dest'..."
    end
    
    cp $cp_args "$source" "$dest"
end

# Usage examples:
# my_copy file.txt backup/
# my_copy -v -f important.doc /backup/
```

#### Functions that modify global state

Sometimes you need functions that modify variables in the calling scope:

```bash
#!/usr/bin/env fish

function append_to_path -a new_path
    if not contains "$new_path" $PATH
        set -gx PATH $PATH "$new_path"
        echo "Added '$new_path' to PATH"
    else
        echo "'$new_path' already in PATH"
    end
end

function remove_from_path -a path_to_remove
    if contains "$path_to_remove" $PATH
        set -l new_path
        for path_entry in $PATH
            if test "$path_entry" != "$path_to_remove"
                set new_path $new_path "$path_entry"
            end
        end
        set -gx PATH $new_path
        echo "Removed '$path_to_remove' from PATH"
    else
        echo "'$path_to_remove' not found in PATH"
    end
end
```

#### Functions with comprehensive error handling

Build robust functions with proper error checking:

```bash
#!/usr/bin/env fish

function safe_file_operation -a operation source dest
    # Validate operation type
    if not contains "$operation" copy move
        echo "Error: operation must be 'copy' or 'move'" >&2
        return 1
    end
    
    # Validate source file
    if test -z "$source"
        echo "Error: source file not specified" >&2
        return 1
    end
    
    if not test -e "$source"
        echo "Error: source file '$source' does not exist" >&2
        return 1
    end
    
    if not test -r "$source"
        echo "Error: cannot read source file '$source'" >&2
        return 1
    end
    
    # Validate destination
    if test -z "$dest"
        echo "Error: destination not specified" >&2
        return 1
    end
    
    set -l dest_dir (dirname "$dest")
    if not test -d "$dest_dir"
        echo "Creating destination directory: $dest_dir"
        if not mkdir -p "$dest_dir"
            echo "Error: failed to create destination directory" >&2
            return 1
        end
    end
    
    # Check if destination exists and prompt for confirmation
    if test -e "$dest"
        echo "Destination '$dest' already exists. Overwrite? [y/N]"
        read -l confirm
        if test "$confirm" != "y"
            echo "Operation cancelled"
            return 0
        end
    end
    
    # Perform operation
    switch "$operation"
        case copy
            if cp "$source" "$dest"
                echo "Successfully copied '$source' to '$dest'"
            else
                echo "Error: failed to copy file" >&2
                return 1
            end
        case move
            if mv "$source" "$dest"
                echo "Successfully moved '$source' to '$dest'"
            else
                echo "Error: failed to move file" >&2
                return 1
            end
    end
end
```

## How to handle file and folder paths for dependencies

As your scripts become more complex, you might need to handle loading multiple scripts. In this case
you can just pull other scripts in from your current script by using `source my-script.fish`.
However fish looks for this `my-script.fish` file in the current directory, from which you started
executing the script. And this current directory might not match where you need to load this
dependency from. This can happen if your main script is on the `$PATH` but the dependencies are not.
In this case, you can do something like the following in your main script.

```bash
set MY_FOLDER_PATH (dirname (status --current-filename))
source $MY_FOLDER_PATH/my-script.fish
```

So what this snippet actually does is get the folder in which the main script is running, and stores
it in `MY_FOLDER_PATH` and then it become possible for any dependencies to be loaded using the
`source` command. There is one limitation to this approach, which is that the path stored in
`MY_FOLDER_PATH` is relative to the directory from which the main script is actually executed. This
is a subtle detail that you may not care about, unless you need to have absolute path names. In this
case you can do the following.

```bash
set MY_FOLDER_PATH (realpath (dirname (status --current-filename)))
source $MY_FOLDER_PATH/my-script.fish
```

Using [`realpath`](https://man7.org/linux/man-pages/man1/realpath.1.html) gives you the fully
qualified path name for your folder for the uses cases where you need this capability.

## How to write multi line strings to files

There are many situations where you need to write strings and multi line strings to new or existing
files in your scripts.

Here's an example of writing single strings to a file.

```bash
# echo "echo 'ClientAliveInterval 60' >> recurring-tasks.log" | xargs -I% sudo sh -c %
set linesToAdd "TCPKeepAlive yes" "ClientAliveInterval 60" "ClientAliveCountMax 120"
for line in $linesToAdd
  set command "echo '$line' >> /etc/ssh/sshd_config"
  executeString "$command | xargs -I% sudo sh -c %"
end
```

Here's an example of writing multi line strings to a file.

```bash
# More info on writing multiline strings: https://stackoverflow.com/a/35628657/2085356
function _workflowWriteEmptyMarkdownContentToFile --argument datestr filename
  echo > $filename "\
---
Title: About $filename
Date: $datestr
---
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Your heading
"
end
```

## How to create colorized echo output

The [`set_color`](https://fishshell.com/docs/current/cmds/set_color.html) function allows fish to
colorize and format text content that is printed to `stdout` using `echo`. This is great when
creating text output that needs to have different foreground, background colors, and bold, italic,
or underlined output. There are many ways to use this command, and here are two examples of how to
use it (inline of `echo` statements, and just by itself).

```bash
function myFunction
  if test (count $argv) -lt 2
    set -l currentFunctionName (status function)
    echo "Usage: "(set_color -o -u)"$currentFunctionName"(set_color normal)\
      (set_color blue)" <arg1> "\
      (set_color yellow)"<arg2>"(set_color normal)
    set_color blue
    echo "- <arg1>: Something about arg1."
    set_color yellow
    echo "- <arg2>: Something about arg2"
    set_color normal
    return 1
  end
end
```

Notes:

1. `set_color normal` has to be called to reset whatever formatting options were set in previous
   statements.
2. `set_color -u` does underline, and `set_color -o` does bold.

## How to get user input

There are situations where you need to ask a user for confirmation before performing some
potentially destructive operation or you might need user input for some argument to a function (that
isn't passed via the command line). In these cases it is possible to get user input from the user by
reading `stdin` using the [`read`](https://fishshell.com/docs/current/cmds/read.html) function.

The following function simply returns a `0` for "Y"/"y", and `1` for "N"/"n".

```bash
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
```

And here is an example of using the `_promptUserForConfirmation` function.

```bash
if _promptUserForConfirmation "Delete branch $featureBranchName"
  git branch -D $featureBranchName
  echo "👍 Successfully deleted $featureBranchName"
else
  echo "⛔ Did not delete $featureBranchName"
end
```

## How to use fzf for interactive selection

The [`fzf`](https://github.com/junegunn/fzf) command-line fuzzy finder enables interactive selection from lists with powerful search capabilities. It's particularly useful for creating interactive menus and file selection interfaces in fish scripts.

### Basic selection example

Here's a simple example of using fzf to select from a list of options:

```bash
#!/usr/bin/env fish

# Create a list of options to choose from
set options 'Option 1' 'Option 2' 'Option 3' 'Exit'

# Use fzf for fuzzy searching and selection
set selection (
    printf '%s\n' $options | fzf --prompt 'Select an option: '
)

# Handle the selection
if test -n "$selection"
    echo "You selected: $selection"
else
    echo "No selection made"
end
```

### Interactive file menu example

Here's a more practical example that creates an interactive file operations menu:

```bash
#!/usr/bin/env fish

function interactive_file_menu
    # Define menu options
    set menu_options \
        "📁 Browse files" \
        "🔍 Search in files" \
        "📝 Edit a file" \
        "🗑️  Delete a file" \
        "📊 Show file stats" \
        "❌ Exit"
    
    while true
        # Show menu with fzf (with colors and preview)
        set selection (
            printf '%s\n' $menu_options | \
            fzf --prompt '➤ Choose action: ' \
                --height 40% \
                --layout reverse \
                --border \
                --ansi
        )
        
        # Process selection
        switch "$selection"
            case "📁 Browse files"
                set chosen_file (ls -la | fzf --prompt 'Select file: ')
                echo "You browsed: $chosen_file"
            case "🔍 Search in files"
                echo "Enter search term: "
                read search_term
                grep -r "$search_term" . | fzf
            case "📝 Edit a file"
                set file_to_edit (find . -type f | fzf --preview 'head -20 {}')
                if test -n "$file_to_edit"
                    $EDITOR "$file_to_edit"
                end
            case "🗑️  Delete a file"
                set file_to_delete (find . -type f | fzf --preview 'ls -la {}')
                if test -n "$file_to_delete"
                    echo "Delete $file_to_delete? [y/N]"
                    read confirm
                    if test "$confirm" = "y"
                        rm "$file_to_delete"
                        echo "Deleted: $file_to_delete"
                    end
                end
            case "📊 Show file stats"
                find . -type f | fzf --preview 'stat {}'
            case "❌ Exit" ""
                echo "Goodbye!"
                break
        end
    end
end
```

### Multiple selection example

You can also select multiple items using the `--multi` flag:

```bash
# Select multiple files for batch operations
set selected_files (
    find . -type f -name "*.txt" | \
    fzf --multi \
        --prompt 'Select files (TAB to mark): ' \
        --preview 'cat {}' \
        --preview-window right:50%
)

if test (count $selected_files) -gt 0
    echo "Selected files:"
    for file in $selected_files
        echo "  - $file"
    end
end
```

### Common fzf options

- `--prompt`: Custom prompt text
- `--height`: Display height (percentage or lines)
- `--layout reverse`: Show prompt at top
- `--border`: Add border around fzf
- `--preview`: Show preview window with command
- `--preview-window`: Configure preview window position and size
- `--multi`: Allow multiple selections (use TAB to mark)
- `--ansi`: Enable ANSI color codes

### Installation and usage notes

- fzf must be installed first (`brew install fzf` on macOS, `apt install fzf` on Ubuntu)
- Use TAB for multiple selections when `--multi` is enabled
- Use ESC or Ctrl-C to cancel without making a selection
- Type to fuzzy search through the available options
- Arrow keys or Ctrl-J/Ctrl-K to navigate up and down

## How to use sed

This is useful for removing fragments of files that are not needed, especially when `xargs` is used
to pipe the result of `find`.

Here's an example that removes `./` from the start of each file that's found.

```bash
echo "./.Android" | sed 's/^\.\///'
```

Here's a more complex example of using `sed`, `find`, and `xargs` together.

```bash
set folder .Android*
find ~ -maxdepth 1 -name $folder | sed 's/.\///g' | \
  xargs -I % echo "cleaned up name: %"
```

## How to use xargs

This is useful for piping the output of some commands as arguments for more commands.

Here's a simple example: `ls | xargs echo "folders: "`.

- Which produces this: `folders: idea-http-proxy-settings images tmp`.
- Note how the arguments are concatenated in the output.

Here's a slightly different example using `-I %` which allows arguments to be placed anywhere (not
just at the end).

```bash
ls | xargs -I % echo "folder: %"
```

Which produces this output:

```bash
folder: idea-http-proxy-settings
folder: images
folder: tmp
```

Note how the arguments are each in a separate line.

## How to use cut to split strings

Let's say you have a string `"token1:token2"` and you want to split the string and only keep the
first part of it. This can be done using the following cut command.

```bash
echo "token1:token2" | cut -d ':' -f 1
```

- `-d ':'` - this splits the string by the `:` delimiter
- `-f 1` - this keeps the first field in the tokenized string

Here's a real example of finding all the HTML files in `~/github/developerlife.com` with the string
`"fonts.googleapis"` in it and then opening them up in `subl`.

```bash
cd ~/github/developerlife.com
echo \
"find . -name '*html' | \
 xargs grep fonts.googleapis | \
 cut -d ':' -f 1 | \
 xargs subl" \
 | sh
```

- [More info on the `cut` command](https://www.geeksforgeeks.org/cut-command-linux-examples/)

## How to calculate how long the script took to run

```bash
function timed -d Pass the program or function that you want to execute as an argument
  set START_TS (date +%s)

  # This is where your code would go.
  $argv

  sleep 5

  set END_TS (date +%s)
  set RUNTIME (math $END_TS - $START_TS)
  set RUNTIME (math $RUNTIME / 60)
  echo "⏲ Total runtime: $RUNTIME min ⏲"
end
```

## How to debug fish scripts

Fish provides several debugging capabilities to help troubleshoot your scripts and understand what's happening during execution.

### Enable command tracing

Fish can show you every command that's being executed, which is useful for debugging complex scripts:

```bash
#!/usr/bin/env fish

# Enable tracing for debugging
set -g fish_trace 1

# Your script code here
echo "Starting script..."
set MY_VAR "test value"
echo "MY_VAR is: $MY_VAR"

# Disable tracing when done
set -e fish_trace
```

You can also enable tracing for just a portion of your script by setting and unsetting `fish_trace` around specific sections.

### Conditional debug output

Create debug output that only shows when debugging is enabled:

```bash
#!/usr/bin/env fish

function debug_echo -a message
    if set -q DEBUG
        echo "DEBUG: $message" >&2
    end
end

function my_function -a param1 param2
    debug_echo "my_function called with: $param1, $param2"
    
    set result (math $param1 + $param2)
    debug_echo "calculation result: $result"
    
    echo $result
end

# Usage: DEBUG=1 ./my_script.fish
# Or: set -x DEBUG 1; ./my_script.fish
```

### Check command success and status codes

Always check if commands succeeded, especially external commands:

```bash
#!/usr/bin/env fish

function safe_git_pull
    if git pull
        echo "✅ Git pull successful"
        return 0
    else
        echo "❌ Git pull failed with status: $status" >&2
        return $status
    end
end

# Check if a command exists before using it
if command -v fzf >/dev/null
    echo "fzf is available"
else
    echo "fzf is not installed" >&2
    exit 1
end
```

### Validate function arguments

Add argument validation to catch errors early:

```bash
#!/usr/bin/env fish

function process_file -a filename
    # Validate arguments
    if test (count $argv) -eq 0
        echo "Error: filename required" >&2
        echo "Usage: process_file <filename>" >&2
        return 1
    end
    
    if not test -f "$filename"
        echo "Error: file '$filename' does not exist" >&2
        return 1
    end
    
    if not test -r "$filename"
        echo "Error: file '$filename' is not readable" >&2
        return 1
    end
    
    # Process the file
    echo "Processing $filename..."
end
```

### Use verbose output for complex operations

Show what your script is doing step by step:

```bash
#!/usr/bin/env fish

function verbose_copy -a source dest
    set -l verbose_flag ""
    if set -q VERBOSE
        set verbose_flag "-v"
        echo "Copying $source to $dest..."
    end
    
    if cp $verbose_flag "$source" "$dest"
        if set -q VERBOSE
            echo "✅ Copy successful"
        end
    else
        echo "❌ Copy failed" >&2
        return 1
    end
end

# Usage: VERBOSE=1 ./my_script.fish
```

### Debug script timing and performance

Profile sections of your script to identify bottlenecks:

```bash
#!/usr/bin/env fish

function time_section -a section_name
    if set -q DEBUG_TIMING
        set start_time (date +%s.%3N)
        # Execute the commands passed as arguments
        $argv[2..-1]
        set end_time (date +%s.%3N)
        set duration (math $end_time - $start_time)
        echo "TIMING: $section_name took $duration seconds" >&2
    else
        # Just execute the commands without timing
        $argv[2..-1]
    end
end

# Usage example
time_section "file_processing" find . -name "*.txt" -exec wc -l {} \;
time_section "git_operations" git add . && git commit -m "Update files"
```

### Environment variable debugging

Show important environment variables for troubleshooting:

```bash
#!/usr/bin/env fish

function show_debug_info
    if set -q DEBUG
        echo "=== DEBUG INFO ===" >&2
        echo "Script: "(status --current-filename) >&2
        echo "PWD: $PWD" >&2
        echo "USER: $USER" >&2
        echo "PATH: $PATH" >&2
        echo "fish version: "(fish --version) >&2
        echo "=================" >&2
    end
end

# Call at start of script
show_debug_info
```

## Fish scripting best practices

Following these best practices will make your fish scripts more robust, readable, and maintainable.

### Always quote variables

Quote variables to handle spaces and special characters correctly:

```bash
#!/usr/bin/env fish

# Good: quoted variables
set filename "my file with spaces.txt"
if test -f "$filename"
    echo "File exists: $filename"
end

# Bad: unquoted variables (will break with spaces)
if test -f $filename
    echo "This will fail with spaces in filename"
end
```

### Use meaningful variable names

Choose descriptive names that make your code self-documenting:

```bash
#!/usr/bin/env fish

# Good: descriptive names
set config_file_path "$HOME/.config/myapp/config.json"
set backup_directory "/backup/myapp"
set max_retry_attempts 3

# Bad: cryptic names
set cfp "$HOME/.config/myapp/config.json"
set bd "/backup/myapp"
set mra 3
```

### Validate inputs and handle errors

Always validate function parameters and handle potential errors:

```bash
#!/usr/bin/env fish

function backup_file -a source_file backup_dir
    # Validate required parameters
    if test (count $argv) -lt 2
        echo "Usage: backup_file <source_file> <backup_dir>" >&2
        return 1
    end
    
    # Validate source file exists and is readable
    if not test -f "$source_file"
        echo "Error: Source file '$source_file' does not exist" >&2
        return 1
    end
    
    if not test -r "$source_file"
        echo "Error: Cannot read source file '$source_file'" >&2
        return 1
    end
    
    # Validate backup directory
    if not test -d "$backup_dir"
        echo "Creating backup directory: $backup_dir"
        mkdir -p "$backup_dir"
    end
    
    # Perform backup with error checking
    if cp "$source_file" "$backup_dir/"
        echo "Successfully backed up '$source_file' to '$backup_dir'"
        return 0
    else
        echo "Failed to backup '$source_file'" >&2
        return 1
    end
end
```

### Use local variables in functions

Use `set -l` to keep variables local to function scope:

```bash
#!/usr/bin/env fish

function calculate_average
    set -l numbers $argv
    set -l sum 0
    set -l count (count $numbers)
    
    # Local variables don't pollute global scope
    for num in $numbers
        set sum (math $sum + $num)
    end
    
    set -l average (math $sum / $count)
    echo $average
end
```

### Prefer fish builtins over external commands

Use fish's built-in commands when possible for better performance and portability:

```bash
#!/usr/bin/env fish

# Good: use fish string builtin
set filename "document.pdf"
if string match -q "*.pdf" "$filename"
    echo "PDF file detected"
end

# Less optimal: external grep
if echo "$filename" | grep -q "\.pdf$"
    echo "PDF file detected"
end

# Good: use fish test builtin
if test -f "$filename"
    echo "File exists"
end

# Less optimal: external test command
if /bin/test -f "$filename"
    echo "File exists"
end
```

### Use command substitution appropriately

Store command output in variables for reuse and error checking:

```bash
#!/usr/bin/env fish

function check_git_status
    # Store command output for reuse
    set git_status (git status --porcelain 2>/dev/null)
    
    # Check if git command succeeded
    if test $status -ne 0
        echo "Not a git repository" >&2
        return 1
    end
    
    # Now we can use the result multiple times
    if test -z "$git_status"
        echo "Repository is clean"
    else
        echo "Repository has changes:"
        echo "$git_status"
    end
end
```

### Use functions for reusable code

Break complex scripts into smaller, reusable functions:

```bash
#!/usr/bin/env fish

function log_message -a level message
    set timestamp (date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message"
end

function create_backup -a source dest
    log_message "INFO" "Starting backup from '$source' to '$dest'"
    
    if cp -r "$source" "$dest"
        log_message "SUCCESS" "Backup completed successfully"
        return 0
    else
        log_message "ERROR" "Backup failed"
        return 1
    end
end

# Main script logic
create_backup "/important/data" "/backup/location"
```

### Handle signals gracefully

Set up signal handlers for clean script termination:

```bash
#!/usr/bin/env fish

# Clean up temporary files on exit
function cleanup
    if set -q temp_file
        rm -f "$temp_file"
    end
    if set -q temp_dir
        rm -rf "$temp_dir"
    end
end

# Set up signal handlers
trap cleanup EXIT
trap 'echo "Script interrupted"; cleanup; exit 130' INT

# Your script logic here
set temp_file (mktemp)
set temp_dir (mktemp -d)
```

### Use consistent exit codes

Follow standard exit code conventions:

```bash
#!/usr/bin/env fish

function my_script
    # 0 = success
    # 1 = general error
    # 2 = usage error
    # 130 = script terminated by Control-C
    
    if test (count $argv) -eq 0
        echo "Usage: my_script <filename>" >&2
        return 2  # Usage error
    end
    
    if not test -f "$argv[1]"
        echo "File not found: $argv[1]" >&2
        return 1  # General error
    end
    
    # Process file...
    echo "Processing $argv[1]"
    return 0  # Success
end
```

### Document your functions

Use the `--description` flag to document function purpose:

```bash
#!/usr/bin/env fish

function process_log_files --description "Process and rotate log files older than specified days"
    # Function implementation here
    echo "Processing log files..."
end

function backup_database --description "Create timestamped backup of database to specified directory"
    # Function implementation here
    echo "Backing up database..."
end

# Users can see function descriptions with: functions --details function_name
```

## Common fish scripting pitfalls

These are frequent mistakes that can cause confusing behavior in fish scripts. Learning to avoid them will save you debugging time.

### Forgetting that all variables are lists

In fish, every variable is a list, even if it contains only one element. This can lead to unexpected behavior:

```bash
#!/usr/bin/env fish

# Pitfall: assuming single values
set filename "my file.txt"
set result (echo $filename)  # This works fine

# But when you have multiple values:
set filenames "file1.txt" "file2.txt" "file3.txt"
set result (echo $filenames)  # This passes 3 arguments to echo

# Correct: quote the variable to treat as single argument
set result (echo "$filenames")  # This treats the whole list as one string
```

### Using bash syntax in fish

Fish syntax is different from bash/sh. These bash patterns don't work in fish:

```bash
#!/usr/bin/env fish

# Bash syntax that doesn't work in fish:
# if [ "$var" = "value" ]     # Use 'test' instead
# export VAR=value            # Use 'set -x VAR value'
# VAR=value command           # Use 'env VAR=value command'
# $((1 + 2))                  # Use 'math 1 + 2'
# ${var:-default}             # Use separate if/else logic

# Fish equivalents:
if test "$var" = "value"
    echo "correct fish syntax"
end

set -x VAR value              # export variable
env VAR=value command         # set variable for single command
set result (math 1 + 2)       # arithmetic
```

### Mixing up `set -q` (exists) vs `test -z` (empty)

These test different things and can cause logic errors:

```bash
#!/usr/bin/env fish

# set -q tests if variable EXISTS
# test -z tests if variable is EMPTY

set empty_var ""
set undefined_var  # This variable doesn't exist

# This will be TRUE (variable exists but is empty)
if set -q empty_var
    echo "empty_var exists"
end

# This will be FALSE (variable doesn't exist)
if set -q undefined_var
    echo "This won't print"
end

# This will be TRUE (variable is empty)
if test -z "$empty_var"
    echo "empty_var is empty"
end

# This will be TRUE (undefined variables are treated as empty strings)
if test -z "$undefined_var"
    echo "undefined_var is also considered empty"
end
```

### Not quoting variables with spaces

Unquoted variables with spaces will be split into multiple arguments:

```bash
#!/usr/bin/env fish

set file_with_spaces "my document.pdf"

# Wrong: this will fail because it becomes 'test -f my document.pdf'
# which is 3 arguments instead of the filename
if test -f $file_with_spaces
    echo "This test will fail incorrectly"
end

# Correct: quote the variable
if test -f "$file_with_spaces"
    echo "This works correctly"
end

# Wrong: will try to copy 'my', 'document.pdf' separately
cp $file_with_spaces /backup/

# Correct: treats as single filename
cp "$file_with_spaces" /backup/
```

### Incorrect variable expansion in loops

Variable expansion behaves differently in different contexts:

```bash
#!/usr/bin/env fish

set items "item1" "item2" "item3"

# Pitfall: trying to modify the loop variable
for item in $items
    set item "modified_$item"  # This creates a new local variable!
    echo $item                  # Prints modified version
end

echo $items  # Original list is unchanged!

# Correct approach: use a different variable or array indexing
for i in (seq (count $items))
    set items[$i] "modified_$items[$i]"
end
```

### Forgetting command substitution captures stdout only

Command substitution with `()` only captures stdout, not stderr:

```bash
#!/usr/bin/env fish

# This will capture the error count, but error messages go to terminal
set error_output (find /root -name "*.txt" 2>&1)  # Capture both stdout and stderr

# Better: separate handling of stdout and stderr
find /root -name "*.txt" 2>/tmp/find_errors.log
set found_files (find /root -name "*.txt" 2>/dev/null)

if test -s /tmp/find_errors.log
    echo "Errors occurred during find operation"
end
```

### Using `!` for negation instead of `not`

Fish uses `not` for logical negation, not `!`:

```bash
#!/usr/bin/env fish

set filename "document.txt"

# Wrong: bash/sh syntax
# if ! test -f "$filename"

# Correct: fish syntax
if not test -f "$filename"
    echo "File doesn't exist"
end

# Also works with commands
if not git pull
    echo "Git pull failed"
end
```

### Assuming `$0` contains the script name

In fish, `$argv[0]` or `(status current-filename)` should be used instead of `$0`:

```bash
#!/usr/bin/env fish

# Wrong: $0 doesn't exist in fish
# echo "Script name: $0"

# Correct ways to get script name:
echo "Script name: "(status current-filename)
echo "Script basename: "(basename (status current-filename))

# For command line arguments:
echo "First argument: $argv[1]"
echo "All arguments: $argv"
echo "Number of arguments: "(count $argv)
```

### Not checking command exit status

Always verify that commands succeeded, especially in automated scripts:

```bash
#!/usr/bin/env fish

# Pitfall: assuming commands always succeed
git clone https://github.com/user/repo.git
cd repo
make install

# Better: check each step
if not git clone https://github.com/user/repo.git
    echo "Failed to clone repository" >&2
    exit 1
end

if not cd repo
    echo "Failed to enter repository directory" >&2
    exit 1
end

if not make install
    echo "Failed to install" >&2
    exit 1
end
```

### Global variable pollution

Functions can accidentally modify global variables if you don't use local scope:

```bash
#!/usr/bin/env fish

set counter 10

function increment_counter
    # Pitfall: modifying global variable unintentionally
    set counter (math $counter + 1)
    echo "Counter in function: $counter"
end

increment_counter
echo "Global counter: $counter"  # This is now 11, which might be unexpected

# Better: use local variables when appropriate
function safe_increment -a input
    set -l local_counter (math $input + 1)
    echo $local_counter  # Return the result
end

set counter (safe_increment $counter)
```
