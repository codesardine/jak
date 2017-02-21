
# coding: utf-8

JAK           = " Jade Application Kit "
__version__   = " 0.19b2"
__author__    = " Copyright (c) 2016 Vitor Lopes " 
__url__       = " https://codesardine.github.io/Jade-Application-Kit "

#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import sys
import json
import os
import socket
import argparse
import subprocess
try:
    import gi
except ImportError:
    print("PyGObject not found")
    sys.exit(0)

gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, Gdk, WebKit2, Gio

def cml_options():

    # Create command line options
    option = argparse.ArgumentParser(description='''\
      Jade Application Kit
      --------------------
      Create desktop applications with
      Python, JavaScript and Webkit2

      Author: Vitor Lopes
      Licence: GPLv2 or later

      url: https://codesardine.github.io/Jade-Application-Kit''', epilog='''\
      ex: jak /path/to/my/app/folder
      ex: jak -d http://my-url.com
      ''', formatter_class=argparse.RawTextHelpFormatter)
    option.add_argument("-d", "--debug", metavar='\b', help="enable developer extras in webkit2")
    option.add_argument('route', nargs="?", help='''\
    Point to your application folder or url!
    ''')
    return option.parse_args()

options = cml_options()
w = Gtk.Window
path = os.getcwd()
jak_path = os.path.dirname(__file__)

class Api:

    html = ""

    def open_file(filename, accessmode="r"):
        """
            input:  filename and path.
            output: file contents.
        """
        file = open(filename, accessmode, encoding='utf-8')  # fixme need a way of closing the file?
        return file

def sanitize_input():

    get_route = options.route
    # if running as module
    if get_route is None:
        # returns the path of the file importing the module
        get_route = os.path.dirname(os.path.abspath(sys.argv[0])) 
          
    NOSSL_MSG = "You can only run unsecured url's in debug mode. Change "
    SSL_MSG   = " forcing SSL"
      
    if get_route.endswith("/"):
        pass

    else:
        get_route = get_route + "/"

    app_settings = get_route + "application-settings.json"
    app_path = get_route
    if os.path.isdir(get_route):
        get_route = get_route + "index.html"

    elif not options.debug and get_route.startswith("http://"):
        get_route = get_route.replace("http:", "https:")
        print(NOSSL_MSG + "http: to https:" + SSL_MSG)

    elif not options.debug and get_route.startswith("ws:"):
        get_route = get_route.replace("ws:", "wss:")
        print(NOSSL_MSG + "ws:// to wss://" + SSL_MSG)

    return get_route, app_settings, app_path

def load_window_css(css):

    styles = Gtk.CssProvider()

    if os.path.isfile(css):
        styles.load_from_path(css)

    else:
        styles.load_from_data(css)

    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        styles,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

class AppWindow(w):

    def __init__(self):  # Create window frame

        # get tuple values from function
        get_name, get_description,\
        get_version, get_author,\
        get_licence, get_help_contents,\
        get_url, get_route,\
        get_icon, get_hint_type,\
        get_width, get_height,\
        is_fullscreen, is_resizable,\
        is_decorated, is_transparent,\
        get_debug = get_app_config()

        if get_hint_type == "desktop" or get_hint_type == "dock":
                w.__init__(self, title = get_name, skip_pager_hint=True, skip_taskbar_hint=True)

        else:
                w.__init__(self, title = get_name)

        # create webview
        self.webview = WebKit2.WebView()
        self.add(self.webview)
        settings = self.webview.get_settings()
        
        jak_window_css_path = jak_path + "/window.css"
        load_window_css(jak_window_css_path)
        
        app_path = sanitize_input()[2]
        app_window_css_path = app_path + "window.css"
        if os.path.exists(app_window_css_path):
            load_window_css(app_window_css_path)
        
        js_path = app_path + "app.js"
        if os.path.exists(js_path):
            app_js = Api.open_file(js_path).read()
            self.webview.run_javascript(str(app_js)) # i am not happy with this since i can only call run_javascript once?

        if is_transparent == "yes":

            # EXPERIMENTAL FEATURE:
            screen = w.get_screen(self)
            color = screen.get_rgba_visual()
            if color != None and screen.is_composited():
                self.set_app_paintable(True) # not shure if i need this 
                                
                css = b"""
                #jade-window, #jade-header, #jade-dock, #jade-desktop {
                    background-color: rgba(0,0,0,0);
                } """

                # TODO hint type dock, remove box shadow, need to find the right css class.
                # TODO hint type dock or desktop, transparent window appears black.
                # TODO this needs more testing maybe using cairo is a better option.

                load_window_css(css)
                self.webview.set_background_color(Gdk.RGBA(0, 0, 0, 0))
            
            else:
                print("Your system does not supports composited windows")
                
        icontheme = Gtk.IconTheme.get_default()

        if os.path.exists(get_icon):
            w.set_icon_from_file(self, get_icon )

        else:
            try:
                get_icon = icontheme.load_icon(Gtk.STOCK_MISSING_IMAGE, 0, 0)
                w.set_icon(self, get_icon)
                print("Icon not specified or incorrect path, loading default icon!")

            except Exception as err:
                print(err)
                print("something went wrong loading your icon")

        if get_hint_type == "desktop":
            w.set_name(self, 'jade-desktop')
            w.set_type_hint(self, Gdk.WindowTypeHint.DESKTOP)
            w.set_resizable(self, False)

        elif get_hint_type == "dock":
            w.set_type_hint(self, Gdk.WindowTypeHint.DOCK)
            w.set_name(self, 'jade-dock')

        else:
            w.set_type_hint(self, Gdk.WindowTypeHint.NORMAL)
            w.set_name(self, "jade-window")
            header = Gtk.HeaderBar()
            header.set_name("jade-header")
            header.set_show_close_button(True)
            header.props.title = get_name
            w.set_titlebar(self, header)

            def about_on_click(about_button):
                # TODO this will be converted to javascript
                    if popover.get_visible():
                       popover.hide()
                    else:
                       popover.show_all()

            def help_on_click(help_button):
                # TODO this will be done in javascript
                test = "alert('alert works')"
                self.webview.run_javascript(test)

            about_button = Gtk.Button(label = "About", relief = Gtk.ReliefStyle.NONE)
            help_button = Gtk.Button(relief = Gtk.ReliefStyle.NONE)

            icon = Gio.ThemedIcon(name = "help")
            image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
            help_button.add(image)

            help_button.set_tooltip_text("HELP section, How to use " + get_name)
            about_button.set_tooltip_text("Get more information about " + get_name)

            #header.pack_start(help_button)
            header.pack_end(about_button)

            about_button.connect("clicked", about_on_click)
            help_button.connect("clicked", help_on_click)

            popover = Gtk.Popover.new(about_button)
            popover.set_name("jade-popover")

            name        = Gtk.Label(get_name)
            author      = Gtk.Label()
            licence     = Gtk.Label()
            version     = Gtk.Label()
            description = Gtk.Label()
            MADE_WITH   = Gtk.Label()
            app_url     = Gtk.Label()
            
            WEBSITE       = "<b>Website:</b> "
            MADE_WITH_MSG = "<b>Made With:</b> "
            
            author.set_markup("<b>Author:</b>  " + get_author)
            licence.set_markup("<b>Licence:</b> " + get_licence)
            version.set_markup("<b>Version:</b> " + get_version)
            description.set_markup("<b>Description:</b>   " + get_description)
            MADE_WITH.set_markup(MADE_WITH_MSG + JAK + "<a href=" + "'" + __url__ + "'" + "> URL </a>")
            app_url.set_markup(WEBSITE  + "<a href=" + "'" + get_url + "'" + ">" + get_url + "</a>")
            
            name.set_name("about-title")
            
            popover_box = Gtk.Box(name = "jade-about-box", spacing=12, orientation=Gtk.Orientation.VERTICAL)

            get_help_box_contents = Gtk.Label(get_help_contents)
            help_box = Gtk.Box(name = "jade-help-box", spacing=12, orientation=Gtk.Orientation.VERTICAL)

            popover_box.add(name)
            popover_box.add(version)
            popover_box.add(description)
            popover_box.add(author)
            popover_box.add(licence)
            popover_box.add(app_url)
            popover_box.add(MADE_WITH)
            help_box.add(get_help_box_contents)
            popover.add(popover_box)

            #self.add(help_box)

        w.set_position(self, Gtk.WindowPosition.CENTER)
        if is_resizable == "no":
            w.set_resizable(self, False)

        if is_decorated == "no":
            w.set_decorated(self, False)

        if is_fullscreen == "yes":
              screen = w.get_screen(self)
              w.set_default_size(self, screen.width(), screen.height())
        else:
              w.set_default_size(self, get_width, get_height)

        if get_debug == "yes" or options.debug:
              settings.set_property("enable-developer-extras", True)

              # disable all cache in debug mode
              settings.set_property("enable-offline-web-application-cache", False)
              settings.set_property("enable-page-cache", False)

        else:
            # Disable webview rigth click menu
            def disable_menu(*args):  return True
            self.webview.connect("context-menu", disable_menu)
            settings.set_property("enable-offline-web-application-cache", True)

        settings.set_property("default-charset", "utf-8")
        settings.set_user_agent_with_application_details(get_app_config()[0], get_app_config()[2])
        settings.set_property("allow-file-access-from-file-urls", True)
        settings.set_property("javascript-can-access-clipboard", True)
        settings.set_property("enable-write-console-messages-to-stdout", True)
        settings.set_property("enable-spatial-navigation", True) # this is good for usability

        get_route = "file://" + get_route

        def load_html():

            self.webview.load_html(Api.html, get_route)
            if Api.html == "":
                print("Python HTML string empty!")

        if os.path.isfile(get_route):

            self.webview.load_uri(get_route)

        else:
            load_html()

def get_app_config():

        get_route = sanitize_input()[0]

        app_settings = sanitize_input()[1]
        if os.path.exists(app_settings):
            # Open application-settings.json and return values

            app_settings = json.load(Api.open_file(app_settings))

            get_name          = app_settings["app"]["name"]
            get_description   = app_settings["app"].get("description")
            get_version       = app_settings["app"].get("version")
            get_author        = app_settings["app"].get("author")
            get_licence       = app_settings["app"].get("license")
            get_help_contents = app_settings["app"].get("help")
            get_url           = app_settings["app"].get("url")

            get_icon          = app_settings["window"].get("icon")
            get_hint_type     = app_settings["window"].get("hint_type")
            get_width         = app_settings["window"].get("width")
            get_height        = app_settings["window"].get("height")
            is_fullscreen     = app_settings["window"].get("fullscreen")
            is_resizable      = app_settings["window"].get("resizable")
            is_decorated      = app_settings["window"].get("decorated")
            is_transparent    = app_settings["window"].get("transparent")

            get_debug         = app_settings["webkit"].get("debug")

        else:
            get_name          = JAK
            get_description   = "application-settings.json missing using defaults"
            get_version       = "working on it just testing out!"
            get_author        = "Vitor Lopes"
            get_licence       = "my license, GPL is a good choice"
            get_help_contents = "help contents goes here"

            get_url           = "i need to think about that, maybe something starting with http?"
            get_icon          = ""
            get_hint_type     = ""
            get_width         = 800
            get_height        = 600
            is_fullscreen     = ""
            is_resizable      = ""
            is_decorated      = ""
            is_transparent    = ""
            get_debug         = "yes"

            print(get_description)

        return get_name, get_description,\
               get_version, get_author,\
               get_licence, get_help_contents,\
               get_url, get_route,\
               get_icon, get_hint_type,\
               get_width, get_height,\
               is_fullscreen, is_resizable,\
               is_decorated, is_transparent,\
               get_debug

def run_sh():
    # not shure if i am happy with this
    sh_path = sanitize_input()[2]
    sh = sh_path + "startup.sh"
    if os.path.exists(sh):
        local = socket.gethostbyname(socket.gethostname()) # this only supports ipv4.
        if sh.startswith("/") or sh == local: # prevent remote execution off shell scripts.
            try:
                subprocess.call([sh])

            except Exception as err:
                print("Ops something went wrong running startup.sh: " + str(err))


def run():

    run_sh()
    w = AppWindow()
    w.connect("delete-event", Gtk.main_quit)
    w.show_all()  # maybe i should only show the window wen the webview finishes loading?
    Gtk.main()

def cml():

    if options.debug:
        options.route = sys.argv[2]

    if options.route:
        run()

    else:
        subprocess.call(["jak", "-h"])
