#### Jade Application Kit
# * https://codesardine.github.io/Jade-Application-Kit
# * Vitor Lopes Copyright (c) 2016 - 2020
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
    print("JAK_PREFERRED_BINDING environment variable not set, falling back to PySide2 Bindings.")
    from PySide2.QtCore import Qt, QCoreApplication
    from PySide2.QtWidgets import QApplication


class JWebApp(QApplication):
    #### Imports: from JAK.Application import JWebApp

    def config():
        return {
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
        "add_CSS": None,
        "run_JavaScript": None,
        "inject_JavaScript": {
            "JavaScript": None,
            "name": "user-script"
        },
        "webChannel": {
            "active": False,
            "shared_obj": None
        },
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

    def __init__(self, config=config(), **app_config):
        self.config = config
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

        if self.config["add_CSS"]:
            from JAK.Utils import JavaScript
            JavaScript.css(self.config["add_CSS"])
            print("Custom CSS detected")

        if self.config["run_JavaScript"]:
            from JAK.Utils import JavaScript
            JavaScript.send(self.config["run_JavaScript"])
            print("Custom JavaScript detected")

        win = Instance.auto("win", JWindow(self.config))
        win.resize(win.default_size("width"), win.default_size("height"))
        win.show()
        win.window_original_position = win.frameGeometry()
        result = self.exec_()
        sys.exit(result)
