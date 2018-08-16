<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [runnerty-quick-start](#runnerty-quick-start)
  - [To Use](#to-use)
  - [Resources for Learning Runnerty](#resources-for-learning-runnerty)
  - [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Notes

## plan.json and filewatcher

The following snippet causes a filewatcher to run on `../_posts` (value of 
`WATCH_FOLDER`) and when anything in that folder `change`s it triggers the
process to execute.
```json
"triggers": [{
    "id": "filewatcher_default",
    "file_name": "@GV(WATCH_FOLDER)",
    "condition": "change"
}],
```

This was causing a big infinite loop problem. Everytime a markdown file would
change, it would trigger the process to run (`run-doctoc.sh`) which would
run `doctoc` on the files that have recently changed. And `doctoc` touches
a file, so that triggers another file system change, which then triggers the
process to run, etc. Inifinte loop! 🤯

So, in order to fix this, I replaced the filewatcher trigger with a scheduled
trigger that runs every 2 minutes and looks for files that have changed in the
last minute in order to run doctoc on them. Here's an excerpt from plan.json
for this.

```json
"triggers": [{
    "id": "schedule_default",
    "schedule_interval": "*/2 * * * *"
}],
```

However, this doesn't cause new files to be processed immediately, when they're
added to the `_posts` folder. In order to handle this, I added another rule, which
triggers when new files are added. Here's a snippet.

```json
"triggers": [{
    "id": "filewatcher_default",
    "file_name": "@GV(WATCH_FOLDER)",
    "condition": "add"
}],
```

# runnerty-quick-start

**Clone and run for a quick way to see Runnerty in action.**

A basic Runnerty planification needs just these files:

- `package.json` - Points to the app's main file and lists its details and dependencies. Extra plugins goes here (**triggers, notifiers and executors**).
- `config.json` - Configuration file for Runnerty's plugins also global values are set here.
- `plan.json` - The processes planification and dependencies are specified here.

## To Use

To clone and run this repository you'll need [Git](https://git-scm.com), [Node.js 8.9.4](https://nodejs.org/en/download/) (which comes with [npm 5.6.0](http://npmjs.com)) or higher and [Runnerty 2.0.0](https://github.com/runnerty/runnerty) installed on your computer.

From your command line:

```bash
# Install runnerty
npm i -g runnerty

# You can check the correct instalation with the command  
runnerty --version
```