#### Jade Application Kit
# * https://codesardine.github.io/Jade-Application-Kit
# * Vitor Lopes Copyright (c) 2016 - 2020
# * https://vitorlopes.me
from JAK.Utils import bindings
if bindings() == "PyQt5":
    from PyQt5.QtCore import Qt
    from PyQt5.QtWebEngineWidgets import QWebEngineSettings
else:
    from PySide2.QtCore import Qt
    from Side2.QtWebEngineWidgets import QWebEngineSettings


def config():
    return {
        "debug": False,
        "debugPort": "9000",
        "setAAttribute": (),
        "disableGPU": False,
        "window": {
            "title": "Jade Application Kit",
            "icon": None,
            "setFlags": Qt.Window,
            "setAttribute": (),
            "fullScreen": False,
            "transparent": False,
            "toolbar": None,
            "menus": None,
        },
        "webview": {
            "webContents": "https://codesardine.github.io/Jade-Application-Kit",
            "online": False,
            "urlRules": None,
            "cookiesPath": None,
            "userAgent": None,
            "addCSS": None,
            "runJavaScript": None,
            "IPC": True,
            "MediaAudioVideoCapture": False,
            "MediaVideoCapture": False,
            "MediaAudioCapture": False,
            "Geolocation": False,
            "MouseLock": False,
            "DesktopVideoCapture": False,
            "DesktopAudioVideoCapture": False,
            "injectJavaScript": {
                "JavaScript": None,
                "name": "Application Script"
            },
            "webChannel": {
                "active": False,
                "sharedOBJ": None
            },
            "enabledSettings": (
                QWebEngineSettings.JavascriptCanPaste,
                QWebEngineSettings.FullScreenSupportEnabled,
                QWebEngineSettings.AllowWindowActivationFromJavaScript,
                QWebEngineSettings.LocalContentCanAccessRemoteUrls,
                QWebEngineSettings.JavascriptCanAccessClipboard,
                QWebEngineSettings.SpatialNavigationEnabled,
                QWebEngineSettings.TouchIconsEnabled
            ),
            "disabledSettings": (
                QWebEngineSettings.PlaybackRequiresUserGesture
            )
        }
}
