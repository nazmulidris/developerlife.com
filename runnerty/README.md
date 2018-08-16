<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [runnerty-quick-start](#runnerty-quick-start)
  - [To Use](#to-use)
  - [Resources for Learning Runnerty](#resources-for-learning-runnerty)
  - [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

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

Note: It's possible that you have to use super user permissions. More: [fix npm permisions](https://docs.npmjs.com/getting-started/fixing-npm-permissions)

```bash
# Clone this repository
git clone https://github.com/runnerty/runnerty-quick-start

# Go into the repository
cd runnerty-quick-start

# Install dependencies
npm install

# Run the example
runnerty
```

## Resources for Learning Runnerty

- [docs.runnerty.io](http://docs.runnerty.io) - all of Runnerty's documentation

## License

[MIT License](LICENSE)
