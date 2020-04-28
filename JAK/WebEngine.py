#### Jade Application Kit
# * https://codesardine.github.io/Jade-Application-Kit
# * Vitor Lopes Copyright (c) 2016 - 2020
# * https://vitorlopes.me
import os
from functools import lru_cache as cache
from JAK.Utils import check_url_rules, get_current_path, bindings
from JAK.RequestInterceptor import Interceptor
if bindings() == "PyQt5":
    from PyQt5.QtCore import QUrl, Qt
    from PyQt5.QtWebEngineCore import QWebEngineUrlSchemeHandler
    from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineSettings
else:
    from PySide2.QtCore import QUrl, Qt
    from PySide2.QtWebEngineCore import QWebEngineUrlSchemeHandler
    from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineSettings


@cache(maxsize=5)
def validate_url(self, url: str) -> None:
    """
    * Check if is a URL or HTML and if is valid
    * :param self: QWebEnginePage
    * :param web_contents: URL or HTML
    """
    if "!doctype" in url.lower():
        # Inject HTML
        base_url = get_current_path()
        self.setHtml(url, QUrl(f"file://{base_url}/"))
        print("Loading local HTML")
    else:
        if url.endswith(".html"):
            # HTML file
            if not url.startswith("/"):
                url = f"/{url}"
            url = f"file://{url}"

        elif "://" not in url:
            # HTML URL
            url = f"https://{url}"

        url = QUrl(url)
        if url.isValid():
            self.load(url)
            print(f"Loading URL:{url.toString()}")


class IpcSchemeHandler(QWebEngineUrlSchemeHandler):
    def __init__(self):
        super().__init__()

    def requestStarted(self, request):
        url = request.requestUrl().toString()
        if url.startswith("ipc:"):
            # * Link's that starts with [ ipc:somefunction() ] trigger's the two way communication system between
            # HTML and Python, only if online is set to false
            from JAK.IPC import Communication
            Communication.send(url)
            return


class JWebPage(QWebEnginePage):
    """ #### Imports: from JAK.WebEngine import JWebPage """
    def __init__(self, profile, webview, config):
        self.config = config
        super(JWebPage, self).__init__(profile, webview)
        self.featurePermissionRequested.connect(self._on_feature_permission_requested)

    def _open_in_browser(self) -> None:
        """ Open url in a external browser """
        print("Open above^ tab in Browser")
        from webbrowser import open_new_tab
        open_new_tab(self.url)

    def _dialog_open_in_browser(self) -> None:
        """ Opens a dialog to confirm if user wants to open url in external browser """
        from JAK.Widgets import JCancelConfirmDialog
        msg = "Open In Your Browser"
        JCancelConfirmDialog(self.parent(), self.title(), msg, self._open_in_browser)

    @cache(maxsize=10)
    def acceptNavigationRequest(self, url, _type, is_main_frame) -> bool:
        """
        * Decide if we navigate to a URL
        * :param url: QtCore.QUrl
        * :param _type: QWebEnginePage.NavigationType
        * :param is_main_frame:bool
        """
        self.url = url.toString()
        self.page = JWebPage(self.profile(), self.view(), self.config)
        # Redirect new tabs to same window
        self.page.urlChanged.connect(self._on_url_changed)

        if self.config['webview']["online"]:
            if _type == QWebEnginePage.WebWindowType.WebBrowserTab:
                if self.config['webview']["urlRules"]:
                    # Check for URL rules on new tabs
                    if self.url.startswith(self.config['webview']["urlRules"]["WebBrowserTab"]):
                        self.open_window(self.url)
                        return False
                    elif check_url_rules("WebBrowserTab", self.url, self.config['webview']["urlRules"]):
                        print(f"Redirecting WebBrowserTab^ to same window")
                        return True
                    else:
                        print(f"Deny WebBrowserTab:{self.url}")
                        # check against WebBrowserWindow list to avoid duplicate dialogs
                        if not check_url_rules("WebBrowserWindow", self.url, self.config['webview']["urlRules"]):
                            self._dialog_open_in_browser()
                        return False
                else:
                    return True

            elif _type == QWebEnginePage.WebBrowserBackgroundTab:
                print(f"WebBrowserBackgroundTab request:{self.url}")
                return True

            elif _type == QWebEnginePage.WebBrowserWindow:
                if self.config["url_rules"] and self.config['webview']["online"]:
                    # Check URL rules on new windows
                    if check_url_rules("WebBrowserWindow", self.url, self.config['webview']["urlRules"]):
                        print(f"Deny WebBrowserWindow:{self.url}")
                        self._dialog_open_in_browser()
                        return False
                    else:
                        print(f"Allow WebBrowserWindow:{self.url}")
                        return True
                else:
                    return True

            elif _type == QWebEnginePage.WebDialog:
                return True
        return True

    def _on_feature_permission_requested(self, security_origin, feature):

        def grant_permission():
            self.setFeaturePermission(security_origin, feature, self.PermissionGrantedByUser)
        def deny_permission():
            self.setFeaturePermission(security_origin, feature, self.PermissionDeniedByUser)

        if feature == self.Notifications:
            grant_permission()
        elif feature == self.MediaAudioVideoCapture and self.config['webview']["MediaAudioVideoCapture"]:
            grant_permission()
        elif feature == self.MediaVideoCapture and self.config['webview']["MediaVideoCapture"]:
            grant_permission()
        elif feature == self.MediaAudioCapture and self.config['webview']["MediaAudioCapture"]:
            grant_permission()
        elif feature == self.Geolocation and self.config['webview']["Geolocation"]:
            grant_permission()
        elif feature == self.MouseLock and self.config['webview']["MouseLock"]:
            grant_permission()
        elif feature == self.DesktopVideoCapture and self.config['webview']["DesktopVideoCapture"]:
            grant_permission()
        elif feature == self.DesktopAudioVideoCapture and self.config['webview']["DesktopAudioVideoCapture"]:
            grant_permission()
        else:
            deny_permission()

    def open_window(self, url):
        """ Open a New Window"""
        # FIXME cookies path needs to be declared for this to work
        self.popup = JWebView(self.config)
        self.popup.page().windowCloseRequested.connect(self.popup.close)
        self.popup.show()
        print(f"Opening New Window^")

    @cache(maxsize=2)
    def createWindow(self, _type: object) -> QWebEnginePage:
        """
        * Redirect new window's or tab's to same window
        * :param _type: QWebEnginePage.WebWindowType
        """
        return self.page

    def _on_url_changed(self, url: str) -> None:
        url = url.toString()
        if url == "about:blank":
            return False
        else:
            validate_url(self, url)


class JWebView(QWebEngineView):
    """ #### Imports: from JAK.WebEngine import JWebView """
    def __init__(self, config):
        self.config = config
        super(JWebView, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.profile = QWebEngineProfile.defaultProfile()
        self.webpage = JWebPage(self.profile, self, config)
        self.setPage(self.webpage)
        if config['webview']["injectJavaScript"]["JavaScript"]:
            self._inject_script(config['webview']["injectJavaScript"])
        self.interceptor = Interceptor(config)

        if config['webview']["userAgent"]:
            # Set user agent
            self.profile.setHttpUserAgent(config['webview']["userAgent"])

        if config["debug"]:
            self.settings().setAttribute(QWebEngineSettings.XSSAuditingEnabled, True)
        else:
            self.setContextMenuPolicy(Qt.PreventContextMenu)

        if config['window']["transparent"]:
            # Activates background transparency
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.page().setBackgroundColor(Qt.transparent)
            print("Transparency detected")

        # * Set Engine options
        self.settings().setAttribute(self.config['webview']['disabledSettings'], False)
        for setting in self.config['webview']['enabledSettings']:
            self.settings().setAttribute(setting, True)

        if config['webview']["online"]:
            self.settings().setAttribute(QWebEngineSettings.DnsPrefetchEnabled, True)
            print("Engine online IPC and Bridge Disabled")
            self.page().profile().downloadRequested.connect(self._download_requested)

            # Set persistent cookies
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)

            # set cookies on user folder
            if config['webview']["cookiesPath"]:
                # allow specific path per application.
                _cookies_path = f"{os.getenv('HOME')}/.jak/{config['webview']['cookiesPath']}"
            else:
                # use separate cookies database per application
                title = config['window']["title"].lower().replace(" ", "-")
                _cookies_path = f"{os.getenv('HOME')}/.jak/{title}"

            self.profile.setPersistentStoragePath(_cookies_path)
            print(f"Cookies PATH:{_cookies_path}")
        else:
            self.settings().setAttribute(QWebEngineSettings.ShowScrollBars, False)
            application_script = "const JAK = {};"

            if config['webview']["IPC"]:
                print("IPC Active:")
                self._ipc_scheme_handler = IpcSchemeHandler()
                self.profile.installUrlSchemeHandler('ipc'.encode(), self._ipc_scheme_handler)
                application_script += """JAK.IPC = function(backendFunction) {
                            window.location.href = "ipc:" + backendFunction;
                        };"""

            if config['webview']["webChannel"]["active"]:
                if bindings() == "PyQt5":
                    from PyQt5.QtCore import QFile, QIODevice
                    from PyQt5.QtWebChannel import QWebChannel

                webchannel_js = QFile(':/qtwebchannel/qwebchannel.js')
                webchannel_js.open(QIODevice.ReadOnly)
                webchannel_js = bytes(webchannel_js.readAll()).decode('utf-8')
                webchannel_js += """new QWebChannel(qt.webChannelTransport, function (channel) {
                                        JAK.Bridge = channel.objects.Bridge;
                                    });"""

                application_script += webchannel_js
                self._inject_script({"JavaScript":application_script, "name":"JAK"})
                channel = QWebChannel(self.page())
                if config['webview']["webChannel"]["sharedOBJ"]:
                    bridge_obj = config['webview']["webChannel"]["sharedOBJ"]
                else:
                    raise NotImplementedError("QWebChannel shared QObject")

                channel.registerObject("Bridge", bridge_obj)
                self.page().setWebChannel(channel)
                print("WebChannel Active:")
            else:
                self._inject_script({"JavaScript":application_script, "name":"JAK"})

        self.profile.setRequestInterceptor(self.interceptor)
        print(self.profile.httpUserAgent())
        validate_url(self, config['webview']["webContents"])

    def _inject_script(self, script: dict):
        from JAK.Utils import JavaScript
        JavaScript.inject(self.page(), script)

    def _download_requested(self, download_item) -> None:
        """
        * If a download is requested call a save file dialog
        * :param download_item: file to be downloaded
        """
        if bindings() == "PyQt5":
            from PyQt5.QtWidgets import QFileDialog
        else:
            from PySide2.QtWidgets import QFileDialog
        dialog = QFileDialog(self)
        path = dialog.getSaveFileName(dialog, "Save File", download_item.path())

        if path[0]:
            download_item.setPath(path[0])
            print(f"downloading file to:( {download_item.path()} )")
            download_item.accept()
            self.download_item = download_item
            download_item.finished.connect(self._download_finished)
        else:
            print("Download canceled")

    def _download_finished(self) -> None:
        """
        Goes to previous page and pops an alert informing the user that the download is finish and were to find it
        """
        file_path = self.download_item.path()
        msg = f"File Downloaded to: {file_path}"
        from JAK.Widgets import InfoDialog
        InfoDialog(self, "Download Complete", msg)
