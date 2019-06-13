"""
 App Name   - Jade Application Kit
 App Url    - https://codesardine.github.io/Jade-Application-Kit
 Author     - Vitor Lopes -> Copyright (c) 2016 - 2019
 Author Url - https://vitorlopes.me
"""
import sys
import time
import subprocess
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication
try:
    from Utils import Instance
    from Widgets import JWindow
    from WebEngine import JWebView
    print("Testing: modules imported locally")
except ImportError:
    # Production
    from JAK.Utils import Instance
    from JAK.Widgets import JWindow
    from JAK.WebEngine import JWebView

time.time()


class JWebApp(QApplication):
    """
    Open a web page in a desktop application
    """
    def __init__(self, title="", icon="", web_contents="", debug=False, transparent=False, online=False, url_rules="",
                 cookies_path="", user_agent="", custom_css="", custom_js="", toolbar=""):
        """
        Create an application which loads a URL into a window
        """
        if debug or "--dev" in sys.argv:
            sys.argv.append("--remote-debugging-port=8000")
            sys.argv.append("--single-process")
            print("Debugging Mode On")
            if not debug:
                debug = True
        else:
            print("Production Mode On, use (--dev) for debugging")

        # Detect virtual machine using systemd and disable GPU acceleration
        detect_virtual_machine = subprocess.Popen(['systemd-detect-virt'], stdout=subprocess.PIPE,
                                                  stderr=subprocess.STDOUT)
        is_virtual = detect_virtual_machine.communicate()

        if is_virtual[-1] is not None:
            print(f"Virtual machine detected:{is_virtual}")
            sys.argv.append("--disable-gpu")
        else:
            print(f"Virtual Machine:{is_virtual[-1]}")

        # Command line arguments MUST BE before creating QApplication
        super(JWebApp, self).__init__(sys.argv)
        self.title = title
        self.web_contents = web_contents
        self.debug = debug
        self.transparent = transparent
        self.online = online
        self.url_rules = url_rules
        self.cookies_path = cookies_path
        self.user_agent = user_agent
        self.custom_css = custom_css
        self.custom_js = custom_js
        self.icon = icon
        self.toolbar = toolbar
        # Enable automatic HDPI scale
        self.setAttribute(Qt.AA_UseHighDpiPixmaps)
        self.setAttribute(Qt.AA_EnableHighDpiScaling)

    def run(self):
        Instance.record("view", JWebView(self.title, self.icon, self.web_contents, self.debug, self.transparent,
                                         self.online, self.url_rules, self.cookies_path, self.user_agent,
                                         self.custom_css, self.custom_js))

        win = Instance.auto("win", JWindow(self.title, self.icon, self.transparent, self.toolbar))
        # set window to 75% of screen size
        geometry = self.desktop().availableGeometry(win)
        win.resize(geometry.width() * 2 / 3, geometry.height() * 2 / 3)
        win.show()
        if self.debug:
            print(Instance.get_instances())

        result = self.exec_()
        sys.exit(result)
