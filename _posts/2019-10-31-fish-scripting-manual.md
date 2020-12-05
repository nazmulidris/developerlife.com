---
author: Nazmul Idris
date: 2019-10-31 17:43:35+00:00
excerpt: |
  Short manual on how to program using fish shell's scripting language.
layout: post
hero-image: assets/fish-shell.svg
title: "fish shell scripting manual"
categories:
  - Misc
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [How to set variables](#how-to-set-variables)
- [How to write for loops](#how-to-write-for-loops)
- [How to write if statements](#how-to-write-if-statements)
  - [Commonly used conditions](#commonly-used-conditions)
  - [Multiple conditions with operators: and, or](#multiple-conditions-with-operators-and-or)
  - [References](#references)
- [How to perform string comparisons](#how-to-perform-string-comparisons)
- [How to write switch statements for strings](#how-to-write-switch-statements-for-strings)
- [How to execute strings](#how-to-execute-strings)
- [How to write functions](#how-to-write-functions)
- [How to pass parameters to functions](#how-to-pass-parameters-to-functions)
- [How to use sed](#how-to-use-sed)
- [How to use xargs](#how-to-use-xargs)
- [How to use cut to split strings](#how-to-use-cut-to-split-strings)
- [How to calculate how long the script took to run](#how-to-calculate-how-long-the-script-took-to-run)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

Learn how to write fish shell scripts by example.

## How to set variables

Here's a simple example of assigning a value to a variable.

```bash
set MY_VAR "some value"
```

Here's an example of appending values to a variable. By default fish variables are lists.

```bash
set MY_VAR $MY_VAR "another value"
```

This is how you can create lists.

```bash
set MY_LIST "value1" "value2" "value3"
```

Here's an example of storing value returned from the execution of a command to a variable.

```bash
set OUR_VAR (math 1+2)
set OUR_VAR (date +%s)
set OUR_VAR (math $OUR_VAR / 60)
```

Since all fish variables are lists, you can access individual elements using `[n]` operator, where `n=1` for the first
element (not 0 index). Here's an example. And negative numbers access elements from the end.

```bash
set LIST one two three
echo $LIST[1]  # one
echo $LIST[2]  # two
echo $LIST[3]  # three
echo $LIST[-1] # This is the same element as above
```

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
set FOLDERS $FOLDERS my \foldername
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

The key to writing if statements is using the `test` command to evaluate some expression to a boolean. This can be
string comparisons or even testing the existence of files and folders. Here are some examples.

### Commonly used conditions

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

Here's an example of how to use the `not` operator in the previous example.

```bash
if not test -d "somefolder"
  echo "somefolder does not exist"
end
```

### Multiple conditions with operators: and, or

If you want to combine multiple conditions into a single statement, then you can use `or` and `and` operators. Also if
you want to check the inverse of a condition, you can use `!`. Here's an example of a function that checks for 2
arguments to be passed via the command line. Here's the logic we will describe.

1. If both the arguments are missing, then usage information should be displayed to the CLI, and perform an early
   return.
2. If either one of the arguments is missing, then display a prompt stating that one of the arguments is missing, and
   perform an early return.

```bash
function requires-two-arguments
  # No arguments are passed.
  if set -q $argv
    echo "Usage: requires-two-arguments arg1 arg2"
    return 1
  end
  # Only 1 argument is passed.
  if set -q $argv[1]; or set -q $argv[2]
    echo "arg1 or arg2 can not be empty"
    return 1
  end
  echo "Thank you, got 1) $argv[1] and 2) $argv[2]"
end
```

Here are some notes on the code.

1. What does the `set -q $variable` function do? It returns true if `$variable` is empty.
2. Instead of `set -q`, if you wanted to use `test` function in order to test if a variable is empty, you can use
   `if test ! -n "$variable"`, which is more verbose.
3. If you wanted to replace the `or` check above w/ `test`, this is what it would look like
   `if test ! -n "$argv[1]"; or test ! -n "$argv[2]"`.
4. Note that when you use `or`, `and` operators that you have to terminate the condition expression w/ a `;`.

### References

1. [test command](https://fishshell.com/docs/current/cmds/test.html)
2. [set command](https://fishshell.com/docs/current/cmds/set.html)
3. [if command](https://fishshell.com/docs/current/cmds/if.html)
4. [stackoverflow answer: how to check if fish variable is empty](https://stackoverflow.com/questions/47743015/fish-shell-how-to-check-if-a-variable-is-set-empty)
5. [stackoverflow answer: how to put multiple conditions in fish if statement](https://stackoverflow.com/questions/17900078/in-fish-shell-how-can-i-put-two-conditions-in-an-if-statement)

## How to perform string comparisons

In order to test substring matches in strings you can use the `string match` command. Here is more information on the
command:

1. [Official docs on string match](https://fishshell.com/docs/current/cmds/string-match.html).
2. [Stackoverflow answer on how to use it](https://unix.stackexchange.com/a/504931/302646).

Here's an example of this in action.

```bash
if string match -q "*myname*" $hostname
  echo "$hostname contains myname"
else
  echo "$hostname does not contain myname"
end
```

## How to write switch statements for strings

In order to create switch statements for strings, the `test` command is used here as well (just like it was for
[if statements](#how-to-write-if-statements)). The `case` statements need to match substrings, which can be expressed
using a combination of wildcard chars and the substring you want to match. Here's an example.

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

This not only makes it easier to debug, but also avoids strange errors when doing multi-line breaks using `\`.

## How to write functions

A fish function is just a list of commands that may optionally take arguments. These arguments are just passed in as a
list (since all variables in fish are lists).

Here's an example.

```bash
function say_hi
  echo "Hi $argv"
end
say_hi
say_hi everbody!
say_hi you and you and you
```

Once you have written a function you can see what it is by using `type`, eg: `type say_hi` will show you the function
that you just created above.

- [Here's the doc for functions](https://fishshell.com/docs/current/tutorial.html#tut_functions)

## How to pass parameters to functions

Instead of using `$argv` to figure out what parameters were passed to a function, you can provide a list of named
parameters that a function expects. Here is more information on this
[from the official docs](https://fishshell.com/docs/current/cmds/function.html).

Here's an example.

```bash
function testFunction -a param1 param2
  echo "arg1 = $param1"
  echo "arg2 = $param2"
end
testFunction A B
```

## How to use sed

This is useful for removing fragments of files that are not needed, especially when `xargs` is used to pipe the result
of `find`.

Here's an example that removes `./` from the start of each file that's found.

```bash
echo "./.Android" | sed 's/.\///g'
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

Here's a slightly different example using `-I %` which allows arguments to be placed anywhere (not just at the end).

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

Let's say you have a string `"token1:token2"` and you want to split the string and only keep the first part of it. This
can be done using the following cut command.

```bash
echo "token1:token2" | cut -d ':' -f 1
```

- `-d ':'` - this splits the string by the `:` delimiter
- `-f 1` - this keeps the first field in the tokenized string

Here's a real example of finding all the HTML files in `~/github/developerlife.com` with the string `"fonts.googleapis"`
in it and then opening them up in `subl`.

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
set START_TS (date +%s)

# This is where your code would go.
sleep 5

set END_TS (date +%s)
set RUNTIME (math $END_TS - $START_TS)
set RUNTIME (math $RUNTIME / 60)
echo "⏲ Total runtime: $RUNTIME min ⏲"
```
