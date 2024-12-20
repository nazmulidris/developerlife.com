---
author: Nazmul Idris
date: 2021-03-09 14:00:00+00:00
excerpt: |
  Linux laptop and desktop for software engineers hardware review - Dell Precision 3440 2020, Dell XPS 13 Developer
  Edition 2021, ThinkPad P15, ThinkPad X1 Carbon Gen 8
layout: post
title: "Linux (Ubuntu) desktop and laptop hardware review for software engineers (early 2021)"
categories:
  - Linux
  - Misc
  - Productivity
  - Hardware
---

<img class="post-hero-image" src="{{ 'assets/ubuntu-hw-review.svg' | relative_url }}"/>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [From Windows, to macOS, to Ubuntu (Linux)](#from-windows-to-macos-to-ubuntu-linux)
- [Waiting for desktop Linux to mature (which happened in late 2020)](#waiting-for-desktop-linux-to-mature-which-happened-in-late-2020)
- [Dell Precision 3440 small form factor workstation](#dell-precision-3440-small-form-factor-workstation)
  - [Pros](#pros)
  - [Cons](#cons)
- [Dell XPS 13 Developer Edition (2021 w/ Tigerlake 11th gen CPU and Intel Xe integrated graphics)](#dell-xps-13-developer-edition-2021-w-tigerlake-11th-gen-cpu-and-intel-xe-integrated-graphics)
- [ThinkPad P15 Gen 1](#thinkpad-p15-gen-1)
  - [Pros](#pros-1)
  - [Cons](#cons-1)
  - [Some tweaks that I had to make for Ubuntu 20.04](#some-tweaks-that-i-had-to-make-for-ubuntu-2004)
- [ThinkPad X1 Carbon Gen 8](#thinkpad-x1-carbon-gen-8)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## From Windows, to macOS, to Ubuntu (Linux)

Before getting to the the desktop and laptop hardware reviews, I would like to share my journey of
how I arrived here. I became a big fan of Ubuntu and GNOME in the last few years, and I recently
switched to using Ubuntu full time as my laptop and desktop environment for both work and personal
use cases.

Prior to that I was using Linux and macOS in my day job and macOS for my personal computing
environment. Like many developers, I really enjoyed the incredible vertical integration of macOS
software and Apple hardware, and loved that macOS is a BSD based operating system and has a "real"
terminal. And before that I primarily used Windows in the 90s, before switching to macOS X in early
2000's.

However, I've been looking to switch to Linux for the last 2-3 years (2017-2019) ever since:

1. Overheating issues on MacBook Pro laptops became so bad that these machines weren't really usable
   for any sustained workloads. And there had been a dearth of desktop computing options for macOS.
2. macOS is getting more and more locked down (it biases apps to be deployed via the Apple App
   Store, and
   [Catalina started the "notarization" requirement](https://www.macrumors.com/2019/12/23/apple-mac-app-notarization-february-2020/)
   for apps that are not delivered via the App Store) restricts choice for me as a developer and
   user.

## Waiting for desktop Linux to mature (which happened in late 2020)

I've been waiting for desktop Linux to mature so that I could switch to it full time. And that time
happened for me at the end of 2020. It was incredible to see this
[Lenovo announcement](https://news.lenovo.com/pressroom/press-releases/lenovo-brings-linux-certification-to-ThinkPad-and-thinkstation-workstation-portfolio-easing-deployment-for-developers-data-scientists/)
in support of Linux. And [Dell](http://dell.com/linux) had already thrown their weight behind Linux
even before that! And of course [System76](https://system76.com/) even before that. What is
incredible about Lenovo and ThinkPads is that there is no need to deal with adding custom PPAs to
get hardware drivers (this isn't the case for Dell or System76)!

Between 2017 and 2020, I purchased various Dell laptops, System76 laptops and desktops, and even
ThinkPad X series laptops to try Ubuntu on them. And overall they had some issue or another.

- The Dell laptops worked really well (XPS and Precision Mobile line of mobile workstations). The
  only exceptions is that I ordered an XPS 15 laptop w/ OLED panels, and they were simply not
  supported. But with non OLED panels, Linux worked pretty well.
- The ThinkPad X1 Extreme machine that I ordered was too "new", and I had all kinds of kernel issues
  and lack of support for the WiFi card. And even after getting that to work, the power management
  was not good at all leading to some awful battery life and performance issues.
- The System76 laptops that I got were nothing "special" in terms of hardware (the
  [open firmware](https://github.com/system76/firmware-open) on them is special and awesome). These
  laptops are currently just rebranded [Clevo](https://en.wikipedia.org/wiki/Clevo) machines (a
  Taiwanese OEM). I am personally waiting for System76 to create their own custom laptops just like
  they do their Thelio desktop. I am also very impressed that they have open sourced their
  mechanical keyboard hardware design (called [`launch`](https://github.com/system76/launch)) as
  well recently!

In 2020, I was really impressed w/ the System76 Thelio desktop, and ended up ordering one as well,
but returned it in favor of the Dell Precision 3440 that I currently have. I am deeply impressed by
AMD Ryzen on Thelio as well as PCI Express 4.0 (w/ 7Gbps read and 5Gbps write speeds for SSDs). My
next desktop is going to be a Thelio 😀. And this leads us to the hardware reviews 🎉.

## Dell Precision 3440 small form factor workstation

The
[Dell Precision 3440](https://www.dell.com/en-us/work/shop/cty/pdp/spd/precision-3440-workstation/xctop3440us_vivp?configurationid=c460c7e5-e696-4ad5-ade0-ab0cad0c87e9)
is a very small computer. It packs a lot of punch though. This machine came out just at the end
of 2020. And it featured an upgraded Xeon CPU line w/ more cores (10 core). I didn't know this at
the time, but this is a big change for this enterprise class machine in many years.

The spec that I ordered was w/ the Xeon W-1290 (10 Core), 64GB of non-ECC RAM, 512GB SSD, and NVIDIA
Quadro P1000 4GB GPU. If I were to to do it over again, I would get a CPU w/ fewer cores, since my
workloads can't be parallelized much (lots of mostly single threaded tasks, or slightly
multi-threaded tasks). Actually if I were to do it over again, I would get a
[System76 Thelio](https://system76.com/desktops/thelio-r2/configure) machine w/ PCEe 4.0 and the AMD
4th Gen Ryzen 7 5800X CPU, with the double speed SSDs (7GB/s read, and 5GB/s read). The System76
comes w/ Ubuntu 20.04 or PopOS! 20.04, whereas the Dell only ships w/ Ubuntu 18.04.

### Pros

- The machine is incredibly small, packs a big punch, is incredibly fast, and can handle just about
  anything I can throw at it which includes Google Chrome, JetBrains IntelliJ IDEA, gradle, npm,
  webpack, Java and Kotlin toolchain, Ruby, TS and JS (browser and node environments).
- The IO is incredibly fast on this machine, and it can handle most compilation tasks w/ ease. I
  even installed [`pigz`](https://zlib.net/pigz/) on this box to make better use of the abundant
  cores to do file compression and expansion.
- Thermal management is excellent. Even over sustained workloads. However, when the fan does kick
  in, it is very loud! Sounds like a plane about to take off.
- To compile the
  [JetBrains IntelliJ Community Edition](https://github.com/JetBrains/intellij-community) IDE took
  about 6 minutes on this machine. I used Amazon `corretto-11` JDK, and applied the parallel
  compiler optimization settings in the README. To give you some context, it takes about 22 minutes
  to build the same project on a top of the line 2020 MacBook Pro 16" laptop (w/ i9 CPU and 32 GB of
  RAM) ... this is with a case sensitive filesystem enabled! It is even slower when using the
  default APFS case insensitive filesystem!
  [EXTFS4](https://manpages.ubuntu.com/manpages/bionic/man5/filesystems.5.html) is fast!
- The build in SSD is as advertised. It gets roughly 3.2GB/s read and 2.9GB/s write. I was able to
  improve the performance slightly (by about 12% for read and write) by using the new generation SSD
  from Samsung (which is made for PCI Express 4.0 systems)
  [980 PRO](https://www.amazon.com/gp/product/B08GL575DB/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1).
  The average access times were much better w/ the new 980 PRO as well (0.02 ms vs 0.42 ms). So it
  is worth the upgrade 👍.

### Cons

- It does not support PCI Express 4.0, and the System76 Thelio has a big edge over this machine in
  terms of disk IO.
- Dell has installed Ubuntu 18.04 on this machine, which is getting long in the tooth now.
- Even though the case is a tool-less design, because the chassis is so tiny, it does require you to
  remove lots of stuff inside of it in order to get to memory and SSD. So if you want to add the 980
  PRO SSD you have to remove the empty drive bays just to get to the single SSD slot.
- The built in Bluetooth chip is not good. I had to use an external USB Bluetooth dongle from
  Plugable that I purchased from
  [amazon](https://www.amazon.com/gp/product/B009ZIILLI/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1).
- If you don't like really loud fan noises, then this machine might not be the one to get. Puget
  Systems makes a really quiet Linux workstation called
  [Serenity](https://www.pugetsystems.com/nav/serenity/Professional/customize.php) that you can take
  a look at if sound deadening is important to you.
- Dell offers an image with all the drivers installed. The only issue w/ this image is that if you
  choose to use full disk encryption using
  [LUKS](https://en.wikipedia.org/wiki/Linux_Unified_Key_Setup) then you will have to add the
  drivers manually (which is a pain). Also to figure out which drivers to install manually, you have
  to dig around the `/etc/apt/sources.list.d` and then use something like
  [Synaptic package manager](https://itsfoss.com/synaptic-package-manager/) to figure out which
  `apt` packages are event installed from these [PPAs](https://itsfoss.com/ppa-guide/). This is an
  area where the ThinkPad putting all the required drivers in the official `apt` repositories is
  really a great advantage.

## Dell XPS 13 Developer Edition (2021 w/ Tigerlake 11th gen CPU and Intel Xe integrated graphics)

I ordered this machine in Dec 2020 and waited almost a month for it to arrive. Dell offers this
machine in pretty much just one spec. You can only choose the display and SSD options. I wasn't sure
if an ultra portable machine would be enough for my workflow. And boy was I surprised!

This Tigerlake 11th gen CPU architecture from Intel w/ the integrated Xe graphics are out of this
world! Thermal management is epic! This machine can run at high clock speeds for a long period of
time and not give in to weak thermals. Even under heavy workloads, this machine doesn't get very
hot, and when it does get warm, you can barely hear the fan kicking in. This is an awesome machine
and I wholeheartedly recommend it to anyone!

Build quality is excellent. It feels like a premium product. It feels like a passion project from
folks at Dell who worked on this machine! The laptop is featherweight as well! Battery life is great
too.

It also comes with Ubuntu 20.04 out of the box, which is great. The display is one of the best I've
ever seen in any laptop. The keyboard is ok. Not the best, but not the worst. And the touchpad is
decent as well. I connected this to a Thunderbolt dock and it just works flawlessly with external
drives, keyboards, mice, and monitors. I can't think of any big knocks against this machine. It is
near perfect. If you want an awesome tightly vertically integrated product that just works
flawlessly, then this is the machine for you!

The only con that I can think of is the one that applies to the Precision as well, which is related
to the use of custom PPAs to deliver hardware drivers. And the inability to use LUKS full disk
encryption from the factory OS image (which is what the recovery media will install).

In terms of my benchmarks, to compile the
[JetBrains IntelliJ Community Edition](https://github.com/JetBrains/intellij-community) IDE took
about 16 minutes on this machine. I used Amazon `corretto-11` JDK, and applied the parallel compiler
optimization settings in the README.

This machine is only 2.7 x slower than the Dell Precision above to compile IDEA. And it is faster
than the MacBook Pro 16 2020 (which takes about 22 minutes).

SSD speeds are great as well, and are as advertised, roughly 3.5GB/s read, and 3.1GB/s write.
Average access times are in the order of 0.02 ms.

## ThinkPad P15 Gen 1

This machine is my favorite mobile workstation of all time. It is a very thick 15" laptop, that fits
in bags that can hold a 16" MacBook Pro. It ships with Ubuntu 20.04 out of the box 🎉. It is a
perfectly capable desktop replacement with incredible thermal management and just raw power. I have
no idea what the battery life is like, but I imagine it can't be very good 😀. I just use it as a
mobile workstation replacement docked to an external monitor, [UHK v1
keyboard]({{ '2021/03/09/mechanical-keyboard-review/' | relative_url }}), trackpad, and mouse.

Let's talk performance. This machine is fast. And it is quiet (my spec anyway). I ordered the P15
with a i7-10750H CPU (6 core, 12 threads), and the Nvidia Quadro P1000 GPU w/ 4GB RAM, with 32GB of
RAM and 1TB SSD. Everything on the machine feels lightning quick. It feels very much like the Dell
Precision desktop, but even snappier, thanks to Ubuntu 20.04 vs 18.04. Also, ThinkPads don't use any
proprietary PPAs for driver installation that is needed for hardware support (you can get it via
`apt`). This makes it a breeze to install Ubuntu on this machine! Just pick a distro, but the ISO to
a USB drive, boot from it, and install.

Here are my performance benchmarks, to compile the
[JetBrains IntelliJ Community Edition](https://github.com/JetBrains/intellij-community) IDE took
about 8.5 minutes on this machine. I used Amazon `corretto-11` JDK, and applied the parallel
compiler optimization settings in the README. This machine is only 30% slower than the Dell
Precision desktop! That is crazy fast! This is not even close to the maximum spec of this machine. I
can imagine if you got the Xeon CPUs w/ more RAM you will definitely get more performance than this.
However, this is enough for my needs.

I picked the slower CPU w/ fewer cores since my workloads aren't really optimized for massive
parallelization. And this machine keeps this CPU running fast at high clock speed under load! I
don't see it drop below 3.6-4GHz when I am really pushing this machine for long periods of time. The
fan sound is super quiet under load as well. I love effective thermal management. The P15 pushes the
CPU as hard as it can as quickly as it can, and just holds it at the highest clock speed that it can
for the longest amount of time that it can. Big win for effective thermal management on this
machine. You can also set the performance profiles in the BIOS (one for when external power is
attached and another for when the machine is on battery power). You can even disable the internal
battery in BIOS 😀.

SSD speeds are great as well, and are as advertised, roughly 3.3GB/s read, and 3.1GB/s write.
Average access times are in the order of 0.02 ms. I wish this machine had PCI Express 4.0 and a
newer generation of SSD w/ 7GB/s read and 5GB/s write 😀. But it does have Thunderbolt 3, which is
great if you have a Thunderbolt dock and Thunderbolt SSD enclosures. I like the Dell XPS 13 for its
Thunderbolt 3 support as well.

### Pros

- The build quality is excellent - this thing is built like a tank with all its ThinkPad ruggedness.
  It feels like a premium device.
- It has plenty of ports - dedicated Ethernet port, 3 Thunderbolt ports, 2 USB-A ports, and more.
- The keyboard and trackpad are great.
- I got the 4k OLED panel, which is really vibrant and bright.
- Amazing performance, incredibly effective thermal management, and fans are really quiet!

### Cons

- The keyboard has a dedicated numeric keypad - this might actually be a plus for some folks.
- I wish the screen had smaller bezels like the Dell XPS 13/15/17. So much usable space is taken up
  by these large bezels and it is just not space efficient. I like the aspect ratio of the Dell XPS
  13/15/17 (16:10, which is a "more tall and less wide" display) better than the widescreen aspect
  ratio of the P15 (16:9).
- The OLED panel is actually touchscreen, which I find pointless. Also the quality of the screen
  isn't as good as the Ultrasharp panels found in Dell XPS 13/15/17.
- It is very heavy! It is about 6 lbs and that's without the charger (which is large, but slim, and
  heavy).

### Some tweaks that I had to make for Ubuntu 20.04

1. Out of the box, the recovery media sets a partition size of only 64GB for the main SSD. This is
   very strange. I had to live boot into the recovery media (on a USB drive) and then increase the
   partition size to 1TB
   [using GParted](https://www.howtogeek.com/114503/how-to-resize-your-ubuntu-partitions/). Also you
   can't use full disk encryption using LVM without nuking the installation which is a shame.
2. I had to change a few BIOS settings because the machine was not using my external monitor
   (connected via Thunderbolt) when it was booting. When the machine boots, press Enter or F1, and
   it will take you to the BIOS settings. There you can tell it use Discrete Graphics when it boots,
   and to activate the external display port of your choice (Thunderbolt, HDMI, etc). When you
   enable Discrete Graphics, the P15 will use the Nvidia GPU and be able to use externally connected
   displays right away, otherwise, the internal graphics do not support the use of these external
   monitors, without first switching to discrete graphics.
3. The last issue I had to work around was a bit weird. I use this machine with the lid closed, as a
   desktop replacement. So when I power it up, the lid is closed. With the fix above, I was able to
   see the "Lenovo" boot screen, which is great. Then as soon as I would login, the computer would
   immediately go to sleep! Since the lid was closed, it thought that it should go to sleep as soon
   as login occurred! This apparently is the default behavior in Ubuntu 20.04. And it is
   [easy to change](https://itsubuntu.com/configure-lid-close-behavior-of-your-laptop-with-ubuntu-20-04-lts/)
   😀. Here are the changes I made to `/etc/systemd/logind.conf`.
   ```properties
   HandleLidSwitch=suspend
   HandleLidSwitchExternalPower=ignore
   HandleLidSwitchDocked=ignore
   ```

## ThinkPad X1 Carbon Gen 8

I ordered this machine at the same time that I ordered the Dell XPS 13 Developer Edition. This X1
Carbon Gen 8 machine works flawlessly with Ubuntu. You can get it from the factory with Ubuntu
preinstall. The only change you have to make to run this on Windows or Linux is one setting in the
BIOS (regarding the sleep state of the CPU). There are no custom PPAs for driver software. So you
can just boot from a Linux Live CD (ISO) and you can install Ubuntu 20.04 and you are good to go!
Everything (keyboard functions like screen brightness control, volume, and media control,
sleep/resume, etc) just works!

The build quality is excellent. This thing is light. I love carbon fiber construction! Battery life
is great. Keyboard and touchpad are great. Screen is great. Thermal management is great, however it
runs way hotter than the XPS 13 (which is on Intel's 11th gen CPU vs this one's 10th gen one).

There is one major flaw this machine has. It is slow. Like really slow. Even the system UI feels
sluggish compared to the Dell XPS 13.

In terms of my benchmarks, to compile the
[JetBrains IntelliJ Community Edition](https://github.com/JetBrains/intellij-community) IDE took
about 48 minutes on this machine. I used Amazon `corretto-11` JDK, and applied the parallel compiler
optimization settings in the README. This machine is 8 x slower than the Dell Precision above to
compile IDEA. And it is 3 x slower than the Dell XPS 13!

Disk IO is as advertised. It got 3.1GB/s read, 2.4GB/s write, and 0.20 ms average access time. So
even the IO is slower than the Dell XPS 13 and Precision.

I returned this laptop and kept the Dell XPS 13 👍.
