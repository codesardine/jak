## Jade Application Kit

[![Join the chat at https://gitter.im/JadeApplicationKit/Lobby](https://badges.gitter.im/JadeApplicationKit/Lobby.svg)](https://gitter.im/JadeApplicationKit/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/c79991176d484d50960a36007749b6a6)](https://www.codacy.com/app/vmnlop/Jade-Application-Kit?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=vmnlopes/Jade-Application-Kit&amp;utm_campaign=Badge_Grade)

Official site: https://github.com/vmnlopes/jak  
Official documentation: Work in progress!

## Introduction

## This is a DEV Preview not fully finish but it works!

 JAK is an application build in Python 3 on top of GTK3, Pygoject and Webkit2. You can write hybrid Web and Desktop applications on top of a webview, including but not limited to DOCKS, Widgets, or any other sort of apps, .
 This works same way as Node Webkit or Electron with a few diferences.
 
## Faqs
 
 * Wy was this build we already have software that does that?
 
  * Other available software did not fullfill my needs. This was build out of my desire of learning python, since i love the syntax and i am building some applications with python and HTML and got fed up off building webviews over and over!
  
 * Does this comes with a server?
  
  * NO, you dont need a server to build a HTML5, Javascript, CSS3 Application.
  * But if you require one, you can use any server you like or even build your own!
  
 * Do i need to know Python?
  
  * NO!
 
 * Is this cross platform?
 
  * There are packages for your Linux distro, for Windows and MacOx i tink you have to compile PyGobject. I have not tested on the lastest 2 since am only trageting Linux for now, it should work!

 * Does it work with PyPy
 
  * Perhaps! there is a version of PyGobject for PyPy, but that was not tested.
  
## Features
 * You can use any scripting language you like (PHP, Python, Ruby, Javascript)!
 * Use HTML5, CSS3 or Webgl.
 * Use any backend server or none at all!
 * Have your applications run in the browser with websockets using the GTK Broadway backend.
 
## Usage
```
jak /path/to/application/directory
```
          or
```
jak http://Address
```
```
debug mode --> jak -d  myAppRoot
help       --> jak -h
```
JAK Will look for 2 files in the root of you app, app.json and window.css.
 * window.css can be used to customize the window look if you want to is not required.
 
 * app.json options
   
    * hint_type   3 options --> dock (can be used to create panels or widgets), desktop (will spawn a fullscreen undecorated window that will stay below all windows) or leave blank for normal application window.
    
    * width       window width
    * height      window height
    * fullscreen  leave blank and above sizes will be used or type yes
    * resizable   leave blank or type no
    * decorated   leave blank for decorations or type no
    * transparent leave blank for normal or type yes  
    * debug       leave blank or type yes
 
 ```
 your app.json should look like this!
 {
  "app": {
  
  "name":        "my application name",
  "description": "some description",
  "version":     "0.1",
  "author":      "your name",
  "url":         "your application url",
  "license":     "GPL",
  "help":        ""
  
  },
  
  "window": {
    "icon":        "your icon path",
    "hint_type":   "dock", 3 options --> dock, desktop or leave blank for normal apps
    "width":       600,
    "height":      400,
    "fullscreen":  "yes"
    "resizable":   "no",  
    "decorated":   "no",  
    "transparent": "yes"  
    
  },
  
  "webkit": {
  
    "debug":  "yes"   
  }
}
```

## Known Issues
 * broadway backend segfaults.
 * window shadows that should not be there wen using transparent window in Dock mode.
 * missing options in app.json will throw an error and crash you app.
 * theres no way of positioning windows in the screen that was not implemented yet but it will be.

## License

*Copyright (c) 2015-2016, Vitor Lopes. All rights reserved.*

JAK is covered by the GPL license.
