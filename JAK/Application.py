#### Jade Application Kit
# * https://codesardine.github.io/Jade-Application-Kit
# * Vitor Lopes Copyright (c) 2016 - 2019
# * https://vitorlopes.me

import sys
import subprocess
from JAK.Utils import Instance, bindings
from JAK.Widgets import JWindow
from JAK.WebEngine import JWebView
from JAK import __version__
if bindings() == "PyQt5":
    print("PyQt5 Bindings")
    from PyQt5.QtCore import Qt, QCoreApplication
    from PyQt5.QtWidgets import QApplication
else:
    print("PySide2 Bindings, JAK_PREFERRED_BINDING environment variable not set.")
    from PySide2.QtCore import Qt, QCoreApplication
    from PySide2.QtWidgets import QApplication


class JWebApp(QApplication):
    #### Imports: from JAK.Application import JWebApp

    config = {
        "title": "Jade Application Kit",
        "icon": None,
        "web_contents": "https://codesardine.github.io/Jade-Application-Kit",
        "debug": False,
        "debug_port": "9000",
        "transparent": False,
        "online": False,
        "disable_gpu": False,
        "url_rules": None,
        "cookies_path": None,
        "user_agent": None,
        "custom_css": None,
        "custom_js": None,
        "toolbar": None,
        "menus": None,
        "MediaAudioVideoCapture": False,
        "MediaVideoCapture": False,
        "MediaAudioCapture": False,
        "Geolocation": False,
        "MouseLock": False,
        "DesktopVideoCapture": False,
        "DesktopAudioVideoCapture": False,
        "JavascriptCanPaste": True,
        "PlaybackRequiresUserGesture": False,
        "FullScreenSupportEnabled": True,
        "AllowWindowActivationFromJavaScript": True,
        "LocalContentCanAccessRemoteUrls": True,
        "JavascriptCanAccessClipboard": True,
        "SpatialNavigationEnabled": True,
        "TouchIconsEnabled": True,
        "FocusOnNavigationEnabled": True
    }

    def __init__(self, config=config, **app_config):
        self.config = config
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
        for key, value in app_config.items():
            config[key] = value

        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if config["debug"] or "--dev" in sys.argv:
            # Adding some command line arguments for testing purposes,
            # this MUST BE done before initializing QApplication
            sys.argv.append(f"--remote-debugging-port={config['debug_port']}")
            print("Debugging Mode On")
            if not config["debug"]:
                config["debug"] = True
        else:
            print("Production Mode On, use (--dev) for debugging")
        # Enable/Disable GPU acceleration
        if not config["disable_gpu"]:
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

        if config["disable_gpu"]:
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
        # Desktop file must match application name in lowercase with dashes instead of white space.
        self.setDesktopFileName(f"{config['title'].lower().replace(' ', '-')}.desktop")
        self.setOrganizationDomain(config['web_contents'])
        self.setApplicationVersion(__version__)
        if not config['online']:
            if bindings() == "PyQt5":
                from PyQt5.QtWebEngineCore import QWebEngineUrlScheme
            else:
                from PySide2.QtWebEngineCore import QWebEngineUrlScheme
            QWebEngineUrlScheme.registerScheme(QWebEngineUrlScheme("ipc".encode()))

    def run(self):
        Instance.record("view", JWebView(self.config))

        if self.config["custom_css"]:
            from JAK.Utils import JavaScript
            JavaScript.css(self.config["custom_css"])
            print("Custom CSS detected")

        if self.config["custom_js"]:
            from JAK.Utils import JavaScript
            JavaScript.send(self.config["custom_js"])
            print("Custom JavaScript detected")

        win = Instance.auto("win", JWindow(self.config))
        win.resize(win.default_size("width"), win.default_size("height"))
        win.show()
        win.window_original_position = win.frameGeometry()
        result = self.exec_()
        sys.exit(result)
