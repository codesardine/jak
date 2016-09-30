## Jade Application Kit

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
 
  * This works on Linux, but there is Python Gobject for Windows and MacOx. I have not tested on the lastest 2 since am only trageting Linux for now, it should work!

 * Does it work with PyPy
 
  * Perhaps! there is a version of PyGobject for PyPy, but that was not tested.
  
## Features
 * You can use any scripting language you like (PHP, Python, Ruby, Javascript)!
 * Use HTML5, CSS3 or Webgl.
 * Use any backend server or none at all!
 * Have your applications run in the browser with websockets using the GTK Broadway backend.
 
## Usage
comming soon.

## Known Issues
broadway backend segfaults.
window shadows that should not be there wen using transparent window in Dock mode.
missing options in app.json will throw an error.

## License

*Copyright (c) 2015-2016, Vitor Lopes. All rights reserved.*

JAK is covered by the GPL license.
