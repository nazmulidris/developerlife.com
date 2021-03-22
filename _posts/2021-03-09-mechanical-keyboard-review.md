---
author: Nazmul Idris
date: 2021-03-09 14:00:00+00:00
excerpt: |
  Review of the Ultimate Hacking Keyboard v1, Drop Alt Captain, and Mistel BAROCCO MD770 keyboards from a 
  programmer's perspective
layout: post
title: "Mechanical keyboard review - UHK v1, Mistel BAROCCO MD770, Drop Alt Captain"
categories:
  - Linux
  - Misc
  - Productivity
  - Hardware
---

<img class="post-hero-image" src="{{ 'assets/mechanical-keyb-review.svg' | relative_url }}"/>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [The search for the best programmer's keyboard](#the-search-for-the-best-programmers-keyboard)
- [Keyboard companions - trackpad and mouse](#keyboard-companions---trackpad-and-mouse)
- [Ergonomic mechanical keyboard - UHK v1](#ergonomic-mechanical-keyboard---uhk-v1)
  - [Pros](#pros)
  - [~~Cons~~ Nits](#cons-nits)
- [Remapping keys and configuring keyboards](#remapping-keys-and-configuring-keyboards)
  - [Hierarchy of needs](#hierarchy-of-needs)
  - [Don't shoot self in foot](#dont-shoot-self-in-foot)
  - [Examples for UHK keymap](#examples-for-uhk-keymap)
    - [Cursor control](#cursor-control)
    - [GNOME workspace control (with window tiling extension)](#gnome-workspace-control-with-window-tiling-extension)
    - [IDEA and Sublime Text 3](#idea-and-sublime-text-3)
    - [Clipboard history, emoji, albert/alfred](#clipboard-history-emoji-albertalfred)
    - [Browser tab management](#browser-tab-management)
    - [Function keys](#function-keys)
    - [Gnome lockups](#gnome-lockups)
    - [Figma, LucidSpark](#figma-lucidspark)
- [Ergonomic mechanical keyboard - Mistel BAROCCO MD770](#ergonomic-mechanical-keyboard---mistel-barocco-md770)
- [Non-ergonomic mechanical keyboard - Drop Alt Captain](#non-ergonomic-mechanical-keyboard---drop-alt-captain)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## The search for the best programmer's keyboard

I type a lot, every day. And I need a keyboard that can help me take care of my hands and body, so as not to wear
anything them out, or cause needless fatigue or repetitive stress injuries.

I used to use the [Kinesis Advantage](https://kinesis-ergo.com/keyboards/advantage2-keyboard/) keyboard for almost a
decade from 2000 to 2010. After that I switched to the
[Kinesis Freestyle](https://kinesis-ergo.com/keyboards/freestyle2-keyboard/) and finally to
[Kinesis Freestyle Edge mechanical RGB backlit keyboard](https://gaming.kinesis-ergo.com/product/freestyle-edge/) after
that came out. So I've had a long history with Kinesis 😀.

All that came to an end when I embarked on the search for a more programmer friendly ergonomic keyboard. Programmer
friendly in the sense that I wanted to remap my keys to be whatever I choose, whether that means swapping keys for other
keys, or creating macros, or even working with multiple keyboard layers.

> You can find an awesome list of split keyboards [here](https://github.com/diimdeep/awesome-split-keyboards).

The first one that I tried was the [Ergodox EZ](https://ergodox-ez.com/) keyboard, which I didn't like at all. The build
quality was not that great and the keyboard layout didn't make much sense to me. And I didn't like the software to
configure the keyboard either. I liked the ergonomics of the Kinesis Freestyle Edge much better, even without the
ability to customize it much. And the build quality of the Freestyle Edge RGB was on par with the Ergodox EZ, nothing
great, but not bad either.

## Keyboard companions - trackpad and mouse

Before getting into the keyboard reviews, I wanted to cover the other input devices I use with them. I have two input
devices that I use with these keyboards.

1. [Logitech MX3 Master](https://www.logitech.com/en-us/products/mice/mx-master-3.910-005620.html) - This is the best
   mouse that I have ever used. Everything about it is amazing. Sadly on Linux customization options are limited, but
   you can do a lot on Windows or macOS w/ customizing the mouse itself.
2. [Apple Magic Trackpad 2](https://www.apple.com/shop/product/MJ2R2LL/A/magic-trackpad-2-silver) - Since the UHK has a
   big gap in the middle, I usually have a trackpad there so that I don't have to reach for the mouse to for scrolling a
   page or some small movements to click on a UI element on screen. When using drawing apps, then I definitely use the
   mouse. But this can be cumbersome for mundane operations like clicking on buttons in IDEA dialog boxes, or just
   browser operation (I try to use [Vimium](https://vimium.github.io/) to minimize mouse / trackpad interaction in
   general). You might also try this
   [trackpad](https://www.amazon.com/gp/product/B07PGFHJDY/ref=ox_sc_saved_title_1?smid=A3VVLG7OTU8AIK&psc=1).

## Ergonomic mechanical keyboard - UHK v1

Then I found out about the [Ultimate Hacking Keyboard](https://ultimatehackingkeyboard.com/). I thought that was quite a
claim in the name when I first heard of it. So I ordered my first one with very high expectations. I ordered it with the
MX Brown switches and the fantastic wrist wrests (made out of solid wood). And I am happy to report that the name
accurately matches the product and my expectations where blown away! I am a fan for life!

Then I ordered another one, with the ISO keyboard layout instead of the US 😀.

Then I pre-ordered the UHK v2 RGB keyboard, and am now impatiently waiting for the keyboard to come out, along with the
modules. As soon as that happens (expected to start shipping in March 2021) I will be sure to post a new review (of v2
and the new modules).

### Pros

Where to begin about all that is right with this keyboard. Just about everything. The build quality is outstanding! I
ordered the wooden palm rests, which are not only solid and heavy, but look and feel great. Everything about this
keyboard exudes craftsmanship and quality. There is no planned obsolescence to be found anywhere in this keyboard.

Not only is the physical keyboard itself magnificent, but the
[UHK Agent](https://github.com/UltimateHackingKeyboard/agent) software that you use to program it is just fantastic! It
has a really easy to use and powerful UI. The electron based app also supports Dark Theme 😀. It is just painless to
use, and makes it a joy to reprogram the keyboard to whatever you desire. And you can do firmware updates with ease. And
it works on any platform.

Here's an example of how amazing Agent and the UHK are. The Support staff at UHK are awesome as well, and they helped me
to figure this out! By default if you double tap the Fn or Mod keys, they lock. And you are in that layer until you
unlock (by pressing the key that got you into that layer in the first place). This can be really annoying when
accidentally double pressing these layer keys. Agent simply allows you to change this behavior in the following ways:

1. You can simply tell Agent to disable the Mod key from sticking if you double press it.
2. You can also tell Agent to toggle everytime you press.

So you can make it to whatever you like! Here's a video to illustrate the awesomeness that is UHK and Agent!

![]({{ 'assets/uhk-agent-mod-key-sticking.gif' | relative_url }})

### ~~Cons~~ Nits

I only have nits against this keyboard. Not really cons. The first is that I really miss not having dedicated cursor
keys and a row of Page Up, Page Down, Home, and End keys. Yes, I know that you can simply map these keys to another
layer like Fn or Mod, or just other individual keys (both of which I have done) but these keys are so frequently used in
GNOME that it would make sense to have them as dedicated keys. UHK makes modules and they have a module that adds a few
keys (that I have on order) which I hope will address this shortcoming.

## Remapping keys and configuring keyboards

The UHK is so configurable that outside of being happy with the build quality, I really had to think through how I was
going to customize the keyboard to suit my programming needs. I did ask for the ultimately configurable keyboard, and I
did get just that 😀. Now it is on me to devise strategies to enhance my productivity using this keyboard.

### Hierarchy of needs

So I broke it down into a few major categories, which are either just individual apps that I use or just tasks that can
be clumped together. And this is what I came up with (the most important stuff is on top):

1. Coding
   - JetBrains IDEA based IDEs
   - Sublime Text 3
2. System level things
   - Terminal (Tilix)
   - Albert
   - CopyQ
   - GNOME workspace control
   - GNOME tiling window extension control
   - Browsers (tab management)
3. App specific
   - Figma
   - Google Sheets

### Don't shoot self in foot

Some historical context is in order. I used to code on laptops, and Kinesis keyboards on desktops, and neither are
really programmable. So in order to keep from using the cursor key cluster (Up, Down, Left, Right) on the bottom right
of the keyboard, I had developed my own crazy shortcuts in Sublime Text and IDEA so that I would not have to move my
hands when I wanted to navigate around in code, UIs, etc.

Also I had to accommodate using macOS as well as Linux, and macOS is terrible about keyboard customization (I still
don't understand how Meta, Ctrl, Alt don't always work). This led to some gnarly key combinations (like `Alt + ;` for
left, and `Alt + '` for right, etc). This also required some heavy customizations to both products, which was very time
consuming and difficult to keep in sync (between apps and across OSes).

After I got the UHK, I have systematically removed these "overly complex" and "custom" workarounds and replaced them w/
the defaults, along with moving any major customizations into the UHK itself. And I just accept that there are limits to
typing using a Drop Alt keyboard or a laptop keyboard, and don't use them for heavy editing sessions. They are mostly
for reading and research type tasks.

These are the insights that I gained to making this work effectively and simply using IDEA and Sublime Text as examples.

- Don't create UHK keymaps for keys that you don't really need. Eg: there's no need to make a keymap for `Ctrl + Y` in
  IDEA.
- Keep the keyboard shortcuts as close to the defaults as possible. Eg: there is no need to change what `Ctrl + Down`
  does in either Sublime or IDEA.
- If not then, pick a shortcut (and add it to IDEA and Sublime) that is consistent between the two apps. Here are some
  examples:
  1. Add `Ctrl + Shift + P` in IDEA to open Settings (this is a Sublime shortcut that is created for IDEA).
  2. Cloning the caret, and clone selection in both IDEA and Sublime mapped to `Ctrl + J` and `Alt + J` respectively.
  3. Expand selection is `Ctrl + W` in both.
- When modifying IDEA keymaps, and Sublime Text key bindings, make sure that each action works well with other modifier
  keys. A great example in IDEA is `Ctrl + Down`, and its usage with `Shift`, `Alt`, and `Shift + Alt`, etc.

By following these steps first, there are 2 advantages:

1. The UHK mapping can be minimal, so it makes it easy to use UHK Agent to create these in the first place, and to have
   multiple keymaps for various OSes (you can have a macOS specific keymap, Linux specific one, and Windows specific
   one).
2. These mappings will just work on other keyboards (eg: Drop Alt series).

### Examples for UHK keymap

You can download these keymaps here.

1. [UHK settings exported json file]({{ 'assets/NAZ-UHK.json' | relative_url }})
2. [IDEA keymap.jar file]({{ 'assets/keymap.jar' | relative_url }})
3. [Sublime Text keybindings.json file]({{ 'assets/sublime-text-keymap.json' | relative_url }})

#### Cursor control

- Cursor keys are on bottom right of keyboard: Fn, Alt, Super, Ctrl
  - RightCtrl : Right
  - RightSuper : Left
  - RightFn : Up
  - RightAlt: Down
- Mod + J : left
- Mod + K : down
- Mod + L : right
- Mod + I : up
- Mod + H : home
- Mod + ; : end
- Mod + O : page up
- Mod + P : page down
- Mod + Del : backspace
- Mod + H : Home
- Mod + J : End
- HiddenKeyLeft : Left
- HiddenKeyRight : right

#### GNOME workspace control (with window tiling extension)

- Super + Up / Down : Move workspace prev and next
  - Add Shift to move a window to the prev or next workspace
- Mod + Tab : Super + J (works w/ GNOME window tiling extension)
  - Add Shift and you can actually move the windows rather than switch focus!
- Mod + 1 / Mod + -: Move workspace prev
  - Simply types Super + Up
  - Add Shift to a move a window to prev workspace
- Mod + 2 / Mod + +: move workspace next
  - Simply types Super + Down
  - Add Shift to a move a window to next workspace

#### IDEA and Sublime Text 3

- RightShift : Super
- Mod + Space : code complete (Ctrl+Space)
- Mod + B : code navigation (go to declaration, jump to source)
  - Maps to Ctrl + Down, which works in both IDEA and Sublime.
  - Shift+Mod + B : code navigation (go to implementation in IDEA)
- Mod + U : code navigation (back)
  - Maps to Ctrl + Up, which works in both IDEA and Sublime.
- Mod + Y : show structure
  - In IDEA this maps to Ctrl + Y
  - In Sublime Text this maps to Ctrl + R
- Alt + left, Alt + right : tab navigation (move tab to next / prev)
- Mod + HiddenKeyLeft, Mod + HiddenKeyRight : tab navigation (switch to tab next / prev)
- Mod + <, Mod + > : move current tab to the left / right
- Ctrl+Shift + P : Settings...
- Mod + F : find usages in files
- Mod + R : run config
- Mod + D, Mod + S : shift + shift
- Mod + H : Home
- Mod + N : End
- Mod + Esc : Reformat code
- Fn + Esc : Optimize imports

#### Clipboard history, emoji, albert/alfred

- Fn + Mod : Albert
- Mod + Fn : CopyQ
- Fn + Space : emoji picker
- Mod + C : copy
- Mod + V : paste
- Mod + X : delete line (cut)
- Mod + Z : undo
- Mod + Enter : Cmd + enter (Mac), Ctrl + enter (Linux)

#### Browser tab management

- Mod + HiddenKeyLeft, Mod + HiddenKeyRight : switch to next / prev tab
  - These simply type `Ctrl + Tab` and `Ctrl + Shift + Tab` respectively
  - [gnome issue fix for terminal](https://askubuntu.com/a/875482/872482)
- Fn + HiddenKeyLeft, Mod + HiddenKeyRight : move current tab to next / prev
  - These simply type `Ctrl + Shift + Page Up` and `Ctrl + Shift + Page Down`

#### Function keys

- Fn + ~ : toggle between MAC and LIN keymaps
- Fn + 1-0, -, + : F1 - F12
- Fn + Del : Insert

#### Gnome lockups

- Fn + Esc : Run the macro `gnome-safe-reboot`, which types "Alt + SysRq", then types "REISUB"

#### Figma, LucidSpark

- Fn + Esc : Space (While Space is pressed, dragging the mouse allows panning to happen in many graphical apps)

## Ergonomic mechanical keyboard - Mistel BAROCCO MD770

My review of this keyboard is very short compared to the UHK v1 😀. The
[Mistel BAROCCO MD770](https://www.mistelkeyboard.com/products/d11cf7a73da49468e2a530b4cf18e76c) has some similarities
to the UHK - it is a split ergonomic keyboard with mechanical switches. And it has major differences - it is a 75%
layout keyboard when compared to the UHK's 60%, and it has RGB lighting, but is is not really very configurable.

The build quality is excellent. I ordered one w/ the MX Brown keys, and they feel great to type on. I think for the
money this is the highest quality keyboard at its price point. Even though the chassis is light, nothing rattles or is
loose. It actually feels like a much heavier and solid construction keyboard.

The connector is USB-C which is great. Just like the Drop Alt Captain, it has a convenient USB-C port on the keyboard
itself which makes it great to add another peripheral to (Bluetooth mouse dongle) or a YubiKey.

The customization ability of this keyboard is extremely limited and is similar to a Kinesis Freestyle. You can't change
any key maps in the default layer, but you can press a sequence of keys on the keyboard to map one key to another in
various layers. This nothing like UHK's Agent, or even the QMK software used by Drop Alt Captain.

The backlight is very weak. It is just not very good. I almost wish it didn't come with this feature. The Drop Alt
Captain wins hands down in a light show competition! However this keyboard is roughly half the price of the Captain.

## Non-ergonomic mechanical keyboard - Drop Alt Captain

This is also a very short review compared to the UHK v1. The
[Drop Alt Captain](https://drop.com/buy/drop-signature-series-captain-keyboard) is a totally different category of
product when compared to the UHK.

The Captain keyboard has phenomenal build quality, it weighs in at almost 3 lbs! It has amazing RGB lighting. It looks
like art more than it does a utilitarian device. The keys feel amazing to type on.

The connector is USB-C which is great. And it has a convenient USB-C port on the keyboard itself which makes it great to
add another peripheral to (Bluetooth mouse dongle) or a YubiKey.

The [customization](https://drop.com/talk/10343/how-to-configure-your-alt-keyboard) is limited, since it uses the QMK
software to configure keyboard shortcuts and then flash them on to the keyboard. This software is nowhere near as easy
to use as the UHK Agent. Nor is it anywhere nearly as powerful.

It is not an ergonomic keyboard which for me means that I don't really type on it for any extended period of time. It is
more of a toy or a keyboard for a machine that I might use occasionally or even to have as a backup keyboard.
