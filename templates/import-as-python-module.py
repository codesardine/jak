#!/usr/bin/env python3
# coding: utf-8
try:
    from j.AK import Api, AppWindow

except Exception as err:
    print("Ops something went wrong: " + str(err))

from gi.repository import Gtk, WebKit2


class applicationWindow(AppWindow):
    """
    extends AK.AppWindow functionality
    """

    def __init__(self):

        super(applicationWindow, self).__init__()

        ## custom html
        
        #AK.Api.html = """
        #<h1>jade Application Kit rocks</h1>
        #<p>hey my app is great<p>
        #"""

        ## custom JavaScript

        #AK.Api.javascript += """
        #alert("Testing JavaScript");
        #"""

        # more code here

        ## only if loading a url

        #URL = "http://my-url.com"
        #self.webview.load_uri(URL)


applicationWindow()
Gtk.main()
