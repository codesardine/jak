#### Jade Application Kit
# * https://codesardine.github.io/Jade-Application-Kit
# * Vitor Lopes Copyright (c) 2016 - 2019
# * https://vitorlopes.me

import sys
import time
import subprocess
from PySide2.QtCore import Qt, QCoreApplication
from PySide2.QtWidgets import QApplication
from JAK.Utils import Instance
from JAK.Widgets import JWindow
from JAK.WebEngine import JWebView

time.time()


# noinspection PyUnresolvedReferences
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
        if debug or "--dev" in sys.argv:
            # Adding some command line arguments for testing purposes,
            # this MUST BE done before initializing QApplication
            sys.argv.append("--remote-debugging-port=8000")
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

        # Enable automatic HDPI scale
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

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
        self.url_rules = url_rules
        self.cookies_path = cookies_path
        self.user_agent = user_agent
        self.custom_css = custom_css
        self.custom_js = custom_js
        self.icon = icon
        self.toolbar = toolbar

    def run(self):
        if "://" not in self.web_contents:
            self.web_contents = f"https://{self.web_contents}"

        Instance.record("view", JWebView(self.title, self.icon, self.web_contents, self.debug, self.transparent,
                                         self.online, self.url_rules, self.cookies_path, self.user_agent,
                                         self.custom_css, self.custom_js))

        win = Instance.auto("win", JWindow(self.title, self.icon, self.transparent, self.toolbar))
        win.resize(win.default_size("width"), win.default_size("height"))
        win.show()
        win.window_original_position = win.frameGeometry()
        if self.debug:
            print(Instance.get_instances())

        result = self.exec_()
        sys.exit(result)
