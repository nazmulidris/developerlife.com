---
author: Nazmul Idris
date: 2020-11-15 5:00:00+00:00
excerpt: |
  Learn how to customize your Ubuntu UI by using fontconfig, Nerd Fonts, Gestures, and Terminal customization
layout: post
hero-image: assets/ubuntu.svg
title: "Customizing Ubuntu UI"
categories:
  - Linux
  - Misc
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [Fonts](#fonts)
  - [Installing fonts](#installing-fonts)
  - [Nerd Fonts](#nerd-fonts)
  - [Configure default Linux fonts](#configure-default-linux-fonts)
- [Gestures](#gestures)
- [Terminal](#terminal)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

I am a big fan of Ubuntu, and a big fan of fonts and UI tweaks and customizations to make the UX of interacting w/ a
desktop OS as fun and productive as possible (for me). I've compiled a list of change that I've made to my Ubuntu
desktop environment to make it a pleasure for me to use and I'm sharing them here. YMMV 🙂.

## Fonts

I tend to install a collection of fonts that I've been curating over the years on every system that I have. This is a
collection of Google Fonts, open source fonts, and even some macOS fonts (since I also use macOS).

### Installing fonts

In order to install fonts, the easiest thing to do is get [Font Manager](https://fontmanager.github.io/). You can simply
install it by running `sudo apt install -y font-manager`. You can then use Font Manager app to install whatever fonts
you have on your computer.

If you don't want to use this app, you can simply copy all your fonts to the following folder `~/.local/share/fonts`.
And then run `sudo fc-cache -fv` to flush the font cache.

You can also see which fonts you have installed on your system by running `fc-list | grep "<FONT_NAME>"`, where
`<FONT_NAME>` is whatever font you have, eg: `Monaco` or `Hack Nerd Font`.

Some of my favorite fonts are:

1. [JetBrains Mono](https://www.jetbrains.com/lp/mono/)
2. [An assortment of Nerd Fonts: Hack, CodeNewRoman, VictorMono](https://www.nerdfonts.com/font-downloads)
3. [macOS fonts: Monaco, Helvetica Neue, SF Mono](https://www.quora.com/Where-is-Helvetica-Neue-located-on-a-Mac)
4. [Google Fonts: Google Sans, Open Sans](https://fonts.google.com/)
5. [Cascadia Code](https://github.com/microsoft/cascadia-code)

### Nerd Fonts

You can get all the Nerd Fonts [here](https://www.nerdfonts.com/font-downloads). There are so many!🎉 Here are some
rules to make it easy to install fonts you download from there. You can see what these fonts look like
[here](https://www.programmingfonts.org/) before downloading them.

1. The font file name ending in "Code" has ligatures. The file names ending in "Mono" do not have ligatures.
2. There are Windows compatible fonts that are provided in there too.
3. For a given font family, I just delete the Windows compatible fonts, and the files ending in "Mono". And that just
   leaves the files ending in "Code". I then install these fonts as show [above](#installing-fonts).

These fonts have ligatures added, font awesome glyps, and even powerline support (which we will get into
[below](#terminal)), and more.

### Configure default Linux fonts

This is where things are going to get good. It is possible to map the defaults on Linux to whatever type face you
choose. This [article](https://jichu4n.com/posts/how-to-set-default-fonts-and-font-aliases-on-linux/) does an incredible
job of explaining font aliases on Linux.

Here's a fish script that will list the current defaults you have on your system.

```shell
set families serif sans-serif monospace Arial Helvetica Verdana "Times New Roman" "Courier New"
for family in $families
  echo -n "$family: "
  fc-match "$family"
end
```

In order to change these defaults, you can edit (or create) the `~/.config/fontconfig/fonts.conf` file. Here you can
specify actual font files at these families will map to. This gives you a tremendous amount of flexibility to change
things like the default font that Google Chrome uses (which is Arimo). If you've ever wanted to use something other than
Arimo in Gmail, then this is the way in which you can change it.

Here's an example of my `fonts.conf` file.

```xml
<?xml version='1.0'?>
<!DOCTYPE fontconfig SYSTEM 'fonts.dtd'>

<!-- https://jichu4n.com/posts/how-to-set-default-fonts-and-font-aliases-on-linux/ -->

<fontconfig>

  <!-- Set preferred serif, sans serif, and monospace fonts. -->
  <alias>
    <family>serif</family>
    <prefer><family>Helvetica Neue</family></prefer>
  </alias>
  <alias>
    <family>sans-serif</family>
    <prefer><family>Helvetica Neue</family></prefer>
  </alias>
  <alias>
    <family>sans</family>
    <prefer><family>Helvetica Neue</family></prefer>
  </alias>
  <alias>
    <family>monospace</family>
    <prefer><family>Hack Nerd Font</family></prefer>
  </alias>

  <!-- Aliases for commonly used MS fonts. -->
  <match>
    <test name="family"><string>Arial</string></test>
    <edit name="family" mode="assign" binding="strong">
      <string>Helvetica Neue</string>
    </edit>
  </match>
  <match>
    <test name="family"><string>Helvetica</string></test>
    <edit name="family" mode="assign" binding="strong">
      <string>Helvetica Neue</string>
    </edit>
  </match>
  <match>
    <test name="family"><string>Verdana</string></test>
    <edit name="family" mode="assign" binding="strong">
      <string>Helvetica Neue</string>
    </edit>
  </match>
  <match>
    <test name="family"><string>Tahoma</string></test>
    <edit name="family" mode="assign" binding="strong">
      <string>Helvetica Neue</string>
    </edit>
  </match>
  <match>
    <test name="family"><string>Comic Sans MS</string></test>
    <edit name="family" mode="assign" binding="strong">
      <string>Helvetica Neue</string>
    </edit>
  </match>
  <match>
    <test name="family"><string>Times New Roman</string></test>
    <edit name="family" mode="assign" binding="strong">
      <string>Helvetica Neue</string>
    </edit>
  </match>
  <match>
    <test name="family"><string>Times</string></test>
    <edit name="family" mode="assign" binding="strong">
      <string>Helvetica Neue</string>
    </edit>
  </match>
  <match>
    <test name="family"><string>Courier New</string></test>
    <edit name="family" mode="assign" binding="strong">
      <string>Hack Nerd Font</string>
    </edit>
  </match>


</fontconfig>
```

And this is what my terminal output from that fish script above looks like.

```text
serif: Helvetica_Neue_Regular.ttc: "Helvetica Neue" "Regular"
sans-serif: Helvetica_Neue_Regular.ttc: "Helvetica Neue" "Regular"
monospace: Hack Regular Nerd Font Complete.ttf: "Hack Nerd Font" "Regular"
Arial: Helvetica_Neue_Regular.ttc: "Helvetica Neue" "Regular"
Helvetica: Helvetica_Neue_Regular.ttc: "Helvetica Neue" "Regular"
Verdana: Helvetica_Neue_Regular.ttc: "Helvetica Neue" "Regular"
Times New Roman: Helvetica_Neue_Regular.ttc: "Helvetica Neue" "Regular"
Courier New: Hack Regular Nerd Font Complete.ttf: "Hack Nerd Font" "Regular"
```

Additionally, you can get [gnome-tweaks](https://gitlab.gnome.org/GNOME/gnome-tweaks) in order to change some of the
defaults that Gnome uses. Here's an example of what I have under "Fonts".

![]({{'assets/gnome-tweaks.png' | relative_url}})

Finally, this is what my Gmail looks like in Google Chrome.

![]({{'assets/googlechrome.png' | relative_url}})

## Gestures

If you have a touchpad and want to use some of the familiar gestures from macOS, then this
[article](https://medium.com/@kaigo/mac-like-gestures-on-ubuntu-20-04-dell-xps-15-7ea6e3be7f76) has some great
information to get you started. Here are the steps.

```shell
sudo apt-get install -y libinput-tools xdotool python3-setuptools
sudo gpasswd -a $USER input

cd ~/Downloads
git clone https://github.com/bulletmark/libinput-gestures.git
cd libinput-gestures
sudo make install
sudo ./libinput-gestures-setup install
libinput-gestures-setup start
libinput-gestures-setup autostart

cd ~/Downloads
git clone https://gitlab.com/cunidev/gestures
cd gestures
sudo python3 setup.py install
```

At this point you will have installed `libinput-tools`, `xdotool`, and `gestures`. You can run the `gestures` app to
configure your gestures. Here's a [list](https://gitlab.com/cunidev/gestures/-/wikis/xdotool-list-of-key-codes) of
[`xdotool`](https://linuxhint.com/xdotool_stimulate_mouse_clicks_and_keystrokes/) keycodes that you will need to type
into your app. The following is a sample of my configuration for this app.

```text
# Generated by Gestures 0.2.3  -->  https://gitlab.com/cunidev/gestures
# Manual editing might result in data loss!


# Invalid lines


# Unsupported lines

# Swipe threshold (0-100)
swipe_threshold 0

# Gestures
gesture swipe right 4 xdotool key 'Super_L+Page_Down'
gesture swipe left 4 xdotool key 'Super_L+Page_Up'
gesture swipe up 4 xdotool key 'Super_L'
gesture pinch in 2 xdotool key 'Control_L+minus'
gesture pinch out 2 xdotool key 'Control_L+plus'
```

If you look at the first `gesture` it does the following: Swipe left w/ 4 fingers results in "Super + Page Down" keys to
be pressed by `xdotool`. You can configure these gestures to map to key presses that you have configured on your system
to do whatever it is that you want. For me, I use [Ultimate Hacking Keyboards](http://uhk.io) and have my keyboard
mapped to do lots of workspace management things (like switch workspaces, switch windows between workspaces, etc) and I
use my custom key mappings for these `xdotool` commands.

## Terminal

Finally, we come to the terminal and shell selection and configuration. I use
[fish shell](https://www.realjenius.com/2020/05/30/oh-my-fish/), and I've also written a
[tutorial](https://developerlife.com/2019/10/31/fish-scripting-manual/) that I have on advanced fish scripting.

I also have [Oh-my-fish](https://github.com/oh-my-fish/oh-my-fish) installed along w/
[bobthefish](https://github.com/oh-my-fish/theme-bobthefish).

So here are the commands after you have fish installed, to get "OMF" and "bobthefish" installed.

```shell
curl -L https://get.oh-my.fish | fish
omf install bobthefish
```

Next we have to get `powerline` setup, and you can follow
[this guide](https://gist.github.com/TrentSPalmer/63a85b582d42ab4bff665fc2dbba42e2) on how to get that going. Here are
the steps.

First install `powerline`.

```shell
apt install fish powerline
```

And then add the following lines to your `~/.config/fish/config.fish` file. Note this snippet makes a check to see if
you are running macOS or Linux.

```shell
# Powerline changes.
# More info: https://gist.github.com/TrentSPalmer/63a85b582d42ab4bff665fc2dbba42e2
# Linux:
#   - Make sure `omf` and `bobthefish` is already installed in fish.
#   - Also make sure `powerline` is installed on linux.
# macOS:
#   - Make sure to install powerline using pip3 in the user directory
#     - More info: https://medium.com/@ITZDERR/how-to-install-powerline-to-pimp-your-bash-prompt-for-mac-9b82b03b1c02
#   - Make sure to use Nerd Fonts in the terminal
if test (uname) = "Darwin"
  set POWERLINE_PATH /Users/nazmul/Library/Python/3.9/lib/python/site-packages
  # I couldn't get it work.
else
  set POWERLINE_PATH /usr/share
  set fish_function_path $fish_function_path "$POWERLINE_PATH/powerline/bindings/fish"
  source $POWERLINE_PATH/powerline/bindings/fish/powerline-setup.fish
  powerline-setup
end
```

And that's it! You can use a font like `Hack Nerd Font` in your terminal or something else. Here's what my terminal
configuration looks like (you can save it to a file named `terminal.prefs`).

```ini
[/]
new-terminal-mode='window'
schema-version=uint32 3

[keybindings]
close-tab='<Primary>w'
close-window='<Primary>q'
move-tab-left='<Alt>comma'
move-tab-right='<Alt>period'
new-tab='<Primary>t'
new-window='<Primary><Shift>t'
next-tab='<Primary>Tab'
preferences='<Super>comma'
prev-tab='<Primary><Shift>Tab'

[profiles:/:b1dcc9dd-5262-4d8d-a863-c897e6d979b9]
audible-bell=true
background-color='rgb(0,0,0)'
background-transparency-percent=19
bold-is-bright=true
cell-height-scale=1.2000000000000002
custom-command='fish'
default-size-columns=140
font='Monaco 12'
foreground-color='rgb(211,215,207)'
login-shell=false
palette=['rgb(46,52,54)', 'rgb(204,0,0)', 'rgb(78,154,6)', 'rgb(196,160,0)', 'rgb(52,101,164)', 'rgb(117,80,123)', 'rgb(6,152,154)', 'rgb(211,215,207)', 'rgb(150,179,121)', 'rgb(239,41,41)', 'rgb(138,226,52)', 'rgb(252,233,79)', 'rgb(114,159,207)', 'rgb(173,127,168)', 'rgb(52,226,226)', 'rgb(238,238,236)']
use-custom-command=true
use-system-font=false
use-theme-colors=false
use-theme-transparency=false
use-transparent-background=true
visible-name='nazmul'
```

These can be loaded into Gnome using the following command.

```shell
# More info: https://askubuntu.com/a/1241849/872482
cat terminal.prefs | dconf load /org/gnome/terminal/legacy/
```

Here's what my terminal looks like.

![]({{'assets/fishshell.png' | relative_url}})
