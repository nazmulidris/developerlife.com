---
author: Nazmul Idris
date: 2017-07-19 23:36:19+00:00
excerpt: |
  Tutorial and code on GitHub that demonstrates the use of ya-csv and inquirer
  to load CSV files from node.js and convert them into JSON files, to generate sample
  data for other apps.
layout: post
title: "Loading CSV files in Node"
categories:
  - Web
---

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [Instructions to run this](#instructions-to-run-this)
- [What is in this project](#what-is-in-this-project)
  - [ya-csv](#ya-csv)
  - [inquirer](#inquirer)
  - [Flow type](#flow-type)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Introduction

This project loads a CSV file from the local filesystem and generates a JSON object that's written
to a JSON file, which can be used for sample data in other projects.

# Instructions to run this

1. Clone the project from [GitHub](https://github.com/r3bl-alliance/node-csv-to-json)
   `https://github.com/r3bl-alliance/node-csv-to-json`.

1. Go to the folder that you cloned the project in, and run `npm install`.

1. Then build the code using `npm run build`.

1. Finally run it using `npm start`.

There's a script `run.sh` that is provided for your convenience to do the build and run step in one.

# What is in this project

There are a few interesting things in this project that I will call out in this article.

1. Using `ya-csv` to load CSV files from the filesystem. More info
   [here](https://www.npmjs.com/package/ya-csv).

1. Using `inquirer` to prompt the user for input from the console. This is a good library to build a
   command line interpreter (CLI). More info [here](https://www.npmjs.com/package/inquirer).

1. Using Flow type in order to annotate the JavaScript code with static typing that is used while
   building, but stripped before running the code. More info
   [here](https://flow.org/en/docs/types/).

## ya-csv

This is a really simple to use library to read and write CSV files. Here's the code to read a CSV
file from your local filesystem.

```javascript
function createObjectFromCSVFile(inputFile: string, onFileLoadedFunction: Array) {
  let csv = require("ya-csv")
  let returnValue: Array = new Array()
  let reader = csv.createCsvFileReader(inputFile, { columnsFromHeader: true })
  reader.addListener(
    "data",
    // Called after each row from CSV file is loaded.
    (rowObject) => {
      // The rowObject is a JSON object, you can get it's properties
      // out by using the keys that are from the first header row of
      // the input CSV file.
      // Eg: if header row of the CSV file is: Type, Trans Date,
      // Post Date then you can use rowObject['Type'],
      // rowObject['Trans Date'], and rowObject['Post Date'] to get
      // the values for each of the columns in the row.
      returnValue.push(rowObject)
    }
  )

  reader.addListener(
    "end",
    // Called after all rows have been loaded from CSV file.
    function (data_row) {
      onFileLoadedFunction(reader.columnNames, returnValue)
    }
  )
}
```

The `ya-csv` library reads each line from your input file and fires an event `data` that you attach
a listener function to. If you have 10 rows in your CSV (including the header), then the function
will be run 9 times.

By passing the object `{columnsFromHeader: true}` to the `createCsvFileReader()` function, you are
telling the `ya-csv` parser to use the first line of the file to get all the header names.

```javascript
csv.createCsvFileReader(inputFile, { columnsFromHeader: true })
```

Here are a few lines from the `sampledata.csv` file (in the `assets` folder).

```text
Type,Trans Date,Post Date,Description,Amount,
Sale,06/30/2017,07/02/2017,WHOLEFDS STC 10267,-25.25,
Sale,06/30/2017,07/02/2017,WHOLEFDS LAT 10155,-16.56,
Sale,06/29/2017,06/30/2017,AMAZON MKTPLACE PMTS,-12.99,
Sale,06/29/2017,06/30/2017,Amazon.com,-44.6,
Sale,06/29/2017,07/02/2017,WHOLEFDS STC 10267,-7.5,
```

The first line is used to get the following column names:

1. `Type`
2. `Trans Date`
3. `Post Date`
4. `Description`
5. `Amount`
6. ``

In the `data` listener function of the `ya-csv` parser, you can access these fields using the
following syntax: `rowObject['Trans Date']`. Note: there are spaces in the column names, which is
why you can't use the normal `rowObject.Trans Date` syntax to get the cell at that column for the
given row.

Finally, if you wanted to write a CSV file using this library, here is some code.

```javascript
let csv = require("ya-csv")
let fs = require("fs")
let writer = csv.createCsvStreamWriter(fs.createWriteStream("file_name.csv"))
writer.writeRecord(["column1", "column2", "column3"])
```

Note: this code will rewrite the file everytime you create the writer. If you want to append data to
an existing CSV file instead, then create the `writer` object in a different way.

```javascript
let writer = csv.createCsvStreamWriter(fs.createWriteStream("file_name.csv", { flags: "a" }))
```

## inquirer

The `inquirer` library is a very sophisticated way to get user input. You can present the user with
prompts and get text input, or even checkboxes, radio buttons, etc. all done as text.

For the purposes of this project, the requirement was to get two things from the user: the input
file name, and the output file name.

Here's the code to make this happen.

```javascript
let inquirer = require("inquirer")
let functions = require("./functions")

// Display welcome message.
let message: string = "node-csv-to-json"
console.log(message)

// Ask the user for the path to the CVS file.
let questions = [
  {
    type: "input",
    name: "inputFilePath",
    message: "What is the path to your input CSV file?",
    default: "assets/sampledata.csv",
  },
  {
    type: "output",
    name: "outputFilePath",
    message: "What is the path to the output JSON file?",
    default: "assets/sampledata.json",
  },
]
inquirer.prompt(questions).then(userReply)
```

There's a callback function `userReply` that gets called, when the library gets the required
answers. And it passes this function an object that contains the answers.

```javascript
function userReply(answers: FileLocationsType) {
  let inputFile = answers.inputFilePath
  let outputFile = answers.outputFilePath

  console.log(inputFile)
  console.log(outputFile)
}
```

## Flow type

Facebook's Flow type is an excellent way to add type safety to JavaScript in a very non invasive
way. Flow is great for creating type aliases that describe the shape of objects, so that you can
remember what type of object goes where, instead of having to guess.

Here are some great links for Flow and Node.

1. [`import type`](https://flow.org/blog/2015/02/18/Import-Types/).
2. [Flow and `npm`](https://stackoverflow.com/questions/39385890/how-to-import-flow-annotations-types-and-interfaces-from-an-npm-published-modul).
3. [Flow website](https://flow.org/).
4. [Flow type annotations](https://flow.org/en/docs/types/).

I've also added some npm scripts to make this go easier.

1. `npm run build` - This actually stripts out all the flow annotations and copies the JS files to
   the `lib/` folder.

2. `npm start` - This just runs the index.js file in the `lib/` folder (and not `src` folder).

The way I've used Flow in this project is to annotate some of the variables with primitive types
such as `string`, and `Array`.

I've also created my own type alias, in the `types.js` file.

```javascript
type FileLocationsType = {
  inputFilePath: string,
  outputFilePath: string,
}
```

Note: I've got `// @flow` at the top of each JS file that has Flow, to let the pre-processor know
that these are files that the type annotations should be stripped out from.

I import my type alias into the `index.js` file using the following statement.

```javascript
import type FileLocationsType from "./types.js"
```

Then, I'm able to use the `FileLocationsType` in my code, like this.

```javascript
function userReply(answers: FileLocationsType) {
  let inputFile = answers.inputFilePath
  let outputFile = answers.outputFilePath
}
```
