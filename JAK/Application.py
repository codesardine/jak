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
    def __init__(self, title="", icon="", web_contents="", debug=False, transparent=False, online=False,
                 disable_gpu=False, url_rules="", cookies_path="", user_agent="", custom_css="", custom_js="",
                 toolbar=""):
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

        if not disable_gpu:
            # Only run if we are not passing --disable-gpu argument
            # Detect virtual machine using systemd and disable GPU acceleration
            detect_virtual_machine = subprocess.Popen(
                ['systemd-detect-virt'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            # FIXME more reliable way of detecting NVIDIA cards
            detect_nvidia_pci = subprocess.Popen(
                'lspci | grep NVIDIA', stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                shell=True
            )
            virtual = detect_virtual_machine.communicate()
            nvidia_pci = detect_nvidia_pci.communicate()
            nvidia_pci = nvidia_pci[0].decode("utf-8").lower()

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
        if disable_gpu:
            self.disable_gpu()
            print("Disabling GPU, Software Rendering explicitly activated")
        else:
            if virtual[-1]:
                print(f"Virtual machine detected:{virtual}")
                self.disable_gpu()

            elif nvidia_pci:
                if "nvidia" in nvidia_pci:
                    print("NVIDIA detected:Known bug - kernel rejected pushbuf")
                    print("Falling back to Software Rendering")
                    self.disable_gpu()
            else:
                print(f"Virtual Machine:{virtual[-1]}")

    def disable_gpu(self):
        self.setAttribute(Qt.AA_UseSoftwareOpenGL, True)

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
