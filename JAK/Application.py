#### Jade Application Kit
# * https://codesardine.github.io/Jade-Application-Kit
# * Vitor Lopes Copyright (c) 2016 - 2019
# * https://vitorlopes.me

import sys
import time
import subprocess
from JAK.Utils import Instance, bindings
from JAK import __version__
if bindings() == "PyQt5":
    print("PyQt5 Bindings")
    from PyQt5.QtCore import Qt, QCoreApplication
    from PyQt5.QtWidgets import QApplication
else:
    print("PySide2 Bindings, JAK_PREFERRED_BINDING environment variable not set.")
    from PySide2.QtCore import Qt, QCoreApplication
    from PySide2.QtWidgets import QApplication
from JAK.Widgets import JWindow
from JAK.WebEngine import JWebView



time.time()



class JWebApp(QApplication):
    #### Imports: from JAK.Application import JWebApp

    def __init__(self, title="", icon="", web_contents="", debug=False, transparent=False, online=False,
                 disable_gpu=False, url_rules="", cookies_path="", user_agent="", custom_css="", custom_js="",
                 toolbar=""):
        """
        * JWebApp(args)
        * :arg title:str: Required
        * :arg icon:str: Optional
        * :arg web_contents:str: Required
        * :arg debug:bool: Optional
        * :arg transparent:bool: Optional
        * :arg online:bool: Optional
        * :arg disable_gpu:bool: Optional
        * :arg url_rules:dict: Optional
        * :arg cookies_path:str: Optional
        * :arg user_agent:str: Optional
        * :arg custom_css:str: Optional
        * :arg custom_js:str: Optional
        * :arg toolbar:dict: Optional
        """
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if debug or "--dev" in sys.argv:
            # Adding some command line arguments for testing purposes,
            # this MUST BE done before initializing QApplication
            sys.argv.append("--remote-debugging-port=9000")
            print("Debugging Mode On")
            if not debug:
                debug = True
        else:
            print("Production Mode On, use (--dev) for debugging")
        # Enable/Disable GPU acceleration
        if not disable_gpu:
            # Virtual machine detection using SystemD
            detect_virtual_machine = subprocess.Popen(
                ["systemd-detect-virt"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            # FIXME find a more reliable way of detecting NVIDIA cards
            detect_nvidia_pci = subprocess.Popen(
                "lspci | grep -i --color 'vga\|3d\|2d'", stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                shell=True
            )
            virtual = detect_virtual_machine.communicate()
            nvidia_pci = detect_nvidia_pci.communicate()
            nvidia_pci = nvidia_pci[0].decode("utf-8").lower()

        def disable_opengl():
            # Disable GPU acceleration
            # https://codereview.qt-project.org/c/qt/qtwebengine-chromium/+/206307
            QCoreApplication.setAttribute(Qt.AA_UseSoftwareOpenGL, True)

        if disable_gpu:
            disable_opengl()
            print("Disabling GPU, Software Rendering explicitly activated")
        else:
            if virtual[-1]:
                # Detect virtual machine
                print(f"Virtual machine detected:{virtual}")
                disable_opengl()

            elif nvidia_pci:
                # Detect NVIDIA cards
                if "nvidia" in nvidia_pci:
                    print("NVIDIA detected:Known bug - kernel rejected pushbuf")
                    print("Falling back to Software Rendering")
                    disable_opengl()
            else:
                print(f"Virtual Machine:{virtual[-1]}")

        super(JWebApp, self).__init__(sys.argv)
        self.title = title
        self.web_contents = web_contents
        self.debug = debug
        self.transparent = transparent
        self.online = online
        self.toolbar = toolbar
        self.url_rules = url_rules
        self.cookies_path = cookies_path
        self.user_agent = user_agent
        self.custom_css = custom_css
        self.custom_js = custom_js
        self.icon = icon
        # Desktop file must match application name in lowercase with dashes instead of white space.
        self.setDesktopFileName(f"{title.lower().replace(' ', '-')}.desktop")
        self.setOrganizationDomain("https://codesardine.github.io/Jade-Application-Kit")
        self.setApplicationVersion(__version__)
        if not self.online:
            if bindings() == "PyQt5":
                from PyQt5.QtWebEngineCore import QWebEngineUrlScheme
            else:
                from PySide2.QtWebEngineCore import QWebEngineUrlScheme
            QWebEngineUrlScheme.registerScheme(QWebEngineUrlScheme("ipc".encode()))

    def run(self):
        Instance.record("view", JWebView(self.title, self.icon, self.web_contents, self.debug, self.transparent,
                                         self.online, self.url_rules, self.cookies_path, self.user_agent,
                                         self.custom_css, self.custom_js))

        win = Instance.auto("win", JWindow(self.debug, self.online, self.title, self.icon, self.transparent, self.toolbar))
        win.resize(win.default_size("width"), win.default_size("height"))
        win.show()
        win.window_original_position = win.frameGeometry()
        if self.debug:
            print(Instance.get_instances())

        result = self.exec_()
        sys.exit(result)
