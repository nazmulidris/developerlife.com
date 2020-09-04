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
- [How to write switch statements for strings](#how-to-write-switch-statements-for-strings)
- [How to execute strings](#how-to-execute-strings)
- [How to write functions](#how-to-write-functions)
- [How to use sed](#how-to-use-sed)
- [How to use xargs](#how-to-use-xargs)
- [How to use cut to split strings](#how-to-use-cut-to-split-strings)
- [How to calculate how long the script took to run](#how-to-calculate-how-long-the-script-took-to-run)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

Learn how to write fish shell scripts by example.

## How to set variables

Here's a simple example of assigning a value to a variable.

```shell script
set MY_VAR "some value"
```

Here's an example of appending values to a variable. By default fish variables are lists.

```shell script
set MY_VAR $MY_VAR "another value"
```

This is how you can create lists.

```shell script
set MY_LIST "value1" "value2" "value3"
```

Here's an example of storing value returned from the execution of a command to a variable.

```shell script
set OUR_VAR (math 1+2)
set OUR_VAR (date +%s)
set OUR_VAR (math $OUR_VAR / 60)
```

Since all fish variables are lists, you can access individual elements using `[n]` operator, where `n=1` for the first
element (not 0 index). Here's an example. And negative numbers access elements from the end.

```shell script
set LIST one two three
echo $LIST[1]  # one
echo $LIST[2]  # two
echo $LIST[3]  # three
echo $LIST[-1] # This is the same element as above
```

You can also use ranges from the variable / list, continuing the example above.

```shell script
set LIST one two three
echo $LIST[1..2]  # one two
echo $LIST[2..3]  # two three
echo $LIST[-1..2] # three two
```

- [Here's the doc for lists](https://fishshell.com/docs/current/tutorial.html#tut_lists)

## How to write for loops

Since variables contain lists by default, it is very easy to iterate thru them. Here's an example.

```shell script
set FOLDERS bin
set FOLDERS $FOLDERS .atom
set FOLDERS $FOLDERS github
for FOLDER in $FOLDERS
  echo "item: $FOLDER"
end
```

## How to write if statements

The key to writing if statements is using the `test` command to evaluate some expression to a boolean. This can be
string comparisons or even testing the existence of files and folders. Here are some examples.

String comparison in variable.

```shell script
if test $hostname = "mymachine"
  echo "hostname is mymachine"
end
```

Checking for file existence.

```shell script
if test -e "somefile"
  echo "somefile exists"
end
```

- [Here are the docs on the `test` command](https://fishshell.com/docs/current/commands.html#test)

## How to write switch statements for strings

In order to create switch statements for strings, the `test` command is used here as well (just like it was for
[if statements](#how-to-write-if-statements)). The `case` statements need to match substrings, which can be expressed
using a combination of wildcard chars and the substring you want to match. Here's an example.

```shell script
switch $hostname
case "*substring1*"
  echo "Matches $hostname containing substring1"
case "*substring2*"
  echo "Matches $hostname containing substring2"
end
```

You can combine this w/ if statements as well, and end up w/ something like this.

```shell script
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

```shell script
echo "ls \
  -la" | sh
```

This not only makes it easier to debug, but also avoids strange errors when doing multi-line breaks using `\`.

## How to write functions

A fish function is just a list of commands that may optionally take arguments. These arguments are just passed in as a
list (since all variables in fish are lists).

Here's an example.

```shell script
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

## How to use sed

This is useful for removing fragments of files that are not needed, especially when `xargs` is used to pipe the result
of `find`.

Here's an example that removes `./` from the start of each file that's found.

```shell script
echo "./.Android" | sed 's/.\///g'
```

Here's a more complex example of using `sed`, `find`, and `xargs` together.

```shell script
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

```shell script
ls | xargs -I % echo "folder: %"
```

Which produces this output:

```shell script
folder: idea-http-proxy-settings
folder: images
folder: tmp
```

Note how the arguments are each in a separate line.

## How to use cut to split strings

Let's say you have a string `"token1:token2"` and you want to split the string and only keep the first part of it. This
can be done using the following cut command.

```shell script
echo "token1:token2" | cut -d ':' -f 1
```

- `-d ':'` - this splits the string by the `:` delimiter
- `-f 1` - this keeps the first field in the tokenized string

Here's a real example of finding all the HTML files in `~/github/developerlife.com` with the string `"fonts.googleapis"`
in it and then opening them up in `subl`.

```shell script
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

```shell script
set START_TS (date +%s)

# This is where your code would go.
sleep 5

set END_TS (date +%s)
set RUNTIME (math $END_TS - $START_TS)
set RUNTIME (math $RUNTIME / 60)
echo "⏲ Total runtime: $RUNTIME min ⏲"
```
