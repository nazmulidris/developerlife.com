---
author: Nazmul Idris
date: 2021-03-04 14:00:00+00:00
excerpt: |
  Learn how to customize your Ubuntu UI with fontconfig, Nerd Fonts, adding gestures, customizing Terminal, and using
  Gnome extensions for Theming and Window tiling. And IDEA theming.
layout: post
title: "Customizing Ubuntu UI"
categories:
  - Linux
  - Misc
  - Productivity
---

<img class="post-hero-image" src="{{ 'assets/ubuntu.svg' | relative_url }}"/>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [Fonts](#fonts)
  - [Installing fonts](#installing-fonts)
  - [Nerd Fonts](#nerd-fonts)
  - [Configure default Linux fonts](#configure-default-linux-fonts)
- [Terminal and shell UI customization](#terminal-and-shell-ui-customization)
  - [Step 1 - Install `fish`, and `powerline` using `bash`](#step-1---install-fish-and-powerline-using-bash)
  - [Step 2 - Next launch `fish` and install OMF and bobthefish](#step-2---next-launch-fish-and-install-omf-and-bobthefish)
  - [Step 3 - Use Nord theme for your terminal and shell](#step-3---use-nord-theme-for-your-terminal-and-shell)
  - [Step 4 - (Optional) Use a custom theme for your terminal app and shell](#step-4---optional-use-a-custom-theme-for-your-terminal-app-and-shell)
- [GNOME tweaks and extensions](#gnome-tweaks-and-extensions)
  - [1. Window tiling](#1-window-tiling)
  - [2. Gnome User Themes](#2-gnome-user-themes)
  - [3. Saving and restoring all gnome settings](#3-saving-and-restoring-all-gnome-settings)
- [Customize Chrome and Firefox](#customize-chrome-and-firefox)
- [IDEA theming](#idea-theming)
- [Mouse customization](#mouse-customization)
  - [Minimum customization - solaar](#minimum-customization---solaar)
  - [Maximum customization - ratbag and piper](#maximum-customization---ratbag-and-piper)
- [Gestures](#gestures)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

I am a big fan of Ubuntu, and a big fan of fonts and UI tweaks and customizations to make the UX of interacting w/ a
desktop OS as fun and productive as possible (for me). I've compiled a list of change that I've made to my Ubuntu
desktop environment to make it a pleasure for me to use and I'm sharing them here. YMMV 🙂.

## Fonts

I tend to install a collection of fonts that I've been curating over the years on every system that I have. This is a
collection of Google Fonts, open source fonts, and even some macOS fonts (since I've also used macOS).

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

## Terminal and shell UI customization

Here are some of my choices for terminal and shell selection and configuration.

1. I use [tilix](https://gnunn1.github.io/tilix-web/) as my main terminal emulator, as I love the ability to tile
   sessions inside the main window so easily.
2. I use [fish shell](https://www.realjenius.com/2020/05/30/oh-my-fish/), and I've also written a
   [tutorial](https://developerlife.com/2019/10/31/fish-scripting-manual/) that I have on advanced fish scripting.
3. I also have [Oh-my-fish](https://github.com/oh-my-fish/oh-my-fish) installed along w/
   [bobthefish](https://github.com/oh-my-fish/theme-bobthefish).
4. I also use `powerline` in order to get the prompt for my shell.

### Step 1 - Install `fish`, and `powerline` using `bash`

```shell
# Install the latest version of fish v3 (apt has older versions).
sudo apt-add-repository -y ppa:fish-shell/release-3
sudo apt update
sudo apt -y install fish powerline
# Make fish your default shell.
sudo chsh --shell /usr/bin/fish
```

### Step 2 - Next launch `fish` and install OMF and bobthefish

```shell
# Download OMF install script and run it.
set omfInstallScript "https://raw.githubusercontent.com/oh-my-fish/oh-my-fish/master/bin/install"
pushd $HOME/Downloads
curl -L $omfInstallScript > install
chmod +x install
./install -y --noninteractive --path=$HOME/.local/share/omf --config=$HOME/.config/omf
popd

# After installing OMF, use it to install bobthefish.
fish -c "omf install bobthefish"
```

### Step 3 - Use Nord theme for your terminal and shell

There are some great themes that are already available which you can easily use in your terminal.
[`Nord`](https://www.nordtheme.com/) is a great example of this. Not only is it supported in Tilix, and Gnome Terminal,
but you can get this theme for IntelliJ IDEA, Sublime Text 3, and most other developer facing apps.

You can download "ports" of `Nord` for various apps [here](https://www.nordtheme.com/ports):

- [Tilix](https://www.nordtheme.com/ports/tilix)
- [Sublime Text](https://www.nordtheme.com/ports/sublime-text)
- [IntelliJ IDEA](https://www.nordtheme.com/ports/jetbrains)
- [GNOME Terminal](https://www.nordtheme.com/ports/gnome-terminal)

In order to get this theme installed in each of these applications, just visit the link for the "port" for that app and
follow the instructions to get it installed. Most of these instructions are very simple.

### Step 4 - (Optional) Use a custom theme for your terminal app and shell

If you don't want to use a preexisting theme like `Nord` in your terminal, then you can create your own. Here's an
example of a custom configuration that I had created in the past.

You can use a font like `Hack Nerd Font` in your terminal or something else. Here's what my terminal configuration looks
like (you can save it to a file named `terminal.prefs`).

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
palette=['rgb(46,52,54)', 'rgb(204,0,0)', 'rgb(78,154,6)', 'rgb(196,160,0)',\
  'rgb(52,101,164)', 'rgb(117,80,123)', 'rgb(6,152,154)', 'rgb(211,215,207)',\
  'rgb(150,179,121)', 'rgb(239,41,41)', 'rgb(138,226,52)', 'rgb(252,233,79)',\
  'rgb(114,159,207)', 'rgb(173,127,168)', 'rgb(52,226,226)', 'rgb(238,238,236)']
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

Here's what this configuration looks like.

![]({{'assets/fishshell.png' | relative_url}})

## GNOME tweaks and extensions

GNOME has a lot of amazing extensions that can radically transform the way it looks and behaves. I've found a few really
useful extensions that make some radical changes to both the form and function of GNOME. In order to use them you have
make sure that you install `gnome-tweaks` on your computer, and an extension for Chrome or Firefox.

1. Install this on your computer: `sudo apt install -y gnome-tweaks`
2. Install this GNOME Shell integration extension browser extension for:
   - [Chrome](https://chrome.google.com/webstore/detail/gnome-shell-integration/gphhapmejobijbbhgpjhcjognlahblep)
   - [Firefox](https://addons.mozilla.org/en-US/firefox/addon/gnome-shell-integration/)

After this is done, you can visit the GNOME extensions site and navigate to any extension and simply install it from the
your browser of choice.

### 1. Window tiling

I love tiling window managers. This is another reason that I use Tilix as my main terminal emulator of choice.
[tmux](https://github.com/tmux/tmux/wiki) is great for doing this if you don't use Tilix, since it is terminal app
agnostic. I haven't switched to i3 or awesomewm yet, but I have found some nice tiling window extensions that I use.

1. [Gnomesome](https://extensions.gnome.org/extension/1268/gnomesome/) works on Ubuntu 20
2. [Tilinggnome](https://extensions.gnome.org/extension/1286/tilingnome/) works on Ubuntu 18

Both these window managers are very similar, and they have similar keyboard shortcuts. One thing that I had to tweak
after using either of these extensions is to change the highlight on the currently focused window. Normally, I would use
"Alt+Tab" to switch between windows, however, with these tiling extensions I just end up using "Super+J/K". By default
it isn't clear which window is currently focused. Using the following
[article on how to decorate the currently focused window on gtk](https://askubuntu.com/questions/1098539/how-to-make-active-window-visually-stand-out-more-in-ubuntu-18-04-gnome-3)
I was able to devise a solution. Here's the `gtk.css` file that I created, which has to be placed in the
`$HOME/.config/gtk-3.0` folder. Make sure to logout and back in again for this to take effect. Here's what the `gtk.css`
file looks like.

```css
/* More info: https://tinyurl.com/y75aen2n */
@define-color backdrop_color #2B303A;
@define-color highlight_color #FF5D2A;

/* Border around windows. */
/* Focused. */
decoration {
  border: 7px solid @highlight_color;
  background: @highlight_color;
  border-radius: 5px;
}
/* Unfocused. */
decoration:backdrop {
  border: 7px solid @backdrop_color;
  background: @backdrop_color;
  border-radius: 5px;
}

/* Title/headerbar colors. */
headerbar.titlebar {
  background: @highlight_color;
}
headerbar.titlebar:backdrop {
  background: @backdrop_color;
}
```

Here's a screenshot of what this looks like.

![]({{'assets/ubuntu-ui-tiling-focused-window.png' | relative_url}})

I have since remapped my "Alt+Tab" to "Super+J" since I use [UHK keyboard](https://ultimatehackingkeyboard.com/). I
actually remapped "Mod+Tab" to invoke "Super+J" instead of "Alt+Tab". Here is a [my review of the UHK
v1]({{ '/2021/03/09/mechanical-keyboard-review/' | relative_url}}).

### 2. Gnome User Themes

Another big change that you can make in GNOME is changing the theme. This changes the look and feel of the entire
operating system. You can also change icon sets as well. One of my favorite theme and icon sets is Nordic. You can
download the theme and icon set from [here](https://www.gnome-look.org/p/1267246/). Here are the steps you then have to
follow.

1. Download the theme file
   [`Nordic-darker.tar.xz`](https://www.gnome-look.org/p/1267246/startdownload?file_id=1614716124&file_name=Nordic-darker.tar.xz&file_type=application/x-xz&file_size=829400)
   and extract it to `$HOME/.themes`.
2. Download the icon pack
   [`Nordic-Folders.tar.xz`](https://www.gnome-look.org/p/1267246/startdownload?file_id=1567965545&file_name=Nordic-Folders.tar.xz&file_type=application/x-xz&file_size=24000)
   and extract it to `$HOME/.icons`.
3. Install the [GNOME User Themes extension](https://extensions.gnome.org/extension/19/user-themes/).
4. Launch `gnome-tweaks` and then select the Themes from the various drop downs in the "Appearance" section.

![]({{'assets/ubuntu-ui-theme.png' | relative_url}})

### 3. Saving and restoring all gnome settings

Now that so much work has been put into GNOME settings it is prudent to back these settings up. This is really easy.
Make sure that you have `dconf-editor` installed.

Then run the following to backup.

```shell
dconf dump / > gnome.all.prefs
```

And run the following to restore.

```shell
cat gnome.all.prefs | dconf load /
```

These commands will save and restore **all** your GNOME settings. So if you have keyboard shortcuts that you created for
GNOME, these will be saved too, along with gnome-terminal app settings.

## Customize Chrome and Firefox

I have the following extensions installed for Chrome (and Firefox for most of them) to enhance my browsing experience.

- R3BL Shorty URL link shortener -
  [chrome](https://chrome.google.com/webstore/detail/shorty/cbgcnhimnlnjejdopldfdicfingmaijg?hl=en-US)
- Lastpass password manager -
  [chrome](https://chrome.google.com/webstore/detail/lastpass-free-password-ma/hdokiejnpimakedhajhdlcegeplioahd?hl=en-US),
  [firefox](https://addons.mozilla.org/en-US/firefox/addon/lastpass-password-manager/)
- Vimium (VIM shortcuts in browsers) -
  [chrome](https://chrome.google.com/webstore/detail/vimium/dbepggeogbaibhgnhhndojpepiihcmeb),
  [firefox](https://addons.mozilla.org/en-US/firefox/addon/vimium-ff/)
- Dark Reader dark mode for browsers -
  [chrome](https://chrome.google.com/webstore/detail/dark-reader-dark/kbbbldgkhcpkmmjbjelmkjkchibeklng?hl=en),
  [firefox](https://addons.mozilla.org/en-US/firefox/addon/darkreader/)
- New tab extension (featuring unsplash images) -
  [chrome](https://chrome.google.com/webstore/detail/unsplash-instant/pejkokffkapolfffcgbmdmhdelanoaih?hl=en),
  [firefox](https://addons.mozilla.org/en-US/firefox/addon/tabliss/)
- UBlock Origin ad blocker -
  [chrome](https://chrome.google.com/webstore/detail/ublock-origin/cjpalhdlnbpafiamejdnhcphjbkeiagm?hl=en),
  [firefox](https://addons.mozilla.org/en-US/firefox/addon/ublock-origin/)
- Shortlink custom shortlinks -
  [chrome](https://chrome.google.com/webstore/detail/shortlink/apgeooocopnncglmnlngfpgggkmlcldf?hl=en-US)
- Emoji Keyboard -
  [chrome](https://chrome.google.com/webstore/detail/emoji-keyboard-by-joypixe/ipdjnhgkpapgippgcgkfcbpdpcgifncb?hl=en),
  [firefox](https://addons.mozilla.org/en-US/firefox/addon/awesome-emoji-picker/)

## IDEA theming

In order to theme JetBrains IDEA with Nord, you can simply download the "Nord" plugin from the JetBrains Marketplace.
However, I've created some changes to the default theme to make Markdown documents "pop" more and be more readable while
editing. You can download the `Nord-NazmulModifiedIDEAColorScheme.icls` file
[here]({{'assets/Nord-NazmulModifiedIDEAColorScheme.icls' | relative_url}}). You can set this color scheme by opening
Settings in IDEA and going to "Color Scheme" to import it. Here's a screenshot of this.

![]({{'assets/idea-settings-color-scheme.png' | relative_url}})

Here's a screenshot of what this theme modification does (notice the stuff highlighted in pink and blue).

![]({{'assets/idea-settings-nord-modified-by-nazmul.png' | relative_url}})

## Mouse customization

I use a Logitech MX3 Master mouse, and it works really well out of the box. One of the interesting features of this
mouse is that the button on the bottom left actually presses `Alt + Tab`. So if you press and release quickly it will
just type `Alt + Tab` and if you hold the button down then it will press and hold `Alt + Tab` 🎉. There are ways to
customize this behavior in case you don't like it. And that is where `solaar` and `piper` / `ratbag` come into play.

### Minimum customization - solaar

[Solaar](https://www.omgubuntu.co.uk/2013/12/logitech-unifying-receiver-linux-solaar) allows you to configure your
Logitec Unifying Receiver (in case you don't use Bluetooth, which I don't). You can't customize very much, but you can
tweak the DPI settings and the scroll threshold. You can install [solaar](https://github.com/pwr-Solaar/Solaar) using
`sudo apt install -y solaar`.

### Maximum customization - ratbag and piper

So if you want to
[customize all the things](https://www.linuxuprising.com/2020/11/configure-logitech-steelseries-and.html) on your mouse,
the `ratbag` is your friend, and `piper` is the GUI on top of it.

The version of [`piper`](https://github.com/libratbag/piper/) in the universal `apt` repo is quite old, so it is best to
get the latest version from the official PPA.

```bash
sudo add-apt-repository -y ppa:libratbag-piper/piper-libratbag-git
sudo apt update
sudo apt install -y piper
```

`piper` has a nice GUI that you can use to customize just about everything on your mouse.

> Note - As of Mar 2021, `ratbag` does not support adding macros to Logitech MX3 Master mouse buttons; hopefully it will
> be added in the future. This limitation prevents `piper` from assigning macros to buttons.

In case you wanted to use `ratbag` without `piper` you can use the command line to control it. `ratbag` comes
preinstalled with Ubuntu 20.04, so you won't need to install it. You can use
[`ratbagctl`](https://manpages.debian.org/experimental/ratbagd/ratbagctl.1.en.html) in your terminal to control
`ratbagd`. The documentation is sparse, and here's an
[article w/ some information](https://www.linux.org/threads/ratbag-command-macro-examples.21942/) on how to add macros.

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
to do whatever it is that you want. For me, I use [Ultimate Hacking Keyboards v1](http://uhk.io) and have my keyboard
mapped to do lots of workspace management things (like switch workspaces, switch windows between workspaces, etc) and I
use my custom key mappings for these `xdotool` commands. Here is a [my review of the UHK
v1]({{ '/2021/03/09/mechanical-keyboard-review/' | relative_url}}).
