# coding: utf-8
"""

          Jade Application Kit
 Author - Copyright (c) 2016 Vitor Lopes
 url    - https://codesardine.github.io/Jade-Application-Kit

"""

import argparse
import json
import os
import subprocess
import sys

try:
    import gi

except ImportError:
    print("PyGObject not found.")
    sys.exit(0)

gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, Gdk, WebKit2


def cml_options():
    # Create command line options
    option = argparse.ArgumentParser(description='''\
      Jade Application Kit
      --------------------
      Create desktop applications with
      Python, JavaScript and Webkit2

      Author : Vitor Lopes
      Licence: GPLv2

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
path = os.getcwd()
jak_path = os.path.dirname(__file__)
application_path = options.route

# if running as module
if application_path is None:
    # returns the path of the file importing the module
    application_path = os.path.dirname(os.path.abspath(sys.argv[0]))

if application_path.endswith("/"):
    pass

else:
    application_path += "/"


class Api:
    html = ""
    javascript = ""

    def openFile(file_name, access_mode="r"):
        """
            input:  filename and path.
            output: file contents.
        """
        try:
            with open(file_name, access_mode, encoding='utf-8') as file:
                return file.read()

        except IOError:
            print(file_name + " File not found.")
            sys.exit(0)


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


def get_app_config():
    application_settings = application_path + "application-settings.json"

    if os.path.exists(application_settings):
        # Open application-settings.json and return values

        application_settings = Api.openFile(application_settings)
        application_settings = json.loads(application_settings)

        application_name        = application_settings["application"]["name"]
        application_description = application_settings["application"].get("description")
        application_version     = application_settings["application"].get("version")
        application_author      = application_settings["application"].get("author")
        application_licence     = application_settings["application"].get("license")
        application_url         = application_settings["application"].get("url")

        application_window_hint_type   = application_settings["window"].get("hint_type")
        application_window_width       = application_settings["window"].get("width")
        application_window_height      = application_settings["window"].get("height")
        application_window_full_screen = application_settings["window"].get("fullscreen")
        application_window_resizable   = application_settings["window"].get("resizable")
        application_window_decorated   = application_settings["window"].get("decorated")
        application_window_transparent = application_settings["window"].get("transparent")
        application_window_icon        = application_settings["window"].get("window_icon")

        application_debug = application_settings["webkit"].get("debug")
        application_cache = application_settings["webkit"].get("cache")

    else:
        application_name = \
            application_description = \
            application_version = \
            application_author = \
            application_licence = \
            application_url = \
            application_window_hint_type = \
            application_window_width = \
            application_window_height = \
            application_window_resizable = \
            application_window_decorated = \
            application_window_transparent = \
            application_window_icon = ""

        application_window_full_screen = "yes"
        application_debug = "yes"
        application_cache = "none"

    return application_name, \
           application_description, \
           application_version, \
           application_author, \
           application_licence, \
           application_url, \
           application_path, \
           application_window_hint_type, \
           application_window_width, \
           application_window_height, \
           application_window_full_screen, \
           application_window_resizable, \
           application_window_decorated, \
           application_window_transparent, \
           application_window_icon, \
           application_debug, \
           application_cache


class AppWindow(Gtk.Window):
    def __init__(self):  # Create window frame

        # get tuple values from function
        application_name, \
        application_description, \
        application_version, \
        application_author, \
        application_licence, \
        application_url, \
        application_path, \
        application_window_hint_type, \
        application_window_width, \
        application_window_height, \
        application_window_full_screen, \
        application_window_resizable, \
        application_window_decorated, \
        application_window_transparent, \
        application_window_icon, \
        application_debug, \
        application_cache = get_app_config()

        if application_window_hint_type == "desktop" or application_window_hint_type == "dock":
            Gtk.Window.__init__(self, title=application_name, skip_pager_hint=True, skip_taskbar_hint=True)

        else:
            Gtk.Window.__init__(self, title=application_name)

        # create webview
        self.webview = WebKit2.WebView.new()

        self.add(self.webview)
        self.settings = self.webview.get_settings()

        context = WebKit2.WebContext.get_default()
        
        if application_cache == "local":
            cache_model = WebKit2.CacheModel.DOCUMENT_BROWSER

        elif application_cache == "online":
            cache_model = WebKit2.CacheModel.WEB_BROWSER
            self.settings.set_property("enable-offline-web-application-cache", True)
            self.settings.set_property("enable-dns-prefetching", True)

        else: 
            cache_model = WebKit2.CacheModel.DOCUMENT_VIEWER
            print("Cache model not set, default is NO CACHE")

        context.set_cache_model(cache_model)

        screen = Gtk.Window.get_screen(self)

        #jak_window_style = jak_path + "/window.css"

        #if os.path.isfile(jak_window_style):
        #   load_window_css(jak_window_style)

        application_window_style = application_path + "window.css"

        if os.path.isfile(application_window_style):
            load_window_css(application_window_style)

        if application_window_transparent == "yes":

            # EXPERIMENTAL FEATURE:
            color = screen.get_rgba_visual()

            if color is not None and screen.is_composited():
                self.set_app_paintable(True)  # not sure if i need this

                css = b"""
                #jade-window, #jade-dock, #jade-desktop {
                    background-color: rgba(0,0,0,0);
                } """

                # TODO hint type dock, remove box shadow, need to find the right css class.
                # TODO hint type dock or desktop, transparent window appears black.
                # TODO this needs more testing maybe using cairo is a better option.

                load_window_css(css)
                self.webview.set_background_color(Gdk.RGBA(0, 0, 0, 0))

            else:
                print("Your system does not supports composite windows")

        if application_window_hint_type == "desktop":
            Gtk.Window.set_name(self, 'jade-desktop')
            Gtk.Window.set_type_hint(self, Gdk.WindowTypeHint.DESKTOP)
            Gtk.Window.set_resizable(self, False)

        elif application_window_hint_type == "dock":
            Gtk.Window.set_type_hint(self, Gdk.WindowTypeHint.DOCK)
            Gtk.Window.set_name(self, 'jade-dock')

        else:
            Gtk.Window.set_type_hint(self, Gdk.WindowTypeHint.NORMAL)
            Gtk.Window.set_name(self, "jade-window")

        Gtk.Window.set_position(self, Gtk.WindowPosition.CENTER)

        window_icon = application_path + application_window_icon
        if os.path.isfile(window_icon):
            Gtk.Window.set_icon_from_file(self, window_icon)
            print(window_icon)

        if application_window_resizable == "no":
            Gtk.Window.set_resizable(self, False)

        if application_window_decorated == "no":
            Gtk.Window.set_decorated(self, False)

        if application_window_full_screen == "yes":
            Gtk.Window.set_default_size(self, screen.width(), screen.height())

        else:
            Gtk.Window.set_default_size(self, int(application_window_width), int(application_window_height))

        self.settings.set_user_agent_with_application_details(get_app_config()[0], get_app_config()[2])
        self.settings.set_enable_smooth_scrolling(self)

        self.settings.set_default_charset("UTF-8")
        self.settings.set_property("allow-universal-access-from-file-urls", True)
        self.settings.set_property("allow-file-access-from-file-urls", True)
        self.settings.set_property("enable-write-console-messages-to-stdout", True)
        self.settings.set_property("enable-spatial-navigation", True)  # this is good for usability
        self.settings.set_property("enable-java", False)
        self.settings.set_property("enable-plugins", False)
        self.settings.set_property("enable-accelerated-2d-canvas", True)

        if application_debug == "yes" or options.debug:
            self.settings.set_property("enable-developer-extras", True)

            # disable all cache in debug mode
            self.settings.set_property("enable-offline-web-application-cache", False)
            self.settings.set_property("enable-page-cache", False)

        else:
            # Disable webview rigth click menu
            def disable_menu(*args):
                return True

            self.webview.connect("context-menu", disable_menu)
        
        screen_width = screen.width()
        screen_height = screen.height()

        # TODO javascript Api
        Api.javascript = '''

        var jadeApplication = {

        'name'         : '%(application_name)s',
        'description'  : '%(application_description)s',
        'version'      : '%(application_version)s',
        'author'       : '%(application_author)s',
        'license'      : '%(application_licence)s',
        'url'          : '%(application_url)s',
        'windowWidth'  : '%(application_window_width)s',
        'windowHeight' : '%(application_window_height)s',
        'screenWidth'  : %(screen_width)s,
        'screenHeight' : %(screen_height)s

        };
        jadeApplication.windowWidth = parseInt(jadeApplication.windowWidth);
        jadeApplication.windowHeight = parseInt(jadeApplication.windowHeight);

        if (isNaN(jadeApplication.windowWidth) || isNaN(jadeApplication.windowHeight)) {
            jadeApplication.windowWidth = jadeApplication.screenWidth;
            jadeApplication.windowHeight = jadeApplication.screenHeight;
        };
        ''' % locals()

        self.webview.run_javascript(Api.javascript)

        if os.path.isdir(application_path):

            index = application_path + "index.html"

            if os.path.isfile(index):
                index = "file://" + index
                self.webview.load_uri(index)
                print("index.html loaded in the webview.")

            else:
                application_path = "file://" + application_path
                self.webview.load_html(Api.html, application_path)
                print("Loaded webview as python module.")

        elif application_path.startswith("w") or application_path.startswith("h"):
            NOSSL_MSG = "You can only run unsecured url's in debug mode. Change "
            SSL_MSG = " forcing SSL"

            if not options.debug and application_path.startswith("http://"):
                application_path = application_path.replace("http:", "https:")
                print(NOSSL_MSG + "http: to https:" + SSL_MSG)

            elif not options.debug and application_path.startswith("ws:"):
                application_path = application_path.replace("ws:", "wss:")
                print(NOSSL_MSG + "ws:// to wss://" + SSL_MSG)

            print("URL loaded in the webview.")
            self.webview.load_uri(application_path)

        self.connect("delete-event", Gtk.main_quit)
        self.show_all()  # maybe i should only show the window wen the webview finishes loading?


def main():
    AppWindow()
    Gtk.main()


def cml():
    if options.debug:
        options.route = sys.argv[2]

    if options.route:
        main()

    else:
        subprocess.call(["jak", "-h"])
