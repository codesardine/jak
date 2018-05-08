# coding: utf-8
"""
          Jade Application Kit
 Author - Copyright (c) 2016 - 2018 Vitor Lopes
 url    - https://codesardine.github.io/Jade-Application-Kit
"""
import json
import os
import subprocess
import sys
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, Gdk, WebKit2, Gio
from j import Options, Api


options = Options.Cmdl()
if options.debug or options.video:
    options.route = sys.argv[2]


# if running as module
if options.route is None:
    app_mode = "module"
    # returns the path of the file importing the module
    options.route = os.path.dirname(os.path.abspath(sys.argv[0]))

elif options.route.startswith("http"):
    app_mode = "url"

else:
    app_mode = "folder"


if app_mode != "url" and not options.route.endswith("/"):
    options.route += "/"


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


def settings(key1, key2):
    if app_mode == "url":
        settings_file = os.getcwd() + "/settings.json"
    else:
        settings_file = options.route + "settings.json"

    if os.path.exists(settings_file):
        # Open settings.json and return values

        file = Api.Fs.open_file(settings_file)
        data = json.loads(file)

    elif options.video:
        data = {
            "app": {
                "name": ""
            },

            "window": {
                "hint_type": "dialog",
                "width": 640,
                "height": 360,
                "icon": ""
            },

            "webkit": {
                "cache": "local",
                "user_agent": "",
                "same_frame": ""
            }
        }

    else:
        data = {
            "app": {
                "name": ""
            },
            "window": {
                "width": 1024,
                "height": 600,
                "icon": ""
            },
            "webkit": {
                "cache": "local",
                "context_menu": True,
                "user_agent": "",
                "site_quirks": True,
                "same_frame": ""
            }
        }

    value = data.get(key1).get(key2)
    return value


class AppWindow(Gtk.Window):
    def __init__(self):
        W = Gtk.Window
        if settings("window", "hint_type") == "desktop" or \
           settings("window", "hint_type") == "dock":

            W.__init__(self, title=settings("app", "name"),
                       skip_pager_hint=True, skip_taskbar_hint=True)
        else:
            W.__init__(self, title=settings("app", "name"))

        # create webview
        context = WebKit2.WebContext.get_default()
        sm = context.get_security_manager()

        self.manager = WebKit2.UserContentManager()
        self.webview = WebKit2.WebView.new_with_user_content_manager(self.manager)
        self.add(self.webview)
        self.settings = self.webview.get_settings()

        if settings("webkit", "user_agent"):
            self.settings.set_user_agent(settings("webkit", "user_agent"))

        print("Identifying User Agent as - " + self.settings.get_user_agent())

        if settings("webkit", "site_quirks"):
            # some website features wont work without this
            self.settings.set_property("enable-site-specific-quirks", True)

        def get_storage_path():
            storage_path = os.getenv("HOME") + "/.jak/"
            return storage_path

        def set_storage():
            context.set_favicon_database_directory(get_storage_path())
            context.get_favicon_database()

        if settings("webkit", "cache") == "local":
            cache_model = WebKit2.CacheModel.DOCUMENT_BROWSER
            set_storage()

        elif settings("webkit", "cache") == "online":
            cache_model = WebKit2.CacheModel.WEB_BROWSER
            self.settings.set_property("enable-offline-web-application-cache", True)
            self.settings.set_property("enable-dns-prefetching", True)
            self.settings.set_property("enable-page-cache", True)
            # we only need cookies if we are online
            app_name = settings("app", "name")
            cookies_filename = "cookies.txt"
            set_storage()

            try:
                if not os.path.exists(get_storage_path()):
                    os.makedirs(get_storage_path())

            except OSError:
                print("Error: Creating cookies directory. " + get_storage_path())

            self.session = context.get_cookie_manager()
            storage = WebKit2.CookiePersistentStorage.TEXT
            policy = WebKit2.CookieAcceptPolicy.ALWAYS
            self.session.set_accept_policy(policy)
            self.session.set_persistent_storage(get_storage_path() + cookies_filename, storage)

            def cookies_change(self):
                pass

            self.session.connect("changed", cookies_change)

        else:
            cache_model = WebKit2.CacheModel.DOCUMENT_VIEWER
            print("Default no CACHE")

        context.set_cache_model(cache_model)
        screen = W.get_screen(self)

        if os.path.isfile(options.route + "window.css"):
            load_window_css(options.route + "window.css")

        if settings("window", "transparent") is True:

            # TODO transparent window is not working
            color = screen.get_rgba_visual()

            if color is not None and screen.is_composited():
                self.set_app_paintable(True)

                css = b"""
                #jade-window, #jade-dock, #jade-desktop {
                    background-color: rgba(0,0,0,0);
                } """

                load_window_css(css)
                self.webview.set_background_color(Gdk.RGBA(0, 0, 0, 0))

            else:
                print("Your system does not supports composite windows")

        # https://lazka.github.io/pgi-docs/#Gdk-3.0/enums.html#Gdk.WindowTypeHint
        if settings("window", "hint_type") == "desktop":
            W.set_type_hint(self, Gdk.WindowTypeHint.DESKTOP)

        elif settings("window", "hint_type") == "dialog":
           W.set_type_hint(self, Gdk.WindowTypeHint.DIALOG)

        elif settings("window", "hint_type") == "tooltip":
            W.set_type_hint(self, Gdk.WindowTypeHint.TOOLTIP)

        elif settings("window", "hint_type") == "notification":
            W.set_type_hint(self, Gdk.WindowTypeHint.NOTIFICATION)

        elif settings("window", "hint_type") == "dock":
            W.set_type_hint(self, Gdk.WindowTypeHint.DOCK)

        elif settings("window", "hint_type") == "menu":
            W.set_type_hint(self, Gdk.WindowTypeHint.MENU)

        elif settings("window", "hint_type") == "toolbar":
            W.set_type_hint(self, Gdk.WindowTypeHint.TOOLBAR)

        elif settings("window", "hint_type") == "utility":
            W.set_type_hint(self, Gdk.WindowTypeHint.UTILITY)

        elif settings("window", "hint_type") == "splashscreen":
            W.set_type_hint(self, Gdk.WindowTypeHint.SPLASHSCREEN)

        elif settings("window", "hint_type") == "dropdownmenu":
            W.set_type_hint(self, Gdk.WindowTypeHint.DROPDOWN_MENU)

        elif settings("window", "hint_type") == "popupmenu":
            W.set_type_hint(self, Gdk.WindowTypeHint.POPUP_MENU)

        else:
            W.set_type_hint(self, Gdk.WindowTypeHint.NORMAL)

        W.set_position(self, Gtk.WindowPosition.CENTER)

        if os.path.isfile(settings("window", "icon")):
            W.set_icon_from_file(self, settings("window", "icon"))

        if settings("window", "resizable")is False:
            W.set_resizable(self, False)

        if settings("window", "decorated") is False:
            W.set_decorated(self, False)

        if settings("window", "full_screen") is True:
            W.set_default_size(self, screen.width(), screen.height())

        else:
            W.set_default_size(self, settings("window", "width"), settings("window", "height"))

        if options.video:
            W.set_keep_above(self, True)
            W.set_gravity(self, Gdk.Gravity.SOUTH_EAST)
            #  in multi head setups this will be the last screen
            W.move(self, screen.width(), screen.height())

        self.settings.set_enable_smooth_scrolling(self)
        self.settings.set_default_charset("UTF-8")
        self.settings.set_property("allow-universal-access-from-file-urls", True)
        self.settings.set_property("allow-file-access-from-file-urls", True)
        self.settings.set_property("enable-spatial-navigation", True)  # this is good for usability
        self.settings.set_property("enable-java", False)
        self.settings.set_property("enable-plugins", False)
        self.settings.set_property("enable-accelerated-2d-canvas", True)

        if settings("webkit", "debug") or options.debug:
            self.webview.run_javascript("alert('Running in DEBUG MODE this is only intended for Development. " +
                                        "Any keys you press will be seen in the shell use with CAUTION!')")
            self.settings.set_property("enable-developer-extras", True)
            self.settings.set_property("enable-write-console-messages-to-stdout", True)

            # disable all cache in debug mode
            self.settings.set_property("enable-offline-web-application-cache", False)
            self.settings.set_property("enable-page-cache", False)

        if not settings("webkit", "context_menu"):
            # Disable webview rigth click menu
            def disable_menu(*args):
                return True

            self.webview.connect("context-menu", disable_menu)

        if settings("webkit", "cache") != "online" and app_mode != "url":
            # only for local application
            _name = settings("app", "name")
            _description = settings("app", "description")
            _version = settings("app", "version")
            _author = settings("app", "author")
            _license = settings("app", "license")
            _url = settings("app", "url")
            _screen_width = screen.width()
            _screen_height = screen.height()
            # TODO javascript Api
            Api.js = '''
            var JAK = {
            'app': {
            'getName'            : '%(_name)s',
            'getDescription'     : '%(_description)s',
            'getVersion'         : '%(_version)s',
            'getAuthor'          : '%(_author)s',
            'getLicense'         : '%(_license)s',
            'getUrl'             : '%(_url)s',
            'getScreenWidth'     :  %(_screen_width)s,
            'getScreenHeight'    :  %(_screen_height)s
            }};

            ''' % locals()

            self.webview.run_javascript(Api.js)

        def register_app(route):
            context.register_uri_scheme(route, scheme_callback, None, None)
            sm.register_uri_scheme_as_cors_enabled(route)

            if settings("webkit", "same_frame") is not None:
                for domain in settings("webkit", "same_frame"):
                    context.register_uri_scheme(domain, scheme_callback, None, None)
                    sm.register_uri_scheme_as_cors_enabled(domain)

        def scheme_callback(self, request):
            pass

        def load_app(mode, route):
            if mode == "url":
                # force ssl
                if not options.debug and route.startswith("http:"):
                    route = route.replace("http:", "https:")

                self.webview.load_uri(route)

            elif mode == "module":
                self.webview.load_html(Api.html, "file://" + route)

            elif mode == "folder":
                self.webview.load_uri("file://" + route + "/index.html")

            register_app(route)

        load_app(app_mode, options.route)

        # Get title from webview for http
        def on_title_changed(view, title):
            """
            :param view:
            :param title:
            """
            url = self.webview.get_uri()

            if url.startswith("http"):
                title = self.webview.get_title()
                title = title.rstrip()
                W.set_title(self, title)

        def on_key_release_event(self, event):

            if settings("webkit", "debug") or options.debug:
                # this can be used to find out key names

                print("KeyPress = " + Gdk.keyval_name(event.keyval))

            # distraction free mode, this only works on decorated windows
            if event.keyval == Gdk.KEY_F11:
                is_full_screen = self.get_window().get_state() & \
                                 Gdk.WindowState.FULLSCREEN != False

                if is_full_screen:
                    W.unfullscreen(self)

                else:
                    W.fullscreen(self)

                return True

            # webpage zoom keys
            elif event.keyval == Gdk.KEY_equal and event.state == Gdk.ModifierType.CONTROL_MASK or \
                    event.keyval == Gdk.KEY_minus and event.state == Gdk.ModifierType.CONTROL_MASK:

                zoom = self.webview.get_zoom_level()
                value = 0.1

                if event.keyval == Gdk.KEY_minus:
                    if zoom <= 0.4:
                        # reset value
                        value = 1.0
                    else:
                        value = zoom - value

                elif event.keyval == Gdk.KEY_equal:
                    if zoom >= 1.8:
                        # reset value
                        value = 1.0
                    else:
                        value = zoom + value

                self.webview.set_zoom_level(round(value, 2))

        def on_decide_policy(view, decision, decision_type):

            """
            :param view:
            :param decision:
            :param decision_type:
            """
            if decision_type == WebKit2.PolicyDecisionType.NAVIGATION_ACTION or \
               decision_type == WebKit2.PolicyDecisionType.NEW_WINDOW_ACTION:

                if decision.get_navigation_action().get_request().get_uri() == "about:blank":
                    # ignore blank pages
                    decision.ignore()
                    return True

            elif decision_type == WebKit2.PolicyDecisionType.RESPONSE:
                MIMES = (
                    "application/vnd.oasis.opendocument.text", 
                    "application/pdf", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                    "application/vnd.openxmlformats-officedocument.presentationml.presentation", 
                    "application/zip", 
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                    "application/vnd.oasis.opendocument.spreadsheet")

                response = decision.get_response()
                mime_type = response.props.mime_type
                
                if mime_type in MIMES:
                    decision.download()
                else:
                    decision.use()   
                return False

        def favicon_changed(view, event):
            # webpage icon changed
            icon = view.get_favicon()
            # set as window icon
            pixbuf = Gdk.pixbuf_get_from_surface(icon, 0, 0, icon.get_width(), icon.get_height())
            #Gtk.IconInfo.load_icon(pixbuf)
            W.set_icon(self, pixbuf)

        def on_show_notification(view, notification):
            self.set_urgency_hint(True)
            notify = Gio.Notification.new(notification.get_title())
            notify.set_body(notification.get_body())
            return False

        def on_permission_request(view, request):
            if isinstance(request, WebKit2.NotificationPermissionRequest):
                request.allow()
                return True

        self.webview.connect("show-notification", on_show_notification)
        self.webview.connect("permission-request", on_permission_request)
        self.webview.connect("decide-policy", on_decide_policy)
        self.webview.connect("notify::favicon", favicon_changed)
        self.webview.connect("notify::title", on_title_changed)
        self.connect("key-release-event", on_key_release_event)
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()  # maybe i should only show the window wen the webview finishes loading?


def main():
    AppWindow()
    Gtk.main()


def cml():
    if options.route:
        main()

    else:
        subprocess.call(["jak", "-h"])
