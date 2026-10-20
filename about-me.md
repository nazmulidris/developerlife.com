---
layout: page
author: Nazmul Idris
date: 2016-10-02 17:17:23+00:00
excerpt: About Nazmul Idris
title: Nazmul Idris
exclude: false
---

<div class="avatar-container category">
    <div class="avatar-top-row">
        <div class="avatar-icon">
            <img src="{{ '/assets/nazmul.png' | relative_url }}"/>
        </div>
        <div class="avatar-text">
            Hi, I'm <a href="https://duckduckgo.com/?q=nazmul+idris&ia=web">
            Naz</a> 😃. I am a <strong>Rustacean 🦀 Systems Engineering Leader &amp; Founder</strong>
            building next-generation terminal platforms and developer tooling for the AI &amp; cloud era.
            Also an ex-Googler (Android Studio IDE Platform),
            <a href="https://github.com/r3bl-org/r3bl-open-core/" target="_blank">founder, engineer, maintainer</a>,
            designer, leader, HsingI-er, racer, storyteller.
            I 💓 leadership, authenticity, play, and hope. I build high-performance systems
            infrastructure and lead teams that ship production systems.
        </div>
    </div>
    <div class="avatar-bottom-row">
        {%- include post_title_social.html -%}
    </div>
</div>

<div style="padding-bottom:16pt;"></div>

<img class="post-hero-image" src="{{ 'assets/naz-coffee-hero.png' | relative_url }}"/>

## My story

I move fluidly between technical depth and strategic leadership. I am equally comfortable
architecting low-latency systems, writing production code, defining vision, and building
cultures of engineering excellence.

I am equal parts: engineer, management, and product person; both hands-on and in
leadership. I move fluidly between the realms of desktop, web, mobile, cloud,
infrastructure, server, client.

I've brought products to life from a glimmer of a vision to a team building it, to having
customers, and eventually seeing the product come to an end. I've worked as part of large
and small teams and led them to make impossible things possible.

I have over 30 years of work experience in the tech sector, spanning hands-on software
engineering across the entire 30 years alongside 10+ years in founder, executive, design,
and product leadership roles.

As a multifaceted entrepreneur, leader, engineer, designer, and communicator, I've focused
on creating, designing, building, and collaborating with people to bring amazing user
experiences to life across multiple platforms.

## What I'm Building at R3BL

I'm a **Rustacean 🦀 Systems Engineering Leader** building high-performance infrastructure
and leading teams that ship production systems.

### Building Terminal Platforms & Developer Tools for the AI & Cloud Era ([R3BL](https://r3bl.com) & [ROC](https://github.com/r3bl-org/r3bl-open-core))

```
██████╗  ██████╗  ██████╗
██╔══██╗██╔═══██╗██╔════╝
██████╔╝██║   ██║██║
██╔══██╗██║   ██║██║
██║  ██║╚██████╔╝╚██████╗
╚═╝  ╚═╝ ╚═════╝  ╚═════╝
```

I'm the founder, principal systems engineer, and maintainer of
**[R3BL](https://r3bl.com)** and
**[R3BL Open Core / ROC (`r3bl-open-core`)](https://github.com/r3bl-org/r3bl-open-core)**.

#### Reimagining the Terminal for AI & Cloud Workflows

With the rapid rise of autonomous AI coding agents (Claude Code, Gemini CLI, LLM
harnesses) and remote cloud VM administration over SSH, the **terminal has become the
primary command center** for modern developers. Yet terminal UX and foundational
primitives have largely stagnated since the 1990s.

Over the past **5+ years**, we've been building, and still are,
**[`ROC` (`r3bl-open-core`)](https://github.com/r3bl-org/r3bl-open-core)** from the ground
up in Rust (**2.7M+ downloads** on [crates.io](https://crates.io/users/nazmulidris)) to
bridge this gap. Available today, `ROC` provides a strictly type-safe,
correctness-focused async TUI engine (with a custom CSS/Flexbox layout engine, custom
rendering engine, and a full-featured Markdown editor component with custom Markdown
parsing and syntax highlighting), headless virtual terminal emulation (VTE), low-latency
PTY/TTY runtime, interactive CLI/TUI apps (`edi`, `giti`), AI MCP servers, and
IDE/browser extensions required to modernize terminal interaction.

Built on top of this battle-tested open-source foundation, we're building an upcoming
**closed-source suite of terminal-native apps** at **[r3bl.com](https://r3bl.com)** (that
all work seamlessly over SSH). Products like **local-first** collaborative *"Google Docs
meets Jupyter notebooks"* for Markdown and virtual terminal multiplexers. All focused on
**data sovereignty, privacy, and local-first computing**, while enhancing developer
productivity, knowledge capture & sharing, and workflow management.

#### Architecture, Platform & Ecosystem

Built from the ground up in Rust (**2.7M+ downloads** on
[crates.io](https://crates.io/users/nazmulidris)), our ecosystem spans open-source
foundational infrastructure and upcoming closed-source products:

- **R3BL Open Core / ROC — Async TUI Engine & VTE Primitives
  ([`r3bl_tui`](https://crates.io/crates/r3bl_tui) — Open Source):** Consolidates our
  strictly type-safe, correctness-focused TUI engine (custom CSS/Flexbox layout engine,
  custom rendering engine, Elm-style unidirectional state management, React/JSX-style
  declarative macros, and a full-featured Markdown editor component with custom Markdown
  parser and syntax highlighting), async readline, and headless virtual terminal emulation
  (VTE) / PTY virtualization backed by a low-latency, thread-safe runtime in Rust.
- **Interactive CLI & TUI Apps ([`r3bl-cmdr`](https://crates.io/crates/r3bl-cmdr) — Open
  Source):** Terminal Markdown editor (`edi`) powered by `r3bl_tui`'s Markdown editor
  component, and interactive Git workflows (`giti`) for branch management and staging.
- **AI & MCP Servers
  ([`r3bl-rust-analyzer-mcp-server`](https://crates.io/crates/r3bl-rust-analyzer-mcp-server)
  — Open Source):** High-performance Model Context Protocol (MCP) servers and tools for
  LLMs to orchestrate in their agentic harnesses, bridging AI coding agents directly with
  local language servers and toolchains.
- **IDE & Browser Extensions (Open Source):** Suite of
  [VS Code](https://marketplace.visualstudio.com/publishers/R3BL) and
  [Open VSX](https://open-vsx.org/namespace/R3BL) extensions for Rust development,
  semantic highlighting, and task spaces, alongside the R3BL Shortlink browser extension
  ([Chrome](https://chrome.google.com/webstore/detail/r3bl-shortlink/ffhfkgcfbjoadmhdmdcmigopbfkddial)
  and [Firefox](https://addons.mozilla.org/en-US/firefox/addon/r3bl-shortlink/)).
- **Upcoming Local-First Product Suite ([`r3bl.com`](https://r3bl.com) — Closed Source):**
  Built on top of the `ROC` open-source foundation, we are building an upcoming suite of
  terminal-native apps (that all work seamlessly over SSH). Products like **local-first
  collaborative *"Google Docs meets Jupyter notebooks"* for Markdown** (real-time
  collaborative editing and Markdown code execution) and **headless virtual terminal
  multiplexers** with virtual tabs for interactive cloud infrastructure setup and
  multiplexed AI coding agent workflows — all focused on **data sovereignty, privacy, and
  local-first computing**.

## What I Bring (30-Year Career)

Over a 30-year tech career, I've remained a hands-on software engineer throughout while
spending 10+ of those years concurrently leading companies, teams, and product strategy:

### Hands-On Software Engineering

- **Founder, Principal Systems Engineer & Maintainer, R3BL (5+ years):** Rust systems
  programming at scale — strictly type-safe, correctness-focused async architectures,
  custom CSS/Flexbox layout & rendering engines, full-featured Markdown editor component
  with custom Markdown parser & syntax highlighting, low-latency PTY/TTY I/O, headless
  terminal virtualization, and local-first collaborative developer tools.
- **Senior Software Engineer, Google (7 yrs 6 mos):**
    - **Android Studio IDE platform team:** Performance, memory latency, and stability
      optimization for IntelliJ-based IDE (10M+ LOC codebase) serving millions of
      developers.
    - **Google Maps APIs:** Places API for Android SDK (Java) and Maps
      JavaScript/TypeScript API for Web.
    - **Android Media Framework:** Core Android Media OS framework and ExoPlayer
      (YouTube).
    - **Android UX Design:** Design architectures and frameworks for Android developers.
- **Technical Founder & CEO, TRNQL (1 yr 2 mos, 2015–2016):**
    - **Venture & Team Leadership:** Founded startup, raised $1.5M in VC seed funding,
      recruited and managed a team of 6, set company culture, and operated the business.
    - **Contextual Mobile SDKs & ML Signals:** Created and shipped production Android and
      iOS SDKs (and the
      [TRNQL Interplay](https://apkpure.com/trnql-interplay/com.trnql.sample_interplay)
      app) that collected real-time device signals feeding ML pipelines to better
      understand human behavior in the real world.
    - **Mobile & Cloud Architecture:** Designed and coded the Android contextual-awareness
      SDK container and the Java cloud backend infrastructure.
- **Founder & Principal Engineer, ScreamingToaster (4 yrs 4 mos, 2007–2011):**
    - **Product & Agency Leadership:** Founded a mobile-first product and consulting
      company; architected and delivered cross-platform products (BlackBerry, Android,
      iOS, Web) for clients including Quest Diagnostics, Mizuno USA, and HUGE Inc.
    - **Award-Winning Consumer Apps:** Shipped 4 apps (_RainOrShine_, _Wicked_, _MyListy_,
      _DulyNoted_) used by 100k+ users globally; 2× Global BlackBerry DevCon Best App in
      the World finalist (2009 & 2010), with _RainOrShine_ featured in the top 5 weather
      apps on BlackBerry App World. Also published Android apps (_ExtraTKT_,
      [StayAwake](https://play.google.com/store/apps/details?id=com.r3bl.stayawake&hl=en_US)).
    - **Custom PaaS, DSLs & UI Toolkits:** Built a custom Tomcat-based Java PaaS cloud
      engine (supporting web, iOS, Android, and BlackBerry clients with integrated
      payments, licensing, and subscriptions), declarative DSLs with multi-platform code
      generators (Java, Android, BlackBerry, JS), and custom UI/animation containers.
- **Principal Engineer & Enterprise Solutions Architect (9+ years, 1997–2007):** Led R&D
  and systems architecture across Defywire (invented US Patent
  [US6891860B1](https://patents.google.com/patent/US6891860) for mobile push/socket
  multiplexing, custom binary wire protocols, and mobile UI markup languages), HP, BEA
  Systems, SeeBeyond, Infravio, Noblestar, Nanocom, and BeanFactory. Authored a 400-page
  book on [Java and XML](https://www.amazon.com/dp/188477783X) (Manning Publications,
  2001; ISBN-10: `188477783X`, ISBN-13: `978-1884777837`).
- **Full-Stack Systems Breadth:** Desktop, web, mobile, IDEs, and cloud infrastructure —
  Rust, Kotlin, Java, Android, TypeScript, React, Redux, React Native, Node.js, Python,
  Firebase, SQL/NoSQL, TDD, CLI & GUI toolkits.

### Executive & Technical Leadership

- **Founder & CEO Experience (10+ years):** Built and led startups and engineering
  organizations: R3BL, TRNQL (raised $1.5M VC seed), ScreamingToaster, and BeanFactory.
  Combining deep systems architecture with business and product strategy, and go-to-market
  execution.
- **Team Building & Execution:** Recruiting, mentoring, product vision, and go-to-market
  execution across distributed and in-person engineering teams.
- **Player-Coach Leadership:** Comfortable moving fluidly between low-latency systems
  architecture, production code, and organizational leadership.

## Teaching, Speaking & Community

I've led the creation of developer narratives, tutorials, and educational programs at
scale across the industry and at Google:

- **developerlife.com (Since 1998, 10M+ pageviews):** Founded and authored in-depth
  engineering tutorials and architecture case studies across
  [Rust](https://developerlife.com/category/Rust/), Tokio, TUI/CLI systems, Kotlin,
  Android, TypeScript, React, and Redux.
- **YouTube Live Coding
  ([youtube.com/@developerlifecom](https://www.youtube.com/@developerlifecom)):** Advanced
  Rust systems programming — async, Tokio, design patterns (typestate, newtype),
  concurrent and parallel programming, zero-copy parsing, and procedural macros.
- **Google Android UX Design Show & Udacity Course (400k+ combined reach):** Created and
  hosted the
  [UX Design for Developers YouTube show](https://www.youtube.com/playlist?list=PLWz5rJ2EKKc-riD21lnOjVYBqSkNII3_k)
  for Google Android (200k+ views) and authored the
  [Udacity UX Design for Mobile Developers course](https://www.udacity.com/course/ux-design-for-mobile-developers--ud849)
  (200k+ students).
- **Google I/O Experiential Workshops:** Created and ran the first hands-on UX design
  workshops for developers at Google I/O 2013 and I/O 2014, hosting 2,000+ attendees.
- **Design for Humans Meetup Founder:** Founded and grew a 2,000+ member Silicon Valley
  meetup community, presenting at 34+ monthly meetups with 4,000+ developer and designer
  attendees.

> ✨ You can read all my articles on [developerlife.com](https://developerlife.com) and
> watch my videos on [YouTube](https://www.youtube.com/@developerlifecom).

## Patents and Books

- **US Patent [US6891860B1](https://patents.google.com/patent/US6891860):** _Method and
  apparatus for establishing multiple bandwidth-limited connections for a communication
  device_
- **Book:** [Java and XML](https://www.amazon.com/dp/188477783X) — Manning Publications
  (May 2001, First Edition, 400 pages; ISBN-10: `188477783X`, ISBN-13: `978-1884777837`)
