# scarfer

Source code scan report file reporter

# Introduction

Scarfer outputs compliance related information from a scan report.

A scan report contain lots of information, for example Scancode has 37
entries on the top level for each file, about a file and it is
sometimes cumbersome to open with an editor to extract the information
wanted. Scarfer provides a quick command line access to scan reports.

# Features

Scarfer can output the following information per file:

* copyright (using `-c`)

* license (using `-l`)

* text that caused the license detection (`-m`)

Scarfer can filter files:

* include 

    * license name (`-il`) using Python's regular expressions

    * license name (`-if`) using Python's regular expressions

* exclude

    * license name (`-el`) using Python's regular expressions

    * license name (`-ef`) using Python's regular expressions

*Note: if you're using more than one filter then filters are AND:ed together*

# Example use

Output the file names (full path) of all the files in the Scancode report `example-data/cairo-1.16.0-scan.json`:
```
$ scarfer example-data/cairo-1.16.0-scan.json 
```

As above but output only files with path matching `drm`:
```
$ scarfer example-data/cairo-1.16.0-scan.json -if drm
```

Output the file names (full path) of all the files in the Scancode report `example-data/cairo-1.16.0-scan.json` with a license matching `gpl-3`:
```
$ scarfer example-data/cairo-1.16.0-scan.json -il gpl-3
```

Output the file names (full path) of all the files in the Scancode report `example-data/cairo-1.16.0-scan.json` with a license matching `mpl` and files with path matching `drm`. The output should also contain information (per file) about license and copyright:
```
$ scarfer example-data/cairo-1.16.0-scan.json -il mpl -if drm -c -l 
```

To filter in all files containing "/*pdi" and ending with ".c":
```
$ scarfer example-data/cairo-1.16.0-scan.json -if "/.*pdi.*\.c$"
```

To filter out all files containing "/*pdi" and ending with ".c":
```
$ scarfer example-data/cairo-1.16.0-scan.json -ef "/.*pdi.*\.c$"
```


# Supported scan report formats

* [Scancode](https://github.com/nexB/scancode-toolkit) Toolkit, version 21 and upwards

* [Scancode](https://github.com/nexB/scancode-toolkit) Output Format version 1.0.0






